import requests

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.abc.com.py/"}

def get_abc_url():
    try:
        r = requests.get("https://www.dailymotion.com/player/metadata/video/x9skr3m?embedder=https://www.abc.com.py", headers=HEADERS, timeout=10)
        qualities = r.json().get("qualities", {})
        for q in ["720", "480", "auto"]:
            if q in qualities:
                for item in qualities[q]:
                    if "m3u8" in item.get("url", ""):
                        return item["url"]
    except:
        pass
    return ""

abc = get_abc_url()
m3u = f"""#EXTM3U
#EXTINF:-1 group-title="Paraguay",ABC TV
{abc}
#EXTINF:-1 group-title="Paraguay",Telefuturo HD
https://zn1tf.desdeparaguay.net/telefuturo/telefuturo_py_alta/playlist.m3u8
#EXTINF:-1 group-title="Paraguay",Telefuturo 2
http://edge02-fdo-py.cvattv.com.ar/live/c5eds/TELEFUTURO_C4/verimatrix_rotating_FTA/TELEFUTURO_C4-video=3000000-audio_20000=144800.m3u8"""

with open("canales.m3u", "w") as f:
    f.write(m3u)
print("Listo:", abc[:80] if abc else "SIN URL")
