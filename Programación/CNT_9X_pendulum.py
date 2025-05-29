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
        self.dev.write('CAL:INT:AUTO OFF')
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







    def leer_adev_cnt91(self):
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
                Allan_Deviation = valores[1] if len(valores) > 1 else None
            except Exception:
                Allan_Deviation = None
            
            # 7. Desactivar el cálculo estadístico al terminar
            self.dev.write(':CALC:AVER:STAT OFF')
        
            return Allan_Deviation
            
        except Exception as e:
            print(f"Error al leer ADEV: {str(e)}")
            return None

    def leer_adev_cnt91_improved2(self, no_samples=100, pacing_state=False, pacing_time=20, canal='A'):
        """
        Versión mejorada 2 de la función para extraer la Allan deviation (ADEV) del CNT-91.
        Sigue la estructura correcta de comandos SCPI para cálculos estadísticos.
        
        Nota sobre el cálculo de Allan deviation en el CNT-91:
        El instrumento calcula la Allan deviation internamente usando la fórmula:
        σ²(τ) = 1/[2(N-2m)] * Σ[yₖ₊₂ₘ - 2yₖ₊ₘ + yₖ]²
        
        Donde:
        - τ: tiempo de observación
        - N: número total de muestras
        - m: número de muestras en cada grupo
        - yₖ: mediciones de frecuencia
        
        El CNT-91:
        1. Toma las muestras configuradas
        2. Las agrupa internamente para diferentes valores de τ
        3. Calcula la Allan deviation para cada τ
        4. Devuelve los resultados al solicitar :CALC:DATA?
        
        Nota importante sobre el número de muestras:
        El instrumento requiere que el número de muestras sea un múltiplo del número
        de medidas que puede hacer el trigger. Por ejemplo, si el trigger está configurado
        para 1000 medidas y pedimos 9500 muestras, el instrumento hará 10000 medidas
        (el múltiplo de 1000 más cercano a 9500).
        
        Parámetros:
            no_samples (int): Número de muestras para el cálculo
                - Rango: 2 a 1000000
                - Default: 100
                - Descripción: Define cuántas mediciones individuales se realizarán para el cálculo de la Allan deviation.
                  Un mayor número de muestras proporciona mayor precisión en el cálculo.
                  Nota: El número real de muestras puede ser mayor si no es múltiplo del trigger.
            
            pacing_state (bool): Estado del pacing
                - Valores posibles: True/False
                - Default: False
                - Descripción: Controla si las mediciones se realizan con un intervalo fijo (True)
                  o inmediatamente una tras otra (False)
            
            pacing_time (int): Tiempo de pacing en milisegundos
                - Rango: 1 a 1000000 ms
                - Default: 20
                - Descripción: Define el intervalo de tiempo entre mediciones cuando pacing_state es True.
                  Solo tiene efecto si pacing_state es True.
            
            canal (str o int): Canal de medida
                - Valores posibles: 'A', 'B', 1 o 2
                - Default: 'A'
                - Descripción: Especifica el canal a utilizar para la medición
                  - 'A' o 1: Canal A
                  - 'B' o 2: Canal B
        
        Comandos SCPI utilizados:
            1. *RST (Reset)
               - Descripción: Restablece el instrumento a su estado predeterminado
               - Efecto: Borra todas las configuraciones personalizadas
            
            2. *CLS (Clear Status)
               - Descripción: Borra el registro de errores y eventos
               - Efecto: Limpia el buffer de errores para evitar interferencias
            
            3. :CONF:FREQ (Configure Frequency)
               - Descripción: Configura la medición de frecuencia
               - Sintaxis: :CONF:FREQ (@1) o :CONF:FREQ (@2)
               - Efecto: Prepara el instrumento para medir frecuencia
            
            4. :CALC:AVER:COUN (Calculate Average Count)
               - Descripción: Configura el número de muestras para el cálculo
               - Sintaxis: :CALC:AVER:COUN <número>
               - Efecto: Define cuántas mediciones se realizarán para el cálculo estadístico
               - Nota: El número real de muestras puede ser mayor si no es múltiplo del trigger
            
            5. :TRIG:TIM (Trigger Timer)
               - Descripción: Configura el intervalo de tiempo entre mediciones
               - Sintaxis: :TRIG:TIM <tiempo>ms
               - Efecto: Define el espaciado temporal entre mediciones
            
            6. :TRIG:SOUR (Trigger Source)
               - Descripción: Selecciona la fuente de trigger
               - Valores: 'IMM' (inmediato) o 'TIM' (timer)
               - Efecto: Controla cómo se inician las mediciones
            
            7. :CALC:STAT (Calculate Statistics)
               - Descripción: Activa/desactiva el cálculo estadístico
               - Valores: ON/OFF
               - Efecto: Habilita el procesamiento estadístico de los datos
            
            8. :CALC:TYPE (Calculate Type)
               - Descripción: Define el tipo de cálculo estadístico
               - Valor: 'ADEV' para Allan deviation
               - Efecto: Especifica que se calcule la Allan deviation
            
            9. :INIT (Initialize)
               - Descripción: Inicia la medición
               - Efecto: Comienza el proceso de adquisición de datos
            
            10. *OPC? (Operation Complete Query)
                - Descripción: Consulta si la operación ha terminado
                - Efecto: Espera a que se complete la medición actual
            
            11. :CALC:DATA? (Calculate Data Query)
                - Descripción: Solicita los datos calculados (DEBE usarse para operaciones estadísticas)
                - Efecto: Obtiene los resultados del análisis estadístico
        
        Retorna:
            Allan_Deviation: float
                Allan deviation interna (o None si ocurre algún error)
        """
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            # 1. Resetear el instrumento para asegurar estado limpio
            # *RST - Restablece el instrumento a su estado predeterminado
            self.dev.write('*RST')
            
            # 2. Limpiar errores previos
            # *CLS - Borra el registro de errores
            self.dev.write("*CLS")
            
            # 3. Configurar parámetros de medición
            # :CONF:FREQ - Configura la medición de frecuencia
            self.dev.write(f':CONF:FREQ {canal_cmd}')
            
            # :CALC:AVER:COUN - Configura el número de muestras para el cálculo
            self.dev.write(f':CALC:AVER:COUN {no_samples}')
            
            # :TRIG:TIM - Configura el tiempo de pacing en milisegundos
            self.dev.write(f':TRIG:TIM {pacing_time}ms')
            
            # :TRIG:SOUR - Configura la fuente de trigger
            if pacing_state:
                self.dev.write(':TRIG:SOUR TIM')  # TIM - Timer trigger
            else:
                self.dev.write(':TRIG:SOUR IMM')  # IMM - Immediate trigger
            
            # 4. Configurar y activar el cálculo estadístico
            # :CALC:STAT - Activa/desactiva el cálculo estadístico
            self.dev.write(':CALC:STAT ON')
            # :CALC:TYPE - Define el tipo de cálculo estadístico (ADEV)
            self.dev.write(':CALC:TYPE ADEV')
            
            # 5. Iniciar la medición y esperar a que complete
            # :INIT - Inicia la medición
            self.dev.write(':INIT')
            
            # Bucle para mostrar el progreso de las muestras
            import time
            muestra_anterior = 0
            while True:
                self.dev.write(':CALC:AVER:COUN:CURR?')
                muestra_actual = int(float(self.dev.read()))
                
                # Solo mostrar si el número de muestra ha cambiado
                if muestra_actual != muestra_anterior:
                    print(f"\rMuestra {muestra_actual} de {no_samples}", end='', flush=True)
                    muestra_anterior = muestra_actual
                
                if muestra_actual >= no_samples:
                    print()  # Nueva línea al terminar
                    break
                    
                time.sleep(0.1)  # Pequeña pausa para no saturar el bus
            
            # *OPC? - Consulta si la operación ha terminado
            self.dev.write('*OPC?')
            self.dev.read()  # Esperar a que complete
            
            # 6. Obtener los datos calculados
            # :CALC:DATA? - Solicita los datos calculados (DEBE usarse para operaciones estadísticas)
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            print("Valor bruto de ADEV:", resp_adev)
        
            # 7. Procesar la respuesta
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                Allan_Deviation = valores[1] if len(valores) > 1 else None
            except Exception:
                Allan_Deviation = None
            
            # 8. Desactivar el cálculo estadístico al terminar
            self.dev.write(':CALC:STAT OFF')
        
            return Allan_Deviation
            
        except Exception as e:
            print(f"Error al leer ADEV: {str(e)}")
            return None




    def calcular_adev(self, canal='A'):
        """
        Calcula la Allan deviation (ADEV) y el valor medio de las mediciones.
        Sigue la estructura de comandos SCPI del manual del CNT-91.
        
        Parámetros:
            canal (str o int): Canal de medida
                - Valores posibles: 'A', 'B', 1 o 2
                - Default: 'A'
                - Descripción: Especifica el canal a utilizar para la medición
                  - 'A' o 1: Canal A
                  - 'B' o 2: Canal B
        
        Comandos SCPI utilizados:
            1. :CALC:AVER:STAT ON
               - Descripción: Activa el cálculo estadístico
            
            2. :CALC:TYPE ADEV
               - Descripción: Configura el tipo de cálculo como Allan deviation
            
            3. :INIT
               - Descripción: Inicia la medición
            
            4. *OPC?
               - Descripción: Espera a que la operación se complete
            
            5. :CALC:DATA?
               - Descripción: Obtiene los datos calculados (Allan deviation)
            
            6. :CALC:TYPE MEAN
               - Descripción: Configura el tipo de cálculo como valor medio
            
            7. :CALC:IMM?
               - Descripción: Obtiene el valor medio calculado
        
        Retorna:
            tuple: (allan_deviation, valor_medio)
                - allan_deviation: float - Valor de la Allan deviation
                - valor_medio: float - Valor medio de las mediciones
                Si ocurre algún error, retorna (None, None)
        """
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            # 1. Resetear y limpiar
            self.dev.write('*RST')
            self.dev.write('*CLS')
            
            # 2. Configurar canal
            self.dev.write(f':CONF:FREQ {canal_cmd}')
            
            # 3. Activar estadísticas y configurar ADEV
            self.dev.write(':CALC:AVER:STAT ON')
            self.dev.write(':CALC:TYPE ADEV')
            
            # 4. Iniciar medición y esperar
            self.dev.write(':INIT')
            
            # 5. Obtener Allan deviation
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                allan_deviation = valores[1] if len(valores) > 1 else None
            except Exception:
                allan_deviation = None
            
            # 6. Mantener ADEV para el valor medio
            self.dev.write(':CALC:TYPE ADEV')
            
            # 7. Obtener valor medio
            self.dev.write(':CALC:IMM?')
            resp_media = self.dev.read()
            try:
                valor_medio = float(resp_media)
            except Exception:
                valor_medio = None
            
            # 8. Desactivar estadísticas
            self.dev.write(':CALC:AVER:STAT OFF')
            
            return allan_deviation, valor_medio
            
        except Exception as e:
            print(f"Error al calcular ADEV y media: {str(e)}")
            return None, None

    def calcular_adev_y_media_improved(self, canal='A'):
        """
        Versión mejorada que calcula la Allan deviation (ADEV) y el valor medio.
        Sigue exactamente la estructura del manual del CNT-91:
        
        Ejemplo del manual:
        SEND :CALC:AVER:STAT ON;TYPE SDEV;:INIT;*OPC
        Wait for operation complete
        SEND :CALC:DATA?
        READ <Value of standard deviation>
        SEND :CALC:AVER:TYPE MEAN
        SEND :CALC:IMM?
        READ <Mean value>
        
        Parámetros:
            canal (str o int): Canal de medida
                - Valores posibles: 'A', 'B', 1 o 2
                - Default: 'A'
                - Descripción: Especifica el canal a utilizar para la medición
                  - 'A' o 1: Canal A
                  - 'B' o 2: Canal B
        
        Comandos SCPI utilizados:
            1. :CALC:AVER:STAT ON
               - Descripción: Activa el cálculo estadístico
            
            2. :CALC:TYPE ADEV
               - Descripción: Configura el tipo de cálculo como Allan deviation
            
            3. :INIT
               - Descripción: Inicia la medición
            
            4. *OPC?
               - Descripción: Espera a que la operación se complete
            
            5. :CALC:DATA?
               - Descripción: Obtiene los datos calculados (Allan deviation)
            
            6. :CALC:TYPE MEAN
               - Descripción: Cambia el tipo de cálculo a valor medio
            
            7. :CALC:IMM?
               - Descripción: Obtiene el valor medio calculado
        
        Retorna:
            tuple: (allan_deviation, valor_medio)
                - allan_deviation: float - Valor de la Allan deviation
                - valor_medio: float - Valor medio de las mediciones
                Si ocurre algún error, retorna (None, None)
        """
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            # 1. Resetear y limpiar
            self.dev.write('*RST')
            self.dev.write('*CLS')
            
            # 2. Configurar canal
            self.dev.write(f':CONF:FREQ {canal_cmd}')
            
            # 3. Activar estadísticas y configurar ADEV (siguiendo el ejemplo del manual)
            self.dev.write(':CALC:AVER:STAT ON;TYPE ADEV;:INIT;*OPC?')
            self.dev.read()  # Esperar a que complete
            
            # 4. Obtener Allan deviation
            self.dev.write(':CALC:DATA?')
            resp_adev = self.dev.read()
            try:
                valores = [float(val) for val in resp_adev.strip().split(',') if val]
                allan_deviation = valores[1] if len(valores) > 1 else None
            except Exception:
                allan_deviation = None
            
            # 5. Cambiar a cálculo de media (siguiendo el ejemplo del manual)
            self.dev.write(':CALC:AVER:TYPE MEAN')
            
            # 6. Obtener valor medio
            self.dev.write(':CALC:IMM?')
            resp_media = self.dev.read()
            try:
                valor_medio = float(resp_media)
            except Exception:
                valor_medio = None
            
            # 7. Desactivar estadísticas
            self.dev.write(':CALC:AVER:STAT OFF')
            
            return allan_deviation, valor_medio
            
        except Exception as e:
            print(f"Error al calcular ADEV y media: {str(e)}")
            return None, None

    def muestreo_adev_improved2(
        self,
        n_bloques=5,
        muestras_por_bloque=100,
        pacing_time_ms=20,
        intervalo_s=0.1,
        canal='A'
    ):
        """
        Realiza múltiples muestreos estadísticos de frecuencia y obtiene ADEV, media, SDEV, min y max para cada bloque.
        
        Nota sobre la adquisición de datos:
        Para cada bloque de muestreo:
        1. Se toman 'muestras_por_bloque' mediciones de frecuencia
        2. El instrumento calcula internamente:
           - ADEV: Un único valor de Allan deviation para todo el bloque
           - Media: Valor medio de todas las muestras del bloque
           - SDEV: Desviación estándar de todas las muestras del bloque
           - Min: Valor mínimo de todas las muestras del bloque
           - Max: Valor máximo de todas las muestras del bloque
        
        Ejemplo de adquisición para un bloque:
        Si muestras_por_bloque = 100:
        - Se toman 100 mediciones de frecuencia
        - Se obtiene 1 valor de ADEV para las 100 muestras
        - Se obtienen media, SDEV, min y max de las 100 muestras
        
        Parámetros:
            n_bloques (int): Número de bloques de muestreo a realizar
                - Rango: 1 a 1000
                - Default: 5
                - Descripción: Número de veces que se repetirá el muestreo completo
                - Ejemplo: Si n_bloques=3, se obtendrán 3 conjuntos de estadísticas
            
            muestras_por_bloque (int): Número de muestras por cada bloque
                - Rango: 2 a 1000000
                - Default: 100
                - Descripción: Número de mediciones que se realizarán en cada bloque
                - Nota: El número real puede ser mayor si no es múltiplo del trigger
                - Ejemplo: Si muestras_por_bloque=50, cada bloque tendrá 50 mediciones
            
            pacing_time_ms (int): Tiempo entre muestras en milisegundos
                - Rango: 1 a 1000000 ms
                - Default: 20
                - Descripción: Intervalo de tiempo entre mediciones consecutivas
                - Ejemplo: Si pacing_time_ms=20, habrá 20ms entre cada medición
            
            intervalo_s (float): Tiempo de apertura en segundos
                - Rango: 0.000001 a 1000 s
                - Default: 0.1
                - Descripción: Tiempo durante el cual se realiza cada medición individual
                - Ejemplo: Si intervalo_s=0.1, cada medición durará 0.1 segundos
                - Nota: Este es el tiempo de integración para cada medición
            
            canal (str o int): Canal de medida
                - Valores posibles: 'A', 'B', 1 o 2
                - Default: 'A'
                - Descripción: Especifica el canal a utilizar para la medición
                - 'A' o 1: Canal A
                - 'B' o 2: Canal B
        
        Comandos SCPI utilizados:
            1. :CALC:AVER:STAT ON
               - Descripción: Activa el cálculo estadístico
               - Efecto: Habilita el procesamiento estadístico de las muestras
            
            2. :CALC:TYPE ADEV
               - Descripción: Configura el tipo de cálculo como Allan deviation
               - Efecto: El instrumento calculará la Allan deviation de las muestras
            
            3. :CALC:AVER:COUN
               - Descripción: Configura el número de muestras para el cálculo
               - Efecto: Define cuántas mediciones se realizarán en cada bloque
            
            4. :TRIG:TIM
               - Descripción: Configura el intervalo entre muestras
               - Efecto: Establece el tiempo de espera entre mediciones consecutivas
            
            5. :SENS:ACQ:APER
               - Descripción: Configura el tiempo de apertura
               - Efecto: Define el tiempo de integración para cada medición individual
            
            6. :INIT
               - Descripción: Inicia la medición
               - Efecto: Comienza la adquisición de muestras
            
            7. :CALC:AVER:ALL?
               - Descripción: Obtiene media, SDEV, min y max
               - Retorna: String con los valores separados por comas
               - Formato: "media,sdev,min,max"
            
            8. :CALC:DATA?
               - Descripción: Obtiene el valor de ADEV
               - Retorna: String con los valores de ADEV
               - Formato: "tipo,valor" donde tipo es el tipo de cálculo (ADEV)
        
        Retorna:
            list: Lista de diccionarios con los resultados de cada bloque
                Cada diccionario contiene:
                - 'bloque': número de bloque (1 a n_bloques)
                - 'adev': valor de Allan deviation calculado para el bloque
                - 'media': valor medio de todas las muestras del bloque
                - 'sdev': desviación estándar de todas las muestras del bloque
                - 'min': valor mínimo de todas las muestras del bloque
                - 'max': valor máximo de todas las muestras del bloque
                Si ocurre algún error, retorna lista vacía
        
        Ejemplo de uso:
            resultados = cnt.muestreo_adev_improved2(
                n_bloques=3,
                muestras_por_bloque=50,
                pacing_time_ms=20,
                intervalo_s=0.1,
                canal='A'
            )
            # resultados será una lista de 3 diccionarios, uno por cada bloque
            # Cada diccionario tendrá los valores estadísticos de sus 50 muestras
        """
        try:
            # ========== SECCIÓN 1: Validación y selección de canal ==========
            canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
            ch = str(canal).upper()
            if ch not in canales:
                raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
            canal_cmd = canales[ch]
            
            resultados = []
            
            # ========== SECCIÓN 2: Bucle principal para cada bloque ==========
            for bloque in range(n_bloques):
                print(f"\nIniciando bloque {bloque + 1} de {n_bloques}")
                
                # 1. Resetear y limpiar
                self.dev.write('*RST')
                self.dev.write('*CLS')
                
                # 2. Configurar canal
                self.dev.write(f':CONF:FREQ {canal_cmd}')
                
                # 3. Configurar parámetros de medición
                self.dev.write(':CALC:AVER:STAT ON')
                self.dev.write(':CALC:TYPE ADEV')
                self.dev.write(f':CALC:AVER:COUN {muestras_por_bloque}')
                self.dev.write(f':TRIG:TIM {pacing_time_ms}ms')
                self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
                
                # 4. Iniciar medición
                self.dev.write(':INIT')
                
                # 5. Mostrar progreso
                muestra_anterior = 0
                while True:
                    self.dev.write(':CALC:AVER:COUN:CURR?')
                    muestra_actual = int(float(self.dev.read()))
                    
                    if muestra_actual != muestra_anterior:
                        print(f"\rMuestra {muestra_actual} de {muestras_por_bloque}", end='', flush=True)
                        muestra_anterior = muestra_actual
                    
                    if muestra_actual >= muestras_por_bloque:
                        print()  # Nueva línea al terminar
                        break
                        
                    time.sleep(0.1)
                
                # 6. Obtener estadísticas completas
                # :CALC:AVER:ALL? devuelve "media,sdev,min,max"
                self.dev.write(':CALC:AVER:ALL?')
                resp_stats = self.dev.read()
                try:
                    stats = [float(val) for val in resp_stats.strip().split(',') if val]
                    media, sdev, min_val, max_val = stats
                except Exception:
                    media = sdev = min_val = max_val = None
                
                # 7. Obtener ADEV
                # :CALC:DATA? devuelve "tipo,valor" donde tipo es ADEV
                self.dev.write(':CALC:DATA?')
                resp_adev = self.dev.read()
                try:
                    valores = [float(val) for val in resp_adev.strip().split(',') if val]
                    adev = valores[1] if len(valores) > 1 else None
                except Exception:
                    adev = None
                
                # 8. Almacenar resultados
                resultados.append({
                    'bloque': bloque + 1,
                    'adev': adev,
                    'media': media,
                    'sdev': sdev,
                    'min': min_val,
                    'max': max_val
                })
                
                # 9. Desactivar estadísticas
                self.dev.write(':CALC:AVER:STAT OFF')
            
            return resultados
            
        except Exception as e:
            print(f"Error en muestreo ADEV: {str(e)}")
            return []
        
        ##### importante probar que haria el pacing_time_ms "    self.dev.write(':TRIG:TIM 20ms')   en la funcion v31" 