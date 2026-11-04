-- BeeWeek: relaciones y validación de horarios en la base.
-- Ejecutar en el SQL Editor de Supabase después de revisar datos existentes.

create schema if not exists private;
alter table public.estudiantes add column if not exists curso_id integer;

do $$
begin
    if not exists (select 1 from pg_catalog.pg_constraint where conname = 'beeweek_estudiante_curso_fk') then
        alter table public.estudiantes add constraint beeweek_estudiante_curso_fk
            foreign key (curso_id) references public.cursos(id) on delete restrict;
    end if;
    if not exists (select 1 from pg_catalog.pg_constraint where conname = 'beeweek_horario_horas_ck') then
        alter table public.horarios add constraint beeweek_horario_horas_ck
            check (hora_inicio::time < hora_fin::time);
    end if;
end;
$$;

create index if not exists beeweek_estudiante_curso_idx on public.estudiantes(curso_id);
create index if not exists beeweek_horario_curso_idx on public.horarios(curso_id);
create index if not exists beeweek_horario_aula_idx on public.horarios(aula_id);
create index if not exists beeweek_horario_docente_idx on public.horarios(docente_id);
create index if not exists beeweek_horario_materia_idx on public.horarios(materia_id);

create or replace function private.beeweek_validar_horario()
returns trigger language plpgsql security definer set search_path = '' as $$
declare
    alumnos integer;
    aforo integer;
begin
    -- Serializa las altas y modificaciones del mismo día para evitar dos reservas simultáneas.
    perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtext(new.dia::text));
    select num_estudiantes into alumnos from public.cursos where id = new.curso_id;
    select capacidad into aforo from public.aulas where id = new.aula_id;
    if alumnos is null or aforo is null or alumnos <= 0 or alumnos > aforo then
        raise exception 'El curso no existe o supera el aforo del aula.' using errcode = '23514';
    end if;
    if exists (
        select 1 from public.horarios h
        where h.dia = new.dia
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

revoke all on function private.beeweek_validar_horario() from public, anon, authenticated;
drop trigger if exists beeweek_horario_validar on public.horarios;
create trigger beeweek_horario_validar
before insert or update on public.horarios
for each row execute function private.beeweek_validar_horario();

