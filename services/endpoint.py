import services.config
import requests

def send_to_endpoint(user_input):
    url = f"{services.config.service_endpoint}{user_input}&conversation_id={services.config.conservation_id}"

    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {'query': str(e), 'language': 'error' }
