"""Genera cues.js y public/sfx_track.wav.

Fuente única de verdad para imagen y sonido:
  - Alinea las palabras del guion con la voz REAL usando faster-whisper (timestamps por palabra).
  - Agrupa las palabras en "chunks" de subtítulo cinético (con estilo, posición y énfasis).
  - Genera el calendario de tecleo (tiempo exacto de cada carácter, con ritmo humano).
  - Sintetiza una pista de efectos (teclas al ritmo del tecleo, whooshes, pops, dings, ticks)
    con EXACTAMENTE los mismos tiempos que usa el HTML => sincronía perfecta.

Uso (desde apps/video):  python build_cues.py
"""
import difflib
import json
import random
import re
import unicodedata
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).parent
SR = 48000
FPS = 30

tl = json.loads((ROOT / "src" / "timeline.json").read_text(encoding="utf-8"))
SCENES = [round(s["start_frame"] / FPS, 3) for s in tl["scenes"]]
END = round(tl["total_frames"] / FPS, 3)

LINEAS = [l.strip() for l in (ROOT / "guion" / "anders_hejlsberg.txt").read_text(encoding="utf-8").splitlines() if l.strip()]


# ───────────────────────── 1. Palabras del guion ─────────────────────────
def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("#", "sharp")
    return re.sub(r"[^a-z0-9]", "", s)


def script_words():
    out = []
    for li, linea in enumerate(LINEAS):
        toks = linea.split()
        i = 0
        while i < len(toks):
            w = toks[i]
            # "punto net," se pronuncia "dot net": una sola palabra visual ".NET,"
            if norm(w) == "punto" and i + 1 < len(toks) and norm(toks[i + 1]).startswith("net"):
                trailing = re.search(r"[.,;:?!]+$", toks[i + 1])
                out.append({"w": ".NET" + (trailing.group(0) if trailing else ""), "n": "dotnet", "line": li})
                i += 2
                continue
            out.append({"w": w, "n": norm(w), "line": li})
            i += 1
    return out


# ───────────────────────── 2. Alineación con Whisper ─────────────────────────
def transcribe():
    cache = ROOT / "assets" / "whisper_words.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    from faster_whisper import WhisperModel

    model_path = str(ROOT / "assets" / "whisper-base")
    model = WhisperModel(model_path, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(ROOT / "public" / "voz_masterizada.wav"), language="es",
                               word_timestamps=True, beam_size=5)
    words = []
    for s in segs:
        for w in s.words:
            words.append({"w": w.word.strip(), "s": float(w.start), "e": float(w.end)})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    return words


def sim(a, b):
    return 1.0 if a == b else difflib.SequenceMatcher(None, a, b).ratio()


