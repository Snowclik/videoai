import os
import subprocess
import urllib.request
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def create_sfx():
    sfx_dir = os.path.join("assets", "sfx")
    music_dir = os.path.join("assets", "music")
    os.makedirs(sfx_dir, exist_ok=True)
    os.makedirs(music_dir, exist_ok=True)
    
    print("[1/3] Generating synthetic SFX with ffmpeg...")
    
    # 1. Whoosh: dynamic swept bandpass noise
    whoosh_path = os.path.join(sfx_dir, "whoosh.wav")
    cmd_whoosh = [
        FFMPEG_EXE, "-y",
        "-f", "lavfi",
        "-i", "anoisesrc=d=0.5:c=white:r=44100",
        "-af", "bandpass=f=1200:width_type=h:w=900,volume=2.5,afade=t=in:ss=0:d=0.2,afade=t=out:st=0.2:d=0.3",
        whoosh_path
    ]
    subprocess.run(cmd_whoosh, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  Created: {whoosh_path}")
    
    # 2. Pop: short sine chirp
    pop_path = os.path.join(sfx_dir, "pop.wav")
    cmd_pop = [
        FFMPEG_EXE, "-y",
        "-f", "lavfi",
        "-i", "aevalsrc=sin(2*PI*(750 - 450*t)*t):s=44100:d=0.12",
        "-af", "volume=1.8,afade=t=out:st=0.04:d=0.08",
        pop_path
    ]
    subprocess.run(cmd_pop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  Created: {pop_path}")

    # 3. Bell / Chime (for highlighting key programs)
    bell_path = os.path.join(sfx_dir, "bell.wav")
    cmd_bell = [
        FFMPEG_EXE, "-y",
        "-f", "lavfi",
        "-i", "aevalsrc=0.5*sin(2*PI*1046.5*t)+0.3*sin(2*PI*2093*t):s=44100:d=0.7",
        "-af", "afade=t=out:st=0.05:d=0.65",
        bell_path
    ]
    subprocess.run(cmd_bell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  Created: {bell_path}")

    print("\n[2/3] Getting background music...")
    bg_music_path = os.path.join(music_dir, "background.mp3")
    
    # Try downloading a public domain lo-fi acoustic chill track or synthesize an ambient chord progression
    lofi_urls = [
        "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3",
        "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3"
    ]
    
    downloaded = False
    for url in lofi_urls:
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            print(f"  Downloading music from {url[:50]}...")
            with urllib.request.urlopen(req, timeout=10) as response, open(bg_music_path, 'wb') as out_file:
                out_file.write(response.read())
            if os.path.exists(bg_music_path) and os.path.getsize(bg_music_path) > 10000:
                print(f"  Background music downloaded: {os.path.getsize(bg_music_path)} bytes")
                downloaded = True
                break
        except Exception as e:
            print(f"  Download error: {e}")
            
    if not downloaded:
        print("  Generating smooth ambient lo-fi synthetic pad background...")
        # Generates a pleasant mellow chord progression ambient track (120 seconds loop)
        cmd_ambient = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi",
            "-i", "aevalsrc=0.15*sin(2*PI*220*t)+0.12*sin(2*PI*261.63*t)+0.1*sin(2*PI*329.63*t)+0.08*sin(2*PI*392*t):s=44100:d=120",
            "-af", "lowpass=f=800,volume=0.8,afade=t=in:ss=0:d=2,afade=t=out:st=117:d=3",
            "-b:a", "192k",
            bg_music_path
        ]
        subprocess.run(cmd_ambient, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  Ambient music generated: {bg_music_path}")

    print("\nAssets generation complete!")

if __name__ == "__main__":
    create_sfx()
