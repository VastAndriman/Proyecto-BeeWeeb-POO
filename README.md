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

Las migraciones se aplican de forma transaccional con la herramienta de Supabase.
Si alguna falla, revisa el mensaje y corrige el problema antes de iniciar la
aplicación actualizada. No ejecutes de nuevo el
antiguo script de autenticación que permitía consultar la tabla de usuarios.

## Comprobaciones

- `python -m unittest discover -s tests -v` comprueba la ruta de acceso protegida
  y la relación estudiante-curso sin modificar la base.
- `python test_conexion.py` comprueba la conexión con una consulta de solo lectura.

Esta migración protege las credenciales de la tabla `usuarios`, pero las demás
tablas aún requieren políticas de acceso por usuario. No uses datos personales
reales de terceros hasta completar esa protección. La aplicación todavía no
verifica que el correo institucional exista ni ofrece recuperación de contraseña.