def align(Dn, Wn):
    """Needleman-Wunsch sobre tokens normalizados. Devuelve {idx_D: idx_W}."""
    n, m = len(Dn), len(Wn)
    GAP = -0.5
    S = np.zeros((n + 1, m + 1))
    P = np.zeros((n + 1, m + 1), dtype=int)  # 0 diag, 1 arriba, 2 izquierda
    for i in range(1, n + 1):
        S[i, 0] = i * GAP
        P[i, 0] = 1
    for j in range(1, m + 1):
        S[0, j] = j * GAP
        P[0, j] = 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            r = sim(Dn[i - 1], Wn[j - 1])
            diag = S[i - 1, j - 1] + ((r - 0.45) * 3 if r >= 0.5 else -1.5)
            up = S[i - 1, j] + GAP
            left = S[i, j - 1] + GAP
            best = max(diag, up, left)
            S[i, j] = best
            P[i, j] = 0 if best == diag else (1 if best == up else 2)
    i, j, mp = n, m, {}
    while i > 0 or j > 0:
        if i > 0 and j > 0 and P[i, j] == 0:
            if sim(Dn[i - 1], Wn[j - 1]) >= 0.5:
                mp[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif i > 0 and (j == 0 or P[i, j] == 1):
            i -= 1
        else:
            j -= 1
    return mp


def aligned_words():
    D = script_words()
    try:
        W = transcribe()
        for w in W:
            w["n"] = norm(w["w"])
        mp = align([d["n"] for d in D], [w["n"] for w in W])
        used = set(mp.values())
        for i, d in enumerate(D):
            if i in mp:
                j = mp[i]
                d["s"], d["e"] = W[j]["s"], W[j]["e"]
                # palabra visual que abarca varios tokens de whisper ("C" + "sharp", "dot" + "net")
                if len(d["n"]) > len(W[j]["n"]) + 1:
                    if j - 1 >= 0 and (j - 1) not in used and d["n"].startswith(W[j - 1]["n"]):
                        d["s"] = W[j - 1]["s"]
                    k = j + 1
                    while k < len(W) and k not in used and (k - j) <= 2:
                        d["e"] = max(d["e"], W[k]["e"])
                        k += 1
        print(f"Whisper: {len(W)} tokens, {len(mp)}/{len(D)} palabras alineadas")
    except Exception as e:  # respaldo: tiempos estimados del pipeline anterior
        print("Whisper no disponible, uso estimación:", e)
        for d, t in zip(D, tl["words"]):
            d["s"], d["e"] = t["start_frame"] / FPS, t["end_frame"] / FPS

    # Interpolar las no alineadas
    known = [i for i, d in enumerate(D) if "s" in d]
    if not known:
        raise RuntimeError("sin palabras alineadas")
    i = 0
    while i < len(D):
        if "s" in D[i]:
            i += 1
            continue
        j = i
        while j < len(D) and "s" not in D[j]:
            j += 1
        grp = D[i:j]
        t0 = D[i - 1]["e"] if i > 0 else max(0.0, D[j]["s"] - 0.3 * len(grp))
        t1 = D[j]["s"] if j < len(D) else t0 + 0.3 * len(grp)
        if t1 - t0 < 0.07 * len(grp):
            t1 = t0 + 0.07 * len(grp)
        wts = [len(d["n"]) + 1 for d in grp]
        cur = t0
        for d, wt in zip(grp, wts):
            d["s"] = cur
            cur += (t1 - t0) * wt / sum(wts)
            d["e"] = cur
        i = j
    # Monotonía
    for k, d in enumerate(D):
        if k > 0:
            d["s"] = max(d["s"], D[k - 1]["s"] + 0.03)
        d["e"] = max(d["e"], d["s"] + 0.08)
    for k in range(len(D) - 1):
        D[k]["e"] = min(D[k]["e"], D[k + 1]["s"]) if D[k + 1]["s"] > D[k]["s"] + 0.08 else D[k]["e"]
    for d in D:
        d["s"], d["e"] = round(d["s"], 3), round(d["e"], 3)
    return D


# ───────────────────────── 3. Chunks de subtítulo cinético ─────────────────────────
STOP = {"de", "la", "el", "a", "y", "que", "en", "los", "las", "su", "se", "un", "una", "al", "del", "con", "por", "para", "como", "es", "o", "lo"}
HARD = re.compile(r"[.?!:]$")
SOFT = re.compile(r"[,;]$")
EMPH = {"csharp", "typescript", "pascal", "turbo", "anders", "hejlsberg", "microsoft", "dotnet", "javascript",
        "genio", "tipado", "web", "ochenta", "legado", "herramientas", "empoderen", "elegantes", "creador",
        "compilacion", "velocidad", "caotico", "escalabilidad", "inventó", "invento", "solitario", "diario"}
ACCENTS = ["#2563EB", "#0D9488", "#EA580C", "#7C3AED", "#0284C7", "#059669"]
STYLES = ["marker", "sticker", "outline", "mask"]
SLOTS = [1380, 1520, 1660]


def scene_of(t):
    k = 0
    for i, s in enumerate(SCENES):
        if t >= s - 0.01:
            k = i
    return k


def build_chunks(words):
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["s"] - w["e"]) if nxt else 9
        if HARD.search(w["w"]) or SOFT.search(w["w"]) or len(cur) >= 3 or gap > 0.45:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    # Palabras funcionales al final del chunk pasan al siguiente
    for k in range(len(chunks) - 1):
        c = chunks[k]
        while (len(c) > 1 and c[-1]["n"] in STOP and not (HARD.search(c[-1]["w"]) or SOFT.search(c[-1]["w"]))
               and len(chunks[k + 1]) < 3):
            chunks[k + 1].insert(0, c.pop())
    # Chunks de una sola palabra funcional se funden con el siguiente
    merged = []
    k = 0
    while k < len(chunks):
        c = chunks[k]
        if (len(c) == 1 and c[0]["n"] in STOP and k + 1 < len(chunks) and len(chunks[k + 1]) < 3
                and not (HARD.search(c[0]["w"]) or SOFT.search(c[0]["w"]))):
            chunks[k + 1] = c + chunks[k + 1]
        else:
            merged.append(c)
        k += 1
    return merged


