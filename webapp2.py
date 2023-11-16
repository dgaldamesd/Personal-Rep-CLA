from flask import Flask, render_template, request
import subprocess
import sqlite3
import pandas as pd  # Agrega esta línea
import plotly.express as px
import plotly.io as pio
import base64

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
    return render_template('config_call.html')

# -----FUNCION QUE REEMPLAZA PARAMETROS DE USUARIO E IDIOMA EN SCRIPT DE BACKUP-----#
@app.route('/CONFIG_CALL_BACKUP', methods=['GET', 'POST'])
def CONFIG_CALL_BACKUP():
    if request.method == 'POST':
        user_call_backup = request.form['user']
        lang_call_backup = request.form['lang']
        modificar_parametros_backup(call_script_backup, user_call_backup, lang_call_backup)
        return "Parámetros actualizados con éxito."
    return render_template('config_call_backup.html')

def modificar_parametros(script, user_cb, lang_cb):
    try:
        with open(script, 'r') as file:
            lines = file.readlines()

        with open(script, 'w') as file:
            for line in lines:
                if 'user = ' in line:
                    file.write(f'    user = "{user_cb}"  # Número de usuario\n')
                elif 'lang = ' in line:
                    file.write(f'    lang = "{lang_cb}"  # Idioma\n')
                else:
                    file.write(line)

        return "Parámetros actualizados con éxito."
    except Exception as e:
        return f"Error al actualizar parámetros: {str(e)}"

# -----FUNCION QUE REEMPLAZA PARAMETROS DE USUARIO E IDIOMA EN SCRIPT DE BACKUP-----#
def modificar_parametros_backup(script, user_c, lang_c):
    with open(script, 'r') as file:
        lines = file.readlines()

    with open(script, 'w') as file:
        for line in lines:
            if 'user =' in line:  # Asegúrate de que estás buscando la línea correcta
                file.write(f'    user = "{user_c}"  # Número de usuario\n')
            elif 'lang =' in line:  # Asegúrate de que estás buscando la línea correcta
                file.write(f'    lang = "{lang_c}"  # Idioma\n')
            else:
                file.write(line)

# ---------------------------------------FUNCION QUE RECIBE SOLICITUD PARA REALIZAR LLAMADA-----------------------------------------#
@app.route('/realizar_llamada_texto', methods=['POST'])
def realizar_llamada_texto():
    if request.method == 'POST':
        data = request.get_json()
        if 'text' in data:
            texto_recibido = data['text']

            with open('backup.py', 'r') as archivo:
                lineas = archivo.readlines()

            with open('backup.py', 'w') as archivo:
                for linea in lineas:
                    if 'texto = ' in linea:
                        archivo.write(f'    texto = "Alerta!, llamado de escalamiento. {texto_recibido}"  # Texto para la llamada\n')
                    else:
                        archivo.write(linea)

            with open('otro_codigo.py', 'r') as archivo:
                lineas = archivo.readlines()

            with open('otro_codigo.py', 'w') as archivo:
                for linea in lineas:
                    if 'texto = ' in linea:
                        archivo.write(f'    texto = "{texto_recibido}"  # Texto para la llamada\n')
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
    with app.app_context():
        app.run(host='0.0.0.0', port=8080, debug=True)
