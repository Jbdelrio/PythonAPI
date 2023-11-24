import time
import threading
import asyncio
import aiohttp
import socket
import json

# Fonction asynchrone pour récupérer les données OHLCV (Open, High, Low, Close, Volume) à partir de l'API de Binance.
async def fetch_ohlcv(session, symbol: str) -> dict[str, float]:

    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': '1d',
        'limit': 1
    }

    async with session.get(url, params=params) as response:
        details = await response.json()
        return {symbol: {'open': d[1], 'high': d[2], 'low': d[3], 'close': d[4], 'volume': d[5]}
                for d in details}

# Fonction asynchrone pour récupérer les données OHLCV pour plusieurs symboles simultanément.
async def gather_ohlcv(symbols: list[str]) -> dict[str, dict[str, float]]:

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ohlcv(session, symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
    
    return {key: value for d in results for key, value in d.items()}  

# Fonction exécutée par un thread pour récupérer périodiquement les données OHLCV.
def thread_ohlcv(symbols: list[str]) -> dict[str, dict[str, float]]:
    
    global mapping
    while True:
        mapping = asyncio.run(gather_ohlcv(symbols))
        time.sleep(60)

# Fonction pour traiter la demande du client en fonction du symbole demandé.
def process_request(request_data: dict[str, str]) -> dict[str, dict[str, float]]:

    global mapping
    data = json.loads(request_data)
    symbol = data['symbol']

    try:
        return json.dumps({'result': mapping[symbol]})
    except KeyError:
        return json.dumps({'result': f'erreur : aucune donnée trouvée pour {symbol}'})

# Fonction pour gérer la connexion d'un client au serveur.
def handle_client(conn, addr):

    print(f"Connecté à {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            response = process_request(data.decode('utf-8'))
            conn.sendall(response.encode('utf-8'))
    finally:
        conn.close()

# Fonction principale pour démarrer le serveur.
def server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 6789))
        s.listen()
        print("Serveur démarré sur le port 6789...")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == '__main__':
  
    # Dictionnaire pour stocker les données OHLCV récupérées.
    mapping = {}
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT']

    # Exécution de la fonction de collecte de données de marché en tant que thread séparé.
    thread = threading.Thread(target=thread_ohlcv, args=(symbols,))
    thread.start()

    # Démarrage du serveur.
    server()
