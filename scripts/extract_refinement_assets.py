#!/usr/bin/env python3
"""
Extractor for Official Refinement (Refinamento com Trindade) Assets and Textures from Unreal Engine PAK archives.
Decodes BGRA and ASTC compressed textures into web-ready PNGs for VAMPIR FAQ.
"""

import os
import sys
import subprocess

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
FAQ_DIR = os.path.join(BASE_DIR, "faq")
OUT_DIR = os.path.join(FAQ_DIR, "assets/refinement")
TMP_DIR = "/tmp/refinement_extract"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(FAQ_DIR, "scripts"))
from extract_portraits_and_artifacts import decode_uexp_to_png

TARGETS_501 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Refine.uexp", "flat_refine.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_Item_Refinement01.uexp", "refinement_stone.png"),
]

TARGETS_503 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Img_ItemRefineNumber.uexp", "refine_number.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/ItemRefine_Grade_Max.uexp", "grade_max.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/ItemRefine_Grade_MinMid.uexp", "grade_mid.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/ItemRefine_Grade_None.uexp", "grade_none.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Slot_Refine.uexp", "slot_refine.png"),
]

def extract_and_decode(pak_name, targets):
    pak_path = os.path.join(PAKS_DIR, pak_name)
    if not os.path.exists(pak_path):
        print(f"Error: Pak file not found: {pak_path}")
        return

    cmd = ["repak", "--aes-key", AES_KEY, "unpack", "-o", TMP_DIR]
    for internal_path, _ in targets:
        cmd.extend(["-i", internal_path])
        cmd.extend(["-i", internal_path.replace(".uexp", ".uasset")])
    cmd.append(pak_path)

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

    for internal_path, out_name in targets:
        uexp_disk = os.path.join(TMP_DIR, internal_path)
        out_png = os.path.join(OUT_DIR, out_name)
        if os.path.exists(uexp_disk):
            ok = decode_uexp_to_png(uexp_disk, out_png)
            size = os.path.getsize(out_png) if ok else 0
            print(f"  ✓ {internal_path} -> {out_name}: {ok} ({size:,} bytes)")
        else:
            print(f"  ✗ Failed to unpack: {internal_path}")

def main():
    print("=== Extracting Refinement Textures ===")
    extract_and_decode("pakchunk501-Android_ASTC.pak", TARGETS_501)
    extract_and_decode("pakchunk503-Android_ASTC.pak", TARGETS_503)
    print("Extraction complete.")

if __name__ == "__main__":
    main()
