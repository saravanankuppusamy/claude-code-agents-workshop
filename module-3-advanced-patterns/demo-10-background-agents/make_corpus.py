#!/usr/bin/env python3
"""Generate corpus/ - 120 short customer reviews for the background indexer demo.
    python3 make_corpus.py [N]
"""
import os, random, sys
random.seed(3)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 120
os.makedirs("corpus", exist_ok=True)
titles = ["The Tide Clock", "Salt and Cedar", "Paper Boats", "Drop Anchor", "The Quiet Ledger"]
good = ["couldn't put it down", "beautiful prose", "arrived quickly", "perfect gift"]
bad = ["arrived damaged", "pages missing", "wrong edition sent", "very slow delivery"]
for i in range(n):
    t = random.choice(titles)
    stars = random.choice([1, 2, 3, 4, 5, 5, 4])
    phrase = random.choice(good if stars >= 4 else bad)
    with open(f"corpus/review-{i:04d}.md", "w") as f:
        f.write(f"# Review {i}\n\n- book: {t}\n- stars: {stars}\n\n{phrase.capitalize()}. "
                f"{'Would recommend.' if stars >= 4 else 'Not happy.'}\n")
print(f"wrote {n} reviews to corpus/")
