#!/usr/bin/env python3
"""
VAMPIR (ProjectRED) Forge, Crafting & Materials Texture Extractor
Extracts all materials, craft tokens, currency icons, forge UI, and forge targets
from Unreal Engine encrypted PAK files and decodes them to PNG.
Supports ASTC, BGRA8, FloatRGBA (half-float), and RGBA8.
"""

import os
import re
import struct
import subprocess
import zlib
import shutil
from concurrent.futures import ThreadPoolExecutor

AES_KEY = "0x4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed"
BASE_DIR = "/home/thiagofdso/vampir"
PAKS_DIR = os.path.join(BASE_DIR, "game_data/com.netmarble.thered/files/Patch/Install")
TMP_EXTRACT_DIR = os.path.join(BASE_DIR, "analysis/ui_extracted_crafting")
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

    w, h, depth = struct.unpack('<III', data[-28:-16])
    if w <= 0 or w > 8192 or h <= 0 or h > 8192:
        return False

    fmt_pos = data.find(b'PF_')
    if fmt_pos == -1:
        return False

    fmt_str = data[fmt_pos:fmt_pos+16].split(b'\x00')[0].decode('ascii', errors='ignore')

    def make_png(rgba_bytes):
        raw_lines = b''.join(b'\x00' + rgba_bytes[y*w*4 : (y+1)*w*4] for y in range(h))
        def chunk(tag, payload):
            return struct.pack('>I', len(payload)) + tag + payload + struct.pack('>I', zlib.crc32(tag + payload))
        ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
        idat = zlib.compress(raw_lines)
        return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

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

        png_data = make_png(rgba)
        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        with open(out_png_path, 'wb') as fp:
            fp.write(png_data)
        return True

    # 2. FloatRGBA (Half float 16-bit)
    elif 'PF_FloatRGBA' in fmt_str:
        expected_bytes = w * h * 8
        payload = data[-28 - expected_bytes : -28]
        if len(payload) != expected_bytes:
            return False

        floats = struct.unpack(f'<{w*h*4}e', payload)
        rgba = bytearray(w * h * 4)
        for i in range(len(floats)):
            val = max(0.0, min(1.0, floats[i]))
            rgba[i] = int(val * 255.0 + 0.5)

        png_data = make_png(rgba)
        os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
        with open(out_png_path, 'wb') as fp:
            fp.write(png_data)
        return True

    # 3. ASTC Compressed
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

def get_pak_file_list(pak_filename):
    pak_path = os.path.join(PAKS_DIR, pak_filename)
    if not os.path.exists(pak_path):
        return []
    cmd_list = ['repak', '--aes-key', AES_KEY, 'list', pak_path]
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    return res.stdout.splitlines()

def unpack_files(pak_filename, file_list):
    pak_path = os.path.join(PAKS_DIR, pak_filename)
    if not file_list or not os.path.exists(pak_path):
        return
    print(f"  Unpacking {len(file_list)} files from {pak_filename}...")
    batch_size = 150
    for i in range(0, len(file_list), batch_size):
        batch = file_list[i:i+batch_size]
        cmd = ['repak', '--aes-key', AES_KEY, 'unpack', '-o', TMP_EXTRACT_DIR]
        for f in batch:
            cmd.extend(['-i', f])
        cmd.append(pak_path)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("=== Extração de Texturas de Materiais, Forja e Itens ===")
    existing_pngs = set(os.listdir(ASSETS_OUT))
    print(f"Imagens já presentes em assets/items: {len(existing_pngs)}")

    paks = [
        'pakchunk501-Android_ASTC.pak',
        'pakchunk501_s1-Android_ASTC.pak'
    ]

    extra_targets = {
        'IMG_Asset_Gold',
        'IMG_Asset_Diamond',
        'IMG_Asset_Exp',
        'IMG_Asset_Mileage',
        'IMG_Flat_ItemCraft',
        'IMG_Flat_ItemCraft2',
        'IMG_Flat_CraftBefore',
        'IMG_Flat_Enchant',
        'IMG_Flat_EnchantMulti',
        'IMG_Flat_ItemInfo_Enchant'
    }

    files_to_unpack = {}
    for p in paks:
        all_lines = get_pak_file_list(p)
        for line in all_lines:
            if not line.endswith('.uexp'):
                continue
            base = line.split('/')[-1].replace('.uexp', '')
            clean = base.replace('IMG_', '').replace('TEX_', '').lower() + '.png'

            is_item = line.startswith('ProjectRED/Content/RED/UI/Resource/Texture/Image/Item/')
            is_extra = base in extra_targets

            if is_item or is_extra:
                if clean not in existing_pngs:
                    if p not in files_to_unpack:
                        files_to_unpack[p] = []
                    files_to_unpack[p].append(line)

    total_candidates = sum(len(v) for v in files_to_unpack.values())
    print(f"Total de arquivos .uexp a descompactar: {total_candidates}")

    for p, flist in files_to_unpack.items():
        unpack_files(p, flist)

    print("Decodificando arquivos extraídos para PNG...")
    tasks = []
    for root, dirs, files in os.walk(TMP_EXTRACT_DIR):
        for f in files:
            if f.endswith('.uexp'):
                uexp_path = os.path.join(root, f)
                base = f.replace('.uexp', '')
                clean_name = base.replace('IMG_', '').replace('TEX_', '').lower() + '.png'
                out_png = os.path.join(ASSETS_OUT, clean_name)
                tasks.append((uexp_path, out_png))

    print(f"Total de tarefas de decodificação: {len(tasks)}")

    def do_decode(t):
        uexp, out = t
        return decode_uexp_to_png(uexp, out)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(do_decode, tasks))

    success_count = sum(1 for r in results if r)
    print(f"✓ Concluído: {success_count}/{len(tasks)} texturas decodificadas com sucesso!")

    # Cleanup temp directory
    print("Limpando diretório temporário...")
    shutil.rmtree(TMP_EXTRACT_DIR, ignore_errors=True)
    print(f"Total atual em assets/items: {len(os.listdir(ASSETS_OUT))} arquivos PNG.")

if __name__ == '__main__':
    main()
