from flask import Flask, render_template, request
import sqlite3
import pandas as pd  # Agrega esta línea
import plotly.express as px
import plotly.io as pio
import base64


app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
