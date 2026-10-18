from modelos.aula import Aula

# Creamos un objeto Aula de prueba
nueva_aula = Aula(numero="101", capacidad=40, tipo="Laboratorio")

# Intentamos guardarlo en Supabase
try:
    nueva_aula.guardar()
    print("¡Conexión exitosa! El aula se guardó en Supabase.")
except Exception as e:
    print(f"Ocurrió un error al conectar o guardar: {e}")