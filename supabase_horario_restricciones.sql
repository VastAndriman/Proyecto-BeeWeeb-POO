-- Evita horarios incompletos y valores imposibles aun si se escribe fuera de BeeWeek.
alter table public.horarios
    alter column dia set not null,
    alter column hora_inicio set not null,
    alter column hora_fin set not null,
    alter column materia_id set not null,
    alter column docente_id set not null,
    alter column aula_id set not null,
    alter column curso_id set not null;

alter table public.horarios add constraint beeweek_horario_dia_ck
    check (dia in ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'));
alter table public.cursos add constraint beeweek_curso_alumnos_ck
    check (num_estudiantes > 0);
alter table public.aulas add constraint beeweek_aula_capacidad_ck
    check (capacidad > 0);
