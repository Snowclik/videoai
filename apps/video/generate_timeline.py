import json
import re
import os

def parse_vtt(filepath):
    cues = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.read().splitlines()
    
    current_cue = None
    for line in lines:
        if '-->' in line:
            parts = line.split('-->')
            start = parts[0].strip()
            end = parts[1].strip().split(' ')[0]
            current_cue = {'start': start, 'end': end, 'text': ''}
        elif current_cue is not None:
            if line.strip() == '':
                cues.append(current_cue)
                current_cue = None
            else:
                current_cue['text'] += line + ' '
    if current_cue:
        cues.append(current_cue)
    return cues

def time_to_seconds(t_str):
    t_str = t_str.replace(',', '.')
    parts = t_str.split(':')
    if len(parts) == 3:
        return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0])*60 + float(parts[1])
    return 0

def main():
    vtt = parse_vtt("assets/subtitulos.vtt")
    
    words_data = []
    fps = 30
    
    for cue in vtt:
        start_seconds = time_to_seconds(cue['start'])
        end_seconds = time_to_seconds(cue['end'])
        
        start_frame = int(start_seconds * fps)
        end_frame = int(end_seconds * fps)
        
        text = cue['text'].replace("\n", " ").strip()
        tokens = text.split(" ")
        duration = end_frame - start_frame
        frames_per_word = max(1, int(duration / len(tokens)))
        
        for i, token in enumerate(tokens):
            w_start = start_frame + (i * frames_per_word)
            w_end = w_start + frames_per_word - 1
            words_data.append({
                "word": token,
                "start_frame": w_start,
                "end_frame": w_end
            })

    phrases = []
    current_phrase = []
    
    for i, w in enumerate(words_data):
        current_phrase.append(w)
        if len(current_phrase) >= 4 or i == len(words_data) - 1:
            phrases.append(current_phrase)
            current_phrase = []

    total_frames = words_data[-1]["end_frame"] + 90 if words_data else 300

    c1_end = int(total_frames * 0.3)
    c2_end = int(total_frames * 0.6)
    c3_end = int(total_frames * 0.85)

    clips = [
        {
            "id": "clip_csharp",
            "type": "video",
            "title": "C# Code",
            "video_source": "broll/csharp_code.mp4",
            "clean_audio": "voz_masterizada.wav",
            "tag": "CREACIÓN",
            "is_theme_transition": True,
            "has_zoom": True,
            "global_start_frame": 0,
            "source_start_frame": 0,
            "duration_frames": c1_end,
            "words": [w for w in words_data if w["start_frame"] < c1_end]
        },
        {
            "id": "clip_anders",
            "type": "video",
            "title": "Anders Hejlsberg",
            "video_source": "broll/software_engineer.mp4",
            "clean_audio": "sfx/keyboard.wav",
            "tag": "EL GENIO",
            "is_theme_transition": True,
            "has_zoom": True,
            "global_start_frame": c1_end,
            "source_start_frame": 0,
            "duration_frames": c2_end - c1_end,
            "words": [w for w in words_data if w["start_frame"] >= c1_end and w["start_frame"] < c2_end]
        },
        {
            "id": "clip_servers",
            "type": "video",
            "title": "Servers and Scale",
            "video_source": "broll/server_room.mp4",
            "clean_audio": "sfx/whoosh.wav",
            "tag": "ESCALABILIDAD",
            "is_theme_transition": True,
            "has_zoom": True,
            "global_start_frame": c2_end,
            "source_start_frame": 0,
            "duration_frames": c3_end - c2_end,
            "words": [w for w in words_data if w["start_frame"] >= c2_end and w["start_frame"] < c3_end]
        },
        {
            "id": "clip_sources",
            "type": "video",
            "title": "Sources",
            "video_source": "broll/csharp_code.mp4",
            "clean_audio": "sfx/keyboard.wav",
            "tag": "FUENTES",
            "is_theme_transition": True,
            "has_zoom": True,
            "global_start_frame": c3_end,
            "source_start_frame": c3_end % 100,
            "duration_frames": total_frames - c3_end,
            "words": [w for w in words_data if w["start_frame"] >= c3_end]
        }
    ]

    timeline = {
        "metadata": {
            "title": "Anders Hejlsberg",
            "width": 1080,
            "height": 1920,
            "fps": 30
        },
        "settings": {
            "background_music": "music/lofi.mp3",
            "music_volume": 0.05
        },
        "total_frames": total_frames,
        "clips": clips
    }

    with open("src/timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
