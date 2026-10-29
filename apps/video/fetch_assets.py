"""Descarga SVGs de Iconify (sin API key) y busca imágenes reales en Wikimedia Commons.
Uso: python fetch_assets.py   (desde apps/video)
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
UA = {"User-Agent": "VideoIA-student-project/1.0 (educational)"}

ICONS = {
    # nombre_local: "set:icono"
    "keyboard": "ph:keyboard-fill",
    "terminal": "ph:terminal-window-fill",
    "floppy": "ph:floppy-disk-fill",
    "zap": "ph:lightning-fill",
    "shield": "ph:shield-check-fill",
    "rocket": "ph:rocket-launch-fill",
    "code": "ph:code-bold",
    "sparkle": "ph:sparkle-fill",
    "cpu": "ph:cpu-fill",
    "globe": "ph:globe-hemisphere-west-fill",
    "building": "ph:buildings-fill",
    "bug": "ph:bug-fill",
    "check": "ph:check-circle-fill",
    "pascal": "devicon:delphi",
    "windows": "logos:microsoft-windows-icon",
    "dotnet": "devicon:dotnetcore",
    "nodejs": "devicon:nodejs",
    "react": "devicon:react",
    "github": "devicon:github",
}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def icons():
    out = ROOT / "public" / "icons2"
    out.mkdir(parents=True, exist_ok=True)
    for name, ref in ICONS.items():
        s, i = ref.split(":")
        try:
            svg = get(f"https://api.iconify.design/{s}/{i}.svg?height=256")
            (out / f"{name}.svg").write_text(svg, encoding="utf-8")
            print("OK icono", name)
        except Exception as e:
            print("FALLO icono", name, e)


def commons(query, n=6):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrsearch": query,
        "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": 1200,
    })
    data = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))
    res = []
    for p in (data.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        res.append((p["title"], ii.get("thumburl") or ii.get("url"), ii.get("width"), ii.get("height"), ii.get("mime")))
    return res


if __name__ == "__main__":
    icons()
    for q in ["Turbo Pascal", "Borland Turbo Pascal screenshot", "Anders Hejlsberg", "TypeScript logo", "Visual Studio 2002"]:
        print("\n##", q)
        try:
            for r in commons(q):
                print(r)
        except Exception as e:
            print("FALLO busqueda", e)
