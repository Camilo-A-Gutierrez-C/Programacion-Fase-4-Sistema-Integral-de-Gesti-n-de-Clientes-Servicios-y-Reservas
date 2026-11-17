"""
Módulo: entidad.py
EntidadBase es una clase ABSTRACTA: no se puede crear directamente
(EntidadBase() daría error). Solo sirve como "molde" para Cliente, Servicio
y Reserva, que heredan de ella.
"""

from abc import ABC, abstractmethod  # ABC = "Abstract Base Class" (clase abstracta)


class EntidadBase(ABC):
    """Molde común de todo lo que tiene un ID en el sistema."""

    # Cada clase hija cambia este prefijo (CLI, SRV, RES) para armar su ID.
    _PREFIJO = "ENT"

    # Diccionario PRIVADO y compartido por todas las clases: guarda cuántos IDs
    # se han entregado por prefijo. Ejemplo: {"CLI": 2, "SRV": 4}
    __contadores = {}

    def __init__(self):
        # Busca el último número usado para este prefijo (0 si es el primero) y suma 1
        numero = EntidadBase.__contadores.get(self._PREFIJO, 0) + 1
        # Guarda el nuevo número para que el siguiente objeto no lo repita
        EntidadBase.__contadores[self._PREFIJO] = numero
        # Arma el ID final con 3 dígitos: "CLI-001", "CLI-002", ...
        self.__id = f"{self._PREFIJO}-{numero:03d}"

    @property
    def id(self):
        """El ID es de SOLO LECTURA: se puede consultar, pero no cambiar."""
        return self.__id

    @abstractmethod
    def mostrar_datos(self):
        """Cada clase hija debe devolver un texto con sus datos."""

    @abstractmethod
    def validar_integridad(self):
        """Cada clase hija debe poder decir si sus datos internos son coherentes
        (devuelve True/False)."""

    def obtener_resumen(self):
        """Resumen corto de la entidad. Por defecto es lo mismo que mostrar_datos()."""
        return self.mostrar_datos()

    def __str__(self):
        # Cuando se hace print(objeto) se muestra el texto de mostrar_datos()
        return self.mostrar_datos()
