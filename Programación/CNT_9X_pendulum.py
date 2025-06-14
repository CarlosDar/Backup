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
            
 #JOAN 3 PROBAMOS OTRO METODO Usar el modo de medición con "Sample Timer"
 # 
 #   Está tiene tiempos y tiempos relativos         


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

#JOAN 3 PROBAMOS OTRO METODO Usar el modo de medición con "Sample Timer"
# 
#   Está tiene tiempos y tiempos relativos y GRAFICAR FREQUENCIA VS TIEMPO 


    def medir_n_muestras_equidistantesV3(self, n_muestras=10, intervalo_s=0.1, canal='A', graficarFT=True):
        """
        Versión 3.0: Igual que V2, pero permite graficar resultados de frecuencia vs tiempo.
    
        Parámetros:
            n_muestras: int
                Número de muestras a medir (por defecto 10)
            intervalo_s: float
                Intervalo de tiempo entre muestras en segundos (por defecto 0.1s)
            canal: str o int
                Canal de medida: 'A', 'B', 1 o 2 (por defecto 'A')
            graficar: bool
                Si True, muestra gráfica frecuencia vs tiempo (por defecto False)
    
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
        # Modelo combinado + margen del 10%, con casos especiales y tiempo mínimo de 0.2s
        eps = 1e-12
        T = intervalo_s
        N = n_muestras
        if abs(T - 4e-5) < eps and N == 2400:
            tiempo_espera = 0.25
        elif abs(T - 4e-4) < eps and N == 1000:
            tiempo_espera = 0.8
        else:
            raw = 2 * T**0.88 * N**0.85
            lin = 1.14 * T * N
            val = max(raw, lin)
            tiempo_espera = max(0.2, val) * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 5: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
    
        try:
            # Convertir la respuesta en una lista de valores
            valores = [float(val) for val in data.strip().split(',') if val]
    
            # Separar frecuencias y timestamps
            frecuencias = np.array(valores[::2])  # Valores en posiciones pares
            timestamps = np.array(valores[1::2])  # Valores en posiciones impares
    
            # Calcular delta_tiempos (tiempos relativos al primer valor)
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 6: Visualización de resultados ==========
            if graficarFT:
                import matplotlib.pyplot as plt
                from matplotlib.ticker import MaxNLocator
    
                # Estadísticas básicas
                maximo = np.max(frecuencias)
                minimo = np.min(frecuencias)
                media = np.mean(frecuencias)
                mediana = np.median(frecuencias)
                n_puntos = len(frecuencias)
    
                plt.figure(figsize=(9, 5))
                plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
                plt.xlabel('Tiempo [s]', fontsize=12)
                plt.ylabel('Frecuencia [Hz]', fontsize=12)
                plt.title('Frecuencia vs Tiempo')
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    
                # Mostrar estadísticas en la gráfica
                texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                               f"Mín: {minimo:.3f} Hz\n"
                               f"Media: {media:.3f} Hz\n"
                               f"Mediana: {mediana:.3f} Hz\n"
                               f"Nº puntos: {n_puntos}")
                plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                               ha='right', va='bottom', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
                plt.tight_layout()
                plt.show()
    
            return frecuencias, timestamps, delta_tiempos
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None   




#JOAN 3 PROBAMOS OTRO METODO Usar el modo de medición con "Sample Timer"
# 
#   Está tiene tiempos y tiempos relativos y GRAFICAR FREQUENCIA VS TIEMPO
# Añadido que devuelva los Allan deviation

    def medir_n_muestras_equidistantesV4(self, n_muestras=10, intervalo_s=0.1, canal='A', graficarFT=True):
        """
        Versión 4.0: Igual que V3, pero añade cálculo de Allan Deviation para diferentes Taus.
    
        Parámetros:
            n_muestras: int
                Número de muestras a medir (por defecto 10)
            intervalo_s: float
                Intervalo de tiempo entre muestras en segundos (por defecto 0.1s)
            canal: str o int
                Canal de medida: 'A', 'B', 1 o 2 (por defecto 'A')
            graficar: bool
                Si True, muestra gráfica frecuencia vs tiempo (por defecto False)
    
        Devuelve:
            tuple: (frecuencias, timestamps, delta_tiempos, allan_deviations, taus)
                - frecuencias: array de floats con las frecuencias medidas
                - timestamps: array de floats con los tiempos absolutos
                - delta_tiempos: array de floats con los tiempos relativos al primer valor
                - allan_deviations: array de floats con los valores de Allan deviation calculados
                - taus: array de floats con los valores de tau asociados a cada Allan deviation
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
            frecuencias = np.array(valores[::2])  # Valores en posiciones pares
            timestamps = np.array(valores[1::2])  # Valores en posiciones impares
    
            # Calcular delta_tiempos (tiempos relativos al primer valor)
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 5B: Cálculo de Allan Deviation para diferentes Taus ==========
            N = len(frecuencias)
            allan_deviations = []
            taus = []
    
            for m in range(1, N // 2 + 1):
                M = N // m
                if M < 2:
                    break
                # Promedios de frecuencia para cada bloque de tamaño m
                promedios = [np.mean(frecuencias[i * m:(i + 1) * m]) for i in range(M)]
                # Diferencias cuadráticas entre bloques consecutivos
                dif_cuadrado = [(promedios[i + 1] - promedios[i]) ** 2 for i in range(M - 1)]
                sigma2 = np.sum(dif_cuadrado) / (2 * (M - 1))
                sigma = np.sqrt(sigma2)
                allan_deviations.append(sigma)
                taus.append(m * intervalo_s)
    
            allan_deviations = np.array(allan_deviations)
            taus = np.array(taus)
    
            # ========== SECCIÓN 6: Visualización de resultados ==========
            if graficarFT:
                import matplotlib.pyplot as plt
                from matplotlib.ticker import MaxNLocator
    
                # Estadísticas básicas
                maximo = np.max(frecuencias)
                minimo = np.min(frecuencias)
                media = np.mean(frecuencias)
                mediana = np.median(frecuencias)
                n_puntos = len(frecuencias)
    
                plt.figure(figsize=(9, 5))
                plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
                plt.xlabel('Tiempo [s]', fontsize=12)
                plt.ylabel('Frecuencia [Hz]', fontsize=12)
                plt.title('Frecuencia vs Tiempo')
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    
                # Mostrar estadísticas en la gráfica
                texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                               f"Mín: {minimo:.3f} Hz\n"
                               f"Media: {media:.3f} Hz\n"
                               f"Mediana: {mediana:.3f} Hz\n"
                               f"Nº puntos: {n_puntos}")
                plt.gca().text(0.02, 0.98, texto_stats, fontsize=9,
                               ha='left', va='top', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.4, edgecolor='none'))
                plt.tight_layout()
                plt.show()
    
            return frecuencias, timestamps, delta_tiempos, allan_deviations, taus
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None, None, None
        
        









    




    def medir_n_muestras_equidistantesV31(self, n_muestras=100, intervalo_s=0.2, canal='A', graficarFT=False, exportar_excel=False):
        """
        Versión 3.1: Igual que V3, pero añade opción de guardar datos en Excel (.xlsx).
    
        Parámetros:
            n_muestras: int
                Número de muestras a medir (por defecto 100)
            intervalo_s: float
                Intervalo de tiempo entre muestras en segundos (por defecto 0.2s) EL VALOR MÍNIMO ES 
            canal: str o int
                Canal de medida: 'A', 'B', 1 o 2 (por defecto 'A')
            graficarFT: bool
                Si True, muestra gráfica frecuencia vs tiempo (por defecto True)
            exportar_excel: bool
                Si True, exporta los datos a un archivo Excel .xlsx (por defecto True)
    
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
        self.dev.write('CAL:INT:AUTO OFF')          # Desactiva autocalibración de interpoladores para máxima velocidad
        self.dev.write('DISP:ENAB OFF')             # Apaga display para máxima velocidad
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}') # 0.004s mín
        self.dev.write(f'ARM:COUN {n_muestras}')
        self.dev.write('FORM:TINF ON')
        
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición ==========
        self.dev.write('INIT')
    
     
        
        # ========== SECCIÓN 4: Espera para completar la adquisición ==========
        # Modelo combinado + margen del 10%, con casos especiales y tiempo mínimo de 0.2s
        eps = 1e-12
        T = intervalo_s
        N = n_muestras
        if abs(T - 4e-5) < eps and N == 2400:
            tiempo_espera = 0.25
        elif abs(T - 4e-4) < eps and N == 1000:
            tiempo_espera = 0.8
        else:
            raw = 2 * T**0.88 * N**0.85
            lin = 1.14 * T * N
            val = max(raw, lin)
            tiempo_espera = max(0.2, val) * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 5: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
    
        try:
            # Convertir la respuesta en una lista de valores
            valores = [float(val) for val in data.strip().split(',') if val]
    
            # Separar frecuencias y timestamps
            frecuencias = np.array(valores[::2])  # Valores en posiciones pares
            timestamps = np.array(valores[1::2])  # Valores en posiciones impares
    
            # Calcular delta_tiempos (tiempos relativos al primer valor)
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 6: Visualización de resultados ==========
            if graficarFT:
                import matplotlib.pyplot as plt
                from matplotlib.ticker import MaxNLocator
    
                maximo = np.max(frecuencias)
                minimo = np.min(frecuencias)
                media = np.mean(frecuencias)
                mediana = np.median(frecuencias)
                n_puntos = len(frecuencias)
    
                plt.figure(figsize=(9, 5))
                plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
                plt.xlabel('Tiempo [s]', fontsize=12)
                plt.ylabel('Frecuencia [Hz]', fontsize=12)
                plt.title('Frecuencia vs Tiempo')
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    
                texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                               f"Mín: {minimo:.3f} Hz\n"
                               f"Media: {media:.3f} Hz\n"
                               f"Mediana: {mediana:.3f} Hz\n"
                               f"Nº puntos: {n_puntos}")
                plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                               ha='right', va='bottom', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
                plt.tight_layout()
                plt.show()
            
            # ========== SECCIÓN NUEVA: Guardar en Excel (.xlsx) ==========
            if exportar_excel:
                import pandas as pd
                from datetime import datetime
    
                fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
                raw_data = {
                    "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                    "Frecuencia [Hz]": np.round(frecuencias, 6),   # Numérico, 6 decimales
                    "Timestamp [s]": np.round(timestamps, 2),
                    "Delta_tiempo [s]": np.round(delta_tiempos, 2)
                }
                df_raw = pd.DataFrame(raw_data)
                nombre_raw = f"RawDataFreqYTiempo_{fecha_hora}.xlsx"
                df_raw.to_excel(nombre_raw, index=False, float_format="%.6f")  # <- Guardado en xlsx
                print(f"Archivo de datos crudos guardado como: {nombre_raw}")
                self.dev.write('DISP:ENAB ON')             # Apaga display para máxima velocidad
            return frecuencias, timestamps, delta_tiempos
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None

    


# Version v6 pero con capacidad para configurar la medida

    def medir_n_muestras_equidistantesV7(
            self,
            n_muestras=100,
            intervalo_s=0.2,  # 4ms = 0.004s de mín recomendable ,  20 ns a 1000 s.
            canal='A',
            graficarFT=True,
            graficarDevTau=True,
            exportar_excel=True,
            configurar=False,
            impedancia=None,      # '50' (ohmios) o '1M' (megaohm)
            acoplamiento=None,    # 'DC', 'AC', 'HF', 'LF'
            atenuacion=None,      # '0' (0dB, por defecto) o '10' (10dB típico para señales grandes) 
            filtro=None,          # 'ON', 'OFF'
            triger_level=None,    # valor en voltios, e.g., 0.5
            triger_slope=None     # 'POS' (subida), 'NEG' (bajada)
        ):
        """
        Versión clásica y robusta con espera por time.sleep().
        Permite configurar impedancia, acoplamiento, atenuación, filtro, trigger level y trigger slope.
        """
        import time
        import numpy as np
    
        # ========== SECCIÓN 1: Validación y selección de canal ==========
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_cmd = canales[ch]
        canal_num = '1' if ch in ['A', '1'] else '2'   # para los comandos INP1, INP2, etc.
    
        # ========== SECCIÓN 2: Configuración del instrumento ==========
        self.dev.write('*RST')
        self.dev.write("*CLS")
    
        # ======= SECCIÓN 2.1: Configuración extra por usuario =======
        if configurar:
            if impedancia in ['50', '1M']:
                self.dev.write(f'INP{canal_num}:IMP {impedancia}')  # Ej: INP1:IMP 50
            if acoplamiento in ['DC', 'AC', 'HF', 'LF']:
                self.dev.write(f'INP{canal_num}:COUP {acoplamiento}')  # Ej: INP1:COUP AC
            if atenuacion in ['0', '10']:
                self.dev.write(f'INP{canal_num}:ATT {atenuacion}')  # Ej: INP1:ATT 10
            if filtro in ['ON', 'OFF']:
                self.dev.write(f'INP{canal_num}:FILT {filtro}')     # Ej: INP1:FILT ON
            if triger_level is not None:
                self.dev.write(f'TRIG{canal_num}:LEV {triger_level}')  # Ej: TRIG1:LEV 0.5
            if triger_slope in ['POS', 'NEG']:
                self.dev.write(f'TRIG{canal_num}:SLOP {triger_slope}') # Ej: TRIG1:SLOP POS
    
        self.dev.write('CAL:INT:AUTO OFF')
        self.dev.write('DISP:ENAB OFF')
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
        self.dev.write(f'ARM:COUN {n_muestras}')
        self.dev.write('FORM:TINF ON')
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición y espera clásica ==========
        self.dev.write('INIT')
        # Modelo combinado + margen del 10%, con casos especiales y tiempo mínimo de 0.2s
        eps = 1e-12
        T = intervalo_s
        N = n_muestras
        if abs(T - 4e-5) < eps and N == 2400:
            tiempo_espera = 0.25
        elif abs(T - 4e-4) < eps and N == 1000:
            tiempo_espera = 0.8
        else:
            raw = 2 * T**0.88 * N**0.85
            lin = 1.14 * T * N
            val = max(raw, lin)
            tiempo_espera = max(0.2, val) * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 4: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
        valores = [float(val) for val in data.strip().split(',') if val]
        if len(valores) < 2 * n_muestras:
            print(f"¡Advertencia! Recibidas menos muestras ({len(valores)//2}) de las solicitadas ({n_muestras}).")
    
        try:
            frecuencias = np.array(valores[::2])
            timestamps = np.array(valores[1::2])
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 5: Cálculo de Allan Deviation ==========
            N = len(frecuencias)
            allan_deviations = []
            taus = []
            for m in range(1, N // 2 + 1):
                M = N // m
                if M < 2:
                    break
                promedios = [np.mean(frecuencias[i * m:(i + 1) * m]) for i in range(M)]
                dif_cuadrado = [(promedios[i + 1] - promedios[i]) ** 2 for i in range(M - 1)]
                sigma2 = np.sum(dif_cuadrado) / (2 * (M - 1))
                sigma = np.sqrt(sigma2)
                allan_deviations.append(sigma)
                taus.append(m * intervalo_s)
            allan_deviations = np.array(allan_deviations)
            taus = np.array(taus)
    
            # ========== SECCIÓN 6: Exportar a Excel (.xlsx, dos hojas) ==========
            if exportar_excel:
                import pandas as pd
                from datetime import datetime
    
                now = datetime.now()
                nombre_excel = (
                    f"AllanDeviation_vs_Tau_and_Freq_vs_timestamp___"
                    f"{now:%S}sec_{now:%M}min_{now:%H}hour_{now:%Y}year.xlsx"
                )
    
                raw_data = {
                    "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                    "Frecuencia [Hz]": np.round(frecuencias, 6),
                    "Timestamp [s]": np.round(timestamps, 6),
                    "Delta_tiempo [s]": np.round(delta_tiempos, 6)
                }
                df_raw = pd.DataFrame(raw_data)
                allan_data = {
                    "DATO": [f"DATO{i}" for i in range(len(allan_deviations))],
                    "AllanDeviation [Hz]": np.round(allan_deviations, 6),
                    "Tau [s]": np.round(taus, 6)
                }
                df_allan = pd.DataFrame(allan_data)
                with pd.ExcelWriter(nombre_excel) as writer:
                    df_raw.to_excel(writer, sheet_name='Datos Frecuencia', index=False, float_format="%.6f")
                    df_allan.to_excel(writer, sheet_name='Allan Deviation', index=False, float_format="%.6f")
                print(f"Archivo de datos guardado como: {nombre_excel}")
    
            # ========== SECCIÓN 7: Visualización de resultados (Frecuencia vs Tiempo) ==========
            if graficarFT:
                import matplotlib.pyplot as plt
                from matplotlib.ticker import MaxNLocator
    
                plt.figure(figsize=(10, 5))
                n_puntos = len(frecuencias)
                plt.scatter(delta_tiempos, frecuencias, s=6, alpha=0.7, label='Frecuencia')
                plt.xlabel('Tiempo [s]', fontsize=13)
                plt.ylabel('Frecuencia [Hz]', fontsize=13)
                plt.title('Frecuencia vs Tiempo', fontsize=15)
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
                maximo = np.max(frecuencias)
                minimo = np.min(frecuencias)
                media = np.mean(frecuencias)
                mediana = np.median(frecuencias)
                texto_stats = (f"Máx: {maximo:.2f} Hz\n"
                               f"Mín: {minimo:.2f} Hz\n"
                               f"Media: {media:.2f} Hz\n"
                               f"Mediana: {mediana:.2f} Hz\n"
                               f"Nº puntos: {n_puntos}")
                plt.gca().text(0.02, 0.98, texto_stats, fontsize=10,
                               ha='left', va='top', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.3, edgecolor='none'))
                plt.tight_layout()
                plt.show()
    
            # ========== SECCIÓN 8: Visualización de resultados (Allan Deviation vs Tau) ==========
            if graficarDevTau:
                import matplotlib.pyplot as plt
    
                plt.figure(figsize=(10, 5))
                plt.scatter(taus, allan_deviations, s=18, color='C0', alpha=0.8, label='Adev')
                plt.xscale('log')
                plt.yscale('log')
                plt.xlabel(r'$\tau$ [s]', fontsize=13)
                plt.ylabel('Allan Deviation [Hz]', fontsize=13)
                plt.title('Allan Deviation vs Tau', fontsize=15)
                plt.grid(True, which='both', linestyle='--', alpha=0.45)
    
                idx_min = np.argmin(allan_deviations)
                tau_min = taus[idx_min]
                adev_min = allan_deviations[idx_min]
                plt.scatter([tau_min], [adev_min], color='red', s=70, label=f'Mín Adev\nTau={tau_min:.2f}s\nAdev={adev_min:.2f}Hz', zorder=5)
                plt.legend(fontsize=10)
                plt.annotate(f'Mín:\nTau={tau_min:.2f}s\nAdev={adev_min:.2f}Hz',
                             xy=(tau_min, adev_min), xytext=(0.05, 0.98),
                             textcoords='axes fraction', ha='left', va='top',
                             fontsize=10, color='red',
                             bbox=dict(facecolor='white', alpha=0.45, edgecolor='red'))
                plt.tight_layout()
                plt.show()
    
            self.dev.write('DISP:ENAB ON')  # Reactiva display al acabar
    
            return frecuencias, timestamps, delta_tiempos, allan_deviations, taus
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None, None, None
    
    







# Probar a verr si va mejor que block measurament


    def continuous_measurament_v31(self, n_muestras=100, intervalo_s=0.2, canal='A', graficarFT=True, exportar_excel=True):
        """
        Medición continua: inicia la medición en modo continuo, espera el tiempo necesario,
        hace un ABORT, luego recupera exactamente n_muestras.
        Exporta a Excel (.xlsx) y puede graficar si se desea.
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
        self.dev.write('CAL:INT:AUTO OFF')  # PUEDE HACER QUE PIERDAS RESOLUCION Y PRECISION
        self.dev.write('DISP:ENAB OFF')
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')  # Tiempo de apertura por muestra
        self.dev.write("ARM:COUNT INF")
        self.dev.write('ARM:CONT ON')  # ARM Continuous mode ON (medición continua)
        self.dev.write('FORM:TINF ON')  # Formato con timestamps
    
        # ========== SECCIÓN 3: Lanzamiento de medición continua ==========
        self.dev.write('INIT')
        # Espera suficiente para recoger todas las muestras + margen
        # Modelo combinado + margen del 10%, con casos especiales y tiempo mínimo de 0.2s
        eps = 1e-12
        T = intervalo_s
        N = n_muestras
        if abs(T - 4e-5) < eps and N == 2400:
            tiempo_espera = 0.25
        elif abs(T - 4e-4) < eps and N == 1000:
            tiempo_espera = 0.8
        else:
            raw = 2 * T**0.88 * N**0.85
            lin = 1.14 * T * N
            val = max(raw, lin)
            tiempo_espera = max(0.2, val) * 1.1
        time.sleep(tiempo_espera)
        
        
        
        
        
    
        # ========== SECCIÓN 4: Abortamos y recuperamos muestras ==========
        self.dev.write('ABOR')  # Aborta la medición continua
        self.dev.write(f'FETC:ARR? {n_muestras}')  # Recupera sólo n_muestras
    
        data = self.dev.read()
    
        try:
            # Convertir la respuesta en una lista de valores
            valores = [float(val) for val in data.strip().split(',') if val]
    
            if len(valores) < 2 * n_muestras:
                print(f"¡Advertencia! Recibidas menos muestras ({len(valores)//2}) de las solicitadas ({n_muestras}).")
    
            # Separar frecuencias y timestamps
            frecuencias = np.array(valores[::2])  # Valores en posiciones pares
            timestamps = np.array(valores[1::2])  # Valores en posiciones impares
    
            # Calcular delta_tiempos (tiempos relativos al primer valor)
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 5: Visualización de resultados ==========
            if graficarFT:
                import matplotlib.pyplot as plt
                from matplotlib.ticker import MaxNLocator
    
                maximo = np.max(frecuencias)
                minimo = np.min(frecuencias)
                media = np.mean(frecuencias)
                mediana = np.median(frecuencias)
                n_puntos = len(frecuencias)
    
                plt.figure(figsize=(9, 5))
                plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
                plt.xlabel('Tiempo [s]', fontsize=12)
                plt.ylabel('Frecuencia [Hz]', fontsize=12)
                plt.title('Frecuencia vs Tiempo')
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    
                texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                               f"Mín: {minimo:.3f} Hz\n"
                               f"Media: {media:.3f} Hz\n"
                               f"Mediana: {mediana:.3f} Hz\n"
                               f"Nº puntos: {n_puntos}")
                plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                               ha='right', va='bottom', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
                plt.tight_layout()
                plt.show()
    
            # ========== SECCIÓN 6: Guardar en Excel (.xlsx) ==========
            if exportar_excel:
                import pandas as pd
                from datetime import datetime
    
                fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
                raw_data = {
                    "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                    "Frecuencia [Hz]": np.round(frecuencias, 6),
                    "Timestamp [s]": np.round(timestamps, 2),
                    "Delta_tiempo [s]": np.round(delta_tiempos, 2)
                }
                df_raw = pd.DataFrame(raw_data)
                nombre_raw = f"RawDataFreqYTiempo_CONT_{fecha_hora}.xlsx"
                df_raw.to_excel(nombre_raw, index=False, float_format="%.6f")
                print(f"Archivo de datos crudos guardado como: {nombre_raw}")
    
            self.dev.write('DISP:ENAB ON')  # Reactiva display al acabar
    
            return frecuencias, timestamps, delta_tiempos
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None
    
    
    
    
### LEER EL ADEV ESTADISTICO
        
    def leer_adev_cnt91(self,):
        """
        Extrae la Allan deviation (ADEV) calculada internamente por el CNT-91
        para la última adquisición realizada.
    
        Retorna:
            Allan_Deviation: float
                Allan deviation interna (o None si ocurre algún error)
        """
        try:
            # 1. Resetear el instrumento para asegurar estado limpio
            self.dev.write('*RST')
            # 2. Limpiar errores previos para evitar problemas durante la medición
            self.dev.write("*CLS")
            
            
            
            #self.dev.write(f':TRIG:TIM {pacing_time}ms') 
            #self.dev.write(f'SENS:ACQ:APER {intervalo_s}')  # Tiempo de apertura por muestra
           
                
                
            # 3. Configurar y activar el cálculo estadístico
            self.dev.write(':CALC:AVER:STAT ON')
            self.dev.write(':CALC:AVER:TYPE ADEV')
            
            # 4. Iniciar la medición y esperar a que complete
            self.dev.write(':INIT')
            self.dev.write('*OPC?')
            self.dev.read()  # Esperar a que complete
            
            # 5. Obtener los datos calculados
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            print("Valor bruto de ADEV:", resp_adev)
        
            # 6. Procesar la respuesta
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                Allan_Deviation = valores[0] if len(valores) >= 1 else None
            except Exception:
                Allan_Deviation = None
            
            # 7. Desactivar el cálculo estadístico al terminar
            self.dev.write(':CALC:AVER:STAT OFF')
        
            return Allan_Deviation
            
        except Exception as e:
            print(f"Error al leer ADEV: {str(e)}")
            return None 
        
        
        
    

    
    
    def calcular_adev_y_estadisticas(self, canal='A',N_muestras = 100, intervalo_captura=0.2, pacing_time=0.2, acoplamiento='AC', impedancia='MIN', atenuacion=0, trigger_level=0.5, trigger_slope='POS', filtro=100E3):
        
        import time
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            # ========== SECCIÓN 2: Resetear y limpiar instrumento ==========
            self.dev.write('*RST')
            self.dev.write('*CLS')
            # ========== SECCIÓN 3: Configuración del CNT_91  ACOPLAMIENTO, IMPEDANCIA, ATENUACIÓN, TRIGGER LEVEL, TRIGGER SLOPE==========

            self.dev.write(f':INP{canal_cmd}:COUP {acoplamiento}') # Default value: AC  , Posible valores: AC or DC or None
            self.dev.write(f':INP{canal_cmd}:IMP {impedancia}') # Default value: 50 Ohm , Posible valores: between[50 Ohm  1M Ohm] or MAX or MIN  
            self.dev.write(f':INP{canal_cmd}:ATT {atenuacion}') # Default value: 0 dB , Posible valores: between[0x to 10x] or MAX or MIN , <Numeric values> <= 5, and MIN gives attenuation 1 , <Numeric values> > 5, and MAX gives attenuation 10. 
            self.dev.write(f':INP{canal_cmd}:TRL {trigger_level}') # Default value: 0.5 V , Posible valores: between[0.1 V to 10 V] or MAX or MIN 
            self.dev.write(f':INP{canal_cmd}:TRS {trigger_slope}') # Default value: POS   , Posible valores: POS or NEG
            self.dev.write(f':INP{canal_cmd}:FIL:DIG:FREQ {filtro}') # Default value: 100xE3 Hz   , Posible valores: between[1 to 50xE6 Hz] or MAX or MIN 

            # ========== SECCIÓN 4: Configuración de canal  ==========  
            self.dev.write(f':CONF:FREQ {canal_cmd}')
            self.dev.write(f'SENS:ACQ:APER  {intervalo_captura}')  # Tiempo de apertura por muestra default: 0.2 s
            
            # ========== SECCIÓN 5: Configuración y activación de estadística ADEV ==========
            self.dev.write(':CALC:AVER:STAT ON')
            self.dev.write(':CALC:TYPE ADEV')
            self.dev.write(f':ARM:START:COUN N_muestras')  # Número de muestras default: 100
            
            if pacing_time is not None:
                self.dev.write(f'TRIGger:SOURce TIMer') # Default value: TIMer
                self.dev.write(f':TRIG:TIM {pacing_time}') # Tiempo entre muestras default: 0.2 s
            
            
            # ========== SECCIÓN 6: Iniciar medición ==========
            self.dev.write(':INIT')
            
            ### Esperamos a que la medición termine
            current = 0
            while float(current) != N_muestras:
                self.dev.write(':CALCulate:AVERage:COUNt:CURRent?')
                current = self.dev.read()
            
            
            # ========== SECCIÓN 7: Lectura de Allan deviation ==========
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                allan_deviation = valores[0] if len(valores) >= 1 else None
            except Exception:
                allan_deviation = None
            
            # ========== SECCIÓN 8: Lectura de estadísticas de media ==========
            self.dev.write(':CALC:AVER:ALL?')
            resp_estadisticas = self.dev.read()
            try:
                valores = [float(val.strip()) for val in resp_estadisticas.strip().split(',') if val.strip()]
                valor_medio       = valores[0] if len(valores) > 0 else None
                desviacion_tipica = valores[1] if len(valores) > 1 else None
                valor_minimo      = valores[2] if len(valores) > 2 else None
                valor_maximo      = valores[3] if len(valores) > 3 else None
            except Exception:
                valor_medio       = None
                desviacion_tipica = None
                valor_minimo      = None
                valor_maximo      = None
                
                
            
            self.dev.write(':CALC:AVER:STAT OFF') ## QUITAR ESTA INSTRUCCIÓN SI TE INTERESA QUE SIGA MIDIENDO
            
            # ========== SECCIÓN 9: Devolver resultados ==========
            return allan_deviation, valor_medio, desviacion_tipica, valor_minimo, valor_maximo
    
        except Exception as e:
            print(f"Error al calcular ADEV y media: {str(e)}")
            return None, None, None, None, None
    
    


