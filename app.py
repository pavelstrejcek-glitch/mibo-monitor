import requests
from flask import Flask, render_template

app = Flask(__name__)

# --- KONFIGURACE MI:BO ---
USER_LOGIN = "flotila@mibotrans.cz"
USER_PASS = "dangup-kovbuh-Mewte3"
CLIENT_ID = "website"

# Společné maskování pro všechny požadavky
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json'
}

def get_mibo_data():
    try:
        # 1. Získání TOKENU (přihlášení)
        auth_url = "https://o1-api.gpsguard.eu/webapi/auth/login"
        auth_data = {"username": USER_LOGIN, "password": USER_PASS, "clientId": CLIENT_ID}
        
        res = requests.post(auth_url, json=auth_data, headers=HEADERS, timeout=10)
        
        if res.status_code != 200:
            print(f"Chyba login: {res.status_code}")
            return []

        token = res.json().get('accessToken')
        auth_h = HEADERS.copy()
        auth_h['Authorization'] = f'Bearer {token}'

        # 2. Stažení dat (Statusy a Info o vozidlech)
        s_res = requests.get("https://o1-api.gpsguard.eu/webapi/DOCU/vehicle/statusV2", headers=auth_h, timeout=10)
        i_res = requests.get("https://o1-api.gpsguard.eu/webapi/DOCU/vehicle/infoV2", headers=auth_h, timeout=10)

        if s_res.status_code != 200 or i_res.status_code != 200:
            print("Chyba při stahování dat")
            return []

        statusy = s_res.json()
        auta_info = i_res.json()

        vysledek = []
        for s in statusy:
            kod = str(s.get('code'))
            info = auta_info.get(kod, {})
            vysledek.append({
                "jmeno": info.get('SPZ') or info.get('Name') or kod,
                "rychlost": s.get('speed', 0),
                "adresa": s.get('address', 'Poloha se zjišťuje...'),
                "cas": s.get('time', '---')
            })
        
        # Seřadit auta podle jména
        vysledek.sort(key=lambda x: str(x['jmeno']))
        return vysledek

    except Exception as e:
        print(f"Kritická chyba: {e}")
        return []

@app.route('/')
def home():
    data = get_mibo_data()
    return render_template('index.html', auta=data if data else [])

if __name__ == "__main__":
    app.run()
