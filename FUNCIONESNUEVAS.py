def configurar_medicion_estadistica(self,
    tiempo_apertura=1.0,
    acoplamiento='DC',
    impedancia='50',
    atenuador='10',
    filtro_analogico=True,
    filtro_digital=True,
    freq_filtro_digital=1000,
    nivel_auto=True,
    nivel_disparo=0.5,
    medicion_continua=True,
    numero_muestras=100
):
    """
    Configura el instrumento CNT-91 para mediciones estadísticas como ADEV, media, std, etc.
    
    Parámetros:
        tiempo_apertura (float): Tiempo de adquisición en segundos. (SENS:ACQ:APER)
        acoplamiento (str): 'AC' o 'DC' (INP:COUP)
        impedancia (str): '50' o '1E6' (INP:IMP)
        atenuador (str): '1' o '10' (INP:ATT)
        filtro_analogico (bool): Activa/desactiva filtro analógico (INP:FILT)
        filtro_digital (bool): Activa/desactiva filtro digital (INP:FILT:DIG)
        freq_filtro_digital (int): Frecuencia de corte en Hz para filtro digital (INP:FILT:DIG:FREQ)
        nivel_auto (bool): Nivel de trigger automático (INP:LEV:AUTO)
        nivel_disparo (float): Valor de nivel de trigger manual si nivel_auto=False (INP:LEV)
        medicion_continua (bool): Si se realiza medición continua (INIT:CONT)
        numero_muestras (int): Número de muestras estadísticas (STAT:COUN)
    """
    # Reset + limpieza
    self.dev.write("*RST")
    self.dev.write("*CLS")

    # Apertura (tiempo de adquisición)
    self.dev.write(f"SENS:ACQ:APER {tiempo_apertura}")

    # Acoplamiento de entrada
    self.dev.write(f"INP:COUP {acoplamiento}")

    # Impedancia de entrada
    self.dev.write(f"INP:IMP {impedancia}")

    # Atenuador
    self.dev.write(f"INP:ATT {atenuador}")

    # Filtro analógico
    self.dev.write(f"INP:FILT {'ON' if filtro_analogico else 'OFF'}")

    # Filtro digital y frecuencia
    self.dev.write(f"INP:FILT:DIG {'ON' if filtro_digital else 'OFF'}")
    if filtro_digital:
        self.dev.write(f"INP:FILT:DIG:FREQ {freq_filtro_digital}")

    # Nivel de disparo
    self.dev.write(f"INP:LEV:AUTO {'ON' if nivel_auto else 'OFF'}")
    if not nivel_auto:
        self.dev.write(f"INP:LEV {nivel_disparo}")

    # Medición continua
    self.dev.write(f"INIT:CONT {'ON' if medicion_continua else 'OFF'}")

    # Número de muestras para estadísticas
    self.dev.write(f"STAT:COUN {numero_muestras}")


"""


cnt = CNT_frequenciometro()
cnt.configurar_medicion_estadistica(
    tiempo_apertura=10,
    acoplamiento='DC',
    impedancia='50',
    atenuador='10',
    filtro_analogico=True,
    filtro_digital=True,
    freq_filtro_digital=1000,
    nivel_auto=False,
    nivel_disparo=0.3,
    medicion_continua=True,
    numero_muestras=500
)




"""






def leer_estadisticas(self, tiempo_apertura=1.0, numero_muestras=100):
    """
    Ejecuta una adquisición estadística completa y devuelve los resultados clave.
    
    Parámetros:
        tiempo_apertura (float): Tiempo de apertura en segundos, debe coincidir con configuración previa.
        numero_muestras (int): Número de muestras estadísticas, debe coincidir con configuración previa.

    Retorna:
        dict con claves: 'media', 'min', 'max', 'pico_pico', 'std', 'adev'
    """
    import time

    # Limpieza previa
    self.dev.write("*CLS")

    # Iniciar adquisición estadística
    self.dev.write("INIT")

    # Tiempo estimado total = muestras × apertura (más margen)
    tiempo_total = tiempo_apertura * numero_muestras * 1.1
    time.sleep(tiempo_total)

    # Leer los valores estadísticos
    resultados = {}

    comandos = {
        'media': ':CALC:STAT:MEAN?',
        'min':   ':CALC:STAT:MIN?',
        'max':   ':CALC:STAT:MAX?',
        'pico_pico': ':CALC:STAT:PP?',
        'std':   ':CALC:STAT:STD?',
        'adev':  ':CALC:STAT:ADEV?'
    }

    for nombre, comando in comandos.items():
        self.dev.write(comando)
        respuesta = self.dev.read().strip()
        try:
            resultados[nombre] = float(respuesta)
        except ValueError:
            resultados[nombre] = None  # En caso de fallo en conversión

    return resultados




"""

cnt = CNT_frequenciometro()

cnt.configurar_medicion_estadistica(
    tiempo_apertura=1.0,
    acoplamiento='DC',
    impedancia='50',
    atenuador='10',
    filtro_analogico=True,
    filtro_digital=True,
    freq_filtro_digital=1000,
    nivel_auto=False,
    nivel_disparo=0.3,
    medicion_continua=True,
    numero_muestras=100
)

resultados = cnt.leer_estadisticas(tiempo_apertura=1.0, numero_muestras=100)

print(resultados)
"""