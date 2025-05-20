"""

Created on Mon Feb 24 11:47 2025

@author: Carlos Darvoy Espigulé

Objetivo : crear clase de un instrumento de medida

MI MODELO : Timer/Counter/Analyzer CNT_91

"""
""" Comunicación PVISA;  """

    
""" ═━═━═━═━═━═━═━═━═━═━═━═ Definición de Clase ━═━═━═━═━═━═━═━━═━═━═━═━ """
class CNT_frequenciometro: 
   
   
    """ Address: Dirección del recurso VISA 
    Por defecto -> "GPIB0::18::INSTR" instrumento conectado vía GPIB """   
    def __init__(self, address ='GPIB0::10::INSTR'):
        
        import pyvisa
        from pyvisa.highlevel import ResourceManager
        
        rm =ResourceManager() 
        #Se crea una instancia de ResourceManager 
        #Detección y Administración de conexion con el instrumento
        
        self.dev=rm.open_resource(address)
        #Utiliza el objeto rm para abrir una 
        #conexión con el instrumento especificado por la dirección address.
        #self.dev: representa el instrumento para enviar,recibir 
        #self.dev.write('*CLS')  # Limpiar errores previos
        self.dev.write('*IDN?')
        #Envio comando SCPI  -> *IDN? (identificación estándar)
        #permite verificar que la comunicación se ha establecido correctamente.
        
        resposta=self.dev.read()
        #Lee la respuesta que el instrumento envía tras recibir el comando *IDN?.
        #almacenada en la variable resposta, generalmente contiene información 
        #identificativa del dispositivo.
        
        self.dev.write('*OPT?')
        #Envio comando SCPI  -> *IDN? (identificación estándar)
        #permite verificar que la comunicación se ha establecido correctamente.
        
        resposta2=self.dev.read()
        #Lee 
        
        print('Communication established with GSE-UIB ' + resposta  )
        #Enseña la respuesta          
        print('Options instaled   ' + resposta2  )

        

   

   # UNA MEDICIÓN DE FREQUENCIA
    def measure_frequency(self, channel='A'):
        
        """
        Realiza una medición única de frecuencia en el canal especificado.
        
        Parámetros:
          channel (str o int): Puede ser 'A', 'B', 1 o 2.
                               - 'A' o 1 medirá el canal A (comando MEASure:FREQ? (@1))
                               - 'B' o 2 medirá el canal B (comando MEASure:FREQ? (@2))
                               Por defecto se utiliza el canal A.
        
        Retorna:
          La respuesta del instrumento con el valor medido.
        """
        # Limpieza de errores previos
        self.dev.write("*CLS")
        
        # Diccionario para mapear la entrada a su comando correspondiente
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        
        canal_seleccionado = str(channel).upper()
        if canal_seleccionado not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        
        # Construir y enviar el comando basado en el canal seleccionado
        comando = f"MEASure:FREQ? ({canales[canal_seleccionado]})"
        self.dev.write(comando)
        
        # Leer y retornar la respuesta del instrumento
        response = self.dev.read()
        return response
    
    
    
    








# MEDICION DE TEMPERATURA
        
        """  Es La temperatura a la salida del fan del instrumento en el controlador """   
    def Measure_temperature_example(self):
             
             self.dev.write(':SYST:TEMP?')
             temp = self.dev.read()
             return temp 






# JOAN 2

