"""Descarga el modelo faster-whisper-base a assets/whisper-base (sin usar huggingface_hub).
Uso: python fetch_whisper_model.py   (desde apps/video)
"""
import urllib.request
from pathlib import Path

DEST = Path(__file__).parent / "assets" / "whisper-base"
DEST.mkdir(parents=True, exist_ok=True)
BASE = "https://huggingface.co/Systran/faster-whisper-base/resolve/main/"
FILES = ["config.json", "tokenizer.json", "vocabulary.txt", "model.bin"]

for f in FILES:
    out = DEST / f
    if out.exists() and out.stat().st_size > 0:
        print("YA EXISTE", f)
        continue
    try:
        req = urllib.request.Request(BASE + f, headers={"User-Agent": "VideoIA/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        print("OK", f, out.stat().st_size)
    except Exception as e:
        print("FALLO", f, e)
        if out.exists():
            out.unlink()
