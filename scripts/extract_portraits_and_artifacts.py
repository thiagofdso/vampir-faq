#!/usr/bin/env python3
"""
Extractor for Official Portraits and Artifacts Textures from Unreal Engine PAK archives.
Decodes BGRA and ASTC compressed textures into web-ready PNGs for VAMPIR FAQ.
"""

import os
import sys
import csv
import struct
import zlib
import re
import subprocess
import shutil

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
FAQ_DIR = os.path.join(BASE_DIR, "faq")
ASSETS_DIR = os.path.join(FAQ_DIR, "assets")
ARTIFACTS_OUT = os.path.join(ASSETS_DIR, "artifacts")
PORTRAITS_OUT = os.path.join(ASSETS_DIR, "portraits")
ASTCENC_BIN = "/home/thiagofdso/.local/bin/astcenc"
TMP_DIR = "/tmp/vampir_assets_extract"

os.makedirs(ARTIFACTS_OUT, exist_ok=True)
os.makedirs(PORTRAITS_OUT, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

def decode_uexp_to_png(uexp_path, out_png_path):
    if not os.path.exists(uexp_path):
        return False

    with open(uexp_path, 'rb') as f:
        data = f.read()

    if len(data) < 32 or data[-4:] != b'\xc1\x83\x2a\x9e':
        return False

    # Universal 28-byte Unreal Engine 5 export footer:
    w, h, depth = struct.unpack('<III', data[-28:-16])
    if w <= 0 or w > 8192 or h <= 0 or h > 8192:
        return False

    fmt_pos = data.find(b'PF_')
    if fmt_pos == -1:
        return False

    fmt_str = data[fmt_pos:fmt_pos+16].split(b'\x00')[0].decode('ascii', errors='ignore')

    # 1. BGRA Uncompressed
    if 'PF_B8G8R8A8' in fmt_str:
        expected_bytes = w * h * 4
        payload = data[-28 - expected_bytes : -28]
        if len(payload) != expected_bytes:
            return False

        rgba = bytearray(expected_bytes)
        for i in range(0, expected_bytes, 4):
            rgba[i] = payload[i+2]
            rgba[i+1] = payload[i+1]
            rgba[i+2] = payload[i]
            rgba[i+3] = payload[i+3]

        raw_lines = b''.join(b'\x00' + rgba[y*w*4 : (y+1)*w*4] for y in range(h))
        def chunk(tag, payload):
            return struct.pack('>I', len(payload)) + tag + payload + struct.pack('>I', zlib.crc32(tag + payload))
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
        idat = zlib.compress(raw_lines)
        png_data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        with open(out_png_path, 'wb') as fp:
            fp.write(png_data)
        return True

    # 2. ASTC Compressed
    elif 'PF_ASTC' in fmt_str:
        m = re.search(r'(\d+)x(\d+)', fmt_str)
        bx, by = (int(m.group(1)), int(m.group(2))) if m else (6, 6)

        blocks_x = (w + bx - 1) // bx
        blocks_y = (h + by - 1) // by
        expected_bytes = blocks_x * blocks_y * 16

        payload = data[-28 - expected_bytes : -28]
        if len(payload) != expected_bytes:
            return False

        header = bytearray(b'\x13\xab\xa1\x5c')
        header.append(bx)
        header.append(by)
        header.append(1)
        header += struct.pack('<I', w)[:3]
        header += struct.pack('<I', h)[:3]
        header += struct.pack('<I', 1)[:3]

        tmp_astc = f'/tmp/tmp_{os.path.basename(uexp_path)}.astc'
        with open(tmp_astc, 'wb') as fp:
            fp.write(header + payload)

        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        cmd = [ASTCENC_BIN, '-dl', tmp_astc, out_png_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(tmp_astc):
            os.remove(tmp_astc)
        return os.path.exists(out_png_path)

    return False


def unpack_files(pak_name, files_list):
    pak_path = os.path.join(PAKS_DIR, pak_name)
    if not os.path.exists(pak_path):
        print(f"Error: Pak file {pak_path} does not exist.")
        return False
    print(f"Unpacking {len(files_list)} assets from {pak_name}...")
    cmd = ['repak', '--aes-key', AES_KEY, 'unpack', '-o', TMP_DIR]
    for f in files_list:
        cmd.extend(['-i', f])
    cmd.append(pak_path)
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Warning during unpack: {res.stderr}")
    return True


def extract_artifacts():
    print("\n--- 1. Extracting Artifact Textures & Artworks ---")
    
    # 1.1 Unpack Tab icons and Flat icons from pakchunk501
    pak501_files = [
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab01.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab02.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab03.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab04.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab05.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Artifact.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Portrait.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_ObjetItem_SlateForm_01.uexp"
    ]
    unpack_files("pakchunk501-Android_ASTC.pak", pak501_files)

    # 1.2 Unpack Hero Portraits from pakchunk501_s1
    pak501s1_files = [
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Olga.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Oscar.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Tancilla.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Philippos.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Ruggiero.uexp",
    ]
    unpack_files("pakchunk501_s1-Android_ASTC.pak", pak501s1_files)

    # 1.3 Unpack Glow/Deco from pakchunk503
    pak503_files = [
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Olga_Glow.uexp",
        "ProjectRED/Content/RED/UI/Resource/Texture/Image/Deco_ArtifactSlate_A_On.uexp"
    ]
    unpack_files("pakchunk503-Android_ASTC.pak", pak503_files)

    # Convert to target PNGs
    artifact_mappings = [
        # (source rel path in TMP_DIR, dest path in ARTIFACTS_OUT, label)
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab01.uexp", "artifact_1001.png", "Óleo de Unção de Olga (Ícone)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab02.uexp", "artifact_1002.png", "Essência de Oscar (Ícone)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab03.uexp", "artifact_1003.png", "Tesouro de Tancilla (Ícone)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab04.uexp", "artifact_1004.png", "Selo de Philippos (Ícone)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Artifact_Tab05.uexp", "artifact_1005.png", "Espada Sagrada de Ruggiero (Ícone)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/IMG_ObjetItem_SlateForm_01.uexp", "artifact_1101.png", "Olga Transformação I (Ícone Slate)"),
        
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Olga.uexp", "art_1001.png", "Olga (Arte 1024x1024)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Olga_Glow.uexp", "art_1101.png", "Olga Transformação I (Arte Glow 512x512)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Oscar.uexp", "art_1002.png", "Oscar (Arte 1024x1024)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Tancilla.uexp", "art_1003.png", "Tancilla (Arte 1024x1024)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Philippos.uexp", "art_1004.png", "Philippos (Arte 1024x1024)"),
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait/IMG_Portrait_Ruggiero.uexp", "art_1005.png", "Ruggiero (Arte 1024x1024)"),
        
        ("ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Artifact.uexp", "flat_artifact.png", "Ícone Flat Artefatos"),
    ]

    for src_rel, dst_fn, label in artifact_mappings:
        src_path = os.path.join(TMP_DIR, src_rel)
        dst_path = os.path.join(ARTIFACTS_OUT, dst_fn)
        if decode_uexp_to_png(src_path, dst_path):
            print(f"  ✓ Extracted {dst_fn}: {label}")
        else:
            print(f"  ✗ Failed to decode {src_rel}")

    # Flat portrait icon
    flat_port_src = os.path.join(TMP_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image/IMG_Flat_Portrait.uexp")
    flat_port_dst = os.path.join(PORTRAITS_OUT, "flat_portrait.png")
    if decode_uexp_to_png(flat_port_src, flat_port_dst):
        print(f"  ✓ Extracted flat_portrait.png: Ícone Flat Retratos")


def extract_portraits():
    print("\n--- 2. Extracting Character & Lineage Portraits (Portraits Catalog) ---")
    csv_path = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/patch_extracted/ProjectRED/Content/RED/Data/CSV/Portrait.csv")
    with open(csv_path, encoding='utf-8-sig') as f:
        portraits = list(csv.DictReader(f))

    # Query all available files in pakchunk501_s1
    pak501s1 = os.path.join(PAKS_DIR, "pakchunk501_s1-Android_ASTC.pak")
    res = subprocess.run(['repak', '--aes-key', AES_KEY, 'list', pak501s1], capture_output=True, text=True)
    pak_files = set(res.stdout.splitlines())

    files_to_unpack = []
    id_to_files = {}

    for p in portraits:
        pid = p['Id']
        base = p['ImgPortrait']
        big = p.get('ImgPortrait_Big')

        # Find best small portrait
        small_chosen = None
        for suffix in ['_M.uexp', '_F.uexp', '.uexp']:
            cand = f"ProjectRED/Content/RED/UI/Resource/Texture/Image/PortraitContents/{base}{suffix}"
            if cand in pak_files:
                small_chosen = cand
                break

        # Find best big portrait
        big_chosen = None
        if big:
            for suffix in ['_M.uexp', '_F.uexp', '.uexp']:
                cand = f"ProjectRED/Content/RED/UI/Resource/Texture/Image/PortraitContents/{big}{suffix}"
                if cand in pak_files:
                    big_chosen = cand
                    break

        id_to_files[pid] = {
            'small': small_chosen,
            'big': big_chosen
        }
        if small_chosen:
            files_to_unpack.append(small_chosen)
        if big_chosen:
            files_to_unpack.append(big_chosen)

    # Deduplicate and unpack
    unique_files = list(set(files_to_unpack))
    print(f"Unpacking {len(unique_files)} portrait textures...")
    # Repak in chunks if needed
    chunk_size = 100
    for i in range(0, len(unique_files), chunk_size):
        chunk = unique_files[i : i + chunk_size]
        unpack_files("pakchunk501_s1-Android_ASTC.pak", chunk)

    # Decode each portrait
    small_success = 0
    big_success = 0

    for p in portraits:
        pid = p['Id']
        info = id_to_files[pid]

        if info['small']:
            src = os.path.join(TMP_DIR, info['small'])
            dst = os.path.join(PORTRAITS_OUT, f"portrait_{pid}.png")
            if decode_uexp_to_png(src, dst):
                small_success += 1

        if info['big']:
            src = os.path.join(TMP_DIR, info['big'])
            dst = os.path.join(PORTRAITS_OUT, f"portrait_{pid}_big.png")
            if decode_uexp_to_png(src, dst):
                big_success += 1

    print(f"  ✓ Successfully extracted {small_success}/{len(portraits)} standard portraits (256x256)")
    print(f"  ✓ Successfully extracted {big_success} high-resolution big portraits (440x440)")


def main():
    print("==================================================")
    print("VAMPIR - Portraits and Artifacts Texture Extractor")
    print("==================================================")
    extract_artifacts()
    extract_portraits()
    
    # Cleanup temp
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    print("\nTexture extraction finished successfully!")

if __name__ == "__main__":
    main()
