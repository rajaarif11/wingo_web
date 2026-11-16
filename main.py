import os, time, json, requests
from flask import Flask, send_file
app = Flask(__name__)
DATA_FILE = "ak_history.json"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def collect_data():
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://dkwin.org',
            'Referer': 'https://dkwin.org/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        payload = {"pageSize": 50, "pageNo": 1, "typeId": 30, "language": 0}
        res = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            res_json = res.json()
            data_list = res_json.get('data', {}).get('list', [])
            if data_list:
                existing = []
                if os.path.exists(DATA_FILE):
                    try:
                        with open(DATA_FILE, 'r', encoding='utf-8') as f:
                            existing = json.load(f)
                    except:
                        existing = []
                
                mapped = {item['issueNumber']: item for item in existing if 'issueNumber' in item}
                for row in data_list:
                    issue = row.get('issueNumber')
                    if issue and issue not in mapped:
                        num = int(row.get('number', -1))
                        row['size'] = 'Big' if num >= 5 else 'Small'
                        row['logged_at'] = time.strftime('%Y-%m-%d %I:%M:%S %p')
                        mapped[issue] = row
                
                sorted_data = sorted(mapped.values(), key=lambda x: x['issueNumber'], reverse=True)
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(sorted_data, f, indent=4, ensure_ascii=False)
                return len(sorted_data)
    except Exception as e:
        print("Error fetching data:", e)
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return len(json.load(f))
        except:
            pass
    return 0

@app.route('/')
def home():
    total = collect_data()
    return f"""
    <html>
        <head><title>AK7ZB Wingo Logger</title></head>
        <body style="background:#111; color:#0f0; font-family:monospace; text-align:center; padding-top:50px;">
            <h1>🚀 Wingo Data Logger Active</h1>
            <p>Total Saved Records: <b>{total}</b></p>
            <br><br>
            <a href="/download" style="background:#0f0; color:#000; padding:15px 30px; text-decoration:none; font-weight:bold; border-radius:5px;">📥 Download JSON History File</a>
        </body>
    </html>
    """

@app.route('/download')
def download_file():
    collect_data()
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name="WinGo_History.json")
    return "No data found yet! Please refresh home page.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
