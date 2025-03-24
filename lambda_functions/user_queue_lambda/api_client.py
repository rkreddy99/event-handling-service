import requests

class ApiClient:
    """API Client for POST requests."""

    @staticmethod
    def post_request(ip_port, token, payload):
        """Make a POST request with Bearer token authentication."""
        url = f"http://{ip_port}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        print(payload)
        try:
            response = requests.post(url, data=payload, headers=headers)
            print(response.text)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error during POST request: {e}")
            return None

