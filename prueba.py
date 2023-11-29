from flask import Flask, render_template, request
import subprocess
import sqlite3
import pandas as pd  # Agrega esta línea
import plotly.express as px
import plotly.io as pio
import base64
from otro_codigo import user, texto, lang
from backup import user_b, texto_b, lang_b 
from datetime import datetime, time
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)


def guardar_en_base_de_datos(texto_recibido):
    try:
        conn = sqlite3.connect('alertas.db')
        cursor = conn.cursor()

        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas_nov (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            fecha DATE,
            hora TIME
            )
        ''')

        # Insertar los datos en la tabla
        cursor.execute('''
            INSERT INTO alertas_nov (texto, fecha, hora)
            VALUES (?, DATE('now'), TIME('now'))
        ''', (texto_recibido,))
        conn.commit()
        conn.close()
        print('Datos almacenados correctamente en la base de datos.')
        return 'Datos almacenados correctamente en la base de datos.'
    except sqlite3.Error as e:
        print(f'Error al insertar datos en la base de datos: {str(e)}')
        return f'Error al insertar datos en la base de datos: {str(e)}'



@app.route('/realizar_llamada_texto', methods=['POST'])  # Define una ruta para manejar solicitudes POST
def realizar_llamada_texto():
    if request.method == 'POST':  # Verifica si es una solicitud POST
        data = request.get_json()  # Obtiene los datos JSON de la solicitud
        
        if 'text' in data:  # Verifica si el campo 'text' está presente en los datos
            texto_recibido = data['text']  # Obtiene el texto de la solicitud

            hora_actual = datetime.now().time()  # Obtiene la hora actual
            hora_inicio_habil = time(12, 0)  # Establece el horario hábil (12:00)
            hora_fin_habil = time(14, 30)  # Establece el horario hábil (14:30)

            if hora_inicio_habil <= hora_actual <= hora_fin_habil:  # Verifica si estamos en horario hábil
                return 'Ignorando solicitud POST debido a horario hábil.'  # Si es así, ignora la solicitud
            
            else:
                try:
                    guardar_en_base_de_datos(texto_recibido)  # Llama a la función para guardar en la base de datos
                except Exception as e:
                    return f'Error al guardar en la base de datos: {str(e)}'  # Captura y muestra errores al guardar

                time.sleep(120)
               

                with open('backup.py', 'r') as archivo:  # Abre el archivo 'backup.py' en modo lectura
                    lineas = archivo.readlines()  # Lee las líneas del archivo

                with open('backup.py', 'w') as archivo:  # Abre el archivo 'backup.py' en modo escritura
                    for linea in lineas:  # Itera sobre cada línea del archivo
                        if 'texto_b = ' in linea:  # Busca una línea específica
                            archivo.write(f'texto_b = "Alerta!, llamado de escalamiento. {texto_recibido}"  # Texto para la llamada\n')
                        else:
                            archivo.write(linea)  # Escribe la línea original si no se cumple la condición

                with open('otro_codigo.py', 'r') as archivo:  # Abre el archivo 'otro_codigo.py' en modo lectura
                    lineas = archivo.readlines()  # Lee las líneas del archivo

                with open('otro_codigo.py', 'w') as archivo:  # Abre el archivo 'otro_codigo.py' en modo escritura
                    for linea in lineas:  # Itera sobre cada línea del archivo
                        if 'texto = ' in linea:  # Busca una línea específica
                            archivo.write(f'texto = "{texto_recibido}"  # Texto para la llamada\n')
                        else:
                            archivo.write(linea)  # Escribe la línea original si no se cumple la condición

                proceso = subprocess.Popen(['python3', 'otro_codigo.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Ejecuta un proceso en Python con 'otro_codigo.py'
                salida, error = proceso.communicate()  # Obtiene la salida y el error del proceso ejecutado

                if error:  # Verifica si hay algún error
                    return f'Error al ejecutar otro_codigo.py: {error.decode()}'  # Muestra el error si ocurre alguno
                else:
                    return f'Texto recibido y actualizado en otro_codigo.py. Ejecución exitosa.'  # Mensaje de éxito si no hay errores

    return 'Error: no se proporcionó el campo "text" en la solicitud.'  # Mensaje si no se proporcionó 'text' en la solicitud
