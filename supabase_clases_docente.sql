-- Cuenta docente vinculada a su ficha academica, sin exponer otras clases.
-- Aplicar despues de supabase_inscripciones.sql y supabase_gestion_usuarios.sql.
alter table public.docentes add column if not exists usuario_id bigint;
create unique index if not exists beeweek_docentes_usuario_uidx
    on public.docentes(usuario_id) where usuario_id is not null;
do $$ begin
    if not exists (select 1 from pg_catalog.pg_constraint
                   where conname = 'beeweek_docentes_usuario_fk') then
        alter table public.docentes add constraint beeweek_docentes_usuario_fk
            foreign key (usuario_id) references public.usuarios(id) on delete set null;
    end if;
end $$;

create or replace function private.beeweek_teacher_classes(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        teacher_id integer;
        classes jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Docente') then
        raise exception 'Solo Docente puede consultar sus clases' using errcode = '42501';
    end if;
    -- La identificacion del registro es autodeclarada: solo vale el vinculo
    -- que un administrador haya aprobado expresamente.
    select d.id into teacher_id from public.docentes d
    where d.usuario_id = actor_id;
    if teacher_id is null then
        return pg_catalog.jsonb_build_object('vinculado', false, 'clases', '[]'::jsonb);
    end if;
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'horario_id', h.id, 'dia', h.dia,
        'hora_inicio', pg_catalog.to_char(h.hora_inicio, 'HH24:MI'),
        'hora_fin', pg_catalog.to_char(h.hora_fin, 'HH24:MI'),
        'materia', m.nombre, 'curso', c.paralelo, 'aula', a.numero,
        'estudiantes', (
            select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
                'nombre', u.nombre, 'apellido', u.apellido) order by u.apellido, u.nombre),
                '[]'::jsonb)
            from private.beeweek_inscripciones i
            join public.usuarios u on u.id = i.usuario_id and u.activo
            where i.materia_id = h.materia_id and i.curso_id = h.curso_id
              and i.estado = 'Inscrito')
    ) order by h.dia, h.hora_inicio), '[]'::jsonb)
    into classes from public.horarios h
    join public.materias m on m.id = h.materia_id
    join public.cursos c on c.id = h.curso_id
    join public.aulas a on a.id = h.aula_id
    where h.docente_id = teacher_id and h.estado = 'Publicado';
    return pg_catalog.jsonb_build_object('vinculado', true, 'clases', classes);
end;
$$;

create or replace function private.beeweek_admin_link_teacher(
    p_token text, p_user_id bigint, p_docente_id integer)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        linked_id integer;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Administrador') then
        raise exception 'Solo Administrador puede vincular docentes' using errcode = '42501';
    end if;
    if p_user_id is null or p_docente_id is null or p_docente_id <= 0
       or not exists (select 1 from public.usuarios
                      where id = p_user_id and rol = 'Docente' and activo) then
        raise exception 'Selecciona una cuenta docente activa' using errcode = '22023';
    end if;
    if exists (select 1 from public.docentes
               where usuario_id = p_user_id and id <> p_docente_id) then
        raise exception 'Esa cuenta ya esta vinculada a otro docente' using errcode = '23505';
    end if;
    update public.docentes set usuario_id = p_user_id
    where id = p_docente_id and (usuario_id is null or usuario_id = p_user_id)
    returning id into linked_id;
    if linked_id is null then
        raise exception 'El docente no existe o ya tiene otra cuenta' using errcode = '23505';
    end if;
    return pg_catalog.jsonb_build_object('docente_id', linked_id, 'usuario_id', p_user_id);
end;
$$;

create or replace function public.beeweek_teacher_classes(p_token text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_teacher_classes(p_token); $$;
create or replace function public.beeweek_admin_link_teacher(
    p_token text, p_user_id bigint, p_docente_id integer)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_admin_link_teacher(p_token, p_user_id, p_docente_id); $$;

revoke all on function private.beeweek_teacher_classes(text) from public, anon, authenticated;
revoke all on function private.beeweek_admin_link_teacher(text,bigint,integer) from public, anon, authenticated;
revoke all on function public.beeweek_teacher_classes(text) from public, anon, authenticated;
revoke all on function public.beeweek_admin_link_teacher(text,bigint,integer) from public, anon, authenticated;
grant execute on function private.beeweek_teacher_classes(text) to anon, authenticated;
grant execute on function private.beeweek_admin_link_teacher(text,bigint,integer) to anon, authenticated;
grant execute on function public.beeweek_teacher_classes(text) to anon, authenticated;
grant execute on function public.beeweek_admin_link_teacher(text,bigint,integer) to anon, authenticated;
