#!/usr/bin/env python3
"""
VAMPIR (ProjectRED) Game Texture & Asset Extractor
Extracts official UI textures (Classes, Weapons, Armor, Monsters/Bosses, Dungeons)
from Unreal Engine .pak archives and converts them to standard Web-ready PNGs.
"""

import os
import re
import struct
import subprocess
import zlib

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
TMP_EXTRACT_DIR = os.path.join(BASE_DIR, "analysis/ui_extracted")
ASSETS_OUT = os.path.join(BASE_DIR, "faq/assets")
ASTCENC_BIN = "/home/thiagofdso/.local/bin/astcenc"

os.makedirs(TMP_EXTRACT_DIR, exist_ok=True)
os.makedirs(os.path.join(ASSETS_OUT, "classes"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_OUT, "monsters"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_OUT, "items"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_OUT, "dungeons"), exist_ok=True)

def decode_uexp_to_png(uexp_path, out_png_path):
    if not os.path.exists(uexp_path):
        return False

    with open(uexp_path, 'rb') as f:
        data = f.read()

    fmt_pos = data.find(b'PF_')
    if fmt_pos == -1:
        return False

    w = struct.unpack('<I', data[fmt_pos-16:fmt_pos-12])[0]
    h = struct.unpack('<I', data[fmt_pos-12:fmt_pos-8])[0]
    if w <= 0 or w > 8192 or h <= 0 or h > 8192:
        return False

    # 1. BGRA Uncompressed
    if b'PF_B8G8R8A8' in data[fmt_pos:fmt_pos+16]:
        expected_bytes = w * h * 4
        payload = data[-4-expected_bytes:-4]
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
    elif b'PF_ASTC' in data[fmt_pos:fmt_pos+16]:
        fmt_str = data[fmt_pos:fmt_pos+16].split(b'\x00')[0].decode('ascii', errors='ignore')
        m = re.search(r'(\d+)x(\d+)', fmt_str)
        bx, by = (int(m.group(1)), int(m.group(2))) if m else (6, 6)

        blocks_x = (w + bx - 1) // bx
        blocks_y = (h + by - 1) // by
        expected_bytes = blocks_x * blocks_y * 16

        payload = data[-4-expected_bytes:-4]
        if len(payload) != expected_bytes:
            return False

        header = bytearray()
        header += b'\x13\xab\xa1\x5c'
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

