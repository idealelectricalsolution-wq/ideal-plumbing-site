#!/usr/bin/env python3
"""
Diagnostic: lists every visible <p> block scoring below 70 Flesch,
with full text and metadata, so we can decide which need rewriting.
Run: python3 diagnose-flesch.py
"""
import re
from pathlib import Path

PATH = Path("src/pages/index.astro")

def count_syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    return max(1, len(re.findall(r'[aeiouy]+', word)))

def flesch(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return None
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if not sentences or not words:
        return None
    syllables = sum(count_syllables(w) for w in words)
    return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words)), 1)

content = PATH.read_text(encoding='utf-8')
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, flags=re.DOTALL)

results = []
for raw in paragraphs:
    text = re.sub(r'<[^>]+>', '', raw).strip()
    text = re.sub(r'\s+', ' ', text)
    if len(text) > 20:
        score = flesch(text)
        if score is not None:
            results.append((score, len(text), text))

# Show every paragraph under 70, sorted worst first
problem = sorted([r for r in results if r[0] < 70])
print(f"=== {len(problem)} paragraphs below 70 ===\n")
for i, (score, length, text) in enumerate(problem, 1):
    print(f"#{i}  Flesch: {score}   ({length} chars)")
    print(f"     {text[:300]}")
    print()

# Quick stats by length bucket
print("=== Score distribution by paragraph length ===")
short = [r[0] for r in results if r[1] < 80]
medium = [r[0] for r in results if 80 <= r[1] < 200]
long_ = [r[0] for r in results if r[1] >= 200]
def stats(name, scores):
    if scores:
        print(f"  {name:8s}  count={len(scores):3d}  avg={sum(scores)/len(scores):.1f}  min={min(scores)}  below70={sum(1 for s in scores if s<70)}")
    else:
        print(f"  {name:8s}  count=0")
stats("<80 chr", short)
stats("80-200",  medium)
stats(">=200",   long_)

print(f"\n=== All paragraphs ===")
print(f"  Total:    {len(results)}")
print(f"  Avg:      {sum(r[0] for r in results)/len(results):.1f}")
print(f"  Avg ≥80c: {sum(r[0] for r in results if r[1] >= 80)/max(1,sum(1 for r in results if r[1] >= 80)):.1f}  (excludes micro-text)")
