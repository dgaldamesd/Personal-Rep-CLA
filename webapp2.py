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




@app.route('/realizar_llamada_texto', methods=['POST'])
def realizar_llamada_texto():
    if request.method == 'POST':  # Verifica si es una solicitud POST
        data = request.get_json()  # Obtiene los datos JSON de la solicitud
        if 'text' in data:  # Verifica si el campo 'text' está presente en los datos
            texto_recibido = data['text']  # Obtiene el texto de la solicitud

            hora_actual = datetime.now().time()  # Obtiene la hora actual
            hora_inicio_habil = time(12, 0)  # Establece el horario hábil (10:00)
            hora_fin_habil = time(14, 30)  # Establece el horario hábil (14:30)

            if hora_inicio_habil <= hora_actual <= hora_fin_habil:  # Verifica si estamos en horario hábil
                return 'Ignorando solicitud POST debido a horario hábil.'  # Si es así, ignora la solicitud
            
            else:
                try:
                    guardar_en_base_de_datos(texto_recibido)
                except Exception as e:
                    return f'Error al guardar en la base de datos: {str(e)}'

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

                proceso = subprocess.Popen(['python3', 'otro_codigo.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                salida, error = proceso.communicate()

                if error:
                    return f'Error al ejecutar otro_codigo.py: {error.decode()}'
                else:
                    return f'Texto recibido y actualizado en otro_codigo.py. Ejecución exitosa.'
    return 'Error: no se proporcionó el campo "text" en la solicitud.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)