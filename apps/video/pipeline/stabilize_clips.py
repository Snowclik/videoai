import os
import sys
import json
import time
import subprocess
import imageio_ffmpeg
from semantic_match import CLIPS_CONFIG

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def stabilize_all():
    out_dir = os.path.join("public", "videos_stabilized")
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"============================================================")
    print(f"Starting Video Stabilization with vidstab for {len(CLIPS_CONFIG)} clips")
    print(f"============================================================")
    
    for idx, cfg in enumerate(CLIPS_CONFIG, 1):
        clip_id = cfg["id"]
        vfile = cfg["video_file"]
        start_t = cfg["start_time"]
        dur = round(cfg["end_time"] - start_t, 3)
        trf_file = f"{clip_id}.trf"
        out_mp4 = os.path.join(out_dir, f"{clip_id}_stab.mp4")
        
        # Check if already stabilized (clip_01 is already done)
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000000:
            print(f"[{idx}/{len(CLIPS_CONFIG)}] {clip_id} already stabilized ({out_mp4}). Skipping...")
            continue
            
        print(f"\n[{idx}/{len(CLIPS_CONFIG)}] Stabilizing {clip_id}: {vfile} ({dur:.1f}s)")
        
        # Pass 1: Motion detection on vertical crop 1080x1920 @ 30fps
        vf_detect = f"fps=30,crop=1134:2016:(in_w-1134)/2:0,scale=1080:1920,vidstabdetect=stepsize=6:shakiness=7:accuracy=15:result={trf_file}"
        cmd1 = [
            FFMPEG_EXE, "-y",
            "-ss", f"{start_t:.3f}",
            "-t", f"{dur:.3f}",
            "-i", vfile,
            "-vf", vf_detect,
            "-f", "null",
            "-"
        ]
        t0 = time.time()
        p1 = subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if p1.returncode != 0:
            print(f"  Error Pass 1: {p1.stderr[-200:]}")
            continue
        print(f"  -> Pass 1 completed in {time.time() - t0:.1f}s")
        
        # Pass 2: Motion stabilization transform
        vf_transform = f"fps=30,crop=1134:2016:(in_w-1134)/2:0,scale=1080:1920,vidstabtransform=input={trf_file}:smoothing=30:optalgo=gauss:interpol=bilinear:crop=black:zoom=3"
        cmd2 = [
            FFMPEG_EXE, "-y",
            "-ss", f"{start_t:.3f}",
            "-t", f"{dur:.3f}",
            "-threads", "0",
            "-i", vfile,
            "-vf", vf_transform,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-an",
            out_mp4
        ]
        t1 = time.time()
        p2 = subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if p2.returncode != 0:
            print(f"  Error Pass 2: {p2.stderr[-200:]}")
            continue
        print(f"  -> Pass 2 completed in {time.time() - t1:.1f}s")
        
        # Remove trf file
        if os.path.exists(trf_file):
            try:
                os.remove(trf_file)
            except Exception:
                pass

    # Clean any stray .trf files
    for f in os.listdir("."):
        if f.endswith(".trf"):
            try:
                os.remove(f)
            except Exception:
                pass

    # Update timeline.json and src/timeline.json
    with open("timeline.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)
        
    for clip in timeline["clips"]:
        stab_path = f"videos_stabilized/{clip['id']}_stab.mp4"
        if os.path.exists(os.path.join("public", stab_path)):
            clip["video_source"] = stab_path
            clip["source_start_frame"] = 0
            clip["source_start_sec"] = 0

    with open("timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join("src", "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print("\n============================================================")
    print("All clips stabilized and timeline updated successfully!")
    print("============================================================")

if __name__ == "__main__":
    stabilize_all()
