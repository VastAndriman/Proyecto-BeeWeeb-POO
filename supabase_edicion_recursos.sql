-- Edicion y eliminacion de aulas y horarios con permiso de Administrador.
-- Los horarios conservan las validaciones del trigger beeweek_horario_validar.
create or replace function private.beeweek_update(p_token text, p_table text,
    p_id integer, p_data jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare allowed text[];
        fields_to_update text;
        updated_id integer;
        result jsonb;
begin
    if not exists (
        select 1 from public.usuarios u
        where u.id = private.beeweek_require_session(p_token)
          and u.rol = 'Administrador'
    ) then
        raise exception 'Solo Administrador puede editar recursos academicos'
            using errcode = '42501';
    end if;
    allowed := case p_table
        when 'aulas' then array['numero','capacidad','tipo']
        when 'horarios' then array['dia','hora_inicio','hora_fin','materia_id','docente_id','aula_id','curso_id']
        else null end;
    if allowed is null or p_id is null or p_id <= 0
       or pg_catalog.jsonb_typeof(p_data) <> 'object'
       or p_data = '{}'::jsonb
       or exists (select 1 from pg_catalog.jsonb_object_keys(p_data) k where k <> all(allowed)) then
        raise exception 'Cambios no permitidos' using errcode = '22023';
    end if;
    if p_table = 'aulas' and p_data ? 'capacidad' and exists (
        select 1 from public.horarios h
        join public.cursos c on c.id = h.curso_id
        where h.aula_id = p_id and c.num_estudiantes > (p_data->>'capacidad')::integer
    ) then
        raise exception 'La nueva capacidad es menor que la matrícula de un horario del aula'
            using errcode = '23514';
    end if;
    select pg_catalog.string_agg(pg_catalog.format('%I = r.%I', k, k), ', ')
      into fields_to_update from pg_catalog.jsonb_object_keys(p_data) k;
    execute pg_catalog.format(
        'update public.%I t set %s from pg_catalog.jsonb_populate_record(null::public.%I, $1) r where t.id = $2 returning t.id',
        p_table, fields_to_update, p_table)
      into updated_id using p_data, p_id;
    if updated_id is null then
        raise exception 'El registro ya no existe' using errcode = 'P0002';
    end if;
    execute pg_catalog.format('select to_jsonb(t) from public.%I t where id = $1', p_table)
      into result using updated_id;
    return result;
end;
$$;

create or replace function private.beeweek_delete(p_token text, p_table text, p_id integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare deleted jsonb;
begin
    if not exists (
        select 1 from public.usuarios u
        where u.id = private.beeweek_require_session(p_token)
          and u.rol = 'Administrador'
    ) then
        raise exception 'Solo Administrador puede eliminar recursos academicos'
            using errcode = '42501';
    end if;
    if p_table not in ('aulas', 'horarios') or p_id is null or p_id <= 0 then
        raise exception 'Eliminacion no permitida' using errcode = '22023';
    end if;
    execute pg_catalog.format('delete from public.%I t where id = $1 returning to_jsonb(t)', p_table)
      into deleted using p_id;
    if deleted is null then
        raise exception 'El registro ya no existe' using errcode = 'P0002';
    end if;
    return deleted;
end;
$$;

create or replace function public.beeweek_update(p_token text, p_table text,
    p_id integer, p_data jsonb)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_update(p_token, p_table, p_id, p_data); $$;
create or replace function public.beeweek_delete(p_token text, p_table text, p_id integer)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_delete(p_token, p_table, p_id); $$;

revoke all on function private.beeweek_update(text,text,integer,jsonb) from public, anon, authenticated;
revoke all on function private.beeweek_delete(text,text,integer) from public, anon, authenticated;
revoke all on function public.beeweek_update(text,text,integer,jsonb) from public, anon, authenticated;
revoke all on function public.beeweek_delete(text,text,integer) from public, anon, authenticated;
grant execute on function private.beeweek_update(text,text,integer,jsonb) to anon, authenticated;
grant execute on function private.beeweek_delete(text,text,integer) to anon, authenticated;
grant execute on function public.beeweek_update(text,text,integer,jsonb) to anon, authenticated;
grant execute on function public.beeweek_delete(text,text,integer) to anon, authenticated;