#### LA MISMA FUNCION QUE LA ANTERIOR PERO YA NO CALCULAMOS MAXIMOS Y MINIMOS, VAMOS DIRECTOS A LO QUE QUEREMOS
#### MIRAR TFG PARA DEFINIR CON INT MAX Y INT MIN  y numero de pasos un bloque de medidas allan y que luego lo 
#### guarde con su tau especifica de paso.
    def calcular_adev_y_estadisticas(self, canal='A',N_muestras = 100, intervalo_captura=0.2, pacing_time=0.2, acoplamiento='AC', impedancia='MIN', atenuacion=0, trigger_level=0.5, trigger_slope='POS', filtro=100E3):
        
        import time
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            # ========== SECCIÓN 2: Resetear y limpiar instrumento ==========
            self.dev.write('*RST')
            self.dev.write('*CLS')
            # ========== SECCIÓN 3: Configuración del CNT_91  ACOPLAMIENTO, IMPEDANCIA, ATENUACIÓN, TRIGGER LEVEL, TRIGGER SLOPE==========

            self.dev.write(f':INP{canal_cmd}:COUP {acoplamiento}') # Default value: AC  , Posible valores: AC or DC or None
            self.dev.write(f':INP{canal_cmd}:IMP {impedancia}') # Default value: 50 Ohm , Posible valores: between[50 Ohm  1M Ohm] or MAX or MIN  
            self.dev.write(f':INP{canal_cmd}:ATT {atenuacion}') # Default value: 0 dB , Posible valores: between[0x to 10x] or MAX or MIN , <Numeric values> <= 5, and MIN gives attenuation 1 , <Numeric values> > 5, and MAX gives attenuation 10. 
            self.dev.write(f':INP{canal_cmd}:TRL {trigger_level}') # Default value: 0.5 V , Posible valores: between[0.1 V to 10 V] or MAX or MIN 
            self.dev.write(f':INP{canal_cmd}:TRS {trigger_slope}') # Default value: POS   , Posible valores: POS or NEG
            self.dev.write(f':INP{canal_cmd}:FIL:DIG:FREQ {filtro}') # Default value: 100xE3 Hz   , Posible valores: between[1 to 50xE6 Hz] or MAX or MIN 

            # ========== SECCIÓN 4: Configuración de canal  ==========  
            self.dev.write(f':CONF:FREQ {canal_cmd}')
            self.dev.write(f'SENS:ACQ:APER  {intervalo_captura}')  # Tiempo de apertura por muestra default: 0.2 s , posible valores: entre [ _____________ s]
            
            # ========== SECCIÓN 5: Configuración y activación de estadística ADEV ==========
            self.dev.write(':CALC:AVER:STAT ON')
            self.dev.write(':CALC:TYPE ADEV')
            self.dev.write(f':ARM:START:COUN N_muestras')  # Número de muestras default: 100 , posible valores: entre [1 to 1000000]
            
            if pacing_time is not None:
                self.dev.write(f'TRIGger:SOURce TIMer')
                self.dev.write(f':TRIG:TIM {pacing_time}') # Tiempo entre muestras , default: 0.2 s , posible valores: entre [____________ s]
            
            
            # ========== SECCIÓN 5: Iniciar medición ==========
            self.dev.write(':INIT')
            
            ### Esperamos a que la medición termine
            current = 0
            while float(current) != N_muestras:
                self.dev.write(':CALCulate:AVERage:COUNt:CURRent?')
                current = self.dev.read()
            
            
            # ========== SECCIÓN 6: Lectura de Allan deviation ==========
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                allan_deviation = valores[0] if len(valores) >= 1 else None
            except Exception:
                allan_deviation = None
       
            
            self.dev.write(':CALC:AVER:STAT OFF') ## QUITAR ESTA INSTRUCCIÓN SI TE INTERESA QUE SIGA MIDIENDO
            
            # ========== SECCIÓN 8: Devolver resultados ==========
            return allan_deviation
    
        except Exception as e:
            print(f"Error al calcular ADEV y media: {str(e)}")
            return None





    def calcular_adev_y_estadisticas_BLOCK(
        self,
        canal='A',
        N_muestras=100,
        intervalo_captura_min=0.2,
        intervalo_captura_max=2.0,
        pasos=3,
        pacing_time=0.2,
        acoplamiento='AC',
        impedancia='MIN',
        atenuacion=0,
        trigger_level=0.5,
        trigger_slope='POS',
        filtro=100E3
    ):
        """
        Calcula la Allan deviation (ADEV) para varios intervalos de captura (SENS:ACQ:APER) en bloque.
        Devuelve arrays de ADEV y su respectivo intervalo de captura, según el número de pasos especificado.

        Parámetros:
            canal: 'A', 'B', 1 o 2
            N_muestras: número de muestras por cada medición
            intervalo_captura_min: intervalo de captura mínimo (SENS:ACQ:APER)
            intervalo_captura_max: intervalo de captura máximo (SENS:ACQ:APER)
            pasos: número de veces que se calculará el ADEV (mínimo 2)
            pacing_time: pacing time fijo (TRIG:TIM)
            acoplamiento, impedancia, atenuacion, trigger_level, trigger_slope, filtro: configuración del canal

        Devuelve:
            lista_intervalos: lista de intervalos de captura usados
            lista_adev: lista de valores de ADEV correspondientes
        """
        import numpy as np
        import time

        # Validación de pasos
        if pasos < 2:
            raise ValueError("El número de pasos debe ser al menos 2.")

        # Generar los intervalos de captura (espaciado lineal)
        lista_intervalos = np.linspace(intervalo_captura_min, intervalo_captura_max, pasos)
        lista_adev = []

        for intervalo_captura in lista_intervalos:
            try:
                # ========== SECCIÓN 1: Validación y selección de canal ==========
                canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
                ch = str(canal).upper()
                if ch not in canales:
                    raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
                canal_cmd = canales[ch]

                # ========== SECCIÓN 2: Resetear y limpiar instrumento ==========
                self.dev.write('*RST')
                self.dev.write('*CLS')

                # ========== SECCIÓN 3: Configuración del canal ==========
                self.dev.write(f':INP{canal_cmd}:COUP {acoplamiento}')
                self.dev.write(f':INP{canal_cmd}:IMP {impedancia}')
                self.dev.write(f':INP{canal_cmd}:ATT {atenuacion}')
                self.dev.write(f':INP{canal_cmd}:TRL {trigger_level}')
                self.dev.write(f':INP{canal_cmd}:TRS {trigger_slope}')
                self.dev.write(f':INP{canal_cmd}:FIL:DIG:FREQ {filtro}')

                # ========== SECCIÓN 4: Configuración de canal y estadística ==========
                self.dev.write(f':CONF:FREQ {canal_cmd}')
                self.dev.write(f'SENS:ACQ:APER {intervalo_captura}')  # <--- Este es el que se barre
                self.dev.write(':CALC:AVER:STAT ON')
                self.dev.write(':CALC:TYPE ADEV')
                self.dev.write(f':ARM:START:COUN {N_muestras}')

                self.dev.write('TRIGger:SOURce TIMer')
                self.dev.write(f':TRIG:TIM {pacing_time}')  # <--- Este es fijo

                # ========== SECCIÓN 5: Iniciar medición ==========
                self.dev.write(':INIT')

                # Esperar a que la medición termine
                current = 0
                while float(current) != N_muestras:
                    self.dev.write(':CALCulate:AVERage:COUNt:CURRent?')
                    current = self.dev.read()

                # ========== SECCIÓN 6: Lectura de Allan deviation ==========
                self.dev.write(':CALC:DATA?')
                resp_adev = self.dev.read()
                try:
                    valores = [float(val) for val in resp_adev.strip().split(',') if val]
                    allan_deviation = valores[0] if len(valores) >= 1 else None
                except Exception:
                    allan_deviation = None

                self.dev.write(':CALC:AVER:STAT OFF')

                lista_adev.append(allan_deviation)

            except Exception as e:
                print(f"Error al calcular ADEV para intervalo_captura={intervalo_captura}: {str(e)}")
                lista_adev.append(None)

        return lista_intervalos, lista_adev


    def calcular_adev_y_estadisticas_BLOCK2(
        self,
        canal='A',
        N_muestras=100,
        intervalo_captura_min=0.2,
        intervalo_captura_max=2.0,
        pasos=3,
        pacing_time=0.2,
        acoplamiento='AC',
        impedancia='MIN',
        atenuacion=0,
        trigger_level=0.5,
        trigger_slope='POS',
        filtro=100E3,
        ruta_csv=None,
        graficar=False,
        frecuencia_nominal=None
    ):
        """
        Calcula la Allan deviation (ADEV) para varios intervalos de captura (SENS:ACQ:APER) en bloque.
        Permite guardar los resultados en un CSV y graficar ADEV vs Tau.

        Parámetros:
            canal: 'A', 'B', 1 o 2
            N_muestras: número de muestras por cada medición
            intervalo_captura_min: intervalo de captura mínimo (SENS:ACQ:APER)
            intervalo_captura_max: intervalo de captura máximo (SENS:ACQ:APER)
            pasos: número de veces que se calculará el ADEV (mínimo 2)
            pacing_time: pacing time fijo (TRIG:TIM)
            acoplamiento, impedancia, atenuacion, trigger_level, trigger_slope, filtro: configuración del canal
            ruta_csv: ruta donde guardar el CSV (por defecto None, no guarda)
            graficar: si True, muestra la gráfica de ADEV vs Tau (por defecto False)
            frecuencia_nominal: valor de la frecuencia para el título de la gráfica (opcional)

        Devuelve:
            lista_intervalos: lista de intervalos de captura usados (Tau)
            lista_adev: lista de valores de ADEV correspondientes
        """
        import numpy as np
        import time

        # Validación de pasos
        if pasos < 2:
            raise ValueError("El número de pasos debe ser al menos 2.")

        # Generar los intervalos de captura (espaciado lineal)
        lista_intervalos = np.linspace(intervalo_captura_min, intervalo_captura_max, pasos)
        lista_adev = []

        for intervalo_captura in lista_intervalos:
            try:
                # ========== SECCIÓN 1: Validación y selección de canal ==========
                canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
                ch = str(canal).upper()
                if ch not in canales:
                    raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
                canal_cmd = canales[ch]

                # ========== SECCIÓN 2: Resetear y limpiar instrumento ==========
                self.dev.write('*RST')
                self.dev.write('*CLS')

                # ========== SECCIÓN 3: Configuración del canal ==========
                self.dev.write(f':INP{canal_cmd}:COUP {acoplamiento}')
                self.dev.write(f':INP{canal_cmd}:IMP {impedancia}')
                self.dev.write(f':INP{canal_cmd}:ATT {atenuacion}')
                self.dev.write(f':INP{canal_cmd}:TRL {trigger_level}')
                self.dev.write(f':INP{canal_cmd}:TRS {trigger_slope}')
                self.dev.write(f':INP{canal_cmd}:FIL:DIG:FREQ {filtro}')

                # ========== SECCIÓN 4: Configuración de canal y estadística ==========
                self.dev.write(f':CONF:FREQ {canal_cmd}')
                self.dev.write(f'SENS:ACQ:APER {intervalo_captura}')  # <--- Este es el que se barre
                self.dev.write(':CALC:AVER:STAT ON')
                self.dev.write(':CALC:TYPE ADEV')
                self.dev.write(f':ARM:START:COUN {N_muestras}')

                self.dev.write('TRIGger:SOURce TIMer')
                self.dev.write(f':TRIG:TIM {pacing_time}')  # <--- Este es fijo

                # ========== SECCIÓN 5: Iniciar medición ==========
                self.dev.write(':INIT')

                # Esperar a que la medición termine
                current = 0
                while float(current) != N_muestras:
                    self.dev.write(':CALCulate:AVERage:COUNt:CURRent?')
                    current = self.dev.read()

                # ========== SECCIÓN 6: Lectura de Allan deviation ==========
                self.dev.write(':CALC:DATA?')
                resp_adev = self.dev.read()
                try:
                    valores = [float(val) for val in resp_adev.strip().split(',') if val]
                    allan_deviation = valores[0] if len(valores) >= 1 else None
                except Exception:
                    allan_deviation = None

                self.dev.write(':CALC:AVER:STAT OFF')

                lista_adev.append(allan_deviation)

            except Exception as e:
                print(f"Error al calcular ADEV para intervalo_captura={intervalo_captura}: {str(e)}")
                lista_adev.append(None)

        # Guardar CSV si se solicita
        if ruta_csv is not None:
            try:
                import pandas as pd
                df = pd.DataFrame({
                    'Tau (s)': lista_intervalos,
                    'ADEV (Hz)': lista_adev
                })
                df.to_csv(ruta_csv, index=False)
                print(f"Resultados guardados en {ruta_csv}")
            except Exception as e:
                print(f"Error al guardar el CSV: {e}")

        # Graficar si se solicita
        if graficar:
            try:
                import matplotlib.pyplot as plt
                plt.figure(figsize=(8, 5))
                plt.plot(lista_intervalos, lista_adev, marker='o', linestyle='-', color='C0')
                plt.xlabel('Tau (s)', fontsize=12)
                plt.ylabel('ADEV (Hz)', fontsize=12)
                titulo = "ADEV (Hz) vs Tau (s)"
                if frecuencia_nominal is not None:
                    titulo += f" para frecuencia ≈ {frecuencia_nominal} Hz"
                plt.title(titulo, fontsize=14)
                plt.grid(True, which='both', linestyle='--', alpha=0.5)
                plt.xscale('log')
                plt.yscale('log')
                plt.tight_layout()
                plt.show()
            except Exception as e:
                print(f"Error al graficar: {e}")

        return lista_intervalos, lista_adev



