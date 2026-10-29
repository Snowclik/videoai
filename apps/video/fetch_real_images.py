"""Descarga imágenes reales (Wikimedia Commons) para el video y reporta tamaños.
Uso: python fetch_real_images.py   (desde apps/video)
"""
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public" / "real"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "VideoIA-student-project/1.0 (educational)"}

IMAGES = {
    "turbopascal6.png": "https://upload.wikimedia.org/wikipedia/commons/8/84/Turbopascal_6.png",
    "turbopascal_floppies.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Turbo_Pascal_7.0_Install_Floppy_Discs_%28Deutsch%29.jpg/1280px-Turbo_Pascal_7.0_Install_Floppy_Discs_%28Deutsch%29.jpg",
    "turbopascal_blackboard.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Turbo_Pascal_on_blackboard.jpg/1280px-Turbo_Pascal_on_blackboard.jpg",
    "vs2005_box.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Visual_Studio_2005_beta_2_packaging.jpg/1280px-Visual_Studio_2005_beta_2_packaging.jpg",
}

for name, url in IMAGES.items():
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=40).read()
        (OUT / name).write_bytes(data)
        print("OK", name, len(data))
    except Exception as e:
        print("FALLO", name, e)

try:
    from PIL import Image
    for p in sorted(list(OUT.glob("*")) + list((ROOT / "public" / "anders").glob("*"))):
        try:
            with Image.open(p) as im:
                print("SIZE", p.name, im.size)
        except Exception as e:
            print("NOIMG", p.name, e)
except ImportError:
    print("PIL no disponible")
