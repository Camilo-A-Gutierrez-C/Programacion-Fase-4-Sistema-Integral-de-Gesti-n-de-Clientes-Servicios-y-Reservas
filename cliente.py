"""
Módulo: cliente.py
Descripción: Clase Cliente con encapsulación de datos personales y
validaciones estrictas de nombre, documento y correo.
"""

import re

from entidad import EntidadBase
from excepciones import ClienteInvalidoError
from logger_config import registrar_errores


class Cliente(EntidadBase):
    """Cliente de Software FJ. Los datos personales son atributos PRIVADOS
    (__nombre, __documento, __correo): solo se leen y modifican mediante
    getters/setters (o sus propiedades equivalentes), que siempre validan."""

    _PREFIJO = "CLI"
    _LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
    # Nombre: solo letras separadas por espacios
    _PATRON_NOMBRE = re.compile(rf"^[{_LETRAS}]+(?: [{_LETRAS}]+)*$")
    # Documento: entre 6 y 12 dígitos
    _PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")
    # Correo: formato usuario@dominio.ext
    _PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}$")

    @registrar_errores
    def __init__(self, nombre, documento, correo):
        # Se validan los tres datos y se acumulan los errores encontrados
        errores = []
        for setter, valor in ((self.set_nombre, nombre),
                              (self.set_documento, documento),
                              (self.set_correo, correo)):
            try:
                setter(valor)
            except ClienteInvalidoError as error:
                errores.append(error)

        if errores:
            # Encadenamiento de excepciones: el error general "viene de" el primero
            raise ClienteInvalidoError(
                "No se pudo crear el cliente: " + " | ".join(str(e) for e in errores)
            ) from errores[0]

        super().__init__()  # El id solo se asigna si el cliente es válido

    # ---------------- Validaciones ----------------
    @classmethod
    def validar_nombre(cls, valor):
        """Valida y devuelve el nombre limpio (mínimo 3 caracteres, solo letras)."""
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El nombre debe ser texto")
        limpio = " ".join(valor.split())  # Quita espacios sobrantes
        if len(limpio) < 3 or not cls._PATRON_NOMBRE.match(limpio):
            raise ClienteInvalidoError(
                f"Nombre inválido '{valor}': mínimo 3 letras, sin números ni símbolos")
        return limpio

    @classmethod
    def validar_documento(cls, valor):
        """Valida y devuelve el documento (6 a 12 dígitos)."""
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise ClienteInvalidoError("El documento debe ser texto o número")
        limpio = str(valor).strip()
        if not cls._PATRON_DOCUMENTO.match(limpio):
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 12 dígitos")
        return limpio

    @classmethod
    def validar_correo(cls, valor):
        """Valida y devuelve el correo en minúsculas."""
        if not isinstance(valor, str):
            raise ClienteInvalidoError("El correo debe ser texto")
        limpio = valor.strip().lower()
        if len(limpio) > 254 or not cls._PATRON_CORREO.match(limpio):
            raise ClienteInvalidoError(f"Correo inválido '{valor}'")
        return limpio

    # ---------------- Getters y setters ----------------
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

    # Propiedades equivalentes (estilo pythónico): cliente.nombre, etc.
    nombre = property(get_nombre, set_nombre)
    documento = property(get_documento, set_documento)
    correo = property(get_correo, set_correo)

    # ---------------- Presentación ----------------
    def mostrar_datos(self):
        return (f"Cliente {self.id} | Nombre: {self.__nombre} | "
                f"Documento: {self.__documento} | Correo: {self.__correo}")

