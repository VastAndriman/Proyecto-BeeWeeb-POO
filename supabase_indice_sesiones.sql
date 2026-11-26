-- Acelera las comprobaciones de sesiones al consultar o borrar un usuario.
create index if not exists beeweek_sessions_user_id_idx
    on private.beeweek_sessions(user_id);