# MEDICIÓN CONTINUA DE FREQUENCIAS [[Medición continua]+[FETCH on FLY]]
# Especialmente rápida en solo 50s ha sacado 1700 medidas, Pero el tiempo que tarda es desconocido

    def measure_frequency_array_CONTINUOUS(self, duration_s, channel='A'):
        """
        Mide frecuencias de manera continua durante un tiempo dado, usando el canal especificado.
    
        Parámetros:
            duration_s (float): Duración total de la medida en segundos.
            channel (str|int): Canal a medir ('A', 'B', 1 o 2). Por defecto 'A'.
    
        Retorna:
            lista de floats con los valores medidos.
        """
        import time
    
        # ========== SECCIÓN 1: Selección y validación del canal ==========
        # Diccionario para mapear la selección de canal del usuario a la sintaxis SCPI correcta
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        ch = str(channel).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_cmd = canales[ch]
    
        # ========== SECCIÓN 2: Configuración inicial del instrumento ==========
        # 1. Resetear el instrumento para asegurar estado limpio
        self.dev.write("*RST")
        # 2. Limpiar errores previos para evitar problemas durante la medición
        self.dev.write("*CLS")
        # 3. Desactivar cálculos internos automáticos que podrían interferir con la adquisición continua
        self.dev.write(":CALC:STAT OFF")
        # 4. Configurar el instrumento para medición continua de frecuencia en el canal elegido
        self.dev.write(f":CONF:ARR:FREQ? ( ,({canal_cmd}))")
        # 5. Iniciar la adquisición continua
        self.dev.write(":INIT:CONT ON")
    
        # ========== SECCIÓN 3: Adquisición continua de datos ==========
        t0 = time.time()         # Guardar el instante de inicio
        results = []             # Lista para almacenar resultados
        try:
            while (time.time() - t0) < duration_s:
                # 5. Solicitar el último valor disponible sin detener la adquisición continua
                self.dev.write("FETC:ARR? -1")
                resp = self.dev.read().strip()
                try:
                    # 6. Intentar convertir la respuesta a float y almacenar
                    val = float(resp)
                    results.append(val)
                except ValueError:
                    # 7. Si la respuesta no es un número, ignorar (pueden aparecer respuestas vacías o errores de comunicación)
                    pass
        finally:
            # ========== SECCIÓN 4: Finalización segura ==========
            # 8. Asegurarse de detener la adquisición continua al final, ocurra lo que ocurra en el bucle
            self.dev.write(":INIT:CONT OFF")
    
        # ========== SECCIÓN 5: Devolver resultados ==========
        return results
    
    


#JOAN 3 PROBAMOS OTRO METODO Usar el modo de medición con "Sample Timer"
# JOAN 3
# Hay un error el el tiempo de 0.02s aproximadamente, El tiempo que tarda es conocido


    def medir_n_muestras_equidistantes(self, n_muestras=10, intervalo_s=0.1, canal='A'):
        """
        Realiza una adquisición de 'n_muestras' equidistantes en el tiempo usando el CNT-91,
        devolviendo para cada muestra la frecuencia y el timestamp asociado, pudiendo elegir el canal de entrada.
    
        Parámetros:
            n_muestras: int
                Número de muestras a medir (por defecto 10)
            intervalo_s: float
                Intervalo de tiempo entre muestras en segundos (por defecto 0.1s)
            canal: str o int
                Canal de medida: 'A', 'B', 1 o 2 (por defecto 'A')
    
        Devuelve:
            lista de tuplas (frecuencia, delta_t) en floats
            (El tiempo de cada muestra es relativo al primero, es decir, delta_t = t - t0)
        """
    
        import time
    
        # ========== SECCIÓN 1: Validación y selección de canal ==========
        # Diccionario para convertir la selección del usuario al formato SCPI adecuado
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_cmd = canales[ch]
    
        # ========== SECCIÓN 2: Configuración mínima del instrumento ==========
        # 1. Resetear el instrumento para asegurar estado limpio
        self.dev.write('*RST')
        # 2. Limpiar errores previos para evitar problemas durante la medición
        self.dev.write("*CLS")
        # 3. Configurar función de frecuencia en el canal seleccionado
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        # 4. Configurar el intervalo entre muestras (apertura/pacing)
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
        # 5. Establecer el número de muestras a adquirir (adquisición en bloque)
        self.dev.write(f'ARM:COUN {n_muestras}')
        # 6. Activar la inclusión del timestamp en la respuesta
        self.dev.write('FORM:TINF ON')
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición ==========
        # 7. Iniciar la adquisición
        self.dev.write('INIT')
    
        # ========== SECCIÓN 4: Espera para completar la adquisición ==========
        # 8. Calcular y esperar el tiempo suficiente para que el instrumento termine
        #    Se añade un 10% extra como margen de seguridad
        tiempo_espera = intervalo_s * n_muestras * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 5: Recuperación y procesamiento de los datos ==========
        # 9. Solicitar todas las muestras disponibles en el buffer
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
        
    
        # 10. Procesar los datos: vienen en el formato <freq1>,<ts1>,<freq2>,<ts2>,...
        try:
            valores = [float(val) for val in data.strip().split(',') if val]
            resultados = []
            # 11. Agrupar de dos en dos: (frecuencia, timestamp)
            for i in range(0, len(valores)-1, 2):
                frecuencia = valores[i]
                timestamp = valores[i+1]
                resultados.append((frecuencia, timestamp))
            # 12. Ajustar los timestamps para que sean relativos al primero (delta_t)
            if resultados:
                t0 = resultados[0][1]
                resultados = [(f, t - t0) for (f, t) in resultados]
        except Exception:
            # Si el formato recibido no es el esperado, devolver el texto crudo para depuración
            resultados = data
    
        # 12. Devolver la lista de tuplas (frecuencia, delta_t)
        return resultados
            
            















