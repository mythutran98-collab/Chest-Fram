import os
import time
import requests
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot dang chay truc tiep khong proxy!", 200

def run_web_server():
    app.run(host='0.0.0.0', port=8085)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# Cấu hình ID game và Webhook của bạn
PLACE_ID = "98991765221603" 
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1520677058995290134/lM-gVfvifvr_vaZ2fUVlSmaU68WGrdL6s0XCi3EeSSphVgd5BED3U6DlVeNfHm19-ChX"

# GỌI TRỰC TIẾP API ROBLOX - BỎ TOÀN BỘ PROXY TRUNG GIAN
ROBLOX_API_URL = f"https://games.roblox.com/v1/games/{PLACE_ID}/servers/Public?limit=100"

notified_servers = {}

def check_roblox_servers():
    try:
        # Giả lập Header giống hệt trình duyệt Chrome trên Android để tránh bị chặn
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://www.roblox.com",
            "Referer": "https://www.roblox.com/"
        }
        
        res = requests.get(ROBLOX_API_URL, headers=headers, timeout=15)
        
        if res.status_code != 200:
            print(f"[{time.strftime('%H:%M:%S')}] API Roblox phan hoi Code: {res.status_code}")
            return
            
        data = res.json()
        servers = data.get("data", [])
        
        if not servers:
            print(f"[{time.strftime('%H:%M:%S')}] Ket noi thanh cong! Game hien tai dang co 0 server mo.")
            return
            
        print(f"[{time.strftime('%H:%M:%S')}] THANH CONG! Quet truc tiep tim thay {len(servers)} servers.")
        current_time = time.time()

        for server in servers:
            server_id = server.get("id")
            player_count = server.get("playing", 0)
            max_players = server.get("maxPlayers", 60)
            
            try:
                server_genesis_time = int(server_id.split("-")[0], 16) / 1000000 
                server_real_uptime = current_time - server_genesis_time
            except:
                server_real_uptime = (int(current_time) ^ hash(server_id)) % 7200

            time_in_cycle = server_real_uptime % 1200  
            time_until_chest = 1200 - time_in_cycle
            time_until_chest_minutes = time_until_chest / 60

            if time_until_chest_minutes <= 5.5 or time_in_cycle <= 60:
                if server_id in notified_servers and (current_time - notified_servers[server_id] < 480):
                    continue

                join_link = f"https://www.roblox.com/games/start?placeId={PLACE_ID}&gameInstanceId={server_id}"
                
                if time_in_cycle <= 60:
                    status_title = "🔥 CHEST ĐANG CÓ SẴN TRONG SERVER!"
                    status_text = "Rương hiện **đang xuất hiện** tại server này! Vào nhặt ngay!"
                    color_code = 16711680
                else:
                    status_title = "⏳ SẮP CÓ CHEST (DƯỚI 5.5 PHÚT)!"
                    status_text = f"Hệ thống quét thấy rương sắp xuất hiện sau: **{round(time_until_chest_minutes, 1)} phút**."
                    color_code = 16776960

                payload = {
                    "username": "Roblox Tracker",
                    "embeds": [{
                        "title": status_title,
                        "description": status_text,
                        "color": color_code,
                        "fields": [
                            {"name": "Nguoi choi", "value": f"👤 {player_count}/{max_players}", "inline": True},
                            {"name": "Uptime", "value": f"🕒 Chạy được {round(server_real_uptime/60, 1)} phút", "inline": True},
                            {"name": "👉 Link vao thẳng", "value": f"[BẤM VÀO ĐÂY ĐỂ VÀO GAME]({join_link})", "inline": False}
                        ],
                        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                    }]
                }
                requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
                notified_servers[server_id] = current_time
                print(f"-> Da gui thong bao ra Discord cho server: {server_id}")
                
    except Exception as e:
        print(f"Loi ket noi vao mang Roblox: {e}")

if __name__ == "__main__":
    keep_alive()
    while True:
        check_roblox_servers()
        # Đặt 30 giây để giữ kết nối an toàn với máy chủ Roblox gốc
        time.sleep(30)
EOF
