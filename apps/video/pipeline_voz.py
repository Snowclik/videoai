"""Genera la locución frase por frase (pausas naturales), la masteriza con FFmpeg
y produce src/timeline.json con tiempos por palabra y las escenas del video.

Uso: python pipeline_voz.py [voz] [rate]
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts

VOZ = sys.argv[1] if len(sys.argv) > 1 else "es-ES-AlvaroNeural"
RATE = sys.argv[2] if len(sys.argv) > 2 else "+2%"
FPS = 30
PAUSA = 0.32  # segundos de respiro entre frases
LEAD = 0.35   # silencio inicial

ROOT = Path(__file__).parent
TMP = ROOT / "assets" / "voz_tmp"
TMP.mkdir(parents=True, exist_ok=True)

LINEAS = [l.strip() for l in (ROOT / "guion" / "anders_hejlsberg.txt").read_text(encoding="utf-8").splitlines() if l.strip()]

# Corrección fonética para TTS en español:
# C# debe leerse como "C-Sharp" (y nunca "C almohadilla")
# punto net debe leerse natural
def preparar_texto_fonetico(linea: str) -> str:
    texto = linea
    texto = texto.replace("C#", "C-Sharp")
    texto = texto.replace("punto net", "dot net")
    return texto

LEER = [preparar_texto_fonetico(l) for l in LINEAS]


def dur(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    return float(out.decode().strip())


async def sintetizar(i, texto):
    f = TMP / f"s{i}.mp3"
    await edge_tts.Communicate(texto, VOZ, rate=RATE).save(str(f))
    return f


async def main():
    archivos = [await sintetizar(i, t) for i, t in enumerate(LEER)]
    durs = [dur(f) for f in archivos]

    # Concatenar con silencios
    inputs, filtros, partes = [], [], []
    for i, f in enumerate(archivos):
        inputs += ["-i", str(f)]
    inputs += ["-f", "lavfi", "-t", "1", "-i", "anullsrc=r=24000:cl=mono"]
    n = len(archivos)
    fc = []
    for i in range(n):
        pad = LEAD if i == 0 else PAUSA
        fc.append(f"[{i}:a]aresample=24000,adelay={int(pad*1000)}:all=1[a{i}]")
    fc.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[cat]")
    # Masterización: filtros de voz + compresión suave + EBU R128
    fc.append(
        "[cat]highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=2,equalizer=f=200:t=q:w=1:g=1.5,"
        "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,"
        "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[out]"
    )
    salida = ROOT / "public" / "voz_masterizada.wav"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
                           "-map", "[out]", "-ac", "1", str(salida)])

    # Tiempos por palabra (reparto proporcional a los caracteres dentro de cada frase)
    palabras, escenas = [], []
    t = 0.0
    for i, (linea, d) in enumerate(zip(LINEAS, durs)):
        t += LEAD if i == 0 else PAUSA
        toks = linea.split()
        pesos = [len(w) + 2 for w in toks]
        total = sum(pesos)
        cur = t
        for w, p in zip(toks, pesos):
            ws = cur
            we = cur + d * p / total
            palabras.append({"word": w, "start_frame": int(ws * FPS), "end_frame": max(int(ws * FPS) + 1, int(we * FPS) - 1)})
            cur = we
        escenas.append({"index": i, "start_frame": int((t - (0 if i else LEAD)) * FPS) if i else 0,
                        "text": linea})
        t += d
    total_s = t + 1.6
    total_frames = int(total_s * FPS)
    for i, e in enumerate(escenas):
        e["end_frame"] = escenas[i + 1]["start_frame"] if i + 1 < len(escenas) else total_frames
        e["duration_frames"] = e["end_frame"] - e["start_frame"]

    (ROOT / "src" / "timeline.json").write_text(json.dumps({
        "settings": {"fps": FPS, "width": 1080, "height": 1920, "voice": VOZ},
        "total_frames": total_frames,
        "words": palabras,
        "scenes": escenas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {VOZ} {total_s:.1f}s {total_frames} frames, {len(escenas)} escenas")


asyncio.run(main())
