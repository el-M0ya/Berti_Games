"""Lista las portadas con backslashes de sobra en los catalogos."""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
LINEA = re.compile(r"^\s{4}cover: (.+),$", re.M)

total = 0
for f in sorted(RAIZ.glob("src/data/games/*.js")):
    if f.name == "index.js":
        continue
    texto = f.read_text(encoding="utf-8")
    malos = [m.group(1) for m in LINEA.finditer(texto) if m.group(1).count("\\") > 2]
    if malos:
        total += len(malos)
        print(f"{f.name:14s} {len(malos)} portada(s) con backslashes de sobra")
        for m in malos:
            print("     ", m[:78])

print(f"\ntotal afectadas: {total}")