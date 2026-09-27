"""
Escanea tus carpetas de juegos, saca los nombres y arma la lista.

Faena 1 de 2. Esta parte no necesita internet: solo mira el disco.

    python tools/scan_games.py --root "D:\\Juegos"

Que hace:
  1. Recorre las carpetas de cada consola (busca nombres tipo PS2, PS3, PS4,
     PS5, XBOX360 / Xbox 360 / etc, a cualquier nivel).
  2. Limpia los nombres de archivo: saca extensiones, codigos de producto
     entre corchetes, tags tipo "USA", "_PS3", anios sueltos, etc.
  3. Deduce un slug estable para cada juego.
  4. Escribe `game_scan.json` con todo lo encontrado.

Despues corres `fetch_metadata.py` para buscar caratulas y descripciones.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# Extensiones de archivo que cuentan como juego.
GAME_EXTENSIONS = {
    ".iso", ".bin", ".cue", ".gcm", ".gcz", ".rvz", ".wbfs",
    ".cso", ".pkg", ".7z", ".rar", ".zip", ".chd",
    ".mdf", ".nrg", ".img", ".m3u", ".xiso", ".wad", ".pbp",
}

# Nombres de carpeta -> slug de consola (se comparan normalizados).
CONSOLE_FOLDERS = {
    "ps2": "ps2",
    "playstation2": "ps2",
    "ps3": "ps3",
    "playstation3": "ps3",
    "xbox360": "xbox360",
    "xbox": "xbox360",
    "ps4": "ps4",
    "playstation4": "ps4",
    "ps5": "ps5",
    "playstation5": "ps5",
}

# Cualquier bloque entre parentesis, corchetes o llaves: "(USA)", "[SLUS-20958]"
BRACKET_BLOCK = re.compile(r"[\(\[\{]([^\(\)\[\]\{\}]*)[\)\]\}]")

# Codigo de producto: 2 a 5 letras, separador opcional, 2 a 6 digitos.
# Matches SLUS-20958, BCUS30790, PPSA02432, Guild01, TLH01.
# (2 digitos y no 1 para no confundirse con un numero de parte, ej. "War 2")
PRODUCT_CODE = re.compile(r"[A-Za-z]{2,5}[-_ ]?\d{2,6}")

# Idiomas: un bloque es de idiomas si TODOS sus tokens son codigos de idioma.
# Ej: "En,Fr,De,Es,It", "EN FR DE", "Eng-Spa", "Español/Ingles"
LANG_TOKENS = {
    "en", "eng", "english", "ingles",
    "fr", "fra", "fre", "french", "frances",
    "de", "deu", "ger", "german", "aleman",
    "es", "spa", "sp", "spanish", "espanol",
    "it", "ita", "italian", "italiano",
    "pt", "por", "portuguese", "portugues",
    "nl", "nld", "dutch", "holandes",
    "ru", "rus", "russian", "ruso",
    "ja", "jpn", "japanese", "japones",
    "ko", "kor", "korean", "coreano",
    "zh", "zho", "chi", "chinese", "chino",
    "sv", "swe", "swedish", "sueco",
    "no", "nor", "norwegian", "noruego",
    "da", "dan", "danish", "danes",
    "fi", "fin", "finnish", "finlandes",
    "pl", "pol", "polish", "polaco",
    "cs", "cze", "czech", "checo",
    "hu", "hun", "hungarian", "hungaro",
    "tr", "tur", "turkish", "turco",
    "ar", "ara", "arabic", "arabe",
    "he", "heb", "hebrew", "hebreo",
    "cat", "catalan", "catalan", "eus", "eu", "euskar",
}


def is_lang_block(s: str) -> bool:
    """True si el bloque es solo una lista de idiomas."""
    tokens = [t for t in re.split(r"[\s,/&+.-]+", s.strip()) if t]
    return bool(tokens) and all(t.lower() in LANG_TOKENS for t in tokens)

# Palabras que delatan un tag deaglomerado.
NOISE_WORDS = re.compile(
    r"\b(?:ntsc|pal|usa|eu|jp|jap|japan|bra|brazil|esp|spain|uk|eng|multi\d*|region|"
    r"version|edicion|edition|disc|disk|cd|dvd|gd|gdrom|volumen|volume|part|parte|"
    r"req|requires|crack|fixed|proper|repack|complet|full|final|default|"
    r"español|ingles|frances|aleman|italian|japanese|english)\b",
    re.I,
)

# Tags sueltos sin parentesis: _PS3, -USA, [2013]
LOOSE_TAG = re.compile(
    r"[\(\[\{]?\b(?:ps[1-5]|xbox\s?360|pc|switch|wii|psp|vita|ps vita|"
    r"usa|pal|ntsc|jap|bra|multi\d*|region|repack|proper|goty)\b[\)\]\}]?",
    re.I,
)

# Punto entre numeros: "GTA V.2013" / "FIFA.14"
DOT_NUMBER = re.compile(r"(?<=\d)\s*[.\-_]\s*(?=\d)")

# Partes que se limpian del final.
TRAILING_NOISE = re.compile(r"[\s._\-]+$")


def is_noise_block(inner: str) -> bool:
    """Decide si un bloque entre parentesis es un tag que hay que borrar."""
    s = inner.strip()
    if not s:
        return True
    # Codigo de producto: [SLUS-20958], [Guild01], [PPSA02432]
    if PRODUCT_CODE.search(s):
        return True
    # Cualquier tanda de 3+ digitos: (2013), (007), (Disc 2)
    if re.search(r"\d{3,}", s):
        return True
    # Idiomas: (En,Fr,De,Es,It)
    if len(s) > 1 and is_lang_block(s):
        return True
    # Palabras conocidas de tag
    if NOISE_WORDS.search(s):
        return True
    # Siglas en mayusculas de 4+ letras: (USA), (PAL), (DEFAULT), (MULTI5)
    letters = re.sub(r"[^A-Za-z]", "", s)
    if len(letters) >= 4 and s == s.upper() and any(c.isalpha() for c in s):
        return True
    return False


def clean_name(stem: str) -> str:
    """Saca el ruido tipico de los nombres de archivo y deja el titulo."""
    # 1. Sacar bloques entre parentesis, corchetes o llaves que sean tags.
    name = BRACKET_BLOCK.sub(lambda m: " " if is_noise_block(m.group(1)) else m.group(0), stem)
    # 2. Sacar tags sueltos sin parentesis.
    name = LOOSE_TAG.sub(" ", name)
    # 3. "GTA V.2013" -> "GTA V 2013"
    name = DOT_NUMBER.sub(" ", name)
    # 4. Separadores raros -> espacios.
    name = re.sub(r"[._]+", " ", name)
    # 5. Guiones usados como separador de subtitulo -> dos puntos.
    name = re.sub(r"\s+-\s+", ": ", name)
    # 6. Limpiar espacios y parentesis sueltos.
    name = re.sub(r"[\(\[\{]+\s*[\)\]\}]+", " ", name)
    name = re.sub(r"\s{2,}", " ", name)
    name = TRAILING_NOISE.sub("", name)
    return name.strip(" ()[]{}-_")


def slugify(text: str) -> str:
    """Convierte un titulo en un id estable para la web."""
    s = unicodedata.normalize("NFKD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def normalize_key(name: str) -> str:
    """Clave para comparar: sin espacios, guiones ni mayusculas."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def detect_console(folder: Path) -> str | None:
    """Deduce a que consola pertenece una carpeta a partir de su nombre."""
    key = normalize_key(folder.name)
    if key in CONSOLE_FOLDERS:
        return CONSOLE_FOLDERS[key]
    # "Juegos PS2", "Carpeta PS4", "Respaldo XBOX 360"
    for token, slug in CONSOLE_FOLDERS.items():
        if token in key:
            return slug
    return None


