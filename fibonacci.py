import redis
import time
from collections import Counter

conn = redis.Redis(host="localhost", port="6379", db=1, password="admin123", decode_responses=True)

print(f"conexion con la db {conn.ping()}")
conn.flushdb()
print(f"Claves en la db1 {conn.dbsize()}")

#PARTE 2

def fib(n):
    if n <=0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)
    
print(" ")
print("=============================================================================================")
print("PARTE 2")
print("=============================================================================================")
print(" ")

for i in [30, 32, 35]:
    inicio = time.perf_counter()
    resultado = fib(i)
    fin = time.perf_counter()
    tiempo_total = (fin - inicio) * 1000 #tiempo en ms
    print(f"Fib({i}): {resultado} , tiempo: {tiempo_total} ms")

print(" ")
print("=============================================================================================")
print("PARTE 3")
print("=============================================================================================")
print(" ")

CLAVE_HIT = "stats:hits"
CLAVE_MISS = "stats:misses"
TTL = 30
def fib_cache(n):
    conn.lpush("Historial", n)
    conn.sadd("Consultados", n)
    clave = "fib:" + str(n)
    valor = conn.get(clave)
    if valor is not None:
        estado = "HIT"
        conn.incr(CLAVE_HIT)
    else:
        estado = "MISS"
        conn.incr(CLAVE_MISS)
        valor = fib(n)
        conn.set(clave, valor, ex=TTL)
    return valor, estado


tiempo_ahorrado = 0
tiempo_calculo_normal = 0
tiempo_consulta_hit = 0

for i in [30, 30, 25, 30, 25, 32, 32]:
    clave = "fib:" + str(i)

    inicio = time.perf_counter()
    valor, estado = fib_cache(i)
    fin = time.perf_counter()

    tiempo_total = (fin - inicio) * 1000

    if estado == "HIT":
        inicio_normal = time.perf_counter()
        fib(i)
        fin_normal = time.perf_counter()

        tiempo_normal = (fin_normal - inicio_normal) * 1000

        tiempo_calculo_normal += tiempo_normal
        tiempo_consulta_hit += tiempo_total

        tiempo_ahorrado += tiempo_normal - tiempo_total

    print(f"fib_cache({i}): {valor}, estado: {estado}, "
          f"tiempo: {tiempo_total:.4f} ms, TTL: {conn.ttl(clave)} seg")


print(" ")
print("=============================================================================================")
print("PARTE 4")
print("=============================================================================================")
print(" ")

hits = conn.get(CLAVE_HIT)
misses = conn.get(CLAVE_MISS)
print(f"Hits: {hits}")
print(f"Misses: {misses}")
porcentaje = (int(hits)/(int(hits)+int(misses))) * 100 
print(f"Porcentaje de aciertos: {porcentaje}%")

print(" ")
print("=============================================================================================")
print("PARTE 5")
print("=============================================================================================")
print(" ")

print(f"Ultimas 5 consultas (mas recientes): {conn.lrange("Historial", 0, 4)}")
print(f"Total de consultas realizadas: {conn.llen("Historial")}")

print(" ")
print("=============================================================================================")
print("PARTE 6")
print("=============================================================================================")
print(" ")

print(f"Total de numeros consutados: {conn.scard("Consultados")}")
print(f"El 30 fue consultado?: {conn.sismember("Consultados", 30)}")
print(f"El 10 fue consultado?: {conn.sismember("Consultados", 10)}")

print(" ")
print("=============================================================================================")
print("PARTE 7")
print("=============================================================================================")
print(" ")

conn.expire("fib:30", 1)
time.sleep(2)
print(f"La clave fib:30 existe? {conn.exists("fib:30")}")
valor, estado = fib_cache(30)
print(f"fib_cache(30): {valor}, estado: {estado}")

print(" ")
print("=============================================================================================")
print("Memorizacion")
print("=============================================================================================")
print(" ")

def fib_memo(n):
    if n <=0:
        return 0
    elif n == 1:
        return 1
    else:
        clave = "memo:" + str(n)
        valor_memorizado = conn.get(clave)
        if valor_memorizado is not None:
            return int(valor_memorizado)
        resultado = fib_memo(n - 1) + fib_memo(n - 2)
        conn.set(clave, resultado)
        return resultado

for i in [90]:
    inicio = time.perf_counter()
    resultado = fib_memo(i)
    fin = time.perf_counter()
    tiempo_total = (fin - inicio) * 1000 #tiempo en ms
    print(f"Fib_memo({i}): {resultado} , tiempo: {tiempo_total} ms")

print(" ")
print("=============================================================================================")
print("PARTE 8/ INVENTARIO DE CLAVES")
print("=============================================================================================")
print(" ")

total = conn.dbsize()
print("Total de claves (DBSIZE):", total)

claves = list(conn.scan_iter(match="*", count=100))   # SCAN, no KEYS


def prefijo(k):
    for p in ("fib:", "memo:", "stats:"):
        if k.startswith(p):
            return p + "*"
    return "(sin prefijo)"


por_prefijo = Counter(prefijo(k) for k in claves)
for p in ("fib:*", "memo:*", "stats:*", "(sin prefijo)"):
    print(f"  {p:<15} {por_prefijo.get(p, 0)}")

por_tipo = Counter(conn.type(k) for k in claves)
print("Por tipo:", dict(por_tipo))

con_ttl, permanentes = {}, 0
for k in sorted(claves):
    t = conn.ttl(k)
    if t >= 0:
        con_ttl[k] = t
    else:
        permanentes += 1
print("Claves con expiración:")
for k, t in con_ttl.items():
    print(f"  {k:<10} TTL = {t} s")
print("Claves permanentes:", permanentes)

hits = int(conn.get("stats:hits"))
misses = int(conn.get("stats:misses"))
tasa = hits / (hits + misses) * 100
print(f"stats:hits = {hits} | stats:misses = {misses} | tasa = {tasa:.2f} %")

print(f"Tiempo de cálculo normal de los HIT: {tiempo_calculo_normal} ms")
print(f"Tiempo real de las consultas HIT: {tiempo_consulta_hit} ms")
print(f"Tiempo total ahorrado por el caché: {tiempo_ahorrado} ms")