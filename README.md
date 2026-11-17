# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Programa en Python, orientado a objetos y sin base de datos, que administra **clientes**, **servicios**
(salas, alquiler de equipos y asesorías) y **reservas**. Valida los datos que recibe, calcula el costo de
cada reserva, controla qué servicios están disponibles y deja un registro de todo lo que ocurre en un
archivo de log, sin detenerse nunca por un error.

---

## ¿Qué hace el programa?

- **Registra clientes** con nombre, documento, correo y teléfono (opcional), validando cada dato. No permite dos clientes con el mismo documento.
- **Ofrece tres tipos de servicio**: reserva de salas, alquiler de equipos y asesorías especializadas, cada uno con su propia forma de calcular el costo.
- **Crea reservas** que un cliente hace sobre un servicio, y las lleva por un ciclo de vida: pendiente → confirmada → procesada (o cancelada).
- **Calcula el costo total** de cada reserva con descuento opcional e IVA opcional.
- **Controla la disponibilidad**: una sala o una asesoría confirmada queda ocupada hasta que se procesa o se cancela; los equipos descuentan unidades de su stock.
- **Tolera los errores**: cualquier dato inválido o acción no permitida genera un error propio y claro, que se anota en el log mientras el programa continúa.
- **Deja un registro** (`logs/software_fj.log`) con la fecha, la hora y el detalle de cada evento y error, incluida la causa original cuando un error viene de otro.

Al ejecutarlo, el programa corre una **simulación de 15 operaciones** (6 válidas y 9 inválidas a propósito) para mostrar cómo responde en cada caso, y termina con un resumen.

---

## Cómo ejecutarlo

```bash
python main.py
```

- Requiere **Python 3.8 o superior**. No usa librerías externas.
- La carpeta `logs/` y el archivo de log se crean solos. Cada ejecución agrega líneas al final.
- También se incluye `SoftwareFJ_Integrado.ipynb`, con el mismo código dividido por módulos, para abrirlo en Jupyter o Google Colab (ejecuta las celdas de arriba hacia abajo).

### Ejemplo de lo que muestra

```
[02] (VÁLIDA) Sala con VideoBeam, 4 h y 10 % de descuento
     OK Reserva RES-001 | Cliente: Ana María Pérez | Servicio: Sala Ejecutiva Santander | Duración: 4 | Descuento: 10% | con IVA | Estado: PROCESADA | Total: $358,785.00

[10] (NO VÁLIDA) Reservar un servicio no disponible
     X Error controlado: El servicio 'Proyector 4K' no está disponible

[13] (NO VÁLIDA) Asesoría con descuento del 85 % (cálculo inconsistente)
     X Error controlado: No se pudo crear la reserva para Auditoría Arquitectura Cloud: El descuento para asesorías debe estar entre 0 % y 30% (se pidió 85%)
       Causa original: El descuento para asesorías debe estar entre 0 % y 30% (se pidió 85%)
```

Al final imprime cuántas operaciones salieron bien y cuántas fallaron de forma controlada, las reservas creadas con su estado y el estado de cada servicio.

---

## Clientes

| Dato | Regla |
|---|---|
| Nombre | Solo letras (con tildes y ñ) y espacios; mínimo 3 caracteres |
| Documento | Entre 6 y 12 dígitos; no puede repetirse |
| Correo | Formato `usuario@dominio.ext`; se guarda en minúsculas |
| Teléfono | Opcional; si se entrega, entre 7 y 15 dígitos |

Si varios datos están mal, el error los reporta **todos juntos** en un solo mensaje. Cada cliente recibe un ID automático (`CLI-001`, `CLI-002`…); si el cliente no es válido, no se gasta ningún ID.

---

## Servicios

| | Reserva de sala | Alquiler de equipo | Asesoría especializada |
|---|---|---|---|
| Clase | `ReservaSala` | `AlquilerEquipo` | `AsesoriaEspecializada` |
| La duración se mide en | Horas | Días | Horas |
| Duración permitida | 1 a 12 | 1 a 30 | 1 a 8 |
| Dato obligatorio al reservar | `asistentes` | `unidades` | — |
| Cargo adicional | VideoBeam: $15.000 (si la sala lo incluye) | Garantía por unidad (sin IVA) | Asesor *senior*: tarifa × 1,25 |
| Descuento máximo | 50 % | 40 % | 30 % |
| Se ocupa al confirmar | Toda la sala | Solo las unidades alquiladas (stock) | Todo el servicio |

Cada servicio recibe un ID automático (`SRV-001`…). Cómo se crea cada uno:

```python
ReservaSala(nombre, tarifa_hora, capacidad, disponible=True, tiene_videobeam=True)
AlquilerEquipo(nombre, tarifa_dia, tipo_equipo, stock, disponible=True,
               especificaciones=None, deposito_garantia=0.0)
AsesoriaEspecializada(nombre, tarifa_hora, especialidad, nivel="junior", disponible=True)
```