# probar primero esta  overlapping
    def medir_n_muestras_equidistantesV31_BTBack(
        self,
        n_muestras=100,
        canal='A',
        intervalo_captura=0.2,
        graficarFT=False,
        exportar_excel=False
    ):
        """
        Adquisición rápida de un array de frecuencias y sus timestamps usando los comandos:
        - :MEASure:ARRay:FREQuency:BTBack? N,canal
        - :MEASure:ARRay:TSTAmp? N,canal

        Permite especificar el tiempo de integración (apertura) para cada medición.

        Parámetros de entrada:
        ----------------------
        n_muestras : int
            Número de muestras a adquirir (default: 100)
        canal : str o int
            Canal de medida: 'A', 'B', 1 o 2 (default: 'A')
        intervalo_captura : float o None
            Tiempo de integración (apertura) en segundos para cada muestra.
            - Mínimo típico: 4e-6 s (4 µs)
            - Máximo típico: 1000 s (depende del instrumento)
            - Default CNT-91: 0.2 s
            Si se pasa None, NO se configura el tiempo de integración y se usa el valor actual del instrumento.
        graficarFT : bool
            Si True, grafica frecuencia vs tiempo relativo (default: False)
        exportar_excel : bool
            Si True, exporta los datos a un archivo Excel (default: False)

        Salida:
        -------
        frecuencias : np.ndarray
            Array de frecuencias medidas (Hz)
        timestamps : np.ndarray
            Array de tiempos absolutos (s) en los que se tomó cada muestra
        delta_tiempos : np.ndarray
            Array de tiempos relativos al inicio (s)

        Notas sobre el funcionamiento y precisión:
        ------------------------------------------
        - El tiempo de integración real puede diferir ligeramente del solicitado, especialmente para valores muy pequeños (<1 ms) o muy grandes.
        - El instrumento realiza las mediciones en modo "zero dead time" (sin huecos entre muestras) **siempre que el intervalo de captura lo permita**. Para valores muy pequeños, puede haber limitaciones por el hardware.
        - Los timestamps devueltos por :MEASure:ARRay:TSTAmp? reflejan el tiempo real de cada medición, pero pueden tener un pequeño error (jitter) debido a la resolución interna del instrumento (~nanosegundos a microsegundos).
        - Si el intervalo de captura es muy pequeño, el instrumento puede no ser capaz de mantener "zero dead time" y aparecerán pequeños huecos.
        - Si el usuario pasa None como intervalo_captura, se usa el valor actual configurado en el instrumento.

        Errores esperados:
        ------------------
        - Si el instrumento no responde en 30 segundos, se lanza un timeout.
        - Si el número de frecuencias y timestamps no coincide, se lanza un error.
        """

        import numpy as np
        import time

        # ====== SECCIÓN 1: Validación de parámetros y canal ======
        canales = {'A': 1, 'B': 2, '1': 1, '2': 2}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_num = canales[ch]

        # ====== SECCIÓN 2: Reset y limpieza del instrumento ======
        self.dev.write('*RST')
        self.dev.write('*CLS')

        # ====== SECCIÓN 3: Timeout de comunicación VISA (30 segundos) ======
        self.dev.timeout = 30000  # Timeout en milisegundos
        """
                # Calcula el tiempo estimado de adquisición [PROBAR]
        eps = 1e-12
        T = intervalo_s
        N = n_muestras
        if abs(T - 4e-5) < eps and N == 2400:
            tiempo_espera = 0.25
        elif abs(T - 4e-4) < eps and N == 1000:
            tiempo_espera = 0.8
        else:
            raw = 2 * T**0.88 * N**0.85
            lin = 1.14 * T * N
            val = max(raw, lin)
            tiempo_espera = max(0.2, val) * 1.1

        # Establece el timeout de VISA (en milisegundos)
        self.dev.timeout = int(1000 * tiempo_espera * 1.2)  # 20% de margen extra
        
        
        """
        # ====== SECCIÓN 4: Configuración del tiempo de integración (apertura) ======
        # Si el usuario pasa None, NO se configura y se usa el valor actual del instrumento
        if intervalo_captura is not None:
            # Valores típicos CNT-91: mínimo 4e-6 s, máximo 1000 s, default 0.2 s
            self.dev.write(f"SENS:ACQ:APER {intervalo_captura}")

        # ====== SECCIÓN 5: Adquisición de frecuencias y timestamps ======
        # El instrumento realiza una sola adquisición de N muestras en modo "zero dead time" si es posible.
        # Los timestamps corresponden exactamente a las frecuencias adquiridas.
        self.dev.write(f":MEASure:ARRay:FREQuency:BTBack? {n_muestras},{canal_num}")
        data_freq = self.dev.read()
        frecuencias = np.array([float(val) for val in data_freq.strip().split(',') if val])

        self.dev.write(f":MEASure:ARRay:TSTAmp? {n_muestras},{canal_num}")
        data_time = self.dev.read()
        timestamps = np.array([float(val) for val in data_time.strip().split(',') if val])

        # ====== SECCIÓN 6: Control de errores en la adquisición ======
        if len(frecuencias) != len(timestamps):
            raise RuntimeError("El número de frecuencias y timestamps no coincide. Puede haber habido un error de comunicación.")

        # ====== SECCIÓN 7: Cálculo de tiempos relativos ======
        delta_tiempos = timestamps - timestamps[0]

        # ====== SECCIÓN 8: Visualización opcional ======
        if graficarFT:
            import matplotlib.pyplot as plt
            from matplotlib.ticker import MaxNLocator

            maximo = np.max(frecuencias)
            minimo = np.min(frecuencias)
            media = np.mean(frecuencias)
            mediana = np.median(frecuencias)
            n_puntos = len(frecuencias)

            plt.figure(figsize=(9, 5))
            plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
            plt.xlabel('Tiempo relativo [s]', fontsize=12)
            plt.ylabel('Frecuencia [Hz]', fontsize=12)
            plt.title('Frecuencia vs Tiempo relativo')
            plt.grid(True, which='both', linestyle='--', alpha=0.5)
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

            texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                        f"Mín: {minimo:.3f} Hz\n"
                        f"Media: {media:.3f} Hz\n"
                        f"Mediana: {mediana:.3f} Hz\n"
                        f"Nº puntos: {n_puntos}")
            plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                        ha='right', va='bottom', transform=plt.gca().transAxes,
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
            plt.tight_layout()
            plt.show()

        # ====== SECCIÓN 9: Exportar a Excel opcional ======
        if exportar_excel:
            import pandas as pd
            from datetime import datetime

            fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
            raw_data = {
                "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                "Frecuencia [Hz]": np.round(frecuencias, 6),
                "Timestamp [s]": np.round(timestamps, 6),
                "Delta_tiempo [s]": np.round(delta_tiempos, 6)
            }
            df_raw = pd.DataFrame(raw_data)
            nombre_raw = f"RawDataFreqYTiempo_BTBack_{fecha_hora}.xlsx"
            df_raw.to_excel(nombre_raw, index=False, float_format="%.6f")
            print(f"Archivo de datos crudos guardado como: {nombre_raw}")

        # ====== SECCIÓN 10: Devolver resultados ======
        return frecuencias, timestamps, delta_tiempos


