"""
Módulo: entidad.py
Descripción: Clase abstracta que representa las entidades generales del sistema
(Cliente, Servicio y Reserva heredan de ella). Es un requisito del ejercicio.
"""

from abc import ABC, abstractmethod


class EntidadBase(ABC):
    """Entidad general: asigna un identificador único y obliga a las clases
    hijas a implementar mostrar_datos()."""

    _PREFIJO = "ENT"      # Cada clase hija define su propio prefijo (CLI, SRV...)
    __contadores = {}     # Privado: contador de identificadores por prefijo

    def __init__(self):
        # Incrementa el contador del prefijo de la clase hija
        numero = EntidadBase.__contadores.get(self._PREFIJO, 0) + 1
        EntidadBase.__contadores[self._PREFIJO] = numero
        # Ejemplo de identificador: CLI-001 (atributo privado: no se puede alterar)
        self.__id = f"{self._PREFIJO}-{numero:03d}"

    @property
    def id(self):
        """Identificador único (solo lectura: encapsulación)."""
        return self.__id

    @abstractmethod
    def mostrar_datos(self):
        """Devuelve una descripción en texto de la entidad."""

    def __str__(self):
        return self.mostrar_datos()