- **Sala**: capacidad entre 1 y 100 personas; no se aceptan más asistentes que la capacidad.
- **Equipo**: el stock debe alcanzar para las unidades pedidas. Las especificaciones, si se dan, deben tener al menos 5 caracteres.
- **Asesoría**: la especialidad debe ser `ARQUITECTURA`, `CIBERSEGURIDAD`, `CLOUD`, `DATOS` o `DEVOPS` (da igual si se escribe en mayúsculas o minúsculas) y el nivel `junior` o `senior`.

---

## Cómo se calcula el costo

El IVA es del **19 %** y se puede quitar con `aplicar_iva=False`.

| Servicio | Fórmula |
|---|---|
| Sala | `(tarifa × horas + VideoBeam) × (1 − descuento) × 1,19` |
| Equipo | `tarifa × días × unidades × (1 − descuento)`, más el 19 % de IVA sobre ese valor, más la garantía (`depósito × unidades`, sin IVA) |
| Asesoría | `tarifa × horas × factor del nivel × (1 − descuento) × 1,19` (el factor es 1,0 para *junior* y 1,25 para *senior*) |

**Ejemplos** (con los valores de la simulación):

| Caso | Cálculo | Total |
|---|---|---|
| Sala $80.000/h, 4 h, VideoBeam, 10 % de descuento | (320.000 + 15.000) × 0,90 × 1,19 | **$358.785,00** |
| Equipo $65.000/día, 5 días, 1 unidad, 5 % de descuento, garantía $200.000 | 308.750 + 58.662,50 de IVA + 200.000 | **$567.412,50** |
| Asesoría senior $150.000/h, 6 h, sin IVA | 150.000 × 6 × 1,25 | **$1.125.000,00** |

Un equipo se puede cotizar sin garantía con `incluir_garantia=False` (el ejemplo anterior bajaría a $367.412,50).

### Cotizar sin reservar

`cotizar()` calcula un precio de prueba y cambia de variante según cuántos argumentos reciba:

```python
sala.cotizar(2)                # 2 horas, sin descuento, con IVA       -> 208250.0
sala.cotizar(2, 0.10)          # con 10 % de descuento                  -> 187425.0
sala.cotizar(2, 0.10, False)   # con 10 % de descuento y sin IVA        -> 157500.0
```

---

## Reservas

Una reserva une un **cliente**, un **servicio** y una **duración**, y se crea así:

```python
Reserva(cliente, servicio, duracion, descuento=0.0, aplicar_iva=True, **datos_del_servicio)
# Ejemplos de datos_del_servicio: asistentes=8, unidades=2, incluir_garantia=False
```

El costo se calcula **en el momento de crear la reserva**, por lo que un descuento inválido o un dato faltante se detecta de inmediato.

### Estados

```
PENDIENTE ──confirmar()──▶ CONFIRMADA ──procesar()──▶ PROCESADA
    │                          │
    └──────── cancelar() ──────┴──▶ CANCELADA
```

| Acción | Qué hace | Cuándo no se puede |
|---|---|---|
| `confirmar()` | Pasa a CONFIRMADA y **ocupa** el servicio (o descuenta unidades del stock) | Si no está PENDIENTE, si el servicio ya no está disponible o si el stock ya no alcanza |
| `procesar()` | Pasa a PROCESADA, **libera** el servicio y devuelve el costo total | Si no está CONFIRMADA |
| `cancelar()` | Pasa a CANCELADA; si estaba confirmada, libera el servicio | Si ya está CANCELADA o PROCESADA |

Reglas de disponibilidad:

- No se puede crear una reserva sobre un servicio que esté ocupado o desactivado.
- Cancelar una reserva **pendiente** no libera nada, porque nunca ocupó el servicio.
- Cuando el stock de un equipo llega a 0, el equipo queda no disponible hasta que se devuelvan unidades.
- Si dos reservas pendientes piden la última unidad, solo la primera que se confirme lo logra; la otra falla.

---

## Uso desde código

```python
from cliente import Cliente
from servicio import ReservaSala
from reserva import Reserva
from gestor import GestorSoftwareFJ

gestor = GestorSoftwareFJ()

ana = gestor.registrar_cliente(
    Cliente("Ana María Pérez", "1012345678", "ana@correo.com", "3104567890"))
sala = gestor.registrar_servicio(ReservaSala("Sala Ejecutiva", 80000, 20))

reserva = gestor.registrar_reserva(
    Reserva(ana, sala, 4, descuento=0.10, asistentes=8))
print(reserva.estado, reserva.costo_total)   # PENDIENTE 358785.0

reserva.confirmar()
print(sala.disponible)                        # False (la sala quedó ocupada)

print(reserva.procesar())                     # 358785.0
print(reserva.estado, sala.disponible)        # PROCESADA True
```

