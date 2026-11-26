-- State de horarios: los registros actuales permanecen Publicados.
alter table public.horarios
    add column if not exists estado text not null default 'Publicado';
alter table public.horarios drop constraint if exists beeweek_horario_estado_ck;
alter table public.horarios add constraint beeweek_horario_estado_ck
    check (estado in ('Borrador', 'Publicado', 'Cancelado'));
create index if not exists beeweek_horarios_publicados_idx
    on public.horarios(dia, hora_inicio) where estado = 'Publicado';

-- La lista oculta borradores y cancelados a quienes no administran el sistema.
create or replace function private.beeweek_list(p_token text, p_table text,
    p_filter_column text default null, p_filter_value text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare result jsonb;
        account_role text;
        only_published boolean;
begin
    select u.rol into account_role from public.usuarios u
    where u.id = private.beeweek_require_session(p_token);
    if p_table not in ('aulas', 'materias', 'docentes', 'estudiantes', 'cursos', 'horarios')
       or (p_filter_column is not null and p_filter_column not in ('id', 'dia'))
       or (p_filter_column = 'dia' and p_table <> 'horarios') then
        raise exception 'Consulta no permitida' using errcode = '22023';
    end if;
    if account_role not in ('Administrador', 'Docente', 'Estudiante')
       or (p_table = 'estudiantes' and account_role <> 'Administrador') then
        raise exception 'Tu rol no permite consultar estos datos' using errcode = '42501';
    end if;
    if p_table = 'docentes' and account_role <> 'Administrador' then
        if p_filter_column = 'id' then
            select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
                'id', d.id, 'nombre', d.nombre, 'apellido', d.apellido)), '[]'::jsonb)
            into result from public.docentes d where d.id = p_filter_value::integer;
        else
            select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
                'id', d.id, 'nombre', d.nombre, 'apellido', d.apellido)), '[]'::jsonb)
            into result from public.docentes d;
        end if;
        return result;
    end if;
    only_published := p_table = 'horarios' and account_role <> 'Administrador';
    if only_published and p_filter_column is null then
        execute pg_catalog.format(
            'select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t where t.estado = ''Publicado''',
            p_table) into result;
    elsif only_published and p_filter_column = 'id' then
        execute pg_catalog.format(
            'select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t where id = $1 and t.estado = ''Publicado''',
            p_table) into result using p_filter_value::integer;
    elsif only_published then
        execute pg_catalog.format(
            'select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t where dia = $1 and t.estado = ''Publicado''',
            p_table) into result using p_filter_value;
    elsif p_filter_column is null then
        execute pg_catalog.format('select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t', p_table)
            into result;
    elsif p_filter_column = 'id' then
        execute pg_catalog.format('select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t where id = $1', p_table)
            into result using p_filter_value::integer;
    else
        execute pg_catalog.format('select coalesce(jsonb_agg(to_jsonb(t)), ''[]''::jsonb) from public.%I t where dia = $1', p_table)
            into result using p_filter_value;
    end if;
    return result;
end;
$$;

create or replace function private.beeweek_insert(p_token text, p_table text, p_data jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare allowed text[];
        account_role text;
        column_names text;
        source_names text;
        new_id integer;
        result jsonb;
begin
    select u.rol into account_role from public.usuarios u
    where u.id = private.beeweek_require_session(p_token);
    if account_role is distinct from 'Administrador' then
        raise exception 'Solo Administrador puede registrar datos academicos'
            using errcode = '42501';
    end if;
    allowed := case p_table
        when 'aulas' then array['numero','capacidad','tipo']
        when 'materias' then array['nombre','creditos','semestre']
        when 'docentes' then array['identificacion','nombre','apellido','email','especialidad']
        when 'estudiantes' then array['identificacion','nombre','apellido','email','matricula','carrera','curso_id']
        when 'cursos' then array['paralelo','num_estudiantes']
        when 'horarios' then array['dia','hora_inicio','hora_fin','materia_id','docente_id','aula_id','curso_id','estado']
        else null end;
    if allowed is null or pg_catalog.jsonb_typeof(p_data) <> 'object'
       or p_data = '{}'::jsonb
       or exists (select 1 from pg_catalog.jsonb_object_keys(p_data) k where k <> all(allowed)) then
        raise exception 'Datos no permitidos' using errcode = '22023';
    end if;
    select pg_catalog.string_agg(pg_catalog.format('%I', k), ', '),
           pg_catalog.string_agg(pg_catalog.format('r.%I', k), ', ')
      into column_names, source_names
      from pg_catalog.jsonb_object_keys(p_data) k;
    execute pg_catalog.format(
        'insert into public.%I (%s) select %s from pg_catalog.jsonb_populate_record(null::public.%I, $1) r returning id',
        p_table, column_names, source_names, p_table)
      into new_id using p_data;
    execute pg_catalog.format('select to_jsonb(t) from public.%I t where id = $1', p_table)
      into result using new_id;
    return result;
end;
$$;

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
        when 'horarios' then array['dia','hora_inicio','hora_fin','materia_id','docente_id','aula_id','curso_id','estado']
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

create or replace function private.beeweek_validar_horario()
returns trigger language plpgsql security definer set search_path = '' as $$
declare alumnos integer;
        aforo integer;
begin
    if tg_op = 'UPDATE' then
        if old.estado = 'Cancelado' then
            raise exception 'Un horario cancelado no se puede modificar.' using errcode = '23514';
        end if;
        if old.estado = 'Publicado' and new.estado = 'Borrador' then
            raise exception 'Un horario publicado no puede volver a borrador.' using errcode = '23514';
        end if;
    end if;
    perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtext(new.dia::text));
    select num_estudiantes into alumnos from public.cursos where id = new.curso_id;
    select capacidad into aforo from public.aulas where id = new.aula_id;
    if alumnos is null or aforo is null or alumnos <= 0 or alumnos > aforo then
        raise exception 'El curso no existe o supera el aforo del aula.' using errcode = '23514';
    end if;
    if new.estado = 'Publicado' and exists (
        select 1 from public.horarios h
        where h.dia = new.dia and h.estado = 'Publicado'
          and h.id is distinct from new.id
          and new.hora_inicio::time < h.hora_fin::time
          and h.hora_inicio::time < new.hora_fin::time
          and (h.docente_id = new.docente_id or h.aula_id = new.aula_id
               or h.curso_id = new.curso_id)
    ) then
        raise exception 'El horario se cruza con otra clase del docente, aula o curso.'
            using errcode = '23514';
    end if;
    return new;
end;
$$;
