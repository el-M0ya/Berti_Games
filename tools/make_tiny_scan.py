"""
Prueba rapida de la logica de fetch_metadata.py SIN tocar la red:
corta los JSON a 2 juegos por consola y comprueba que se ignoran las
consolas que no existen en la web.

Uso: python tools/make_tiny_scan.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "games"
OUT = ROOT / "_tiny_scan.json"

merged: dict[str, list[dict]] = {}
for path in sorted(GAMES.glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    for console, games in data.items():
        bucket = merged.setdefault(console, {})
        for g in games:
            key = g.get("id") or g.get("title", "")
            if key not in bucket or (g.get("cover") and not bucket[key].get("cover")):
                bucket[key] = g

merged = {c: list(b.values())[:2] for c, b in merged.items()}

OUT.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"{OUT.name} con " + ", ".join(f"{c}:{len(g)}" for c, g in sorted(merged.items())))
print(f"\nProbar con:\n  python tools/fetch_metadata.py --scan {OUT.name} --out-dir _test")
