import subprocess, pathlib

mp4 = 'output/gha_hakt_30s_pbd_1789349837_master.mp4'
out = pathlib.Path('scratch/critique_frames')
out.mkdir(exist_ok=True)

# Chunk 7 timestamps: 9.8s, 10.0s, 10.3s, 10.7s, 11.0s
# Chunk 20 timestamps: 24.5s, 25.0s, 25.4s, 25.7s
timestamps = [9.8, 10.0, 10.3, 10.7, 11.0, 24.5, 25.0, 25.4, 25.7]
for ts in timestamps:
    dst = out / f'frame_{ts:.1f}s.png'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ts), '-i', mp4, '-vframes', '1', '-q:v', '2', str(dst)], check=True)
    print(f'Extracted {dst.name}')
