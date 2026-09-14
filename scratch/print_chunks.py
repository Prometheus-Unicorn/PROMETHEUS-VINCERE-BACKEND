import json
from mini_run_pipeline import speech
transcript = speech.transcribe('remotion-app/public/source/test-video.mp4')
chunks = transcript.get('chunks', [])
for i, c in enumerate(chunks):
    print(f"Chunk {i:02d}: '{c.get('text', '')}'")
