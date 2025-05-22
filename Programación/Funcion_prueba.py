### probar añadir el acoplamiento AC , filtro , atenuacion etc 
### Las graficas se ven feas : generar linea de tendencia en lugar de puntos



# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== PRUEBA DE LA FUNCIÓN CON FORM:DATA REAL ======

# Parámetros de la prueba
n_muestras = 1500
intervalo_s = 0.3

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.3  # igual que en la función, para ser coherente
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición
resultado = objt_prueba.medir_n_muestras_equidistantesV6(
    n_muestras=n_muestras,
    intervalo_s=intervalo_s,
    graficarFT=True,
    graficarDevTau=True,
    exportar_excel=True
)

# Comprobación y presentación amigable
if resultado is None or resultado[0] is None:
    print("No se recibieron datos válidos. Revisa los mensajes de error y depuración anteriores.")
else:
    frecuencias, timestamps, delta_tiempos, allan_deviations, taus = resultado

    print("\nResultados de la medición:")
    for i in range(len(frecuencias)):
        print(f"Muestra {i+1} : {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")

    print("\nDATOS  : Allan deviations y Taus")
    for i in range(len(allan_deviations)):
        print(f"Tau {taus[i]:.3f} s: Allan deviation = {allan_deviations[i]:.6f} Hz")