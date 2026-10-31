#!/usr/bin/env python3
"""
Extractor for Official LifeTree (Árvore da Vida) & Sephira (Sefiras) Assets and Textures from Unreal Engine PAK archives.
Decodes BGRA and ASTC compressed textures into web-ready PNGs for VAMPIR FAQ.
"""

import os
import sys
import subprocess

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
FAQ_DIR = os.path.join(BASE_DIR, "faq")
OUT_DIR = os.path.join(FAQ_DIR, "assets/lifetree")
TMP_DIR = "/tmp/lifetree_extract"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(FAQ_DIR, "scripts"))
from extract_portraits_and_artifacts import decode_uexp_to_png

TARGETS_501 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_LifeTree.uexp", "flat_lifetree.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Sephira.uexp", "flat_sephira.png"),
]

TARGETS_503 = [
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/BG_LifeTree.uexp", "bg_lifetree.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/BG_LifeTree_02.uexp", "bg_lifetree_02.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_TypeA.uexp", "type_a_achillute.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_TypeB.uexp", "type_b_bria.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_TypeC.uexp", "type_c_yechira.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_Symbol_01.uexp", "symbol_alpha.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_Symbol_02.uexp", "symbol_sigma.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_Symbol_03.uexp", "symbol_theta.png"),
    ("ProjectRED/Content/RED/UI/Resource/Texture/_Common/TEX_Sephira_Symbol_04.uexp", "symbol_kappa.png"),
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
    print("=== Extracting LifeTree & Sephira Textures ===")
    extract_and_decode("pakchunk501-Android_ASTC.pak", TARGETS_501)
    extract_and_decode("pakchunk503-Android_ASTC.pak", TARGETS_503)
    
    # Generate web-optimized background if bg_lifetree.png exists
    bg_path = os.path.join(OUT_DIR, "bg_lifetree.png")
    webp_path = os.path.join(OUT_DIR, "bg_lifetree_web.webp")
    if os.path.exists(bg_path):
        subprocess.run(["cwebp", "-q", "80", bg_path, "-o", webp_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("  ✓ Created web-optimized background: bg_lifetree_web.webp")
    print("Extraction complete.")

if __name__ == "__main__":
    main()