def captions(words):
    rnd = random.Random(11)
    chs = build_chunks(words)
    out, last_slot = [], -1
    for i, c in enumerate(chs):
        s = c[0]["s"]
        e_last = c[-1]["e"]
        nxt = chs[i + 1][0]["s"] if i + 1 < len(chs) else None
        end = e_last + 0.35
        if nxt is not None and nxt - e_last < 0.6:
            end = max(e_last + 0.08, nxt - 0.03)
        slot = rnd.choice([x for x in range(3) if x != last_slot])
        last_slot = slot
        style = STYLES[i % len(STYLES)]
        sc = scene_of(s)
        out.append({
            "i": i, "s": round(s, 3), "e": round(end, 3), "style": style, "slot": SLOTS[slot],
            "rot": round(rnd.uniform(-3.5, 3.5), 2), "dx": rnd.randint(-45, 45),
            "accent": ACCENTS[sc], "scene": sc,
            "words": [{"t": w["w"], "s": w["s"], "e": w["e"], "emph": int(w["n"] in EMPH)} for w in c],
        })
    return out


# ───────────────────────── 4. Calendario de tecleo ─────────────────────────
SNIPPETS = {
    "pascal": ("program Turbo;\nbegin\n  writeln('Compilado');\n  writeln('en segundos!');\nend.", 14.0, 4.4),
    "csharp": ("using System;\n\nclass Hola {\n  static void Main() {\n    Console.WriteLine(\"C#\");\n  }\n}", 23.5, 4.8),
    "ts": ("interface Dev {\n  name: string;\n  typed: true;\n}\nconst a: Dev = {\n  name: \"Anders\",\n  typed: true\n};", 31.4, 5.6),
}


def typing_schedule(key, seed):
    text, start, total = SNIPPETS[key]
    rnd = random.Random(seed)
    gaps, prev_nl = [], True
    for i, ch in enumerate(text):
        if ch == "\n":
            g = rnd.uniform(1.8, 2.6)
            prev_nl = True
        elif prev_nl and ch == " ":
            g = 0.0  # auto-indent del editor: sin pulsación
        else:
            prev_nl = False
            g = rnd.uniform(0.55, 1.5)
            if i > 0 and text[i - 1] in ";{(":
                g *= 1.5
            if ch == " ":
                g *= 0.9
        gaps.append(g)
    tot_units = sum(gaps)
    t = start
    times, kinds = [], []
    for ch, g in zip(text, gaps):
        times.append(round(t, 3))
        kinds.append("enter" if ch == "\n" else ("space" if ch == " " and g > 0 else ("indent" if ch == " " else "key")))
        t += total * g / tot_units
    return {"text": text, "start": start, "end": round(t, 3), "times": times, "kinds": kinds}


