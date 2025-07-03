import requests
from flask import Flask, request, Response

# PythonAnywhere tarapyndan döredilen adaty Flask programmasy
app = Flask(__name__)

# ==========================================================
# ESASY LOGIKA ŞU ÝERDE BAŞLAÝAR
# ==========================================================

# Siziň VPS-iňiziň IP adresi we porty girizildi.
VPS_ADDRESS = "http://135.148.82.236"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    """
    Bu funksiýa PythonAnywhere-e gelen ähli HTTP haýyşlaryny alyp,
    göni siziň 135.148.82.236 adresindäki VPS-iňize gönükdirýär
    we jogaby yzyna gaýtarýar.
    """
    
    # Gelen haýyşyň doly URL-ni döretmek (VPS üçin)
    vps_url = f"{VPS_ADDRESS}/{path}"

    # Gelen haýyşdaky ähli maglumatlary göçürmek
    headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
    
    # VPS-e haýyş ibermek
    try:
        resp = requests.request(
            method=request.method,
            url=vps_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.args,
            stream=True
        )
    except requests.exceptions.RequestException as e:
        print(f"VPS-e birikme ýalňyşlygy: {e}")
        return "Serwer ýalňyşlygy: Aralyk serwere birikip bolmady.", 502

    # VPS-den gelen jogaby göçürip, ulanyja yzyna gaýtarmak
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [(name, value) for (name, value) in resp.raw.headers.items()
                        if name.lower() not in excluded_headers]

    response = Response(resp.iter_content(chunk_size=1024), resp.status_code, response_headers)
    
    return response

# ==========================================================
# ESASY LOGIKA ŞU ÝERDE GURTARÝAR
# ==========================================================

# SENIŇ ISLEGIŇ BOÝUNÇA GOŞULAN BÖLEK
if __name__ == '__main__':
    # Ýadyňda sakla: Bu blok, programmany öz komýuteriňde ýa-da VPS-de göni
    # `python flask_app.py` diýip işledeniňde ulanylýar.
    # PythonAnywhere bu bölegi ulanmaz, ol `app` obýektini göni import edýär.
    # Ýöne seniň islegiň boýunça, bu ýere goşuldy.
    try:
        app.run(host='0.0.0.0', port=80, debug=True)
    except OSError as e:
        if e.errno == 13 or e.errno == 10013:
            print("\n**** ÝALŇYŞLYK: Port 80-i ulanmak üçin 'sudo' bilen işlediň. ****")
            print("**** Buýruk: sudo python your_script_name.py ****\n")
        else:
            raise e
