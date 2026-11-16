import os, time, json, requests
from flask import Flask, send_file
app = Flask(__name__)
DATA_FILE = "ak_history.json"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def collect_data():
    try:
        headers = {'Accept': 'application/json, text/plain, */*', 'Origin': 'https://dkwin.org', 'Referer': 'https://dkwin.org/', 'User-Agent': 'Mozilla/5.0'}
        res = requests.post(API_URL, json={"pageSize": 10, "pageNo": 1, "typeId": 30, "language": 0}, headers=headers, timeout=10)
        if res.status_code == 200:
            data_list = res.json().get('data', {}).get('list', [])
            if data_list:
                existing = []
                if os.path.exists(DATA_FILE):
                    try:
                        with open(DATA_FILE, 'r', encoding='utf-8') as f: existing = json.load(f)
                    except: existing = []
                mapped = {item['issueNumber']: item for item in existing if 'issueNumber' in item}
                for row in data_list:
                    issue = row.get('issueNumber')
                    if issue and issue not in mapped:
                        num = int(row.get('number', -1))
                        row['size'] = 'Big' if num >= 5 else 'Small'
                        row['logged_at'] = time.strftime('%Y-%m-%d %I:%M:%S %p')
                        mapped[issue] = row
                sorted_data = sorted(mapped.values(), key=lambda x: x['issueNumber'], reverse=True)
                with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(sorted_data, f, indent=4, ensure_ascii=False)
    except Exception as e: print("Error:", e)

@app.route('/')
def home():
    collect_data()
    total = len(json.load(open(DATA_FILE))) if os.path.exists(DATA_FILE) else 0
    return f"<h1>🚀 Wingo Logger Active</h1><p>Saved Records: {total}</p><br><a href='/download'>📥 Download JSON</a>"

@app.route('/download')
def download_file():
    collect_data()
    return send_file(DATA_FILE, as_attachment=True, download_name="WinGo_History.json") if os.path.exists(DATA_FILE) else ("Not found", 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
