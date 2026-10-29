import json

with open('transcripts/all_transcripts.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for k in ['CAM_20260925105509_0006_D', 'CAM_20260925105732_0007_D', 'CAM_20260925110445_0009_D', 'CAM_20260925112834_0020_D', 'CAM_20260925114950_0024_D', 'CAM_20260925115114_0025_D']:
    print(f"\n*** {k} ***")
    for seg in d[k]['segments']:
        for w in seg['words']:
            print(f"   {w['start']:05.2f} - {w['end']:05.2f}: {w['word']}")
