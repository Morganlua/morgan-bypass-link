from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/bypass', methods=['POST'])
def bypass_target():
    data = request.get_json() or {}
    target_url = data.get('url', '')

    if not target_url:
        return jsonify({"status": "error", "message": "URL target kosong, anjing!"}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': target_url
        }

        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Gagal menembus server target, bajing!"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')
        final_link = None

        # Logika ekstraksi Sub4Unlock / Safelink
        if "sub4unlock" in target_url or "subs4unlock" in target_url:
            btn_target = soup.find('a', id=re.compile('download|btn|unlock', re.I))
            if btn_target and btn_target.get('href'):
                final_link = btn_target['href']
            else:
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('http://' in script.string or 'https://' in script.string):
                        match = re.search(r'https?://[^\s<>"]+|www\.[^\s<>"]+', script.string)
                        if match and 'sub4unlock' not in match.group(0):
                            final_link = match.group(0)
                            break

        elif "safelinku" in target_url or "sfgl.link" in target_url:
            input_token = soup.find('input', {'name': 'url'}) or soup.find('input', id='safelink-value')
            if input_token and input_token.get('value'):
                final_link = input_token['value']
            else:
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and 'safelinku' not in href and 'sfgl' not in href:
                        final_link = href
                        break

        if not final_link:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('http') and not any(x in href for x in ['facebook', 'youtube', 'telegram', 'discord', target_url]):
                    final_link = href
                    break

        if final_link:
            return jsonify({"status": "success", "url": final_link})
        else:
            return jsonify({"status": "error", "message": "Tautan asli terkunci rapat, gagal diekstrak!"}), 422

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def handler(environ, start_response):
    return app(environ, start_response)
