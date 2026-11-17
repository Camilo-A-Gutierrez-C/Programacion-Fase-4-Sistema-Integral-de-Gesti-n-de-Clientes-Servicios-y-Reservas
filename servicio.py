"""
Módulo: servicio.py
Contiene la clase abstracta Servicio y los tres servicios especializados.

Nota sobre la sobrecarga: Python no permite dos métodos con el mismo nombre, así
que se simula: cotizar() decide qué variante usar según CUÁNTOS argumentos recibe:
    cotizar(duracion)                        -> con descuento 0 % y con IVA
    cotizar(duracion, descuento)             -> con ese descuento y con IVA
    cotizar(duracion, descuento, aplicar_iva)-> con descuento y decidiendo el IVA
"""

import math                      # Para detectar números raros (infinito, "no es número")
from abc import ABC, abstractmethod

from entidad import EntidadBase
from excepciones import (CalculoInconsistenteError, ParametroFaltanteError,
                         ParametroInvalidoError, ServicioInvalidoError)
from logger_config import registrar_errores


def _es_entero(valor):
    """True si el valor es un número entero de verdad (descarta True/False)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _es_numero(valor):
    """True si el valor es un número normal y finito (no bool, no infinito, no NaN)."""
    return (isinstance(valor, (int, float)) and not isinstance(valor, bool)
            and math.isfinite(valor))


# Clase abstracta Servicio
class Servicio(EntidadBase, ABC):
    """Molde de TODO servicio. Define lo que cada servicio debe saber hacer
    (calcular su costo, describirse y validar sus parámetros). Sus datos son
    privados (__nombre, __tarifa_base, __disponible); las clases hijas los
    consultan solo mediante propiedades."""

    _PREFIJO = "SRV"              # Los IDs serán SRV-001, SRV-002...
    TASA_IVA = 0.19               # (P2) IVA del 19 %
    RANGO_DURACION = (1, 24)      # (P1) Cada hija define su propio rango (mínimo, máximo)
    DESCUENTO_MAXIMO = 0.30       # (P2) Tope de descuento; cada hija define el suyo
    NOMBRE_TIPO = "servicios"     # Solo se usa para escribir mensajes de error claros

    def __init__(self, nombre, tarifa_base, disponible=True):
        # Validaciones de creación: si algo está mal, el servicio NO se crea
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El nombre del servicio es obligatorio")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:
            raise ServicioInvalidoError(
                f"Tarifa inválida '{tarifa_base}': debe ser un número mayor que 0")
        super().__init__()                        # Asigna el ID (SRV-001...)
        self.__nombre = nombre.strip()            # Quita espacios sobrantes
        self.__tarifa_base = float(tarifa_base)
        self.__disponible = bool(disponible)

    # Propiedades (encapsulación)
    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa_base(self):
        return self.__tarifa_base

    @property
    def disponible(self):
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        self.__disponible = bool(valor)

    # Métodos abstractos: cada servicio los hace a su manera (POLIMORFISMO)
    @abstractmethod
    def calcular_costo(self, duracion, descuento=0.0, aplicar_iva=True, **opciones):
        """Calcula el costo total del servicio."""

    @abstractmethod
    def describir(self):
        """Devuelve un texto que describe el servicio."""

    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Revisa que lleguen los datos necesarios para reservar el servicio."""

    def mostrar_datos(self):
        # Mostrar los datos de un servicio es lo mismo que describirlo
        return self.describir()

    # Bloqueo de disponibilidad
    # Cuando una reserva se CONFIRMA, el servicio se "bloquea" para que nadie más
    # lo reserve; cuando la reserva se procesa o se cancela, se "libera".
    # AlquilerEquipo los reescribe para trabajar con unidades de stock.
    def bloquear_recurso(self, **opciones):
        """Marca el servicio como ocupado."""
        self.__disponible = False

    def liberar_recurso(self, **opciones):
        """Marca el servicio como libre otra vez."""
        self.__disponible = True

    # Sobrecarga simulada por cantidad de argumentos
    @registrar_errores
    def cotizar(self, duracion, *ajustes, **opciones):
        """Calcula un precio de prueba. Los argumentos extra se pasan en orden:
        primero descuento y luego aplicar_iva. Las opciones propias de cada
        servicio (unidades, incluir_garantia...) se envían por nombre."""
        if len(ajustes) > 2:
            raise ParametroInvalidoError(
                "cotizar() admite como máximo descuento y aplicar_iva")
        return self.calcular_costo(duracion, *ajustes, **opciones)

    # Utilidades compartidas por las clases hijas
    def _validar_duracion(self, duracion):
        """Revisa que la duración sea un número dentro del rango del servicio."""
        minimo, maximo = self.RANGO_DURACION
        if not _es_numero(duracion):
            raise ParametroInvalidoError("La duración debe ser un número")
        if not minimo <= duracion <= maximo:
            raise ParametroInvalidoError(
                f"Duración {duracion} fuera de rango ({minimo} a {maximo})")

    def _validar_ajustes(self, descuento, aplicar_iva):
        """(Regla del P2) Revisa el descuento (entre 0 y el tope del servicio)
        y que aplicar_iva sea True o False."""
        if not _es_numero(descuento):
            raise CalculoInconsistenteError("El descuento debe ser un número")
        if not 0 <= descuento <= self.DESCUENTO_MAXIMO:
            raise CalculoInconsistenteError(
                f"El descuento para {self.NOMBRE_TIPO} debe estar entre 0 % y "
                f"{self.DESCUENTO_MAXIMO:.0%} (se pidió {descuento:.0%})")
        if not isinstance(aplicar_iva, bool):
            raise ParametroInvalidoError("'aplicar_iva' debe ser True o False")

    @staticmethod
    def _verificar_total(total):
        """Última revisión del costo: un total <= 0 o raro significa un cálculo
        inconsistente. Si todo está bien, lo devuelve redondeado a 2 decimales."""
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"Resultado inconsistente: {total}")
        return round(total, 2)


