"""
Crea una carpeta de ejemplo con nombres de juegos "sucios" (tipicos de PS2/PS3)
para probar el escaner sin tocar tus discos reales.

Uso: python tools/make_test_folders.py
"""
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "_test_juegos"

FAKE_TREE = {
    "PS2": [
        "Grand Theft Auto - San Andreas [SLUS-20958] [USA].iso",
        "Shadow of the Colossus (USA) (En,Fr,De,Es,It).iso",
        "God of War II [SLUS-21000].iso",
        "Devil May Cry 3 - Dante's Awakening [SLUS-20836] [USA].bin",
        "Metal Gear Solid 3 - Snake Eater (PAL) (En,Fr,De,Es,It).iso",
        "Resident Evil 4 [SLES-53469].iso",
        "Final Fantasy X [SLES-25788].iso",
        "Kingdom Hearts II [SLUS-20923].iso",
        "Gran Turismo 4 [SLUS-97330].iso",
        "Bully - Scholarship Edition [SLUS-21193].iso",
        "Okami [SLUS-21077].iso",
        "Guitar Hero II [SLUS-21383].iso",
        "Okami [SLUS-21077].cue",
    ],
    "PS3": [
        "Grand Theft Auto V [BLUS30443] [USA].iso",
        "The Last of Us [BLUS30457] [USA].iso",
        "Red Dead Redemption [BLES00932].iso",
        "Uncharted 3 - Drake's Deception [BLUS30780].iso",
        "Metal Gear Solid 4 - Guns of the Patriots [BLUS30721].iso",
        "God of War III [BLUS30770].iso",
        "Infamous 2 - Heroic Crimes [BCUS-97222].iso",
        "Heavy Rain [BLUS30555].iso",
        "Demons Souls [BCUS-30790].iso",
        "LittleBigPlanet 2 [BLUS30772].iso",
        "FIFA 14 [BLUS31443].iso",
    ],
    "XBOX 360": [
        "Halo 3 [DEFAULT].xiso",
        "Gears of War 2 [Guild01].iso",
        "Forza Horizon [DEFAULT].xiso",
        "BioShock [DEFAULT].iso",
        "Alan Wake [DEFAULT].iso",
        "Perfect Dark [Guild02].iso",
        "Minecraft [Xbox 360 Edition].iso",
    ],
    "PS4": [
        "Bloodborne [CUSA00900].pkg",
        "The Last of Us Part II [CUSA07724].pkg",
        "God of War [CUSA00852].pkg",
        "Horizon Zero Dawn [CUSA00068].pkg",
        "Marvel's Spider-Man [CUSA00099].pkg",
        "Red Dead Redemption 2 [CUSA03080].pkg",
        "The Witcher 3 - Wild Hunt [CUSA01651].pkg",
    ],
    "PS5": [
        "Demons Souls [PPSA02432].pkg",
        "Marvel's Spider-Man Miles Morales [PPSA02826].pkg",
        "Ratchet and Clank - Rift Apart [PPSA02586].pkg",
        "Horizon Forbidden West [PPSA01461].pkg",
    ],
}


def main() -> int:
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)

    for folder, files in FAKE_TREE.items():
        target = TEST_DIR / folder / "Juegos"
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            (target / name).write_bytes(b"\x00" * 16)  # archivo falso, solo el nombre

    print(f"Carpeta de ejemplo creada en: {TEST_DIR}")
    print(f"\nProba el escaner con:\n  python tools/scan_games.py --root \"{TEST_DIR}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
