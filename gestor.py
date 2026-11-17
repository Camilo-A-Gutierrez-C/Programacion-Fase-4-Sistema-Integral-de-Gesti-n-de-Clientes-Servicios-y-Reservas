"""
Módulo: gestor.py

Aquí NO hay base de datos: todo vive en listas dentro de la memoria del programa.
"""

from cliente import Cliente
from excepciones import (ClienteDuplicadoError, ClienteInvalidoError, ReservaError,
                         ServicioInvalidoError)
from logger_config import Logger, registrar_errores
from reserva import Reserva
from servicio import Servicio


class GestorSoftwareFJ:
    """Guarda y organiza los clientes, servicios y reservas del sistema."""

    def __init__(self):
        # Listas PRIVADAS: desde afuera no se pueden modificar directamente
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        Logger.registrar_evento("Gestor Software FJ iniciado (datos en memoria)")

    # Consulta (devuelven tuplas: copias que no se pueden alterar)
    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    # Registro
    @registrar_errores
    def registrar_cliente(self, cliente):
        """Agrega un cliente a la lista. No permite documentos repetidos."""
        if not isinstance(cliente, Cliente):
            raise ClienteInvalidoError("Solo se pueden registrar objetos de tipo Cliente")
        for existente in self.__clientes:
            if existente.documento == cliente.documento:     # ¿Ya existe ese documento?
                raise ClienteDuplicadoError(
                    f"Ya existe un cliente con el documento {cliente.documento} "
                    f"({existente.id})")
        self.__clientes.append(cliente)
        Logger.registrar_evento(f"Cliente {cliente.id} registrado")
        return cliente

    @registrar_errores
    def registrar_servicio(self, servicio):
        """Agrega un servicio a la lista (cuida que no se registre dos veces)."""
        if not isinstance(servicio, Servicio):
            raise ServicioInvalidoError("Solo se pueden registrar objetos de tipo Servicio")
        if any(existente.id == servicio.id for existente in self.__servicios):
            raise ServicioInvalidoError(f"El servicio {servicio.id} ya está registrado")
        self.__servicios.append(servicio)
        Logger.registrar_evento(f"Servicio {servicio.id} registrado")
        return servicio

    @registrar_errores
    def registrar_reserva(self, reserva):
        """Agrega una reserva a la lista (cuida que no se registre dos veces)."""
        if not isinstance(reserva, Reserva):
            raise ReservaError("Solo se pueden registrar objetos de tipo Reserva")
        if any(existente.id == reserva.id for existente in self.__reservas):
            raise ReservaError(f"La reserva {reserva.id} ya está registrada")
        self.__reservas.append(reserva)
        return reserva

    # Búsqueda
    def buscar_cliente_por_documento(self, documento):
        """Devuelve el cliente con ese documento, o None si no existe."""
        documento = str(documento).strip()
        for cliente in self.__clientes:
            if cliente.documento == documento:
                return cliente
        return None

    def resumen(self):
        """Cantidades registradas, en un diccionario."""
        return {"clientes": len(self.__clientes),
                "servicios": len(self.__servicios),
                "reservas": len(self.__reservas)}
