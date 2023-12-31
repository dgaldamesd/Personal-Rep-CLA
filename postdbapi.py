import requests
import re
import sqlite3
from datetime import datetime
import time
import subprocess

def realizar_llamada(user, text, lang):
    url = f"http://api.callmebot.com/start.php?source=web&user={user}&text={text}&lang={lang}"
    rechazos = 0
    
    while rechazos < 2:  # Intentar máximo 2 veces
        response = requests.get(url)

        if response.status_code == 200:
            response_content = response.text
            print(response_content)  # Imprimir la respuesta completa para su análisis

            result_index = response_content.find("Result:")
            if result_index != -1:
                start_index = result_index + len("Result:")
                end_index = response_content.find("<br>", start_index)
                result_text = response_content[start_index:end_index].strip()
                result_text = re.sub(r"</?[^>]+>", "", result_text)

                guardar_en_base_de_datos(user, text, result_text, datetime.now())  # Guardar también la hora de ejecución

                if result_text == "Call Rejected by user":
                    print("Llamada rechazada por el usuario.")
                    rechazos += 1
                    if rechazos < 2:
                        print(f"Esperando 2 minutos para volver a llamar (Intento {rechazos + 1}/2)...")
                        time.sleep(120)  # Esperar 2 minutos antes de volver a llamar
                else:
                    return result_text
            else:
                return "No se encontró la sección con 'Result:' en la respuesta"
        else:
            return f"Hubo un error al iniciar la llamada. Código de estado: {response.status_code}"

        # Si la llamada fue rechazada, se espera 2 minutos y se vuelve a llamar
        time.sleep(1)  # Evitar hacer peticiones muy rápido, esperar un segundo antes de reintentar

    # Si hay dos rechazos, ejecutar el script de backup
    if rechazos == 2:
        print("Dos intentos de llamada rechazados. Ejecutando el script de backup...")
        try:
            subprocess.run(["python3", "backup.py"])
        except Exception as e:
            print(f"No se pudo ejecutar el script de backup: {e}")

def guardar_en_base_de_datos(user, text, result, timestamp):
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()

    month = timestamp.strftime('%B').lower()  # Convertir el nombre del mes a minúsculas

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS llamadas_{month} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destinatario TEXT,
            mensaje TEXT,
            respuesta TEXT,
            timestamp DATETIME
        )
    ''')

    cursor.execute(f'''
        INSERT INTO llamadas_{month} (destinatario, mensaje, respuesta, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user, text, result, timestamp))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    user = "+56999641574"
    text = "ESTO ES UNA LLAMADA DE PRUEBA PARA PROBAR EL ORDEN DE LA BASE DE DATOS"
    lang = "es-ES-Standard-A"

    realizar_llamada(user, text, lang)
