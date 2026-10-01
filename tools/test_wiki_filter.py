"""
Tests del filtro de similitud de Wikipedia.

El riesgo real: la busqueda difusa devuelve la pagina de otra cosa y la web
muestra una descripcion que es de otro juego, pero con toda la seguridad.
Este archivo comprueba que el filtro rechaza esos casos.

Uso: python tools/test_wiki_filter.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_metadata import similar, wiki_match_is_trustworthy, WIKI_MIN_SIMILARITY  # noqa: E402

# (lo que buscamos, lo que devuelve Wikipedia, se deberia aceptar?)
CASOS = [
    # Se aceptan: el mismo juego con diferencias de escritura.
    ("Demons Souls", "Demon's Souls", True),
    ("Marvel's Spider-Man Miles Morales", "Marvel's Spider-Man: Miles Morales", True),
    ("God of War II", "God of War II", True),
    ("The Last of Us Part II", "The Last of Us Part II", True),
    ("Grand Theft Auto San Andreas", "Grand Theft Auto: San Andreas", True),
    ("007 Blood Stone", "007: Blood Stone", True),
    ("Metal Gear Solid 3 Snake Eater", "Metal Gear Solid 3: Snake Eater", True),
    # Wikipedia anade un parentesis para desambiguar: hay que aceptarlo.
    ("Demon's Souls", "Demon's Souls (2009 video game)", True),
    ("God of War", "God of War (video game)", True),

    # Se rechazan: Wikipedia devolvio otra cosa distinta.
    ("High On Life 2", "Infinity on High", False),
    ("Big Helmet Heroes", "Helmet Heroes Collection", False),
    ("Synapse", "Synaptic Transmission", False),
    ("Trifox", "Trix", False),
    ("Killzone Liberation", "Killzone", False),
    ("Ratchet and Clank Rift Apart", "Ratchet & Clank", False),
    ("BloodRayne 2 ReVamped", "BloodRayne", False),
    ("God of War", "God of War: Chains of Olympus", False),
    ("Assassins Creed II", "Assassin's Creed (video game)", False),
]

fallos = 0

for busqueda, pagina, esperado in CASOS:
    ratio = similar(pagina, busqueda)
    aceptado = wiki_match_is_trustworthy(busqueda, pagina)
    bien = aceptado == esperado
    if not bien:
        fallos += 1
    marca = "OK   " if bien else "FALLA"
    print(f"  {marca} {busqueda[:32]:34s} vs {pagina[:30]:32s} {ratio:.2f} "
          f"-> {'acepta' if aceptado else 'rechaza'}")

print()
print(f"Umbral de parecido: {WIKI_MIN_SIMILARITY}")
print("Todos los tests pasaron." if fallos == 0 else f"{fallos} test(s) fallaron.")
sys.exit(0 if fallos == 0 else 1)
