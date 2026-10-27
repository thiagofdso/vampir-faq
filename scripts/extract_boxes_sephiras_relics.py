#!/usr/bin/env python3
"""
VAMPIR (ProjectRED) Box, Sephira and Relic Texture Extractor
Extracts all ItemBox (baús), Sephira (sefiras) and Relic / Burialgoods (relíquias)
textures from Unreal Engine .pak archives and decodes them to web-ready PNGs.
"""

import os
import re
import struct
import subprocess
import zlib

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
TMP_EXTRACT_DIR = os.path.join(BASE_DIR, "analysis/ui_extracted_boxes")
ASSETS_OUT = os.path.join(BASE_DIR, "faq/assets/items")
ASTCENC_BIN = "/home/thiagofdso/.local/bin/astcenc"

os.makedirs(TMP_EXTRACT_DIR, exist_ok=True)
os.makedirs(ASSETS_OUT, exist_ok=True)

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

        astc_header = bytearray([
            0x13, 0xAB, 0xA1, 0x5C,
            bx, by, 1,
            w & 0xFF, (w >> 8) & 0xFF, (w >> 16) & 0xFF,
            h & 0xFF, (h >> 8) & 0xFF, (h >> 16) & 0xFF,
            1, 0, 0
        ])

        tmp_astc = out_png_path + ".astc"
        with open(tmp_astc, 'wb') as fp:
            fp.write(astc_header + payload)

        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        cmd = [ASTCENC_BIN, '-dl', tmp_astc, out_png_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(tmp_astc):
            os.remove(tmp_astc)
        return os.path.exists(out_png_path)

    return False

def unpack_from_pak(pak_filename, pattern_filter):
    pak_path = os.path.join(PAKS_DIR, pak_filename)
    if not os.path.exists(pak_path):
        print(f"Pak file not found: {pak_path}")
        return []

    cmd_list = ['repak', '--aes-key', AES_KEY, 'list', pak_path]
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    all_files = res.stdout.splitlines()

    matches = [f for f in all_files if pattern_filter(f)]
    if not matches:
        return []

    print(f"Unpacking {len(matches)} files from {pak_filename}...")
    # Unpack in batches of 100 to avoid command line limits
    batch_size = 100
    for i in range(0, len(matches), batch_size):
        batch = matches[i:i+batch_size]
        cmd_unpack = ['repak', '--aes-key', AES_KEY, 'unpack', '-o', TMP_EXTRACT_DIR]
        for m in batch:
            cmd_unpack.extend(['-i', m])
        cmd_unpack.append(pak_path)
        subprocess.run(cmd_unpack, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return matches

def is_target_texture(path):
    if not path.endswith('.uexp'):
        return False
    low = path.lower()
    return any(k in low for k in [
        'itembox', 'sephira', 'relic', 'burialgoods', 'objetitem', 'sacredrelic'
    ])

print("1. Unpacking Baús, Sefiras e Relíquias dos pacotes PAK...")
paks = [
    'pakchunk501-Android_ASTC.pak',
    'pakchunk501_s1-Android_ASTC.pak',
    'pakchunk503-Android_ASTC.pak'
]

all_extracted = []
for p in paks:
    unpacked = unpack_from_pak(p, is_target_texture)
    all_extracted.extend(unpacked)

print(f"\nTotal de arquivos desempacotados: {len(all_extracted)}")

print("\n2. Convertendo texturas UEXP para PNG em assets/items/...")
converted = 0
categories = {"boxes": 0, "sephiras": 0, "relics": 0}

for root, dirs, files in os.walk(TMP_EXTRACT_DIR):
    for f in files:
        if not f.endswith('.uexp'):
            continue
        src = os.path.join(root, f)
        
        # Clean destination name
        # Ex: IMG_ItemBox_Burialgoods_01.uexp -> itembox_burialgoods_01.png
        # Ex: IMG_Sephira_01.uexp -> sephira_01.png
        clean_name = f.replace(".uexp", "").lower()
        if clean_name.startswith("img_"):
            clean_name = clean_name[4:]
        elif clean_name.startswith("tex_"):
            clean_name = clean_name[4:]
            
        out_png = os.path.join(ASSETS_OUT, clean_name + ".png")
        if decode_uexp_to_png(src, out_png):
            converted += 1
            if 'box' in clean_name:
                categories["boxes"] += 1
            elif 'sephira' in clean_name:
                categories["sephiras"] += 1
            else:
                categories["relics"] += 1

print(f"\n✓ Conversão concluída com sucesso!")
print(f"Total de imagens geradas: {converted}")
print(f"  - Baús (Boxes): {categories['boxes']}")
print(f"  - Sefiras: {categories['sephiras']}")
print(f"  - Relíquias / Bens Funerários: {categories['relics']}")
