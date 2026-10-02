"""
Busca problemas de formato en los catalogos:

  - saltos de linea DENTRO de un string de JavaScript: rompen el archivo
  - saltos escapados (\\n): no lo rompen, pero se ven raros en la web
  - comillas simples sin escapar: cierran el string antes de tiempo

Un ' sin escapar es lo mas grave, porque deja de ser JavaScript valido y el
build falla. Un salto de linea literal tambien.

Uso: python tools/check_format.py
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

CAMPOS = ("id", "title", "cover", "description")


def main() -> int:
    sin_cerrar = 0
    con_escapados = 0
    con_comillas = 0
    ejemplos_escapados = []

    for path in sorted(GAMES.glob("*.js")):
        if path.name == "index.js":
            continue

        texto = path.read_text(encoding="utf-8")
        # split('\n') y NO splitlines(): splitlines() tambien parte por U+2028
        # y U+2029, y daria un falso positivo de "string sin cerrar".
        lineas = texto.split("\n")

        rotos_archivo = 0
        escapados = 0
        comillas = 0

        # 1. Un campo que abre comilla y no la cierra en la misma linea.
        for i, linea in enumerate(lineas, 1):
            m = re.match(r"^\s{4}(\w+): '(.*)$", linea)
            if m and m.group(1) in CAMPOS and not re.search(r"',?$", linea):
                rotos_archivo += 1
                if sin_cerrar + rotos_archivo <= 5:
                    print(f"{path.name}:{i}  el string de {m.group(1)} sigue abierto")
                    print(f"    {linea.strip()[:100]}")
                    if i < len(lineas):
                        print(f"    {lineas[i].strip()[:100]}")

        # 2. Saltos escapados dentro de la descripcion.
        for m in re.finditer(r"^\s{4}description: '(.*)',?$", texto, re.M):
            valor = m.group(1)
            if "\\n" in valor or "\\r" in valor or "\\t" in valor:
                escapados += 1
                if len(ejemplos_escapados) < 5:
                    ejemplos_escapados.append((path.name, valor[:90]))

        # 3. Comillas simples sin escapar dentro del texto.
        for m in re.finditer(r"^\s{4}(title|description): '(.*)',?$", texto, re.M):
            valor = m.group(2)
            if re.search(r"(?<!\\)'", valor):
                comillas += 1
                if con_comillas + comillas <= 3:
                    i = valor.find("'")
                    print(f"{path.name}  comilla sin escapar en {m.group(1)}:")
                    print(f"    ...{valor[max(0, i - 45):i + 45]}...")

        sin_cerrar += rotos_archivo
        con_escapados += escapados
        con_comillas += comillas

        print(f"{path.name:12s} sin cerrar: {rotos_archivo:4d}  "
              f"escapados: {escapados:4d}  comillas: {comillas:4d}")

    print("-" * 62)
    print(f"strings sin cerrar:   {sin_cerrar}")
    print(f"saltos escapados:     {con_escapados}")
    print(f"comillas sin escapar: {con_comillas}")

    for nombre, texto in ejemplos_escapados:
        print(f"\n  {nombre}: {texto}")

    return 1 if (sin_cerrar or con_comillas) else 0


if __name__ == "__main__":
    sys.exit(main())