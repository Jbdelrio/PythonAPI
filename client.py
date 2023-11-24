import socket
import json
import time

class MarketDataClient:
    def __init__(self, host: str, port: int):
        # Initialisation de l'objet MarketDataClient avec l'adresse du serveur (host) et le port à utiliser.
        self.host = host
        self.port = port

    def send_request(self, symbol: str) -> dict[str, dict[str, float]]:
        # Méthode pour envoyer une requête au serveur pour obtenir des données sur un symbole donné.
        # La requête est encodée en JSON et envoyée via une socket TCP.
        request_data = json.dumps({'symbol': symbol})

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(request_data.encode('utf-8'))
            response = s.recv(1024)
        
        return json.loads(response.decode('utf-8'))

def process_response(response: dict):
    # Fonction pour traiter la réponse du serveur. Elle extrait et imprime les données si elles sont présentes, sinon affiche une erreur.
    result = response.get('result', None)
    if result:
        print(f"Données reçues : {result}")
    else:
        print("Erreur : Aucune donnée trouvée.")

if __name__ == '__main__':
    # Exécution du code uniquement si le script est exécuté en tant que programme principal.
    
    # Création d'une instance de MarketDataClient avec l'adresse du serveur 'localhost' et le port '6789'.
    market_data_client = MarketDataClient('localhost', 6789)

    # Test des requêtes pour obtenir des données sur les symboles 'ETHUSDT' et 'XRPUSDT'.
    eth_response = market_data_client.send_request('ETHUSDT')
    process_response(eth_response)

    xrp_response = market_data_client.send_request('XRPUSDT')
    process_response(xrp_response)

    # Envoi d'une fausse requête avec le symbole 'BNBUSDC'.
    bnb_response = market_data_client.send_request('BNBUSDC')
    process_response(bnb_response)

    # Pause de 60 secondes, puis nouvelle requête pour vérifier les données récemment collectées pour 'ETHUSDT'.
    time.sleep(60)
    eth_response_after_update = market_data_client.send_request('ETHUSDT')
    process_response(eth_response_after_update)
