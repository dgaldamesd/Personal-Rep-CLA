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

# ---------------------------------------PAGINA INICIO-----------------------------------------#
@app.route('/')
def LOGIN():
    return render_template('login.html')

# ---------------------------------------PAGINA INICIO-----------------------------------------#
@app.route('/INICIO')
def INICIO():
    return render_template('inicio.html')

# ---------------------------------------PAGINA ESTADISTICAS-----------------------------------------#
def obtener_datos(tabla):
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT Respuesta, COUNT(*) FROM {tabla} GROUP BY Respuesta")
    resultados = cursor.fetchall()

    conn.close()

    return resultados

def generar_grafico(datos):
    df = pd.DataFrame(datos, columns=['Respuesta', 'Cantidad'])

    fig = px.bar(df, x='Respuesta', y='Cantidad', color='Respuesta',
                 labels={'Respuesta': 'Respuesta de llamadas', 'Cantidad': 'Cantidad'},
                 title='Estadísticas de llamadas')
    
    return pio.to_html(fig, full_html=False)

@app.route('/ESTADISTICAS', methods=['GET', 'POST'])
def mostrar_grafico():
    tabla_seleccionada = 'llamadas_november'

    if request.method == 'POST':
        tabla_seleccionada = request.form['tabla']

    datos = obtener_datos(tabla_seleccionada)
    grafico_html = generar_grafico(datos)

    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas_disponibles = [row[0] for row in cursor.fetchall()]
    conn.close()

    return render_template('grafico.html', tabla_seleccionada=tabla_seleccionada, grafico_html=grafico_html, tablas_disponibles=tablas_disponibles)


# ---------------------------------------PAGINA ALERTAS-----------------------------------------#
@app.route('/ALERTAS', methods=['GET', 'POST'])
def mostrar_llamadas():
    tablas = get_lista_tablas()

    if request.method == 'POST':
        tabla_seleccionada = request.form['tabla']
        llamadas = obtener_llamadas(tabla_seleccionada)
        return render_template('alertas.html', llamadas=llamadas, tablas=tablas, tabla_seleccionada=tabla_seleccionada)

    # Si es una solicitud GET, mostrar las llamadas de la tabla por defecto
    tabla_default = 'llamadas_november'  # Cambia esto según tu necesidad
    llamadas = obtener_llamadas(tabla_default)
    return render_template('alertas.html', llamadas=llamadas, tablas=tablas, tabla_seleccionada=tabla_default)


def obtener_llamadas(tabla):
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabla} ORDER BY id DESC")
    llamadas = cursor.fetchall()
    conn.close()
    return llamadas

def get_lista_tablas():
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'llamadas_%'")
    tablas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tablas

# ---------------------------------------PAGINA CONFIGURACIONES-----------------------------------------#

@app.route('/CONFIG', methods=['GET', 'POST'])
def CONFIG_MAIN():
    return render_template('config_main.html')

# -----FUNCION QUE REEMPLAZA PARAMETROS DE USUARIO E IDIOMA EN SCRIPT-----#


@app.route('/CONFIG_CALL', methods=['GET', 'POST'])
def CONFIG_CALL():
    if request.method == 'POST':
        user_call = request.form['user']
        lang_call = request.form['lang']
        modificar_parametros(call_script, user_call, lang_call)
        return "Parámetros actualizados con éxito."
    datos = {
        'user': user,
        'texto': texto,
        'lang': lang
    }
    return render_template('config_call.html', datos=datos)

def modificar_parametros(script, user_cb, lang_cb):
    try:
        with open(script, 'r') as file:
            lines = file.readlines()

        with open(script, 'w') as file:
            for line in lines:
                if 'user = ' in line:
                    file.write(f'user = "{user_cb}"  # Número de usuario\n')
                elif 'lang = ' in line:
                    file.write(f'lang = "{lang_cb}"  # Idioma\n')
                else:
                    file.write(line)

        return "Parámetros actualizados con éxito."
    except Exception as e:
        return f"Error al actualizar parámetros: {str(e)}"

# ----------------------FUNCION QUE REEMPLAZA PARAMETROS DE USUARIO E IDIOMA EN SCRIPT DE BACKUP----------------------------#
@app.route('/CONFIG_CALL_BACKUP', methods=['GET', 'POST'])
def CONFIG_CALL_BACKUP():
    if request.method == 'POST':
        user_call_backup = request.form['user']
        lang_call_backup = request.form['lang']
        modificar_parametros_backup(call_script_backup, user_call_backup, lang_call_backup)
        return "Parámetros actualizados con éxito."
    datos_b = {
        'user': user_b,
        'texto': texto_b,
        'lang': lang_b
    }
    return render_template('config_call_backup.html', datos=datos_b)


