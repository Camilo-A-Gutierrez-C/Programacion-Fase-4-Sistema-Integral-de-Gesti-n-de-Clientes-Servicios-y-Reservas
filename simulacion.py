"""
Módulo: simulacion.py
Ejecuta 15 operaciones (6 válidas y 9 no válidas) usando el GestorSoftwareFJ.

Cada operación se crea sus propios datos si los necesita (funciones _cliente y
_servicio). Así, si una operación falla, las demás no se ven afectadas.
"""

from cliente import Cliente
from excepciones import SoftwareFJError
from logger_config import Logger
from reserva import Reserva
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala

# Datos de los clientes de demostración: (nombre, documento, correo, teléfono)
DATOS_CLIENTES = (
    ("Ana María Pérez", "1012345678", "ana.perez@correo.com", "3104567890"),
    ("Carlos Gómez", 80123456, "carlos.gomez@correo.com", "3159876543"),
)

# "Fábricas" de servicios: cada una es una mini-función que crea el servicio cuando se necesita.
# Los valores salen del Proyecto 2; las firmas (sin código manual) son las del Proyecto 1.
_FABRICAS_SERVICIOS = {
    "sala": lambda: ReservaSala("Sala Ejecutiva Santander", 80000, 20, tiene_videobeam=True),
    "sala_aux": lambda: ReservaSala("Sala Auditorio", 120000, 50, tiene_videobeam=False),
    "equipo": lambda: AlquilerEquipo(
        "Workstation Dell Precision", 65000, "Workstation", 5,
        especificaciones="Intel Core i9, 64GB RAM, RTX 4080", deposito_garantia=200000),
    "asesoria": lambda: AsesoriaEspecializada(
        "Auditoría Arquitectura Cloud", 150000, "Cloud", "senior"),
    # Este proyector se crea YA apagado (disponible=False) para probar el error
    "proyector": lambda: AlquilerEquipo("Proyector 4K", 30000, "Proyector", 2,
                                        disponible=False),
}
_servicios_demo = {}   # Aquí se guardan los servicios ya creados, para reutilizarlos


# Funciones auxiliares
def _cliente(gestor, indice):
    """Devuelve el cliente de demostración (0 o 1). Si no existe todavía, lo crea y lo registra."""
    nombre, documento, correo, telefono = DATOS_CLIENTES[indice]
    existente = gestor.buscar_cliente_por_documento(documento)
    if existente is not None:
        return existente
    return gestor.registrar_cliente(Cliente(nombre, documento, correo, telefono))


def _servicio(gestor, clave):
    """Devuelve el servicio de demostración indicado. Si no existe todavía, lo crea y lo registra."""
    if clave not in _servicios_demo:
        _servicios_demo[clave] = gestor.registrar_servicio(_FABRICAS_SERVICIOS[clave]())
    return _servicios_demo[clave]


def _nueva_reserva(gestor, cliente, servicio, duracion, **opciones):
    """Crea una reserva y la guarda en el gestor.
    opciones puede traer descuento, aplicar_iva, asistentes, unidades..."""
    return gestor.registrar_reserva(Reserva(cliente, servicio, duracion, **opciones))


# Ejecución controlada de cada operación
def _ejecutar(numero, tipo, descripcion, accion):
    """Ejecuta UNA operación y controla cualquier error para que el programa no se caiga.
    Devuelve True si terminó bien y False si falló."""
    print(f"\n[{numero:02d}] ({tipo}) {descripcion}")
    try:
        resultado = accion()                       # Corre la operación
    except SoftwareFJError as error:
        # Error propio del sistema: se muestra y el programa continúa.
        # Si la clase ya lo anotó en el log, aquí solo se deja una advertencia.
        if error.registrada:
            Logger.registrar_advertencia(
                f"Operación {numero} no completada - {descripcion}")
        else:
            Logger.registrar_error(f"Operación {numero} fallida - {descripcion}", error)
        print(f"     X Error controlado: {error}")
        if error.__cause__ is not None:            # Si el error venía de otro, lo muestra
            print(f"       Causa original: {error.__cause__}")
        return False
    except Exception as error:                     # Cualquier error imprevisto también se contiene
        Logger.registrar_error(f"Operación {numero} - error inesperado", error)
        print(f"     X Error inesperado controlado: {error}")
        return False
    else:
        # Solo si no hubo errores
        Logger.registrar_evento(f"Operación {numero} exitosa - {descripcion}")
        print(f"     OK {resultado}")
        return True
    finally:
        # Siempre, con o sin error
        Logger.registrar_evento(f"Operación {numero} finalizada")


