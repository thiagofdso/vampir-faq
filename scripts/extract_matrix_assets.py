#!/usr/bin/env python3
"""
Extractor for Official Matrix (Evolução do Reino de Sangue) Assets and Textures from Unreal Engine PAK archives.
Decodes BGRA and ASTC compressed textures into web-ready PNGs for VAMPIR FAQ.
"""

import os
import sys
import subprocess

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
FAQ_DIR = os.path.join(BASE_DIR, "faq")
OUT_DIR = os.path.join(FAQ_DIR, "assets/matrix")
TMP_DIR = "/tmp/matrix_extract"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(FAQ_DIR, "scripts"))
from extract_portraits_and_artifacts import decode_uexp_to_png

TARGETS_501 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Matrix.uexp", "flat_matrix.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_EventMatrix_FullMoon.uexp", "flat_matrix_fullmoon.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_EventMatrix_CrescentMoon.uexp", "flat_matrix_crescent.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Matrix_Tab01.uexp", "matrix_tab01.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Matrix_Tab02.uexp", "matrix_tab02.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Matrix_EventTab01.uexp", "matrix_event_tab01.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_01.uexp", "mat_stone_01.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_02.uexp", "mat_stone_02.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_03.uexp", "mat_stone_03.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_04.uexp", "mat_stone_04.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_05.uexp", "mat_stone_05.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_MatrixEnchantMaterial_06.uexp", "mat_stone_06.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_ItemBox_MatrixEnchantMaterial_Random_01.uexp", "mat_box_01.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_ItemBox_MatrixEnchantMaterial_Random_02.uexp", "mat_box_02.png"),
]

TARGETS_503 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Btn_MatrixReroll.uexp", "btn_reroll.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Slot_MatrixLv1.uexp", "slot_lv1.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Slot_MatrixLv2.uexp", "slot_lv2.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/Slot_MatrixColor.uexp", "slot_color.png"),
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
    print("=== Extracting Matrix (Reino de Sangue) Textures ===")
    extract_and_decode("pakchunk501-Android_ASTC.pak", TARGETS_501)
    extract_and_decode("pakchunk503-Android_ASTC.pak", TARGETS_503)
    print("Extraction complete.")

if __name__ == "__main__":
    main()