def modificar_parametros_backup(call_script_backup, user_b, lang_b):
    try:
        with open(call_script_backup, 'r') as file:
            lines = file.readlines()

        with open(call_script_backup, 'w') as file:
            for line in lines:
                if 'user_b = ' in line:
                    file.write(f'user_b = "{user_b}"  # Número de usuario\n')
                elif 'lang_b = ' in line:
                    file.write(f'lang_b = "{lang_b}"  # Idioma\n')
                else:
                    file.write(line)

        return "Parámetros actualizados con éxito."
    except Exception as e:
        return f"Error al actualizar parámetros: {str(e)}"


# ---------------------------------------FUNCION QUE RECIBE SOLICITUD PARA REALIZAR LLAMADA-----------------------------------------#
import re

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
            origen TEXT,  -- Nueva columna para almacenar el origen
            fecha DATE,
            hora TIME
            )
        ''')

        # Extraer el texto entre "de:" y la coma ","
        origen_match = re.search(r'de:\s([^,]+)', texto)
        origen = origen_match.group(1) if origen_match else ''  # Obtener el texto entre "de:" y la coma ","

        # Insertar los datos en la tabla con la hora actual obtenida en el comando SQL
        cursor.execute(f'''
            INSERT INTO alertas_critical_{month} (texto, origen, fecha, hora)
            VALUES (?, ?, DATE('now'), TIME('now', 'localtime'))
        ''', (texto, origen.strip()))  # Eliminar espacios adicionales alrededor del origen
        
        conn.commit()
        conn.close()
        print(f'Datos almacenados correctamente en la base de datos {db_name}.')
    except sqlite3.Error as e:
        print(f'Error al insertar datos en la base de datos: {str(e)}')

    print(f'Guardando en la base de datos (Critical): {texto}')




#--------------------------------------#
def Guardar_en_DB_Established(texto):
    try:
        month = datetime.now().strftime('%B').lower()
        db_name = f'alertas_established.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS alertas_established_{month} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT,
            fecha DATE,
            hora TIME
            )
        ''')
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






import sqlite3
from datetime import datetime

def verificar_alertas():
    try:
        timestamp = datetime.now()
        month = timestamp.strftime('%B').lower()
        db_name = 'alertas_critical.db'

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Obtener las últimas 5 alertas del mes actual
        cursor.execute(f'''
            SELECT origen, COUNT(*) AS cantidad
            FROM (
                SELECT origen FROM alertas_critical_{month}
                ORDER BY id DESC LIMIT 5
            )
            GROUP BY origen
        ''')

        alertas = cursor.fetchall()

        # Verificar si hay más de 1 alerta con el mismo origen
        for alerta in alertas:
            if alerta[1] > 1:
                print(f"Existen múltiples alertas con el origen '{alerta[0]}' en el mes actual. Deteniendo la función.")
                conn.close()
                return False
        
        conn.close()
        return True  # Continuar con la siguiente función si no hay múltiples alertas con el mismo origen

    except sqlite3.Error as e:
        print(f'Error al realizar la verificación: {str(e)}')
        return False

# Llamar a la función para verificar antes de continuar con la siguiente acción
if verificar_alertas():
    # Continuar con la siguiente acción
    print("No hay múltiples alertas con el mismo origen en el mes actual. Continuando con la siguiente acción.")
else:
    # Detener la siguiente acción debido a múltiples alertas con el mismo origen
    print("Deteniendo la siguiente acción debido a múltiples alertas con el mismo origen en el mes actual.")



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
                    if not verificar_alertas():
                        return 'Deteniendo la siguiente acción debido a múltiples alertas con el mismo origen en el mes actual.'
                    month = datetime.now().strftime('%B').lower()
                    db_name = f'alertas_established.db'
                    texto_alerta = texto_recibido.split(' está')[0]
                    print(f"Texto recibido guardado como texto_alerta: {texto_alerta}")
                    print("Esperando 1 minuto antes de analizar alertas...")
                    time.sleep(60)
                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT texto FROM alertas_established_{month}")
                    alertas = cursor.fetchall()
                    alerta_encontrada = False
                    for alerta in alertas:
                        if texto_alerta in alerta[0]:
                            alerta_encontrada = True
                            break
                    if alerta_encontrada:
                        print("¡Éxito! Se encontró una alerta con el texto proporcionado.")
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
    



