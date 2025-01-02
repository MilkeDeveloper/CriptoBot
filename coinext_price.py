import json
import threading
import websocket
from current_brl_usd_price import get_usd_brl_price_bybit

nextIvalue = 0
# Variáveis de controle
btc_price = None
price_ready = threading.Event()  # Evento para sincronizar a obtenção do preço

# Função para enviar dados ao serviço WebSocket
def call_service(ws, service_name, data, level=0):
    global nextIvalue
    frame = {
        'm': level,
        'i': nextIvalue,
        'n': service_name,
        'o': json.dumps(data)
    }
    nextIvalue += 2
    ws.send(json.dumps(frame))

# Função para lidar com erros
def on_error(ws, error):
    print(error)

# Função para processar a resposta do WebSocket
def show_info(ws, data_string):
    global btc_price
    try:
        # Tenta converter a string JSON para um dicionário
        data = json.loads(data_string)

        # Verifica a chave 'o' dentro da resposta
        if 'o' in data:
            # A chave 'o' contém uma string com a lista JSON
            o_data = json.loads(data['o'])  # Converte a string para uma lista real

            # Verifica se a lista tem algum dado
            if len(o_data) > 0:
                # Pega o preço da última negociação
                last_trade_price_brl = o_data[-1][4]  # O preço está na posição 4 da lista

                # Obtém o preço do USD/BRL
                usd_brl = get_usd_brl_price_bybit()

                if usd_brl:
                    # Converte o preço de BRL para USD
                    btc_price = last_trade_price_brl / usd_brl

                    price_ready.set()
                    ws.close()
            else:
                print("Não há dados disponíveis na lista.")
        else:
            print("Chave 'o' não encontrada na resposta.")
    except json.JSONDecodeError:
        print("Erro ao processar os dados recebidos. A resposta não é um JSON válido.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        price_ready.set()  # Sinaliza mesmo em caso de erro para evitar bloqueio

# Função que é chamada quando a conexão WebSocket é aberta
def start_talking(ws):
    ws.on_message = show_info
    call_service(ws, 'SubscribeTicker', {
        "OMSId": 1,
        "InstrumentId": 1,  # BTCBRL
        "Interval": 60,     # Intervalo de 1 minuto (60 segundos)
        "IncludeLastCount": 10  # Opcional, inclui as últimas negociações
    })

# Função para capturar o preço do BTC em tempo real
def get_btc_price_coinext():
    global btc_price
    # Inicia o WebSocket e conecta à URL da Coinext
    ws = websocket.WebSocketApp('wss://api.coinext.com.br/WSGateway/',
                                on_error=on_error,
                                on_message=show_info,
                                on_open=start_talking)

    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    # Esperar um pouco para o WebSocket conectar e coletar os dados
    price_ready.wait(timeout=10)  # Aguarda no máximo 10 segundos
    return btc_price