# ───────────────────────── 5. Eventos / pops ─────────────────────────
def find_after(words, norms, after=0.0):
    """Primer tiempo de palabra cuyo norm esté en 'norms' y s >= after."""
    for w in words:
        if w["n"] in norms and w["s"] >= after:
            return w["s"]
    return after


def build_pops(words):
    p = {
        "s0_csharp": 0.9, "s0_ts": 1.45, "s0_pascal": 2.0, "s0_center": 2.65, "s0_lines": 2.35,
        "s1_photo1": 5.75, "s1_photo2": 6.45, "s1_chip1": 7.5, "s1_chip2": 8.2,
        "s2_window": 13.55, "s2_shot": 15.6, "s2_floppy": 16.5, "s2_compile": 19.2, "s2_done": 19.95,
        "s3_window": 23.0, "s3_icon1": 25.9, "s3_icon2": 26.6, "s3_icon3": 27.3,
        "s4_window": 31.2, "s4_js": 33.3, "s4_bug1": 33.7, "s4_bug2": 34.1, "s4_bug3": 34.5,
        "s4_shield": 36.6, "s4_ts": 37.3, "s4_chip1": 38.6, "s4_chip2": 39.3,
    }
    s5 = SCENES[5]
    p["s5_node1"] = round(find_after(words, {"compilar"}, s5) - 0.05, 3)
    p["s5_node2"] = round(find_after(words, {"dominar"}, s5) - 0.05, 3)
    p["s5_node3"] = round(find_after(words, {"vision"}, s5) - 0.05, 3)
    p["s5_card"] = round(find_after(words, {"crear"}, s5) - 0.35, 3)
    return p


# ───────────────────────── 6. Síntesis de efectos ─────────────────────────
rng = np.random.default_rng(7)


def key_sound(kind):
    n = int(0.11 * SR)
    t = np.arange(n) / SR
    click = np.diff(rng.standard_normal(n) * np.exp(-t / 0.0030), prepend=0)
    base = {"key": 170, "space": 115, "enter": 95}[kind] * rng.uniform(0.92, 1.12)
    tau = {"key": 0.020, "space": 0.035, "enter": 0.040}[kind]
    thock = np.sin(2 * np.pi * base * t * (1 + 0.25 * np.exp(-t / 0.01))) * np.exp(-t / tau)
    tick = np.sin(2 * np.pi * rng.uniform(2600, 3800) * t) * np.exp(-t / 0.0018)
    s = 0.5 * click + 1.0 * thock + 0.3 * tick
    return s * rng.uniform(0.72, 1.0) * {"key": 1.0, "space": 1.2, "enter": 1.3}[kind]


def key_release():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.diff(rng.standard_normal(n) * np.exp(-t / 0.002), prepend=0) * 0.30


def whoosh(dur=0.9, up=True):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    a = 0.015 + 0.55 * ((t ** 2) if up else ((1 - t) ** 2))
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    y = 0.6 * y + 2.5 * np.diff(y, prepend=0)
    y *= np.sin(np.pi * np.clip(t, 0, 1) ** 1.4) ** 2
    return y / (np.max(np.abs(y)) + 1e-9)


def riser(dur=0.7):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    y = np.diff(rng.standard_normal(n), prepend=0) * (t ** 2.5)
    return y / (np.max(np.abs(y)) + 1e-9)


def impact():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    f = 42 + 110 * np.exp(-t / 0.05)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    b, a = signal.butter(2, 900 / (SR / 2))
    nz = signal.lfilter(b, a, rng.standard_normal(n)) * np.exp(-t / 0.06)
    return boom + 0.6 * nz


def pop(pitch=1.0):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    f = (350 + 1100 * np.exp(-t / 0.018)) * pitch
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)


def ding(f0=1568.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t / (0.5 / m)) for m, a in [(1, 1.0), (2.0, 0.35), (3.01, 0.2)])
    return s * (1 - np.exp(-t / 0.002))


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.004) * 0.6 + np.diff(rng.standard_normal(n) * np.exp(-t / 0.002), prepend=0) * 0.2


