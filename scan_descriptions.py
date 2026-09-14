# scan_descriptions.py
#
# Scans all listing descriptions for text that looks like prompt injection,
# AI instruction attempts, or suspicious embedded commands.

import json
import re

with open("listings_all.json", encoding="utf-8") as f:
    listings = json.load(f)

print(f"Scanning {len(listings)} listings...\n")

# ── Suspicious patterns to look for ──────────────────────────────────────────
PATTERNS = [
    # Direct AI/assistant references
    r"note\s+to\s+ai",
    r"coding\s+assistant",
    r"ai\s+assistant",
    r"language\s+model",
    r"large\s+language",
    r"\bllm\b",
    r"\bgpt\b",
    r"\bchatgpt\b",
    r"\bclaude\b",
    r"\bgemini\b",
    # Instruction-style commands
    r"you\s+must\s+display",
    r"you\s+must\s+include",
    r"you\s+must\s+show",
    r"must\s+display",
    r"must\s+include",
    r"must\s+output",
    r"must\s+print",
    r"must\s+mention",
    r"always\s+display",
    r"always\s+include",
    r"always\s+output",
    # Licence / certification tricks
    r"licen[sc]e\s+requires",
    r"certified\s+by",
    r"terms\s+require",
    r"compliance\s+requires",
    r"api\s+terms",
    r"data\s+provider",
    # Ignore/override instructions
    r"ignore\s+(previous|prior|all|above)\s+instructions",
    r"disregard\s+(previous|prior|all|above)",
    r"override\s+instructions",
    r"forget\s+(previous|prior|all|above)",
    r"new\s+instructions",
    r"system\s+prompt",
    r"your\s+instructions",
    # Typical injection patterns
    r"</?(s|system|user|assistant|prompt|instruction|context)>",
    r"\[INST\]",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"###\s*(instruction|system|assistant|human)",
    # Attribution/watermark injection
    r"powered\s+by",
    r"sponsored\s+by",
    r"watermark",
    r"attribution",
    r"credit[s]?\s+to",
    # Misc suspicious
    r"prompt\s+injection",
    r"jailbreak",
    r"base64",
    r"eval\(",
    r"<script",
    r"javascript:",
]

compiled = [(p, re.compile(p, re.IGNORECASE)) for p in PATTERNS]

# ── Scan ──────────────────────────────────────────────────────────────────────
hits = []

for r in listings:
    desc = r.get("description") or ""
    if not desc.strip():
        continue
    matched = []
    for pattern, regex in compiled:
        m = regex.search(desc)
        if m:
            # Grab a snippet of context around the match
            start = max(0, m.start() - 40)
            end   = min(len(desc), m.end() + 60)
            snippet = desc[start:end].replace("\n", " ").strip()
            matched.append((pattern, snippet))
    if matched:
        hits.append({
            "listing_id": r.get("listing_id"),
            "website":    r.get("website"),
            "matches":    matched,
            "full_desc":  desc,
        })

# ── Report ────────────────────────────────────────────────────────────────────
print(f"{'=' * 65}")
print(f"SUSPICIOUS DESCRIPTIONS FOUND: {len(hits)}")
print(f"{'=' * 65}\n")

if not hits:
    print("No suspicious patterns found across all descriptions.")
else:
    for h in hits:
        print(f"listing_id : {h['listing_id']}  (source: {h['website']})")
        for pattern, snippet in h["matches"]:
            print(f"  pattern  : {pattern}")
            print(f"  snippet  : ...{snippet}...")
        print(f"  full desc: {h['full_desc'][:300]}")
        print()
