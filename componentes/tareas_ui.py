"""Ejecuta consultas remotas sin bloquear el hilo de Tkinter."""

from concurrent.futures import ThreadPoolExecutor
from tkinter import TclError


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="beeweek-red")


def iniciar_tarea(widget, trabajo, al_terminar, al_fallar):
    """Trabajo en segundo plano; los callbacks siempre corren en la interfaz."""
    futuro = _executor.submit(trabajo)

    def revisar():
        try:
            if not widget.winfo_exists():
                return
            if not futuro.done():
                widget.after(50, revisar)
                return
            try:
                resultado = futuro.result()
            except Exception as error:
                al_fallar(error)
            else:
                al_terminar(resultado)
        except TclError:
            # La ventana se cerró antes de recibir la respuesta de la red.
            return

    widget.after(50, revisar)
    return futuro
