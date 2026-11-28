-- Inscripcion voluntaria a materias con horarios publicados.
-- Aplicar despues de supabase_sesiones_academicas.sql y supabase_estados_horario.sql.
create table if not exists private.beeweek_inscripciones (
    usuario_id bigint not null references public.usuarios(id) on delete cascade,
    materia_id integer not null references public.materias(id) on delete restrict,
    curso_id integer not null references public.cursos(id) on delete restrict,
    estado text not null check (estado in ('Inscrito', 'Retirado')),
    inscrito_en timestamptz not null default now(),
    retirado_en timestamptz,
    primary key (usuario_id, materia_id, curso_id)
);
create index if not exists beeweek_inscripciones_cupo_idx
    on private.beeweek_inscripciones(materia_id, curso_id)
    where estado = 'Inscrito';
revoke all on private.beeweek_inscripciones from public, anon, authenticated;

create or replace function private.beeweek_student_catalog(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        ofertas jsonb;
        inscripciones jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Estudiante') then
        raise exception 'Solo Estudiante puede consultar sus materias' using errcode = '42501';
    end if;

    with disponibles as (
        select h.materia_id, h.curso_id,
               min(a.capacidad) as capacidad_aula,
               pg_catalog.string_agg(
                   h.dia || ' ' || pg_catalog.to_char(h.hora_inicio, 'HH24:MI') ||
                   '-' || pg_catalog.to_char(h.hora_fin, 'HH24:MI'), ', '
                   order by h.dia, h.hora_inicio) as horario
        from public.horarios h
        join public.aulas a on a.id = h.aula_id
        where h.estado = 'Publicado'
        group by h.materia_id, h.curso_id
    )
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'materia_id', d.materia_id, 'curso_id', d.curso_id,
        'materia', m.nombre, 'curso', c.paralelo, 'creditos', m.creditos,
        'horario', d.horario,
        'cupos', greatest(0,
            least(d.capacidad_aula, c.num_estudiantes) -
            (select count(*) from private.beeweek_inscripciones i
             where i.materia_id = d.materia_id and i.curso_id = d.curso_id
               and i.estado = 'Inscrito'))
    ) order by m.nombre, c.paralelo), '[]'::jsonb)
    into ofertas
    from disponibles d
    join public.materias m on m.id = d.materia_id
    join public.cursos c on c.id = d.curso_id;

    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'materia_id', i.materia_id, 'curso_id', i.curso_id,
        'materia', m.nombre, 'curso', c.paralelo,
        'inscrito_en', i.inscrito_en) order by m.nombre), '[]'::jsonb)
    into inscripciones from private.beeweek_inscripciones i
    join public.materias m on m.id = i.materia_id
    join public.cursos c on c.id = i.curso_id
    where i.usuario_id = actor_id and i.estado = 'Inscrito';
    return pg_catalog.jsonb_build_object('ofertas', ofertas, 'inscripciones', inscripciones);
end;
$$;