#PROBAMOS A EXTRAER SIMPLEMENTE EL ADEV
    def leer_adev_cnt91(self):
        """
        Extrae la Allan deviation (ADEV) calculada internamente por el CNT-91
        para la última adquisición realizada.
    
        Retorna:
            Allan_Deviation: float
                Allan deviation interna (o None si ocurre algún error)
        """
        # 1. Resetear el instrumento para asegurar estado limpio
        self.dev.write('*RST')
        # 2. Limpiar errores previos para evitar problemas durante la medición
        self.dev.write("*CLS")
        self.dev.write(':CALC:AVER:TYPE ADEV')
        self.dev.write(':CALC:DATA?')
        resp_adev = self.dev.read()
        print("Valor bruto de ADEV:", resp_adev)
    
        # Intenta extraer el segundo valor como ADEV
        try:
            valores = [float(val) for val in resp_adev.strip().split(',') if val]
            Allan_Deviation = valores[1] if len(valores) > 1 else None
        except Exception:
            Allan_Deviation = None
    
        return Allan_Deviation






    def obtener_estadisticas(self, tipo_estadistica='ALL'):
            """
            Obtiene las variables estadísticas calculadas por el CNT-91.
            
            Parámetros:
                tipo_estadistica (str): Tipo de estadística a obtener. Puede ser:
                    - 'ALL': Todas las estadísticas disponibles
                    - 'ADEV': Allan Deviation
                    - 'MEAN': Media
                    - 'STD': Desviación estándar
                    - 'MIN': Valor mínimo
                    - 'MAX': Valor máximo
                    - 'PKPK': Valor pico a pico
            
            Retorna:
                dict: Diccionario con las estadísticas solicitadas. Si tipo_estadistica es 'ALL',
                    devuelve todas las estadísticas disponibles. Si hay error, devuelve None.
            """
            # Diccionario de tipos de estadísticas y sus comandos SCPI
            tipos_estadistica = {
                'ADEV': ':CALC:AVER:TYPE ADEV',
                'MEAN': ':CALC:AVER:TYPE MEAN',
                'STD': ':CALC:AVER:TYPE SDEV',
                'MIN': ':CALC:AVER:TYPE MIN',
                'MAX': ':CALC:AVER:TYPE MAX',
                'PKPK': ':CALC:AVER:TYPE PKPK'
            }
            
            try:
                # Resetear y limpiar el instrumento
                self.dev.write('*RST')
                self.dev.write('*CLS')
                
                # Si se solicitan todas las estadísticas
                if tipo_estadistica.upper() == 'ALL':
                    resultados = {}
                    for tipo, comando in tipos_estadistica.items():
                        # Configurar el tipo de estadística
                        self.dev.write(comando)
                        # Solicitar los datos
                        self.dev.write(':CALC:DATA?')
                        resp = self.dev.read()
                        
                        # Procesar la respuesta
                        try:
                            valores = [float(val) for val in resp.strip().split(',') if val]
                            # El segundo valor es generalmente el que nos interesa
                            resultados[tipo] = valores[1] if len(valores) > 1 else None
                        except Exception as e:
                            print(f"Error procesando {tipo}: {str(e)}")
                            resultados[tipo] = None
                    
                    return resultados
                
                # Si se solicita una estadística específica
                elif tipo_estadistica.upper() in tipos_estadistica:
                    # Configurar el tipo de estadística
                    self.dev.write(tipos_estadistica[tipo_estadistica.upper()])
                    # Solicitar los datos
                    self.dev.write(':CALC:DATA?')
                    resp = self.dev.read()
                    
                    # Procesar la respuesta
                    try:
                        valores = [float(val) for val in resp.strip().split(',') if val]
                        return valores[1] if len(valores) > 1 else None
                    except Exception as e:
                        print(f"Error procesando {tipo_estadistica}: {str(e)}")
                        return None
                else:
                    print(f"Tipo de estadística no válido: {tipo_estadistica}")
                    print("Tipos válidos:", list(tipos_estadistica.keys()) + ['ALL'])
                    return None
                    
            except Exception as e:
                print(f"Error en la comunicación con el instrumento: {str(e)}")
                return None






    

