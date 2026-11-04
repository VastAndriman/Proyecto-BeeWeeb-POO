# BeeWeek

Aplicación de escritorio para registrar recursos académicos y crear horarios con
validación de cruces y aforo.

## Instalación

1. Instala Python 3.13 y las dependencias: `pip install -r requirements.txt`.
2. Copia `.env.example` a `.env` y coloca la URL y la clave pública de Supabase.
   La clave `service_role` nunca debe ir en esta aplicación.
3. Ejecuta `python main.py`.

## Migración de la base existente

Antes de ejecutar esta versión de BeeWeek, haz una copia de seguridad en Supabase
y aplica en su SQL Editor, en este orden:

1. `supabase_login.sql`: restringe la tabla de usuarios y habilita funciones de
   registro e inicio de sesión. Conserva las cuentas existentes y cambia su hash
   antiguo a bcrypt cuando cada persona inicia sesión correctamente. Desactiva
   las dos cuentas de ejemplo cuyas contraseñas estaban publicadas en el
   script anterior; no afecta a las cuentas personales.
2. `supabase_relaciones.sql`: añade la relación opcional entre estudiante y curso,
   las claves foráneas de horarios y una validación de cruces y aforo en la base.
3. `supabase_horario_restricciones.sql`: exige datos completos y valores válidos
   para horarios, cursos y aulas.
4. `supabase_sesiones_academicas.sql`: crea sesiones temporales para el login y
   protege las seis tablas academicas con RLS y sin acceso directo de la clave
   publica. Esta migracion y el cliente Python actualizado deben usarse juntos.
5. `supabase_roles_academicos.sql`: solo Administrador puede registrar recursos
   y horarios. Docente y Estudiante consultan el calendario; no pueden ver la
   lista de estudiantes y de docentes solo reciben los nombres necesarios.

Las migraciones se aplican de forma transaccional con la herramienta de Supabase.
Si alguna falla, revisa el mensaje y corrige el problema antes de iniciar la
aplicación actualizada. No ejecutes de nuevo el
antiguo script de autenticación que permitía consultar la tabla de usuarios.

## Comprobaciones

- `python -m unittest discover -s tests -v` comprueba la ruta de acceso protegida
  y la relación estudiante-curso sin modificar la base.
- `python test_conexion.py` comprueba la conexión con una consulta de solo lectura.

## Patrones creacionales

- **Singleton:** `SupabaseConnection.get_client()` comparte el cliente de Supabase.
- **Factory Method:** `CreadorDocente` y `CreadorEstudiante` crean los modelos
  concretos; las vistas de registro usan su método común `registrar()`.
- **Builder:** `HorarioBuilder` prepara un `HorarioPreparado` completo antes de
  que `HorarioController` consulte aforo y cruces y lo guarde.

La implementación está en `patrones_creacionales_beeweek.py`. Se puede ejecutar
`python patrones_creacionales_beeweek.py` para ver una demostración sin conexión
ni cambios en la base. Las pruebas de integración local están en
`tests/test_patrones_creacionales.py`.

El acceso a las tablas academicas requiere una sesion iniciada y permisos por
rol. Como el registro permite un correo institucional sin verificar su
existencia, usa datos ficticios para la demostracion. La aplicacion tampoco
ofrece recuperacion de contraseña.
