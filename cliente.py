"""
Módulo: cliente.py
"""

import re  # Módulo de "expresiones regulares": sirve para revisar el formato de un texto

from entidad import EntidadBase
from excepciones import ClienteInvalidoError
from logger_config import registrar_errores


class Cliente(EntidadBase):
    """Cliente de Software FJ. Sus datos personales son PRIVADOS (doble guion
    bajo): desde afuera solo se leen o cambian con getters/setters, que SIEMPRE
    validan. Así nadie puede guardar un dato malo saltándose las reglas."""

    _PREFIJO = "CLI"  # Los IDs de cliente serán CLI-001, CLI-002...

    # Letras permitidas en un nombre (incluye tildes, ñ y ü)
    _LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
    # Nombre: solo letras, y las palabras separadas por un espacio
    _PATRON_NOMBRE = re.compile(rf"^[{_LETRAS}]+(?: [{_LETRAS}]+)*$")
    # Documento: entre 6 y 12 dígitos
    _PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")
    # Correo: formato usuario@dominio.ext
    _PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}$")
    # Teléfono (del Proyecto 2): entre 7 y 15 dígitos
    _PATRON_TELEFONO = re.compile(r"^\d{7,15}$")

    @registrar_errores  # Si falla, el error queda escrito en el log
    def __init__(self, nombre, documento, correo, telefono=None):
        # Se validan los datos uno por uno, pero sin detenerse en el primer error:
        # se juntan todos para avisarle al usuario TODO lo que está mal de una vez.
        errores = []
        for setter, valor in ((self.set_nombre, nombre),
                              (self.set_documento, documento),
                              (self.set_correo, correo),
                              (self.set_telefono, telefono)):
            try:
                setter(valor)                       # Intenta guardar el dato (valida adentro)
            except ClienteInvalidoError as error:
                errores.append(error)               # Si falla, guarda el error en la lista

        if errores:
            # Encadenamiento: el error general "viene de" el primer error específico.
            # Por eso en el log se ve el mensaje general y también la causa original.
            raise ClienteInvalidoError(
                "No se pudo crear el cliente: " + " | ".join(str(e) for e in errores)
            ) from errores[0]

        super().__init__()  # Asigna el ID (CLI-001...) solo si el cliente es válido

    # Validaciones
    @classmethod
    def validar_nombre(cls, valor):
        """Revisa el nombre y lo devuelve limpio (mínimo 3 letras, sin números ni símbolos)."""
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El nombre debe ser texto")
        limpio = " ".join(valor.split())  # Quita espacios sobrantes ("Ana   Paz " -> "Ana Paz")
        if len(limpio) < 3 or not cls._PATRON_NOMBRE.match(limpio):
            raise ClienteInvalidoError(
                f"Nombre inválido '{valor}': mínimo 3 letras, sin números ni símbolos")
        return limpio

    @classmethod
    def validar_documento(cls, valor):
        """Revisa el documento y lo devuelve como texto (6 a 12 dígitos)."""
        # bool se descarta aparte porque en Python True/False cuentan como números
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise ClienteInvalidoError("El documento debe ser texto o número")
        limpio = str(valor).strip()  # Se guarda siempre como texto
        if not cls._PATRON_DOCUMENTO.match(limpio):
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 12 dígitos")
        return limpio

    @classmethod
    def validar_correo(cls, valor):
        """Revisa el correo y lo devuelve en minúsculas."""
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El correo debe ser texto")
        limpio = valor.strip().lower()
        if len(limpio) > 254 or not cls._PATRON_CORREO.match(limpio):
            raise ClienteInvalidoError(f"Correo inválido '{valor}'")
        return limpio

    @classmethod
    def validar_telefono(cls, valor):
        """(Del Proyecto 2) Revisa el teléfono: 7 a 15 dígitos. Es opcional:
        si viene None, simplemente no se guarda ningún teléfono."""
        if valor is None:
            return None
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise ClienteInvalidoError("El teléfono debe ser texto o número")
        limpio = str(valor).strip()
        if not cls._PATRON_TELEFONO.match(limpio):
            raise ClienteInvalidoError(
                f"Teléfono inválido '{valor}': debe tener entre 7 y 15 dígitos")
        return limpio

    # Getters y setters
    # "get_" lee el dato privado; "set_" lo cambia, pero SIEMPRE pasando por la validación.
    def get_nombre(self):
        return self.__nombre

    def set_nombre(self, valor):
        self.__nombre = self.validar_nombre(valor)

    def get_documento(self):
        return self.__documento

    def set_documento(self, valor):
        self.__documento = self.validar_documento(valor)

    def get_correo(self):
        return self.__correo

    def set_correo(self, valor):
        self.__correo = self.validar_correo(valor)

    def get_telefono(self):
        return self.__telefono

    def set_telefono(self, valor):
        self.__telefono = self.validar_telefono(valor)

    # Propiedades equivalentes (forma "pythónica"): se usa cliente.nombre en vez de
    # cliente.get_nombre(), y cliente.nombre = "..." en vez de cliente.set_nombre("...").
    nombre = property(get_nombre, set_nombre)
    documento = property(get_documento, set_documento)
    correo = property(get_correo, set_correo)
    telefono = property(get_telefono, set_telefono)

    # Métodos de EntidadBase
    def validar_integridad(self):
        """(Del Proyecto 2) Revisa que los datos guardados sigan siendo válidos."""
        try:
            self.validar_nombre(self.__nombre)
            self.validar_documento(self.__documento)
            self.validar_correo(self.__correo)
            self.validar_telefono(self.__telefono)
            return True
        except ClienteInvalidoError:
            return False

    def mostrar_datos(self):
        """Texto con los datos del cliente."""
        telefono = self.__telefono if self.__telefono else "No registrado"
        return (f"Cliente {self.id} | Nombre: {self.__nombre} | "
                f"Documento: {self.__documento} | Correo: {self.__correo} | "
                f"Teléfono: {telefono}")

    # Presentación
    def mostrar_datos(self):
        return (f"Cliente {self.id} | Nombre: {self.__nombre} | "
                f"Documento: {self.__documento} | Correo: {self.__correo}")

