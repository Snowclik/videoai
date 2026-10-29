import json

with open("transcripts/all_transcripts.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for k, v in data.items():
    print(f"\n=================== {k} (Duration: {v['duration']}s) ===================")
    for s in v["segments"]:
        print(f"  [{s['start']}s -> {s['end']}s]: {s['text']}")
        words_preview = " ".join([f"{w['word']}({w['start']}-{w['end']})" for w in s["words"][:6]])
        if len(s["words"]) > 6:
            words_preview += " ... " + " ".join([f"{w['word']}({w['start']}-{w['end']})" for w in s["words"][-3:]])
        print(f"    Words: {words_preview}")