# ReservaSala
class ReservaSala(Servicio):
    """Servicio de reserva de salas. La duración se mide en HORAS."""

    RANGO_DURACION = (1, 12)      # De 1 a 12 horas
    DESCUENTO_MAXIMO = 0.50       # Máximo 50 % de descuento
    NOMBRE_TIPO = "salas"
    COSTO_VIDEOBEAM = 15000.0     # Cargo fijo si la sala incluye VideoBeam
    CAPACIDAD_MAXIMA = 100        # Una sala admite como máximo 100 personas

    @registrar_errores
    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True, tiene_videobeam=True):
        # Firma del P1: (nombre, tarifa_hora, capacidad, disponible). Se agregó al final
        # "tiene_videobeam" con valor por defecto, para no romper la firma.
        if not _es_entero(capacidad) or not 1 <= capacidad <= self.CAPACIDAD_MAXIMA:
            raise ServicioInvalidoError(
                f"La capacidad debe ser un entero entre 1 y {self.CAPACIDAD_MAXIMA}")
        if not isinstance(tiene_videobeam, bool):
            raise ServicioInvalidoError("'tiene_videobeam' debe ser True o False")
        super().__init__(nombre, tarifa_hora, disponible)
        self.__capacidad = capacidad
        self.__tiene_videobeam = tiene_videobeam

    @property
    def capacidad(self):
        return self.__capacidad

    @property
    def tiene_videobeam(self):
        return self.__tiene_videobeam

    def calcular_costo(self, duracion, descuento=0.0, aplicar_iva=True, **opciones):
        """REGLA DEL P2: (tarifa x horas + VideoBeam) -> se resta el descuento -> se suma el IVA."""
        self._validar_duracion(duracion)
        self._validar_ajustes(descuento, aplicar_iva)
        subtotal = self.tarifa_base * duracion          # Valor de las horas
        if self.__tiene_videobeam:
            subtotal += self.COSTO_VIDEOBEAM            # Suma el VideoBeam
        con_descuento = subtotal * (1 - descuento)      # Resta el descuento
        # Suma el IVA solo si se pidió
        total = con_descuento * (1 + self.TASA_IVA) if aplicar_iva else con_descuento
        return self._verificar_total(total)

    def describir(self):
        video = "con VideoBeam" if self.__tiene_videobeam else "sin VideoBeam"
        return (f"Sala '{self.nombre}' [{self.id}] | Capacidad: {self.__capacidad} personas | "
                f"{video} | Tarifa: ${self.tarifa_base:,.0f}/hora")

    def validar_parametros(self, duracion, asistentes=None, **opciones):
        """Para reservar una sala hay que indicar cuántos asistentes irán."""
        if asistentes is None:
            raise ParametroFaltanteError("Falta el parámetro obligatorio 'asistentes'")
        self._validar_duracion(duracion)
        if not _es_entero(asistentes) or asistentes <= 0:
            raise ParametroInvalidoError("'asistentes' debe ser un entero > 0")
        if asistentes > self.__capacidad:
            raise ParametroInvalidoError(
                f"{asistentes} asistentes superan la capacidad ({self.__capacidad})")
        return True

    def validar_integridad(self):
        """(P2) Revisa que los datos de la sala sigan siendo coherentes."""
        return self.tarifa_base > 0 and 1 <= self.__capacidad <= self.CAPACIDAD_MAXIMA