def looks_like_game(path: Path) -> bool:
    if path.is_dir():
        return False
    name = path.name.lower()
    if name.endswith(".gz") and name[:-3].endswith(tuple(GAME_EXTENSIONS)):
        return True
    return path.suffix.lower() in GAME_EXTENSIONS


def find_console_dirs(root: Path) -> list[tuple[str, Path]]:
    """Devuelve [(slug, carpeta)] para cada carpeta que se parezca a una consola."""
    found: list[tuple[str, Path]] = []
    for dirpath, dirnames, _ in os.walk(root):
        current = Path(dirpath)
        slug = detect_console(current)
        if slug:
            found.append((slug, current))
            # No bajamos mas: los juegos estan adentro de esta carpeta.
            dirnames[:] = []
    return found


def scan(root: Path) -> dict[str, list[dict]]:
    """Recorre `root` y devuelve {slug_consola: [entradas]}."""
    if not root.exists():
        raise SystemExit(f"No existe la carpeta: {root}")

    console_dirs = find_console_dirs(root)
    if not console_dirs:
        raise SystemExit(
            f"No encontre carpetas de consolas dentro de {root}.\n"
            "Renombra tus carpetas a PS2, PS3, PS4, PS5 o XBOX360 (o similar)."
        )

    result: dict[str, list[dict]] = {}
    for slug, folder in console_dirs:
        entries = result.setdefault(slug, [])
        seen: set[str] = set()

        for dirpath, _, filenames in os.walk(folder):
            for filename in sorted(filenames):
                path = Path(dirpath) / filename
                if not looks_like_game(path):
                    continue

                # Si es un .cue, tomamos el nombre del .bin que acompaña.
                if path.suffix.lower() == ".cue":
                    bin_path = path.with_suffix(".bin")
                    if not bin_path.exists():
                        continue
                    path = bin_path

                stem = path.name
                for ext in sorted(GAME_EXTENSIONS, key=len, reverse=True):
                    if stem.lower().endswith(ext):
                        stem = stem[: -len(ext)]
                        break

                title = clean_name(stem)
                if len(title) < 2:
                    continue

                key = normalize_key(title)
                if key in seen:
                    continue
                seen.add(key)

                entries.append({
                    "id": slugify(title),
                    "title": title,
                    "console": slug,
                    "file": str(path),
                })

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Escanea carpetas de juegos y arma la lista de titulos."
    )
    parser.add_argument(
        "--root",
        required=True,
        help='Carpeta con tus juegos. Ej: python tools/scan_games.py --root "D:\\Juegos"',
    )
    parser.add_argument(
        "--out",
        default=str(ROOT / "game_scan.json"),
        help="Archivo de salida (default: game_scan.json)",
    )
    args = parser.parse_args()

    root = Path(args.root)
    print(f"Escaneando: {root}\n")

    result = scan(root)

    total = 0
    for slug in sorted(result):
        games = result[slug]
        total += len(games)
        print(f"{slug:9s} {len(games):4d} juegos")
        for g in games[:5]:
            print(f"           - {g['title']}")
        if len(games) > 5:
            print(f"           ... y {len(games) - 5} mas")
    print(f"\nTotal: {total} juegos")

    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLista guardada en: {out}")
    print("Siguiente paso:  python tools/fetch_metadata.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
