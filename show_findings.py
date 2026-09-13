import json
with open("submission.json", encoding="utf-8") as f:
    d = json.load(f)
for i, finding in enumerate(d["findings"]):
    print(f"findings[{i}]  endpoint={finding['endpoint']}  category={finding['category']}")
    print(f"  evidence : {finding['evidence']}")
    print()
