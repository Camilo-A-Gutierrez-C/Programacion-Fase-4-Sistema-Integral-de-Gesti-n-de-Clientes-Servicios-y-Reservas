"""
Módulo: reserva.py
Clase Reserva: une un cliente, un servicio, una duración y un estado.

Ciclo de vida:
    PENDIENTE --confirmar()--> CONFIRMADA --procesar()--> PROCESADA
        |                          |
        +-------cancelar()---------+--> CANCELADA
"""

from cliente import Cliente
from entidad import EntidadBase
from excepciones import (OperacionNoPermitidaError, ReservaError,
                         ServicioNoDisponibleError, SoftwareFJError)
from logger_config import Logger, registrar_errores
from servicio import Servicio


class Reserva(EntidadBase):
    """Reserva de un servicio por parte de un cliente. Sus datos son privados:
    el estado solo cambia con confirmar(), cancelar() y procesar(); nunca se
    puede asignar directamente desde afuera."""

    _PREFIJO = "RES"   # Los IDs serán RES-001, RES-002...

    # Los cuatro estados posibles
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"

    @registrar_errores
    def __init__(self, cliente, servicio, duracion, descuento=0.0, aplicar_iva=True,
                 **parametros):
        """parametros = datos propios del servicio (asistentes, unidades,
        incluir_garantia...). Se pasan por nombre: Reserva(c, s, 3, asistentes=8)."""

        # 1) Verifica que los objetos sean del tipo correcto
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un Servicio válido")

        # 2) (P2) Si el servicio está ocupado o apagado, ni siquiera se crea la reserva
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible")

        # 3) El servicio revisa sus parámetros (P1) y calcula el costo (P2)
        try:
            servicio.validar_parametros(duracion, **parametros)
            costo = servicio.calcular_costo(duracion, descuento, aplicar_iva, **parametros)
        except SoftwareFJError as error:
            # Encadenamiento: se guarda el error original como "causa" del nuevo
            raise ReservaError(
                f"No se pudo crear la reserva para {servicio.nombre}: {error}") from error

        # 4) Todo está bien: ahora sí se asigna el ID y se guardan los datos privados
        super().__init__()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__descuento = descuento
        self.__aplicar_iva = aplicar_iva
        self.__parametros = dict(parametros)   # Se guarda una COPIA, por seguridad
        self.__estado = self.PENDIENTE         # Toda reserva nace pendiente
        self.__costo_total = costo
        Logger.registrar_evento(
            f"Reserva {self.id} creada: cliente {cliente.id}, servicio {servicio.id}, "
            f"total ${costo:,.2f}")

    # Propiedades de solo lectura
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def descuento(self):
        return self.__descuento

    @property
    def aplicar_iva(self):
        return self.__aplicar_iva

    @property
    def parametros(self):
        return dict(self.__parametros)    # Entrega una copia, no el original

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    # Operaciones
    @registrar_errores
    def confirmar(self):
        """PENDIENTE -> CONFIRMADA. Bloquea el servicio. Usa try/except/else/finally."""
        try:
            # Solo se confirma lo que está pendiente
            if self.__estado != self.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"Solo se confirma una reserva PENDIENTE (estado actual: {self.__estado})")
            # El servicio pudo haber sido tomado por otra reserva mientras tanto
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.__servicio.nombre}' no está disponible")
            # Vuelve a validar (por ejemplo, que todavía alcance el stock del equipo)
            self.__servicio.validar_parametros(self.__duracion, **self.__parametros)
        except SoftwareFJError as error:
            raise ReservaError(f"No se pudo confirmar la reserva {self.id}") from error
        else:
            # "else" se ejecuta SOLO si arriba no hubo ningún error
            self.__servicio.bloquear_recurso(**self.__parametros)   # Bloquea el servicio
            self.__estado = self.CONFIRMADA
            Logger.registrar_evento(f"Reserva {self.id} confirmada")
            return True
        finally:
            # "finally" se ejecuta SIEMPRE, haya habido error o no
            Logger.registrar_evento(f"Fin del intento de confirmar la reserva {self.id}")

    @registrar_errores
    def cancelar(self):
        """PENDIENTE o CONFIRMADA -> CANCELADA. Si estaba confirmada, libera el servicio."""
        try:
            if self.__estado in (self.CANCELADA, self.PROCESADA):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva {self.__estado}")
        except OperacionNoPermitidaError as error:
            raise ReservaError(f"No se pudo cancelar la reserva {self.id}") from error
        else:
            # Solo una reserva CONFIRMADA tiene el servicio bloqueado. Una pendiente
            # no bloqueó nada, así que no hay nada que liberar (evita liberar de más).
            if self.__estado == self.CONFIRMADA:
                self.__servicio.liberar_recurso(**self.__parametros)
            self.__estado = self.CANCELADA
            Logger.registrar_evento(f"Reserva {self.id} cancelada")
            return True
        finally:
            Logger.registrar_evento(f"Fin del intento de cancelar la reserva {self.id}")

    @registrar_errores
    def procesar(self):
        """CONFIRMADA -> PROCESADA. Cierra la reserva, libera el servicio y devuelve
        el costo total (que ya se calculó al crear la reserva)."""
        try:
            if self.__estado != self.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesa una reserva CONFIRMADA (estado actual: {self.__estado})")
        except OperacionNoPermitidaError as error:
            raise ReservaError(f"No se pudo procesar la reserva {self.id}") from error
        else:
            self.__servicio.liberar_recurso(**self.__parametros)    # Libera el servicio
            self.__estado = self.PROCESADA
            Logger.registrar_evento(
                f"Reserva {self.id} procesada. Total: ${self.__costo_total:,.2f}")
            return self.__costo_total
        finally:
            Logger.registrar_evento(f"Fin del intento de procesar la reserva {self.id}")

    # Métodos de EntidadBase
    def validar_integridad(self):
        """(P2) Revisa que la reserva sea coherente: estado válido y costo positivo."""
        estados = (self.PENDIENTE, self.CONFIRMADA, self.CANCELADA, self.PROCESADA)
        return self.__estado in estados and self.__costo_total > 0

    def mostrar_reserva(self):
        """Texto con todos los datos de la reserva."""
        iva = "con IVA" if self.__aplicar_iva else "sin IVA"
        return (f"Reserva {self.id} | Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | Duración: {self.__duracion} | "
                f"Descuento: {self.__descuento:.0%} | {iva} | "
                f"Estado: {self.__estado} | Total: ${self.__costo_total:,.2f}")

    def mostrar_datos(self):
        return self.mostrar_reserva()
