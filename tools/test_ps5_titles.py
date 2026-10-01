"""
Tests de limpieza de titulos de superpsx.

El riesgo real: una regla demasiado agresiva parte titulos que eran correctos.
Ya paso con "Killzone Liberation PS5", que se quedaba en "Killzone Liberati".

Uso: python tools/test_ps5_titles.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ps5_suppsx import clean_title  # noqa: E402

# (crudo, esperado)
CASOS = [
    # Se quita solo la etiqueta de la consola.
    ("High On Life 2 PS5", "High On Life 2"),
    ("Trifox PS5", "Trifox"),
    ("APEX PS5", "APEX"),
    ("Big Helmet Heroes PS5", "Big Helmet Heroes"),
    ("Synapse PS5", "Synapse"),

    # Palabras que terminan en "on" o "for": NO se deben cortar.
    ("Killzone Liberation PS5", "Killzone Liberation"),
    ("Ratchet and Clank Rift Apart PS5", "Ratchet and Clank Rift Apart"),
    ("Helldivers for PS5", "Helldivers"),

    # Partes del nombre que parecen un codigo y hay que conservarlas.
    ("EA SPORTS FC 26 PS5", "EA SPORTS FC 26"),
    ("007 Blood Stone PS5", "007 Blood Stone"),
    ("F1 22 Champions Edition PS5", "F1 22 Champions Edition"),
    ("Atelier Ryza 3 Alchemist of the End & the Secret Key DX PS5",
     "Atelier Ryza 3 Alchemist of the End & the Secret Key DX"),

    # La etiqueta puede venir repetida.
    ("Trifox PS5 PS5", "Trifox"),
    ("Synapse - PS5", "Synapse"),

    # Sin etiqueta, el titulo queda como estaba.
    ("Gran Turismo 7", "Gran Turismo 7"),
    ("Death Stranding 2", "Death Stranding 2"),
]

fallos = 0

for crudo, esperado in CASOS:
    obtenido = clean_title(crudo)
    bien = obtenido == esperado
    if not bien:
        fallos += 1
    marca = "OK   " if bien else "FALLA"
    print(f"  {marca} {crudo[:44]:46s} -> {obtenido[:40]}")

print()
print("Todos los tests pasaron." if fallos == 0 else f"{fallos} test(s) fallaron.")
sys.exit(0 if fallos == 0 else 1)
