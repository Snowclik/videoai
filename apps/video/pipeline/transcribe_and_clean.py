import os
import sys
import glob
import json
import subprocess
import numpy as np
import imageio_ffmpeg
from faster_whisper import WhisperModel

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def clean_audio(video_path, out_audio_path):
    os.makedirs(os.path.dirname(out_audio_path), exist_ok=True)
    # ffmpeg voice enhancement filter chain:
    # 1. afftdn: FFT-based denoiser
    # 2. highpass (80Hz) to cut rumble
    # 3. equalizer: slight cut at 300Hz (boxiness), boost at 3.2kHz (clarity)
    # 4. acompressor: smooth out volume peaks
    # 5. loudnorm: standardize loudness for speech
    filter_chain = (
        "afftdn=nr=14:nf=-25,"
        "highpass=f=80,lowpass=f=8500,"
        "equalizer=f=300:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1:g=3.0,"
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=50:makeup=2,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", video_path,
        "-vn",
        "-af", filter_chain,
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        out_audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error cleaning audio for {video_path}: {res.stderr}")
        return False
    return True

def load_audio_16k_mono(audio_path):
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", audio_path,
        "-f", "f32le",
        "-ac", "1",
        "-ar", "16000",
        "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return np.frombuffer(proc.stdout, dtype=np.float32)

def transcribe_all():
    video_files = sorted(glob.glob("videos/*.MP4"))
    os.makedirs("processed_audio", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    
    print(f"Loading faster-whisper model ('small' in Spanish)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    all_transcriptions = {}
    
    for idx, vpath in enumerate(video_files, 1):
        basename = os.path.splitext(os.path.basename(vpath))[0]
        clean_mp3 = os.path.join("processed_audio", f"{basename}_clean.mp3")
        
        print(f"\n[{idx}/{len(video_files)}] Processing audio: {vpath} -> {clean_mp3}")
        clean_audio(vpath, clean_mp3)
        
        print(f"[{idx}/{len(video_files)}] Loading audio buffer and transcribing...")
        audio_arr = load_audio_16k_mono(clean_mp3)
        duration = len(audio_arr) / 16000.0
        
        segments, info = model.transcribe(
            audio_arr,
            language="es",
            word_timestamps=True,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=350)
        )
        
        transcript_data = {
            "video_file": vpath.replace("\\", "/"),
            "audio_file": clean_mp3.replace("\\", "/"),
            "language": info.language,
            "duration": round(duration, 3),
            "segments": []
        }
        
        full_text_list = []
        for segment in segments:
            seg_data = {
                "id": segment.id,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "text": segment.text.strip(),
                "words": []
            }
            full_text_list.append(segment.text.strip())
            for word in (segment.words or []):
                seg_data["words"].append({
                    "word": word.word.strip(),
                    "start": round(word.start, 3),
                    "end": round(word.end, 3),
                    "probability": round(word.probability, 3)
                })
            transcript_data["segments"].append(seg_data)
            
        transcript_data["full_text"] = " ".join(full_text_list)
        out_json = os.path.join("transcripts", f"{basename}.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
        print(f"-> {basename}: \"{transcript_data['full_text']}\"")
        all_transcriptions[basename] = transcript_data
        
    with open("transcripts/all_transcripts.json", "w", encoding="utf-8") as f:
        json.dump(all_transcriptions, f, ensure_ascii=False, indent=2)
        
    print("\nAll 11 videos processed and transcribed successfully!")

if __name__ == "__main__":
    transcribe_all()
