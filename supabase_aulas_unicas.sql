-- Conserva el aula 101 usada por los horarios y elimina su copia exacta sin uso.
delete from public.aulas a
where a.id = 3 and a.numero = '101' and a.capacidad = 40 and a.tipo = 'Laboratorio'
  and exists (select 1 from public.aulas original
              where original.id = 2 and original.numero = a.numero
                and original.capacidad = a.capacidad and original.tipo = a.tipo)
  and not exists (select 1 from public.horarios h where h.aula_id = a.id);

-- Evita diferencias solo de espacios o mayusculas en los identificadores.
create unique index if not exists beeweek_aula_numero_unico_idx
    on public.aulas (pg_catalog.lower(pg_catalog.btrim(numero)));