# AlquilerEquipo
class AlquilerEquipo(Servicio):
    """Alquiler de equipos. La duración se mide en DÍAS. Cada equipo tiene un
    stock (cuántas unidades hay) que baja al confirmar y sube al devolver."""

    RANGO_DURACION = (1, 30)      # De 1 a 30 días
    DESCUENTO_MAXIMO = 0.40       # Máximo 40 % de descuento
    NOMBRE_TIPO = "equipos"
    MIN_ESPECIFICACIONES = 5      # Las especificaciones deben tener 5+ caracteres

    @registrar_errores
    def __init__(self, nombre, tarifa_dia, tipo_equipo, stock, disponible=True,
                 especificaciones=None, deposito_garantia=0.0):
        # Firma: (nombre, tarifa_dia, tipo_equipo, stock, disponible).
        # Se agregaron al final, opcionales, "especificaciones" y "deposito_garantia".
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("El tipo de equipo es obligatorio")
        if not _es_entero(stock) or stock <= 0:
            raise ServicioInvalidoError("El stock debe ser un entero > 0")
        if especificaciones is None:
            especificaciones = tipo_equipo           # Si no las dan, usa el tipo de equipo
        if (not isinstance(especificaciones, str)
                or len(especificaciones.strip()) < self.MIN_ESPECIFICACIONES):
            raise ServicioInvalidoError(
                f"Las especificaciones deben tener al menos {self.MIN_ESPECIFICACIONES} caracteres")
        if not _es_numero(deposito_garantia) or deposito_garantia < 0:
            raise ServicioInvalidoError("El depósito de garantía debe ser un número >= 0")
        super().__init__(nombre, tarifa_dia, disponible)
        self.__tipo_equipo = tipo_equipo.strip()
        self.__stock = stock
        self.__especificaciones = especificaciones.strip()
        self.__deposito_garantia = float(deposito_garantia)

    @property
    def tipo_equipo(self):
        return self.__tipo_equipo

    @property
    def stock(self):
        return self.__stock

    @property
    def especificaciones(self):
        return self.__especificaciones

    @property
    def deposito_garantia(self):
        return self.__deposito_garantia

    def calcular_costo(self, duracion, descuento=0.0, aplicar_iva=True,
                       unidades=1, incluir_garantia=True, **opciones):
        """REGLA: alquiler = tarifa x días (x unidades) -> se resta el descuento ->
        el IVA se calcula sobre el alquiler -> al final se suma la garantía (que NO paga IVA).
        Con unidades=1."""
        self._validar_duracion(duracion)
        self._validar_ajustes(descuento, aplicar_iva)
        if not _es_entero(unidades) or unidades < 1:
            raise ParametroInvalidoError("'unidades' debe ser un entero >= 1")
        if not isinstance(incluir_garantia, bool):
            raise ParametroInvalidoError("'incluir_garantia' debe ser True o False")
        alquiler = self.tarifa_base * duracion * unidades    # Valor del alquiler
        con_descuento = alquiler * (1 - descuento)           # Resta el descuento
        iva = con_descuento * self.TASA_IVA if aplicar_iva else 0.0   # IVA solo del alquiler
        # La garantía es un depósito por cada unidad alquilada
        garantia = self.__deposito_garantia * unidades if incluir_garantia else 0.0
        return self._verificar_total(con_descuento + iva + garantia)

    def describir(self):
        return (f"Equipo '{self.nombre}' [{self.id}] | Tipo: {self.__tipo_equipo} | "
                f"Specs: {self.__especificaciones} | Stock: {self.__stock} | "
                f"Tarifa: ${self.tarifa_base:,.0f}/día | "
                f"Garantía: ${self.__deposito_garantia:,.0f}")

    def validar_parametros(self, duracion, unidades=None, **opciones):
        """Para alquilar hay que indicar cuántas unidades, y deben alcanzar en stock."""
        if unidades is None:
            raise ParametroFaltanteError("Falta el parámetro obligatorio 'unidades'")
        self._validar_duracion(duracion)
        if not _es_entero(unidades) or unidades <= 0:
            raise ParametroInvalidoError("'unidades' debe ser un entero > 0")
        if unidades > self.__stock:
            raise ParametroInvalidoError(
                f"Se piden {unidades} unidades y solo hay {self.__stock} en stock")
        return True

    # Un equipo no se bloquea entero: solo se descuentan las unidades alquiladas.
    def bloquear_recurso(self, unidades=1, **opciones):
        """Al confirmar: resta las unidades del stock. Si no queda nada, se apaga."""
        self.__stock -= unidades
        if self.__stock <= 0:
            self.disponible = False

    def liberar_recurso(self, unidades=1, **opciones):
        """Al devolver el equipo: suma las unidades al stock y vuelve a estar disponible."""
        self.__stock += unidades
        self.disponible = True

    def validar_integridad(self):
        """(P2) Revisa que los datos del equipo sigan siendo coherentes."""
        return self.tarifa_base > 0 and self.__stock >= 0 and self.__deposito_garantia >= 0