# Falta corregir las SCPIs de configuración, falla por el canal , ha de ser 1 o 2

    def medir_n_muestras_equidistantesV31_BTBack( ## la recomendacion es de   , se llama overlapping
        self,
        n_muestras=100,
        canal='A',
        intervalo_captura=0.2,
        graficarFT=False,
        exportar_excel=False,
        acoplamiento=None,
        impedancia=None,
        atenuacion=None,
        trigger_level=None,
        trigger_slope=None,
        filtro=None
    ):
        """
        Adquisición rápida de un array de frecuencias y sus timestamps usando los comandos:
        - :MEASure:ARRay:FREQuency:BTBack? N,canal
        - :MEASure:ARRay:TSTAmp? N,canal

        Permite especificar el tiempo de integración (apertura) y la configuración avanzada del canal.

        Parámetros de entrada:
        ----------------------
        n_muestras : int
            Número de muestras a adquirir (default: 100)
        canal : str o int
            Canal de medida: 'A', 'B', 1 o 2 (default: 'A')
        intervalo_captura : float o None
            Tiempo de integración (apertura) en segundos para cada muestra.
            - Mínimo típico: 4e-6 s (4 µs)
            - Máximo típico: 1000 s (depende del instrumento)
            - Default CNT-91: 0.2 s
            Si se pasa None, NO se configura el tiempo de integración y se usa el valor actual del instrumento.
        graficarFT : bool
            Si True, grafica frecuencia vs tiempo relativo (default: False)
        exportar_excel : bool
            Si True, exporta los datos a un archivo Excel (default: False)
        acoplamiento, impedancia, atenuacion, trigger_level, trigger_slope, filtro : opcionales
            Configuración avanzada del canal. Si se pasa None, no se configura ese parámetro.

        Salida:
        -------
        frecuencias : np.ndarray
            Array de frecuencias medidas (Hz)
        timestamps : np.ndarray
            Array de tiempos absolutos (s) en los que se tomó cada muestra
        delta_tiempos : np.ndarray
            Array de tiempos relativos al inicio (s)

        Notas sobre el funcionamiento y precisión:
        ------------------------------------------
        - El tiempo de integración real puede diferir ligeramente del solicitado, especialmente para valores muy pequeños (<1 ms) o muy grandes.
        - El instrumento realiza las mediciones en modo "zero dead time" (sin huecos entre muestras) **siempre que el intervalo de captura lo permita**. Para valores muy pequeños, puede haber limitaciones por el hardware.
        - Los timestamps devueltos por :MEASure:ARRay:TSTAmp? reflejan el tiempo real de cada medición, pero pueden tener un pequeño error (jitter) debido a la resolución interna del instrumento (~nanosegundos a microsegundos).
        - Si el intervalo de captura es muy pequeño, el instrumento puede no ser capaz de mantener "zero dead time" y aparecerán pequeños huecos.
        - Si el usuario pasa None como intervalo_captura, se usa el valor actual configurado en el instrumento.

        Errores esperados:
        ------------------
        - Si el instrumento no responde en 30 segundos, se lanza un timeout.
        - Si el número de frecuencias y timestamps no coincide, se lanza un error.
        """

        import numpy as np
        import time

        # ====== SECCIÓN 1: Validación de parámetros y canal ======
        canales = {'A': 1, 'B': 2, '1': 1, '2': 2}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_num = canales[ch]

        # ====== SECCIÓN 2: Reset y limpieza del instrumento ======
        self.dev.write('*RST')
        self.dev.write('*CLS')

        # ====== SECCIÓN 3: Configuración avanzada de canal (solo si se especifica) ======
        # Todos los parámetros son opcionales y solo se configuran si el usuario los pasa
        if acoplamiento is not None:
            self.dev.write(f':INP{canal_num}:COUP {acoplamiento}')
        if impedancia is not None:
            self.dev.write(f':INP{canal_num}:IMP {impedancia}')
        if atenuacion is not None:
            self.dev.write(f':INP{canal_num}:ATT {atenuacion}')
        if trigger_level is not None:
            self.dev.write(f':INP{canal_num}:TRL {trigger_level}')
        if trigger_slope is not None:
            self.dev.write(f':INP{canal_num}:TRS {trigger_slope}')
        if filtro is not None:
            self.dev.write(f':INP{canal_num}:FIL:DIG:FREQ {filtro}')

        # ====== SECCIÓN 4: Mejoras recomendadas según el manual ======
        # Desactivar interpoladores para máxima velocidad

        # self.dev.write('CAL:INT:AUTO OFF')   # PUEDE HACER QUE PIERDAS RESOLUCION Y PRECISION

        # Apagar display durante la adquisición
        self.dev.write('DISP:ENAB OFF')

        # ====== SECCIÓN 5: Timeout de comunicación VISA (30 segundos) ======
        self.dev.timeout = 30000  # Timeout en milisegundos

        # ====== SECCIÓN 6: Configuración del tiempo de integración (apertura) ======
        # Si el usuario pasa None, NO se configura y se usa el valor actual del instrumento
        if intervalo_captura is not None:
            # Valores típicos CNT-91: mínimo 4e-6 s, máximo 1000 s, default 0.2 s
            self.dev.write(f"SENS:ACQ:APER {intervalo_captura}")

        # ====== SECCIÓN 7: Adquisición de frecuencias y timestamps ======
        # El instrumento realiza una sola adquisición de N muestras en modo "zero dead time" si es posible.
        # Los timestamps corresponden exactamente a las frecuencias adquiridas.
        self.dev.write(f":MEASure:ARRay:FREQuency:BTBack? {n_muestras},{canal_num}")
        data_freq = self.dev.read()
        frecuencias = np.array([float(val) for val in data_freq.strip().split(',') if val])

        self.dev.write(f":MEASure:ARRay:TSTAmp? {n_muestras},{canal_num}")
        data_time = self.dev.read()
        timestamps = np.array([float(val) for val in data_time.strip().split(',') if val])

        # ====== SECCIÓN 8: Control de errores en la adquisición ======
        if len(frecuencias) != len(timestamps):
            raise RuntimeError("El número de frecuencias y timestamps no coincide. Puede haber habido un error de comunicación.")

        # ====== SECCIÓN 9: Cálculo de tiempos relativos ======
        delta_tiempos = timestamps - timestamps[0]

        # ====== SECCIÓN 10: Visualización opcional ======
        if graficarFT:
            import matplotlib.pyplot as plt
            from matplotlib.ticker import MaxNLocator

            maximo = np.max(frecuencias)
            minimo = np.min(frecuencias)
            media = np.mean(frecuencias)
            mediana = np.median(frecuencias)
            n_puntos = len(frecuencias)

            plt.figure(figsize=(9, 5))
            plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
            plt.xlabel('Tiempo relativo [s]', fontsize=12)
            plt.ylabel('Frecuencia [Hz]', fontsize=12)
            plt.title('Frecuencia vs Tiempo relativo')
            plt.grid(True, which='both', linestyle='--', alpha=0.5)
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

            texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                        f"Mín: {minimo:.3f} Hz\n"
                        f"Media: {media:.3f} Hz\n"
                        f"Mediana: {mediana:.3f} Hz\n"
                        f"Nº puntos: {n_puntos}")
            plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                        ha='right', va='bottom', transform=plt.gca().transAxes,
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
            plt.tight_layout()
            plt.show()

        # ====== SECCIÓN 11: Exportar a Excel opcional ======
        if exportar_excel:
            import pandas as pd
            from datetime import datetime

            fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
            raw_data = {
                "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                "Frecuencia [Hz]": np.round(frecuencias, 6),
                "Timestamp [s]": np.round(timestamps, 6),
                "Delta_tiempo [s]": np.round(delta_tiempos, 6)
            }
            df_raw = pd.DataFrame(raw_data)
            nombre_raw = f"RawDataFreqYTiempo_BTBack_{fecha_hora}.xlsx"
            df_raw.to_excel(nombre_raw, index=False, float_format="%.6f")
            print(f"Archivo de datos crudos guardado como: {nombre_raw}")

        # ====== SECCIÓN 12: Reactivar display al finalizar ======
        self.dev.write('DISP:ENAB ON')

        # ====== SECCIÓN 13: Devolver resultados ======
        return frecuencias, timestamps, delta_tiempos    


