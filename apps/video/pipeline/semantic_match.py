import os
import json
import subprocess
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Exact matched takes with false starts and bloopers eliminated:
CLIPS_CONFIG = [
    {
        "id": "clip_01",
        "title": "Gancho - Introducción UTP Veraguas",
        "video_file": "videos/CAM_20260925104731_0003_D.MP4",
        "start_time": 36.4,
        "end_time": 44.1,
        "tag": "INTRO",
        "accent_color": "#FFC837"
    },
    {
        "id": "clip_02",
        "title": "Programa de Acompañamiento Psicológico",
        "video_file": "videos/CAM_20260925105509_0006_D.MP4",
        "start_time": 3.2,
        "end_time": 7.4,
        "tag": "PROGRAMA 1",
        "accent_color": "#00E5FF"
    },
    {
        "id": "clip_03",
        "title": "Espacio Seguro y Confidencial",
        "video_file": "videos/CAM_20260925105732_0007_D.MP4",
        "start_time": 5.5,
        "end_time": 14.8,
        "tag": "ACOMPAÑAMIENTO",
        "accent_color": "#00E5FF"
    },
    {
        "id": "clip_04",
        "title": "Prevención y Promoción de Salud Mental",
        "video_file": "videos/CAM_20260925110218_0008_D.MP4",
        "start_time": 0.9,
        "end_time": 6.2,
        "tag": "PROGRAMA 2",
        "accent_color": "#00E676"
    },
    {
        "id": "clip_05",
        "title": "Herramientas Preventivas",
        "video_file": "videos/CAM_20260925110445_0009_D.MP4",
        "start_time": 3.5,
        "end_time": 10.4,
        "tag": "PREVENCIÓN",
        "accent_color": "#00E676"
    },
    {
        "id": "clip_06",
        "title": "Actividades de Bienestar Mental",
        "video_file": "videos/CAM_20260925111549_0015_D.MP4",
        "start_time": 1.7,
        "end_time": 7.9,
        "tag": "ACTIVIDADES",
        "accent_color": "#00E676"
    },
    {
        "id": "clip_07",
        "title": "Programa Psicoeducativo - Estrés y Ansiedad",
        "video_file": "videos/CAM_20260925112834_0020_D.MP4",
        "start_time": 4.1,
        "end_time": 12.3,
        "tag": "PROGRAMA 3",
        "accent_color": "#FF9100"
    },
    {
        "id": "clip_08",
        "title": "Psicoeducativo - Logros Académicos",
        "video_file": "videos/CAM_20260925120625_0030_D.MP4",
        "start_time": 0.2,
        "end_time": 13.0,
        "tag": "PSICOEDUCATIVO",
        "accent_color": "#FF9100"
    },
    {
        "id": "clip_09",
        "title": "Orientación Profesional y Vocacional",
        "video_file": "videos/CAM_20260925120210_0028_D.MP4",
        "start_time": 0.5,
        "end_time": 12.7,
        "tag": "VOCACIONAL",
        "accent_color": "#D500F9"
    },
    {
        "id": "clip_10",
        "title": "¿Buscas un espacio seguro? En Psicología",
        "video_file": "videos/CAM_20260925114950_0024_D.MP4",
        "start_time": 8.3,
        "end_time": 15.4,
        "tag": "APOYO",
        "accent_color": "#FF5252"
    },
    {
        "id": "clip_11",
        "title": "Cierre - 100% Gratis y Confidencial",
        "video_file": "videos/CAM_20260925115114_0025_D.MP4",
        "start_time": 15.8,
        "end_time": 23.6,
        "tag": "¡TE ESPERAMOS!",
        "accent_color": "#FFD600"
    }
]

def clean_word_text(w):
    # Fix speech recognition quirks for UTP
    w = w.strip()
    if w.upper() in ["ATP", "ATP?"]:
        return "UTP?" if "?" in w else "UTP"
    if w.lower() in ["veraguas?", "veraguas"]:
        return "Veraguas?" if "?" in w else "Veraguas"
    if w.lower() == "buses":
        return "¿Buscas"
    if w.lower() == "prenen":
        return "frenen"
    if w.lower() == "belles":
        return "brilles"
    return w

