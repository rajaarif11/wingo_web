import os, time, json, requests
from flask import Flask, send_file
app = Flask(__name__)
DATA_FILE = "ak_history.json"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def collect_data():
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://dkwin.org',
            'Referer': 'https://dkwin.org/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        payload = {"pageSize": 20, "pageNo": 1, "typeId": 30, "language": 0}
        
        res = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        print("API Status Code:", res.status_code)
        print("API Response Text:", res.text[:200]) # টার্মিনাল লগ দেখার জন্য
        
        if res.status_code == 200:
            res_json = res.json()
            data_list = res_json.get('data', {}).get('list', [])
            if not data_list and isinstance(res_json.get('data'), list):
                data_list = res_json.get('data')
                
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
        <head>
            <title>AK7ZB Wingo Logger</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="background:#0a0a0a; color:#00ffcc; font-family:monospace; text-align:center; padding-top:60px;">
            <div style="border: 2px solid #00ffcc; display: inline-block; padding: 30px; border-radius: 15px; box-shadow: 0 0 15px #00ffcc55;">
                <h1 style="color: #00ffcc; text-shadow: 0 0 10px #00ffcc;">⚡ AK7ZB Wingo Logger Pro</h1>
                <p style="font-size: 18px; color: #fff;">Total Saved Records: <b style="color: #00ffcc;">{total}</b></p>
                <br>
                <a href="/download" style="background:#00ffcc; color:#000; padding:15px 30px; text-decoration:none; font-weight:bold; border-radius:8px; display:inline-block; box-shadow: 0 0 10px #00ffcc;">📥 Download JSON History File</a>
            </div>
        </body>
    </html>
    """

@app.route('/download')
def download_file():
    collect_data()
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True, download_name="WinGo_History.json")
    return "No data found yet!", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
