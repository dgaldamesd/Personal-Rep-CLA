from flask import Flask, render_template, request
import subprocess
import sqlite3

import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)

@app.route('/')
def mostrar_llamadas():
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM llamadas ORDER BY id DESC")  # Seleccionar solo la columna 'contestada'
    llamadas = cursor.fetchall()
    conn.close()

    print(llamadas)

    # Procesamiento de los datos para el gráfico
    llamadas_contestadas = sum(1 for llamada in llamadas if "Call answered and ended by the user" in llamada[0])
    llamadas_no_contestadas = sum(1 for llamada in llamadas if "Call Rejected by user" in llamada[0])

    # Crear el gráfico
    labels = ['Contestadas', 'No Contestadas']
    cantidad_llamadas = [llamadas_contestadas, llamadas_no_contestadas]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, cantidad_llamadas, color=['green', 'red'])
    plt.title('Cantidad de llamadas contestadas y no contestadas')

    # Convertir el gráfico a una imagen base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode()

    return render_template('alertas.html', llamadas=llamadas, grafico_base64=grafico_base64)

if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', port=8080, debug=True)