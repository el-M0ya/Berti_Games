"""
Marca o desmarca juegos como favoritos, sin que tengas que editar 7.000
archivos a mano.

    # ver que hay marcados ahora
    python tools/mark_favorites.py --list

    # buscar primero cual es el id exacto
    python tools/mark_favorites.py --find "gta"

    # marcar (por id o por nombre)
    python tools/mark_favorites.py --add bloodborne --add "Shadow of the Colossus"

    # sacar
    python tools/mark_favorites.py --remove bloodborne

Con --dry-run no escribe nada.

Al cambiar algo, el script vuelve a generar los archivos que usa la web
(src/data/generated/), asi que no hay que acordarse de hacerlo aparte.
"""

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

ID = re.compile(r"^\s{4}id: '(.*)',$", re.M)
FAV = re.compile(r"^(\s{4})favorite: (true|false),$", re.M)
TITLE = re.compile(r"^\s{4}title: '(.*)',$", re.M)


def normalizar(texto: str) -> str:
    """Como el id de la web: sin tildes, sin mayusculas, con guiones."""
    s = unicodedata.normalize("NFKD", texto.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def catalogos():
    """Solo los archivos que son catalogos de verdad."""
    return [
        p
        for p in sorted(GAMES.glob("*.js"))
        if "_GAMES = [" in p.read_text(encoding="utf-8")
    ]


def listar() -> int:
    total = 0
    for path in catalogos():
        for bloque in re.split(r"\n  \{\n", path.read_text(encoding="utf-8"))[1:]:
            m = FAV.search(bloque)
            if m and m.group(2) == "true":
                ident = ID.search(bloque)
                titulo = TITLE.search(bloque)
                print(f"  {path.stem:9s} {ident.group(1):44s} {titulo.group(1)}")
                total += 1
    print(f"\n{total} juego(s) marcados como destacado.")
    if total == 0:
        print("No hay ninguno. Usa --add para marcar.")
    return 0


def buscar(texto: str) -> int:
    clave = normalizar(texto)
    encontrados = 0
    for path in catalogos():
        for bloque in re.split(r"\n  \{\n", path.read_text(encoding="utf-8"))[1:]:
            ident = ID.search(bloque)
            titulo = TITLE.search(bloque)
            if not ident or not titulo:
                continue
            if clave in normalizar(ident.group(1)) or clave in normalizar(titulo.group(1)):
                print(f"  {path.stem:9s} {ident.group(1):44s} {titulo.group(1)}")
                encontrados += 1
    print(f"\n{encontrados} coincidencia(s). Usá el id de la izquierda.")
    return 0


def coincidencias(patron: str):
    """
    Resuelve un patron a una lista de (consola, id, titulo).

    Primero busca el id exacto. Si no hay, busca un trozo, pero SOLO lo
    acepta si da un solo resultado: si "shadow of the colossus" matchea
    tres juegos, es demasiado ambiguo y hay que pedir el nombre exacto.
    """
    clave = normalizar(patron)
    exactas = []
    parciales = []

    for path in catalogos():
        for bloque in re.split(r"\n  \{\n", path.read_text(encoding="utf-8"))[1:]:
            ident = ID.search(bloque)
            titulo = TITLE.search(bloque)
            if not ident or not titulo:
                continue
            dato = {
                "consola": path.stem,
                "id": ident.group(1),
                "titulo": titulo.group(1),
            }
            if normalizar(dato["id"]) == clave:
                exactas.append(dato)
            elif clave and (
                clave in normalizar(dato["id"]) or clave in normalizar(dato["titulo"])
            ):
                parciales.append(dato)

    return exactas if exactas else parciales


def aplicar(patrones: list[str], valor: bool, dry: bool) -> int:
    """Marca o desmarca. Acepta el id exacto o un trozo del nombre."""
    a_marcar: dict[str, dict] = {}

    # 1. Resolver cada patron a juegos concretos, antes de tocar nada.
    for patron in patrones:
        hallados = coincidencias(patron)

        if not hallados:
            print(f"\n  OJO: no se encontro ningun juego con '{patron}'.")
            print('       Proba con:  python tools/mark_favorites.py --find "%s"' % patron)
            continue

        if len(hallados) > 1:
            print(f"\n  OJO: '{patron}' matchea {len(hallados)} juegos:")
            for h in hallados:
                print(f"         {h['consola']:9s} {h['id']:44s} {h['titulo']}")
            print("       No marco ninguno. Usa el id exacto de arriba.")
            continue

        a_marcar[hallados[0]["id"]] = hallados[0]

    if not a_marcar:
        print("\nNo se marco nada.")
        return 0

    # 2. Aplicar sobre los archivos.
    cambiados = 0
    for path in catalogos():
        texto = path.read_text(encoding="utf-8")
        bloques = re.split(r"\n  \{\n", texto)
        salida = [bloques[0]]

        for bloque in bloques[1:]:
            ident = ID.search(bloque)
            if not ident or ident.group(1) not in a_marcar:
                salida.append(bloque)
                continue

            info = a_marcar[ident.group(1)]
            actual = FAV.search(bloque)
            estado = actual.group(2) if actual else "false"

            if estado == str(valor).lower():
                ya = "ya estaba marcado" if valor else "ya estaba sin marcar"
                print(f"  (sin cambio) {info['consola']:9s} {info['titulo']}  <- {ya}")
                salida.append(bloque)
                continue

            bloque = FAV.sub(
                lambda mt: f"{mt.group(1)}favorite: {str(valor).lower()},", bloque, count=1
            )
            cambiados += 1
            accion = "marcado   " if valor else "desmarcado"
            print(f"  {accion} {info['consola']:9s} {info['titulo']}")
            salida.append(bloque)

        if not dry and salida != bloques:
            path.write_text("\n  {\n".join(salida), encoding="utf-8")

    print(f"\n{cambiados} juego(s) {'marcados' if valor else 'desmarcados'}.")
    repartir(dry)
    return 0


def repartir(dry: bool) -> None:
    """Vuelve a generar los archivos que usa la web."""
    if dry:
        print("(dry run: no se reparten los archivos)")
        return
    print("\nRepartiendo los archivos para la web...")
    subprocess.run([sys.executable, str(ROOT / "tools" / "split_catalog.py")], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Marca juegos como favoritos.")
    parser.add_argument("--list", action="store_true", help="Muestra los marcados")
    parser.add_argument("--find", metavar="TEXTO", help="Busca el id de un juego")
    parser.add_argument("--add", nargs="*", default=[], metavar="NOMBRE", help="Marca como favorito")
    parser.add_argument("--remove", nargs="*", default=[], metavar="NOMBRE", help="Saca de favoritos")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.find:
        return buscar(args.find)
    if args.add:
        return aplicar(args.add, True, args.dry_run)
    if args.remove:
        return aplicar(args.remove, False, args.dry_run)
    return listar()


if __name__ == "__main__":
    sys.exit(main())