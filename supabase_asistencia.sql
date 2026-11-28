-- Asistencia por clase y fecha. Aplicar despues de supabase_clases_docente.sql.
create table if not exists private.beeweek_asistencia (
    horario_id integer not null references public.horarios(id) on delete cascade,
    fecha date not null,
    usuario_id bigint not null references public.usuarios(id) on delete cascade,
    estado text not null check (estado in ('Presente', 'Ausente', 'Atrasado', 'Justificado')),
    registrado_por bigint not null references public.usuarios(id),
    actualizado_en timestamptz not null default now(),
    primary key (horario_id, fecha, usuario_id)
);
create index if not exists beeweek_asistencia_alumno_idx
    on private.beeweek_asistencia(usuario_id, fecha desc);
revoke all on private.beeweek_asistencia from public, anon, authenticated;

create or replace function private.beeweek_attendance_require_teacher(
    p_token text, p_horario_id integer, p_fecha date)
returns bigint language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        dia text;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Docente') then
        raise exception 'Solo Docente puede gestionar asistencia' using errcode = '42501';
    end if;
    if p_fecha is null or p_fecha > (now() at time zone 'America/Guayaquil')::date
       or p_horario_id is null then
        raise exception 'Selecciona una clase y fecha valida' using errcode = '22023';
    end if;
    select h.dia into dia from public.horarios h
    join public.docentes d on d.id = h.docente_id
    where h.id = p_horario_id and h.estado = 'Publicado' and d.usuario_id = actor_id;
    if dia is null then
        raise exception 'La clase no pertenece a este docente' using errcode = '42501';
    end if;
    if dia <> (array['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])
                  [extract(isodow from p_fecha)::integer] then
        raise exception 'La fecha no coincide con el dia de la clase' using errcode = '22023';
    end if;
    return actor_id;
end;
$$;

create or replace function private.beeweek_attendance_roster(
    p_token text, p_horario_id integer, p_fecha date)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare result jsonb;
begin
    perform private.beeweek_attendance_require_teacher(p_token, p_horario_id, p_fecha);
    with alumnos as (
        select i.usuario_id from public.horarios h
        join private.beeweek_inscripciones i
          on i.materia_id = h.materia_id and i.curso_id = h.curso_id
        where h.id = p_horario_id and i.estado = 'Inscrito'
          and (i.inscrito_en at time zone 'America/Guayaquil')::date <= p_fecha
        union
        select a.usuario_id from private.beeweek_asistencia a
        where a.horario_id = p_horario_id and a.fecha = p_fecha
    )
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'usuario_id', u.id, 'nombre', u.nombre, 'apellido', u.apellido,
        'estado', a.estado) order by u.apellido, u.nombre), '[]'::jsonb)
    into result from alumnos x
    join public.usuarios u on u.id = x.usuario_id
    left join private.beeweek_asistencia a on a.horario_id = p_horario_id
      and a.fecha = p_fecha and a.usuario_id = u.id;
    return result;
end;
$$;

create or replace function private.beeweek_attendance_save(
    p_token text, p_horario_id integer, p_fecha date, p_registros jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        registro record;
        total integer;
        cantidad integer := 0;
begin
    actor_id := private.beeweek_attendance_require_teacher(p_token, p_horario_id, p_fecha);
    if pg_catalog.jsonb_typeof(p_registros) <> 'array' then
        raise exception 'Lista de asistencia invalida' using errcode = '22023';
    end if;
    total := pg_catalog.jsonb_array_length(p_registros);
    if total = 0 or total > 200 or (
        select count(distinct (r->>'usuario_id')) from pg_catalog.jsonb_array_elements(p_registros) r
    ) <> total then
        raise exception 'Lista vacia, duplicada o demasiado grande' using errcode = '22023';
    end if;
    for registro in select * from pg_catalog.jsonb_to_recordset(p_registros)
        as x(usuario_id bigint, estado text) loop
        if registro.usuario_id is null or registro.estado is null
           or registro.estado not in ('Presente','Ausente','Atrasado','Justificado')
           or not exists (
               select 1 from public.horarios h
               join private.beeweek_inscripciones i
                 on i.materia_id = h.materia_id and i.curso_id = h.curso_id
               where h.id = p_horario_id and i.usuario_id = registro.usuario_id
                 and i.estado = 'Inscrito'
                 and (i.inscrito_en at time zone 'America/Guayaquil')::date <= p_fecha
               union
               select 1 from private.beeweek_asistencia a
               where a.horario_id = p_horario_id and a.fecha = p_fecha
                 and a.usuario_id = registro.usuario_id
           ) then
            raise exception 'Alumno o estado de asistencia no permitido' using errcode = '42501';
        end if;
        insert into private.beeweek_asistencia
            (horario_id, fecha, usuario_id, estado, registrado_por)
        values (p_horario_id, p_fecha, registro.usuario_id, registro.estado, actor_id)
        on conflict (horario_id, fecha, usuario_id) do update
        set estado = excluded.estado, registrado_por = excluded.registrado_por,
            actualizado_en = now();
        cantidad := cantidad + 1;
    end loop;
    return pg_catalog.jsonb_build_object('guardados', cantidad);
end;
$$;

create or replace function private.beeweek_student_attendance(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        result jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Estudiante') then
        raise exception 'Solo Estudiante puede consultar su asistencia' using errcode = '42501';
    end if;
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'fecha', a.fecha, 'materia', m.nombre, 'curso', c.paralelo,
        'estado', a.estado) order by a.fecha desc, m.nombre), '[]'::jsonb)
    into result from private.beeweek_asistencia a
    join public.horarios h on h.id = a.horario_id
    join public.materias m on m.id = h.materia_id
    join public.cursos c on c.id = h.curso_id
    where a.usuario_id = actor_id;
    return result;
