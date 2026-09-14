import json
import whisper

print("Loading local Whisper model...")
model = whisper.load_model("base")

print("Transcribing scratch/pilates_audio.mp3 with word timestamps...")
result = model.transcribe("scratch/pilates_audio.mp3", word_timestamps=True)

print("\n--- FULL TEXT ---")
print(result["text"].strip())

print("\n--- WORD LEVEL TIMESTAMPS ---")
words_data = []
for seg in result["segments"]:
    start = seg["start"]
    end = seg["end"]
    txt = seg["text"].strip()
    print(f"[{start:.2f}s -> {end:.2f}s] {txt}")
    if "words" in seg:
        for w in seg["words"]:
            w_txt = w["word"].strip()
            w_start = w["start"]
            w_end = w["end"]
            print(f"   {w_start:6.2f}s - {w_end:6.2f}s: {w_txt}")
            words_data.append({
                "word": w_txt,
                "start": round(w_start, 3),
                "end": round(w_end, 3)
            })

with open("scratch/local_audio_transcript.json", "w", encoding="utf-8") as f:
    json.dump({
        "text": result["text"].strip(),
        "segments": result["segments"],
        "words": words_data
    }, f, indent=2)

print("\nSaved transcript to scratch/local_audio_transcript.json")
