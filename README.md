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
6. `supabase_aulas_unicas.sql`: retira una copia sin uso del aula 101 y evita
   repetir números de aula.
7. `supabase_edicion_recursos.sql`: permite a Administrador editar y eliminar
   aulas y horarios; mantiene las validaciones de aforo y cruces en Supabase.
8. `supabase_estados_horario.sql`: añade Borrador, Publicado y Cancelado. Los
   horarios existentes quedan Publicados; conserva las restricciones de roles y
   valida aforo y cruces al publicar un borrador.
9. `supabase_indice_sesiones.sql`: indexa la relación entre sesiones y usuarios.

Las migraciones se aplican de forma transaccional con la herramienta de Supabase.
Si alguna falla, revisa el mensaje y corrige el problema antes de iniciar la
aplicación actualizada. No ejecutes de nuevo el
antiguo script de autenticación que permitía consultar la tabla de usuarios.

## Comprobaciones

- `python -m unittest discover -s tests -v` comprueba la ruta de acceso protegida
  y la relación estudiante-curso sin modificar la base.
- `python test_conexion.py` comprueba la conexión con una consulta de solo lectura.

En **Reportes**, genera primero la vista de horarios o aulas, elige **CSV** o
**PDF** y pulsa **Exportar reporte**. CSV se abre en Excel y mantiene la
protección frente a fórmulas; PDF permite compartir el reporte formateado.
El tipo **Resumen Institucional** agrega aulas, docentes, cursos y horas
semanales de horarios publicados.

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

## Arquitectura MVC

Las pantallas siguen el flujo **Vista → Controlador → Modelo/datos**. Por ejemplo,
`AulasView` recoge el formulario y muestra la respuesta; `AulasController`
valida los valores y coordina las operaciones; `Aula` representa el recurso y
se usa al guardarlo. `main.py` crea el controlador y se lo entrega a la vista.

Docentes, Estudiantes, el resumen de Inicio y Reportes también obtienen sus
datos mediante controladores. Estudiantes reutiliza la lista de cursos ya
cargada para mostrar el paralelo sin consultar dos veces al abrir la pantalla.

## Patrón de comportamiento: Observer

`HorarioController` avisa a sus observadores cuando Supabase confirma la
creación, edición o eliminación de un horario. `BeeWeekApp` suscribe tres
acciones: actualizar Inicio, sincronizar el Calendario si ya está abierto e
invalidar el reporte anterior para no exportar datos desactualizados. Una
operación rechazada no genera aviso. Los observadores se registran con
`suscribir()` y pueden retirarse con `desuscribir()`.

## Patrón de comportamiento: Strategy

`ExportadorReporte` recibe `ExportarCSV` o `ExportarPDF` y guarda las mismas
columnas y filas con el formato elegido. La implementación está en
`reportes/estrategias_exportacion.py`; la selección se hace en Reportes.

## Patrón de comportamiento: Visitor

`VisitanteResumenInstitucional` recorre los modelos `Aula`, `Docente`, `Curso`
y `HorarioPreparado` mediante `aceptar()`. Calcula capacidad, estudiantes
previstos y horas semanales sin mezclar esos cálculos con la persistencia de
cada modelo. El controlador prepara los modelos y Reportes muestra el
«Resumen Institucional», exportable a CSV o PDF.

## Patrón de comportamiento: State

En Registro de Horario puedes guardar un horario **Publicado** o **Borrador**.
Un borrador no ocupa el aula en el calendario; al publicarlo, Supabase revisa
cruces y aforo otra vez. Un horario publicado se puede **Cancelar** y deja de
aparecer en el calendario y los reportes. Un cancelado no se puede editar ni
reactivar. `modelos/estado_horario.py` define estas acciones y la base aplica
las mismas restricciones aunque alguien intente cambiar el estado fuera de la
interfaz.

El acceso a las tablas academicas requiere una sesion iniciada y permisos por
rol. Como el registro permite un correo institucional sin verificar su
existencia, usa datos ficticios para la demostracion. La aplicacion tampoco
ofrece recuperacion de contraseña.
