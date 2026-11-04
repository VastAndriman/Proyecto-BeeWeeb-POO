-- Permisos de BeeWeek: Administrador gestiona; Docente y Estudiante consultan.
-- La comprobacion se realiza en la base, no depende de ocultar botones.
create or replace function private.beeweek_list(p_token text, p_table text,
    p_filter_column text default null, p_filter_value text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare result jsonb;
        account_role text;
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

    -- El calendario solo necesita los nombres de los docentes.
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

    if p_filter_column is null then
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
        when 'horarios' then array['dia','hora_inicio','hora_fin','materia_id','docente_id','aula_id','curso_id']
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
