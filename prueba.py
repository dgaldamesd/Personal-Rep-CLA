from flask import Flask, render_template
from otro_codigo import user, texto, lang  # Importa las variables desde otro_codigo.py

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mostrar_datos_llamada():
    datos = {
        'user': user,
        'texto': texto,
        'lang': lang
    }
    return render_template('index.html', datos=datos)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
