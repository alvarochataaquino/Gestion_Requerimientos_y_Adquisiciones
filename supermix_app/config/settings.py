# ============================================================================
# MÓDULO: CONFIGURACIÓN PERSISTENTE DEL USUARIO
#   El ejemplo no se utiliza como contraseña fija: los valores se guardan en el perfil.
#   AVISO: el JSON de conexión se escribe sin cifrar la contraseña; debe protegerse.
#   APPDATA en Windows: el archivo de credenciales no forma parte del paquete ZIP.
# ============================================================================

"""Configuración local por usuario, fuera del ejecutable."""
import json
import os
from pathlib import Path


# -----------------------------------------------------------------
# FUNCIÓN: config_path
# Objetivo: Determina dónde guardar parámetros por perfil, fuera del ejecutable.
# Entradas: APPDATA en Windows; ~/.config en sistemas Unix.
# Salida/reglas: Devuelve Path a SupermixGDI/conexion.json.
# -----------------------------------------------------------------
def config_path():
    """Determina la ruta del archivo local de conexion, separada del ejecutable."""
    # La ruta depende del usuario, no de la carpeta donde se extrajo el ZIP.
    return Path(os.environ.get('APPDATA', str(Path.home() / '.config'))) / 'SupermixGDI' / 'conexion.json'


# -----------------------------------------------------------------
# FUNCIÓN: default_config
# Objetivo: Define la configuración inicial sugerida para una instalación local.
# Entradas: localhost, puerto 5432, base supermix_gdi, usuario postgres.
# Salida/reglas: No contiene contraseña real: el operador debe establecerla.
# -----------------------------------------------------------------
def default_config():
    """Devuelve los valores iniciales de host, puerto, base de datos y usuario."""
    return {'host': 'localhost', 'port': '5432', 'dbname': 'supermix_gdi', 'user': 'postgres', 'password': ''}


# -----------------------------------------------------------------
# FUNCIÓN: load_config
# Objetivo: Carga datos del perfil y los combina con valores predeterminados.
# Entradas: Archivo JSON opcional, ausente en el primer arranque.
# Salida/reglas: Retorna siempre un dict con las cinco claves esperadas; ignora datos inválidos.
# -----------------------------------------------------------------
def load_config():
    """Combina los valores predeterminados con los almacenados; usa los defaults si no se puede leer."""
    # El archivo puede no existir en la primera ejecucion.
    # Primero se carga un conjunto completo de campos para no dejar claves ausentes.
    config = default_config()
    try:
        if config_path().exists():
            data = json.loads(config_path().read_text(encoding='utf8'))
            # Solo se copian nombres de campo conocidos: no se aceptan claves extras del JSON.
            config.update({k: str(data[k]) for k in config if k in data})
    except (OSError, ValueError, TypeError):
        # Si JSON falta o está corrupto, se puede seguir usando el diálogo de configuración.
        pass
    return config


# -----------------------------------------------------------------
# FUNCIÓN: save_config
# Objetivo: Guarda en JSON valores de conexión después de validar.
# Entradas: data: dict de campos recogidos por el diálogo de Tkinter.
# Salida/reglas: Crea directorio, comprueba puerto entre 1 y 65535 y escribe UTF-8.
# -----------------------------------------------------------------
def save_config(data):
    """Valida los parametros, crea la carpeta por usuario y persiste la conexion en JSON."""
    safe = {k: str(data.get(k, '')) for k in default_config()}
    try:
        port = int(safe['port'])
    except ValueError as error:
        raise ValueError('El puerto debe ser numérico') from error
    if not (1 <= port <= 65535) or not all(safe[k].strip() for k in ('host', 'dbname', 'user')):
        raise ValueError('Host, puerto, base y usuario deben ser válidos')
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # La contraseña se guarda tal cual: NO es cifrado ni un almacén seguro de secretos.
    path.write_text(json.dumps(safe, ensure_ascii=False, indent=2), encoding='utf8')
    # En Unix, limita la lectura del archivo que contiene la contrasena.
    if os.name != 'nt':
        os.chmod(path, 0o600)