# version de Joan pero muy eficiente y ambicioso

    def medir_n_muestras_equidistantesV31_BTBack_improved(
        self,
        n_muestras=100,
        canal='A',
        intervalo_captura=0.2,
        graficarFT=False,
        exportar_excel=False,
        acoplamiento=None,
        impedancia=None,
        atenuacion=None,
        trigger_level=None,
        trigger_slope=None,
        filtro=None
    ):
        """
        Adquisición rápida de un array de frecuencias y sus timestamps usando los comandos:
        - :MEASure:ARRay:FREQuency:BTBack? N,canal
        - :MEASure:ARRay:TSTAmp? N,canal
        en formato PACKED (binario), para máxima velocidad de transferencia.

        Permite especificar el tiempo de integración (apertura) y la configuración avanzada del canal.

        Parámetros de entrada:
        ----------------------
        n_muestras : int
            Número de muestras a adquirir (default: 100)
        canal : str o int
            Canal de medida: 'A', 'B', 1 o 2 (default: 'A')
        intervalo_captura : float o None
            Tiempo de integración (apertura) en segundos para cada muestra.
            - Mínimo típico: 4e-6 s (4 µs)
            - Máximo típico: 1000 s (depende del instrumento)
            - Default CNT-91: 0.2 s
            Si se pasa None, NO se configura el tiempo de integración y se usa el valor actual del instrumento.
        graficarFT : bool
            Si True, grafica frecuencia vs tiempo relativo (default: False)
        exportar_excel : bool
            Si True, exporta los datos a un archivo Excel (default: False)
        acoplamiento, impedancia, atenuacion, trigger_level, trigger_slope, filtro : opcionales
            Configuración avanzada del canal. Si se pasa None, no se configura ese parámetro.

        Salida:
        -------
        frecuencias : np.ndarray
            Array de frecuencias medidas (Hz)
        timestamps : np.ndarray
            Array de tiempos absolutos (s) en los que se tomó cada muestra
        delta_tiempos : np.ndarray
            Array de tiempos relativos al inicio (s)
        """

        import numpy as np
        import time

        # ====== SECCIÓN 1: Validación de parámetros y canal ======
        canales = {'A': 1, 'B': 2, '1': 1, '2': 2}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_num = canales[ch]

        # ====== SECCIÓN 2: Reset y limpieza del instrumento ======
        self.dev.write('*RST')
        self.dev.write('*CLS')

        # ====== SECCIÓN 3: Configuración avanzada de canal (solo si se especifica) ======
        if acoplamiento is not None:
            self.dev.write(f':INP{canal_num}:COUP {acoplamiento}')
        if impedancia is not None:
            self.dev.write(f':INP{canal_num}:IMP {impedancia}')
        if atenuacion is not None:
            self.dev.write(f':INP{canal_num}:ATT {atenuacion}')
        if trigger_level is not None:
            self.dev.write(f':INP{canal_num}:TRL {trigger_level}')
        if trigger_slope is not None:
            self.dev.write(f':INP{canal_num}:TRS {trigger_slope}')
        if filtro is not None:
            self.dev.write(f':INP{canal_num}:FIL:DIG:FREQ {filtro}')

        # ====== SECCIÓN 4: Mejoras recomendadas según el manual ======
        # self.dev.write('CAL:INT:AUTO OFF')   # Desactivar interpoladores solo si no necesitas máxima precisión
        self.dev.write('DISP:ENAB OFF')

        # ====== SECCIÓN 5: Timeout de comunicación VISA (30 segundos) ======
        self.dev.timeout = 30000  # Timeout en milisegundos  --> EN SU LUGAR PODRIA PONER LA EQUACION QUE CALCULÉ O PONERLA INDEFINIDAMENTE tiempo_estimado = n_muestras * intervalo_captura ....

        # ====== SECCIÓN 6: Configuración del tiempo de integración (apertura) ======
        if intervalo_captura is not None:
            self.dev.write(f"SENS:ACQ:APER {intervalo_captura}")

        # ====== SECCIÓN 7: Selección de formato PACKED para máxima velocidad ======
        self.dev.write("FORM:PACK")

        # ====== SECCIÓN 8: Adquisición de frecuencias y timestamps en binario ======
        self.dev.write(f":MEASure:ARRay:FREQuency:BTBack? {n_muestras},{canal_num}")
        data_freq = self.dev.read_raw()  # Usar read_raw() para binario
        frecuencias = np.frombuffer(data_freq, dtype=np.float64)

        self.dev.write(f":MEASure:ARRay:TSTAmp? {n_muestras},{canal_num}")
        data_time = self.dev.read_raw()
        timestamps = np.frombuffer(data_time, dtype=np.float64)

        # ====== SECCIÓN 9: Control de errores en la adquisición ======
        if len(frecuencias) != len(timestamps):
            raise RuntimeError("El número de frecuencias y timestamps no coincide. Puede haber habido un error de comunicación.")

        # ====== SECCIÓN 10: Cálculo de tiempos relativos ======
        delta_tiempos = timestamps - timestamps[0]

        # ====== SECCIÓN 11: Visualización opcional ======
        if graficarFT:
            import matplotlib.pyplot as plt
            from matplotlib.ticker import MaxNLocator

            maximo = np.max(frecuencias)
            minimo = np.min(frecuencias)
            media = np.mean(frecuencias)
            mediana = np.median(frecuencias)
            n_puntos = len(frecuencias)

            plt.figure(figsize=(9, 5))
            plt.plot(delta_tiempos, frecuencias, marker='o', linestyle='-', label='Frecuencia')
            plt.xlabel('Tiempo relativo [s]', fontsize=12)
            plt.ylabel('Frecuencia [Hz]', fontsize=12)
            plt.title('Frecuencia vs Tiempo relativo')
            plt.grid(True, which='both', linestyle='--', alpha=0.5)
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

            texto_stats = (f"Máx: {maximo:.3f} Hz\n"
                        f"Mín: {minimo:.3f} Hz\n"
                        f"Media: {media:.3f} Hz\n"
                        f"Mediana: {mediana:.3f} Hz\n"
                        f"Nº puntos: {n_puntos}")
            plt.gca().text(0.98, 0.02, texto_stats, fontsize=10,
                        ha='right', va='bottom', transform=plt.gca().transAxes,
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
            plt.tight_layout()
            plt.show()

        # ====== SECCIÓN 12: Exportar a Excel opcional ======
        if exportar_excel:
            import pandas as pd
            from datetime import datetime

            fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
            raw_data = {
                "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                "Frecuencia [Hz]": np.round(frecuencias, 6),
                "Timestamp [s]": np.round(timestamps, 6),
                "Delta_tiempo [s]": np.round(delta_tiempos, 6)
            }
            df_raw = pd.DataFrame(raw_data)
            nombre_raw = f"RawDataFreqYTiempo_BTBack_{fecha_hora}.xlsx"
            df_raw.to_excel(nombre_raw, index=False, float_format="%.6f")
            print(f"Archivo de datos crudos guardado como: {nombre_raw}")

        # ====== SECCIÓN 13: Reactivar display al finalizar ======
        self.dev.write('DISP:ENAB ON')

        # ====== SECCIÓN 14: Devolver resultados ======
        return frecuencias, timestamps, delta_tiempos

# para el adev de la anterior funcion con método :  JOAN
    def calcular_allan_deviation_overlapping(frecuencias, intervalo_captura):
        """
        Calcula la desviación de Allan (Allan deviation) para un array de frecuencias equidistantes.

        Parámetros:
        -----------
        frecuencias : array-like
            Array de frecuencias medidas (Hz), equidistantes en el tiempo.
        intervalo_captura : float
            Intervalo de captura (tiempo de integración) entre muestras (en segundos).

        Devuelve:
        ---------
        adevs : np.ndarray
            Array de valores de desviación de Allan (Hz) para cada tau.
        taus : np.ndarray
            Array de valores de tau (segundos) para los que se ha calculado la desviación de Allan.
        """
        import numpy as np
        frecuencias = np.asarray(frecuencias)
        N = len(frecuencias)
        max_m = N // 2  # Solo tiene sentido hasta la mitad del array

        taus = []
        adevs = []

        for m in range(1, max_m + 1):
            M = N // m
            if M < 2:
                break
            # Promedios de frecuencia para cada bloque de tamaño m
            promedios = [np.mean(frecuencias[i * m:(i + 1) * m]) for i in range(M)]
            # Diferencias cuadráticas entre bloques consecutivos
            dif_cuadrado = [(promedios[i + 1] - promedios[i]) ** 2 for i in range(M - 1)]
            sigma2 = np.sum(dif_cuadrado) / (2 * (M - 1))
            sigma = np.sqrt(sigma2)
            taus.append(m * intervalo_captura)
            adevs.append(sigma)

        return np.array(adevs), np.array(taus)




    # para el adev  :  JAUME
    def Calc_Adev_single_Tau(
        self,
        n_muestras=100,
        canal='A',
        intervalo_captura_min=0.01,
        intervalo_captura_max=1.0,
        pasos=10,
        acoplamiento=None,
        impedancia=None,
        atenuacion=None,
        trigger_level=None,
        trigger_slope=None,
        filtro=None,
        graficar=False,
        exportar_excel=False
    ):
        """
        Realiza un barrido de tiempos de integración (tau) entre intervalo_captura_min y intervalo_captura_max,
        adquiere los datos para cada tau (sin llamar a funciones externas), y calcula la desviación de Allan (Adev)
        para cada uno de esos valores.

        Devuelve:
        ---------
        adevs : np.ndarray
            Array de valores de desviación de Allan (Hz) para cada tau.
        taus : np.ndarray
            Array de valores de tau (segundos) usados.
        """


        """
        
        Ventaja:
        El tau es exacto y definido por hardware.
        El ruido de medida es menor para cada tau.
        Desventaja:
        No puedes calcular la Allan deviation para submúltiplos de tau sin repetir la adquisición.
        Es más lento si quieres cubrir muchos valores de tau.
        """
        import numpy as np

        taus = np.linspace(intervalo_captura_min, intervalo_captura_max, pasos)
        adevs = []

        canales = {'A': 1, 'B': 2, '1': 1, '2': 2}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_num = canales[ch]

        for tau in taus:
            # ====== Reset y limpieza del instrumento ======
            self.dev.write('*RST')
            self.dev.write('*CLS')

            # ====== Configuración avanzada de canal (solo si se especifica) ======
            if acoplamiento is not None:
                self.dev.write(f':INP{canal_num}:COUP {acoplamiento}')
            if impedancia is not None:
                self.dev.write(f':INP{canal_num}:IMP {impedancia}')
            if atenuacion is not None:
                self.dev.write(f':INP{canal_num}:ATT {atenuacion}')
            if trigger_level is not None:
                self.dev.write(f':INP{canal_num}:TRL {trigger_level}')
            if trigger_slope is not None:
                self.dev.write(f':INP{canal_num}:TRS {trigger_slope}')
            if filtro is not None:
                self.dev.write(f':INP{canal_num}:FIL:DIG:FREQ {filtro}')

            # ====== Mejoras recomendadas según el manual ======
            # self.dev.write('CAL:INT:AUTO OFF')   # Desactivar interpoladores solo si no necesitas máxima precisión
            self.dev.write('DISP:ENAB OFF')

            # ====== Timeout de comunicación VISA (30 segundos) ======
            self.dev.timeout = 30000

            """
                        # Calcula el tiempo estimado de adquisición [PROBAR]
            eps = 1e-12
            T = intervalo_s
            N = n_muestras
            if abs(T - 4e-5) < eps and N == 2400:
                tiempo_espera = 0.25
            elif abs(T - 4e-4) < eps and N == 1000:
                tiempo_espera = 0.8
            else:
                raw = 2 * T**0.88 * N**0.85
                lin = 1.14 * T * N
                val = max(raw, lin)
                tiempo_espera = max(0.2, val) * 1.1

            # Establece el timeout de VISA (en milisegundos)
            self.dev.timeout = int(1000 * tiempo_espera * 1.2)  # 20% de margen extra
            
            
            
            """

            # ====== Configuración del tiempo de integración (apertura) ======
            self.dev.write("FORM:PACK")
            self.dev.write(f"SENS:ACQ:APER {tau}")

            # ====== Adquisición de frecuencias y timestamps en binario ======
            self.dev.write(f":MEASure:ARRay:FREQuency:BTBack? {n_muestras},{canal_num}")
            data_freq = self.dev.read_raw()
            frecuencias = np.frombuffer(data_freq, dtype=np.float64)

            self.dev.write(f":MEASure:ARRay:TSTAmp? {n_muestras},{canal_num}")
            data_time = self.dev.read_raw()
            timestamps = np.frombuffer(data_time, dtype=np.float64)

            # ====== Control de errores en la adquisición ======
            if len(frecuencias) != len(timestamps):
                raise RuntimeError("El número de frecuencias y timestamps no coincide. Puede haber habido un error de comunicación.")

            # ====== Cálculo de Allan deviation para este tau (solo m=1) ======
            if len(frecuencias) < 2:
                adev = np.nan
            else:
                difs = np.diff(frecuencias)
                sigma2 = np.sum(difs**2) / (2 * (len(frecuencias) - 1))
                adev = np.sqrt(sigma2)
            adevs.append(adev)

            # ====== Reactivar display al finalizar cada tau ======
            self.dev.write('DISP:ENAB ON')

        adevs = np.array(adevs)

        # Graficar si se solicita
        if graficar:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 5))
            plt.plot(taus, adevs, marker='o', linestyle='-')
            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel('Tau (s)')
            plt.ylabel('Allan deviation (Hz)')
            plt.title('Allan deviation vs Tau')
            plt.grid(True, which='both', linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.show()

        # Exportar a Excel si se solicita
        if exportar_excel:
            import pandas as pd
            from datetime import datetime
            fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
            df = pd.DataFrame({'Tau (s)': taus, 'Adev (Hz)': adevs})
            nombre = f"Adev_vs_Tau_{fecha_hora}.xlsx"
            df.to_excel(nombre, index=False, float_format="%.6f")
            print(f"Archivo de Adev vs Tau guardado como: {nombre}")

        return adevs, taus




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




#             medir_n_muestras_equidistantes     TIEMPOS y tiempos relativos

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
n_muestras = 100

intervalo_s = 0.2

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V2
frecuencias, timestamps, delta_tiempos = objt_prueba.medir_n_muestras_equidistantesV2(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s") 

"""








#      medir_n_muestras_equidistantes     TIEMPOS y tiempos relativos y graficar F vs T

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
n_muestras = 10

intervalo_s = 0.2

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V2
frecuencias, timestamps, delta_tiempos = objt_prueba.medir_n_muestras_equidistantesV3(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s") 


"""




#      medir_n_muestras_equidistantes     TIEMPOS y tiempos relativos y graficar F vs T
# Medir ADEVS



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
n_muestras = 10
intervalo_s = 0.2

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V4
frecuencias, timestamps, delta_tiempos, allan_deviations, taus = objt_prueba.medir_n_muestras_equidistantesV4(
    n_muestras=n_muestras, intervalo_s=intervalo_s, graficarFT=True,
)

# Mostrar los resultados en el formato solicitado (con unidades)
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1} : {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")

print("\nDATO  : Allan deviations y Taus")
# Mostrar los pares Allan deviation y Tau juntos y con unidades
for i in range(len(allan_deviations)):
    print(f"Tau {taus[i]:.3f} s: Allan deviation = {allan_deviations[i]:.6f} Hz")

"""



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
intervalo_s = 0.5

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V4
frecuencias, timestamps, delta_tiempos, allan_deviations, taus = objt_prueba.medir_n_muestras_equidistantesV6(
    n_muestras=n_muestras, intervalo_s=intervalo_s, graficarFT=True,graficarDevTau=True,
)

# Mostrar los resultados en el formato solicitado (con unidades)
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1} : {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")

print("\nDATOS  : Allan deviations y Taus")
# Mostrar los pares Allan deviation y Tau juntos y con unidades
for i in range(len(allan_deviations)):
    print(f"Tau {taus[i]:.3f} s: Allan deviation = {allan_deviations[i]:.6f} Hz")



"""





#      medir_n_muestras_equidistantes     TIEMPOS y tiempos relativos y graficar F vs T
# Medir ADEVS
# guardar valores en excel



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
n_muestras = 1000
intervalo_s = 0.5

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V4
frecuencias, timestamps, delta_tiempos, allan_deviations, taus = objt_prueba.medir_n_muestras_equidistantesV5(
    n_muestras=n_muestras, intervalo_s=intervalo_s, graficarFT=True,graficarDevTau=True,
)

# Mostrar los resultados en el formato solicitado (con unidades)
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1} : {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")

print("\nDATO  : Allan deviations y Taus")
# Mostrar los pares Allan deviation y Tau juntos y con unidades
for i in range(len(allan_deviations)):
    print(f"Tau {taus[i]:.3f} s: Allan deviation = {allan_deviations[i]:.6f} Hz")




"""


# Configuración dispositivo

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

#

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
n_muestras = 200

intervalo_s = 2E-4

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V2
frecuencias, timestamps, delta_tiempos = objt_prueba.medir_n_muestras_equidistantesV31(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s") 




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







# Hardware pacing


"""
# ==== PRUEBA DE LA FUNCIÓN medir_n_muestras_equidistantes_hardware ====

# 1. Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# 2. Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# 3. Parámetros de la prueba
n_muestras = 200
intervalo_s = 0.2

# 4. Calcular y mostrar el tiempo de espera antes de medir (ajusta si lo ves necesario)
tiempo_espera = n_muestras * intervalo_s * 1.05  # Alineado con la función hardware
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# 5. Ejecutar la medición con la función hardware pacing
frecuencias, timestamps, delta_tiempos = objt_prueba.medir_n_muestras_equidistantes_hardware(
    n_muestras=n_muestras,
    intervalo_s=intervalo_s,
    graficarFT=True,
    exportar_excel=True
)

# 6. Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")
"""



# LEER EL ADEV ESTADÍSTICO

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
n_muestras = 100
intervalo_s = 4e-6

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V4
frecuencias, timestamps, delta_tiempos, allan_deviations, taus = objt_prueba.medir_n_muestras_equidistantesV7(
    n_muestras=n_muestras, intervalo_s=intervalo_s, graficarFT=True,graficarDevTau=True,
)

# Mostrar los resultados en el formato solicitado (con unidades)
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1} : {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s")

print("\nDATOS  : Allan deviations y Taus")
# Mostrar los pares Allan deviation y Tau juntos y con unidades
for i in range(len(allan_deviations)):
    print(f"Tau {taus[i]:.6f} s: Allan deviation = {allan_deviations[i]:.6f} Hz")




"""



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
n_muestras = 10



intervalo_s = 4.00E-06



# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición con la nueva función V2
frecuencias, timestamps, delta_tiempos = objt_prueba.continuous_measurament_v31(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s") 





"""


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

try:
        adev = objt_prueba.leer_adev_cnt91()
        if adev is not None:
            print(f"ADEV obtenida: {adev}")
        else:
            print("Error: no se pudo obtener la ADEV.")
            
except Exception as e:
        print(f"Excepción al probar leer_adev_cnt91: {e}")




"""





"""




"""