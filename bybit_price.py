import requests

# Função para capturar o preço do BTC em tempo real
def get_btc_price_bybit():
    """
    Consulta o preço atual do BTC em USD na Bybit usando a API oficial.

    Returns:
        dict: Contém o preço do BTC e informações adicionais.
              Exemplo: {"price": 35000.5, "timestamp": "2025-01-01T12:00:00Z"}
        str: Mensagem de erro em caso de falha.
    """
    url = "https://api.bybit.com/v5/market/tickers"

    try:
        response = requests.get(url, params={"category": "spot", "symbol": "BTCUSDT"})
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
