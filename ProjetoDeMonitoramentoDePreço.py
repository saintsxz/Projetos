import json 
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
def pegar_preco(url):
    options = webdriver.ChromeOptions()

    options.add_argument(
        r"user-data-dir=C:\selenium-profile"
    )

    options.add_argument("--profile-directory=Default")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument("--start-maximized")

    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "andes-money-amount__fraction")
        )
    )
    try:
        botao = driver.find_element(By.TAG_NAME, "button")
        botao.click()

        time.sleep(3)
    except:
        pass
    try:
        container = driver.find_element(
            By.CSS_SELECTOR,
            ".ui-pdp-price__second-line"
        )

        inteiro = container.find_element(
            By.CLASS_NAME,
            "andes-money-amount__fraction"
        ).text

        try:
            centavos = container.find_element(
                By.CLASS_NAME,
                "andes-money-amount__cents"
            ).text
        except:
            centavos = "00"

        preco = float(f"{inteiro}.{centavos}")

        print(preco)

        return preco
    except Exception as e:
        print(e)
        return None
    finally:
        driver.quit()
def pegar_ultimo_preco():
    try:
        with open("Lista de preço.jsonl", "r")as f:
            linhas= f.readlines()

            if linhas:
                ultimo = json.loads(linhas[-1])
                return ultimo["preco"]
    except (FileNotFoundError, json.JSONDecodeError):
        return None
def alerta(preco_atual, preco_antigo):
    if preco_atual < preco_antigo:
        diferenca = preco_antigo - preco_atual
        print("🚨 ALERTA: O preço caiu!")
        print(f"💰 Caiu R$ {diferenca:.2f}")
def enviar_email(preco_atual, preco_antigo):
    senha = os.getenv("email_senha")
    if not senha:
        print("Senha de email não encontrada")
        return
    msg = EmailMessage()
    email = os.getenv("email_remetente")
    msg["From"] = email
    msg["To"] = email
    if preco_antigo > preco_atual:
        msg["Subject"] = "🚨 Preço caiu!"
        msg.set_content(f"""
O preço caiu!!!
De: R${preco_antigo}
Para: R${preco_atual}
""")
    elif preco_antigo < preco_atual:
        msg["Subject"] = "📈 Preço subiu!"
        msg.set_content(f"""
O preço subiu!!!
De: R${preco_antigo}
Para: R${preco_atual}
""")
    else:
        msg["Subject"] = "➖ Sem alteração"
        msg.set_content(f"""
O preço não mudou.
Preço atual: R${preco_atual}
""")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email, senha)
        smtp.send_message(msg)
url = "https://www.mercadolivre.com.br/suporte-de-monitor-17-a-35-braco-articulado-com-pisto-a-gas-north-bayou-nb-f150/p/MLB18628313"

preco_atual = pegar_preco(url)
preco_antigo = pegar_ultimo_preco()

if preco_atual is None:
    print("Erro ao pegar preço")
    exit()

print(f"Preço atual: R$ {preco_atual}")

if preco_antigo is not None:
    print(f"Preço anterior: R$ {preco_antigo}")

    if preco_atual < preco_antigo:
        alerta(preco_atual, preco_antigo)
        enviar_email(preco_atual, preco_antigo)
        print("🔥 O preço caiu!")
    elif preco_atual > preco_antigo:
        enviar_email(preco_atual, preco_antigo)
        print("📈 O preço subiu!")
    else:
        enviar_email(preco_atual, preco_antigo)
        print("➖ Sem alteração")
else:
    print("📌 Primeiro registro")
data = {
        "produto": "Suporte Monitor",
        "preco": preco_atual,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
with open("Lista de preço.jsonl", "a") as f:
    f.write(json.dumps(data) + "\n")
