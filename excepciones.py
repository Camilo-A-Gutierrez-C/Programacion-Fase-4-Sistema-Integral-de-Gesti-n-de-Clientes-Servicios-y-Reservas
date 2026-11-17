"""
Módulo: excepciones.py

Una "excepción personalizada" es un tipo de error propio del sistema.
Así, en vez de un error genérico, el programa dice exactamente QUÉ salió mal.

Árbol de excepciones:

    SoftwareFJError                      (error base del sistema)
    ├── ClienteInvalidoError             (datos de cliente incorrectos)
    │   └── ClienteDuplicadoError        (documento ya registrado)
    ├── ServicioInvalidoError            (servicio mal creado)
    ├── ParametroInvalidoError           (un parámetro tiene un valor malo)
    │   └── ParametroFaltanteError       (falta un parámetro obligatorio)
    ├── ServicioNoDisponibleError        (el servicio está ocupado o apagado)
    ├── CalculoInconsistenteError        (el costo no tiene sentido)
    ├── ReservaError                     (la reserva no se pudo crear/cambiar)
    └── OperacionNoPermitidaError        (acción prohibida en ese estado)
"""


class SoftwareFJError(Exception):
    """Error base: todas las demás excepciones del sistema heredan de esta.
    Gracias a eso, con un solo `except SoftwareFJError` se atrapa cualquiera."""

    # Marca para no escribir el mismo error dos veces en el archivo de logs.
    # False = "todavía no se ha escrito en el log".
    registrada = False


class ClienteInvalidoError(SoftwareFJError):
    """Los datos del cliente (nombre, documento, correo, teléfono) son malos."""


class ClienteDuplicadoError(ClienteInvalidoError):
    """Se intentó registrar un cliente con un documento que ya existe."""


class ServicioInvalidoError(SoftwareFJError):
    """El servicio se creó mal (tarifa negativa, nombre vacío, etc.)."""


class ParametroInvalidoError(SoftwareFJError):
    """Un parámetro existe pero su valor no sirve (ej.: duración negativa)."""


class ParametroFaltanteError(ParametroInvalidoError):
    """No se envió un parámetro obligatorio (ej.: 'asistentes' en una sala)."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio no se puede reservar porque está ocupado o desactivado."""


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo del costo da algo ilógico (descuento fuera de tope, total <= 0)."""


class ReservaError(SoftwareFJError):
    """No se pudo crear, confirmar, cancelar o procesar una reserva."""


class OperacionNoPermitidaError(SoftwareFJError):
    """La acción no se puede hacer en el estado actual (ej.: procesar una
    reserva que ya está cancelada)."""
