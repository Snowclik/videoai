import os
import subprocess
import numpy as np
import scipy.io.wavfile as wav
import noisereduce as nr
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def test_chain():
    # 1. Highpass 140Hz (eliminates wind rumble) + Neural RNNoise + Spectral Denoise + Noise Gate
    vfile = "videos/CAM_20260925104731_0003_D.MP4"
    start_sec = 36.4
    dur_sec = 7.7
    
    # Step 1: Pre-filter highpass 140Hz + RNNoise neural isolation to 48kHz mono
    pre_cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{start_sec:.3f}",
        "-t", f"{dur_sec:.3f}",
        "-i", vfile,
        "-af", "highpass=f=140:p=2,arnndn=m=bd.rnnn",
        "-ar", "48000",
        "-ac", "1",
        "temp_stage1.wav"
    ]
    subprocess.run(pre_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Step 2: Spectral gating for ultra-clean transparency
    sr, data = wav.read("temp_stage1.wav")
    audio_float = data.astype(np.float32) / 32768.0
    reduced = nr.reduce_noise(
        y=audio_float,
        sr=sr,
        stationary=True,
        prop_decrease=0.75,
        n_fft=2048,
        hop_length=512
    )
    reduced_int16 = np.clip(reduced * 32767.0, -32768, 32767).astype(np.int16)
    wav.write("temp_stage2.wav", sr, reduced_int16)
    
    # Step 3: Noise Gate + Vocal Clarity EQ + Studio Leveler + Loudnorm
    # agate: when she is not speaking, background noise/whispers drop by -30dB!
    post_chain = (
        "agate=threshold=-34dB:ratio=3:range=-24dB:attack=15:release=120,"
        "equalizer=f=300:t=q:w=1.5:g=-2.5,"
        "equalizer=f=3300:t=q:w=1.2:g=3.0,"
        "equalizer=f=8000:t=q:w=1.5:g=1.5,"
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=50:makeup=2,"
        "loudnorm=I=-14:TP=-1.0:LRA=7,"
        "afade=t=in:ss=0:d=0.06,afade=t=out:st={:.3f}:d=0.06".format(dur_sec - 0.06)
    )
    
    final_cmd = [
        FFMPEG_EXE, "-y",
        "-i", "temp_stage2.wav",
        "-af", post_chain,
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "320k",
        "public/audio/clip_01_clean.mp3"
    ]
    subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup temp
    for p in ["temp_stage1.wav", "temp_stage2.wav"]:
        if os.path.exists(p):
            os.remove(p)
            
    print("clip_01_clean.mp3 processed with wind-cut, RNNoise neural isolation, and studio noise gate!")

if __name__ == "__main__":
    test_chain()