def ejecutar_simulaciones(gestor):
    """Corre las 15 operaciones sobre el gestor recibido y devuelve un resumen."""
    _servicios_demo.clear()    # Permite ejecutar la simulación varias veces sin mezclar datos

    Logger.registrar_evento("===== INICIO DE LA SIMULACIÓN =====")

    # OPERACIONES VÁLIDAS
    def v1():  # Registrar clientes válidos (ahora con teléfono)
        for datos in DATOS_CLIENTES:
            gestor.registrar_cliente(Cliente(*datos))   # El * reparte la tupla en argumentos
        return " / ".join(c.mostrar_datos() for c in gestor.clientes)

    def v2():  # Sala con VideoBeam, 4 horas, 10 % de descuento -> esperado $358.785,00
        reserva = _nueva_reserva(gestor, _cliente(gestor, 0), _servicio(gestor, "sala"), 4,
                                 descuento=0.10, asistentes=8)
        reserva.confirmar()
        reserva.procesar()
        return reserva.mostrar_reserva()

    def v3():  # Equipo 5 días, 5 % de descuento, con garantía -> esperado $567.412,50
        equipo = _servicio(gestor, "equipo")
        reserva = _nueva_reserva(gestor, _cliente(gestor, 0), equipo, 5,
                                 descuento=0.05, unidades=1)
        reserva.confirmar()
        stock_alquilado = equipo.stock       # Al confirmar, el stock baja de 5 a 4
        reserva.procesar()                   # Al procesar, la unidad regresa: stock vuelve a 5
        return (f"{reserva.mostrar_reserva()} | Stock durante el alquiler: "
                f"{stock_alquilado} | Stock al devolver: {equipo.stock}")

    def v4():  # Asesoría senior, 6 horas, SIN IVA -> esperado $1.125.000,00
        reserva = _nueva_reserva(gestor, _cliente(gestor, 1), _servicio(gestor, "asesoria"), 6,
                                 aplicar_iva=False)
        reserva.confirmar()
        reserva.procesar()
        return reserva.mostrar_reserva()

    def v5():  # Reservar, confirmar y cancelar: el servicio se bloquea y luego se libera
        asesoria = _servicio(gestor, "asesoria")
        reserva = _nueva_reserva(gestor, _cliente(gestor, 1), asesoria, 2)
        reserva.confirmar()
        disponible_confirmada = asesoria.disponible   # Debe ser False (está bloqueada)
        reserva.cancelar()
        return (f"{reserva.mostrar_reserva()} | Disponible al confirmar: "
                f"{disponible_confirmada} | Disponible al cancelar: {asesoria.disponible}")

    def v6():  # Sobrecarga simulada: tres formas de cotizar la misma sala
        sala = _servicio(gestor, "sala")
        base = sala.cotizar(2)                  # Solo duración: sin descuento y con IVA
        con_descuento = sala.cotizar(2, 0.10)   # Duración + 10 % de descuento
        completo = sala.cotizar(2, 0.10, False) # Duración + 10 % de descuento + SIN IVA
        return (f"Sala 2 h -> básico: ${base:,.2f} | 10 % desc.: ${con_descuento:,.2f} | "
                f"10 % desc. sin IVA: ${completo:,.2f}")

    # OPERACIONES NO VÁLIDAS
    def i1():  # Cliente con nombre, documento, correo y teléfono inválidos
        return gestor.registrar_cliente(Cliente("L1", "12AB", "luis@@correo", "123"))

    def i2():  # Servicio mal creado: tarifa negativa
        return ReservaSala("Sala VIP", -50000, 10)

    def i3():  # Falta el parámetro obligatorio 'asistentes'
        return _nueva_reserva(gestor, _cliente(gestor, 0), _servicio(gestor, "sala"), 2)

    def i4():  # Servicio apagado: el proyector está no disponible
        return _nueva_reserva(gestor, _cliente(gestor, 0), _servicio(gestor, "proyector"), 1,
                              unidades=1)

    def i5():  # Servicio ocupado: la primera reserva lo bloquea, la segunda no puede
        auditorio = _servicio(gestor, "sala_aux")
        primera = _nueva_reserva(gestor, _cliente(gestor, 0), auditorio, 2, asistentes=10)
        primera.confirmar()     # El auditorio queda ocupado
        return _nueva_reserva(gestor, _cliente(gestor, 1), auditorio, 1, asistentes=5)

    def i6():  # Operación no permitida: procesar una reserva cancelada
        reserva = _nueva_reserva(gestor, _cliente(gestor, 1), _servicio(gestor, "sala"), 1,
                                 asistentes=3)
        reserva.cancelar()
        return reserva.procesar()

    def i7():  # Descuento ilegal: 85 % en una asesoría (el tope es 30 %)
        return _nueva_reserva(gestor, _cliente(gestor, 0), _servicio(gestor, "asesoria"), 3,
                              descuento=0.85)

    def i8():  # Operación no permitida: cancelar una reserva que ya fue procesada
        reserva = _nueva_reserva(gestor, _cliente(gestor, 1), _servicio(gestor, "asesoria"), 1)
        reserva.confirmar()
        reserva.procesar()
        return reserva.cancelar()

    def i9():  # Cliente duplicado: mismo documento que Ana María
        return gestor.registrar_cliente(
            Cliente("Ana María Pérez", "1012345678", "otro.correo@correo.com", "3001112233"))

    # Lista con todas las operaciones: (tipo, descripción, función)
    operaciones = [
        ("VÁLIDA", "Registrar clientes válidos (con teléfono)", v1),
        ("VÁLIDA", "Sala con VideoBeam, 4 h y 10 % de descuento", v2),
        ("VÁLIDA", "Alquilar equipo con garantía (el stock baja y sube)", v3),
        ("VÁLIDA", "Asesoría senior de 6 h sin IVA", v4),
        ("VÁLIDA", "Crear, confirmar y cancelar (el servicio se libera)", v5),
        ("VÁLIDA", "Cotizar una sala de tres formas (sobrecarga)", v6),
        ("NO VÁLIDA", "Registrar cliente con datos inválidos", i1),
        ("NO VÁLIDA", "Crear sala con tarifa negativa", i2),
        ("NO VÁLIDA", "Reservar sala sin indicar asistentes", i3),
        ("NO VÁLIDA", "Reservar un servicio no disponible", i4),
        ("NO VÁLIDA", "Reservar una sala que ya está ocupada", i5),
        ("NO VÁLIDA", "Procesar una reserva cancelada", i6),
        ("NO VÁLIDA", "Asesoría con descuento del 85 % (cálculo inconsistente)", i7),
        ("NO VÁLIDA", "Cancelar una reserva ya procesada", i8),
        ("NO VÁLIDA", "Registrar un cliente con documento repetido", i9),
    ]

    resumen = {"exitosas": 0, "fallidas": 0}
    # enumerate(..., start=1) numera las operaciones desde 1
    for numero, (tipo, descripcion, accion) in enumerate(operaciones, start=1):
        if _ejecutar(numero, tipo, descripcion, accion):
            resumen["exitosas"] += 1
        else:
            resumen["fallidas"] += 1

    Logger.registrar_evento(
        f"===== FIN DE LA SIMULACIÓN: {resumen['exitosas']} exitosas, "
        f"{resumen['fallidas']} fallidas =====")
    return resumen
