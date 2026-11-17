"""
Módulo: main.py

Ejecución:  python main.py
"""

from gestor import GestorSoftwareFJ
from logger_config import Logger
from simulacion import ejecutar_simulaciones


def main():
    """Prepara el logger, corre la simulación y muestra el resumen final."""
    Logger.configurar_logger()   # Deja listo el archivo de logs
    print("=" * 70)
    print(" SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)

    gestor = GestorSoftwareFJ()  # Aquí vivirán clientes, servicios y reservas

    try:
        resumen = ejecutar_simulaciones(gestor)
    except KeyboardInterrupt:
        # El usuario presionó Ctrl+C: se sale con elegancia
        Logger.registrar_evento("Ejecución interrumpida por el usuario")
        print("\nEjecución interrumpida por el usuario.")
        return
    except Exception as error:
        # Última red de seguridad: si algo inesperado pasa, el programa no se cae
        Logger.registrar_error("Error crítico en la ejecución principal", error)
        print(f"Error crítico controlado: {error}")
        return
    finally:
        print("\n" + "-" * 70)

    # Resumen final usando los datos del gestor
    totales = gestor.resumen()
    print("RESUMEN FINAL")
    print(f"  Operaciones exitosas : {resumen['exitosas']}")
    print(f"  Operaciones fallidas : {resumen['fallidas']} (controladas, el sistema siguió activo)")
    print(f"  Clientes registrados : {totales['clientes']}")
    print(f"  Servicios creados    : {totales['servicios']}")
    print(f"  Reservas creadas     : {totales['reservas']}")
    for reserva in gestor.reservas:
        print(f"    - {reserva.mostrar_reserva()}")
    print("  Estado final de los servicios:")
    for servicio in gestor.servicios:
        estado = "disponible" if servicio.disponible else "NO disponible"
        print(f"    - {servicio.nombre} [{servicio.id}]: {estado}")
    print(f"\nRegistro completo de eventos y errores en: {Logger.RUTA_LOG}")


if __name__ == "__main__":
    main()
