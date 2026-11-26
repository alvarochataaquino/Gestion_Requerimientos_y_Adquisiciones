# ============================================================================
# MÓDULO: INICIO DEL APLICATIVO / PUNTO DE ENTRADA
#   La UI se crea una sola vez; main.py no gestiona tablas ni credenciales.
#   La conexión PostgreSQL se configura después desde el diálogo de la aplicación.
#   PyInstaller utiliza este mismo módulo para iniciar la compilación de Windows.
# ============================================================================

"""Punto de entrada para ejecutar con python main.py o PyInstaller onefile."""
import tkinter as tk
from gestion_app.frontend.ui import GestionApp

# Esta guarda evita abrir una ventana al importar el modulo desde otras herramientas.
if __name__ == '__main__':
    # Tk debe instanciarse una sola vez; root es la ventana principal.
    root=tk.Tk()
    # Evita tamaños que ocultarían formularios o la barra lateral.
    root.minsize(1050, 700)
    # Construye todos los elementos visuales sobre la misma ventana raíz.
    GestionApp(root)
    # El bucle atiende eventos hasta que el usuario cierra la aplicacion.
    root.mainloop()
