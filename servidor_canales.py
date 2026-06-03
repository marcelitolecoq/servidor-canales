from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import os
import time
from datetime import datetime

PORT = int(os.environ.get("PORT", 8888))
ABC_VIDEO_ID = "x9skr3m"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.abc.com.py/",
}

TELEFUTURO_2 = "http://edge02-fdo-py.cvattv.com.ar/live/c5eds/TELEFUTURO_C4/verimatrix_rotating_FTA/TELEFUTURO_C4-video=3000000-audio_20000=144800.m3u8"
TELEFUTURO_ALTA = "https://zn1tf.desdeparaguay.net/telefuturo/telefuturo_py_alta/playlist.m3u8"

# Cache
cache = {"m3u": None, "ts": 0}
CACHE_TTL = 300  # 5 minutos


def get_abc_url():
    try:
        api_url = f"https://www.dailymotion.com/player/metadata/video/{ABC_VIDEO_ID}?embedder=https://www.abc.com.py"
        r = requests.get(api_url, headers=HEADERS, timeout=10)
        data = r.json()
        qualities = data.get("qualities", {})
        for quality in ["1080", "720", "480", "380", "240", "auto"]:
            if quality in qualities:
                for item in qualities[quality]:
                    if "m3u8" in item.get("url", ""):
                        return item["url"]
    except Exception as e:
        print(f"[ERROR ABC] {e}")
    return None


def build_m3u():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando lista...")
    abc_url = get_abc_url()
    m3u = "#EXTM3U\n"
    if abc_url:
        m3u += f'#EXTINF:-1 group-title="Paraguay",ABC TV\n{abc_url}\n'
        print("  ABC TV OK")
    else:
        print("  ABC TV FALLO")
    m3u += f'#EXTINF:-1 group-title="Paraguay",Telefuturo HD\n{TELEFUTURO_ALTA}\n'
    m3u += f'#EXTINF:-1 group-title="Paraguay",Telefuturo 2\n{TELEFUTURO_2}\n'
    return m3u


def get_cached_m3u():
    now = time.time()
    if cache["m3u"] is None or (now - cache["ts"]) > CACHE_TTL:
        cache["m3u"] = build_m3u()
        cache["ts"] = now
    return cache["m3u"]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/canales.m3u":
            m3u = get_cached_m3u()
            content = m3u.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegurl")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Servidor de canales Paraguay OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


print(f"Servidor iniciando en puerto {PORT}...")

# Pre-cargar cache al inicio
cache["m3u"] = build_m3u()
cache["ts"] = time.time()
print("Cache cargado. Servidor listo.")

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
