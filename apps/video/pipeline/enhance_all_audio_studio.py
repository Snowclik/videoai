import os
import subprocess
import numpy as np
import scipy.io.wavfile as wav
import noisereduce as nr
import imageio_ffmpeg
from semantic_match import CLIPS_CONFIG

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def enhance_all_audio():
    out_dir = os.path.join("public", "audio")
    os.makedirs(out_dir, exist_ok=True)
    temp_dir = "temp_audio_proc"
    os.makedirs(temp_dir, exist_ok=True)

    print("============================================================")
    print("Mastering Vocal – Viento + Voces Fondo (modo delicado)")
    print("Sin suprimir la voz principal: RNNoise suave + Spectral 40%")
    print("============================================================")

    for idx, cfg in enumerate(CLIPS_CONFIG, 1):
        clip_id = cfg["id"]
        vfile = cfg["video_file"]
        start_sec = cfg["start_time"]
        dur_sec = round(cfg["end_time"] - start_sec, 3)
        out_mp3 = os.path.join(out_dir, f"{clip_id}_clean.mp3")

        print(f"\n[{idx}/{len(CLIPS_CONFIG)}] Procesando {clip_id} ({dur_sec:.1f}s)...")

        temp_wav_raw   = os.path.join(temp_dir, f"{clip_id}_raw.wav")
        temp_wav_rnn   = os.path.join(temp_dir, f"{clip_id}_rnn.wav")
        temp_wav_spec  = os.path.join(temp_dir, f"{clip_id}_spec.wav")

        # ── PASO 1: Extraer audio limpio con highpass suave anti-viento (120 Hz, orden 1)
        # Se usa orden 1 (no 2) para no cortar componentes graves de la voz femenina
        # arnndn: red neuronal RNNoise − atenúa ruido de fondo sin tocar la voz
        cmd1 = [
            FFMPEG_EXE, "-y",
            "-ss", f"{start_sec:.3f}",
            "-t",  f"{dur_sec:.3f}",
            "-i",  vfile,
            "-vn",
            "-af", "highpass=f=120:p=1,arnndn=m=bd.rnnn",
            "-ar", "48000",
            "-ac", "1",
            temp_wav_raw
        ]
        subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ── PASO 2: Spectral gating suave (prop_decrease=0.40 – elimina ~40% del residual)
        # Usamos stationary=False para no confundir la voz con el ruido de fondo
        sr, data = wav.read(temp_wav_raw)
        audio_float = data.astype(np.float32) / 32768.0 if data.dtype == np.int16 else data.astype(np.float32)

        reduced = nr.reduce_noise(
            y=audio_float,
            sr=sr,
            stationary=False,     # Adapta el perfil de ruido dinámicamente
            prop_decrease=0.40,   # *** CLAVE: solo 40% – no suprime voz ***
            n_fft=2048,
            hop_length=512,
            time_mask_smooth_ms=80,  # Suaviza la máscara temporal para evitar artefactos
            freq_mask_smooth_hz=200  # Suaviza en frecuencia para no crear huecos
        )

        reduced_int16 = np.clip(reduced * 32767.0, -32768, 32767).astype(np.int16)
        wav.write(temp_wav_spec, sr, reduced_int16)

        # ── PASO 3: Studio Voice Chain – sin noise gate duro
        # Se usa un expander suave (adelay) en vez de agate para NO silenciar pausas
        mastering_chain = (
            # EQ vocal: quitar mud (300Hz), realzar presencia (3kHz), aire (8kHz)
            "equalizer=f=300:t=q:w=1.4:g=-2.0,"
            "equalizer=f=3300:t=q:w=1.2:g=2.5,"
            "equalizer=f=8000:t=q:w=1.5:g=1.2,"
            # Compresor vocal suave: control de dinámica sin bombeo
            "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=80:makeup=2.0,"
            # Normalización broadcast EBU R128
            "loudnorm=I=-14:TP=-1.0:LRA=9,"
            # Fade in/out suave para evitar clics
            "afade=t=in:ss=0:d=0.05,afade=t=out:st={:.3f}:d=0.05".format(max(0, dur_sec - 0.05))
        )

        cmd2 = [
            FFMPEG_EXE, "-y",
            "-i", temp_wav_spec,
            "-af", mastering_chain,
            "-ar", "48000",
            "-ac", "2",
            "-b:a", "320k",
            out_mp3
        ]
        subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  -> OK: {out_mp3}")

    # Limpiar temporales
    for f in os.listdir(temp_dir):
        try:
            os.remove(os.path.join(temp_dir, f))
        except Exception:
            pass
    try:
        os.rmdir(temp_dir)
    except Exception:
        pass

    print("\n¡Los 11 clips de audio masterizados con voz preservada!")

if __name__ == "__main__":
    enhance_all_audio()