create or replace function private.beeweek_student_enroll(
    p_token text, p_materia_id integer, p_curso_id integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        limite integer;
        ocupados integer;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Estudiante') then
        raise exception 'Solo Estudiante puede inscribirse' using errcode = '42501';
    end if;
    if p_materia_id is null or p_curso_id is null or p_materia_id <= 0 or p_curso_id <= 0 then
        raise exception 'Selecciona una materia y un curso validos' using errcode = '22023';
    end if;
    perform pg_catalog.pg_advisory_xact_lock(p_materia_id, p_curso_id);
    select least(min(a.capacidad), max(c.num_estudiantes)) into limite
    from public.horarios h
    join public.aulas a on a.id = h.aula_id
    join public.cursos c on c.id = h.curso_id
    where h.materia_id = p_materia_id and h.curso_id = p_curso_id
      and h.estado = 'Publicado';
    if limite is null or limite <= 0 then
        raise exception 'La materia no tiene un horario publicado' using errcode = '22023';
    end if;
    if exists (select 1 from private.beeweek_inscripciones
               where usuario_id = actor_id and materia_id = p_materia_id
                 and curso_id = p_curso_id and estado = 'Inscrito') then
        raise exception 'Ya estas inscrito en esta materia' using errcode = '23505';
    end if;
    select count(*) into ocupados from private.beeweek_inscripciones
    where materia_id = p_materia_id and curso_id = p_curso_id and estado = 'Inscrito';
    if ocupados >= limite then
        raise exception 'No quedan cupos disponibles' using errcode = '23514';
    end if;
    if exists (
        select 1 from public.horarios nuevo
        join private.beeweek_inscripciones i on i.usuario_id = actor_id and i.estado = 'Inscrito'
        join public.horarios actual on actual.materia_id = i.materia_id
            and actual.curso_id = i.curso_id and actual.estado = 'Publicado'
        where nuevo.materia_id = p_materia_id and nuevo.curso_id = p_curso_id
          and nuevo.estado = 'Publicado' and nuevo.dia = actual.dia
          and nuevo.hora_inicio < actual.hora_fin
          and actual.hora_inicio < nuevo.hora_fin
    ) then
        raise exception 'La materia se cruza con otra de tus clases' using errcode = '23514';
    end if;
    insert into private.beeweek_inscripciones
        (usuario_id, materia_id, curso_id, estado, inscrito_en, retirado_en)
    values (actor_id, p_materia_id, p_curso_id, 'Inscrito', now(), null)
    on conflict (usuario_id, materia_id, curso_id) do update
    set estado = 'Inscrito', inscrito_en = now(), retirado_en = null;
    return pg_catalog.jsonb_build_object('materia_id', p_materia_id,
        'curso_id', p_curso_id, 'estado', 'Inscrito');
end;
$$;

create or replace function private.beeweek_student_withdraw(
    p_token text, p_materia_id integer, p_curso_id integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Estudiante') then
        raise exception 'Solo Estudiante puede retirarse' using errcode = '42501';
    end if;
    update private.beeweek_inscripciones
    set estado = 'Retirado', retirado_en = now()
    where usuario_id = actor_id and materia_id = p_materia_id
      and curso_id = p_curso_id and estado = 'Inscrito';
    if not found then
        raise exception 'No tienes una inscripcion activa en esa materia' using errcode = 'P0002';
    end if;
    return pg_catalog.jsonb_build_object('materia_id', p_materia_id,
        'curso_id', p_curso_id, 'estado', 'Retirado');
end;
$$;

create or replace function public.beeweek_student_catalog(p_token text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_student_catalog(p_token); $$;
create or replace function public.beeweek_student_enroll(
    p_token text, p_materia_id integer, p_curso_id integer)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_student_enroll(p_token, p_materia_id, p_curso_id); $$;
create or replace function public.beeweek_student_withdraw(
    p_token text, p_materia_id integer, p_curso_id integer)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_student_withdraw(p_token, p_materia_id, p_curso_id); $$;

revoke all on function private.beeweek_student_catalog(text) from public, anon, authenticated;
revoke all on function private.beeweek_student_enroll(text,integer,integer) from public, anon, authenticated;
revoke all on function private.beeweek_student_withdraw(text,integer,integer) from public, anon, authenticated;
revoke all on function public.beeweek_student_catalog(text) from public, anon, authenticated;
revoke all on function public.beeweek_student_enroll(text,integer,integer) from public, anon, authenticated;
revoke all on function public.beeweek_student_withdraw(text,integer,integer) from public, anon, authenticated;
grant execute on function private.beeweek_student_catalog(text) to anon, authenticated;
grant execute on function private.beeweek_student_enroll(text,integer,integer) to anon, authenticated;
grant execute on function private.beeweek_student_withdraw(text,integer,integer) to anon, authenticated;
grant execute on function public.beeweek_student_catalog(text) to anon, authenticated;
grant execute on function public.beeweek_student_enroll(text,integer,integer) to anon, authenticated;
grant execute on function public.beeweek_student_withdraw(text,integer,integer) to anon, authenticated;