def unpack_from_pak(pak_filename, pattern_filter):
    pak_path = os.path.join(PAKS_DIR, pak_filename)
    if not os.path.exists(pak_path):
        print(f"Pak file not found: {pak_path}")
        return []

    # List matching
    cmd_list = ['repak', '--aes-key', AES_KEY, 'list', pak_path]
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    all_files = res.stdout.splitlines()

    matches = [f for f in all_files if pattern_filter(f)]
    if not matches:
        return []

    print(f"Unpacking {len(matches)} files from {pak_filename}...")
    cmd_unpack = ['repak', '--aes-key', AES_KEY, 'unpack', '-o', TMP_EXTRACT_DIR]
    for m in matches:
        cmd_unpack.extend(['-i', m])
    cmd_unpack.append(pak_path)

    subprocess.run(cmd_unpack, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return matches

print("1. Extracting Class Icons and Portraits...")
# Class files from pakchunk501
unpack_from_pak('pakchunk501-Android_ASTC.pak', lambda f: 'IMG_Class' in f)

class_mappings = {
    # DarkMage (Víbora)
    "IMG_ClassType_DarkMage.uexp": "classes/darkmage_icon.png",
    "IMG_Class_DarkMage_Male.uexp": "classes/darkmage_male.png",
    "IMG_Class_DarkMage_Female.uexp": "classes/darkmage_female.png",
    # Reaper (Ceifador)
    "IMG_ClassType_Reaper.uexp": "classes/reaper_icon.png",
    "IMG_Class_Reaper_Male.uexp": "classes/reaper_male.png",
    "IMG_Class_Reaper_Female.uexp": "classes/reaper_female.png",
    # Gunner (Carnificina)
    "IMG_ClassType_Gunner.uexp": "classes/gunner_icon.png",
    "IMG_Class_Gunner_Male.uexp": "classes/gunner_male.png",
    "IMG_Class_Gunner_Female.uexp": "classes/gunner_female.png",
    # SwordMan (Manchado de Sangue)
    "IMG_ClassType_SwordMan.uexp": "classes/swordman_icon.png",
    "IMG_Class_SwordMan_Male.uexp": "classes/swordman_male.png",
    "IMG_Class_SwordMan_Female.uexp": "classes/swordman_female.png",
    # Fighter (Akasha)
    "IMG_ClassType_Fighter.uexp": "classes/fighter_icon.png",
    "IMG_Class_Fighter_Male.uexp": "classes/fighter_male.png",
    "IMG_Class_Fighter_Female.uexp": "classes/fighter_female.png"
}

for src_name, rel_out in class_mappings.items():
    src_path = os.path.join(TMP_EXTRACT_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image", src_name)
    dst_path = os.path.join(ASSETS_OUT, rel_out)
    if decode_uexp_to_png(src_path, dst_path):
        print(f"  ✓ Converted: {rel_out}")

print("\n2. Extracting Monster and Boss Portraits...")
# Monster portraits from pakchunk501_s1
unpack_from_pak('pakchunk501_s1-Android_ASTC.pak', lambda f: 'IMG_Monster_Portrait_' in f and f.endswith('.uexp'))

monster_uexps = [
    f for f in os.listdir(os.path.join(TMP_EXTRACT_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait"))
    if f.startswith("IMG_Monster_Portrait_") and f.endswith(".uexp")
]

monster_count = 0
for m in monster_uexps:
    src_path = os.path.join(TMP_EXTRACT_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image/Portrait", m)
    clean_name = m.replace("IMG_Monster_Portrait_", "").replace(".uexp", "").lower() + ".png"
    dst_path = os.path.join(ASSETS_OUT, "monsters", clean_name)
    if decode_uexp_to_png(src_path, dst_path):
        monster_count += 1

print(f"  ✓ Converted {monster_count} monster & boss portraits to assets/monsters/")

print("\n3. Extracting Weapons, Armors and Items...")
# Select key items from pakchunk501 and pakchunk501_s1
unpack_from_pak('pakchunk501_s1-Android_ASTC.pak', lambda f: ('IMG_Weapon_' in f or 'IMG_Potion_' in f) and f.endswith('.uexp'))
unpack_from_pak('pakchunk501-Android_ASTC.pak', lambda f: ('IMG_Accessory_' in f or 'IMG_Armor_' in f) and f.endswith('.uexp'))

item_dirs = [
    os.path.join(TMP_EXTRACT_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image/Item")
]

item_count = 0
for idir in item_dirs:
    if not os.path.exists(idir): continue
    for it in os.listdir(idir):
        if it.endswith(".uexp") and (it.startswith("IMG_Weapon_") or it.startswith("IMG_Armor_") or it.startswith("IMG_Accessory_") or it.startswith("IMG_Potion_")):
            src_path = os.path.join(idir, it)
            clean_name = it.replace("IMG_", "").replace(".uexp", "").lower() + ".png"
            dst_path = os.path.join(ASSETS_OUT, "items", clean_name)
            if decode_uexp_to_png(src_path, dst_path):
                item_count += 1

print(f"  ✓ Converted {item_count} weapon and item icons to assets/items/")

print("\n4. Extracting Dungeon Backgrounds...")
unpack_from_pak('pakchunk501-Android_ASTC.pak', lambda f: 'IMG_Dungeon_BG_' in f and f.endswith('.uexp'))

dungeon_dir = os.path.join(TMP_EXTRACT_DIR, "ProjectRED/Content/RED/UI/Resource/Texture/Image/Dungeon")
dungeon_count = 0
if os.path.exists(dungeon_dir):
    for d in os.listdir(dungeon_dir):
        if d.startswith("IMG_Dungeon_BG_") and d.endswith(".uexp"):
            src_path = os.path.join(dungeon_dir, d)
            clean_name = d.replace("IMG_Dungeon_BG_", "").replace(".uexp", "").lower() + ".png"
            dst_path = os.path.join(ASSETS_OUT, "dungeons", clean_name)
            if decode_uexp_to_png(src_path, dst_path):
                dungeon_count += 1

print(f"  ✓ Converted {dungeon_count} dungeon backgrounds to assets/dungeons/")
print("\nAsset extraction completed successfully!")
