-- BeeWeek: acceso a datos academicos solo tras iniciar sesion.
-- Aplicar junto con el cliente Python de esta revision.
create table if not exists private.beeweek_sessions (
    token_hash text primary key,
    user_id bigint not null references public.usuarios(id) on delete cascade,
    expires_at timestamptz not null
);
create index if not exists beeweek_sessions_expiry_idx
    on private.beeweek_sessions(expires_at);
revoke all on private.beeweek_sessions from public, anon, authenticated;

create or replace function private.beeweek_login_session(p_login text, p_password text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare profile jsonb;
        token text;
begin
    profile := private.beeweek_login(p_login, p_password);
    if profile is null then return null; end if;
    token := pg_catalog.encode(extensions.gen_random_bytes(32), 'hex');
    insert into private.beeweek_sessions(token_hash, user_id, expires_at)
    values (pg_catalog.encode(extensions.digest(token, 'sha256'), 'hex'),
            (profile->>'id')::bigint, pg_catalog.now() + interval '12 hours');
    return profile || pg_catalog.jsonb_build_object('session_token', token);
end;
$$;

create or replace function private.beeweek_require_session(p_token text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare account_id bigint;
begin
    if p_token is null or p_token !~ '^[0-9a-f]{64}$' then
        raise exception 'Sesion no valida. Inicia sesion nuevamente.' using errcode = '28000';
    end if;
    select s.user_id into account_id
    from private.beeweek_sessions s
    join public.usuarios u on u.id = s.user_id
    where s.token_hash = pg_catalog.encode(extensions.digest(p_token, 'sha256'), 'hex')
      and s.expires_at > pg_catalog.now() and u.activo;
    if account_id is null then
        raise exception 'Sesion caducada. Inicia sesion nuevamente.' using errcode = '28000';
    end if;
    return account_id;
end;
$$;

create or replace function private.beeweek_list(p_token text, p_table text,
    p_filter_column text default null, p_filter_value text default null)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare result jsonb;
begin
    perform private.beeweek_require_session(p_token);
    if p_table not in ('aulas', 'materias', 'docentes', 'estudiantes', 'cursos', 'horarios')
       or (p_filter_column is not null and p_filter_column not in ('id', 'dia'))
       or (p_filter_column = 'dia' and p_table <> 'horarios') then
        raise exception 'Consulta no permitida' using errcode = '22023';
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
        column_names text;
        source_names text;
        new_id integer;
        result jsonb;
begin
    perform private.beeweek_require_session(p_token);
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

create or replace function private.beeweek_logout(p_token text)
returns void language plpgsql security definer set search_path = '' as $$
begin
    delete from private.beeweek_sessions
    where token_hash = pg_catalog.encode(extensions.digest(p_token, 'sha256'), 'hex');
end;
$$;

create or replace function public.beeweek_login(p_login text, p_password text)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_login_session(p_login, p_password); $$;
create or replace function public.beeweek_list(p_token text, p_table text,
    p_filter_column text default null, p_filter_value text default null)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_list(p_token, p_table, p_filter_column, p_filter_value); $$;
create or replace function public.beeweek_insert(p_token text, p_table text, p_data jsonb)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.beeweek_insert(p_token, p_table, p_data); $$;
create or replace function public.beeweek_logout(p_token text)
returns void language sql security invoker set search_path = ''
as $$ select private.beeweek_logout(p_token); $$;

revoke all on function private.beeweek_login_session(text,text) from public, anon, authenticated;
revoke all on function private.beeweek_require_session(text) from public, anon, authenticated;
revoke all on function private.beeweek_list(text,text,text,text) from public, anon, authenticated;
revoke all on function private.beeweek_insert(text,text,jsonb) from public, anon, authenticated;
revoke all on function private.beeweek_logout(text) from public, anon, authenticated;
revoke all on function public.beeweek_list(text,text,text,text) from public, anon, authenticated;
revoke all on function public.beeweek_insert(text,text,jsonb) from public, anon, authenticated;
revoke all on function public.beeweek_logout(text) from public, anon, authenticated;
grant usage on schema private to anon, authenticated;
grant execute on function private.beeweek_login_session(text,text) to anon, authenticated;
grant execute on function private.beeweek_require_session(text) to anon, authenticated;
grant execute on function private.beeweek_list(text,text,text,text) to anon, authenticated;
grant execute on function private.beeweek_insert(text,text,jsonb) to anon, authenticated;
grant execute on function private.beeweek_logout(text) to anon, authenticated;
grant execute on function public.beeweek_list(text,text,text,text) to anon, authenticated;
grant execute on function public.beeweek_insert(text,text,jsonb) to anon, authenticated;
grant execute on function public.beeweek_logout(text) to anon, authenticated;

alter table public.aulas enable row level security;
alter table public.materias enable row level security;
alter table public.docentes enable row level security;
alter table public.estudiantes enable row level security;
alter table public.cursos enable row level security;
alter table public.horarios enable row level security;
revoke all on public.aulas, public.materias, public.docentes,
    public.estudiantes, public.cursos, public.horarios from public, anon, authenticated;
revoke all on sequence public.aulas_id_seq, public.materias_id_seq,
    public.docentes_id_seq, public.estudiantes_id_seq,
    public.cursos_id_seq, public.horarios_id_seq from anon, authenticated;
