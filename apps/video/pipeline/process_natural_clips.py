import os
import sys
import time
import subprocess
import imageio_ffmpeg

sys.path.append(os.path.dirname(__file__))
from semantic_match import CLIPS_CONFIG

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def process_natural():
    out_dir = os.path.join("public", "videos_enhanced")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print(f"Generando clips con COLOR 100% NATURAL + Denoise limpio + CAS 1080p")
    print("Sin curvas de contraluz artificiales")
    print("=" * 60)

    for idx, cfg in enumerate(CLIPS_CONFIG, 1):
        clip_id = cfg["id"]
        vfile = cfg["video_file"]
        start_t = cfg["start_time"]
        dur = round(cfg["end_time"] - start_t, 3)
        trf_file = f"{clip_id}.trf"
        out_mp4 = os.path.join(out_dir, f"{clip_id}_enh.mp4")

        print(f"\n[{idx}/{len(CLIPS_CONFIG)}] {clip_id}: {vfile} ({dur:.1f}s)")
        t0 = time.time()

        # Pass 1: Motion detection for stabilization
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
        p1 = subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if p1.returncode != 0:
            print(f"  Error Pass 1: {p1.stderr[-180:]}")
            continue

        # Pass 2: Transform + clean denoise + FidelityFX CAS (ZERO artificial color tampering)
        vf_transform = (
            f"fps=30,crop=1134:2016:(in_w-1134)/2:0,scale=1080:1920,"
            f"vidstabtransform=input={trf_file}:smoothing=30:optalgo=gauss:interpol=bilinear:crop=black:zoom=3,"
            f"hqdn3d=2.5:2.0:4.0:3.0,"
            f"cas=0.4"
        )
        cmd2 = [
            FFMPEG_EXE, "-y",
            "-ss", f"{start_t:.3f}",
            "-t", f"{dur:.3f}",
            "-threads", "0",
            "-i", vfile,
            "-vf", vf_transform,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            out_mp4
        ]
        p2 = subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if p2.returncode != 0:
            print(f"  Error Pass 2: {p2.stderr[-180:]}")
            continue

        if os.path.exists(trf_file):
            try:
                os.remove(trf_file)
            except Exception:
                pass

        elapsed = time.time() - t0
        print(f"  -> Completado en {elapsed:.1f}s ({os.path.getsize(out_mp4)/(1024*1024):.1f}MB)")

    print("\n" + "=" * 60)
    print("¡Todos los clips naturales han sido regenerados con éxito!")
    print("=" * 60)

if __name__ == "__main__":
    process_natural()