`GestorSoftwareFJ` guarda los clientes, servicios y reservas en memoria. Sus listas son de solo lectura (`gestor.clientes`, `gestor.servicios`, `gestor.reservas` devuelven tuplas) y se usan `registrar_cliente`, `registrar_servicio`, `registrar_reserva` y `buscar_cliente_por_documento` para trabajar con ellas.

---

## Errores

Todos los errores del sistema heredan de `SoftwareFJError`, así que con un solo `except SoftwareFJError` se atrapa cualquiera.

| Excepción | Cuándo aparece |
|---|---|
| `ClienteInvalidoError` | Nombre, documento, correo o teléfono con formato incorrecto |
| `ClienteDuplicadoError` | Documento que ya pertenece a otro cliente |
| `ServicioInvalidoError` | Servicio mal creado: tarifa ≤ 0, capacidad fuera de rango, especialidad o nivel no válidos… |
| `ParametroInvalidoError` | Duración fuera de rango, asistentes o unidades con un valor no válido |
| `ParametroFaltanteError` | Falta un dato obligatorio (`asistentes` en una sala, `unidades` en un equipo) |
| `ServicioNoDisponibleError` | El servicio está ocupado, desactivado o sin stock |
| `CalculoInconsistenteError` | Descuento por encima del tope del servicio o total no válido |
| `ReservaError` | No se pudo crear, confirmar, cancelar o procesar una reserva |
| `OperacionNoPermitidaError` | Acción no permitida en el estado actual (por ejemplo, procesar una reserva cancelada) |

Cuando un error se produce a causa de otro, se conservan los dos: el mensaje general y la **causa original**. Ambos aparecen en pantalla y en el log.

---

## Registro de eventos (log)

El archivo `logs/software_fj.log` guarda una línea por evento, con fecha, hora y nivel:

```
2026-11-17 20:18:28,790 | INFO    | Reserva RES-001 creada: cliente CLI-001, servicio SRV-001, total $358,785.00
2026-11-17 20:18:28,790 | ERROR   | Error en Reserva.__init__ | ServicioNoDisponibleError: El servicio 'Proyector 4K' no está disponible
2026-11-17 20:18:28,790 | WARNING | Operación 10 no completada - Reservar un servicio no disponible
```

- **INFO**: algo normal (cliente registrado, reserva confirmada, operación terminada).
- **WARNING**: una operación no se completó.
- **ERROR**: el error exacto, dónde ocurrió y su causa original. Cada error se escribe una sola vez.

Si no se puede escribir el archivo (por ejemplo, por falta de permisos), el programa **no se detiene**: muestra los mensajes en consola.

---

## Estructura del proyecto

```
software_fj_integrado/
├── main.py            Punto de entrada: corre la simulación y muestra el resumen final
├── simulacion.py      Las 15 operaciones de demostración
├── gestor.py          GestorSoftwareFJ: guarda y consulta clientes, servicios y reservas
├── entidad.py         EntidadBase (clase abstracta): asigna los IDs automáticos
├── cliente.py         Cliente y sus validaciones
├── servicio.py        Servicio (abstracta), ReservaSala, AlquilerEquipo, AsesoriaEspecializada
├── reserva.py         Reserva y su ciclo de vida
├── excepciones.py     Excepciones propias del sistema
├── logger_config.py   Logger y decorador @registrar_errores
├── SoftwareFJ_Integrado.ipynb   El mismo código en formato notebook
└── logs/              Aquí se genera software_fj.log
```

---

## Conceptos de programación orientada a objetos que aplica

| Concepto | Dónde se ve |
|---|---|
| **Abstracción** | `EntidadBase` y `Servicio` son clases abstractas: no se pueden crear directamente |
| **Herencia** | `Cliente`, `Servicio` y `Reserva` heredan de `EntidadBase`; los tres servicios heredan de `Servicio` |
| **Polimorfismo** | `calcular_costo()`, `describir()` y `validar_parametros()` se comportan distinto en cada servicio |
| **Encapsulación** | Los datos son privados (`__nombre`, `__estado`…) y solo se cambian mediante métodos que validan |
| **Sobrecarga simulada** | `cotizar()` y `calcular_costo()` aceptan distintas combinaciones de argumentos |
| **Manejo de excepciones** | Excepciones propias, `try/except/else/finally` y encadenamiento con `raise … from` |
| **Decoradores** | `@registrar_errores` anota en el log cualquier error propio donde ocurre |

---

## Limitaciones

- **Los datos viven en memoria**: al cerrar el programa se pierden los clientes, servicios y reservas. Lo único que se conserva en disco es el log.
- **No tiene menú interactivo**: al ejecutarse corre la simulación incluida. Para usarlo con datos propios se importan las clases, como en el ejemplo de "Uso desde código".
