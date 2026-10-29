import os
import sys
import time
import subprocess
import imageio_ffmpeg
import glob

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def enhance_all():
    in_dir = os.path.join("public", "videos_stabilized")
    out_dir = os.path.join("public", "videos_enhanced")
    os.makedirs(out_dir, exist_ok=True)
    
    clips = sorted(glob.glob(os.path.join(in_dir, "clip_*_stab.mp4")))
    
    if not clips:
        print("No stabilized clips found!")
        return

    print("=" * 60)
    print(f"Mejorando calidad de video y reduciendo ruido para {len(clips)} clips")
    print(f"Destino: {out_dir}")
    print("Cadena: Denoise 3D + Shadow Recovery Curve + FidelityFX CAS")
    print("=" * 60)

    vf = (
        "hqdn3d=3.0:2.5:5.0:4.0,"
        "curves=m='0/0 0.16/0.28 0.38/0.52 0.70/0.76 1/0.95':r='0/0 0.30/0.32 1/1':b='0/0 0.30/0.28 1/1',"
        "cas=0.55"
    )

    for idx, clip_path in enumerate(clips, 1):
        filename = os.path.basename(clip_path)
        clip_id = filename.replace("_stab.mp4", "")
        out_mp4 = os.path.join(out_dir, f"{clip_id}_enh.mp4")
        
        # Si ya existe y es mayor a 1MB, continuar
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000000:
            print(f"[{idx}/{len(clips)}] Ya existe: {out_mp4}. Omitiendo...")
            continue
            
        print(f"\n[{idx}/{len(clips)}] Procesando: {filename} -> {os.path.basename(out_mp4)}...")
        t0 = time.time()
        
        cmd = [
            FFMPEG_EXE, "-y",
            "-i", clip_path,
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "17",
            "-pix_fmt", "yuv420p",
            "-an",
            out_mp4
        ]
        
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"Error procesando {filename}: {res.stderr[-200:]}")
            if os.path.exists(out_mp4):
                os.remove(out_mp4)
            continue
            
        elapsed = time.time() - t0
        orig_size = os.path.getsize(clip_path) / (1024 * 1024)
        new_size = os.path.getsize(out_mp4) / (1024 * 1024)
        print(f"  Completado en {elapsed:.1f}s ({orig_size:.1f}MB -> {new_size:.1f}MB)")

    print("\n" + "=" * 60)
    print("¡Todos los clips han sido mejorados con éxito!")
    print("=" * 60)

if __name__ == "__main__":
    enhance_all()