#              measure_frequency

"""
# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de la función modificada ======

"""             
"""

try:
    resultado = objt_prueba.measure_frequency('A')
    print("Resultado de measure_frequency", resultado)
except Exception as e:
    print("Error al ejecutar measure_frequency", e)

"""





#             Measure_temperature_example

"""
# MIDE LA TEMPERATURA

    
    
"""

"""
try:
    temperatura = objt_prueba.Measure_temperature_example()
    print("Resultado de Measure_temperature_example", temperatura)
except Exception as t:
    print("Error al ejecutar Measure_temperature_example", t)

"""



#               measure_frequency_array_CONTINUOUS    

"""

# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)
 # ====== NUEVA SECCIÓN: Prueba de medida continua con try/except ======
try:
    if not resources:
        raise RuntimeError("No hay recursos VISA disponibles.")
    
    duration = 5.0  # Duración de la prueba en segundos
    print(f"\nIniciando medida continua durante {duration:.1f} s en canal A...")
    freqs = objt_prueba.measure_frequency_array_CONTINUOUS(duration_s=duration, channel='A')

    print(f"\nRecibidos {len(freqs)} valores:")
    for idx, f in enumerate(freqs, start=1):
        print(f"  #{idx}: {f:.6f} Hz")
    if not freqs:
        print("  ¡No se recibieron valores! Verifica la conexión y configuración.")

except Exception as e:
    print(f"Error durante la prueba de medida continua: {e}")
    
    
"""


#             medir_n_muestras_equidistantes     DELTA TIEMPOS y Tiempo de espera

"""

# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de la función modificada ======

# Parámetros de la prueba
n_muestras = 500
intervalo_s = 0.2

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición
resultados = objt_prueba.medir_n_muestras_equidistantes(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Ajustar los timestamps para restar el inicial
if resultados and isinstance(resultados[0], tuple) and len(resultados[0]) == 2:
    t0 = resultados[0][1]
    resultados_rel = [(f, t - t0) for (f, t) in resultados]
else:
    resultados_rel = resultados  # Si el formato es inesperado, dejar igual

print("Frecuencia (Hz), Delta t (s) respecto a la primera muestra:")
for freq, dt in resultados_rel:
    print(f"{freq:.6f}, {dt:.6f}")


"""




#             medir_n_muestras_equidistantes     DELTA TIEMPOS

"""
# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de la función modificada ======

resultados = objt_prueba.medir_n_muestras_equidistantes(n_muestras=20, intervalo_s=0.2)

# Ajustar los timestamps para restar el inicial
if resultados and isinstance(resultados[0], tuple) and len(resultados[0]) == 2:
    t0 = resultados[0][1]
    resultados_rel = [(f, t - t0) for (f, t) in resultados]
else:
    resultados_rel = resultados  # Si el formato es inesperado, dejar igual

print("Frecuencia (Hz), Delta t (s) respecto a la primera muestra:")
for freq, dt in resultados_rel:
    print(f"{freq:.6f}, {dt:.6f}")

"""



