from flask import Flask, render_template, request
import subprocess
import sqlite3
import pandas as pd  # Agrega esta línea
import plotly.express as px
import plotly.io as pio
import base64
from otro_codigo import user, texto, lang
from backup import user_b, texto_b, lang_b 
from datetime import datetime, time as datetime_time
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

# Variables para los scripts
call_script = 'otro_codigo.py'
call_script_backup = 'backup.py'



#---------------------------------------------#
def Guardar_en_DB_critical(texto):
    try:
        timestamp = datetime.now()
        month = timestamp.strftime('%B').lower()
        db_name = f'alertas_critical.db'

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Crear la tabla si no existe para el mes actual
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS alertas_critical_{month} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            fecha DATE,
            hora TIME
            )
        ''')

        # Insertar los datos en la tabla con la hora actual obtenida en el comando SQL
        cursor.execute(f'''
            INSERT INTO alertas_critical_{month} (texto, fecha, hora)
            VALUES (?, DATE('now'), TIME('now', 'localtime'))
        ''', (texto,))
        
        conn.commit()
        conn.close()
        print(f'Datos almacenados correctamente en la base de datos {db_name}.')
    except sqlite3.Error as e:
        print(f'Error al insertar datos en la base de datos: {str(e)}')

    print(f'Guardando en la base de datos (Critical): {texto}')


#----------------FUNCION ENCARGADA DE ALMACENAR LAS ALERTAS CUANDO YA SE NORMALIZARON----#

def Guardar_en_DB_Established(texto):
    try:
        month = datetime.now().strftime('%B').lower()
        db_name = f'alertas_established.db'

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Crear la tabla si no existe para el mes actual
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS alertas_established_{month} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            fecha DATE,
            hora TIME
            )
        ''')

        # Insertar los datos en la tabla con la hora actual obtenida en el comando SQL
        cursor.execute(f'''
            INSERT INTO alertas_established_{month} (texto, fecha, hora)
            VALUES (?, DATE('now'), TIME('now', 'localtime'))
        ''', (texto,))
        
        conn.commit()
        conn.close()
        print(f'Datos almacenados correctamente en la base de datos {db_name}.')
    except sqlite3.Error as e:
        print(f'Error al insertar datos en la base de datos: {str(e)}')

    print(f'Guardando en la base de datos (Established): {texto}')
#------------------------------------ENDPOINT QUE RECIBE POST------------------------------------#

@app.route('/realizar_llamada_texto', methods=['POST'])
def realizar_llamada_texto():
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data:
            texto_recibido = data['text']
            print("POST con alerta recibido. . .")

            hora_actual = datetime.now().time()
            hora_inicio_habil = datetime_time(8, 0)
            hora_fin_habil = datetime_time(10, 30)

            if hora_inicio_habil <= hora_actual <= hora_fin_habil:
                return 'Ignorando solicitud POST debido a horario hábil.'
            
            else:
                if "Critical" in texto_recibido:
                    Guardar_en_DB_critical(texto_recibido)
                    month = datetime.now().strftime('%B').lower()
                    db_name = f'alertas_established.db'

                    # Procesar el texto recibido para obtener la parte antes de 'está'
                    texto_alerta = texto_recibido.split(' está')[0]

                    print(f"Texto recibido guardado como texto_alerta: {texto_alerta}")
                    print("Esperando 1 minuto antes de analizar alertas...")
                    time.sleep(60)

                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()

                    # Obtener todas las alertas establecidas
                    cursor.execute(f"SELECT texto FROM alertas_established_{month}")
                    alertas = cursor.fetchall()

                    # Comprobar si alguna alerta coincide con el texto proporcionado
                    alerta_encontrada = False
                    for alerta in alertas:
                        if texto_alerta in alerta[0]:
                            alerta_encontrada = True
                            break

                    if alerta_encontrada:
                        print("¡Éxito! Se encontró una alerta con el texto proporcionado.")
                        # Aquí puedes añadir la lógica para la acción que desees realizar en este caso
                        return 'Proceso terminado por encontrar una alerta.'  # Esto detendrá la función aquí
                    else:
                        conn.close()
                        print("Error: No se encontraron coincidencias en la base de datos.")
                        print("Procediendo con la llamada. . .")
                        with open('backup.py', 'r') as archivo:
                            lineas = archivo.readlines()

                        with open('backup.py', 'w') as archivo:
                            for linea in lineas:
                                if 'texto_b = ' in linea:
                                    archivo.write(f'texto_b = "Alerta!, llamado de escalamiento. {texto_recibido}"  # Texto para la llamada\n')
                                else:
                                    archivo.write(linea)

                        with open('otro_codigo.py', 'r') as archivo:
                            lineas = archivo.readlines()

                        with open('otro_codigo.py', 'w') as archivo:
                            for linea in lineas:
                                if 'texto = ' in linea:
                                    archivo.write(f'texto = "{texto_recibido}"  # Texto para la llamada\n')
                                else:
                                    archivo.write(linea)

                        print("Realizando llamada. . .")
                        proceso = subprocess.Popen(['python3', 'otro_codigo.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        salida, error = proceso.communicate()

                        if error:
                            return f'Error al ejecutar otro_codigo.py: {error.decode()}'
                        else:
                            return f'Texto recibido y actualizado en otro_codigo.py. Ejecución exitosa.'
                        


                    
                
                else:
                    Guardar_en_DB_Established(texto_recibido)

                return 'Proceso completado'
        else:
            return 'Error: El campo "text" no está presente en los datos JSON de la solicitud.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)