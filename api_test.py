# test_bybit_price.py
import time
import pytz
import requests
import os
from datetime import datetime
from bybit_price import get_btc_price_bybit
from coinext_price import get_btc_price_coinext
from dotenv import load_dotenv

load_dotenv()

telegram_api_key = os.getenv('TELEGRAM_API_TOKEN')
telegram_chat_id = os.getenv('CHAT_ID')

minimum_percentage = 1.0
delay_time = 60

# Função para testar a captura dos dados na Bybit
def test_btc_price():
    btc_data = get_btc_price_bybit()

    print(f"Preço do BTC na Bybit: ${btc_data}")

    return btc_data

# Função para testar a captura dos dados na Coinext
def test_btc_price_coinext():
    btc_data = get_btc_price_coinext()

    print(f"Preço do BTC na Cointext: ${btc_data}")

    return btc_data

def send_telegram_message(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Falha ao enviar mensagem. Status: {response.status_code}")

# Função que calcula a relação de preço entre as corretoras e detecta se há ou não oportunidade
# para arbitragem
def detect_arbitrage(price_bybit, price_coinext, fees_percent):
    """
    Detecta oportunidades de arbitragem entre duas corretoras.

    Nota:
        price_bybit (float): Preço do BTC em USD na Bybit.
        price_coinext (float): Preço do BTC em USD na Coinext.
        fees_percent (float): Taxa total estimada como porcentagem.
    """

    # Retorna se o valor de alguma das corretoras não for válido
    if price_bybit is None or price_coinext is None:
        print("Erro: Não foi possível obter os preços das corretoras.")
        return

    try:
        # Compara a relação de compra e venda entre as duas corretoras
        if price_bybit > price_coinext:
            difference_percent = ((price_bybit - price_coinext) / price_coinext) * 100

            if difference_percent - fees_percent > minimum_percentage:

                message = f"Oportunidade de arbitragem: Compre na Coinext por ${price_coinext} e venda na Bybit por ${price_bybit}.\nLucro estimado: {difference_percent - fees_percent:.2f}%"
                send_telegram_message(message, telegram_api_key, telegram_chat_id)

                print(
                    f"Arbitragem disponível! Compre na Coinext à (${price_coinext}) e venda na Bybit à (${price_bybit}).")
                print(f"Lucro estimado: {difference_percent - fees_percent:.2f}%")

            else:
                print("Não há boas oportunidades no momento.")

        elif price_coinext > price_bybit:
            difference_percent = ((price_coinext - price_bybit) / price_bybit) * 100

            if difference_percent - fees_percent > minimum_percentage:

                message = f"Oportunidade de arbitragem: Compre na Bybit por ${price_bybit} e venda na Coinext por ${price_coinext}.\nLucro estimado: {difference_percent - fees_percent:.2f}%"
                send_telegram_message(message, telegram_api_key, telegram_chat_id)

                print(
                    f"Arbitragem disponível! Compre na Bybit à (${price_bybit}) e venda na Coinext à (${price_coinext}).")
                print(f"Lucro estimado: {difference_percent - fees_percent:.2f}%")

            else:
                print("Não há boas oportunidades no momento.")

    except KeyError as e:
        print(f"Erro ao acessar dados de preço: {e}")

# Função para exibir o horário local atual
def show_date_hour():
    # Obter o timestamp UTC e converter para horário de Brasília
    utc_now = datetime.now(pytz.utc)  # Obtém o tempo atual em UTC com fuso horário
    br_timezone = pytz.timezone("America/Sao_Paulo")  # Fuso horário de Brasília
    timestamp_br = utc_now.astimezone(br_timezone)  # Converte para o horário de Brasília

    # Formata o timestamp em formato desejado
    formatted_timestamp = print(timestamp_br.strftime("Data: %d-%m-%Y Hora: %H:%M:%S"))

    return formatted_timestamp

# Função que executa o loop de monitoramento
def run_every_60_seconds():
    try:
        while True:
            # Chama a função para pegar o preço do BTC
            test_btc_price()
            test_btc_price_coinext()

            show_date_hour()

            detect_arbitrage(
                price_bybit=get_btc_price_bybit(),  # Preço na Bybit em USD
                price_coinext=get_btc_price_coinext(),  # Preço na Coinext em USD
                fees_percent=0.75  # Taxas totais estimadas (1%)
            )

            # Aguarda 60 segundos antes de rodar novamente
            time.sleep(delay_time)
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