#             medir_n_muestras_equidistantes     TIEMPOS


"""
# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de ======



resultados = objt_prueba.medir_n_muestras_equidistantes(n_muestras=20, intervalo_s=0.2)
print(resultados)

"""



#             medir_n_muestras_equidistantes     ADEV interno

"""
# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de la función modificada ======

adev = objt_prueba.leer_adev_cnt91()
print("Allan deviation interna CNT-91:", adev)
    
   
"""






#PARA FINALIZAR LA CONEXIÓN CON EL DISPOSITIVO

"""
FINALIZAR LA COMUNICACIÓN CON EL DISPOSITIVO (FALTA)

"""

"""
try:
     objt_prueba.Reset_Device()
    
except Exception as t:
    print("Error al ejecutar Measure_temperature_example", t)
    
    
"""   


# PARA LOS ERRORES

"""

try:
    NumeroError = objt_prueba.System_Error_Number()
    print("Resultado de ERROR:", NumeroError)
except Exception as p:
    print("Error al ejecutar Measure_example:", p) 
"""   

    









#             obtener_estadisticas
"""
# Obtener todas las estadísticas
todas_estadisticas = cnt91.obtener_estadisticas('ALL')
# Resultado: {'ADEV': valor, 'MEAN': valor, 'STD': valor, ...}

# Obtener solo ADEV
adev = cnt91.obtener_estadisticas('ADEV')
# Resultado: valor numérico

# Obtener solo la media
media = cnt91.obtener_estadisticas('MEAN')
# Resultado: valor numérico
"""

    def medir_n_muestras_equidistantesV2(self, n_muestras=10, intervalo_s=0.1, canal='A'):
        """
        Versión 2.0 de la función de medición de muestras equidistantes.
        Realiza una adquisición de 'n_muestras' equidistantes en el tiempo usando el CNT-91,
        devolviendo tres arrays separados: frecuencias, timestamps y delta_tiempos.
    
        Parámetros:
            n_muestras: int
                Número de muestras a medir (por defecto 10)
            intervalo_s: float
                Intervalo de tiempo entre muestras en segundos (por defecto 0.1s)
            canal: str o int
                Canal de medida: 'A', 'B', 1 o 2 (por defecto 'A')
    
        Devuelve:
            tuple: (frecuencias, timestamps, delta_tiempos)
                - frecuencias: array de floats con las frecuencias medidas
                - timestamps: array de floats con los tiempos absolutos
                - delta_tiempos: array de floats con los tiempos relativos al primer valor
        """
    
        import time
        import numpy as np
    
        # ========== SECCIÓN 1: Validación y selección de canal ==========
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_cmd = canales[ch]
    
        # ========== SECCIÓN 2: Configuración mínima del instrumento ==========
        self.dev.write('*RST')
        self.dev.write("*CLS")
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
        self.dev.write(f'ARM:COUN {n_muestras}')
        self.dev.write('FORM:TINF ON')
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición ==========
        self.dev.write('INIT')
    
        # ========== SECCIÓN 4: Espera para completar la adquisición ==========
        tiempo_espera = intervalo_s * n_muestras * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 5: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
        
        try:
            # Convertir la respuesta en una lista de valores
            valores = [float(val) for val in data.strip().split(',') if val]
            
            # Separar frecuencias y timestamps
            frecuencias = valores[::2]  # Valores en posiciones pares
            timestamps = valores[1::2]  # Valores en posiciones impares
            
            # Convertir a arrays numpy
            frecuencias = np.array(frecuencias)
            timestamps = np.array(timestamps)
            
            # Calcular delta_tiempos (tiempos relativos al primer valor)
            delta_tiempos = timestamps - timestamps[0]
            
            return frecuencias, timestamps, delta_tiempos
            
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None