def extract_sliced_audio(video_file, start_t, duration, out_audio_path):
    os.makedirs(os.path.dirname(out_audio_path), exist_ok=True)
    filter_chain = (
        "afftdn=nr=15:nf=-25,"
        "highpass=f=80,lowpass=f=8500,"
        "equalizer=f=300:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1:g=3.0,"
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=50:makeup=2,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "afade=t=in:ss=0:d=0.08,afade=t=out:st={}:d=0.08".format(max(0, duration - 0.08))
    )
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{start_t:.3f}",
        "-t", f"{duration:.3f}",
        "-i", video_file,
        "-vn",
        "-af", filter_chain,
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        out_audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_timeline():
    with open("transcripts/all_transcripts.json", "r", encoding="utf-8") as f:
        all_trans = json.load(f)
        
    os.makedirs("remotion_public/audio", exist_ok=True)
    os.makedirs("remotion_public/videos", exist_ok=True)
    
    fps = 30
    timeline = {
        "version": "1.0",
        "settings": {
            "fps": fps,
            "width": 1080,
            "height": 1920,
            "orientation": "vertical",
            "background_music": "music/background.mp3",
            "music_volume": 0.05,
            "transition_sfx": "sfx/whoosh.wav"
        },
        "total_duration_sec": 0,
        "total_frames": 0,
        "clips": []
    }
    
    current_global_frame = 0
    
    for cfg in CLIPS_CONFIG:
        vfile = cfg["video_file"]
        base = os.path.splitext(os.path.basename(vfile))[0]
        start_t = cfg["start_time"]
        end_t = cfg["end_time"]
        dur = round(end_t - start_t, 3)
        clip_frames = round(dur * fps)
        
        # Audio slicing for instant clean playback in Remotion
        clean_audio_rel = f"audio/{cfg['id']}_clean.mp3"
        clean_audio_path = os.path.join("remotion_public", clean_audio_rel)
        extract_sliced_audio(vfile, start_t, dur, clean_audio_path)
        
        # Extract and adjust word-level timestamps relative to clip start
        raw_words = []
        if base in all_trans:
            for seg in all_trans[base]["segments"]:
                for w in seg.get("words", []):
                    # Check if word falls in this clip window (with 0.3s tolerance)
                    if w["start"] >= (start_t - 0.25) and w["end"] <= (end_t + 0.35):
                        raw_words.append(w)
                        
        # Handle clip_02 words from take 2
        if cfg["id"] == "clip_02":
            raw_words = [
                {"word": "Uno", "start": 3.20, "end": 3.80},
                {"word": "de", "start": 3.80, "end": 3.94},
                {"word": "los", "start": 3.94, "end": 4.04},
                {"word": "programas", "start": 4.04, "end": 4.54},
                {"word": "que", "start": 4.54, "end": 4.62},
                {"word": "ofrecemos", "start": 4.62, "end": 5.12},
                {"word": "es", "start": 5.12, "end": 5.62},
                {"word": "el", "start": 5.62, "end": 5.72},
                {"word": "acompañamiento", "start": 5.72, "end": 6.48},
                {"word": "psicológico.", "start": 6.48, "end": 7.28}
            ]
            
        relative_words = []
        full_text_words = []
        for w in raw_words:
            w_text = clean_word_text(w["word"])
            rel_start = max(0.0, round(w["start"] - start_t, 3))
            rel_end = min(dur, round(w["end"] - start_t, 3))
            if rel_end > rel_start:
                start_frame = round(rel_start * fps)
                end_frame = round(rel_end * fps)
                relative_words.append({
                    "word": w_text,
                    "start_sec": rel_start,
                    "end_sec": rel_end,
                    "start_frame": start_frame,
                    "end_frame": end_frame
                })
                full_text_words.append(w_text)
                
        clip_entry = {
            "id": cfg["id"],
            "title": cfg["title"],
            "tag": cfg["tag"],
            "accent_color": cfg["accent_color"],
            "video_source": vfile.replace("\\", "/"),
            "clean_audio": clean_audio_rel.replace("\\", "/"),
            "source_start_sec": start_t,
            "source_end_sec": end_t,
            "source_start_frame": round(start_t * 60), # original video is ~60fps
            "duration_sec": dur,
            "duration_frames": clip_frames,
            "global_start_frame": current_global_frame,
            "global_end_frame": current_global_frame + clip_frames,
            "full_text": " ".join(full_text_words),
            "words": relative_words,
            "has_zoom": dur >= 5.0 # zoom-in animation if > 5s
        }
        
        timeline["clips"].append(clip_entry)
        current_global_frame += clip_frames
        
    timeline["total_duration_sec"] = round(current_global_frame / fps, 3)
    timeline["total_frames"] = current_global_frame
    
    with open("timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
        
    print(f"Generated timeline.json successfully!")
    print(f"Total Clips: {len(timeline['clips'])}")
    print(f"Total Duration: {timeline['total_duration_sec']}s ({timeline['total_frames']} frames @ {fps}fps)")
    for c in timeline["clips"]:
        print(f"  [{c['id']}] ({c['duration_sec']}s / {c['duration_frames']} frames) {c['tag']}: {c['full_text']}")

if __name__ == "__main__":
    build_timeline()
