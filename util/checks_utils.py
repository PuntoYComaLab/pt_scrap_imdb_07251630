import requests

def check_vpn_connection(expected_country="US"):
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        current_ip = data.get("query")
        current_country = data.get("countryCode")
        print(f"IP actual: {current_ip}, País: {current_country}")
        if current_country == expected_country:
            print(f"VPN conectada correctamente al país esperado ({expected_country}).")
            return True
        else:
            print(f"VPN NO conectada al país esperado. País actual: {current_country}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"No se pudo verificar la conexión VPN: {e}")
        return False


if __name__ == "__main__":
    check_vpn_connection() 