import requests
from flask import Flask, render_template

app = Flask(__name__)

# --- ÚDAJE MI:BO TRANSPORTATION ---
USER_LOGIN = "flotila@mibotrans.cz"
USER_PASS = "dangup-kovbuh-Mewte3"
CLIENT_ID = "website"

def get_mibo_data():
    try:
        # 1. Přihlášení do GPS Guard
        auth_url = "https://o1-api.gpsguard.eu/webapi/auth/login"
        auth_data = {"username": USER_LOGIN, "password": USER_PASS, "clientId": CLIENT_ID}
        auth_res = requests.post(auth_url, json=auth_data).json()
        token = auth_res.get('accessToken')
        headers = {'Authorization': f'Bearer {token}'}

        # 2. Stažení aktuálních poloh a rychlostí
        statusy = requests.get("https://o1-api.gpsguard.eu/webapi/DOCU/vehicle/statusV2", headers=headers).json()
        # Stažení názvů aut (SPZ)
        auta_info = requests.get("https://o1-api.gpsguard.eu/webapi/DOCU/vehicle/infoV2", headers=headers).json()

        vysledek = []
        for s in statusy:
            kod = str(s.get('code'))
            info = auta_info.get(kod, {})
            
            # SPZ nebo jméno, pokud SPZ chybí
            jmeno = info.get('SPZ') or info.get('Name') or kod
            
            vysledek.append({
                "jmeno": jmeno,
                "rychlost": s.get('speed', 0),
                "adresa": s.get('address', 'Poloha se zjišťuje...'),
                "cas": s.get('time', '---')
            })
        
        # Seřadit auta podle abecedy
        vysledek.sort(key=lambda x: x['jmeno'])
        return vysledek

    except Exception as e:
        print(f"Chyba: {e}")
        return []

@app.route('/')
def home():
    data = get_mibo_data()
    return render_template('index.html', auta=data)

if __name__ == "__main__":
    app.run()
