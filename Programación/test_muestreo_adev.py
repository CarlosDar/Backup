"""
Script de prueba para la función muestreo_adev_improved2 del CNT-91.
"""

import pandas as pd
import matplotlib.pyplot as plt
from CNT_9X_pendulum import CNT_frequenciometro
from datetime import datetime

def test_muestreo_adev():
    # Crear instancia del instrumento
    cnt = CNT_frequenciometro()
    
    # Parámetros de prueba
    n_bloques = 3
    muestras_por_bloque = 50
    pacing_time_ms = 20
    canal = 'A'
    
    print("Iniciando prueba de muestreo ADEV...")
    print(f"Configuración:")
    print(f"- Número de bloques: {n_bloques}")
    print(f"- Muestras por bloque: {muestras_por_bloque}")
    print(f"- Tiempo entre muestras: {pacing_time_ms}ms")
    print(f"- Canal: {canal}")
    
    # Realizar el muestreo
    resultados = cnt.muestreo_adev_improved2(
        n_bloques=n_bloques,
        muestras_por_bloque=muestras_por_bloque,
        pacing_time_ms=pacing_time_ms,
        canal=canal
    )
    
    # Convertir resultados a DataFrame
    df = pd.DataFrame(resultados)
    
    # Mostrar resultados en consola
    print("\nResultados del muestreo:")
    print(df.to_string(index=False))
    
    # Crear gráficas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Gráfica de ADEV por bloque
    ax1.plot(df['bloque'], df['adev'], 'bo-', label='ADEV')
    ax1.set_xlabel('Bloque')
    ax1.set_ylabel('Allan Deviation [Hz]')
    ax1.set_title('Allan Deviation por Bloque')
    ax1.grid(True)
    
    # Gráfica de estadísticas por bloque
    ax2.plot(df['bloque'], df['media'], 'ro-', label='Media')
    ax2.plot(df['bloque'], df['sdev'], 'go-', label='SDEV')
    ax2.plot(df['bloque'], df['min'], 'mo-', label='Mín')
    ax2.plot(df['bloque'], df['max'], 'co-', label='Máx')
    ax2.set_xlabel('Bloque')
    ax2.set_ylabel('Valor [Hz]')
    ax2.set_title('Estadísticas por Bloque')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    
    # Guardar gráficas
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'muestreo_adev_{fecha_hora}.png')
    
    # Exportar resultados a Excel
    nombre_excel = f'muestreo_adev_{fecha_hora}.xlsx'
    df.to_excel(nombre_excel, index=False)
    print(f"\nResultados guardados en: {nombre_excel}")
    
    # Mostrar gráficas
    plt.show()

if __name__ == "__main__":
    test_muestreo_adev() 