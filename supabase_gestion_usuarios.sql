-- Aplicar despues de supabase_login.sql y supabase_sesiones_academicas.sql.
-- Solo una sesion activa de Administrador puede consultar y cambiar roles.
create table if not exists private.beeweek_role_audit (
    id bigint generated always as identity primary key,
    actor_id bigint not null references public.usuarios(id),
    usuario_id bigint not null references public.usuarios(id),
    rol_anterior text not null,
    rol_nuevo text not null,
    cambiado_en timestamptz not null default now()
);
revoke all on private.beeweek_role_audit from public, anon, authenticated;

create or replace function private.beeweek_admin_list_users(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        result jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Administrador') then
        raise exception 'Solo un administrador puede consultar las cuentas' using errcode = '42501';
    end if;
    select coalesce(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object(
        'id', id, 'nombre', nombre, 'apellido', apellido, 'username', username,
        'email', email, 'rol', rol, 'activo', activo) order by nombre, apellido), '[]'::jsonb)
    into result from public.usuarios;
    return result;
end;
$$;

create or replace function private.beeweek_admin_set_role(
    p_token text, p_user_id bigint, p_role text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare actor_id bigint;
        previous_role text;
        result jsonb;
begin
    actor_id := private.beeweek_require_session(p_token);
    if not exists (select 1 from public.usuarios where id = actor_id and rol = 'Administrador') then
        raise exception 'Solo un administrador puede cambiar roles' using errcode = '42501';
    end if;
    if p_role is null or p_role not in ('Administrador', 'Docente', 'Estudiante')
       or p_user_id is null or p_user_id = actor_id then
        raise exception 'Cambio de rol no permitido' using errcode = '22023';
    end if;
    select rol into previous_role from public.usuarios
    where id = p_user_id and activo for update;
    if not found then
        raise exception 'La cuenta no existe o esta desactivada' using errcode = 'P0002';
    end if;
    if previous_role = p_role then
        raise exception 'La cuenta ya tiene ese rol' using errcode = '22023';
    end if;
    update public.usuarios set rol = p_role where id = p_user_id;
    delete from private.beeweek_sessions where user_id = p_user_id;
    insert into private.beeweek_role_audit(actor_id, usuario_id, rol_anterior, rol_nuevo)
    values (actor_id, p_user_id, previous_role, p_role);
    select pg_catalog.jsonb_build_object('id', id, 'username', username, 'rol', rol)
    into result from public.usuarios where id = p_user_id;
    return result;
end;
$$;

create or replace function public.beeweek_admin_list_users(p_token text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_admin_list_users(p_token); $$;
create or replace function public.beeweek_admin_set_role(
    p_token text, p_user_id bigint, p_role text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_admin_set_role(p_token, p_user_id, p_role); $$;

revoke all on function private.beeweek_admin_list_users(text) from public, anon, authenticated;
revoke all on function private.beeweek_admin_set_role(text,bigint,text) from public, anon, authenticated;
revoke all on function public.beeweek_admin_list_users(text) from public, anon, authenticated;
revoke all on function public.beeweek_admin_set_role(text,bigint,text) from public, anon, authenticated;
grant execute on function private.beeweek_admin_list_users(text) to anon, authenticated;
grant execute on function private.beeweek_admin_set_role(text,bigint,text) to anon, authenticated;
grant execute on function public.beeweek_admin_list_users(text) to anon, authenticated;
grant execute on function public.beeweek_admin_set_role(text,bigint,text) to anon, authenticated;
