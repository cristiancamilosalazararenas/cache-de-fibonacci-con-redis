# Taller de Fibonacci con Redis

Proyecto de la asignatura **Bases de Datos II** que compara el cálculo recursivo de números de Fibonacci con una versión apoyada en **Redis** como caché, midiendo tiempos y llevando estadísticas de uso (hits/misses, historial de consultas, etc.).

## Contenido del repositorio

```
redis-project/
├── fibonacci.py     # Script principal del taller
├── .gitignore       # Archivos excluidos del control de versiones
└── README.md
```

## Requisitos

- **Python 3.13** (probado con 3.13.1)
- **Redis** en ejecución en `localhost:6379`
- Librería de Python [`redis`](https://pypi.org/project/redis/) (redis-py)

El script se conecta con esta configuración (definida directamente en `fibonacci.py`):

| Parámetro | Valor |
|-----------|-------|
| Host | `localhost` |
| Puerto | `6379` |
| Base de datos | `1` |
| Contraseña | `admin123` |
| `decode_responses` | `True` |

> Si tu servidor Redis usa otra contraseña, puerto o base de datos, ajusta la línea `conn = redis.Redis(...)` al inicio del script.

## Instalación

Desde la raíz del proyecto, en PowerShell:

```powershell
# Crear el entorno virtual (si no existe)
python -m venv .venv

# Activarlo
.\.venv\Scripts\Activate.ps1

# Instalar la dependencia
pip install redis
```

Para dejar constancia de las dependencias del proyecto:

```powershell
pip freeze > requirements.txt
```

## Ejecución

1. Asegúrate de que el servidor Redis esté levantado y acepte la contraseña configurada.
2. Ejecuta el script:

```powershell
python fibonacci.py
```

> ⚠️ **Atención:** el script ejecuta `FLUSHDB` al inicio, por lo que **borra todas las claves de la base de datos 1** (`db=1`). No lo ejecutes contra una base con datos que quieras conservar.

## Qué hace el script

El programa está dividido en las partes del taller:

| Sección | Descripción |
|---------|-------------|
| **Conexión** | Verifica la conexión con `PING`, limpia la base de datos y muestra el número de claves. |
| **Parte 2** | Calcula `fib(30)`, `fib(32)` y `fib(35)` de forma recursiva pura y mide el tiempo de cada cálculo. |
| **Parte 3** | Usa `fib_cache(n)`: busca `fib:{n}` en Redis; si existe es un **HIT**, si no, calcula el valor, lo guarda con TTL de **30 s** y lo registra como **MISS**. También apila cada consulta en la lista `Historial` y la añade al conjunto `Consultados`. |
| **Parte 4** | Muestra el total de hits, misses y el porcentaje de aciertos. |
| **Parte 5** | Consulta las últimas 5 entradas de `Historial` y el total de consultas realizadas. |
| **Parte 6** | Muestra cuántos números distintos se consultaron (`SCARD`) y comprueba si el 30 y el 10 están en `Consultados` (`SISMEMBER`). |
| **Parte 7** | Fuerza la expiración de `fib:30` (`EXPIRE` a 1 s), espera 2 s y comprueba con `EXISTS` que ya no está; al volver a pedirlo se produce un **MISS**. |
| **Memorización** | `fib_memo(90)` resuelve Fibonacci usando Redis como memoizador con claves `memo:{n}` (sin TTL). |
| **Parte 8** | Inventario de claves: `DBSIZE`, recorrido con `SCAN` (no `KEYS`), recuento por prefijo y por tipo, claves con expiración y resumen final de estadísticas y tiempos ahorrados. |

## Claves utilizadas en Redis

| Clave | Tipo | Descripción |
|-------|------|-------------|
| `fib:{n}` | String | Resultado cacheado de Fibonacci con TTL de 30 s. |
| `memo:{n}` | String | Valores memoizados por `fib_memo` (sin expiración). |
| `stats:hits` | String (contador) | Número de aciertos de caché. |
| `stats:misses` | String (contador) | Número de fallos de caché. |
| `Historial` | Lista | Historial de números consultados (el más reciente al inicio). |
| `Consultados` | Conjunto | Números distintos consultados. |

## Notas

- Las credenciales están escritas en el código porque es un proyecto académico. En un entorno real conviene moverlas a variables de entorno; el archivo `.env` ya está incluido en `.gitignore`.
- Las claves `memo:*` no tienen TTL, así que permanecen hasta que se ejecute `FLUSHDB` o se eliminen manualmente.
- El cálculo recursivo sin caché crece de forma exponencial; por eso las pruebas se hacen con valores moderados (`n` entre 25 y 35), mientras que la versión memoizada llega a `n = 90`.
