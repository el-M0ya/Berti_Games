"""
Tests de limpieza de titulos de los catalogos.

Cada caso es un problema real que encontramos en los datos:

  - "Kung-Fu" se rompia en "Kung - Fu"
  - "007-BLOOD STONE" hay que separarlo
  - las notas de trabajo entre parentesis hay que quitarlas
  - "FINAL FANTASY XIII 2" no puede quedar en "Final Fantasy Xiii 2"
  - "(Arcade)" es una etiqueta de genero, no parte del nombre
  - los subtitulos de verdad hay que respetarlos

Uso: python tools/test_titles.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_catalog import clean_title, normalize_genres, fix_players  # noqa: E402

TITULOS = [
    # Mayusculas que pasan a Title Case.
    ("007-BLOOD STONE", "007 Blood Stone"),
    ("007 From Russia With Love", "007 From Russia With Love"),
    ("50 CENT", "50 Cent"),
    ("ARMY TWO 40 DAY", "Army Two 40 Day"),
    ("AVATAR. THE LEGEND OF AANG", "Avatar. The Legend of Aang"),
    ("ASSASSINS CREED BROTHEHOOOD", "Assassins Creed Brothehoood"),
    # El apostrofo mal escrito se arregla; "HOT" se queda porque el titulo
    # ya venia mezclado y no se toca. El acento va como escape para que
    # check_text.py no se queje de este archivo.
    ("HOT Wheels World\u00b4s Best Driver", "HOT Wheels World's Best Driver"),

    # Numeros romanos y siglas se respetan.
    ("FINAL FANTASY XIII 2", "Final Fantasy XIII 2"),
    ("GOD OF WAR II", "God of War II"),
    ("FIFA 14", "FIFA 14"),
    ("METAL GEAR SOLID 4 GUNS OF THE PATRIOTS", "Metal Gear Solid 4 Guns of the Patriots"),
    ("DRAGON BALL Z BUDOKAI TENKAICHI 2", "Dragon Ball Z Budokai Tenkaichi 2"),

    # Palabras hifenadas NO se rompen.
    ("Kung-Fu Master", "Kung-Fu Master"),
    ("Call of duty Modern Warfare 2", "Call of duty Modern Warfare 2"),
    ("MARVELS SPIDER-MAN", "Marvels Spider-Man"),
    ("H.A.W.X. 2", "H.A.W.X. 2"),
    ("SpongeBob SquarePants", "SpongeBob SquarePants"),

    # Notas de trabajo: se quitan.
    ("Call of duty 4 M.W (buscar de nuevo,no sale)", "Call of duty 4 M.W"),
    ("DESTROY All HUMANS 2 (esta pal)", "DESTROY All HUMANS 2"),
    ("AVATAR. THE LEGEND OF AANG (no grabar,no sirve)", "Avatar. The Legend of Aang"),
    ("BINARY DOMAIN (ingles) (grabar el de arriba)", "Binary Domain"),
    ("Armored Core V (ntsc)", "Armored Core V"),
    ("Blades of Time [PAL]", "Blades of Time"),
    ("Kinect Star Wars (ntsc) (Kinect)", "Kinect Star Wars"),
    ("Little Big Planet 2 [3.41_3.55]", "Little Big Planet 2"),
    ("GTA V (Arcade)", "GTA V"),
    ("Test (PSP)", "Test"),
    ("Juego (J)", "Juego"),
    ("PAL Game (PAL)", "PAL Game"),

    # Extensiones de archivo que quedaron en el nombre de la carpeta.
    ("50 Cent.rar", "50 Cent"),
    ("Asterix & Obelix - Kick Buttix.iso", "Asterix & Obelix - Kick Buttix"),
    ("Armored Core Last Raven Portable.rar", "Armored Core Last Raven Portable"),
    ("GTA V [SLUS-20958].iso", "GTA V"),

    # Codigo de idioma suelto, sin parentesis.
    ("Alien Vs. Predator Extinction Ing", "Alien Vs. Predator Extinction"),
    ("GRANTURISMO3 pal", "Granturismo 3"),
    # Nota suelta al final, sin parentesis.
    ("CRASH BANDICOT TWIN SANITH buscar", "Crash Bandicot Twin Sanith"),
    ("Tekken 5 no sirve", "Tekken 5"),
    ("Cold Winter problemas", "Cold Winter"),

    # Subtitulos de verdad: se dejan.
    ("Howling Wolf (Howling Wolf)", "Howling Wolf (Howling Wolf)"),
    ("Furia de Titanes (Furia de Titanes)", "Furia de Titanes (Furia de Titanes)"),
    ("Boy and Girl (Boy and Girl)", "Boy and Girl (Boy and Girl)"),
]

GENEROS = [
    ("Action", ["Accion"]),
    # El orden lo fija GENRE_PRIORITY: Accion, Aventura, Disparadores.
    ("Action, Shooter, Adventure", ["Accion", "Aventura", "Disparadores"]),
    ("RPG", ["Rol"]),
    ("Action, Adventure, RPG", ["Accion", "Aventura", "Rol"]),
    ("", ["Variado"]),
    ("null", ["Variado"]),
    # Los generos sueltos (Indie, Casual) van al final, no al principio.
    ("Indie, Action, Adventure", ["Accion", "Aventura", "Indie"]),
    ("Family, Casual, Indie", ["Familiar", "Casual", "Indie"]),
]

JUGADORES = [
    (["1 jugador"], ["1 jugador"]),
    (["1 jugador", "2 jugadores", "4 jugadores"], ["2 jugadores", "4 jugadores"]),
    (["1 jugador", "4 jugadores"], ["4 jugadores"]),
    (["1 jugador", "2 jugadores"], ["2 jugadores"]),
]


def main() -> int:
    fallos = 0

    print("Titulos:\n")
    for original, esperado in TITULOS:
        obtenido, _ = clean_title(original)
        bien = obtenido == esperado
        if not bien:
            fallos += 1
        marca = "OK   " if bien else "FALLA"
        print(f"  {marca} {original[:44]:46s} -> {obtenido[:40]}")
        if not bien:
            print(f"         se esperaba: {esperado!r}")

    print("\nGeneros:\n")
    for original, esperado in GENEROS:
        obtenido = normalize_genres(original)
        bien = obtenido == esperado
        if not bien:
            fallos += 1
        marca = "OK   " if bien else "FALLA"
        print(f"  {marca} {original[:36]:38s} -> {obtenido}")

    print("\nJugadores:\n")
    for original, esperado in JUGADORES:
        obtenido = fix_players(original)
        bien = obtenido == esperado
        if not bien:
            fallos += 1
        marca = "OK   " if bien else "FALLA"
        print(f"  {marca} {str(original):46s} -> {obtenido}")

    print()
    print("Todos los tests pasaron." if fallos == 0 else f"{fallos} test(s) fallaron.")
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())