import numpy as np
import scipy.io.wavfile as wav
import os

def create_subtle_transition_sfx():
    os.makedirs("public/sfx", exist_ok=True)
    sr = 48000
    duration = 0.35 # 350 ms, rápido y dinámico
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # 1. Soft clean whoosh / air texture (bandpassed noise with frequency sweep)
    np.random.seed(42)
    noise = np.random.normal(0, 1, len(t))
    # Sweep filter simulated with modulated sine window
    envelope_noise = np.sin(np.pi * t / duration) ** 2
    # Sine sweep for pitch lift: 280Hz -> 680Hz (warm, friendly, modern UI feel)
    freq = 280 + (680 - 280) * (t / duration) ** 1.8
    phase = 2 * np.pi * np.cumsum(freq) / sr
    tone = np.sin(phase)
    
    # Chime harmonics (subtle, 880Hz A5 + 1320Hz E6)
    harmonic1 = 0.3 * np.sin(2 * np.pi * 880 * t) * np.exp(-t * 14)
    harmonic2 = 0.15 * np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 20)
    
    # Combined sound: 70% soft warm sweep + 30% soft modern chime
    env_tone = np.sin(np.pi * (t / duration) ** 0.8) ** 2
    sound = (tone * 0.45 * env_tone) + (noise * 0.15 * envelope_noise) + harmonic1 + harmonic2
    
    # Normalize to -6dB peak
    sound = sound / (np.max(np.abs(sound)) + 1e-6) * 0.55
    sound_int16 = (sound * 32767).astype(np.int16)
    
    out_path = "public/sfx/topic_transition.wav"
    wav.write(out_path, sr, sound_int16)
    print(f"Generated clean topic transition SFX: {out_path}")

if __name__ == "__main__":
    create_subtle_transition_sfx()
