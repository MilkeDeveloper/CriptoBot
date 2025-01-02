import time
import hashlib
import hmac
import requests
import os
from dotenv import load_dotenv

load_dotenv()



# Configurações
api_key = os.getenv('API_BYBIT_KEY')
api_secret = os.getenv('API_BYBIT_SECRET')
base_url = "https://api.bybit.com"

# Endpoint e parâmetros
endpoint = "/v5/market/tickers"
params = {
    "category": "spot",
    "symbol": "BTCUSDT",
}

# Gerar timestamp
timestamp = str(int(time.time() * 1000))

# Gerar a assinatura
query_string = "&".join(f"{key}={value}" for key, value in params.items())
signature_payload = f"{timestamp}5000{query_string}".encode()
signature = hmac.new(api_secret.encode(), signature_payload, hashlib.sha256).hexdigest()

# Cabeçalhos
headers = {
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-SIGN": signature,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": "5000",
}

# Configuração do proxy
proxies = {
    "http": "http://38.9.141.250:10609",  # Para conexões HTTP
    "https": "http://38.9.141.250:10609"  # Para conexões HTTPS
}

# Função para capturar o preço do BTC em tempo real
def get_btc_price_bybit():
    """
    Consulta o preço atual do BTC em USD na Bybit usando a API oficial.

    Returns:
        dict: Contém o preço do BTC e informações adicionais.
              Exemplo: {"price": 35000.5, "timestamp": "2025-01-01T12:00:00Z"}
        str: Mensagem de erro em caso de falha.
    """


    try:

        #p_response = requests.get("https://api64.ipify.org?format=json", proxies=proxies, timeout=10)
        #print("Resposta do Proxy:", p_response.text)

        response = requests.get(base_url + endpoint, headers=headers, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos HTTP >= 400

        data = response.json()

        if "result" in data and data["result"]["list"]:
            ticker = data["result"]["list"][0]  # O primeiro item contém o BTCUSDT
            price = float(ticker["lastPrice"])  # Preço atual do BTC

            return price
        else:
            return "Erro: Dados do BTC não encontrados na resposta da API."
    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar à API da Bybit: {e}"
