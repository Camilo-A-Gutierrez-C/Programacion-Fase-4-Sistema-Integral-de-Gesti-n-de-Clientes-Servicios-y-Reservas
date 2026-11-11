"""
Módulo: excepciones.py
Descripción: Define la jerarquía de excepciones personalizadas de Software FJ.
Todas heredan de SoftwareFJError, de modo que el sistema pueda capturar
cualquier error propio con un solo "except SoftwareFJError".
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ.

    El atributo 'registrada' indica si el error ya quedó escrito en el archivo
    de logs (lo marca Logger.registrar_error). Así se evita registrar dos veces
    el mismo error cuando atraviesa varias capas del sistema.
    """

    registrada = False


class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones."""


class ClienteDuplicadoError(ClienteInvalidoError):
    """Se lanza cuando se intenta registrar un cliente con un documento que
    ya existe (es un caso particular de cliente inválido)."""


class ServicioInvalidoError(SoftwareFJError):
    """Se lanza cuando un servicio se intenta crear con datos incorrectos."""


class ParametroInvalidoError(SoftwareFJError):
    """Se lanza cuando un parámetro (duración, cantidad, etc.) es inválido."""


class ParametroFaltanteError(ParametroInvalidoError):
    """Se lanza cuando falta un parámetro obligatorio (es un caso particular
    de parámetro inválido, por eso hereda de ParametroInvalidoError)."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio no disponible."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando una operación no es válida para el estado actual
    (por ejemplo, procesar una reserva cancelada)."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce valores inconsistentes."""


class ReservaError(SoftwareFJError):
    """Error general de una reserva. Se usa para ENCADENAR excepciones:
    envuelve el error original usando 'raise ReservaError(...) from error'."""
