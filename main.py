import os
import time
import json
import requests
from flask import Flask, send_file

app = Flask(__name__)
DATA_FILE = "ak_history.json"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def collect_data():
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://dkwin.org',
            'Referer': 'https://dkwin.org/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.post(API_URL, json={"pageSize": 10, "pageNo": 1, "typeId": 30, "language": 0}, headers=headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            list_data = res_json.get('data', {}).get('list', [])
            if list_data:
                existing = []
                if os.path.exists(DATA_FILE):
                    try:
                        with open(DATA_FILE, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                    except:
                        existing = []
                
                mapped = {item['issueNumber']: item for item in existing if 'issueNumber' in item}
                
                for row in list_data:
                    issue = row.get('issueNumber')
                    if issue and issue not in mapped:
                        num = int(row.get('number', -1))
                        row['size'] = 'Big' if num >= 5 else 'Small'
                        row['logged_at'] = time.strftime('%Y-%m-%d %I:%M:%S %p')
                        mapped[issue] = row
                
                sorted_data = sorted(mapped.values(), key=lambda x: x['issueNumber'], reverse=True)
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(sorted_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error:", e)

@app.route('/')
def home():
    # প্রতিবার ব্রাউজারে লিংক ভিজিট করলেই লেটেস্ট ডেটা টেনে আনবে এবং স্ট্যাটাস দেখাবে
    collect_data()
    total = 0
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                total = len(json.load(f))
        except:
            total = 0
            
    return f"""
    <html>
        <head><title>AK7ZB Wingo Logger</title></head>
        <body style="background:#111; color:#0f0; font-family:monospace; text-align:center; padding-top:50px;">
            <h1>🚀 Wingo Data Logger Active (Render)</h1>
            <p>Total Saved Records: <b>{total}</b></p>
            <br>
            <a href="/download" style="background:#0f0; color:#000; padding:15px 30px; text-decoration:none; font-weight:bold; border-radius:5px;">📥 Download JSON History File</a>
        </body>
    </html>
    """

@app.route('/download')
def download_file():
    collect_data()
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name="WinGo_History.json")
    return "No data file found yet!", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
