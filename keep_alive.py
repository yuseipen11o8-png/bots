import os
from threading import Thread
from flask import Flask

# --- Render用：Webサーバー設定 ---
app = Flask('')


@app.route('/')
def home():
    return "Lili, Nana, and Makaron are online!", 200


def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