# AsesoriaEspecializada
class AsesoriaEspecializada(Servicio):
    """Asesoría por horas. El nivel del asesor (junior/senior) cambia el costo."""

    RANGO_DURACION = (1, 8)       # (P1) De 1 a 8 horas
    DESCUENTO_MAXIMO = 0.30       # (P2) Máximo 30 % de descuento
    NOMBRE_TIPO = "asesorías"
    NIVELES = {"junior": 1.0, "senior": 1.25}    # (P2) El senior cuesta 25 % más
    # (P2) Solo se aceptan estas especialidades
    ESPECIALIDADES_VALIDAS = ("ARQUITECTURA", "CIBERSEGURIDAD", "CLOUD", "DATOS", "DEVOPS")

    @registrar_errores
    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        # Firma idéntica a la del Proyecto 1.
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad es obligatoria")
        especialidad = especialidad.strip().upper()   # "cloud" y "Cloud" valen igual
        if especialidad not in self.ESPECIALIDADES_VALIDAS:
            raise ServicioInvalidoError(
                f"Especialidad '{especialidad}' inválida. "
                f"Opciones: {', '.join(self.ESPECIALIDADES_VALIDAS)}")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' inválido. Opciones: {', '.join(self.NIVELES)}")
        super().__init__(nombre, tarifa_hora, disponible)
        self.__especialidad = especialidad
        self.__nivel = nivel

    @property
    def especialidad(self):
        return self.__especialidad

    @property
    def nivel(self):
        return self.__nivel

    def calcular_costo(self, duracion, descuento=0.0, aplicar_iva=True, **opciones):
        """REGLA DEL P2: tarifa x horas x factor del nivel (senior = 1,25) ->
        se resta el descuento -> se suma el IVA."""
        self._validar_duracion(duracion)
        self._validar_ajustes(descuento, aplicar_iva)
        subtotal = self.tarifa_base * duracion * self.NIVELES[self.__nivel]
        con_descuento = subtotal * (1 - descuento)
        total = con_descuento * (1 + self.TASA_IVA) if aplicar_iva else con_descuento
        return self._verificar_total(total)

    def describir(self):
        return (f"Asesoría '{self.nombre}' [{self.id}] | Especialidad: {self.__especialidad} | "
                f"Nivel: {self.__nivel} | Tarifa: ${self.tarifa_base:,.0f}/hora")

    def validar_parametros(self, duracion, **opciones):
        """Una asesoría solo necesita una duración válida."""
        self._validar_duracion(duracion)
        return True

    def validar_integridad(self):
        """(P2) Revisa que los datos de la asesoría sigan siendo coherentes."""
        return (self.tarifa_base > 0 and self.__nivel in self.NIVELES
                and self.__especialidad in self.ESPECIALIDADES_VALIDAS)
