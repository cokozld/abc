import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "ask.db"

# --- 1. Veritabanı Kurulumu ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS lovers (
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    score INTEGER,
                    inbox_message TEXT,
                    has_notification INTEGER DEFAULT 0
                )''')
    c.execute('SELECT count(*) FROM lovers')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO lovers (name, score, inbox_message, has_notification) VALUES (?, ?, ?, ?)", ("E", 0, "Sistem: Henüz mesaj yok.", 0))
        c.execute("INSERT INTO lovers (name, score, inbox_message, has_notification) VALUES (?, ?, ?, ?)", ("B", 0, "Sistem: Henüz mesaj yok.", 0))
        conn.commit()
    conn.close()

# --- 2. HTML, CSS (Video Arka Plan + Pembe User 2) ---
HTML_KODU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><3<3<3</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=VT323&display=swap" rel="stylesheet">
    <style>
        /* Temel Ayarlar */
        body {
            margin: 0; padding: 20px;
            color: #ffffff;
            font-family: 'VT323', monospace;
            text-align: center;
            min-height: 100vh;
            display: flex; flex-direction: column; align-items: center;
            overflow-x: hidden;
        }

        /* --- VİDEO ARKA PLAN AYARLARI --- */
        #bg-video {
            position: fixed;
            right: 0; bottom: 0;
            min-width: 100%; min-height: 100%;
            width: auto; height: auto;
            z-index: -3;
            object-fit: cover;
            filter: grayscale(100%) contrast(1.2);
        }

        .overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: -2;
        }

        .scanlines {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: repeating-linear-gradient(0deg, rgba(0,0,0,0.5) 0px, rgba(0,0,0,0.5) 1px, transparent 1px, transparent 2px);
            pointer-events: none; z-index: -1;
        }

        /* --- STİLLER --- */
        h1 {
            font-family: 'Orbitron', sans-serif; font-size: 3em; letter-spacing: 2px;
            margin-bottom: 20px; text-shadow: 0 0 10px #fff;
            animation: flicker 3s infinite alternate;
        }
        @keyframes flicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 10px #fff; }
            20%, 24%, 55% { opacity: 0.5; text-shadow: none; }
        }

        /* Standart Beyaz Neon Kutu */
        .neon-box {
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #fff;
            box-shadow: 0 0 10px #fff, inset 0 0 5px #fff;
            padding: 20px; border-radius: 5px;
            backdrop-filter: blur(2px);
            transition: all 0.3s;
        }

        /* --- ÖZEL PEMBE MOD (User 2 İçin) --- */
        .pink-glow {
            border-color: #ff00ff !important;
            box-shadow: 0 0 15px #ff00ff, inset 0 0 5px #ff00ff !important;
        }
        .pink-glow .name { color: #ff00ff !important; text-shadow: 0 0 5px #ff00ff !important; }
        .pink-glow .score { color: #ff00ff !important; text-shadow: 0 0 20px #ff00ff !important; }
        
        /* Pembe Butonlar */
        .pink-glow button { 
            border-color: #ff00ff !important; color: #ff00ff !important; box-shadow: 0 0 5px #ff00ff !important; 
        }
        .pink-glow button:hover { 
            background: #ff00ff !important; color: black !important; box-shadow: 0 0 25px #ff00ff !important; 
        }

        /* --- DİĞER HTML ELEMANLARI --- */
        .user-select { margin-bottom: 30px; font-size: 1.5em; }
        .user-select a { text-decoration: none; color: #aaa; padding: 5px 15px; border: 1px solid #555; transition: 0.3s; }
        .user-select a.active { color: #fff; border-color: #fff; box-shadow: 0 0 10px #fff; background: rgba(255,255,255,0.1); }

        .container { display: flex; gap: 30px; flex-wrap: wrap; justify-content: center; margin-bottom: 40px; }
        .card { width: 220px; }
        .name { font-family: 'Orbitron'; font-size: 1.5em; text-shadow: 0 0 5px #fff; }
        .score { font-size: 5em; font-weight: bold; margin: 10px 0; text-shadow: 0 0 15px #fff; animation: flicker 1.5s infinite; }
        
        button {
            font-family: 'VT323'; font-size: 1.3em; text-transform: uppercase;
            background: black; color: #fff; border: 2px solid #fff;
            padding: 10px 20px; cursor: pointer; transition: 0.2s; box-shadow: 0 0 5px #fff;
        }
        button:hover { background: #fff; color: #000; box-shadow: 0 0 20px #fff; }
        button:active { transform: scale(0.95); }
        .btn-heart { width: 100%; }

        .message-section { width: 90%; max-width: 500px; display: flex; flex-direction: column; gap: 15px; }
        textarea {
            width: 100%; height: 80px; padding: 10px; background: rgba(0,0,0,0.5); color: #fff;
            border: 2px solid #555; font-family: 'VT323'; font-size: 1.2em; resize: none; outline: none;
        }
        textarea:focus { border-color: #fff; box-shadow: 0 0 10px #fff; }
        
        .btn-read { width: 100%; border: 2px dashed #555; color: #aaa; background: black; }
        
        .notification-active { border: 2px solid #fff; color: #fff; animation: strobe 0.5s infinite; }
        @keyframes strobe {
            0% { background: #000; color: #fff; box-shadow: 0 0 5px #fff; }
            50% { background: #fff; color: #000; box-shadow: 0 0 30px #fff; }
            100% { background: #000; color: #fff; box-shadow: 0 0 5px #fff; }
        }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #000; border: 4px solid #fff; box-shadow: 0 0 30px #fff; padding: 30px; width: 80%; max-width: 400px; text-align: center; }
        .message-text { font-size: 1.5em; margin: 20px 0; border-left: 4px solid #fff; padding-left: 15px; text-align: left; white-space: pre-wrap; }
    </style>
</head>
<body>

    <video autoplay muted loop id="bg-video">
        <source src="/static/background.mp4" type="video/mp4">
    </video>
    <div class="overlay"></div>
    <div class="scanlines"></div>

    <div class="user-select neon-box">
        [ SISTEM HESABI ] : 
        <a href="/?user_id=1" class="{{ 'active' if active_user == 1 else '' }}">E</a> //
        <a href="/?user_id=2" class="{{ 'active' if active_user == 2 else '' }}">B</a>
    </div>

    <h1>ETKILESIM BEKLENIYOR...</h1>

    <div class="container">
        {% for kisi in kisiler %}
        <div class="card neon-box {{ 'pink-glow' if kisi[0] == 2 else '' }}">
            <div class="name">TARGET: {{ kisi[1] }}</div>
            <div class="score">{{ kisi[2] }}</div>
            <form action="/boost/{{ kisi[0] }}?user_id={{ active_user }}" method="post">
                <button type="submit" class="btn-heart">>> SİNYAL GÖNDER <<</button>
            </form>
        </div>
        {% endfor %}
    </div>

    <div class="message-section neon-box">
        <h3>// DATA UPLINK //</h3>
        <form action="/send_message" method="post" style="border-bottom: 2px dashed #333; padding-bottom: 15px;">
            <input type="hidden" name="sender_id" value="{{ active_user }}">
            <textarea name="message" placeholder="Veri girişi yapın..."></textarea>
            <br><br>
            <button type="submit" class="btn-send" style="width: 100%;">[ MESAJ GONDER ]</button>
        </form>

        {% set me = kisiler[active_user - 1] %}
        <div style="margin-top: 15px;">
        <button onclick="openModal()" class="btn-read {{ 'notification-active' if me[4] == 1 else '' }}">
            {{ '*** UYARI: BEKLEYEN MESAJ ***' if me[4] == 1 else '[ MESAJ YOK. ]' }}
        </button>
        </div>
    </div>

    <div id="messageModal" class="modal">
        <div class="modal-content">
            <h2 style="font-family: 'Orbitron';">> GELEN MESAJ <</h2>
            <div class="message-text">{{ me[3] }}</div>
            <form action="/clear_notification" method="post">
                <input type="hidden" name="user_id" value="{{ active_user }}">
                <button type="submit" class="close-btn">[ MESAJI KAPAT ]</button>
            </form>
        </div>
    </div>

    <script>
        function openModal() { document.getElementById('messageModal').style.display = 'flex'; }
    </script>

</body>
</html>
"""

# --- 3. Backend (Aynı) ---
@app.route('/')
def index():
    active_user = int(request.args.get('user_id', 1))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM lovers")
    kisiler = c.fetchall()
    conn.close()
    return render_template_string(HTML_KODU, kisiler=kisiler, active_user=active_user)

@app.route('/boost/<int:id>', methods=['POST'])
def boost(id):
    active_user = request.args.get('user_id', 1)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE lovers SET score = score + 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', user_id=active_user))

@app.route('/send_message', methods=['POST'])
def send_message():
    sender_id = int(request.form['sender_id'])
    message = request.form['message']
    receiver_id = 2 if sender_id == 1 else 1
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE lovers SET inbox_message = ?, has_notification = 1 WHERE id = ?", (message, receiver_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index', user_id=sender_id))

@app.route('/clear_notification', methods=['POST'])
def clear_notification():
    user_id = request.form['user_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE lovers SET has_notification = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', user_id=user_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