def chime():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2093 * t) + 0.5 * np.sin(2 * np.pi * 3136 * t)) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.002))


def mix_sfx(typing, pops, caps):
    N = int((END + 1.5) * SR)
    m = np.zeros(N)

    def add(snd, t, g):
        i = int(t * SR)
        if i < 0 or i >= N:
            return
        seg = snd[: N - i]
        m[i:i + len(seg)] += seg * g

    # Transiciones: riser -> whoosh -> impacto exactamente en el corte
    for k, t in enumerate(SCENES[1:], start=1):
        add(riser(0.65), t - 0.65, 0.22)
        add(whoosh(0.9, up=True), t - 0.45, 0.55)
        add(impact(), t - 0.02, 0.55)
    add(impact(), 0.0, 0.40)  # arranque

    # Teclas al ritmo exacto del tecleo
    for sch in typing.values():
        for tm, kd in zip(sch["times"], sch["kinds"]):
            if kd == "indent":
                continue
            add(key_sound(kd), tm, 0.75)
            add(key_release(), tm + 0.07, 0.6)
        add(ding(1318), sch["end"] + 0.12, 0.22)

    # Pops de elementos gráficos
    pitches = {"s4_bug1": 0.6, "s4_bug2": 0.55, "s4_bug3": 0.5}
    for name, t in pops.items():
        if name in ("s2_compile",):
            add(riser(0.7), t, 0.25)
        elif name in ("s2_done", "s4_shield"):
            add(ding(1760), t, 0.30)
        elif name.endswith("_lines") or name.endswith("_window"):
            add(whoosh(0.5, up=True), t - 0.25, 0.25)
        else:
            add(pop(pitches.get(name, 1.0 + rng.uniform(-0.08, 0.1))), t, 0.45)

    # Ticks suaves por cada chunk de subtítulo y chime en la primera palabra enfatizada
    for c in caps:
        add(tick(), c["s"], 0.10)
        for w in c["words"]:
            if w["emph"]:
                add(chime(), w["s"], 0.07)
                break

    peak = np.max(np.abs(m)) + 1e-9
    m = np.tanh(m / peak * 1.4) / 1.4  # limitador suave
    m *= 0.42 / (np.max(np.abs(m)) + 1e-9)  # pico ≈ -7.5 dBFS (la voz va al frente)
    wavfile.write(str(ROOT / "public" / "sfx_track.wav"), SR, (m * 32767).astype(np.int16))
    return float(np.max(np.abs(m)))


# ───────────────────────── 7. Main ─────────────────────────
def main():
    words = aligned_words()
    caps = captions(words)
    typing = {k: typing_schedule(k, seed) for k, seed in (("pascal", 3), ("csharp", 5), ("ts", 9))}
    pops = build_pops(words)

    # Tiempos de la frase final (cita) para sincronizar su aparición
    s5 = SCENES[5]
    qn = ["crear", "herramientas", "elegantes", "que", "empoderen", "a", "los", "desarrolladores"]
    qtimes = []
    idx = next((i for i, w in enumerate(words) if w["n"] == "crear" and w["s"] >= s5), None)
    if idx is not None:
        qtimes = [words[idx + k]["s"] for k in range(min(len(qn), len(words) - idx))]

    peak = mix_sfx(typing, pops, caps)

    cues = {"fps": FPS, "end": END, "scenes": SCENES, "pops": pops, "typing": typing,
            "captions": caps, "quote": qtimes}
    (ROOT / "cues.js").write_text("window.CUES = " + json.dumps(cues, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"OK cues.js: {len(caps)} chunks, {sum(len(c['words']) for c in caps)} palabras, SFX pico {peak:.2f}")
    for c in caps:
        print(f"  {c['s']:6.2f}-{c['e']:6.2f} [{c['style']:7}] " + " ".join(w["t"] for w in c["words"]))


if __name__ == "__main__":
    main()
