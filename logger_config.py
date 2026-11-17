"""
Módulo: logger_config.py

El "log" es un archivo de texto donde el programa anota todo lo que pasa
(eventos, advertencias y errores) con fecha y hora. Sirve para revisar
después qué ocurrió. Es el ÚNICO uso de archivos del sistema (no hay base de datos).
"""

import functools   # Sirve para que los decoradores no "disfracen" el nombre de la función
import logging     # Módulo de Python para escribir logs
import os          # Para manejar rutas de carpetas y archivos

from excepciones import SoftwareFJError

# Carpeta donde está este archivo. Si el código se ejecuta dentro de un
# Notebook (Jupyter), _file_ no existe y se usa la carpeta actual.
try:
    _CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _CARPETA_BASE = os.getcwd()


class Logger:
    """Envoltura sencilla sobre el módulo logging de Python."""

    # Ruta completa del archivo de log: <carpeta del proyecto>/logs/software_fj.log
    RUTA_LOG = os.path.join(_CARPETA_BASE, "logs", "software_fj.log")

    # Aquí se guarda el logger ya creado, para crearlo UNA sola vez
    _logger = None

    @classmethod
    def configurar_logger(cls, ruta=None, nivel=logging.INFO):
        """Crea el logger la primera vez; las siguientes veces reutiliza el mismo."""
        if cls._logger is not None:      # Si ya existe, lo devuelve sin crear otro
            return cls._logger

        ruta = ruta or cls.RUTA_LOG      # Si no dan ruta, usa la de por defecto
        logger = logging.getLogger("software_fj")
        logger.setLevel(nivel)           # Nivel mínimo que se escribe (INFO en adelante)
        logger.propagate = False         # Evita que el mensaje salga repetido en consola

        # Formato de cada línea: fecha y hora | nivel | mensaje
        formato = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
        try:
            os.makedirs(os.path.dirname(ruta), exist_ok=True)   # Crea la carpeta /logs si falta
            manejador = logging.FileHandler(ruta, encoding="utf-8")  # Escribe en el archivo
        except OSError:
            # Si no se puede escribir el archivo, el sistema NO se detiene:
            # usa la consola como plan B.
            manejador = logging.StreamHandler()
        manejador.setFormatter(formato)
        logger.addHandler(manejador)

        cls._logger = logger
        return logger

    @classmethod
    def registrar_evento(cls, mensaje):
        """Anota algo normal que pasó (nivel INFO)."""
        cls.configurar_logger().info(mensaje)

    @classmethod
    def registrar_advertencia(cls, mensaje):
        """Anota algo que merece atención pero no es grave (nivel WARNING)."""
        cls.configurar_logger().warning(mensaje)

    @classmethod
    def registrar_error(cls, mensaje, excepcion=None):
        """Anota un error (nivel ERROR). Si se envía la excepción, también deja
        escrita la cadena de causas (los errores encadenados con 'raise ... from')."""
        detalle = mensaje
        if excepcion is not None:
            # Agrega el tipo de error y su texto
            detalle += f" | {type(excepcion).__name__}: {excepcion}"
            # Recorre las causas: __cause__ guarda el error original de un "raise ... from"
            causa = excepcion.__cause__
            while causa is not None:
                detalle += f" <- causa: {type(causa).__name__}: {causa}"
                causa = causa.__cause__
            # Marca el error como "ya registrado" para no escribirlo dos veces
            if isinstance(excepcion, SoftwareFJError):
                excepcion.registrada = True
        cls.configurar_logger().error(detalle)


def registrar_errores(funcion):
    """DECORADOR. Se coloca encima de una función con @registrar_errores.
    Si la función lanza un error del sistema, el decorador lo anota en el log
    y luego lo vuelve a lanzar SIN cambiarlo (el programa sigue su flujo normal)."""
    @functools.wraps(funcion)            # Conserva el nombre original de la función
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)      # Ejecuta la función normalmente
        except SoftwareFJError as error:
            if not error.registrada:             # Solo lo anota si nadie lo anotó antes
                Logger.registrar_error(f"Error en {funcion.__qualname__}", error)
            raise                                # Relanza el mismo error intacto
    return envoltura
