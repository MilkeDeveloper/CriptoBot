import requests

# Função para capturar o preço do USDT/BRL em tempo real
def get_usd_brl_price_bybit():
    """
    Consulta o preço atual do BTC em USD na Bybit usando a API oficial.

    Returns:
        dict: Contém o preço do BTC e demais dados.
        str: Mensagem de erro em caso de falha.
    """
    url = "https://api.bybit.com/v5/market/tickers"

    try:
        response = requests.get(url, params={"category": "spot", "symbol": "USDTBRL"})
        response.raise_for_status()  # Lança um erro para códigos HTTP >= 400

        data = response.json()


        if "result" in data and data["result"]["list"]:
            ticker = data["result"]["list"][0]  # O primeiro item contém o BTCUSDT
            price = float(ticker["lastPrice"])  # Preço atual do BTC

            return price  # Retorna o preço atual
        else:
            return "Erro: Dados do BTC não encontrados na resposta da API."
    except requests.exceptions.RequestException as e:
        return f"Erro ao conectar à API da Bybit: {e}"