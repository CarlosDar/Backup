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
                plt.gca().text(0.02, 0.98, texto_stats, fontsize=10,
                               ha='left', va='top', transform=plt.gca().transAxes,
                               bbox=dict(facecolor='white', alpha=0.4, edgecolor='none'))
                plt.tight_layout()
                plt.show()
    
            return frecuencias, timestamps, delta_tiempos, allan_deviations, taus
    
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None, None, None
        
        
#JOAN 3 PROBAMOS OTRO METODO Usar el modo de medición con "Sample Timer"
# 
#   Está tiene tiempos y tiempos relativos y GRAFICAR FREQUENCIA VS TIEMPO
# Añadido que devuelva los Allan deviation
# Graficar el ALLAN DEVIATION EN FUNCION DE TAUS

    
    def medir_n_muestras_equidistantesV5(
            self,
            n_muestras=10,
            intervalo_s=0.1,
            canal='A',
            graficarFT=True,
            graficarDevTau=True,
            exportar_excel=True
        ):
        """
        Versión con opción de exportar a Excel (CSV) los datos crudos y las Allan deviations (con 2 decimales).
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
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
        self.dev.write(f'ARM:COUN {n_muestras}')
        self.dev.write('FORM:TINF ON')
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición ==========
        self.dev.write('INIT')
        tiempo_espera = intervalo_s * n_muestras * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 4: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
    
        try:
            valores = [float(val) for val in data.strip().split(',') if val]
            frecuencias = np.array(valores[::2])
            timestamps = np.array(valores[1::2])
            delta_tiempos = timestamps - timestamps[0]
    
            # ========== SECCIÓN 5: Cálculo de Allan Deviation para diferentes Taus ==========
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
    
            # ========== SECCIÓN 6: Exportar a Excel/CSV si se solicita ==========
            if exportar_excel:
                import pandas as pd
                from datetime import datetime
    
                fecha_hora = datetime.now().strftime("%S_%M_%H_%d_%m_%Y")
                # Formatear arrays a 2 decimales antes de crear los DataFrame
                raw_data = {
                    "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                    "Frecuencia [Hz]": np.round(frecuencias, 2),
                    "Timestamp [s]": np.round(timestamps, 2),
                    "Delta_tiempo [s]": np.round(delta_tiempos, 2)
                }
                df_raw = pd.DataFrame(raw_data)
                nombre_raw = f"RawDataFreqYTiempo_{fecha_hora}.csv"
                df_raw.to_csv(nombre_raw, index=False, float_format="%.2f")
                print(f"Archivo de datos crudos guardado como: {nombre_raw}")
    
                allan_data = {
                    "DATO": [f"DATO{i}" for i in range(len(allan_deviations))],
                    "AllanDeviation [Hz]": np.round(allan_deviations, 2),
                    "Tau [s]": np.round(taus, 2)
                }
                df_allan = pd.DataFrame(allan_data)
                nombre_allan = f"AllanDeviationyTaus_{fecha_hora}.csv"
                df_allan.to_csv(nombre_allan, index=False, float_format="%.2f")
                print(f"Archivo Allan Deviation guardado como: {nombre_allan}")
    
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
                # Estadísticas
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
                self.dev.write('DISP:ENAB ON')             # Apaga display para máxima velocidad
            return frecuencias, timestamps, delta_tiempos, allan_deviations, taus
            
        except Exception as e:
            print(f"Error procesando los datos: {str(e)}")
            return None, None, None, None, None

    
# VERSION POSIBLEMENTE DEFINITIVA

    def medir_n_muestras_equidistantesV6(
            self,
            n_muestras=100,
            intervalo_s=0.2,
            canal='A',
            graficarFT=True,
            graficarDevTau=True,
            exportar_excel=True
        ):
        """
        Versión definitiva: Exporta a un solo Excel (.xlsx) dos hojas, una para datos crudos frecuencia/tiempo y otra para Allan deviation/Tau.
        """
        import time
        import numpy as np
    
        # ========== SECCIÓN 1: Validación y selección de canal ==========
        canales = {'A': '@1', 'B': '@2', '1': '@1', '2': '@2'}
        ch = str(canal).upper()
        if ch not in canales:
            raise ValueError("El canal debe ser 'A', 'B', 1 o 2")
        canal_cmd = canales[ch]
    
        # ========== SECCIÓN 2: Configuración del instrumento ==========
        self.dev.write('*RST')
        self.dev.write("*CLS")
        self.dev.write('CAL:INT:AUTO OFF')
        self.dev.write('DISP:ENAB OFF')
        self.dev.write(f'CONF:FREQ {canal_cmd}')
        self.dev.write(f'SENS:ACQ:APER {intervalo_s}')
        self.dev.write(f'ARM:COUN {n_muestras}')
        self.dev.write('FORM:TINF ON')
    
    
        # ========== SECCIÓN 3: Lanzamiento de adquisición ==========
        self.dev.write('INIT')
        tiempo_espera = intervalo_s * n_muestras * 1.1
        time.sleep(tiempo_espera)
    
        # ========== SECCIÓN 4: Recuperación y procesamiento de los datos ==========
        self.dev.write('FETC:ARR? MAX')
        data = self.dev.read()
    
        try:
            valores = [float(val) for val in data.strip().split(',') if val]
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
    
                # Datos crudos
                raw_data = {
                    "Muestra": [f"Muestra{i}" for i in range(len(frecuencias))],
                    "Frecuencia [Hz]": np.round(frecuencias, 6),
                    "Timestamp [s]": np.round(timestamps, 6),
                    "Delta_tiempo [s]": np.round(delta_tiempos, 6)
                }
                df_raw = pd.DataFrame(raw_data)
    
                # Allan deviation
                allan_data = {
                    "DATO": [f"DATO{i}" for i in range(len(allan_deviations))],
                    "AllanDeviation [Hz]": np.round(allan_deviations, 6),
                    "Tau [s]": np.round(taus, 6)
                }
                df_allan = pd.DataFrame(allan_data)
    
                # Guardar ambos DataFrames en un único Excel (dos hojas)
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

    def leer_adev_cnt91_improved2(self):
        """
        Versión mejorada 2 de la función para extraer la Allan deviation (ADEV) del CNT-91.
        Sigue la estructura correcta de comandos SCPI para cálculos estadísticos.
        
        Retorna:
            Allan_Deviation: float
                Allan deviation interna (o None si ocurre algún error)
        """
        try:
            # 1. Resetear el instrumento para asegurar estado limpio
            self.dev.write('*RST')
            # 2. Limpiar errores previos
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