end;
$$;

create or replace function private.beeweek_admin_attendance(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        result jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Administrador') then
        raise exception 'Solo Administrador puede consultar el resumen' using errcode = '42501';
    end if;
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'fecha', x.fecha, 'materia', x.materia, 'curso', x.curso,
        'hora', x.hora,
        'presentes', x.presentes, 'ausentes', x.ausentes,
        'atrasados', x.atrasados, 'justificados', x.justificados)
        order by x.fecha desc, x.materia), '[]'::jsonb)
    into result from (
        select a.fecha, m.nombre as materia, c.paralelo as curso,
               pg_catalog.to_char(h.hora_inicio, 'HH24:MI') || '-' ||
               pg_catalog.to_char(h.hora_fin, 'HH24:MI') as hora,
               count(*) filter (where a.estado = 'Presente') as presentes,
               count(*) filter (where a.estado = 'Ausente') as ausentes,
               count(*) filter (where a.estado = 'Atrasado') as atrasados,
               count(*) filter (where a.estado = 'Justificado') as justificados
        from private.beeweek_asistencia a
        join public.horarios h on h.id = a.horario_id
        join public.materias m on m.id = h.materia_id
        join public.cursos c on c.id = h.curso_id
        group by a.fecha, h.id, m.nombre, c.paralelo
    ) x;
    return result;
end;
$$;

create or replace function public.beeweek_attendance_roster(
    p_token text, p_horario_id integer, p_fecha date)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_attendance_roster(p_token,p_horario_id,p_fecha); $$;
create or replace function public.beeweek_attendance_save(
    p_token text, p_horario_id integer, p_fecha date, p_registros jsonb)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_attendance_save(p_token,p_horario_id,p_fecha,p_registros); $$;
create or replace function public.beeweek_student_attendance(p_token text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_student_attendance(p_token); $$;
create or replace function public.beeweek_admin_attendance(p_token text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_admin_attendance(p_token); $$;

revoke all on function private.beeweek_attendance_require_teacher(text,integer,date) from public,anon,authenticated;
revoke all on function private.beeweek_attendance_roster(text,integer,date) from public,anon,authenticated;
revoke all on function private.beeweek_attendance_save(text,integer,date,jsonb) from public,anon,authenticated;
revoke all on function private.beeweek_student_attendance(text) from public,anon,authenticated;
revoke all on function private.beeweek_admin_attendance(text) from public,anon,authenticated;
revoke all on function public.beeweek_attendance_roster(text,integer,date) from public,anon,authenticated;
revoke all on function public.beeweek_attendance_save(text,integer,date,jsonb) from public,anon,authenticated;
revoke all on function public.beeweek_student_attendance(text) from public,anon,authenticated;
revoke all on function public.beeweek_admin_attendance(text) from public,anon,authenticated;
grant execute on function private.beeweek_attendance_require_teacher(text,integer,date) to anon,authenticated;
grant execute on function private.beeweek_attendance_roster(text,integer,date) to anon,authenticated;
grant execute on function private.beeweek_attendance_save(text,integer,date,jsonb) to anon,authenticated;
grant execute on function private.beeweek_student_attendance(text) to anon,authenticated;
grant execute on function private.beeweek_admin_attendance(text) to anon,authenticated;
grant execute on function public.beeweek_attendance_roster(text,integer,date) to anon,authenticated;
grant execute on function public.beeweek_attendance_save(text,integer,date,jsonb) to anon,authenticated;
grant execute on function public.beeweek_student_attendance(text) to anon,authenticated;
grant execute on function public.beeweek_admin_attendance(text) to anon,authenticated;
