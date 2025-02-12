from flask import Flask, request, jsonify
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

def hacer_pregunta(pregunta):
    """Envia una pregunta a Copilot y obtiene la respuesta completa."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  
    options.add_argument("--disable-blink-features=AutomationControlled")  
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://copilot.microsoft.com/chats/LG18W2X4gD7MdzugnJcdB")

    wait = WebDriverWait(driver, 15)

    try:
        input_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id='userInput']")))
        input_box.click()
        time.sleep(1)

        for letra in pregunta:
            input_box.send_keys(letra)
            time.sleep(random.uniform(0.05, 0.15))

        input_box.send_keys(Keys.ENTER)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.space-y-3.break-words")))
        time.sleep(5)

        respuesta_anterior = ""
        intentos = 0
        while intentos < 5:
            respuesta_elementos = driver.find_elements(By.CSS_SELECTOR, "div.space-y-3.break-words p")
            respuesta_completa = " ".join([element.text for element in respuesta_elementos])

            if respuesta_completa == respuesta_anterior:
                break  

            respuesta_anterior = respuesta_completa
            time.sleep(3)
            intentos += 1

        respuesta_final = respuesta_completa.replace(" 1", "").replace(" 2", "").replace(" 3", "").replace(" .", ".")
        driver.quit()

        return respuesta_final.strip() if respuesta_final else "No se encontró respuesta."

    except Exception as e:
        driver.quit()
        return f"Error obteniendo respuesta: {str(e)}"

@app.route("/preguntar", methods=["POST"])
def preguntar():
    data = request.json
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "Falta la pregunta"}), 400

    respuesta = hacer_pregunta(pregunta)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)