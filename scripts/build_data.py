#!/usr/bin/env python3
"""
VAMPIR (ProjectRED) Web Application Data Builder
Parses raw game CSVs, documentation and extracted game texture assets
to generate structured JSON databases with rich image bindings.
"""

import csv
import json
import os
import re
from collections import defaultdict, Counter

BASE_DIR = "/home/thiagofdso/vampir"
CSV_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/patch_extracted/ProjectRED/Content/RED/Data/CSV")
L10N_DIR = os.path.join(CSV_DIR, "L10N/pt")
OUT_DIR = os.path.join(BASE_DIR, "faq/data")
ASSETS_DIR = os.path.join(BASE_DIR, "faq/assets")

os.makedirs(OUT_DIR, exist_ok=True)

# Preload available images
monster_pngs = set(os.listdir(os.path.join(ASSETS_DIR, "monsters"))) if os.path.exists(os.path.join(ASSETS_DIR, "monsters")) else set()
item_pngs = set(os.listdir(os.path.join(ASSETS_DIR, "items"))) if os.path.exists(os.path.join(ASSETS_DIR, "items")) else set()
dungeon_pngs = set(os.listdir(os.path.join(ASSETS_DIR, "dungeons"))) if os.path.exists(os.path.join(ASSETS_DIR, "dungeons")) else set()
class_pngs = set(os.listdir(os.path.join(ASSETS_DIR, "classes"))) if os.path.exists(os.path.join(ASSETS_DIR, "classes")) else set()

def load_csv_dict(filepath, key_col="Id"):
    data = {}
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return data
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = row.get(key_col, "").strip()
            if k:
                data[k] = row
    return data

def load_csv_list(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return []
    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

# Authentic Item Rarity System extracted from DT_CommonColor.uasset & ItemFilter.csv
RARITY_MAP = {
    0: {
        "code": 0,
        "name": "Comum",
        "name_en": "Common",
        "color": "#979694",
        "highlight": "#CCCBC8",
        "class_name": "rarity-common",
        "badge_class": "badge-rarity-common"
    },
    1: {
        "code": 1,
        "name": "Incomum",
        "name_en": "Uncommon",
        "color": "#64935E",
        "highlight": "#C5F1C0",
        "class_name": "rarity-uncommon",
        "badge_class": "badge-rarity-uncommon"
    },
    2: {
        "code": 2,
        "name": "Raro",
        "name_en": "Rare",
        "color": "#5E84CD",
        "highlight": "#C9E1FF",
        "class_name": "rarity-rare",
        "badge_class": "badge-rarity-rare"
    },
    3: {
        "code": 3,
        "name": "Heroico",
        "name_en": "Epic",
        "color": "#A165E8",
        "highlight": "#E6D8FF",
        "class_name": "rarity-epic",
        "badge_class": "badge-rarity-epic"
    },
    4: {
        "code": 4,
        "name": "Lendário",
        "name_en": "Legendary",
        "color": "#E2BE6F",
        "highlight": "#FCF2D6",
        "class_name": "rarity-legendary",
        "badge_class": "badge-rarity-legendary"
    },
    5: {
        "code": 5,
        "name": "Mítico",
        "name_en": "Mythic",
        "color": "#FF7373",
        "highlight": "#FFEAE0",
        "class_name": "rarity-mythic",
        "badge_class": "badge-rarity-mythic"
    },
    100: {
        "code": 100,
        "name": "Único",
        "name_en": "Unique",
        "color": "#FFA3D1",
        "highlight": "#FFE6F1",
        "class_name": "rarity-unique",
        "badge_class": "badge-rarity-unique"
    },
    101: {
        "code": 101,
        "name": "Sazonal",
        "name_en": "Seasonal",
        "color": "#6EA8AC",
        "highlight": "#CBE6E8",
        "class_name": "rarity-seasonal",
        "badge_class": "badge-rarity-seasonal"
    },
    102: {
        "code": 102,
        "name": "Único",
        "name_en": "Unique",
        "color": "#FFA3D1",
        "highlight": "#FFE6F1",
        "class_name": "rarity-unique",
        "badge_class": "badge-rarity-unique"
    }
}

def get_rarity_info(code):
    try:
        c = int(code)
    except (ValueError, TypeError):
        c = 0
    return RARITY_MAP.get(c, RARITY_MAP[0])

print("Reading CSVs...")
class_raw = load_csv_dict(os.path.join(CSV_DIR, "Class.csv"))
class_names = load_csv_dict(os.path.join(L10N_DIR, "Class_Name.csv"))
skill_raw = load_csv_dict(os.path.join(CSV_DIR, "Skill.csv"))
skill_names = load_csv_dict(os.path.join(L10N_DIR, "Skill_Name.csv"))
npc_raw = load_csv_dict(os.path.join(CSV_DIR, "Npc.csv"))
npc_list = load_csv_list(os.path.join(CSV_DIR, "Npc.csv"))
npc_names = load_csv_dict(os.path.join(L10N_DIR, "Npc_Name.csv"))
dungeon_raw = load_csv_dict(os.path.join(CSV_DIR, "Dungeon.csv"))
dungeon_list = load_csv_list(os.path.join(CSV_DIR, "Dungeon.csv"))
dungeon_names = load_csv_dict(os.path.join(L10N_DIR, "Dungeon_Name.csv"))
item_raw = load_csv_dict(os.path.join(CSV_DIR, "Item.csv"))
item_names = load_csv_dict(os.path.join(L10N_DIR, "Item_Name.csv"))
skill_card_raw = load_csv_dict(os.path.join(CSV_DIR, "SkillCard.csv"), "ItemId")
const_raw = load_csv_list(os.path.join(CSV_DIR, "Const.csv"))

# Additional gameplay & monster tables from extracted CSVs
npcbattle_list = load_csv_list(os.path.join(CSV_DIR, "NpcBattle.csv"))
npc_battles_map = defaultdict(list)
for r in npcbattle_list:
    npc_battles_map[r.get("GroupId", "").strip()].append(r)

npc_spawns_map = defaultdict(list)
for r in load_csv_list(os.path.join(CSV_DIR, "NpcSpawn.csv")):
    npc_spawns_map[r.get("NpcInfoId", "").strip()].append(r)

npc_spawn_details_map = defaultdict(list)
for r in load_csv_list(os.path.join(CSV_DIR, "NpcSpawnDetail.csv")):
    npc_spawn_details_map[r.get("NpcSpawnId", "").strip()].append(r)

npc_profiles_map = defaultdict(list)
for r in load_csv_list(os.path.join(CSV_DIR, "NpcProfile.csv")):
    npc_profiles_map[r.get("NpcInfoId", "").strip()].append(r)

world_names_map = load_csv_dict(os.path.join(L10N_DIR, "World_Name.csv"))

dungeon_boss_map = defaultdict(list)
for r in dungeon_list:
    bid = r.get("BossInfoId", "").strip()
    if bid:
        dname_row = dungeon_names.get(r.get("Id", "").strip(), {})
        dname = dname_row.get("Name", "").strip() or f"Masmorra #{r.get('Id')}"
        dungeon_boss_map[bid].append(dname)

# ==========================================
# 0. DROPS DATABASE (recompensas_por_npc.csv)
# ==========================================
print("Loading Monster Drops catalog from analysis/versions/2026-10-31/reports/drops/recompensas_por_npc.csv...")
DROPS_CSV = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/drops/recompensas_por_npc.csv")
npc_drops = defaultdict(list)
item_droppers_raw = defaultdict(list)
drop_npc_ids = set()
dropped_item_ids = set()

if os.path.exists(DROPS_CSV):
    with open(DROPS_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            nid = r["npc_id"].strip()
            nname = r["npc_nome"].strip()
            nlvl = r.get("npc_nivel", "").strip()
            ngrade = r.get("npc_grade", "0").strip()
            iid = r.get("reward_param", "").strip()
            iname = r.get("item_nome", "").strip()
            rarity = r.get("item_raridade", "0").strip()
            qmin = r.get("quantidade_min", "1").strip()
            qmax = r.get("quantidade_max", "1").strip()
            rate = r.get("taxa_raiz_bruta", "").strip()
            if not iid or not iname or not iid.isdigit():
                continue
            drop_npc_ids.add(nid)
            dropped_item_ids.add(iid)
            npc_drops[nid].append({
                "item_id": iid,
                "name": iname,
                "rarity": rarity,
                "qty_min": qmin,
                "qty_max": qmax,
                "rate": rate
            })
            item_droppers_raw[iid].append({
                "npc_id": nid,
                "npc_name": nname,
                "npc_level": nlvl,
                "npc_grade": ngrade,
                "qty_min": qmin,
                "qty_max": qmax,
                "rate": rate
            })
print(f"  ✓ Loaded drops for {len(npc_drops)} NPCs, covering {len(dropped_item_ids)} distinct dropped items.")

# ==========================================
# 1. CLASSES
# ==========================================
print("Processing Classes with official portraits and icons...")
CLASSES_CONFIG = {
    "1": {
        "slug": "vipora",
        "resource": "DarkMage",
        "weapon": "Orbe Mágico",
        "role": "Mago de Maldição / DPS Mágico à Distância",
        "archetype": "Feitiçaria Ancestral & Venenos",
        "color": "#8b5cf6",
        "radar": {"atq": 90, "def": 60, "hp": 65, "alcance": 95, "velocidade": 70, "controle": 85},
        "highlights": [
            "Controle de área com dano contínuo de veneno (DoT)",
            "Redução massiva de Resistência Mágica dos alvos",
            "Escudo de veneno proporcional ao poder de feitiçaria",
            "Sustentação vampírica através do Chamado de Sangue"
        ]
    },
    "2": {
        "slug": "ceifador",
        "resource": "Reaper",
        "weapon": "Foice das Sombras",
        "role": "Assassino Corpo a Corpo / Dano de Ruptura (Burst)",
        "archetype": "Retalhamento Sombrio & Execução",
        "color": "#ec4899",
        "radar": {"atq": 95, "def": 65, "hp": 70, "alcance": 50, "velocidade": 95, "controle": 80},
        "highlights": [
            "Dano explosivo em alvos únicos e isolados",
            "Prisão sombria e imobilização de alvos em fuga",
            "Amplificação de Dano Crítico e Dano Corpo a Corpo",
            "Pele grossa e regeneração sombria baseada em ATQ"
        ]
    },
    "3": {
        "slug": "carnificina",
        "resource": "Gunner",
        "weapon": "Armas de Fogo de Sangue Abençoado",
        "role": "Atirador Ranged DPS / Alta Cadência e Perfuração",
        "archetype": "Artilharia Balística & Sangue Sagrado",
        "color": "#f97316",
        "radar": {"atq": 90, "def": 55, "hp": 60, "alcance": 100, "velocidade": 85, "controle": 65},
        "highlights": [
            "Maior alcance efetivo do jogo (até 8.5 metros)",
            "Disparos rápidos consecutivos e perfuração de armadura",
            "Auto-buffs de Esquiva (ESQ) e Precisão Ranged",
            "Controle de distanciamento e knockback de ameaças"
        ]
    },
    "4": {
        "slug": "manchado_de_sangue",
        "resource": "SwordMan",
        "weapon": "Espada de Sangue Carmesim",
        "role": "Cavaleiro / Tanque de Absorção e Autocura",
        "archetype": "Sacrifício de Sangue & Lâmina Sádica",
        "color": "#ef4444",
        "radar": {"atq": 80, "def": 95, "hp": 95, "alcance": 45, "velocidade": 65, "controle": 85},
        "highlights": [
            "Alta sobrevivência com roubo de vida ativo",
            "Puxão de inimigos (Sede de Sangue) e atordoamento em área",
            "Buffs de defesa física e redução de dano recebido",
            "Fúria de sangue que converte dano causado em PV direto"
        ]
    },
    "5": {
        "slug": "akasha",
        "resource": "Fighter",
        "weapon": "Garras & Tonfas Corpóreas",
        "role": "Brawler / Perseguidor e Rompedor de Defesas",
        "archetype": "Mutação Corporal & Frenesi Vampírico",
        "color": "#eab308",
        "radar": {"atq": 90, "def": 80, "hp": 85, "alcance": 40, "velocidade": 90, "controle": 90},
        "highlights": [
            "Roubo de atributos em tempo real (drena ATQ do alvo)",
            "Frenesi Carmesim com aumento extremo de cadência de golpes",
            "Libertação Absoluta (imunidade a CC e atordoamentos)",
            "Combos velozes e quebra de postura de chefes"
        ]
    }
}

classes_data = []
for cid, meta in CLASSES_CONFIG.items():
    raw_c = class_raw.get(cid, {})
    name_c = class_names.get(cid, {})
    name = name_c.get("Name", meta["resource"])
    desc = name_c.get("Desc", "").strip()
    desc_short = name_c.get("DescShort", "").strip()
    
    slug = meta["slug"]
    rname = meta["resource"].lower()
    
    icon_file = f"{rname}_icon.png" if f"{rname}_icon.png" in class_pngs else "logo.png"
    male_file = f"{rname}_male.png" if f"{rname}_male.png" in class_pngs else ""
    female_file = f"{rname}_female.png" if f"{rname}_female.png" in class_pngs else ""

    classes_data.append({
        "id": int(cid),
        "slug": meta["slug"],
        "name": name,
        "resource": meta["resource"],
        "role": meta["role"],
        "archetype": meta["archetype"],
        "weapon": meta["weapon"],
        "desc": desc,
        "desc_short": desc_short,
        "move_speed": raw_c.get("MoveSpeed", "550"),
        "body_radius": raw_c.get("BodyRadius", "25"),
        "color": meta["color"],
        "radar": meta["radar"],
        "highlights": meta["highlights"],
        "icon_img": f"assets/classes/{icon_file}",
        "male_img": f"assets/classes/{male_file}" if male_file else "",
        "female_img": f"assets/classes/{female_file}" if female_file else ""
    })

with open(os.path.join(OUT_DIR, "classes.json"), "w", encoding="utf-8") as f:
    json.dump(classes_data, f, indent=2, ensure_ascii=False)

# ==========================================
# 2. BUILDS & SPECIALIZED VARIANTS (FARM, CHEFE, PVP, GERAL)
# ==========================================
print("Processing Builds and Variants from docs/builds/...")
DOCS_BUILDS_DIR = os.path.join(BASE_DIR, "docs/builds")

def parse_markdown_build_file(fpath):
    if not os.path.exists(fpath):
        return {"title": "", "objective": "", "skills": [], "equipment": []}
    
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    t_match = re.search(r"^#\s+(.+)$", content, re.M)
    title = t_match.group(1).strip() if t_match else ""

    obj_match = re.search(r"\*\*Objetivo:\*\*\s*(.+?)(?:\n\n|\n[A-Z]|\nEsta)", content, re.S)
    objective = obj_match.group(1).strip().replace("\n", " ") if obj_match else ""

    skills = []
    table_m = re.search(r"\|\s*ID[^\n]+\n((?:\|[^\n]+\n)+)", content)
    if table_m:
        lines = table_m.group(1).strip().splitlines()
        for l in lines:
            if "---" in l: continue
            parts = [c.strip() for c in l.split("|")[1:-1]]
            if len(parts) >= 3:
                clean_col0 = parts[0].replace("`", "")
                m_id = re.search(r"(\d{5,7})", clean_col0)
                sid = m_id.group(1) if m_id else ""
                sname = clean_col0.replace(sid, "").strip()
                
                if not sname and len(parts) > 1 and not parts[1].isdigit():
                    sname = parts[1].replace("`", "").strip()
                    role = parts[2] if len(parts) > 2 else ""
                    book = parts[4] if len(parts) > 4 else ""
                    cd = parts[2] if len(parts) > 2 else ""
                    mp = ""
                    rng = ""
                    rarity = ""
                    slot = parts[3] if len(parts) > 3 else "1"
                else:
                    role = parts[1] if len(parts) > 1 else ""
                    cd = parts[2] if len(parts) > 2 else ""
                    mp = parts[3] if len(parts) > 3 else ""
                    rng = parts[4] if len(parts) > 4 else ""
                    rarity = parts[5] if len(parts) > 5 else ""
                    slot = parts[6] if len(parts) > 6 else "1"
                    book = ""

                skills.append({
                    "id": sid,
                    "name": sname if sname else f"Habilidade {sid}",
                    "role": role,
                    "cooldown": cd,
                    "mp": mp,
                    "range": rng,
                    "rarity": rarity,
                    "slot": slot,
                    "book": book
                })

    equipment = []
    eq_m = re.search(r"##\s+(?:Equipamentos candidatos|Possíveis armas).*?(\|[^\n]+\|.*?\n(?:\|[^\n]+\n)+)", content, re.S)
    if eq_m:
        lines = eq_m.group(1).strip().splitlines()
        for l in lines:
            if "---" in l or "Raridade" in l or "Item" in l: continue
            parts = [c.strip() for c in l.split("|")[1:-1]]
            if len(parts) >= 3:
                equipment.append({
                    "item": parts[0].replace("`", ""),
                    "rarity": parts[1],
                    "attributes": parts[2],
                    "class_info": parts[3] if len(parts) > 3 else "",
                    "level_limits": parts[4] if len(parts) > 4 else ""
                })

    return {"title": title, "objective": objective, "skills": skills, "equipment": equipment}

builds_data = []

class_build_slugs = [
    (1, "Víbora", "DarkMage", "vipora"),
    (2, "Ceifador", "Reaper", "ceifador"),
    (3, "Carnificina", "Gunner", "carnificina"),
    (4, "Manchado de Sangue", "SwordMan", "manchado_de_sangue"),
    (5, "Akasha", "Fighter", "akasha")
]

for cid, cname, cres, cslug in class_build_slugs:
    base_raw = parse_markdown_build_file(os.path.join(DOCS_BUILDS_DIR, f"{cslug}.md"))
    farm_raw = parse_markdown_build_file(os.path.join(DOCS_BUILDS_DIR, "variantes", f"{cslug}-farm.md"))
    chefe_raw = parse_markdown_build_file(os.path.join(DOCS_BUILDS_DIR, "variantes", f"{cslug}-chefe.md"))
    pvp_raw = parse_markdown_build_file(os.path.join(DOCS_BUILDS_DIR, "variantes", f"{cslug}-pvp.md"))

    variants = [
        {
            "type": "geral",
            "badge": "🛡️ PvE Geral Equilibrado",
            "title": base_raw["title"] or f"Build de {cname}: PvE Geral",
            "objective": base_raw["objective"] or "Equilíbrio de sobrevivência, sustentação e dano para progressão geral.",
            "skills": base_raw["skills"],
            "equipment": base_raw["equipment"] or [
                {"item": f"Armamento Principal de {cname}", "rarity": "Raro a Épico", "attributes": "Bônus de dano principal da classe e atributos base", "class_info": str(cid), "level_limits": "Progresso Natural"}
            ],
            "stat_priority": ["Dano Principal", "Redução de Cooldown (Haste)", "Pontos de Sangue (BP)", "Defesa / Resistência", "Taxa Crítica"]
        },
        {
            "type": "farm",
            "badge": "🌾 Farm em Massa & Área (AoE)",
            "title": farm_raw["title"] or f"{cname}: Variante Farm",
            "objective": farm_raw["objective"] or "Limpeza acelerada de ondas de monstros com manutenção contínua de PV e MP.",
            "skills": farm_raw["skills"],
            "equipment": farm_raw["equipment"],
            "stat_priority": ["Dano a Monstros", "Dano em Área", "Recuperação de MP", "Velocidade de Movimento", "Taxa de Ataque"]
        },
        {
            "type": "chefe",
            "badge": "👑 Caçador de Chefes (Single-Target)",
            "title": chefe_raw["title"] or f"{cname}: Variante Chefe",
            "objective": chefe_raw["objective"] or "Dano concentrado em alvo único, quebra de defesa e sobrevivência contra chefes de masmorra.",
            "skills": chefe_raw["skills"],
            "equipment": chefe_raw["equipment"],
            "stat_priority": ["Dano a Chefes", "Perfuração de Defesa", "Dano Crítico", "Taxa Crítica", "Resistência a Dano de Habilidade"]
        },
        {
            "type": "pvp",
            "badge": "⚔️ Conflito PvP & Controle (JxJ)",
            "title": pvp_raw["title"] or f"{cname}: Variante PvP",
            "objective": pvp_raw["objective"] or "Duelo e combate em zonas de conflito, foco em controle de grupo, ruptura e mitigação de dano de outros jogadores.",
            "skills": pvp_raw["skills"],
            "equipment": pvp_raw["equipment"],
            "stat_priority": ["Dano em Jogadores", "Redução de Dano PvP", "Imunidade a CC / Tenacidade", "Esquiva (ESQ)", "Penetração"]
        }
    ]

    builds_data.append({
        "class_id": cid,
        "class_name": cname,
        "resource": cres,
        "slug": cslug,
        "icon_img": f"assets/classes/{cres.lower()}_icon.png",
        "male_img": f"assets/classes/{cres.lower()}_male.png",
        "female_img": f"assets/classes/{cres.lower()}_female.png",
        "variants": variants
    })

with open(os.path.join(OUT_DIR, "builds.json"), "w", encoding="utf-8") as f:
    json.dump(builds_data, f, indent=2, ensure_ascii=False)

with open(os.path.join(OUT_DIR, "builds.json"), "w", encoding="utf-8") as f:
    json.dump(builds_data, f, indent=2, ensure_ascii=False)

# ==========================================
# 3. SKILLS DATABASE (ENRICHED WITH 425 SKILL BOOKS)
# ==========================================
print("Processing Skills & Mapping Skill Books...")

# Pre-gather craft targets to check if books are craftable
recipe_target_map = {}
receitas_path_early = os.path.join(BASE_DIR, "analysis/reports/jogo/receitas.csv")
if os.path.exists(receitas_path_early):
    with open(receitas_path_early, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            succ_list = json.loads(r.get("SuccessRewardGroupId_registros_json", "[]")) if r.get("SuccessRewardGroupId_registros_json") else []
            if succ_list:
                param = succ_list[0].get("Param", "")
                if param:
                    recipe_target_map[param] = r.get("Id", "")

# Load skill books catalog
skill_books_csv_path = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/habilidades-livros/habilidades-e-livros.csv")
skills_to_books = defaultdict(list)
all_linked_book_ids = set()

if os.path.exists(skill_books_csv_path):
    with open(skill_books_csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = r["skill_id"].strip()
            raw_items = json.loads(r.get("itens_json", "[]"))
            for it in raw_items:
                iid = it.get("item_id", "").strip()
                all_linked_book_ids.add(iid)

                b_name = it.get("nome", "").strip()
                b_desc = it.get("descricao", "").strip()
                if "2025-" in b_name or "2026-" in b_name:
                    m = re.search(r'<SkillEffect>(Livro de Habilidade:[^<]+)</>', b_desc)
                    if m:
                        b_name = m.group(1).strip()
                    else:
                        b_name = f"Item de Habilidade #{iid}"
                b_name = re.sub(r'\{[^}]+\}', '', b_name).strip()

                cls_id_str = it.get("classe", "").strip()
                cls_id = int(cls_id_str) if cls_id_str.isdigit() else 0
                class_names_map = {1: "Víbora", 2: "Ceifador", 3: "Carnificina", 4: "Manchado de Sangue", 5: "Akasha", 0: "Todas as Classes"}
                b_class_name = class_names_map.get(cls_id, "Todas as Classes")

                rar_code = int(it.get("raridade", 0)) if str(it.get("raridade", "")).isdigit() else 0
                r_info = get_rarity_info(rar_code)

                # Icon matching from item_raw
                i_row = item_raw.get(iid, {})
                raw_img = i_row.get("Img", "").strip()
                clean_img = raw_img.replace("IMG_", "").replace("TEX_", "").lower() + ".png"
                if clean_img in item_pngs:
                    b_icon = f"assets/items/{clean_img}"
                elif cls_id == 1:
                    b_icon = "assets/items/skillbook_darkmage_02.png" if "skillbook_darkmage_02.png" in item_pngs else "assets/items/skillbook_darkmage.png"
                elif cls_id == 2:
                    b_icon = "assets/items/skillbook_reaper_02.png" if "skillbook_reaper_02.png" in item_pngs else "assets/items/skillbook_reaper.png"
                elif cls_id == 3:
                    b_icon = "assets/items/skillbook_gunner_02.png" if "skillbook_gunner_02.png" in item_pngs else "assets/items/skillbook_gunner.png"
                elif cls_id == 4:
                    b_icon = "assets/items/skillbook_swordman_02.png" if "skillbook_swordman_02.png" in item_pngs else "assets/items/skillbook_swordman.png"
                elif cls_id == 5:
                    b_icon = "assets/items/skillbook_fighter_02.png" if "skillbook_fighter_02.png" in item_pngs else "assets/items/skillbook_fighter.png"
                else:
                    b_icon = "assets/items/skillbook_allclass.png"

                t_code = it.get("tipo", "31")
                t_name = "Livro de Habilidade" if t_code == "31" else "Item de Aprendizado / Emblema"
                clean_desc = re.sub(r'<[^>]+>', '', b_desc).strip()

                is_craft = iid in recipe_target_map
                craft_rec_id = recipe_target_map.get(iid, "")

                skills_to_books[sid].append({
                    "id": iid,
                    "name": b_name,
                    "type_code": t_code,
                    "type_name": t_name,
                    "class_id": cls_id,
                    "class_name": b_class_name,
                    "rarity": rar_code,
                    "rarity_name": r_info["name"],
                    "rarity_color": r_info["color"],
                    "rarity_highlight": r_info["highlight"],
                    "rarity_badge_class": r_info["badge_class"],
                    "icon_img": b_icon,
                    "desc": clean_desc,
                    "is_craftable": is_craft,
                    "craft_recipe_id": craft_rec_id
                })

skills_catalog = []
class_type_map = {
    "DarkMage": {"name": "Víbora", "class_id": 1, "icon": "darkmage_icon.png"},
    "Reaper": {"name": "Ceifador", "class_id": 2, "icon": "reaper_icon.png"},
    "Gunner": {"name": "Carnificina", "class_id": 3, "icon": "gunner_icon.png"},
    "SwordMan": {"name": "Manchado de Sangue", "class_id": 4, "icon": "swordman_icon.png"},
    "Fighter": {"name": "Akasha", "class_id": 5, "icon": "fighter_icon.png"},
    "All": {"name": "Comum / Todas", "class_id": 0, "icon": "logo.png"}
}

target_type_map = {
    "0": "Inimigo Único",
    "1": "Área ao Redor",
    "2": "Cone Frontal",
    "3": "Linha Reta / Projétil",
    "4": "Próprio Personagem (Self-Buff)",
    "5": "Aliado Selecionado",
    "6": "Grupo Inteiro"
}

for sid, srow in skill_raw.items():
    sname_row = skill_names.get(sid)
    if not sname_row:
        continue
    
    name = sname_row.get("Name", "").strip()
    desc = sname_row.get("Description", "").strip()
    effect_desc = sname_row.get("EffectDescription", "").strip()
    
    if not name or "2025-05-21 Registered" in name or "2026-" in name:
        if not desc or "Registered" in desc:
            continue
        name = f"Habilidade {sid}"
        
    ctype_raw = srow.get("ClassType", "").strip()
    class_info = class_type_map.get(ctype_raw, {"name": ctype_raw if ctype_raw else "Geral", "class_id": 0, "icon": "logo.png"})
    
    cd_min = srow.get("MinCoolTime", "")
    cd_max = srow.get("MaxCoolTime", "")
    cd_display = f"{float(cd_max)/1000.0:.1f}s" if cd_max and cd_max.isdigit() else (f"{float(cd_min)/1000.0:.1f}s" if cd_min and cd_min.isdigit() else "Instantâneo")
    
    mp_min = srow.get("MpMin", "0")
    mp_max = srow.get("MpMax", "0")
    mp_display = mp_max if mp_max and mp_max != "0" else (mp_min if mp_min != "0" else "Sem Custo")
    
    dist = srow.get("MaxCastDistance", "0")
    dist_display = f"{float(dist)/100.0:.1f}m" if dist and dist.isdigit() and int(dist) > 0 else "Curto Alcance"
    
    target_type = target_type_map.get(srow.get("TargetType", ""), "Alvo")
    
    b_list = skills_to_books.get(sid, [])
    has_b = len(b_list) > 0
    notes = ""
    if sid == "72":
        name = "Habilidade 72"
        notes = "Registro canônico sem nome próprio traduzido no cliente ('2025-05-21 Registered'); efeito explícito reduz 50% da recarga ativa. Sem livro vinculado diretamente nos arquivos do jogo."
        has_b = False
        b_list = []
        
    skills_catalog.append({
        "id": sid,
        "name": name,
        "description": desc,
        "effect_description": effect_desc,
        "class_id": class_info["class_id"],
        "class_name": class_info["name"],
        "class_resource": ctype_raw,
        "icon_img": f"assets/classes/{class_info['icon']}",
        "category": srow.get("Category", "1"),
        "cooldown": cd_display,
        "mp_cost": mp_display,
        "range": dist_display,
        "target_type": target_type,
        "stack_count": srow.get("StackCount", "1"),
        "is_slot_skill": srow.get("UseSkillSlot", "0") == "1",
        "dash_offset": srow.get("DashOffset", "0"),
        "mobile": srow.get("Mobile", "0") == "1",
        "has_books": has_b,
        "books_count": len(b_list),
        "books": b_list,
        "notes": notes
    })

with open(os.path.join(OUT_DIR, "skills.json"), "w", encoding="utf-8") as f:
    json.dump(skills_catalog, f, indent=2, ensure_ascii=False)
print(f"  ✓ Processed {len(skills_catalog)} skills ({sum(1 for s in skills_catalog if s['has_books'])} with linked skill books).")

# ==========================================
# 4. BOSSES & ENEMIES (DEDUPLICATED & ENRICHED)
# ==========================================
print("Processing Bosses & Enemies with deduplication and rich combat data...")
DAYS_MAP = {
    '1': 'Segunda-feira', '2': 'Terça-feira', '3': 'Quarta-feira',
    '4': 'Quinta-feira', '5': 'Sexta-feira', '6': 'Sábado', '7': 'Domingo'
}
APPEARANCE_TYPE_MAP = {
    '0': 'Padrão / Terrestre',
    '1': 'Mordida Selvagem (HumanNeckBite)',
    '2': 'Estrangulamento (Strangulation)',
    '3': 'Drenagem / Absorção (Absorption)',
    '4': 'Voo / Fase Aérea (Flight)',
    '5': 'Profeta / Invocador (Prophet)',
    '6': 'Especial Mortífero (NotDeadly)',
    '7': 'Forma Rara'
}
ATTRIBUTE_MAP = {
    '1': 'Fogo / Carmesim',
    '2': 'Gelo / Água',
    '3': 'Veneno / Trevas',
    '7': 'Neutro / Físico'
}
grade_map = {
    "0": "Monstro Comum",
    "1": "Monstro de Elite",
    "2": "Chefe de Masmorra (Boss)",
    "3": "Chefe de Campo (Field Boss)"
}

default_boss_portraits = [
    "abysslord_01.png",
    "blacklotuscatainboss.png",
    "brandedoneboss.png",
    "delilahboss.png",
    "demonexecutioner_01.png",
    "draco_01.png",
    "duncan_01.png",
    "forgottenlord_01.png",
    "hermitfiendboss05.png"
]

# Exclude invisible UE5 collision dummies / triggers (BP_Monster_Invisible01)
visible_npcs = [
    n for n in npc_list
    if (n.get("GradeType", "").strip() in ["1", "2", "3"] or n.get("Id", "").strip() in drop_npc_ids)
    and "invisible" not in n.get("Blueprint", "").lower()
]

# Deduplicate into unique combat profiles
groups = defaultdict(list)
for n in visible_npcs:
    nid = n.get("Id", "").strip()
    name_row = npc_names.get(nid, {})
    name = name_row.get("Name", "").strip() or n.get("NameEN", "").strip() or f"Monstro #{nid}"
    bp = n.get("Blueprint", "").strip()
    grade = n.get("GradeType", "0").strip()

    # Disambiguate appendages if name is identical in localization
    if bp == "BP_MonsterAlrauneTentacleFrontBoss":
        name = "Alraune (Tentáculos Frontais)"
    elif bp == "BP_MonsterAlrauneTentacleBackBoss":
        name = "Alraune (Tentáculos Traseiros)"

    groups[(name, bp, grade)].append(n)

bosses_catalog = []
for (name, bp, grade), items in groups.items():
    primary = items[0]
    pid = primary.get("Id", "").strip()
    title_row = npc_names.get(pid, {})
    title = title_row.get("Title", "").strip()
    if not title:
        title = "Chefe Mundial" if grade == "3" else ("Guardião de Masmorra" if grade == "2" else ("Inimigo de Elite" if grade == "1" else "Monstro de Campo / Caçada"))

    levels = sorted(list(set(int(x.get("Level", 0)) for x in items if x.get("Level", "").isdigit())))
    min_lvl = levels[0] if levels else 1
    max_lvl = levels[-1] if levels else 1
    lvl_disp = f"Nv. {min_lvl}" if min_lvl == max_lvl else f"Nv. {min_lvl} - {max_lvl}"

    # Tiers
    tiers = []
    seen_tiers = set()
    for item in items:
        bg = item.get("BattleGroupId", "").strip()
        lvl = int(item.get("Level") or 0)
        bat_rows = npc_battles_map.get(bg, [{}])
        bat = bat_rows[0] if bat_rows else {}
        hp = int(bat.get("HP") or 0)
        atk = int(bat.get("AttackPower") or 0)
        df = int(bat.get("DefensePower") or 0)
        sig = (lvl, hp, atk, df)
        if sig not in seen_tiers:
            seen_tiers.add(sig)
            tiers.append({
                "id": item.get("Id", "").strip(),
                "level": lvl,
                "hp": hp,
                "atk": atk,
                "def": df,
                "dungeon": ", ".join(dungeon_boss_map.get(item.get("Id", "").strip(), []))
            })
    tiers.sort(key=lambda x: x["level"])
    peak_tier = tiers[-1] if tiers else {"hp": 0, "atk": 0, "def": 0}

    # Skills from NpcProfile + NpcBattle
    skill_ids = []
    for item in items:
        for p in npc_profiles_map.get(item.get("Id", "").strip(), []):
            for sid in p.get("UseSkillId", "").split(","):
                sid = sid.strip()
                if sid and sid not in skill_ids:
                    skill_ids.append(sid)
        bg = item.get("BattleGroupId", "").strip()
        for bat in npc_battles_map.get(bg, []):
            for sid in bat.get("SkillIdList", "").split(","):
                sid = sid.strip()
                if sid and sid not in skill_ids:
                    skill_ids.append(sid)

    skills_data = []
    for sid in skill_ids:
        sk = skill_raw.get(sid, {})
        sn = skill_names.get(sid, {})
        sname = sn.get("Name", "").strip()
        sdesc = sn.get("Description", "").strip() or sn.get("EffectDescription", "").strip()
        cd_raw = sk.get("MinCoolTime") or sk.get("MaxCoolTime") or "0"
        cd = f"{float(cd_raw)/1000:.1f}s" if cd_raw.isdigit() and int(cd_raw) > 0 else "-"
        dist_raw = sk.get("MaxCastDistance") or sk.get("AiMaxCastDistance") or "0"
        dist = f"{int(dist_raw)//100}m" if dist_raw.isdigit() and int(dist_raw) > 0 else "-"
        skills_data.append({
            "id": sid,
            "name": sname if sname else f"Habilidade #{sid}",
            "desc": sdesc if sdesc else "Ataque ou manobra de combate do chefe.",
            "cooldown": cd,
            "range": dist
        })

    # Spawns & Schedule
    w_set = set()
    sched_list = []
    for item in items:
        nid = item.get("Id", "").strip()
        for sp in npc_spawns_map.get(nid, []):
            wid = sp.get("WorldInfoId", "").strip()
            wn = world_names_map.get(wid, {}).get("Name", "").strip()
            if wn:
                w_set.add(wn)
            for sd in npc_spawn_details_map.get(sp.get("Id", "").strip(), []):
                dow = DAYS_MAP.get(sd.get("DayOfWeek", "").strip(), "Diário")
                h = sd.get("Hour", "00").strip().zfill(2)
                m = sd.get("Minute", "00").strip().zfill(2)
                s_str = f"{dow} às {h}:{m}"
                if s_str not in sched_list:
                    sched_list.append(s_str)

    # Portrait matching
    img_field = primary.get("Img", "").strip()
    clean_img = img_field.replace("IMG_Monster_Portrait_", "").lower() + ".png"
    bp_clean = bp.lower()
    matched_img = ""
    if clean_img in monster_pngs:
        matched_img = clean_img
    else:
        for m in monster_pngs:
            token = m.replace(".png", "")
            if token in bp_clean or token in clean_img:
                matched_img = m
                break
    if not matched_img:
        matched_img = default_boss_portraits[int(pid) % len(default_boss_portraits)]

    # Dungeons
    dung_list = []
    for item in items:
        for d in dungeon_boss_map.get(item.get("Id", "").strip(), []):
            if d not in dung_list:
                dung_list.append(d)

    # Drops matching from npc_drops (recompensas_por_npc.csv)
    boss_drops = []
    seen_drops = set()
    for item_inst in items:
        nid = item_inst.get("Id", "").strip()
        for d in npc_drops.get(nid, []):
            d_key = d["item_id"]
            if d_key not in seen_drops:
                seen_drops.add(d_key)
                it_row = item_raw.get(d["item_id"], {})
                raw_img = it_row.get("Img", "").strip()
                clean_img_file = raw_img.replace("IMG_", "").replace("TEX_", "").lower() + ".png"
                drop_icon = f"assets/items/{clean_img_file}" if clean_img_file in item_pngs else "assets/items/flat_relic.png"
                qmin = d["qty_min"]
                qmax = d["qty_max"]
                qty_str = f"{qmin}~{qmax}" if qmin != qmax else qmin
                boss_drops.append({
                    "id": d["item_id"],
                    "name": d["name"],
                    "rarity": d["rarity"],
                    "qty": qty_str,
                    "rate": d["rate"],
                    "icon": drop_icon
                })

    bg0 = primary.get("BattleGroupId", "").strip()
    bat0 = npc_battles_map.get(bg0, [{}])[0] if npc_battles_map.get(bg0) else {}
    sight_raw = bat0.get("SightRange", "0")
    sight_disp = f"{int(sight_raw)//100}m" if sight_raw.isdigit() and int(sight_raw) > 0 else "Padrão"
    attr_disp = ATTRIBUTE_MAP.get(bat0.get("Attribute", "7"), "Neutro / Físico")
    appear_disp = APPEARANCE_TYPE_MAP.get(primary.get("MonsterAppearanceType", "0"), "Padrão / Terrestre")

    bosses_catalog.append({
        "id": pid,
        "name": name,
        "title": title,
        "grade_code": grade,
        "grade_name": grade_map.get(grade, "Chefe"),
        "level": str(max_lvl),
        "level_display": lvl_disp,
        "levels": levels,
        "tiers": tiers,
        "instance_count": len(items),
        "instance_ids": [x.get("Id", "").strip() for x in items],
        "portrait_img": f"assets/monsters/{matched_img}",
        "blueprint": bp,
        "scale_factor": primary.get("ScaleFactor", "1.0"),
        "body_radius": primary.get("BodyRadius", "50"),
        "walk_speed": primary.get("WalkSpeed", "120"),
        "run_speed": primary.get("RunSpeed", "400"),
        "appearance_type": appear_disp,
        "is_aggressive": bat0.get("Aggressive") == "1",
        "sight_range": sight_disp,
        "attribute": attr_disp,
        "world_map": ", ".join(sorted(w_set)) if w_set else "Masmorra / Campo Dimensional",
        "regions": sorted(list(w_set)),
        "drops": boss_drops,
        "spawn_schedule": ", ".join(sched_list),
        "dungeons": dung_list,
        "skills": skills_data,
        "hp_raw": str(peak_tier["hp"]),
        "atk_raw": str(peak_tier["atk"]),
        "def_raw": str(peak_tier["def"]),
        "reward_preview": "Equipamentos Épicos/Lendários, Livros Raros, Essências de Sangue" if grade in ["2", "3"] else "Materiais de Refino, Fragmentos de Sangue"
    })

bosses_catalog.sort(key=lambda x: (int(x["grade_code"]), int(x["level"])), reverse=True)

npc_to_boss_map = {}
all_regions_set = set()
for b in bosses_catalog:
    for inst_id in b["instance_ids"]:
        npc_to_boss_map[inst_id] = b
    for r in b.get("regions", []):
        if r:
            all_regions_set.add(r)
all_regions_list = sorted(list(all_regions_set))

with open(os.path.join(OUT_DIR, "bosses.json"), "w", encoding="utf-8") as f:
    json.dump(bosses_catalog, f, indent=2, ensure_ascii=False)

# ==========================================
# 5. DUNGEONS (WITH REAL ARTWORKS)
# ==========================================
print("Processing Dungeons with background artworks...")
dungeon_type_labels = {
    "1": "Masmorra de Grupo (Party Dungeon)",
    "2": "Masmorra de Conquista (Conquest)",
    "3": "Zona de Chefe de Elite (Elite Boss Zone)",
    "4": "Masmorra de Guilda / Defesa (Guild Dungeon)",
    "5": "Masmorra de História Narrativa",
    "6": "Masmorra Tutorial / Treinamento",
    "7": "Masmorra da Linhagem Vampírica (Bloodline)",
    "8": "Masmorra Infinita (Vale Naricanje)",
    "9": "Masmorra Inter-Servidor (Cross-Server)",
    "10": "Masmorra de Invasão Temporal",
    "11": "Masmorra de Evento Sazonal",
    "12": "Arena de Provação Vampírica",
    "13": "Torneio Mundial (World Tournament)",
    "14": "Catacumba Secreta"
}

dungeons_catalog = []
default_dungeon_img = "bloodruins.png" if "bloodruins.png" in dungeon_pngs else "splash.png"

for did, drow in dungeon_raw.items():
    dname_row = dungeon_names.get(did)
    name = dname_row.get("Name", "").strip() if dname_row else ""
    desc = dname_row.get("Description", "").strip() if dname_row else ""
    
    if not name or "2025-" in name or "2026-" in name:
        name = f"Masmorra #{did}"
        
    dtype = drow.get("Type", "1")
    type_label = dungeon_type_labels.get(dtype, f"Instância Tipo {dtype}")
    
    req_lvl = drow.get("RestrictedLevel", "1")
    rec_lvl = drow.get("RecommendedLevel", req_lvl)
    
    # Pick matching dungeon artwork
    matched_dimg = default_dungeon_img
    if dtype == "8" and "infinitedungeon_01.png" in dungeon_pngs:
        matched_dimg = "infinitedungeon_01.png"
    elif dtype == "3" and "elitedungeon01.png" in dungeon_pngs:
        matched_dimg = "elitedungeon01.png"
    elif dtype == "7" and "bloodlinedungeon_bg_01.png" in dungeon_pngs:
        matched_dimg = "bloodlinedungeon_bg_01.png"
    elif dtype == "4" and "clandefence01.png" in dungeon_pngs:
        matched_dimg = "clandefence01.png"
    elif "bloodruins.png" in dungeon_pngs:
        matched_dimg = "bloodruins.png"

    dungeons_catalog.append({
        "id": did,
        "name": name,
        "description": desc if desc else f"Instância de combate com desafios de monstros e chefes de elite ({type_label}).",
        "type_code": dtype,
        "type_name": type_label,
        "bg_img": f"assets/dungeons/{matched_dimg}",
        "req_level": int(req_lvl) if req_lvl.isdigit() else 1,
        "rec_level": int(rec_lvl) if rec_lvl.isdigit() else 1,
        "reward_exp": drow.get("RewardExp", "Varia conforme pontuação"),
        "max_clear_grade": "Grau 6 (SS) com bônus de itens lendários"
    })

dungeons_catalog.sort(key=lambda x: (x["type_code"], x["req_level"]))
with open(os.path.join(OUT_DIR, "dungeons.json"), "w", encoding="utf-8") as f:
    json.dump(dungeons_catalog, f, indent=2, ensure_ascii=False)

# ==========================================
# 6. ITEMS & GEAR (WITH REAL ICONS)
# ==========================================
print("Processing Items & Gear with official game icons...")

# Category mappings based on EItemType enum from libUnreal.so
POTION_TYPES = {"5", "26", "48", "79", "80", "81", "36", "37", "38"}

# Build Item to Codex Collections mapping
CODEX_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/codex")
item_collections_map = defaultdict(list)
codex_collections_raw = []

TAB_LABELS = {
    1: "Equipamentos & Armas",
    2: "Relíquias & Estátuas",
    3: "Diários & Manuscritos",
    4: "Eventos & Especiais",
    5: "Registros de Reide"
}
RARITY_LABELS = {
    0: "Comum",
    1: "Incomum",
    2: "Raro",
    3: "Heroico",
    4: "Lendário",
    5: "Mítico"
}

codex_csv_path = os.path.join(CODEX_REPORTS_DIR, "colecoes_itens_completas.csv")
if os.path.exists(codex_csv_path):
    with open(codex_csv_path, "r", encoding="utf-8-sig") as f:
        codex_collections_raw = list(csv.DictReader(f))
    for crow in codex_collections_raw:
        cid = crow["Id"]
        cname = crow["nome_pt"]
        tab_id = int(crow["CollectionTabId"])
        t_label = TAB_LABELS.get(tab_id, f"Aba {tab_id}")
        reqs_data = json.loads(crow["requisitos_json"])
        for q in reqs_data:
            q_iid = q["CollectParam"]
            item_collections_map[q_iid].append({
                "id": cid,
                "name": cname,
                "ench": int(q.get("EnchantLevel", 0) or 0),
                "qty": int(q.get("Count", 1) or 1),
                "tab": t_label
            })

# Build Item Droppers mapping using npc_to_boss_map
item_droppers_map = defaultdict(list)
for iid, dlist in item_droppers_raw.items():
    seen_bosses = set()
    dropper_entries = []
    for dr in dlist:
        nid = dr["npc_id"]
        boss = npc_to_boss_map.get(nid)
        boss_id = boss["id"] if boss else nid
        if boss_id in seen_bosses:
            continue
        seen_bosses.add(boss_id)
        b_name = boss["name"] if boss else dr["npc_name"]
        b_grade = boss["grade_name"] if boss else ("Elite" if dr["npc_grade"] == "1" else "Monstro Comum")
        b_grade_code = boss["grade_code"] if boss else dr["npc_grade"]
        b_lvl = dr["npc_level"]
        b_world = boss["world_map"] if boss else ""
        qmin = dr["qty_min"]
        qmax = dr["qty_max"]
        qty_str = f"{qmin}~{qmax}" if qmin != qmax else qmin
        dropper_entries.append({
            "id": boss_id,
            "name": b_name,
            "lvl": b_lvl,
            "grade": b_grade,
            "grade_code": b_grade_code,
            "world": b_world,
            "qty": qty_str
        })
    dropper_entries.sort(key=lambda x: (int(x["lvl"]) if str(x["lvl"]).isdigit() else 0), reverse=True)
    item_droppers_map[iid] = dropper_entries[:25]

items_by_cat = defaultdict(list)
all_processed_items = {}

# Pre-gather recipe materials from receitas.csv to tag pure crafting materials
recipe_mat_ids = set()
receitas_path_preview = os.path.join(BASE_DIR, "analysis/reports/jogo/receitas.csv")
if os.path.exists(receitas_path_preview):
    with open(receitas_path_preview, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            mats = json.loads(r['materiais_json']) if r.get('materiais_json') else []
            for m in mats:
                p = m.get('CostParam')
                if p and p != 'Gold':
                    recipe_mat_ids.add(p)

for iid, irow in item_raw.items():
    iname_row = item_names.get(iid)
    if not iname_row:
        continue
    name = iname_row.get("Name", "").strip()
    desc = iname_row.get("Desc", "").strip()
    
    if not name or (("2025-" in name or "2026-" in name) and iid not in all_linked_book_ids):
        continue
    
    itype = irow.get("Type", "")
    tier = irow.get("Tier", "1")
    rarity = irow.get("Rarity", "102")
    raw_img = irow.get("Img", "").strip()
    
    # Categorization and clean title
    if itype == "1":
        if any(k in raw_img.lower() for k in ["relic", "burial", "objet"]) or any(k in name.lower() for k in ["relíquia", "fúnebre"]):
            cat = "relic"
            type_label = "Relíquia & Equipamento Fúnebre"
        else:
            cat = "1"
            type_label = "Arma & Equipamento"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif itype == "31" or iid in all_linked_book_ids:
        cat = "31"
        type_label = "Livro de Habilidade" if itype == "31" else "Item de Aprendizado / Emblema"
        if ("2025-" in name or "2026-" in name) and "<SkillEffect>" in desc:
            m = re.search(r'<SkillEffect>(Livro de Habilidade:[^<]+)</>', desc)
            clean_name = m.group(1).strip() if m else re.sub(r'\{[^}]+\}', '', name).strip()
        else:
            clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
    elif itype in POTION_TYPES:
        cat = "potion"
        type_label = "Poção & Consumível"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif itype == "70":
        cat = "70"
        type_label = "Carta de Habilidade"
        card = skill_card_raw.get(iid)
        if card:
            lvl = card.get("SkillLevel", "1")
            clean_name = name.replace("{ReplaceString1}", f"Nv. {lvl}").strip()
            sid = card.get("SkillId")
            sname = skill_names.get(sid, {}).get("Name", "")
            sdesc = skill_names.get(sid, {}).get("Description", "")
            clean_desc = f"Carta de Habilidade para {sname} (Nível {lvl}). {sdesc}".strip()
        else:
            clean_name = re.sub(r'\{[^}]+\}', 'Nv. 1', name).strip()
            clean_desc = "Carta mística de aprimoramento de habilidade."
    elif itype in ["32", "42"] or "sephira" in raw_img.lower() or "sefira" in name.lower():
        cat = "32"
        type_label = "Sefira Mística"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif any(k in raw_img.lower() for k in ["burial", "objet", "relic"]) or any(k in name.lower() for k in ["relíquia", "sepultamento", "fúnebre"]):
        cat = "relic"
        type_label = "Relíquia & Sepultamento"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif itype in ["4", "25"] or "itembox" in raw_img.lower() or "baú" in name.lower():
        cat = "4"
        type_label = "Baú de Tesouro"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif itype in ["33", "34", "35"] or any(k in raw_img.lower() for k in ["artifactenchantmaterial", "enchantmaterial"]) or any(k in name.lower() for k in ["pedra de aprimoramento", "material de aprimoramento"]):
        cat = "materials"
        type_label = "Material de Aprimoramento"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif (iid in recipe_mat_ids and itype not in ['1', '2', '4', '25', '26', '31', '32', '33', '34', '35', '42', '53', '54', '70', '75', '8', '9']) \
         or 'materials_craftmaterial' in raw_img.lower() \
         or (itype == '0' and any(k in name.lower() for k in ['fragmento de arma', 'fragmento de armadura', 'fragmento de acessório', 'cristal cinzento', 'peridoto', 'safira gélida', 'manual de arma', 'manual de armadura', 'manual de acessório', 'página do manual', 'página do livro de habilidade', 'indícios de grandeza', 'energia mágica lazúli', 'energia mágica eterna', 'diagrama de criação'])):
        cat = "crafting_materials"
        type_label = "Material de Criação & Forja"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif itype in ["2", "54"] or any(k in raw_img.lower() for k in ["costume", "seal"]) or any(k in name.lower() for k in ["traje", "chapéu", "medalha", "selo"]):
        cat = "costumes"
        type_label = "Traje, Cosmético & Selo"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    elif iid in dropped_item_ids:
        cat = "drops"
        type_label = "Drop de Monstro / Campo"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    else:
        continue

    if len(clean_name) < 2:
        continue

    # Image matching
    raw_img = irow.get("Img", "").strip()
    clean_img_file = raw_img.replace("IMG_", "").replace("TEX_", "").lower() + ".png"
    
    item_img = ""
    if clean_img_file in item_pngs:
        item_img = f"assets/items/{clean_img_file}"
    elif cat == "materials":
        for m in ["materials_artifactenchantmaterial_04.png", "materials_artifactenchantmaterial_01.png", "weaponenchantmaterial_01.png"]:
            if m in item_pngs:
                item_img = f"assets/items/{m}"
                break
    elif cat == "crafting_materials":
        for cm in ["materials_craftmaterial_01.png", "materials_craftmaterial_02.png", "flat_itemcraft.png"]:
            if cm in item_pngs:
                item_img = f"assets/items/{cm}"
                break
    elif cat == "costumes":
        for c in ["costumeitemicon_alle011armor.png", "costumeitemicon_alle011hair.png", "costumeicon_alle011armor.png"]:
            if c in item_pngs:
                item_img = f"assets/items/{c}"
                break
    elif cat == "4":
        for b in ["itembox_fieldboss_01.png", "itembox_equipment_01.png", "itembox_enchantscroll_01.png", "itembox_burialgoods_01.png"]:
            if b in item_pngs:
                item_img = f"assets/items/{b}"
                break
    elif cat == "32":
        for s in ["sephira_01.png", "flat_sephira.png", "sephira_11.png"]:
            if s in item_pngs:
                item_img = f"assets/items/{s}"
                break
    elif cat == "relic":
        for r in ["flat_relic.png", "itembox_relic_01.png", "itembox_burialgoods_01.png", "itembox_objetitem_01.png"]:
            if r in item_pngs:
                item_img = f"assets/items/{r}"
                break
    elif cat == "potion":
        for p in ["hppotion_01.png", "attackpowerpotion_01.png", "potion_event_01.png"]:
            if p in item_pngs:
                item_img = f"assets/items/{p}"
                break
    elif cat == "70":
        for c in ["flat_skillcard.png", "skill_active_waveofforce.png"]:
            if c in item_pngs:
                item_img = f"assets/items/{c}"
                break
    elif cat == "1":
        for w in ["weapon_bloodsword_common_01.png", "armor_armor_common_01.png"]:
            if w in item_pngs:
                item_img = f"assets/items/{w}"
                break
    elif cat == "31":
        for b in ["skillbook_allclass.png", "skillbook_darkmage.png", "skillbook_swordman.png"]:
            if b in item_pngs:
                item_img = f"assets/items/{b}"
                break
    elif cat == "drops":
        for d_icon in ["flat_relic.png", "flat_itemcraft.png", "asset_gold.png"]:
            if d_icon in item_pngs:
                item_img = f"assets/items/{d_icon}"
                break

    if not item_img:
        item_img = "assets/logo.png"

    r_code = int(rarity) if str(rarity).isdigit() else 0
    r_info = get_rarity_info(r_code)

    item_dict = {
        "id": iid,
        "name": clean_name,
        "desc": clean_desc if clean_desc else "Item de uso e progressão vampírica.",
        "type_code": itype,
        "category": cat,
        "type_name": type_label,
        "icon_img": item_img,
        "tier": tier if tier else "1",
        "rarity": r_code,
        "rarity_name": r_info["name"],
        "rarity_color": r_info["color"],
        "rarity_highlight": r_info["highlight"],
        "rarity_badge_class": r_info["badge_class"],
        "max_enchant": "+15 (Encantamento Seguro até +5, Risco de Falha/Degradação acima)",
        "usable": irow.get("Usable", "0") == "1",
        "weight": irow.get("Weight", "0"),
        "droppers": item_droppers_map.get(iid, []),
        "collections": item_collections_map.get(iid, [])[:15]
    }
    all_processed_items[iid] = item_dict
    items_by_cat[cat].append(item_dict)

# Curate a balanced collection across ALL categories with real extracted icons prioritized:
curated_items = []

# 1. All Potions & Consumables (56 items)
curated_items.extend(items_by_cat["potion"])

# 2. Skill Cards (120 cards with skill levels)
curated_items.extend(items_by_cat["70"][:120])

# 3. Weapons & Gear (120 items)
curated_items.extend(items_by_cat["1"][:120])

# 4. Todos os 425 Livros de Habilidade e Itens de Aprendizado Catalogados (100% de cobertura)
curated_items.extend(items_by_cat["31"])
for bid in all_linked_book_ids:
    if bid in all_processed_items and all_processed_items[bid] not in curated_items:
        curated_items.append(all_processed_items[bid])

# 5. Chests & Baús (80 items with authentic icons)
curated_items.extend(items_by_cat["4"][:80])

# 6. Sephiras Místicas (72 items - all core Sephiras)
curated_items.extend(items_by_cat["32"][:72])

# 7. Relíquias & Equipamento Fúnebre (60 items)
curated_items.extend(items_by_cat["relic"][:60])

# 8. Materiais de Aprimoramento e Forja
curated_items.extend(items_by_cat["materials"])

# 9. Materiais de Criação & Forja (Pure Crafting Materials)
curated_items.extend(items_by_cat["crafting_materials"])

# 10. Trajes, Cosméticos & Medalhas Comemorativas
curated_items.extend(items_by_cat["costumes"])

# 10. Todos os Itens com Drop Confirmado de Monstros (Garantia de 100% de cobertura e cross-linking)
curated_ids = set(it["id"] for it in curated_items)
for iid in dropped_item_ids:
    if iid in all_processed_items and iid not in curated_ids:
        curated_items.append(all_processed_items[iid])
        curated_ids.add(iid)

# 11. Materiais de Pesquisa Mágica (Trindade, Catalisador e Orbes/Esferas)
RESEARCH_MATERIAL_IDS = {'100000000', '100000359', '100000501', '100000502', '100000503', '100000504', '100000505', '100001501', '100001502', '100001503', '100001504', '100004023'}
for mid in RESEARCH_MATERIAL_IDS:
    if mid in all_processed_items and mid not in curated_ids:
        curated_items.append(all_processed_items[mid])
        curated_ids.add(mid)

# 12. Kits de Restauração de Retratos
PORTRAIT_MATERIAL_IDS = {'140015010', '140018010', '140010010', '140004010', '140003010', '140011010', '140017010', '140010011', '140002010', '140019010', '140014010', '140007010', '140009010', '140010012', '140006010', '140016010', '140008010', '140013010', '140005010', '140012010'}
for pid in PORTRAIT_MATERIAL_IDS:
    if pid in all_processed_items and pid not in curated_ids:
        curated_items.append(all_processed_items[pid])
        curated_ids.add(pid)

# 13. Materiais de Aprimoramento de Artefatos
ARTIFACT_MATERIAL_IDS = {'60000000', '110000613', '110000776', '60000001', '60000014', '60000015'}
for aid in ARTIFACT_MATERIAL_IDS:
    if aid in all_processed_items and aid not in curated_ids:
        curated_items.append(all_processed_items[aid])
        curated_ids.add(aid)

with open(os.path.join(OUT_DIR, "items.json"), "w", encoding="utf-8") as f:
    json.dump(curated_items, f, indent=2, ensure_ascii=False)

# ==========================================
# 7. QUESTS & MISSIONS (1.353 Quests, 5.944 Tasks)
# ==========================================
print("Processing Quests and Tasks from analysis/reports/jogo/missoes.csv...")
JOGO_DIR = os.path.join(BASE_DIR, "analysis/reports/jogo")
type_pt_map = {
    'Scenario': 'Campanha Principal',
    'Daily': 'Missão Diária',
    'Guide': 'Guia / Tutorial',
    'Sub': 'Missão Secundária',
    'Wanted': 'Caçada / Procurado',
    'GuildDefense': 'Defesa de Guilda',
    'Dungeon': 'Masmorra & Desafio',
    'Bloodline': 'Linhagem de Sangue',
    'Item': 'Missão de Item'
}

quests_catalog = []
missoes_path = os.path.join(JOGO_DIR, "missoes.csv")
if os.path.exists(missoes_path):
    with open(missoes_path, encoding='utf-8-sig') as f:
        raw_quests = list(csv.DictReader(f))
    for q in raw_quests:
        qid = q['Id']
        name = q.get('pt_nomes', '').strip()
        if not name or "2025-" in name or "2026-" in name:
            name = f"Missão #{qid}"
        
        qtype = q.get('tipo_nome_enum', 'Scenario').strip()
        type_pt = type_pt_map.get(qtype, qtype)
        req_lv = q.get('RequireCharacterLv', '').strip() or "1"
        tasks_count = q.get('tarefas_count', '').strip() or "1"
        rewards_raw = json.loads(q['recompensas_por_grupo_json']) if q.get('recompensas_por_grupo_json') else []
        
        quests_catalog.append({
            "id": qid,
            "name": name,
            "type": qtype,
            "type_pt": type_pt,
            "req_level": int(req_lv) if req_lv.isdigit() else 1,
            "tasks_count": int(tasks_count) if tasks_count.isdigit() else 1,
            "rewards_count": len(rewards_raw),
            "has_instance": q.get('StartRunInInstance') == '1',
            "pre_quest": q.get('PreQuestId') if q.get('PreQuestId') != '0' else None
        })
    with open(os.path.join(OUT_DIR, "quests.json"), "w", encoding="utf-8") as f:
        json.dump(quests_catalog, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Processed {len(quests_catalog)} quests.")

# ==========================================
# 8. CRAFTING & FORGE (602 Recipes, 38 Orphan Materials)
# ==========================================
print("Processing Crafting Recipes from analysis/reports/jogo/receitas.csv...")
craft_tab_names = {}
craft_tab_file = os.path.join(L10N_DIR, "ItemCraftTab_Name.csv")
if os.path.exists(craft_tab_file):
    with open(craft_tab_file, encoding='utf-8-sig') as f:
        craft_tab_names = {r['Id']: r['Name'] for r in csv.DictReader(f)}

crafting_catalog = []
receitas_path = os.path.join(JOGO_DIR, "receitas.csv")
if os.path.exists(receitas_path):
    with open(receitas_path, encoding='utf-8-sig') as f:
        raw_recipes = list(csv.DictReader(f))
    for r in raw_recipes:
        rid = r['Id']
        tab_id = r.get('CraftTabInfoId', '')
        tab_name = craft_tab_names.get(tab_id, f"Aba #{tab_id}")
        
        mats = json.loads(r['materiais_json']) if r.get('materiais_json') else []
        succ_list = json.loads(r['SuccessRewardGroupId_registros_json']) if r.get('SuccessRewardGroupId_registros_json') else []
        
        target_name = "Item Forjado"
        target_param = ""
        target_rarity = 0
        if succ_list:
            target_name = succ_list[0].get('item_nome_pt', '').strip() or f"Item #{succ_list[0].get('Param')}"
            target_param = succ_list[0].get('Param', '')

        # Target Icon & Rarity matching directly from Item.csv
        target_row = item_raw.get(target_param, {})
        rep_str = target_row.get("ReplaceString1", "").strip()
        if rep_str:
            target_name = target_name.replace("{ReplaceString1}", rep_str).strip()

        raw_rarity = target_row.get("Rarity", "").strip()
        if not raw_rarity and succ_list:
            raw_rarity = succ_list[0].get('RewardRank', '0')
        target_rarity = int(raw_rarity) if raw_rarity.isdigit() else 0
        rarity_info = get_rarity_info(target_rarity)

        target_img_raw = target_row.get("Img", "").strip()
        target_clean_img = target_img_raw.replace("IMG_", "").replace("TEX_", "").lower() + ".png"
        if target_clean_img in item_pngs:
            icon = f"assets/items/{target_clean_img}"
        else:
            icon = "assets/items/flat_itemcraft.png"

        clean_mats = []
        for m in mats:
            mname = m.get('item_nome_pt', '').strip()
            param = m.get('CostParam', '')
            if not mname and param == 'Gold':
                mname = 'Ouro (Gold)'
            elif not mname:
                mname = f"Material #{param}"

            # Material icon matching
            mat_icon = "assets/items/flat_itemcraft.png"
            if param == 'Gold':
                mat_icon = "assets/items/asset_gold.png"
            elif param in item_raw:
                m_raw = item_raw[param].get("Img", "").strip()
                m_clean = m_raw.replace("IMG_", "").replace("TEX_", "").lower() + ".png"
                if m_clean in item_pngs:
                    mat_icon = f"assets/items/{m_clean}"

            mat_row = item_raw.get(param, {})
            mat_raw_rarity = mat_row.get("Rarity", "").strip()
            mat_rarity_num = int(mat_raw_rarity) if mat_raw_rarity.isdigit() else 0
            mat_rarity_info = get_rarity_info(mat_rarity_num)
            mat_desc = item_names.get(param, {}).get("Desc", "").strip()

            clean_mats.append({
                "id": param,
                "name": mname,
                "amount": m.get('CostValue', '1'),
                "type": m.get('custo_tipo_nome_enum', 'Item'),
                "icon": mat_icon,
                "rarity": mat_rarity_num,
                "rarity_name": mat_rarity_info["name"],
                "rarity_color": mat_rarity_info["color"],
                "desc": mat_desc
            })

        succ_rate = (int(r.get('SuccessRate') or 0)) // 10000
        big_rate = (int(r.get('BigSuccessRate') or 0)) // 10000
        
        tab_num = int(tab_id) if tab_id.isdigit() else 0
        if tab_num in range(101, 106):
            recipe_category = "weapons"
            cat_label = "Armas de Classe"
        elif tab_num in range(601, 606):
            recipe_category = "books"
            cat_label = "Livros de Habilidade"
        elif tab_num in range(201, 205):
            recipe_category = "armors"
            cat_label = "Armaduras & Peças"
        elif tab_num in range(301, 308):
            recipe_category = "accessories"
            cat_label = "Acessórios & Joias"
        elif tab_num in [401, 402, 403]:
            recipe_category = "materials"
            cat_label = "Materiais & Forja"
        elif tab_num in [501]:
            recipe_category = "consumables"
            cat_label = "Consumíveis & Poções"
        else:
            recipe_category = "events"
            cat_label = "Eventos / Emblemas"

        # Skill Book enrichment
        sk_id = None
        sk_name = None
        sk_desc = None
        sk_effect = None
        it_desc = None
        class_name = None
        if recipe_category == "books":
            class_name = tab_name
            eff_param = target_row.get("EffectParams", "").strip()
            sk = skill_names.get(eff_param, {})
            sk_name = sk.get("Name", "").strip() or None
            sk_id = eff_param or None
            sk_desc = re.sub(r'<[^>]+>', '', sk.get("Description", "")).strip() or None
            sk_effect = re.sub(r'<[^>]+>', '', sk.get("EffectDescription", "")).strip() or None
            it_desc = re.sub(r'<[^>]+>', '', item_names.get(target_param, {}).get("Desc", "")).strip() or None

        raw_tier = target_row.get("Tier", "").strip()
        tier_val = int(raw_tier) if raw_tier.isdigit() else None

        crafting_catalog.append({
            "id": rid,
            "target_name": target_name,
            "target_item_id": target_param,
            "tier": tier_val,
            "tier_label": f"T{tier_val}" if tier_val else None,
            "rarity": target_rarity,
            "rarity_name": rarity_info["name"],
            "rarity_color": rarity_info["color"],
            "rarity_highlight": rarity_info["highlight"],
            "rarity_badge_class": rarity_info["badge_class"],
            "tab_id": tab_id,
            "tab_name": tab_name,
            "category": recipe_category,
            "category_label": cat_label,
            "class_name": class_name,
            "skill_id": sk_id,
            "skill_name": sk_name,
            "skill_desc": sk_desc,
            "skill_effect": sk_effect,
            "item_desc": it_desc,
            "success_rate": f"{succ_rate}%",
            "big_success_rate": f"{big_rate}%",
            "materials": clean_mats,
            "tradeable_on_big": big_rate > 0,
            "icon_img": icon
        })
    with open(os.path.join(OUT_DIR, "crafting.json"), "w", encoding="utf-8") as f:
        json.dump(crafting_catalog, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Processed {len(crafting_catalog)} crafting recipes.")


# ==========================================
# 9. GAME MODES (196+ Instances across 8 Disciplines)
# ==========================================
print("Processing Game Modes catalog...")
modes_catalog = [
    {
        "id": "party_dungeons",
        "category": "pve_coop",
        "category_label": "Cooperativo em Grupo",
        "title": "Masmorras em Grupo (Party Dungeons)",
        "subtitle": "77 instâncias cooperativas para grupos de até 5 jogadores",
        "icon_img": "assets/dungeons/dungeon_vampiregraveyard_01.png",
        "instances_count": 77,
        "level_range": "Nv. 20 - Nv. 84+",
        "capacity": "4 a 5 Jogadores (Grupo)",
        "cost": "Bilhete de Masmorra em Grupo (PartyDungeonTicket) ou Gold",
        "reset_type": "Diário / Semanal",
        "description": "Masmorras desafiadoras projetadas para esquadrões coordenados com divisão rígida de funções (Tanque, DPS Burst, DPS Sustentado e Suporte de Sangue). Cada masmorra culmina em um chefe com múltiplas fases de mecânica que pune posicionamento inadequado.",
        "key_locations": [
            "Vila Lamentosa (Lament Village)",
            "Santuário Profanado (Defiled Sanctuary)",
            "Trono da Serpente (Serpent Throne)",
            "Monastério do Silêncio (Silent Monastery)"
        ],
        "rewards": [
            "Equipamentos Raros e Heroicos de Nível Alto",
            "Livros de Habilidade de Classe e Grimórios",
            "Materiais Nobres de Forja (Fragmentos de Arma/Armadura)",
            "Pontos de Conquista e Moedas de Honra"
        ],
        "badge": "Cooperativo Hardcore"
    },
    {
        "id": "infinite_dungeons",
        "category": "pve_solo",
        "category_label": "Progressão Solo / Torre",
        "title": "Masmorras Infinitas & Torre da Ascensão",
        "subtitle": "50 andares de escalada solo com dificuldade exponencial",
        "icon_img": "assets/dungeons/dungeon_bloodcave_01.png",
        "instances_count": 50,
        "level_range": "Nv. 30 - Nv. 90+",
        "capacity": "1 Jogador (Solo)",
        "cost": "Bilhete de Temporada Infinita (InfiniteDungeonSeasonTicket)",
        "reset_type": "Temporada Mensal (InfiniteDungeonSeason)",
        "description": "O teste supremo de habilidade individual. Cada andar apresenta hordas de elite sob efeito de modificadores de combate que limitam cura ou amplificam dano elemental. Atingir os andares mais altos garante títulos exclusivos e posições no ranking sazonal com distribuição massiva de Diamantes.",
        "key_locations": [
            "Abismo da Criação (Creation Abyss)",
            "Legado Desbotado (Faded Legacy)",
            "Oficina Antiga (Ancient Workshop)",
            "Origem da Evolução (Origin of Evolution)"
        ],
        "rewards": [
            "Cristais Cinzentos Superiores e Trindades",
            "Moedas de Temporada para Loja da Torre",
            "Sefiras Místicas de Grau Épico",
            "Diamantes e Pontos de Realização de Temporada"
        ],
        "badge": "Desafio Sazonal"
    },
    {
        "id": "cross_server_dungeons",
        "category": "cross_server",
        "category_label": "Inter-Servidor (Cross-Server)",
        "title": "Masmorras Inter-Servidores (Cross-Server Hubs)",
        "subtitle": "30 zonas massivas com limite de até 200 jogadores por servidor conectado",
        "icon_img": "assets/dungeons/dungeon_vampirecastle_01.png",
        "instances_count": 30,
        "level_range": "Nv. 55 - Nv. 100",
        "capacity": "Até 200 Jogadores por Servidor (Multisservidor)",
        "cost": "Bilhete de Grupo de Servidores (ServerGroupDungeonTicket)",
        "reset_type": "Janelas Horárias Específicas / Rotação",
        "description": "Campos de batalha e masmorras colossais compartilhadas entre grupos de servidores de uma mesma região (ServerGroup). Reúne chefes de campo de nível Mítico e áreas de PvP aberto onde guildas de diferentes servidores duelam pelo controle de corredores e espólios raros.",
        "key_locations": [
            "Berço da Radiança (Cradle of Radiance)",
            "Salão da Graça Sagrada (Hall of Holy Grace)",
            "Zona Proibida da Radiância (Forbidden Zone)",
            "Terra da Eternidade (Land of Eternity)"
        ],
        "rewards": [
            "Equipamentos de Linhagem Mítica",
            "Selo da Graça Sagrada e Selo da Radiância",
            "Núcleos de Matriz Cósmica e Joias Raras",
            "Emblemas de Mudança de Classe"
        ],
        "badge": "Cross-Server Massivo"
    },
    {
        "id": "bloodline_dungeons",
        "category": "lore_progression",
        "category_label": "Linhagem & Tradição",
        "title": "Masmorras da Linhagem Vampírica (Bloodline)",
        "subtitle": "12 rituais arcanos narrativos dos 10 capítulos ancestrais",
        "icon_img": "assets/items/flat_relic.png",
        "instances_count": 12,
        "level_range": "Nv. 15 - Nv. 80",
        "capacity": "1 Jogador (Instanciado Cinematográfico)",
        "cost": "Progresso na Campanha da Linhagem (Bloodline Questline)",
        "reset_type": "Único / Replay de Domínio",
        "description": "Instâncias rituais onde o vampiro revive os confrontos decisivos da história de Krvna. As lutas ocorrem em cenários cinemáticos isolados (BeforeStartInstance / StartRunInInstance) e desbloqueiam novos ramos na Árvore da Vida e despertares passivos da linhagem.",
        "key_locations": [
            "Cerimônia de Sucessão de Sangue",
            "Guerra nas Sombras & Noite da Escolha",
            "Batalha Histórica de Krvna",
            "Santuário Ancestral de Bezdan"
        ],
        "rewards": [
            "Desbloqueio de Nós na Árvore da Vida (LifeTree Matrix)",
            "Cartas de Tumba e Aprimoramento de Caixão",
            "Habilidades Passivas Hereditárias",
            "Pontos de Sangue Permanentes (Max BloodPoint)"
        ],
        "badge": "Progressão de Lore"
    },
    {
        "id": "guild_defense",
        "category": "guild",
        "category_label": "Defesa de Guilda",
        "title": "Defesa de Relíquia da Guilda (Guild Defense)",
        "subtitle": "Modo Tower Defense cooperativo contra 5+ ondas de invasores",
        "icon_img": "assets/pvp/flat_guildconquest.png",
        "instances_count": 1,
        "level_range": "Guilda Nv. 3+ / Jogadores Nv. 40+",
        "capacity": "Todos os membros da guilda (Até 50 Jogadores)",
        "cost": "Sem custo de bilhete (Agendado pela Liderança)",
        "reset_type": "Semanal",
        "description": "A guilda inteira se reúne no Santuário para proteger a Relíquia Central contra 5 ondas sequenciais de monstros implacáveis. Cada membro pode ativar Totens de Operação (OperationGroup) para invocar barreiras defensivas ou buffs aleatórios (RandomEffectGroup). Se a quantidade de monstros vivos exceder 100, é aplicada uma penalidade severa à guilda.",
        "key_locations": [
            "Santuário da Relíquia da Guilda (Dungeon ID 71001)"
        ],
        "rewards": [
            "Pontos de Experiência de Guardião da Guilda (GuildGuardianExp)",
            "Moedas de Contribuição de Guilda e Fundos de Clã",
            "Baús de Recompensa Pessoal de Onda (PersonalRewardGroup)",
            "Baús Coletivos do Tesouro da Guilda"
        ],
        "badge": "Cooperativo de Clã"
    },
    {
        "id": "guild_crypt",
        "category": "guild",
        "category_label": "Cripta Subterrânea",
        "title": "Cripta da Guilda (Guild Crypt)",
        "subtitle": "Instalação subterrânea com 4 sistemas autônomos de progressão",
        "icon_img": "assets/items/flat_itemcraft.png",
        "instances_count": 4,
        "level_range": "Guilda Nv. 2+",
        "capacity": "Membros da Guilda",
        "cost": "Fundos e Essências de Sangue da Guilda",
        "reset_type": "Contínuo / Invocações Diárias",
        "description": "A base subterrânea secreta do clã. Composta por 4 alas operacionais mapeadas em GuildCrypt.csv: 1) Invocação de Chefes de Sangue (MI_Crypt_Summon), 2) Caçada de Cripta (MI_Crypt_BossHunt), 3) Mercador Errante de Relíquias (MI_Crypt_WandererTrade) e 4) Bancada de Encantamento Coletivo (MI_Crypt_Enchant).",
        "key_locations": [
            "Cripta dos Ancestrais - Nível 1 a 4"
        ],
        "rewards": [
            "Essências Raras de Troca com Mercadores Errantes",
            "Encantamentos Compartilhados de Clã",
            "Drops de Chefes Invocados em Grupo",
            "Subida de Nível do Guardião da Guilda"
        ],
        "badge": "Infraestrutura de Clã"
    },
    {
        "id": "elite_boss_zones",
        "category": "world_pve",
        "category_label": "Chefes de Campo & Raides",
        "title": "Zonas de Chefes de Elite (Elite Boss Zones)",
        "subtitle": "10 zonas abertas com chefes colossais de spawn programado",
        "icon_img": "assets/dungeons/dungeon_vampiregraveyard_02.png",
        "instances_count": 10,
        "level_range": "Nv. 45 - Nv. 90",
        "capacity": "Raides de até 50 Jogadores / Aberto ao Mundo",
        "cost": "Acesso Livre (Respawn Cronometrado)",
        "reset_type": "Horários Fixos de Aparição (NpcSpawnDetail)",
        "description": "Grandes batalhas de campo aberto onde chefes de classificação Elite e Chefe Mundial surgem em horários específicos. Exigem grupos com líder de raide habilitado (Ready Check Duration: 20s). As recompensas são fracionadas entre maior dano causado, último golpe e participação geral (EliteBossZoneParticipantsReward).",
        "key_locations": [
            "Vale Naricanje (Naricanje Valley)",
            "Parque Temático da Meia-Noite (Midnight Theme Park)",
            "Floresta da Manhã Serena",
            "Jardim Proibido"
        ],
        "rewards": [
            "Baús de Chefe de Campo (itembox_fieldboss_01.png)",
            "Equipamentos de Grau Heroico e Lendário",
            "Receitas Épicas de Forja e Minérios Raros",
            "Emblemas de Desafio e Moedas de Honra"
        ],
        "badge": "Mundo Aberto"
    },
    {
        "id": "support_mode",
        "category": "automation",
        "category_label": "Automação & Autoplay",
        "title": "Modo de Suporte & Farm Offline (SupportMode)",
        "subtitle": "Sistema inteligente de continuidade de jogo desconectado",
        "icon_img": "assets/items/flat_itemcraft2.png",
        "instances_count": 1,
        "level_range": "Nv. 1+",
        "capacity": "Individual (Offline)",
        "cost": "Gratuito (Temporizador Recarregável)",
        "reset_type": "Diário (Tempo de Jogo Offline)",
        "description": "Permite ao vampiro continuar acumulando experiência, ouro e materiais mesmo após encerrar o aplicativo no Android ou PC. O sistema monitora o estoque de poções (AutoMaintain.HpPotionMinCount: 100), realiza compras automáticas na cidade e executa a limpeza expressa de missões diárias pendentes (DailyQuestQuickClear).",
        "key_locations": [
            "Qualquer Campo de Caça Habilitado para Suporte"
        ],
        "rewards": [
            "Experiência e Ouro Contínuos durante o Deslogue",
            "Coleta Automática de Materiais de Criação",
            "Conclusão Instantânea de Missões Diárias",
            "Conserva Poções e Recursos em Ciclo Seguro"
        ],
        "badge": "Qualidade de Vida"
    }
]

with open(os.path.join(OUT_DIR, "modes.json"), "w", encoding="utf-8") as f:
    json.dump(modes_catalog, f, indent=2, ensure_ascii=False)
print(f"  ✓ Processed {len(modes_catalog)} game mode categories.")

# ==========================================
# 10. PVP & WAR SYSTEMS (Arena 5v5, Conquest, World Tournament, PK Karma & Revenge Radar)
# ==========================================
print("Processing PvP and War systems...")
pvp_catalog = {
    "arena": {
        "title": "Arena de Sangue (Coliseu 5v5)",
        "subtitle": "Combate tático competitivo em arena fechada com regras sincronizadas",
        "format": "5 vs 5 (Equipe Vermelha vs Equipe Azul)",
        "duration": "300 Segundos (5 Minutos)",
        "target_score": "10 Abates (Primeira equipe a atingir vence)",
        "map_image": "assets/pvp/arena_guidemap_deathmatch.png",
        "map_name": "Ruínas Rubras de Sangue (Dungeon ID 90101)",
        "special_mechanic": "Spawn de Barreiras Mágicas e Relíquias Ativas (Skills #326001 e #326002)",
        "leagues": [
            {"name": "Fera (Beast)", "bp_req": "0 - 599.999 BP", "badge": "badge-gray", "desc": "Liga de entrada para novatos e testes de composição."},
            {"name": "Predador (Predator)", "bp_req": "600.000 - 899.999 BP", "badge": "badge-green", "desc": "Confrontos intermediários com exigência de sinergia básica."},
            {"name": "Soberano (Sovereign)", "bp_req": "900.000 - 1.199.999 BP", "badge": "badge-blue", "desc": "Combates ranqueados avançados com foco em controle de grupo (CC)."},
            {"name": "Imortal (Immortal)", "bp_req": "1.200.000 - 1.499.999 BP", "badge": "badge-gold", "desc": "Elite do servidor; erros de posicionamento são fatais."},
            {"name": "Mítico (Mythic)", "bp_req": "1.500.000+ BP", "badge": "badge-crimson", "desc": "O topo supremo; apenas os maiores campeões e lendas de clãs."}
        ],
        "traits": [
            {
                "id": "101",
                "name": "Defesa (Guardião)",
                "icon": "assets/pvp/trait_guardian.png",
                "skillset": "SkillSet #325101",
                "desc": "Aumenta a armadura física e mágica em 25%, gera escudo de sangue ao sofrer atordoamento e reduz dano em área (AoE) recebido por aliados próximos."
            },
            {
                "id": "102",
                "name": "Proteção (Bênção)",
                "icon": "assets/pvp/trait_blessing.png",
                "skillset": "SkillSet #325102",
                "desc": "Acelera a taxa de regeneração contínua de PV, dissipa lentidões e sangramentos, e concede aura de absorção para a linha de trás."
            },
            {
                "id": "103",
                "name": "Esmagamento (Crushing)",
                "icon": "assets/pvp/trait_crushing.png",
                "skillset": "SkillSet #325103",
                "desc": "Ignora 30% da resistência a dano crítico do alvo, quebra escudos de sangue instantaneamente e inflige penalidade severa de cura."
            },
            {
                "id": "104",
                "name": "Assassinato (Assassination)",
                "icon": "assets/pvp/trait_assassination.png",
                "skillset": "SkillSet #325104",
                "desc": "Amplifica o dano pelas costas (Back Attack) em 40%, concede bônus de velocidade de movimento e executa inimigos com menos de 25% de vida."
            }
        ]
    },
    "conquest": {
        "title": "Guerra de Conquista & Cerco de Guildas",
        "subtitle": "Conflito massivo semanal pelo controle territorial e soberania de clã",
        "schedule": "Todos os Sábados às 20h30 (Duração: 31 Minutos cronometrados)",
        "countdown": "10 Segundos de Preparação / 180s para Desocupação Pós-Guerra",
        "maps": [
            {
                "name": "Guerra de Ocupação (Occupation War)",
                "type": "Disputa de Altares & Zonas de Controle",
                "image": "assets/pvp/conquest_guidemap_occupation.png",
                "desc": "As guildas disputam 5 Altares de Sangue espalhados pela fortaleza. Cada altar controlado acumula pontos de ocupação por segundo. A destruição das Torres de Defesa abre caminhos para o Núcleo Central."
            },
            {
                "name": "Guerra de Raide (Raid War)",
                "type": "Assalto a Chefes & Fortificações",
                "image": "assets/pvp/conquest_guidemap_raid.png",
                "desc": "Modo de combate híbrido com chefes titânicos de cerco (ConquestBoss). Eliminar os mini-chefes e o chefe principal de conquista concede bônus multiplicadores massivos para a pontuação de território."
            }
        ],
        "tiers": [
            {"tier": "5", "name": "Tier 5 - Diamante", "points": "850+ Pontos", "badge": "badge-blue", "privilege": "Controle Máximo, Taxa de Leilão Reduzida, Título de Soberano."},
            {"tier": "4", "name": "Tier 4 - Platina", "points": "750 a 849 Pontos", "badge": "badge-gold", "privilege": "Acesso a Masmorras de Conquista Exclusivas e Loja de Clã Nv. 5."},
            {"tier": "3", "name": "Tier 3 - Ouro", "points": "650 a 749 Pontos", "badge": "badge-crimson", "privilege": "Baús de Recompensa Semanal e Emblemas de Ocupação."},
            {"tier": "2", "name": "Tier 2 - Prata", "points": "550 a 649 Pontos", "badge": "badge-gray", "privilege": "Fundos Expandidos e Bônus de EXP de Guilda."},
            {"tier": "1", "name": "Tier 1 - Bronze", "points": "0 a 549 Pontos", "badge": "badge-gray", "privilege": "Recompensas de Participação Básica de Batalha."}
        ]
    },
    "pk_system": {
        "title": "Sistema de PK Aberto & Notoriedade de Sangue",
        "subtitle": "Regras de combate em mundo aberto, penalidades de karma e radar de retaliação",
        "icon": "assets/pvp/flat_pvppenalty.png",
        "penalty_mark": "assets/pvp/pvppenalty_01.png",
        "penalty_levels": [
            {
                "level": "1",
                "points": "4.000 pts",
                "status": "Suspeito (PvpPenalty_01)",
                "effects": "Marca visual discreta sobre a cabeça. -5% em Ataque e Defesa. Guardas de capitais ficam em estado de alerta.",
                "color": "#f59e0b"
            },
            {
                "level": "2",
                "points": "7.500 pts",
                "status": "Hostil (PvpPenalty_02)",
                "effects": "Marca avermelhada pulsante. -10% em todos os atributos base. Proibido montar em veículos dentro de áreas seguras.",
                "color": "#f97316"
            },
            {
                "level": "3",
                "points": "10.000 pts",
                "status": "Criminoso (PvpPenalty_03)",
                "effects": "-20% de atributos de combate. Queda de EXP dobrada ao ser abatido. Perda de 50% de eficiência de poções de cura.",
                "color": "#ef4444"
            },
            {
                "level": "4",
                "points": "12.500 pts",
                "status": "Vilão Infame (PvpPenalty_04)",
                "effects": "-35% de atributos. Bloqueio absoluto de teleporte rápido e proibição de acessar leilão e correio de jogo.",
                "color": "#dc2626"
            },
            {
                "level": "5",
                "points": "15.000 pts",
                "status": "Demônio / Fora da Lei (PvpPenalty_05)",
                "effects": "-50% em combate total. Localização revelada no minimapa para todo o servidor. Qualquer jogador pode eliminá-lo sem acumular karma.",
                "color": "#991b1b"
            }
        ],
        "revenge_radar": {
            "title": "Radar de Vingança (AlertTarget / Revenge World)",
            "max_targets": "Até 50 Assassinos Monitorados",
            "radar_range": "3.000 Unidades de Distância no Mapa",
            "duration": "24 Horas de Rastreamento Ativo (86.400 segundos)",
            "refresh_rate": "Atualização de Posição a cada 10 Segundos",
            "desc": "Se você for eliminado por outro jogador em zona neutra ou de conflito, ele é incluído na sua lista de alvos de vingança. Ao se aproximar de você, um alerta sonoro e visual avisa sua presença, permitindo emboscadas e retaliação."
        },
        "pvp_stats": [
            {"stat": "AttackPowerPvp", "name": "Poder de Ataque PvP", "desc": "Aumenta diretamente o dano final causado a outros jogadores."},
            {"stat": "DamageReductionPvp", "name": "Redução de Dano PvP", "desc": "Diminui o dano sofrido por ataques diretos de vampiros rivais."},
            {"stat": "CriticalRatePvp", "name": "Taxa Crítica PvP", "desc": "Probabilidade de acerto crítico calculada independentemente do PvE."},
            {"stat": "CriticalResistanceRatePvp", "name": "Resistência Crítica PvP", "desc": "Reduz a chance de receber golpes críticos de inimigos."},
            {"stat": "DamageMultiplierPvp", "name": "Multiplicador de Dano PvP", "desc": "Amplifica o multiplicador de dano em caso de acerto crítico no PvP."},
            {"stat": "DamageReducerPvp", "name": "Atenuador de Dano PvP", "desc": "Reduz a gravidade dos golpes de alto impacto sofridos."},
            {"stat": "HitValuePvp", "name": "Precisão de Acerto PvP", "desc": "Contrarresta o valor de esquiva do adversário."},
            {"stat": "DodgeValuePvp", "name": "Esquiva PvP", "desc": "Aumenta a probabilidade de anular dano total de ataques normais."},
            {"stat": "IgnoreCriticalDamageMultiplierPvp", "name": "Ignorar Multiplicador Crítico", "desc": "Cancela bônus de dano de golpes letais sofridos."}
        ]
    },
    "world_tournament": {
        "title": "Torneio Mundial dos Vampiros (Vampir Tournament World)",
        "subtitle": "O campeonato de elite interservidores entre os maiores clãs do ecossistema",
        "format": "Torneio eliminatório em 5 rodadas (Round 0 a Round 4)",
        "schedule": "Sazonal (Fins de Temporada de Conquista)",
        "desc": "As guildas campeãs de cada servidor são transportadas para uma arena colossal de outro plano. Cada vitória distribui recompensas monumentais para os combatentes e bônus passivos para toda a comunidade de seu servidor de origem.",
        "rewards_sample": "Caixas de Linhagem Soberana, Títulos Cósmicos, Diamantes e Asas de Predador Mítico."
    },
    "nobility_titles": {
        "title": "Títulos de Nobreza & Ranking Geral da Temporada",
        "subtitle": "Benefícios passivos de combate PvP concedidos pela classificação global de temporada",
        "icon": "assets/pvp/flat_noble.png",
        "rankings": [
            {
                "title": "Duque",
                "position": "1º Lugar",
                "skill_id": "570015",
                "effect_id": "10065",
                "rp_reward": "400 RP",
                "badge": "badge-crimson",
                "icon": "assets/pvp/buffnoble_duke.png",
                "bonus_skill": "Dignidade do Duque",
                "effects_summary": "Bônus soberano de Ataque, Redução de Dano PvP, Precisão, Esquiva PvP e amplificação máxima na drenagem de sangue.",
                "color": "#ef4444"
            },
            {
                "title": "Marquês",
                "position": "2º e 3º Lugar",
                "skill_id": "570014",
                "effect_id": "10064",
                "rp_reward": "200 RP",
                "badge": "badge-gold",
                "icon": "assets/pvp/buffnoble_marquess.png",
                "bonus_skill": "Dignidade do Marquês",
                "effects_summary": "Atributos avançados de combate PvP e alta taxa de sucesso em drenagem vampírica de alvos.",
                "color": "#f59e0b"
            },
            {
                "title": "Conde",
                "position": "4º ao 6º Lugar",
                "skill_id": "570013",
                "effect_id": "10063",
                "rp_reward": "100 RP",
                "badge": "badge-blue",
                "icon": "assets/pvp/buffnoble_earl.png",
                "bonus_skill": "Dignidade do Conde",
                "effects_summary": "Aumento significativo em mitigação de dano de jogadores rivais e precisão de golpes.",
                "color": "#38bdf8"
            },
            {
                "title": "Visconde",
                "position": "7º ao 40º Lugar",
                "skill_id": "570012",
                "effect_id": "10062",
                "rp_reward": "50 RP",
                "badge": "badge-purple",
                "icon": "assets/pvp/buffnoble_viscount.png",
                "bonus_skill": "Dignidade do Visconde",
                "effects_summary": "Atributos intermediários de defesa territorial, ataque e preservação de pontos de sangue.",
                "color": "#a855f7"
            },
            {
                "title": "Barão",
                "position": "41º ao 100º Lugar",
                "skill_id": "570011",
                "effect_id": "10061",
                "rp_reward": "25 RP",
                "badge": "badge-gray",
                "icon": "assets/pvp/buffnoble_baron.png",
                "bonus_skill": "Dignidade do Barão (205003)",
                "effects_summary": "Ataque +6, Redução de Dano PvP +6, Precisão +3 (Skill diz +6, Efeito +3), Esquiva PvP +3.",
                "color": "#94a3b8"
            }
        ],
        "ranking_pillars": [
            {
                "name": "1. Invocação (Gacha)",
                "icon": "assets/items/itembox_artifactenchantmaterial_random_01.png",
                "badge": "badge-blue",
                "desc": "Pontos ao obter itens raros, heroicos ou lendários por invocações. Raro: 10 pts, Épico: 105 pts, Lendário: 1.400 pts (ScoreTabId=101)."
            },
            {
                "name": "2. Raides Mundiais",
                "icon": "assets/pvp/flat_conquest.png",
                "badge": "badge-crimson",
                "desc": "Contribuir para derrotar Chefes Mundiais de campo; os pontos acumulados são calculados proporcionalmente ao dano e suporte na batalha."
            },
            {
                "name": "3. Mercado Negro",
                "icon": "assets/items/materials_artifactenchantmaterial_01.png",
                "badge": "badge-gold",
                "desc": "Obter Moedas do Mercado Negro em transações com o Comerciante Errante (Wanderer Trade)."
            },
            {
                "name": "4. Aprimoramento",
                "icon": "assets/items/flat_enchant.png",
                "badge": "badge-purple",
                "desc": "Alcançar o limiar de destruição no aprimoramento (+6 ou maior com risco de quebra) de armas, armaduras ou acessórios."
            }
        ],
        "rules": {
            "schedule": "Concedido com base na classificação da temporada anterior no reset semanal ({{Schedule::WeeklyReset}})",
            "duration": "Permanece ativo até o final da temporada atual",
            "menu_location": "Obtido e ativado no Menu de Personagem (NOBLE_GET_SYSTEM_MESSAGE)",
            "tiebreaker": "Em empate de pontuação, prioridade para o personagem com nível mais alto; cálculo abrange até o Top 500.",
            "divergence_note": "Divergência técnica: A descrição da habilidade do Barão informa PRE e ESQ PvP +6, enquanto a descrição do efeito e a tabela StaticOperation (GroupId 1110) registram +3. Os testes estáticos indicam que o motor aplica o valor da tabela de efeitos (+3)."
        }
    }
}

with open(os.path.join(OUT_DIR, "pvp.json"), "w", encoding="utf-8") as f:
    json.dump(pvp_catalog, f, indent=2, ensure_ascii=False)
print("  ✓ Processed PvP & War systems.")


# ==========================================
# 11. ITEM ENCHANTMENT & UPGRADE (5,071 Rules across 26 Equipment Types)
# ==========================================
print("Processing Item Enchantment catalog...")
enchantment_catalog = {
    "summary": {
        "total_rules": 5071,
        "equipment_types_count": 26,
        "rarities_count": 8,
        "max_enchant_level": 15,
        "safe_zone_limit": 5,
        "auto_multi_limit": 11,
        "currency": "Gold"
    },
    "scrolls": [
        {
            "id": "scroll_normal",
            "name": "Pergaminho Normal de Aprimoramento",
            "type_code": "8, 9, 10",
            "icon": "assets/items/weaponenchantmaterial_01.png",
            "weapon_icon": "assets/items/weaponenchantmaterial_01.png",
            "armor_icon": "assets/items/armorenchantmaterial_01.png",
            "acc_icon": "assets/items/accessoryenchantmaterial_01.png",
            "tag": "Padrão de Forja",
            "badge": "badge-blue",
            "description": "Aprimora o equipamento correspondente em +1 nível. Possui 100% de taxa de sucesso (Zona Segura) nos níveis +0 a +5. Do nível +6 em diante, surge risco progressivo de quebra (BreakRate).",
            "safe_zone": "+0 até +5 (100% Sucesso)",
            "risk_start": "+6 em diante (Quebra progressiva)"
        },
        {
            "id": "scroll_blessed",
            "name": "Pergaminho Sagrado / Abençoado",
            "type_code": "12, 13, 14",
            "icon": "assets/items/weaponenchantmaterial_02.png",
            "weapon_icon": "assets/items/weaponenchantmaterial_02.png",
            "armor_icon": "assets/items/armorenchantmaterial_02.png",
            "acc_icon": "assets/items/accessoryenchantmaterial_02.png",
            "tag": "Chance de Salto Duplo (+2)",
            "badge": "badge-gold",
            "description": "Quando bem-sucedido, possui chance (BigSuccessRate = 1000) de aumentar o nível em dois (+2) de uma só vez (ex: de +6 direto para +8). ⚠️ ATENÇÃO: NÃO protege contra quebra — possui o mesmo BreakRate bruto do pergaminho normal.",
            "safe_zone": "+0 até +5 (100% Sucesso)",
            "risk_start": "+6 em diante (Mesmo risco de quebra do normal + 10% Salto Duplo)"
        },
        {
            "id": "scroll_cursed",
            "name": "Pergaminho Amaldiçoado",
            "type_code": "16, 17, 18",
            "icon": "assets/items/weaponenchantmaterial_03.png",
            "weapon_icon": "assets/items/weaponenchantmaterial_03.png",
            "armor_icon": "assets/items/armorenchantmaterial_03.png",
            "acc_icon": "assets/items/accessoryenchantmaterial_03.png",
            "tag": "Redução Controlada (-1)",
            "badge": "badge-crimson",
            "description": "Quando o aprimoramento de maldição é bem-sucedido (CurseRate = 10000), diminui o nível do equipamento em 1 (-1). Usado estrategicamente para descer níveis (ex: de +7 para +6) para tentar nova subida abençoada para +8.",
            "safe_zone": "Não se aplica",
            "risk_start": "Reduz 1 nível (-1) com 100% de probabilidade"
        }
    ],
    "transition_rates": [
        {
            "category": "Armas (Espada, Foice, Mosquete, Orbe, Tonfa)",
            "gold_cost": "4.500 Gold",
            "normal_success": "85.0% (8.500)",
            "break_rate": "15.0% (1.500)",
            "big_success": "10.0% (1.000)",
            "risk_profile": "Risco Baixo a Médio",
            "risk_badge": "badge-green"
        },
        {
            "category": "Armaduras (Elmo, Peitoral, Luvas, Botas)",
            "gold_cost": "2.500 Gold",
            "normal_success": "55.0% (5.500)",
            "break_rate": "45.0% (4.500)",
            "big_success": "10.0% (1.000)",
            "risk_profile": "Risco Médio / Custo Menor",
            "risk_badge": "badge-gold"
        },
        {
            "category": "Acessórios (Cinto, Anel, Colar, Brincos, Bracelete)",
            "gold_cost": "8.500 Gold",
            "normal_success": "40.0% (4.000)",
            "break_rate": "60.0% (6.000)",
            "big_success": "10.0% (1.000)",
            "risk_profile": "Risco Alto / Custo Elevado",
            "risk_badge": "badge-crimson"
        },
        {
            "category": "Relíquias & Bens Funerários (Máscara, Cálice, Perfume)",
            "gold_cost": "15.000 Gold",
            "normal_success": "50.0% (5.000)",
            "break_rate": "50.0% (5.000)",
            "big_success": "10.0% (1.000)",
            "risk_profile": "Custo Máximo de Linhagem",
            "risk_badge": "badge-crimson"
        }
    ],
    "sword_progression": [
        {"level": "+0", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+0", "hit": "—", "crit": "+9", "status": "Seguro"},
        {"level": "+1", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+3", "hit": "—", "crit": "+9", "status": "Seguro"},
        {"level": "+2", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+6", "hit": "—", "crit": "+9", "status": "Seguro"},
        {"level": "+3", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+9", "hit": "—", "crit": "+9", "status": "Seguro"},
        {"level": "+4", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+12", "hit": "—", "crit": "+9", "status": "Seguro"},
        {"level": "+5", "succ": "100%", "break": "0%", "gold": "4.500", "atk": "+15", "hit": "—", "crit": "+9", "status": "Limite da Zona Segura"},
        {"level": "+6", "succ": "85%", "break": "15%", "gold": "4.500", "atk": "+18", "hit": "—", "crit": "+9", "status": "Início do Risco de Quebra"},
        {"level": "+7", "succ": "70%", "break": "30%", "gold": "4.500", "atk": "+23 (+5)", "hit": "+3 (Desbloqueado!)", "crit": "+9", "status": "Salto de Atributo + Precisão"},
        {"level": "+8", "succ": "55%", "break": "45%", "gold": "4.500", "atk": "+28", "hit": "+6", "crit": "+9", "status": "Risco Médio"},
        {"level": "+9", "succ": "50%", "break": "50%", "gold": "4.500", "atk": "+33", "hit": "+9", "crit": "+9", "status": "50/50 Chance"},
        {"level": "+10", "succ": "45%", "break": "55%", "gold": "4.500", "atk": "+43 (+10)", "hit": "+15 (+6)", "crit": "+9", "status": "Salto Maior (+10 Atk, +6 Hit)"},
        {"level": "+11", "succ": "40%", "break": "60%", "gold": "4.500", "atk": "+53", "hit": "+21", "crit": "+9", "status": "Limite do Multi-Encantamento"},
        {"level": "+12", "succ": "35%", "break": "65%", "gold": "4.500", "atk": "+63", "hit": "+27", "crit": "+9", "status": "Risco Elevado"},
        {"level": "+13", "succ": "30%", "break": "70%", "gold": "4.500", "atk": "+73", "hit": "+33", "crit": "+9", "status": "Risco Extremo"},
        {"level": "+14", "succ": "25%", "break": "75%", "gold": "4.500", "atk": "+83", "hit": "+39", "crit": "+9", "status": "Penúltimo Nível"},
        {"level": "+15", "succ": "20%", "break": "80%", "gold": "4.500", "atk": "+93", "hit": "+45", "crit": "+9", "status": "Nível Máximo do Jogo"}
    ],
    "accessory_progression": [
        {"level": "+0", "dmg_red": "+13", "skill_hit": "—", "crit_red": "+3", "status": "Base"},
        {"level": "+1", "dmg_red": "+16", "skill_hit": "—", "crit_red": "+3", "status": "Seguro"},
        {"level": "+5", "dmg_red": "+30", "skill_hit": "+3 (Desbloqueado!)", "crit_red": "+3", "status": "Desbloqueia Precisão de Skill"},
        {"level": "+6", "dmg_red": "+35", "skill_hit": "+6", "crit_red": "+3", "status": "Risco de Quebra (60%)"},
        {"level": "+7", "dmg_red": "+40", "skill_hit": "+9", "crit_red": "+3", "status": "Progressão Avançada"},
        {"level": "+10", "dmg_red": "+70", "skill_hit": "+27", "crit_red": "+3", "status": "Salto Monumental de Defesa"},
        {"level": "+15", "dmg_red": "+120", "skill_hit": "+57", "crit_red": "+3", "status": "Nível Máximo Absoluto"}
    ],
    "artifact_transformation": {
        "id": "1101",
        "name": "Transformação I (Óleo de Unção de Olga)",
        "category": "Artefato Místico de Mitigação",
        "unlock_level": 100,
        "unlock_lock_id": "91010",
        "max_level": 20,
        "material_item_id": "110000776",
        "material_name": "Pedra de Aprimoramento de Artefato de Transformação",
        "material_icon": "assets/items/materials_artifactenchantmaterial_04.png",
        "craft_recipe_id": "4020010",
        "craft_recipe_reqs": "180x Pedra de Aprimoramento de Artefato, 25x Trindade, 30.000 Gold",
        "description": "Artefato supremo desbloqueado no Nível 100. Possui 20 estágios de avanço cíclico com 100% de probabilidade de retenção (0% de falha ou destruição), mitigando progressivamente as 5 disciplinas de dano do jogo: Corpo a Corpo, Habilidade, À Distância, Ataque Básico e Magia.",
        "progression": [
            {"level": "+1", "stat_name": "Redução de Poder de Ataque Corpo a Corpo", "stat_key": "AttackPowerReductionMelee", "bonus": "+4", "discipline": "Corpo a Corpo", "discipline_badge": "badge-crimson", "cost_stones": 5, "cost_gold": "400.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+2", "stat_name": "Redução de Dano Corpo a Corpo", "stat_key": "DamageReductionMelee", "bonus": "+2", "discipline": "Corpo a Corpo", "discipline_badge": "badge-crimson", "cost_stones": 5, "cost_gold": "400.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+3", "stat_name": "Redução de Dano Geral", "stat_key": "DamageReduction", "bonus": "+2", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 5, "cost_gold": "400.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+4", "stat_name": "Redução de Poder de Ataque", "stat_key": "AttackPowerReduction", "bonus": "+3", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 5, "cost_gold": "400.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+5", "stat_name": "Redução de Poder de Ataque de Habilidade", "stat_key": "AttackPowerReductionSkill", "bonus": "+4", "discipline": "Habilidade", "discipline_badge": "badge-purple", "cost_stones": 6, "cost_gold": "450.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+6", "stat_name": "Redução de Dano de Habilidade", "stat_key": "DamageReductionSkill", "bonus": "+2", "discipline": "Habilidade", "discipline_badge": "badge-purple", "cost_stones": 6, "cost_gold": "450.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+7", "stat_name": "Redução de Dano Geral", "stat_key": "DamageReduction", "bonus": "+2", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 6, "cost_gold": "450.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+8", "stat_name": "Redução de Poder de Ataque", "stat_key": "AttackPowerReduction", "bonus": "+3", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 6, "cost_gold": "450.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+9", "stat_name": "Redução de Poder de Ataque à Distância", "stat_key": "AttackPowerReductionRange", "bonus": "+4", "discipline": "À Distância", "discipline_badge": "badge-blue", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+10", "stat_name": "Redução de Dano à Distância", "stat_key": "DamageReductionRange", "bonus": "+2", "discipline": "À Distância", "discipline_badge": "badge-blue", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+11", "stat_name": "Redução de Dano Geral", "stat_key": "DamageReduction", "bonus": "+2", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+12", "stat_name": "Redução de Poder de Ataque", "stat_key": "AttackPowerReduction", "bonus": "+3", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+13", "stat_name": "Redução de Poder de Ataque Normal", "stat_key": "AttackPowerReductionNormalAttack", "bonus": "+4", "discipline": "Ataque Básico", "discipline_badge": "badge-gray", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+14", "stat_name": "Redução de Dano de Ataque Normal", "stat_key": "DamageReductionNormalAttack", "bonus": "+2", "discipline": "Ataque Básico", "discipline_badge": "badge-gray", "cost_stones": 7, "cost_gold": "500.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+15", "stat_name": "Redução de Dano Geral", "stat_key": "DamageReduction", "bonus": "+2", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 10, "cost_gold": "550.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+16", "stat_name": "Redução de Poder de Ataque", "stat_key": "AttackPowerReduction", "bonus": "+3", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 10, "cost_gold": "550.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+17", "stat_name": "Redução de Poder de Ataque Mágico", "stat_key": "AttackPowerReductionMagic", "bonus": "+4", "discipline": "Magia", "discipline_badge": "badge-blue", "cost_stones": 10, "cost_gold": "550.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+18", "stat_name": "Redução de Dano Mágico", "stat_key": "DamageReductionMagic", "bonus": "+2", "discipline": "Magia", "discipline_badge": "badge-blue", "cost_stones": 10, "cost_gold": "550.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+19", "stat_name": "Redução de Dano Geral", "stat_key": "DamageReduction", "bonus": "+2", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 10, "cost_gold": "550.000", "rates": "55% / 24% / 21%", "fail": "0%"},
            {"level": "+20", "stat_name": "Redução de Poder de Ataque", "stat_key": "AttackPowerReduction", "bonus": "+3", "discipline": "Mitigação Geral", "discipline_badge": "badge-gold", "cost_stones": 13, "cost_gold": "600.000", "rates": "55% / 24% / 21%", "fail": "0%"}
        ]
    }
}

with open(os.path.join(OUT_DIR, "enchantment.json"), "w", encoding="utf-8") as f:
    json.dump(enchantment_catalog, f, indent=2, ensure_ascii=False)
print("  ✓ Processed Item Enchantment catalog (5,071 rules).")


# ==========================================
# 12. GAME SHOPS & MERCANTILE CATALOG (1,301 Offers, 14 Categories, 78 Tabs)
# ==========================================
print("Processing Game Shops catalog...")
shops_raw = load_csv_list(os.path.join(CSV_DIR, "Shop.csv"))
tabs_raw = load_csv_dict(os.path.join(CSV_DIR, "ShopTab.csv"))
cats_raw = load_csv_dict(os.path.join(CSV_DIR, "ShopCategory.csv"))
cat_names = load_csv_dict(os.path.join(L10N_DIR, "ShopCategory_Name.csv"))
tab_names = load_csv_dict(os.path.join(L10N_DIR, "ShopTab_Name.csv"))
shop_names = load_csv_dict(os.path.join(L10N_DIR, "Shop_Name.csv"))
rewards_raw = load_csv_list(os.path.join(CSV_DIR, "Reward.csv"))

rewards_by_group = defaultdict(list)
for r in rewards_raw:
    gid = r.get("GroupId", "").strip()
    if gid:
        rewards_by_group[gid].append(r)

cost_type_map = {"1": "Asset", "2": "Item", "3": "ItemId", "4": "InAppPurchase"}

cat_counts = defaultdict(int)
offers_list = []

for s in shops_raw:
    sid = s.get("Id", "").strip()
    tid = s.get("ShopTabInfoId", "").strip()
    tab = tabs_raw.get(tid, {})
    cid = tab.get("ShopCategoryInfoId", "").strip()

    cname = cat_names.get(cid, {}).get("MainTabName", "").strip() or "Diversos"
    tname = tab_names.get(tid, {}).get("SubTabName", "").strip() or "Geral"

    cat_counts[cid] += 1

    sname_data = shop_names.get(sid, {})
    name = sname_data.get("Name", "").strip() or f"Oferta #{sid}"
    desc = sname_data.get("Desc", "").strip()

    ctype_code = s.get("CostType", "").strip()
    ctype = cost_type_map.get(ctype_code, "Outro")
    cparam = s.get("CostParam", "").strip()
    cval = s.get("CostValue", "").strip()

    rgid = s.get("BaseRewardGroupId", "").strip()
    rew_list = []
    if rgid and rgid in rewards_by_group:
        for rew in rewards_by_group[rgid][:3]:
            item_id = rew.get("Param", "").strip()
            iname = item_names.get(item_id, {}).get("Name", "").strip() or f"Item #{item_id}"
            cnt = rew.get("MinCount", "1").strip()
            rew_list.append([iname, cnt])

    plim_val = s.get("PurchaseLimitValue", "").strip()
    limit_str = f"Limite: {plim_val}" if plim_val and plim_val != "0" else ""

    img = s.get("Img", "").strip().lower().replace("img_", "")
    icon_path = f"assets/items/{img}.png" if img else "assets/items/flat_shop.png"

    item_dict = {
        "id": sid,
        "name": name,
        "cid": cid,
        "cat": cname,
        "tid": tid,
        "tab": tname,
        "cost_type": ctype,
        "cost_param": cparam,
        "cost_val": cval,
        "icon": icon_path,
        "rewards": rew_list
    }
    if desc:
        item_dict["desc"] = desc
    if limit_str:
        item_dict["limit"] = limit_str
    if s.get("NetmarbleSItemId"):
        item_dict["iap"] = s["NetmarbleSItemId"].strip()
    if s.get("IsSaleClosed") == "1":
        item_dict["closed"] = 1

    offers_list.append(item_dict)

categories_list = [
    {"id": "all", "name": "Todas as Lojas", "count": len(offers_list)},
    {"id": "1", "name": "Produto (Pacotes & IAP)", "count": cat_counts.get("1", 0)},
    {"id": "2", "name": "Trocar (Moedas & Atividades)", "count": cat_counts.get("2", 0)},
    {"id": "4", "name": "Loja de Habilidades", "count": cat_counts.get("4", 0)},
    {"id": "99", "name": "Passe Sazonal", "count": cat_counts.get("99", 0)},
    {"id": "6", "name": "Moeda da Eternidade", "count": cat_counts.get("6", 0)},
    {"id": "7", "name": "Moeda do Clã", "count": cat_counts.get("7", 0)},
    {"id": "18", "name": "Ponto de Geena", "count": cat_counts.get("18", 0)},
    {"id": "19", "name": "Masmorra de Elite", "count": cat_counts.get("19", 0)},
    {"id": "90", "name": "Evento Alto-Baixo", "count": cat_counts.get("90", 0)},
    {"id": "91", "name": "Roleta do Crocodilo", "count": cat_counts.get("91", 0)},
    {"id": "10", "name": "Evocação Especial", "count": cat_counts.get("10", 0)},
    {"id": "11", "name": "Invocação Especial II", "count": cat_counts.get("11", 0)},
    {"id": "5", "name": "Loja de Equipamentos", "count": cat_counts.get("5", 0)},
    {"id": "3", "name": "Loja Geral", "count": cat_counts.get("3", 0)}
]

shops_catalog = {
    "summary": {
        "total_offers": len(offers_list),
        "categories_count": len(cats_raw),
        "tabs_count": len(tabs_raw),
        "cost_types": {
            "in_app_purchase": sum(1 for o in offers_list if o["cost_type"] == "InAppPurchase"),
            "asset": sum(1 for o in offers_list if o["cost_type"] == "Asset"),
            "item": sum(1 for o in offers_list if o["cost_type"] == "Item")
        }
    },
    "categories": categories_list,
    "offers": offers_list
}

with open(os.path.join(OUT_DIR, "shops.json"), "w", encoding="utf-8") as f:
    json.dump(shops_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Game Shops catalog ({len(offers_list)} offers).")


# ==========================================
# 13. GAME CONSTANTS & FAQ
# ==========================================
print("Processing Constants and FAQ...")
constants_dict = {crow.get("Key", "").strip(): crow.get("Value", "").strip() for crow in const_raw if crow.get("Key")}
with open(os.path.join(OUT_DIR, "constants.json"), "w", encoding="utf-8") as f:
    json.dump(constants_dict, f, indent=2, ensure_ascii=False)

faq_catalog = [
    {
        "category": "Mecânicas Vampíricas",
        "question": "O que são Pontos de Sangue (Blood Points / BP) e como funcionam?",
        "answer": "Os Pontos de Sangue (BP) representam a energia vital e espiritual do vampiro. O BP é alimentado através de três mecanismos: 1) Drenagem Direta no Alvo (Target Blood Drain), 2) Drenagem de Execução em inimigos caídos, e 3) Alimentação de Lacaios/Seguidores (Follower.DrainCountRecoveryPotionList). O acúmulo de BP ativa as Formas de Sangue (CostumeArmorSkin), concedendo bônus de dano de até +20%, velocidade adicional e habilidades exclusivas de linhagem."
    },
    {
        "category": "Mecânicas Vampíricas",
        "question": "O que são os Caixões e as Cartas de Tumba (Tomb Cards)?",
        "answer": "O sistema de Caixões (TombCard) é um pilar de descanso e fortalecimento do vampiro. Caixões variam de 'Caixão de Madeira Comum' a 'Caixão de Pedra Requintado' e 'Caixões Nobres'. Ao sincronizar Cartas de Tumba em sua tumba ancestral, o jogador desbloqueia bônus permanentes na Árvore da Linhagem (Bloodline Tree), como resistência a dano de luz, redução de tempo de atordoamento e slots extras para poções de sangue."
    },
    {
        "category": "Combate & Chefes",
        "question": "Como funcionam as 6 Fases dos Grandes Chefes?",
        "answer": "Chefes de Masmorra e Raide possuem 6 fases (EMonsterPhase): Fase 1 (100-85%): rotação básica; Fase 2 (85-70%): primeiras invocações de lacaios; Fase 3 (70-50%): escudos protetores e campos de dano contínuo; Fase 4 (50-30%): ataques em cone e atordoamento; Fase 5 (30-15%): alertas sonoros dedicados (MetaSound) e teleporte; Fase 6 (<15%): Frenesi Mortal (Enrage), onde o chefe dobra a velocidade e o dano até ser derrotado."
    },
    {
        "category": "Combate & Chefes",
        "question": "Como funciona o sistema de Cooldown e delays de habilidades?",
        "answer": "Cada habilidade em VAMPIR possui parâmetros de tempo calibrados: MinCoolTime (tempo base de recarga), MaxCoolTime (tempo com penalidades de ambiente), TotalTime (duração total da animação) e StackCount (cargas acumuláveis). Habilidades com a flag Mobile=1 permitem que o vampiro se movimente enquanto conjura, enquanto DashOffset determina o avanço vetorial durante o golpe."
    },
    {
        "category": "Equipamentos & Forja",
        "question": "Como funciona o Encantamento de Itens e quais são os limites?",
        "answer": "O limite máximo de encantamento é +15 (Auction.FilterMaxEnchantLevel: 15), com zona segura garantida de +0 até +5 (100% de sucesso e 0% de quebra). O multi-encantamento sequencial vai até o nível +11 (ItemEnchant.MultiEnchantSequenceEnchantLevel: 11). Existem 3 tipos de pergaminhos: Normal (avança +1 nível; a partir do +6 há risco de quebra), Abençoado (em caso de sucesso, oferece chance de salto duplo de +2 níveis; ATENÇÃO: a engenharia reversa confirmou que ele NÃO protege contra quebra, possuindo o mesmo BreakRate do pergaminho normal) e Amaldiçoado (aplica maldição garantida com CurseRate de 10.000 reduzindo -1 nível para re-rolagem estratégica)."
    },
    {
        "category": "PvP & Mundo Aberto",
        "question": "Como funciona o PvP em Zonas de Conflito e o Radar de Vingança?",
        "answer": "O mapa é dividido em 3 zonas: Segurança (Safety), Neutra (Neutral) e Conflito (Conflict). Em zonas de conflito, jogadores podem ser atacados livremente. Caso você seja eliminado por um jogador, o sistema ativa o Radar de Vingança (PVP.RevengeWorldGroupIdList), rastreando a localização exata do agressor no mapa com atualização a cada 10 segundos (PVP.LocationSearchPosRefreshTime: 10) por até 24 horas (PVP.ReactionTimeLimit: 86400)."
    },
    {
        "category": "Modos de Jogo & Raides",
        "question": "Qual é a capacidade de Grupos, Raides e Servidores?",
        "answer": "Grupos convencionais suportam até 5 membros (Party.MaxMemberCount: 5). Equipes de Raide suportam até 50 membros simultâneos (RaidTeam.MaxMemberCount: 50) com líder de raid e verificações de prontidão ('Ready Check Duration: 20s'). Em Masmorras Inter-Servidor (Cross-Server), o limite de entrada é de 200 jogadores por servidor conectado (ServerDungeon.ServerEntryLimit: 200)."
    },
    {
        "category": "Automação & Suporte",
        "question": "Como funciona o Modo de Manutenção Automática (SupportMode / AFK)?",
        "answer": "O jogo conta com o recurso SupportModeAutoMaintain, que permite ao personagem continuar farmando ou completando rotinas automaticamente mesmo offline. O sistema monitora poções de vida (AutoMaintain.HpPotionMinCount: 100) e recarrega suprimentos em cidades antes de retornar ao ponto de caça."
    },
    {
        "category": "Economia & Lojas",
        "question": "Como funcionam as Lojas, Moedas de Troca e Pacotes no jogo?",
        "answer": "O catálogo comercial possui 1.301 ofertas mapeadas em 14 categorias e 78 abas. As duas categorias principais são Produto (740 ofertas, incluindo pacotes semanais/mensais e compras no app via Netmarble IAP) e Trocar (337 ofertas para moedas de jogo: Diamantes, Milhas, Ouro, Moedas do Mercado Negro, Pontos de Tumba e Arena). Há também lojas especializadas de Habilidades (55 ofertas de livros arcanos), Passes Sazonais (41), Moedas de Clã e Eternidade (24 cada) e Masmorras de Elite."
    },
    {
        "category": "Arquitetura & Engenharia",
        "question": "Qual motor gráfico e arquitetura de segurança o jogo utiliza?",
        "answer": "O VAMPIR foi desenvolvido na Unreal Engine 5.5.4 em ARM64 (libUnreal.so), utilizando o Gameplay Ability System (GAS), MetaSound para áudio espacial, e FluidNinja para simulação volumétrica de sangue e magia negra. Toda a lógica de combate é Server-Authoritative: cálculos de vida, recarga e dano são validados no servidor, impedindo modificações ilegais de memória de cliente."
    },
    {
        "category": "Mecânicas Vampíricas",
        "question": "Como funciona a Drenagem de Sangue (Drain) em combate e o Medidor de Adrenalina?",
        "answer": "Ao atacar monstros em campo, surge um ícone contextual de Drenar (Drain) com base em taxas probabilísticas calibradas (Guia Oficial Netmarble #129). Pressionar o ícone executa a habilidade especial Drain Skill, que causa morte instantânea (Instant Kill) no monstro-alvo e absorve essência vital. O ato da drenagem preenche o Medidor de Adrenalina (à esquerda dos Quick Slots). Quando a barra atinge 100%, o personagem entra no estado de Adrenalina, recebendo amplificadores severos de dano bruto (DamageMultiplier), taxa crítica (CriticalRate) e velocidades de ataque e conjuração (Adrenaline.csv)."
    },
    {
        "category": "PvP & Mundo Aberto",
        "question": "Quais são os bônus permanentes de combate concedidos aos líderes do Ranking de Nível e Poder de Combate (CP)?",
        "answer": "O VAMPIR recompensa os Top 100 jogadores de cada servidor com bônus de combate maciços aplicados diretamente no personagem (Guia Oficial Netmarble #102 e RankingReward.csv): 1) Top 1: Dano PvP +25, Resiliência a Dano PvP +10 e Precisão PvP +9; 2) Top 2: Dano PvP +20, Resiliência a Dano PvP +8 e Precisão PvP +6; 3) Top 3: Dano PvP +15, Resiliência a Dano PvP +6 e Precisão PvP +3; 4) Top 4 a 10: Dano PvP +10 e Resiliência a Dano PvP +4; 5) Top 11 a 100: Dano PvP +5 e Resiliência a Dano PvP +2. Os bônus são recalculados a cada ciclo periódico de ranking."
    },
    {
        "category": "Equipamentos & Forja",
        "question": "Como funciona a Bênção de Equipamentos (Blessing) com Trindade e quais são as chances?",
        "answer": "O sistema de Bênção (Guia Oficial Netmarble #96 e ItemBlessing.csv) consome Trindade (MaterialItemType #50) para despertar subatributos adicionais em equipamentos de grau Raro, Heroico e Lendário. A taxa de sucesso é rigorosamente fixada em 20,00% (SuccessRate: 2000). Caso a tentativa falhe, o equipamento NÃO é destruído e seu nível de aprimoramento não sofre perda. Ao obter sucesso, o item recebe o prefixo 'Abençoado' no nome e ganha atributos adicionais exibidos em destaque."
    },
    {
        "category": "Automação & Suporte",
        "question": "Quais são as 4 travas de segurança do Modo Suporte (Support Mode / Autoplay)?",
        "answer": "O Modo Suporte (Guia Oficial Netmarble #72) opera caça autônoma mesmo com o jogo fechado ou em segundo plano, protegido por 4 travas de segurança: 1) Reabastecimento Automático: Ao atingir o limite mínimo de poções, retorna à cidade mais próxima, compra suprimentos configurados e usa teleporte de volta à caçada; 2) Fuga PvP: Ao sofrer agressão hostil de outro jogador em área de conflito, executa teleporte de emergência imediato para a vila; 3) Proteção de Sobrecarga: Suspende a caça ao atingir 100% de capacidade de peso no inventário; 4) Alerta Remoto: Notifica o jogador no launcher de PC ou aplicativo caso o personagem seja derrotado acidentalmente."
    },
    {
        "category": "Comunidade & Clãs",
        "question": "Como funcionam as Patentes de Clã, Sucessão por Inatividade e a Cripta de Clã?",
        "answer": "Os Clãs (Guild.csv e Guias Oficiais #48 e #110) possuem 6 patentes: Mestre (Master), Vice-Mestre (Vice Master), Líder (Leader), Elite, Geral (General) e Aprendiz (Apprentice). Se o Mestre permanecer sem efetuar login por 5 dias consecutivos, a autoridade máxima de liderança é delegada automaticamente pelo servidor para outro membro ativo. Ao sair ou desbandar um clã, o jogador sofre um bloqueio de 5 minutos antes de poder ingressar em outro. A Cripta do Clã (GuildCrypt.csv) atua como cofre de espólios raros obtidos em raides, permitindo distribuição direta pelo líder ou realização de leilões internos."
    },
    {
        "category": "Economia & Lojas",
        "question": "Como funcionam o Mercado entre Jogadores (Marketplace) e o Mercado Negro?",
        "answer": "O Mercado (Marketplace, Guia Oficial #45) opera leilões com Diamantes entre jogadores para equipamentos negociáveis, gemas e insumos raros. Cada venda concluída recolhe uma taxa de transação oficial, sendo também possível realizar Comércio Privado (Private Trade) direto. O Mercado Negro (Black Market, Guia Oficial #46) é um balcão de câmbio dinâmico no qual materiais específicos e Moedas do Mercado Negro são trocados por consumíveis arcanos, chaves de masmorra e baús selados com cotas de estoque limitadas por servidor."
    },
    {
        "category": "PvP & Mundo Aberto",
        "question": "O que é o Campo de Batalha de Geena (Gehenna) e como funcionam os Pontos de Geena?",
        "answer": "Geena (Guia Oficial Netmarble #112) é um território aberto de PvP e caça de alta intensidade, com capacidade máxima limitada a 200 jogadores por instância. A entrada exige um Bilhete de Entrada de Geena e a região é subdividida em zonas com monstros de elite e chefes mundiais exclusivos. Abater ameaças em Geena concede a moeda especial Pontos de Geena (Gehenna Points), que pode ser trocada com o Mercador de Geena na vila por itens épicos e fórmulas de progressão."
    },
    {
        "category": "Mundo & Exploração",
        "question": "Como funcionam os Portões de Sangue (Blood Gate) e a expansão do Mapa Mundial?",
        "answer": "Os Portões de Sangue (Guia Oficial Netmarble #111) são marcos arcanos espalhados pelas províncias do jogo. Em estado inativo, exibem luz cinzenta e a região circundante no Mapa Mundial permanece encoberta por névoa. Ao se aproximar e ativar o portão, ele projeta um feixe de luz vermelha no campo e ícone branco no mapa, dissipando o nevoeiro territorial, revelando a lista completa de espólios dos pontos de caça próximos e liberando rota de teleporte instantâneo."
    },
    {
        "category": "Mundo & Exploração",
        "question": "O que são os Anais (Annals) e a Saga do Servidor no sistema de Arquivo?",
        "answer": "O sistema de Arquivo (Archive.csv e Guia Oficial #52) documenta a história do servidor em duas frentes: 1) Anais (Annals): Conquistas comunitárias cooperativas (ex: total acumulado de monstros e masmorras limpas por todos os jogadores). Ao completar a meta, todos os personagens do servidor recebem recompensas; 2) Saga: Conquistas competitivas de Primeiro do Servidor (First Clear/First Kill). O nome do jogador ou do clã pioneiro é imortalizado na crônica do servidor e uma recompensa comemorativa é distribuída para a comunidade."
    },
    {
        "category": "Progressão & Personagem",
        "question": "Como funciona o sistema de Disciplina (Engraving) e travas de compartimento com Trindade?",
        "answer": "A Disciplina (Engraving.csv, EngravingSlot.csv e Guia Oficial #47) permite gravar atributos permanentes em 3 compartimentos por capítulo mediante o consumo de Trindade (20 unidades base). O jogador pode utilizar o recurso de Trava (Slot Lock) para congelar atributos desejados: travar 1 slot eleva o custo para 30 Trindades, e travar 2 slots eleva para 150 Trindades por tentativa. Quando os atributos máximos são atingidos em todos os 3 slots do capítulo, um bônus adicional de sinergia é ativado."
    }
]

with open(os.path.join(OUT_DIR, "faq.json"), "w", encoding="utf-8") as f:
    json.dump(faq_catalog, f, indent=2, ensure_ascii=False)


# ==========================================
# 14. CODEX & ANCESTRAL COLLECTIONS CATALOG
# ==========================================
print("Processing Codex & Ancestral Collections catalog...")

STAT_NAME_MAP = {
    "AttackPower": "Poder de Ataque",
    "AttackPowerBoss": "Poder de Ataque contra Chefes",
    "AttackPowerMonster": "Poder de Ataque contra Monstros",
    "AttackPowerNormalAttack": "Poder de Ataque Normal",
    "AttackPowerPvp": "Poder de Ataque PvP",
    "AttackPowerReduction": "Redução de Poder de Ataque",
    "AttackPowerReductionBoss": "Redução de Ataque de Chefes",
    "AttackPowerReductionMagic": "Redução de Ataque Mágico",
    "AttackPowerReductionMelee": "Redução de Ataque Corpo a Corpo",
    "AttackPowerReductionMonster": "Redução de Ataque de Monstros",
    "AttackPowerReductionNormalAttack": "Redução de Ataque Normal",
    "AttackPowerReductionPvp": "Redução de Ataque PvP",
    "AttackPowerReductionRange": "Redução de Ataque à Distância",
    "AttackPowerReductionSkill": "Redução de Ataque de Habilidade",
    "AttackPowerSkill": "Poder de Ataque de Habilidade",
    "CriticalDamageMultiplier": "Dano Crítico (%)",
    "CriticalDamageMultiplierMonster": "Dano Crítico contra Monstros (%)",
    "CriticalDamageMultiplierPvp": "Dano Crítico PvP (%)",
    "CriticalResistanceRate": "Resistência a Crítico (%)",
    "CriticalResistanceRateMonster": "Resistência a Crítico de Monstros (%)",
    "CriticalResistanceRatePvp": "Resistência a Crítico PvP (%)",
    "DamageMultiplier": "Dano Adicional (%)",
    "DamageMultiplierBoss": "Dano contra Chefes (%)",
    "DamageMultiplierMonster": "Dano contra Monstros (%)",
    "DamageMultiplierNormalAttack": "Dano de Ataque Normal (%)",
    "DamageMultiplierPvp": "Dano PvP (%)",
    "DamageMultiplierSkill": "Dano de Habilidade (%)",
    "DamageReducer": "Redutor de Dano",
    "DamageReducerBoss": "Redutor de Dano de Chefes",
    "DamageReduction": "Redução de Dano",
    "DamageReductionBoss": "Redução de Dano de Chefes",
    "DamageReductionCritical": "Redução de Dano Crítico",
    "DamageReductionMagic": "Redução de Dano Mágico",
    "DamageReductionMelee": "Redução de Dano Corpo a Corpo",
    "DamageReductionMonster": "Redução de Dano de Monstros",
    "DamageReductionNormalAttack": "Redução de Dano de Ataque Normal",
    "DamageReductionPvp": "Redução de Dano PvP",
    "DamageReductionRange": "Redução de Dano à Distância",
    "DamageReductionSkill": "Redução de Dano de Habilidade",
    "DamageValue": "Dano Fixo Adicional",
    "DamageValueBoss": "Dano contra Chefes",
    "DamageValueCritical": "Dano Crítico",
    "DamageValueMonster": "Dano contra Monstros",
    "DamageValueNormalAttack": "Dano de Ataque Normal",
    "DamageValuePvp": "Dano PvP",
    "DamageValueSkill": "Dano de Habilidade",
    "DodgeValue": "Esquiva",
    "DodgeValueBoss": "Esquiva contra Chefes",
    "DodgeValueMagic": "Esquiva Mágica",
    "DodgeValueMelee": "Esquiva Corpo a Corpo",
    "DodgeValueMonster": "Esquiva contra Monstros",
    "DodgeValueNormalAttack": "Esquiva de Ataque Normal",
    "DodgeValuePvp": "Esquiva PvP",
    "DodgeValueRange": "Esquiva à Distância",
    "DodgeValueSkill": "Esquiva de Habilidade",
    "ExpAmountMultiplier": "Bônus de EXP (%)",
    "GoldAmountMultiplier": "Bônus de Ouro (%)",
    "HitRateCrowdControl": "Taxa de Acerto de CC (%)",
    "HitValue": "Precisão",
    "HitValueBoss": "Precisão contra Chefes",
    "HitValueMonster": "Precisão contra Monstros",
    "HitValueNormalAttack": "Precisão de Ataque Normal",
    "HitValuePvp": "Precisão PvP",
    "HitValueSkill": "Precisão de Habilidade",
    "HpRecovery": "Recuperação de HP",
    "IgnoreCriticalDamageMultiplier": "Ignorar Dano Crítico (%)",
    "IgnoreCriticalDamageMultiplierMonster": "Ignorar Dano Crítico de Monstros (%)",
    "IgnoreCriticalDamageMultiplierPvp": "Ignorar Dano Crítico PvP (%)",
    "MaxHp": "HP Máximo",
    "MaxInventoryWeight": "Limite de Peso",
    "MaxMp": "MP Máximo",
    "MpRecovery": "Recuperação de MP",
    "NormalAttackSpeedMultiplier": "Velocidade de Ataque Normal (%)",
    "SkillAttackSpeedMultiplier": "Velocidade de Ataque de Habilidade (%)",
    "WeaponAttackPower": "Poder de Ataque da Arma",
    "WeaponAttackPowerMax": "Poder de Ataque Máx. da Arma",
    "DamageReducerMonster": "Resiliência a Dano de Monstros",
    "DamageReducerNormalAttack": "Resiliência a Dano de Ataque Básico",
    "DamageReducerPvp": "Resiliência a Dano PvP",
    "MoveSpeedMultiplier": "Velocidade de Movimento (%)",
    "ResistRateCrowdControl": "Resistência a Efeitos de Controle (%)",
    "SkillCoolTimeReducer": "Redução de Recarga de Habilidade"
}

codex_collections_list = []
for r in codex_collections_raw:
    tid = int(r["CollectionTabId"])
    rar = int(r["Rarity"] or 0)
    reqs = json.loads(r["requisitos_json"])
    effs = json.loads(r["efeitos_json"])
    
    compact_reqs = []
    for q in reqs:
        q_id = q["CollectParam"]
        p_item = all_processed_items.get(q_id)
        icon_img = p_item["icon_img"] if p_item else "assets/logo.png"
        compact_reqs.append({
            "id": q_id,
            "name": q["item_nome"],
            "r": int(q.get("item_raridade", 0) or 0),
            "ench": int(q.get("EnchantLevel", 0) or 0),
            "qty": int(q.get("Count", 1) or 1),
            "icon": icon_img
        })

    compact_effs = []
    for e in effs:
        raw_t = e.get("tipo_nome") or e.get("Type")
        t_label = STAT_NAME_MAP.get(raw_t, raw_t)
        min_v = e.get("Min", "0")
        max_v = e.get("Max", "0")
        val_str = f"+{min_v}" if min_v == max_v else f"+{min_v}~{max_v}"
        compact_effs.append({
            "name": t_label,
            "raw_type": raw_t,
            "val": val_str,
            "min": min_v,
            "max": max_v
        })

    codex_collections_list.append({
        "id": r["Id"],
        "tab": tid,
        "tab_name": TAB_LABELS.get(tid, f"Aba {tid}"),
        "name": r["nome_pt"],
        "rarity": rar,
        "rarity_name": RARITY_LABELS.get(rar, "Comum"),
        "reqs": compact_reqs,
        "effects": compact_effs
    })

# Process Tile Codex Entries (codex_entradas.csv)
COLLECT_TYPE_MAP = {
    "0": {"name": "Formas de Sangue (Costume)", "table": "Costume", "icon": "assets/classes/darkmage_icon.png"},
    "2": {"name": "Montarias (Vehicle)", "table": "Vehicle", "icon": "assets/items/flat_relic.png"},
    "4": {"name": "Cartas da Tumba (TombCard)", "table": "TombCard", "icon": "assets/items/itembox_relic_01.png"},
    "6": {"name": "Cartas de Habilidade (SkillCard)", "table": "SkillCard", "icon": "assets/items/flat_skillcard.png"},
    "8": {"name": "Progênies / Mascotes (Pet)", "table": "Pet", "icon": "assets/logo.png"}
}

codex_entries_list = []
entradas_csv_path = os.path.join(CODEX_REPORTS_DIR, "codex_entradas.csv")
unmatched_count = 0
if os.path.exists(entradas_csv_path):
    with open(entradas_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            ct = r["CollectType"]
            cands = json.loads(r["candidatos_json"])
            matched = len(cands) > 0
            if matched:
                c = cands[0]
                name = c.get("nome") or "Sem Nome"
                tbl = c.get("tabela") or COLLECT_TYPE_MAP.get(ct, {}).get("table", "Desconhecido")
                rar = int(c.get("dados", {}).get("Rarity", 0) or 0)
            else:
                unmatched_count += 1
                name = f"Alvo Reservado #{r['FillTileNum']} (ID Pendente)"
                tbl = "Pendente"
                rar = 0

            codex_entries_list.append({
                "type": ct,
                "type_name": COLLECT_TYPE_MAP.get(ct, {}).get("name", f"Tipo {ct}"),
                "tile_num": int(r["FillTileNum"] or 0),
                "group_id": r["GroupId"],
                "param": r["CollectParam"],
                "matched": matched,
                "name": name,
                "table": tbl,
                "rarity": rar,
                "rarity_name": RARITY_LABELS.get(rar, "Comum")
            })

# Process Character Codex (CharacterCollection.csv)
char_collections = []
char_csv_path = os.path.join(CODEX_REPORTS_DIR, "CharacterCollection.csv")
if os.path.exists(char_csv_path):
    with open(char_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            char_collections.append({
                "id": r["Id"],
                "name": r["nome_pt"],
                "quest_id": r["UnlockQuestInfoId"],
                "points": [r["NeedEpisodePoint1"], r["NeedEpisodePoint2"], r["NeedEpisodePoint3"], r["NeedEpisodePoint4"], r["NeedEpisodePoint5"]],
                "rewards": [r["EpisodeRewardGroupId1"], r["EpisodeRewardGroupId2"], r["EpisodeRewardGroupId3"], r["EpisodeRewardGroupId4"], r["EpisodeRewardGroupId5"]]
            })

# Process Tomb Card Collection Groups (TombCardCollectionGroup.csv)
tomb_card_groups = []
tc_csv_path = os.path.join(CODEX_REPORTS_DIR, "TombCardCollectionGroup.csv")
if os.path.exists(tc_csv_path):
    with open(tc_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            tomb_card_groups.append({
                "id": r["Id"],
                "name": r["nome_pt"],
                "order": r["DisplayOrder"]
            })

codex_catalog = {
    "stats": {
        "total_collections": len(codex_collections_list),
        "total_requirements": 6801,
        "total_entries": len(codex_entries_list),
        "matched_entries": len(codex_entries_list) - unmatched_count,
        "unmatched_entries": unmatched_count,
        "character_territories": len(char_collections),
        "tomb_card_groups": len(tomb_card_groups)
    },
    "collections": codex_collections_list,
    "entries": codex_entries_list,
    "character": char_collections,
    "tomb_cards": tomb_card_groups
}

with open(os.path.join(OUT_DIR, "codex.json"), "w", encoding="utf-8") as f:
    json.dump(codex_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Codex & Collections ({len(codex_collections_list)} collections, {len(codex_entries_list)} tile entries, {unmatched_count} pending IDs preserved).")


# ==========================================
# 15. MAGIC RESEARCH CATALOG (EXTRACT SYSTEM)
# ==========================================
print("Processing Magic Research catalog (Extract system)...")
RESEARCH_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/pesquisa-magica")

steps_by_group = defaultdict(list)
extract_step_path = os.path.join(RESEARCH_REPORTS_DIR, "ExtractStep.csv")
if os.path.exists(extract_step_path):
    with open(extract_step_path, "r", encoding="utf-8-sig") as f:
        for s in csv.DictReader(f):
            c_list = json.loads(s["custo_json"])
            c_name = c_list[0]["item_nome"] if c_list else ""
            c_val = c_list[0]["CostValue"] if c_list else "0"
            c_id = c_list[0].get("CostParam", "") if c_list else ""
            c_icon = all_processed_items.get(c_id, {}).get("icon_img", "assets/items/flat_potion.png") if c_id else "assets/items/flat_potion.png"
            e_list = json.loads(s["efeitos_json"])
            steps_by_group[s["GroupId"]].append({
                "step": int(s["Step"]),
                "rate": int(s["GrowthSuccessRate"] or 0),
                "cost_name": c_name,
                "cost_val": int(c_val) if str(c_val).isdigit() else 0,
                "cost_id": c_id,
                "cost_icon": c_icon,
                "effects": [
                    {
                        "name": STAT_NAME_MAP.get(e.get("tipo_nome") or e.get("Type"), e.get("tipo_nome") or e.get("Type")),
                        "val": f"+{e.get('Min', '0')}" if e.get("Min") == e.get("Max") else f"+{e.get('Min', '0')}~{e.get('Max', '0')}",
                        "raw_type": e.get("tipo_nome") or e.get("Type")
                    }
                    for e in e_list
                ]
            })

magic_flasks_data = []
extract_group_path = os.path.join(RESEARCH_REPORTS_DIR, "ExtractGroup.csv")
if os.path.exists(extract_group_path):
    with open(extract_group_path, "r", encoding="utf-8-sig") as f:
        for g in csv.DictReader(f):
            c_trin = json.loads(g["custo_json"])
            c_cat = json.loads(g["custo_substituto_json"])
            trin_val = c_trin[0]["CostValue"] if c_trin else "0"
            cat_val = c_cat[0]["CostValue"] if c_cat else "0"
            e_list = json.loads(g["efeitos_json"])
            magic_flasks_data.append({
                "id": g["Id"],
                "line_id": g["ExtractId"],
                "line_name": g["magia"],
                "name": f"{g['frasco_nome']} {g['frasco_nivel']}",
                "base_name": g["frasco_nome"],
                "level": g["frasco_nivel"],
                "rate": int(g["CompleteSuccessRate"] or 0),
                "rate_display": f"{int(g['CompleteSuccessRate'] or 0)/100:.1f}%" if g["CompleteSuccessRate"] else "0%",
                "trinity": int(trin_val) if str(trin_val).isdigit() else 0,
                "catalyst": int(cat_val) if str(cat_val).isdigit() else 0,
                "effects": [
                    {
                        "name": STAT_NAME_MAP.get(e.get("tipo_nome") or e.get("Type"), e.get("tipo_nome") or e.get("Type")),
                        "val": f"+{e.get('Min', '0')}" if e.get("Min") == e.get("Max") else f"+{e.get('Min', '0')}~{e.get('Max', '0')}",
                        "raw_type": e.get("tipo_nome") or e.get("Type")
                    }
                    for e in e_list
                ],
                "steps": sorted(steps_by_group.get(g["Id"], []), key=lambda x: x["step"])
            })

MAGIC_LINES_INFO = [
    {
        "id": "100",
        "name": "Magia da Criação",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 15,
        "lock_val": "32",
        "primary_orb": "Orbe Mágica da Criação",
        "orb_source": "Abismo da Criação (Masmorra)",
        "focus": "Dano de Ataque Normal, Precisão e Redução de Dano Normal"
    },
    {
        "id": "200",
        "name": "Magia Desbotada",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 15,
        "lock_val": "34",
        "primary_orb": "Orbe Mágica Desbotada",
        "orb_source": "Abismo Desbotado (Masmorra)",
        "focus": "Poder de Ataque de Habilidade, Precisão e Redução de Habilidade"
    },
    {
        "id": "300",
        "name": "Magia Antiga",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 15,
        "lock_val": "41",
        "primary_orb": "Orbe Mágica Antiga",
        "orb_source": "Ruínas Antigas (Masmorra)",
        "focus": "Dano contra Monstros, Precisão contra Monstros e Esquiva"
    },
    {
        "id": "400",
        "name": "Magia da Geena",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 15,
        "lock_val": "52",
        "primary_orb": "Orbe Mágica de Geena",
        "orb_source": "Profundezas de Geena (Masmorra de Reide)",
        "focus": "Dano contra Chefes, Precisão contra Chefes e Redução de Chefes"
    },
    {
        "id": "500",
        "name": "Magia de Elite",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 10,
        "lock_val": "70",
        "primary_orb": "Orbe Mágica de Elite",
        "orb_source": "Zonas de Monstros de Elite e Chefes de Campo",
        "focus": "Poder de Ataque Geral, Redução de Dano Crítico e Bônus"
    },
    {
        "id": "600",
        "name": "Magia de Evolução",
        "icon": "assets/items/flat_potion.png",
        "flasks_count": 20,
        "lock_val": "78",
        "primary_orb": "Orbe Mágico de Evolução",
        "orb_source": "Campos Dimensionais & Zonas de Guerra",
        "focus": "Poder de Ataque PvP, Esquiva PvP e Multiplicadores Críticos"
    }
]

research_catalog = {
    "stats": {
        "total_lines": 6,
        "total_flasks": len(magic_flasks_data),
        "total_steps": 890
    },
    "lines": MAGIC_LINES_INFO,
    "flasks": magic_flasks_data
}

with open(os.path.join(OUT_DIR, "research.json"), "w", encoding="utf-8") as f:
    json.dump(research_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Magic Research ({len(magic_flasks_data)} flasks across 6 lines, 890 infusion steps).")


# ==========================================
# 16. PORTRAITS CATALOG (PORTRAIT & FRAGMENTS SYSTEM)
# ==========================================
print("Processing Portraits & Fragments catalog...")
PORTRAITS_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/retratos")

RARITY_PT_MAP = {
    "Common": "Comum",
    "Uncommon": "Incomum",
    "Rare": "Raro",
    "Epic": "Heroico",
    "Legendary": "Lendário",
    "Mythic": "Mítico"
}
TYPE_PT_MAP = {
    "0": "Personagens & Linhagens",
    "1": "Especiais & Eventos",
    "2": "Retrato Inicial Padrão"
}

portraits_list = []
portraits_csv_path = os.path.join(PORTRAITS_REPORTS_DIR, "retratos.csv")
if os.path.exists(portraits_csv_path):
    with open(portraits_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            frags = json.loads(r["fragmentos_json"])
            rets = json.loads(r["retencao_json"])

            effects_summary = defaultdict(int)
            compact_ret = []
            for ret in rets:
                effs = json.loads(ret.get("efeitos_json", "[]"))
                rews = json.loads(ret.get("recompensas_json", "[]"))
                eff_list = []
                for e in effs:
                    raw_t = e.get("tipo_nome") or e.get("Type")
                    tname = STAT_NAME_MAP.get(raw_t, raw_t)
                    min_v = int(e.get("Min", "0") or 0)
                    effects_summary[tname] += min_v
                    eff_list.append({"name": tname, "val": f"+{e.get('Min', '0')}"})

                rew_list = []
                for rw in rews:
                    p = rw.get("Param") or rw.get("item_nome") or "Recompensa"
                    min_c = rw.get("MinCount", "0")
                    rew_list.append({"name": p, "count": f"{int(min_c):,}" if str(min_c).isdigit() else str(min_c)})

                compact_ret.append({
                    "milestone": int(ret.get("Count", 0)),
                    "effects": eff_list,
                    "rewards": rew_list
                })

            compact_frags = []
            for fr in frags:
                m_id = fr.get("MaterialItemInfoId", "")
                m_item = all_processed_items.get(m_id)
                m_icon = m_item["icon_img"] if m_item else "assets/items/flat_relic.png"
                compact_frags.append({
                    "num": int(fr.get("Num", 0)),
                    "mat_id": m_id,
                    "mat_name": fr.get("material_nome", ""),
                    "qty": int(fr.get("MaterialItemNeedCount", 0) or 0),
                    "individual": fr.get("IsIndividualCount", "0") == "1",
                    "icon": m_icon
                })

            rate_raw = r["AcquireSuccessRate"] or "10000"
            rate_disp = f"{int(rate_raw)/100:.1f}%" if str(rate_raw).isdigit() else "100.0%"

            pid = r["Id"]
            p_icon = f"assets/portraits/portrait_{pid}.png"
            p_art_cand = f"assets/portraits/portrait_{pid}_big.png"
            p_art = p_art_cand if os.path.exists(os.path.join(BASE_DIR, "faq", p_art_cand)) else p_icon

            portraits_list.append({
                "id": pid,
                "group_id": r["GroupId"],
                "name": r["nome_pt"],
                "icon": p_icon,
                "art": p_art,
                "rarity_code": r["Rarity"],
                "rarity": RARITY_PT_MAP.get(r["raridade_nome"], r["raridade_nome"]),
                "type_code": r["PortraitBigType"],
                "type": TYPE_PT_MAP.get(r["PortraitBigType"], "Geral"),
                "is_default": r["IsDefault"] == "1",
                "rate": rate_raw,
                "rate_display": rate_disp,
                "frags_count": len(compact_frags),
                "fragments": compact_frags,
                "retention": compact_ret,
                "summary_effects": [{"name": k, "total": f"+{v}"} for k, v in effects_summary.items()]
            })

portraits_catalog = {
    "stats": {
        "total_portraits": len(portraits_list),
        "total_fragments": 665,
        "portraits_with_fragments": sum(1 for p in portraits_list if p["frags_count"] > 0),
        "total_retention_rules": 665
    },
    "portraits": portraits_list
}

with open(os.path.join(OUT_DIR, "portraits.json"), "w", encoding="utf-8") as f:
    json.dump(portraits_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Portraits catalog ({len(portraits_list)} portraits, 665 fragments).")

# ==========================================
# 17. ARTIFACTS CATALOG (5 ORIGINAIS + TRANSFORMAÇÃO I)
# ==========================================
print("Processing Artifacts & Enhancement catalog...")
ARTIFACTS_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/artefatos")

PCT_STAT_KEYS = {
    'DamageMultiplier', 'CriticalDamageMultiplier', 'IgnoreCriticalDamageMultiplier',
    'DamageReducer', 'HitRateCrowdControl', 'DamageMultiplierNormalAttack',
    'DamageMultiplierSkill', 'DamageMultiplierBoss', 'DamageMultiplierPvp'
}

artifacts_list = []
artifacts_csv_path = os.path.join(ARTIFACTS_REPORTS_DIR, "artefatos.csv")
enchant_csv_path = os.path.join(ARTIFACTS_REPORTS_DIR, "aprimoramentos.csv")

if os.path.exists(artifacts_csv_path) and os.path.exists(enchant_csv_path):
    levels_by_artifact = defaultdict(list)
    with open(enchant_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            levels_by_artifact[r["ArtifactId"]].append(r)

    with open(artifacts_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            aid = r["Id"]
            al = levels_by_artifact.get(aid, [])
            totals = defaultdict(float)
            compact_levels = []
            materials_seen = {}
            milestones = []

            for l in al:
                lvl = int(l["Level"])
                fail_r = round(float(l["EnchantFailRate"] or 0) / 100, 1)
                s1_r = round(float(l["EnchantSuccessRate1"] or 0) / 100, 1)
                s2_r = round(float(l["EnchantSuccessRate2"] or 0) / 100, 1)
                s3_r = round(float(l["EnchantSuccessRate3"] or 0) / 100, 1)

                costs_raw = json.loads(l["custos_json"])
                costs_compact = []
                for co in costs_raw:
                    c_param = co.get("CostParam")
                    c_val = int(co.get("CostValue") or 0)
                    c_name = co.get("item_nome") or ("Ouro" if c_param == "Gold" else c_param)
                    if c_param == "Gold":
                        c_icon = "assets/items/asset_gold.png"
                    elif c_param in all_processed_items:
                        c_icon = all_processed_items[c_param].get("icon_img") or "assets/items/materials_artifactenchantmaterial_01.png"
                    else:
                        c_icon = "assets/items/materials_artifactenchantmaterial_01.png"

                    costs_compact.append({"name": c_name, "param": c_param, "amount": c_val, "icon": c_icon})
                    if c_name not in materials_seen:
                        materials_seen[c_name] = {"name": c_name, "icon": c_icon}

                effs_raw = json.loads(l["efeitos_json"])
                effs_compact = []
                for e in effs_raw:
                    t = e.get("tipo_nome")
                    v = float(e.get("Min") or 0)
                    totals[t] += v
                    t_name = STAT_NAME_MAP.get(t, t)
                    v_disp = f"+{v/100:.1f}%" if t in PCT_STAT_KEYS else f"+{int(v):,}"
                    effs_compact.append({"key": t, "name": t_name, "val": v_disp, "raw_val": v})

                rews_raw = json.loads(l["recompensas_json"])
                rews_compact = []
                for rw in rews_raw:
                    rw_p = rw.get("Param") or rw.get("item_nome") or "Recompensa de Marco"
                    rw_cnt = rw.get("MinCount", "1")
                    rews_compact.append({"name": f"Emblema de Marco {rw_p}" if rw.get("Type") == "20" else rw_p, "count": rw_cnt})

                is_final = l["FinalStageEvent"] == "1"
                if rews_compact or is_final:
                    milestones.append({"level": lvl, "rewards": rews_compact, "is_final": is_final})

                compact_levels.append({
                    "level": lvl,
                    "fail": fail_r,
                    "s1": s1_r,
                    "s2": s2_r,
                    "s3": s3_r,
                    "costs": costs_compact,
                    "effects": effs_compact,
                    "rewards": rews_compact,
                    "final": is_final
                })

            summary_effects = []
            for t, v in totals.items():
                name = STAT_NAME_MAP.get(t, t)
                disp = f"+{v/100:.1f}%" if t in PCT_STAT_KEYS else f"+{int(v):,}"
                summary_effects.append({"key": t, "name": name, "total": disp, "raw_total": v, "is_pct": t in PCT_STAT_KEYS})
            summary_effects.sort(key=lambda x: (not x["is_pct"], -x["raw_total"]))

            art_map = {
                "1001": ("assets/artifacts/artifact_1001.png", "assets/artifacts/art_1001.png"),
                "1101": ("assets/artifacts/artifact_1101.png", "assets/artifacts/art_1101.png"),
                "1002": ("assets/artifacts/artifact_1002.png", "assets/artifacts/art_1002.png"),
                "1003": ("assets/artifacts/artifact_1003.png", "assets/artifacts/art_1003.png"),
                "1004": ("assets/artifacts/artifact_1004.png", "assets/artifacts/art_1004.png"),
                "1005": ("assets/artifacts/artifact_1005.png", "assets/artifacts/art_1005.png"),
            }
            icon_img, art_img = art_map.get(aid, ("assets/artifacts/artifact_1001.png", "assets/artifacts/art_1001.png"))

            disp_name = r["categoria_nome"]
            if r["Type"] == "1":
                disp_name = f"{r['categoria_nome']} ({r['variante_nome']})"

            divergence = None
            if aid == "1004":
                divergence = "Divergência: O texto da interface do jogo afirma Nv. 90, mas a condição técnica cadastrada exige Nv. 100."

            transform_info = None
            if r["Type"] == "1":
                transform_info = {
                    "limit_count": int(r["EnchantLimitCount"] or 20),
                    "save_cost": "100.000 Ouro",
                    "load_cost": "200.000 Ouro",
                    "reset_cost": "200.000 Ouro",
                    "unlock_condition": "Exige Olga Original Nv. 100 (Requer Servidor 4000)",
                    "rules": [
                        "Limite estrito de 20 tentativas de aprimoramento por ciclo.",
                        "Taxas fixas sem risco: 55% (+1 Estágio), 24% (+2 Estágios), 21% (+3 Estágios) e 0% de Falha.",
                        "Com 20 tentativas e saltos, atinge entre o Nível 20 e 50.",
                        "Salvar (100k Ouro) registra o nível alcançado para substituição.",
                        "Carregar (200k Ouro) restaura o nível salvo anteriormente.",
                        "Redefinir (200k Ouro) reinicia o ciclo com 20 tentativas para tentar uma nova sequência."
                    ]
                }

            max_lvl = max([l["level"] for l in compact_levels]) if compact_levels else 0

            artifacts_list.append({
                "id": aid,
                "category_id": r["CategoryId"],
                "name": disp_name,
                "category_name": r["categoria_nome"],
                "variant_name": r["variante_nome"],
                "type": int(r["Type"]),
                "type_label": "Transformação" if r["Type"] == "1" else "Original",
                "max_level": max_lvl,
                "levels_count": len(compact_levels),
                "enchant_limit": int(r["EnchantLimitCount"]) if r["EnchantLimitCount"] else None,
                "server_group": r["ServerServiceGroupId"] or "Geral",
                "contents_lock_id": r["ContentsLockId"],
                "unlock_text": r["desbloqueio_texto"] or ("Exige Olga Nv. 100" if r["Type"] == "1" else ""),
                "divergence": divergence,
                "transform_info": transform_info,
                "icon": icon_img,
                "art": art_img,
                "materials": list(materials_seen.values()),
                "milestones": milestones,
                "summary_effects": summary_effects,
                "levels": compact_levels
            })

artifacts_catalog = {
    "stats": {
        "total_artifacts": len(artifacts_list),
        "total_original": sum(1 for a in artifacts_list if a["type"] == 0),
        "total_transformation": sum(1 for a in artifacts_list if a["type"] == 1),
        "total_progression_records": sum(len(a["levels"]) for a in artifacts_list)
    },
    "artifacts": artifacts_list
}

with open(os.path.join(OUT_DIR, "artifacts.json"), "w", encoding="utf-8") as f:
    json.dump(artifacts_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Artifacts catalog ({len(artifacts_list)} artifacts, {artifacts_catalog['stats']['total_progression_records']} progression records).")

# ==========================================
# 18. BLOODLINE (LINHAGEM) CATALOG
# ==========================================
print("Processing Bloodline (Linhagem) catalog...")
bloodline_reports_dir = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/linhagem")
bloodline_dungeons_path = os.path.join(bloodline_reports_dir, "masmorras.csv")
bloodline_quests_path = os.path.join(bloodline_reports_dir, "missoes.csv")
bloodline_transforms_path = os.path.join(bloodline_reports_dir, "transformacoes.csv")

skills_by_id = {s["id"]: s for s in skills_catalog}

boss_map = {
    "80010": {"name": "Ra'av", "img": "assets/monsters/raab_01.png", "title": "Herdeiro Antigo"},
    "80020": {"name": "Luciferre", "img": "assets/monsters/luciferre_01.png", "title": "Senhor da Baía Negra"},
    "80030": {"name": "Malum", "img": "assets/monsters/hermitfiend_02.png", "title": "Eremita Caído"},
    "80040": {"name": "Innocentius", "img": "assets/monsters/innocentius_01.png", "title": "Bispo Corrompido"},
    "80050": {"name": "Massacre", "img": "assets/monsters/massacre_01.png", "title": "Carrasco do Bosque"},
    "80060": {"name": "Lillai", "img": "assets/monsters/relicbeast_01.png", "title": "Besta da Relíquia"},
    "80070": {"name": "Draco", "img": "assets/monsters/draco_01.png", "title": "Dragão de Alabastro"},
    "80080": {"name": "Uigilias", "img": "assets/monsters/uigilias_01.png", "title": "Vigia das Ruínas"},
    "80090": {"name": "Carmon", "img": "assets/monsters/demonexecutioner_04.png", "title": "Executor Abissal"},
    "80100": {"name": "Philippos", "img": "assets/monsters/philipposboss.png", "title": "Guardião da Terra Sagrada"}
}

class_names_map = {
    "1": {"name": "Mago Sombrio (Dark Mage)", "icon": "assets/classes/darkmage_icon.png"},
    "2": {"name": "Ceifador (Reaper)", "icon": "assets/classes/reaper_icon.png"},
    "3": {"name": "Atirador (Gunner)", "icon": "assets/classes/gunner_icon.png"},
    "4": {"name": "Espadachim (SwordMan)", "icon": "assets/classes/swordman_icon.png"},
    "5": {"name": "Lutador (Fighter)", "icon": "assets/classes/fighter_icon.png"}
}

bloodline_chapters = []

if os.path.exists(bloodline_dungeons_path) and os.path.exists(bloodline_quests_path) and os.path.exists(bloodline_transforms_path):
    with open(bloodline_dungeons_path, "r", encoding="utf-8-sig") as f:
        dungeons_raw = list(csv.DictReader(f))
    with open(bloodline_quests_path, "r", encoding="utf-8-sig") as f:
        quests_raw = {r["ContentsLockInfoId"]: r for r in csv.DictReader(f)}
    with open(bloodline_transforms_path, "r", encoding="utf-8-sig") as f:
        transforms_raw = {r["Id"]: r for r in csv.DictReader(f)}

    for idx, d in enumerate(dungeons_raw, 1):
        did = d["Id"]
        param = json.loads(d["AdditionalInfoParam"]) if d.get("AdditionalInfoParam") else {}
        ct_map = {}
        time_limit = 900
        for k in param.get("key", []):
            if "ClassTransform" in k:
                ct_map = k["ClassTransform"]
            if "dungeonLimitTime" in k:
                time_limit = int(k["dungeonLimitTime"])

        q = quests_raw.get(did, {})
        rewards_raw = json.loads(q.get("recompensas_json", "{}"))
        rewards_compact = []
        for gid, items in rewards_raw.items():
            for it in items:
                itype = it.get("Type")
                iparam = it.get("Param", "")
                count = int(it.get("MinCount", 1))
                name = it.get("item_nome", "")
                icon = "assets/items/materials_potion_01.png"
                cat = "item"

                if itype == "2":
                    name = "EXP"
                    cat = "exp"
                    icon = "assets/items/materials_potion_01.png"
                elif itype == "0" and iparam == "Gold":
                    name = "Ouro"
                    cat = "gold"
                    icon = "assets/items/asset_gold.png"
                elif iparam == "80000000":
                    name = "Moeda da Eternidade"
                    cat = "eternity_coin"
                    icon = "assets/items/itembox_coin_02.png"
                elif iparam == "100000000":
                    name = "Trindade"
                    cat = "trinity"
                    icon = "assets/items/etc_contentscoin_01.png"
                elif "Livro de Habilidade" in name:
                    name = name.replace("{ReplaceString1}", "").strip()
                    cat = "skill_book"
                    icon = "assets/items/skillbook_darkmage_02.png"
                elif "Fragmento de Memória" in name:
                    cat = "memory_fragment"
                    icon = "assets/bloodline/mat_bloodline.png"
                elif iparam in all_processed_items:
                    icon = all_processed_items[iparam].get("icon_img") or icon
                    name = all_processed_items[iparam].get("name") or name

                rewards_compact.append({
                    "name": name,
                    "count": count,
                    "count_display": f"{count:,}",
                    "category": cat,
                    "icon": icon,
                    "rate": float(it.get("Rate", 1))
                })

        t_list = []
        for cid in ["1", "2", "3", "4", "5"]:
            tid = ct_map.get(cid)
            if not tid or tid not in transforms_raw:
                continue
            tr = transforms_raw[tid]
            l10n = json.loads(tr.get("nome_localizado_json", "{}"))
            skills_raw = json.loads(tr.get("habilidades_json", "[]"))
            skills_compact = []

            for s in skills_raw:
                sid = s.get("Id")
                catalog_skill = skills_by_id.get(sid, {})
                sname = catalog_skill.get("name") or (skill_names.get(sid, {}).get("Name") if isinstance(skill_names.get(sid), dict) else (skill_names.get(sid) or f"Habilidade {sid}"))
                desc = catalog_skill.get("description", "")
                eff_desc = catalog_skill.get("effect_description", "")
                icon_img = catalog_skill.get("icon_img") or "assets/classes/logo.png"

                cd = catalog_skill.get("cooldown") or f"{float(s.get('MaxCoolTime', 0) or 0) / 1000.0:.1f}s"
                dist = catalog_skill.get("range") or f"{float(s.get('MaxCastDistance', 0) or 0) / 100.0:.1f}m"
                mp = catalog_skill.get("mp_cost") or (f"{s.get('MpMin')} MP" if s.get("MpMin") and s.get("MpMin") != "0" else "Sem Custo")
                is_deadly = s.get("Category") == "5"

                skills_compact.append({
                    "id": sid,
                    "name": sname,
                    "description": desc,
                    "effect_description": eff_desc,
                    "icon": icon_img,
                    "cooldown": cd,
                    "range": dist,
                    "mp": mp,
                    "category": "Mortal / Fatal" if is_deadly else ("Esquiva" if s.get("Category") == "3" else ("Ataque Básico" if s.get("Category") == "0" else "Ativa")),
                    "is_deadly": is_deadly
                })

            c_info = class_names_map.get(cid, {"name": f"Classe {cid}", "icon": "assets/classes/logo.png"})
            t_list.append({
                "class_id": int(cid),
                "class_name": c_info["name"],
                "class_icon": c_info["icon"],
                "transform_id": tid,
                "title": l10n.get("Title", "Elottarviziano"),
                "name": l10n.get("Name", ""),
                "full_name": f"{l10n.get('Title', 'Elottarviziano')} - {l10n.get('Name', '')}",
                "resource": tr.get("Resource", ""),
                "gender": "Feminino" if tr.get("GenderType") == "1" else "Masculino",
                "move_speed": int(tr.get("MoveSpeed", 500)),
                "body_radius": int(tr.get("BodyRadius", 50)),
                "character_operation_add_rate": int(tr.get("CharacterOperationAddRate", 25)),
                "skills": skills_compact
            })

        boss_data = boss_map.get(did, {"name": "Chefe da Masmorra", "img": "assets/monsters/raab_01.png", "title": "Chefe de Linhagem"})

        bloodline_chapters.append({
            "chapter": idx,
            "dungeon_id": did,
            "name": d["nome_pt"],
            "quest_id": q.get("Id", ""),
            "quest_name": q.get("nome_pt", ""),
            "prerequisite_quest_id": q.get("RequireCompleteQuestInfoId", ""),
            "prerequisite_quest_name": q.get("missao_previa_nome", ""),
            "time_limit": time_limit,
            "time_limit_minutes": round(time_limit / 60),
            "restricted_level": int(d.get("RestrictedLevel", 1) or 1),
            "recommended_level": int(d.get("RecommendedLevel", 20) or 20),
            "boss": boss_data,
            "rewards": rewards_compact,
            "transformations": t_list,
            "rules": [
                "Controle de Elottarviziano com conjunto próprio de habilidades ativas e mortais.",
                "Aplicação configurada de 25% dos atributos do seu personagem principal.",
                "Limite de tempo de 15 minutos (900 segundos).",
                "Entrada individual: saída automática do grupo e indisponível em emparelhamento.",
                "Sistema de aviso contra inatividade e expulsão automática por AFK.",
                "Progressão narrativa única: liberada após completar missões específicas da campanha principal."
            ]
        })

bloodline_catalog = {
    "stats": {
        "total_dungeons": len(bloodline_chapters),
        "total_transformations": sum(len(c["transformations"]) for c in bloodline_chapters),
        "attribute_transfer_rate": "25%",
        "time_limit_default": "15 minutos (900s)",
        "unique_bosses": len(set(c["boss"]["name"] for c in bloodline_chapters))
    },
    "chapters": bloodline_chapters
}

with open(os.path.join(OUT_DIR, "bloodline.json"), "w", encoding="utf-8") as f:
    json.dump(bloodline_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Bloodline catalog ({len(bloodline_chapters)} chapters, {bloodline_catalog['stats']['total_transformations']} transformations).")

# ==========================================
# 19. BLOOD REALM EVOLUTION (MATRIX) CATALOG
# ==========================================
print("Processing Blood Realm Evolution (Matrix) catalog...")
matrix_reports_dir = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/reino-de-sangue")
matrix_quadros_path = os.path.join(matrix_reports_dir, "quadros.csv")
matrix_fileiras_path = os.path.join(matrix_reports_dir, "fileiras.csv")
matrix_celulas_path = os.path.join(matrix_reports_dir, "celulas.csv")
matrix_bonus_path = os.path.join(matrix_reports_dir, "bonus_colunas.csv")

STAT_NAME_MAP_MATRIX = {
    "AttackPower": "Poder de Ataque",
    "AttackPowerNormalAttack": "Poder de Ataque Básico",
    "AttackPowerReduction": "Redução do Poder de Ataque Inimigo",
    "AttackPowerReductionNormalAttack": "Redução de Ataque Básico Inimigo",
    "AttackPowerReductionSkill": "Redução de Ataque de Habilidade Inimigo",
    "AttackPowerSkill": "Poder de Ataque de Habilidade",
    "DamageMultiplierNormalAttack": "Multiplicador de Dano Básico",
    "DamageMultiplierSkill": "Multiplicador de Dano de Habilidade",
    "DamageReducerNormalAttack": "Redução de Dano Básico",
    "DamageReducerSkill": "Redução de Dano de Habilidade",
    "DamageReduction": "Redução de Dano",
    "DamageReductionCritical": "Redução de Dano Crítico",
    "DamageReductionNormalAttack": "Redução de Dano Básico",
    "DamageReductionSkill": "Redução de Dano de Habilidade",
    "DamageValue": "Dano Adicional",
    "DamageValueCritical": "Dano Crítico",
    "DamageValueNormalAttack": "Dano Básico",
    "DamageValueSkill": "Dano de Habilidade",
    "DodgeValue": "Evasão",
    "HitValue": "Precisão",
    "HitValueNormalAttack": "Precisão de Ataque Básico",
    "HitValueSkill": "Precisão de Habilidade",
    "IgnoreCriticalDamageMultiplier": "Ignorar Multiplicador Crítico",
    "MaxHp": "HP Máximo"
}

bloodrealm_boards = []

if os.path.exists(matrix_quadros_path) and os.path.exists(matrix_fileiras_path) and os.path.exists(matrix_celulas_path):
    with open(matrix_quadros_path, "r", encoding="utf-8-sig") as f:
        quadros_raw = list(csv.DictReader(f))
    with open(matrix_fileiras_path, "r", encoding="utf-8-sig") as f:
        fileiras_raw = list(csv.DictReader(f))
    with open(matrix_celulas_path, "r", encoding="utf-8-sig") as f:
        celulas_raw = list(csv.DictReader(f))
    bonus_raw = []
    if os.path.exists(matrix_bonus_path):
        with open(matrix_bonus_path, "r", encoding="utf-8-sig") as f:
            bonus_raw = list(csv.DictReader(f))

    rows_by_matrix = {}
    for r in fileiras_raw:
        mid = r["MatrixId"]
        rows_by_matrix.setdefault(mid, []).append(r)

    cells_by_row = {}
    for c in celulas_raw:
        rid = c.get("MatrixRowId")
        if rid:
            cells_by_row.setdefault(rid, []).append(c)

    bonus_by_matrix = {}
    for b in bonus_raw:
        mid = b.get("MatrixId")
        if mid:
            bonus_by_matrix.setdefault(mid, []).append(b)

    boards_map = {}
    for q in quadros_raw:
        qid = q["Id"]
        if qid not in boards_map or q.get("SaveCostGroupId"):
            boards_map[qid] = q

    for qid, q in boards_map.items():
        cat_name = q.get("categoria_nome", "Reino de Sangue")
        tab_name = q.get("aba_nome", "Geral")
        is_event = "Evento" in cat_name or bool(q.get("DateTimeSetting"))

        if is_event:
            cat_icon = "assets/matrix/matrix_event_tab01.png"
            mat_icon = "assets/matrix/mat_stone_03.png"
        elif "2" in cat_name:
            cat_icon = "assets/matrix/matrix_tab02.png"
            mat_icon = "assets/matrix/mat_stone_02.png"
        else:
            cat_icon = "assets/matrix/matrix_tab01.png"
            mat_icon = "assets/matrix/mat_stone_01.png"

        q_rows = rows_by_matrix.get(qid, [])
        q_rows.sort(key=lambda r: int(r.get("RowIndex", 0) or 0))

        rows_data = []
        mat_name = "Pedra da Evolução"
        mat_cost = 10
        max_rerolls_per_row = 2
        init_dia = 100
        init_item = "Bilhete de Redefinição de Evolução do Reino de Sangue"

        for r in q_rows:
            rid = r["Id"]
            mat_name = r.get("material_nome") or mat_name
            mat_cost = int(r.get("RerollCostItemCount", 10) or 10)
            max_rerolls_per_row = int(r.get("MaxRerollCount", 2) or 2)
            init_dia = int(r.get("InitDiaCount", 100) or 100)
            init_item = r.get("item_reset_nome") or init_item

            r_cells = cells_by_row.get(rid, [])
            r_cells.sort(key=lambda c: int(c.get("ColumnIndex", 0) or 0))

            total_rate = sum(int(c.get("SelectRate", 0) or 0) for c in r_cells) or 10000

            cells_data = []
            for c in r_cells:
                rate_raw = int(c.get("SelectRate", 0) or 0)
                rate_pct = round((rate_raw / total_rate) * 100, 1)
                niveis_raw = json.loads(c.get("niveis_json", "[]"))
                levels_data = []
                for nv in niveis_raw:
                    effs_raw = json.loads(nv.get("efeitos_json", "[]"))
                    effects_data = []
                    for eff in effs_raw:
                        t = eff.get("tipo_nome", "")
                        val = float(eff.get("Min", 0) or 0)
                        t_name = STAT_NAME_MAP_MATRIX.get(t, STAT_NAME_MAP.get(t, t))
                        v_disp = f"+{val/100:.1f}%" if "Multiplier" in t else f"+{int(val):,}"
                        effects_data.append({"key": t, "name": t_name, "val": v_disp, "raw_val": val})
                    levels_data.append({
                        "level": int(nv.get("Level", 1)),
                        "effects": effects_data
                    })

                cells_data.append({
                    "cell_id": c["Id"],
                    "column_index": int(c.get("ColumnIndex", 1) or 1),
                    "select_rate_raw": rate_raw,
                    "select_rate_pct": rate_pct,
                    "max_level": max([l["level"] for l in levels_data]) if levels_data else 1,
                    "levels": levels_data
                })

            rows_data.append({
                "row_id": rid,
                "row_index": int(r.get("RowIndex", 1) or 1),
                "reroll_cost_count": mat_cost,
                "max_rerolls": max_rerolls_per_row,
                "init_dia_count": init_dia,
                "init_item_count": int(r.get("InitItemCount", 1) or 1),
                "cells": cells_data
            })

        q_bonus = bonus_by_matrix.get(qid, [])
        q_bonus.sort(key=lambda b: int(b.get("ColumnIndex", 0) or 0))
        bonus_data = []
        for b in q_bonus:
            col_idx = int(b.get("ColumnIndex", 1) or 1)
            niveis_raw = json.loads(b.get("niveis_json", "[]"))
            levels_data = []
            for nv in niveis_raw:
                effs_raw = json.loads(nv.get("efeitos_json", "[]"))
                effects_data = []
                for eff in effs_raw:
                    t = eff.get("tipo_nome", "")
                    val = float(eff.get("Min", 0) or 0)
                    t_name = STAT_NAME_MAP_MATRIX.get(t, STAT_NAME_MAP.get(t, t))
                    v_disp = f"+{val/100:.1f}%" if "Multiplier" in t else f"+{int(val):,}"
                    effects_data.append({"key": t, "name": t_name, "val": v_disp, "raw_val": val})
                levels_data.append({
                    "level": int(nv.get("Level", 1)),
                    "effects": effects_data
                })
            bonus_data.append({
                "column_index": col_idx,
                "cell_id": b.get("CellId", ""),
                "levels": levels_data
            })

        save_cost = "70.000 Ouro" if q.get("SaveCostGroupId") else None
        load_cost = "100.000 Ouro" if q.get("LoadCostGroupId") else None

        bloodrealm_boards.append({
            "id": qid,
            "name": q["nome_pt"],
            "category_name": cat_name,
            "category_code": 3 if is_event else (2 if "2" in cat_name else 1),
            "tab_name": tab_name,
            "category_icon": cat_icon,
            "material_icon": mat_icon,
            "material_name": mat_name,
            "material_cost_per_attempt": mat_cost,
            "max_rerolls_per_row": max_rerolls_per_row,
            "reset_dia_cost": init_dia,
            "reset_item_name": init_item,
            "rows_count": int(q.get("RowCount", 3) or 3),
            "columns_count": int(q.get("ColumnCount", 3) or 3),
            "dimensions": f"{q.get('RowCount', 3)}×{q.get('ColumnCount', 3)}",
            "is_temporary": is_event,
            "date_setting": q.get("DateTimeSetting", ""),
            "has_save_load": bool(save_cost),
            "save_cost": save_cost,
            "load_cost": load_cost,
            "rows": rows_data,
            "column_bonuses": bonus_data
        })

bloodrealm_catalog = {
    "stats": {
        "total_boards": len(bloodrealm_boards),
        "total_rows": sum(len(b["rows"]) for b in bloodrealm_boards),
        "total_cells": sum(sum(len(r["cells"]) for r in b["rows"]) for b in bloodrealm_boards),
        "total_column_bonuses": sum(len(b["column_bonuses"]) for b in bloodrealm_boards),
        "categories": ["Reino de Sangue 1", "Reino de Sangue 2", "Reino de Sangue do Evento"]
    },
    "boards": bloodrealm_boards
}

with open(os.path.join(OUT_DIR, "bloodrealm.json"), "w", encoding="utf-8") as f:
    json.dump(bloodrealm_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Blood Realm Evolution catalog ({len(bloodrealm_boards)} boards, {bloodrealm_catalog['stats']['total_cells']} cells).")

# ==========================================
# 20. ITEM REFINEMENT (REFINAMENTO COM TRINDADE)
# ==========================================
print("Processing Item Refinement catalog...")
REFINEMENT_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/refinamento")
refinement_rules_path = os.path.join(REFINEMENT_REPORTS_DIR, "regras.csv")
refinement_effects_path = os.path.join(REFINEMENT_REPORTS_DIR, "efeitos_possiveis.csv")

EQUIP_TYPE_NAMES = {
    "BloodSword": "Espada de Sangue",
    "Gun": "Arma de Fogo",
    "Orb": "Orbe",
    "Scythe": "Foice",
    "Tonfa": "Tonfa",
    "Armor": "Armadura",
    "Boots": "Botas",
    "Gloves": "Luvas",
    "Helmet": "Elmo",
    "Belt": "Cinto",
    "Bracelet": "Bracelete",
    "Choker": "Gargantilha",
    "Crest": "Brasão",
    "Earring": "Brinco",
    "Necklace": "Colar",
    "Ring": "Anel",
    "Diary": "Diário",
    "Goblet": "Cálice",
    "Mask": "Máscara",
    "MusicBox": "Caixa de Música",
    "Pen": "Caneta",
    "PocketWatch": "Relógio de Bolso",
    "Ribbon": "Fita",
    "Perfume": "Perfume"
}

CATEGORY_NAMES = {
    "1": "Armas",
    "2": "Armaduras",
    "3": "Acessórios",
    "4": "Relíquias Especiais"
}

RARITY_NAMES = {
    "Rare": "Raro",
    "Epic": "Heroico",
    "Legendary": "Lendário",
    "Mythic": "Mítico",
    "Unique": "Especial"
}

GRADE_INFO = {
    0: {"label": "Comum / Básico", "icon": "assets/refinement/grade_none.png", "color": "#94a3b8"},
    1: {"label": "Intermediário", "icon": "assets/refinement/grade_mid.png", "color": "#38bdf8"},
    2: {"label": "Supremo", "icon": "assets/refinement/grade_max.png", "color": "#f59e0b"}
}

available_item_files = item_pngs

def get_refinement_icon(cat, eq_type, rar):
    rar_key = rar.lower()
    eq_lower = eq_type.lower()
    if cat == "1":
        fname = f"weapon_{eq_lower}_{rar_key}_01.png"
        if fname in available_item_files:
            return f"assets/items/{fname}"
        for f in available_item_files:
            if f.startswith(f"weapon_{eq_lower}") and rar_key in f:
                return f"assets/items/{f}"
        return f"assets/items/weapon_{eq_lower}_common_01.png"
    elif cat == "2":
        fname = f"armor_{eq_lower}_{rar_key}_01.png"
        if fname in available_item_files:
            return f"assets/items/{fname}"
        for f in available_item_files:
            if f.startswith(f"armor_{eq_lower}") and rar_key in f:
                return f"assets/items/{f}"
        return f"assets/items/armor_{eq_lower}_common_01.png"
    elif cat == "3":
        fname = f"accessory_{eq_lower}_{rar_key}_01.png"
        if fname in available_item_files:
            return f"assets/items/{fname}"
        for f in available_item_files:
            if f.startswith(f"accessory_{eq_lower}") and rar_key in f:
                return f"assets/items/{f}"
        return f"assets/items/accessory_{eq_lower}_common_01.png"
    elif cat == "4":
        for f in available_item_files:
            if f"enchanted{eq_lower}" in f:
                return f"assets/items/{f}"
        for f in available_item_files:
            if eq_lower in f and ("itembox" in f or "objet" in f):
                return f"assets/items/{f}"
        return "assets/refinement/flat_refine.png"
    return "assets/refinement/flat_refine.png"

refinement_groups = defaultdict(list)
if os.path.exists(refinement_effects_path):
    with open(refinement_effects_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            gid = r["GroupId"]
            rar_val = int(r["OperationRarity"])
            rate_raw = int(r["SelectedRate"])
            rate_pct = round(rate_raw / 1000.0, 3)
            min_v = int(r["Min"])
            max_v = int(r["Max"])
            t_name = r["tipo_nome"]
            disp_name = STAT_NAME_MAP.get(t_name, t_name)
            val_disp = f"+{min_v}%" if "Multiplier" in t_name or "Rate" in t_name else (f"+{min_v}" if min_v == max_v else f"+{min_v}~{max_v}")
            g_info = GRADE_INFO.get(rar_val, GRADE_INFO[0])
            refinement_groups[gid].append({
                "id": r["Id"],
                "group_id": gid,
                "type_code": r["Type"],
                "type_name": t_name,
                "name": disp_name,
                "rarity": rar_val,
                "rarity_label": g_info["label"],
                "rarity_icon": g_info["icon"],
                "rarity_color": g_info["color"],
                "min": min_v,
                "max": max_v,
                "val_display": val_disp,
                "operation_level": int(r["OperationLevel"]),
                "rate_raw": rate_raw,
                "rate_pct": rate_pct,
                "rate_display": f"{rate_pct:.3f}%"
            })

refinement_rules = []
if os.path.exists(refinement_rules_path):
    with open(refinement_rules_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cid = r["EquipmentCategory"]
            cname = CATEGORY_NAMES.get(cid, f"Categoria {cid}")
            eq_type = r["tipo_equipamento"]
            eq_name = EQUIP_TYPE_NAMES.get(eq_type, eq_type)
            rar = r["raridade_nome"]
            rar_name = RARITY_NAMES.get(rar, rar)
            gid = r["OperationGroupId1"]
            slots = int(r["espacos"])
            tri_cost = int(r["RefinementMarerialCount"] or 0)
            gold_cost = int(r["NeedGold"] or 0)
            save_val = int(r["OperationSaveCostValue"] or 0)
            load_val = int(r["OperationLoadCostValue"] or 0)
            load_item_name = r["item_carregar_nome"] or ("Ouro" if r["OperationLoadCostType"] == "1" else "Pedra de Restauração de Refinamento")
            load_icon = "assets/items/asset_gold.png" if r["OperationLoadCostType"] == "1" else "assets/refinement/refinement_stone.png"
            load_formatted = f"{load_val:,} Ouro".replace(",", ".") if r["OperationLoadCostType"] == "1" else f"{load_val}x {load_item_name}"
            save_formatted = f"{save_val:,} Ouro".replace(",", ".")
            icon = get_refinement_icon(cid, eq_type, rar)

            refinement_rules.append({
                "id": int(r["Id"]),
                "category_id": int(cid),
                "category_name": cname,
                "equipment_type": eq_type,
                "equipment_type_name": eq_name,
                "rarity": rar,
                "rarity_name": rar_name,
                "rarity_code": int(r["EquipmentRarity"]),
                "slots": slots,
                "trinity_cost": tri_cost,
                "trinity_icon": "assets/items/materials_craftmaterial_01.png",
                "gold_cost": gold_cost,
                "gold_cost_formatted": f"{gold_cost:,} Ouro".replace(",", "."),
                "save_cost_value": save_val,
                "save_cost_formatted": save_formatted,
                "load_cost_value": load_val,
                "load_cost_name": load_item_name,
                "load_cost_icon": load_icon,
                "load_cost_formatted": load_formatted,
                "icon": icon,
                "group_id": gid,
                "effects_count": len(refinement_groups.get(gid, []))
            })

cost_matrix = [
    {
        "category": "Armas",
        "category_id": 1,
        "types": ["Espada de Sangue", "Arma de Fogo", "Orbe", "Foice", "Tonfa"],
        "rows": [
            {"rarity": "Raro", "slots": 2, "trinity": 10, "gold": "15.000", "save": "30.000 Ouro", "load": "150.000 Ouro"},
            {"rarity": "Heroico", "slots": 3, "trinity": 30, "gold": "15.000", "save": "90.000 Ouro", "load": "5x Pedra de Restauração"},
            {"rarity": "Lendário", "slots": 4, "trinity": 150, "gold": "15.000", "save": "450.000 Ouro", "load": "25x Pedra de Restauração"},
            {"rarity": "Mítico", "slots": 4, "trinity": 750, "gold": "15.000", "save": "2.250.000 Ouro", "load": "125x Pedra de Restauração"}
        ]
    },
    {
        "category": "Armaduras",
        "category_id": 2,
        "types": ["Elmo", "Armadura", "Luvas", "Botas"],
        "rows": [
            {"rarity": "Raro", "slots": 2, "trinity": 3, "gold": "3.000", "save": "30.000 Ouro", "load": "150.000 Ouro"},
            {"rarity": "Heroico", "slots": 3, "trinity": 10, "gold": "3.000", "save": "90.000 Ouro", "load": "5x Pedra de Restauração"},
            {"rarity": "Lendário", "slots": 4, "trinity": 50, "gold": "3.000", "save": "450.000 Ouro", "load": "25x Pedra de Restauração"},
            {"rarity": "Mítico", "slots": 4, "trinity": 250, "gold": "3.000", "save": "2.250.000 Ouro", "load": "125x Pedra de Restauração"}
        ]
    },
    {
        "category": "Acessórios",
        "category_id": 3,
        "types": ["Cinto", "Brasão", "Colar", "Brinco", "Bracelete", "Anel", "Gargantilha"],
        "rows": [
            {"rarity": "Raro", "slots": 2, "trinity": 15, "gold": "9.000", "save": "30.000 Ouro", "load": "150.000 Ouro"},
            {"rarity": "Heroico", "slots": 3, "trinity": 20, "gold": "9.000", "save": "90.000 Ouro", "load": "5x Pedra de Restauração"},
            {"rarity": "Lendário", "slots": 4, "trinity": 100, "gold": "9.000", "save": "450.000 Ouro", "load": "25x Pedra de Restauração"},
            {"rarity": "Mítico", "slots": 4, "trinity": 500, "gold": "9.000", "save": "2.250.000 Ouro", "load": "125x Pedra de Restauração"}
        ]
    },
    {
        "category": "Relíquias Especiais",
        "category_id": 4,
        "types": ["Perfume", "Cálice", "Caneta", "Relógio de Bolso", "Diário", "Caixa de Música", "Máscara"],
        "rows": [
            {"rarity": "Especial (Unique)", "slots": 4, "trinity": 15, "gold": "9.000", "save": "80.000 Ouro", "load": "5x Pedra de Restauração"}
        ]
    }
]

refinement_catalog = {
    "stats": {
        "total_rules": len(refinement_rules),
        "total_groups": len(refinement_groups),
        "total_effects": sum(len(g) for g in refinement_groups.values()),
        "categories": ["Armas", "Armaduras", "Acessórios", "Relíquias Especiais"],
        "rarities": ["Raro", "Heroico", "Lendário", "Mítico", "Especial"]
    },
    "cost_matrix": cost_matrix,
    "rules": refinement_rules,
    "groups": refinement_groups
}

with open(os.path.join(OUT_DIR, "refinement.json"), "w", encoding="utf-8") as f:
    json.dump(refinement_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Item Refinement catalog ({len(refinement_rules)} rules, {refinement_catalog['stats']['total_effects']} subattributes across {len(refinement_groups)} groups).")

# ==========================================
# 21. LIFE TREE (ÁRVORE DA VIDA) & SEPHIRAS CATALOG
# ==========================================
print("Processing Life Tree & Sephiras catalog...")
SEPHIRA_REPORTS_DIR = os.path.join(BASE_DIR, "analysis/versions/2026-10-31/reports/sefira-arvore-da-vida")
sefiras_csv_path = os.path.join(SEPHIRA_REPORTS_DIR, "sefiras.csv")
espacos_csv_path = os.path.join(SEPHIRA_REPORTS_DIR, "espacos_arvore.csv")
elos_csv_path = os.path.join(SEPHIRA_REPORTS_DIR, "elos_e_conjuntos.csv")
fusoes_csv_path = os.path.join(SEPHIRA_REPORTS_DIR, "fusoes.csv")

FORMAT_NAMES = {
    0: "Achillute",
    1: "Bria",
    2: "Yechira"
}

FORMAT_ICONS = {
    0: "assets/lifetree/type_a_achillute.png",
    1: "assets/lifetree/type_b_bria.png",
    2: "assets/lifetree/type_c_yechira.png"
}

FORMAT_UNLOCKS = {
    0: {"level": 48, "lock_id": "111112", "desc": "Desbloqueia no Nv. 48"},
    1: {"level": 60, "lock_id": "111126", "desc": "Desbloqueia no Nv. 60"},
    2: {"level": 70, "lock_id": "111127", "desc": "Desbloqueia no Nv. 70"}
}

SYMBOL_NAMES = {
    1: "Alfa",
    2: "Sigma",
    3: "Teta",
    4: "Capa"
}

SYMBOL_ICONS = {
    1: "assets/lifetree/symbol_alpha.png",
    2: "assets/lifetree/symbol_sigma.png",
    3: "assets/lifetree/symbol_theta.png",
    4: "assets/lifetree/symbol_kappa.png"
}

RARITY_ORDER = ["Comum", "Incomum", "Raro", "Heroico", "Lendário", "Mítico"]
RARITY_COLORS = {
    0: "#94a3b8",
    1: "#22c55e",
    2: "#3b82f6",
    3: "#a855f7",
    4: "#eab308",
    5: "#ef4444"
}

SEPHIRA_ICON_MAP = {
    (0, 1): "assets/items/sephira_01.png",
    (0, 2): "assets/items/sephira_02.png",
    (0, 3): "assets/items/sephira_03.png",
    (0, 4): "assets/items/sephira_04.png",
    (1, 1): "assets/items/sephira_11.png",
    (1, 2): "assets/items/sephira_12.png",
    (1, 3): "assets/items/sephira_13.png",
    (1, 4): "assets/items/sephira_14.png",
    (2, 1): "assets/items/sephira_21.png",
    (2, 2): "assets/items/sephira_22.png",
    (2, 3): "assets/items/sephira_23.png",
    (2, 4): "assets/items/sephira_24.png",
}

# 1. Tree Slots (10)
tree_slots = []
if os.path.exists(espacos_csv_path):
    with open(espacos_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            stype = int(r["SephiraType"])
            slot_id = int(r["Id"])
            uinfo = FORMAT_UNLOCKS.get(stype, {"level": 1, "lock_id": "", "desc": ""})
            tree_slots.append({
                "slot_id": slot_id,
                "format_code": stype,
                "format_name": FORMAT_NAMES.get(stype, f"Formato {stype}"),
                "format_icon": FORMAT_ICONS.get(stype, "assets/lifetree/type_a_achillute.png"),
                "unlock_level": uinfo["level"],
                "unlock_desc": uinfo["desc"],
                "lock_id": uinfo["lock_id"]
            })

# 2. Sephiras (72)
sephiras_list = []
if os.path.exists(sefiras_csv_path):
    with open(sefiras_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            stype = int(r["SephiraType"])
            sym = int(r["SymbolType"])
            rar = int(r["raridade"])
            cost = int(r["CostValue"] or 0)
            effs_raw = json.loads(r["efeitos_json"])
            effs_compact = []
            for e in effs_raw:
                t = e.get("tipo_nome") or e.get("Type")
                val = float(e.get("Min", 0) or 0)
                t_name = STAT_NAME_MAP.get(t, t)
                v_disp = f"+{val/100:.1f}%" if "Multiplier" in t or "Rate" in t else f"+{int(val):,}"
                effs_compact.append({"key": t, "name": t_name, "val": v_disp, "raw_val": val})

            s_icon = SEPHIRA_ICON_MAP.get((stype, sym), "assets/items/flat_sephira.png")
            sephiras_list.append({
                "id": r["Id"],
                "name": r["nome"],
                "format_code": stype,
                "format_name": FORMAT_NAMES.get(stype, f"Formato {stype}"),
                "format_icon": FORMAT_ICONS.get(stype, "assets/lifetree/type_a_achillute.png"),
                "symbol_code": sym,
                "symbol_name": SYMBOL_NAMES.get(sym, f"Símbolo {sym}"),
                "symbol_icon": SYMBOL_ICONS.get(sym, "assets/lifetree/symbol_alpha.png"),
                "rarity_code": rar,
                "rarity_name": RARITY_ORDER[rar] if rar < len(RARITY_ORDER) else f"Grau {rar}",
                "rarity_color": RARITY_COLORS.get(rar, "#fff"),
                "cost_gold": cost,
                "cost_formatted": f"{cost:,} Ouro".replace(",", "."),
                "icon": s_icon,
                "effects": effs_compact,
                "effect_summary": ", ".join(f"{e['name']} {e['val']}" for e in effs_compact)
            })

# 3. Elos & Conjuntos (90)
bonuses_list = []
if os.path.exists(elos_csv_path):
    with open(elos_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            stype = int(r["SephiraType"])
            rar = int(r["Rarity"])
            is_elo = not bool(r.get("SymbolCount"))
            sym = int(r["SymbolType"]) if r.get("SymbolType") and not is_elo else None
            req_cnt = int(r["RegistrationCount"] or 3)
            
            effs_raw = json.loads(r["efeitos_json"])
            effs_compact = []
            for e in effs_raw:
                t = e.get("tipo_nome") or e.get("Type")
                val = float(e.get("Min", 0) or 0)
                t_name = STAT_NAME_MAP.get(t, t)
                v_disp = f"+{val/100:.1f}%" if "Multiplier" in t or "Rate" in t else f"+{int(val):,}"
                effs_compact.append({"key": t, "name": t_name, "val": v_disp, "raw_val": val})

            disp_name = r["nome"]
            if not disp_name:
                disp_name = f"Elo {FORMAT_NAMES.get(stype, '')} ({RARITY_ORDER[rar]})"

            bonuses_list.append({
                "id": r["Id"],
                "is_elo": is_elo,
                "type_label": "Elo de Formato" if is_elo else "Conjunto de Padrão",
                "format_code": stype,
                "format_name": FORMAT_NAMES.get(stype, f"Formato {stype}"),
                "format_icon": FORMAT_ICONS.get(stype, "assets/lifetree/type_a_achillute.png"),
                "symbol_code": sym,
                "symbol_name": SYMBOL_NAMES.get(sym) if sym else None,
                "symbol_icon": SYMBOL_ICONS.get(sym) if sym else None,
                "rarity_code": rar,
                "rarity_name": RARITY_ORDER[rar] if rar < len(RARITY_ORDER) else f"Grau {rar}",
                "rarity_color": RARITY_COLORS.get(rar, "#fff"),
                "req_count": req_cnt,
                "name": disp_name,
                "effects": effs_compact,
                "effect_summary": ", ".join(f"{e['name']} {e['val']}" for e in effs_compact)
            })

# 4. Fusions (15)
fusions_list = []
if os.path.exists(fusoes_csv_path):
    with open(fusoes_csv_path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            fid = r["Id"]
            rar = int(r["Rarity"])
            rate_raw = int(r["SuccessRate"])
            rate_pct = round(rate_raw / 100.0, 1)
            fail_pct = round(100.0 - rate_pct, 1)
            
            mats = json.loads(r["materiais_json"])
            sucs = json.loads(r["sucesso_json"])
            fals = json.loads(r["falha_json"])
            
            sample_name = mats[0]["item_nome"] if mats else ""
            if "Achillute" in sample_name or "Aquiluta" in sample_name:
                stype = 0
            elif "Bria" in sample_name:
                stype = 1
            else:
                stype = 2

            mats_compact = [{"id": m["ItemInfoId"], "name": m["item_nome"]} for m in mats]
            sucs_compact = [{"id": s["Param"], "name": s["item_nome"]} for s in sucs]
            fals_compact = [{"id": f["Param"], "name": f["item_nome"]} for f in fals]

            fusions_list.append({
                "id": fid,
                "format_code": stype,
                "format_name": FORMAT_NAMES.get(stype, f"Formato {stype}"),
                "format_icon": FORMAT_ICONS.get(stype, "assets/lifetree/type_a_achillute.png"),
                "input_rarity_code": rar,
                "input_rarity_name": RARITY_ORDER[rar] if rar < len(RARITY_ORDER) else f"Grau {rar}",
                "target_rarity_name": RARITY_ORDER[rar + 1] if rar + 1 < len(RARITY_ORDER) else "Superior",
                "material_count": int(r["MaterialCount"] or 4),
                "success_rate_raw": rate_raw,
                "success_rate_pct": rate_pct,
                "fail_rate_pct": fail_pct,
                "materials": mats_compact,
                "success_rewards": sucs_compact,
                "fail_rewards": fals_compact
            })

lifetree_catalog = {
    "stats": {
        "total_slots": len(tree_slots),
        "total_sephiras": len(sephiras_list),
        "total_bonus_rules": len(bonuses_list),
        "total_elos": sum(1 for b in bonuses_list if b["is_elo"]),
        "total_conjuntos": sum(1 for b in bonuses_list if not b["is_elo"]),
        "total_fusions": len(fusions_list),
        "formats": ["Achillute (3 Espaços)", "Bria (3 Espaços)", "Yechira (4 Espaços)"],
        "symbols": ["Alfa", "Sigma", "Teta", "Capa"],
        "rarities": RARITY_ORDER
    },
    "tree_slots": tree_slots,
    "sephiras": sephiras_list,
    "bonuses": bonuses_list,
    "fusions": fusions_list,
    "tree_bg": "assets/lifetree/bg_lifetree_web.webp"
}

with open(os.path.join(OUT_DIR, "lifetree.json"), "w", encoding="utf-8") as f:
    json.dump(lifetree_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Life Tree & Sephiras catalog ({len(sephiras_list)} sephiras, {len(bonuses_list)} elos/conjuntos, {len(fusions_list)} fusions).")

# ==========================================
# 22. BLOODSHAPES (HEMORFORMAS & METAMORFOSES) CATALOG
# ==========================================
print("Processing Bloodshapes (Hemorformas) catalog...")
ENUMS_PATH = os.path.join(BASE_DIR, "analysis/reports/builds/enums_binario.csv")

# 1. Enums
eop_map = {}
if os.path.exists(ENUMS_PATH):
    with open(ENUMS_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("enum") == "EOperationType":
                eop_map[row["valor"]] = row["nome"]

# 2. Operation Names
op_pt_map = {}
op_name_csv = os.path.join(L10N_DIR, "OperationType_Name.csv")
if os.path.exists(op_name_csv):
    with open(op_name_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            op_pt_map[row["OperationType"]] = row.get("Name", "")

# 3. Operation is percentage
op_is_percentage = {}
op_type_csv = os.path.join(CSV_DIR, "OperationType.csv")
if os.path.exists(op_type_csv):
    with open(op_type_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            op_is_percentage[row["OperationType"]] = (row.get("IsPercentage") == "1")

# 4. Static operations
static_ops = defaultdict(list)
static_ops_csv = os.path.join(CSV_DIR, "StaticOperation.csv")
if os.path.exists(static_ops_csv):
    with open(static_ops_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            static_ops[row["GroupId"]].append(row)

# 5. Skills & Skill Sets
skill_sets = defaultdict(list)
skill_set_csv = os.path.join(CSV_DIR, "SkillSet.csv")
if os.path.exists(skill_set_csv):
    with open(skill_set_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            skill_sets[row["GroupId"]].append(row["SkillInfoId"])

# 6. Costume limit break
costume_limit_breaks = defaultdict(list)
costume_lb_csv = os.path.join(CSV_DIR, "CostumeLimitBreak.csv")
if os.path.exists(costume_lb_csv):
    with open(costume_lb_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            costume_limit_breaks[row["CostumeId"]].append(row)

# 7. Costume & names
costume_names_map = {}
costume_name_csv = os.path.join(L10N_DIR, "Costume_Name.csv")
if os.path.exists(costume_name_csv):
    with open(costume_name_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            costume_names_map[row["Id"]] = row.get("Name", "")

costume_rows = load_csv_list(os.path.join(CSV_DIR, "Costume.csv"))

BLOODSHAPE_CLASSES = {
    "1": {"name": "Víbora", "icon": "assets/classes/darkmage_icon.png"},
    "2": {"name": "Ceifador", "icon": "assets/classes/reaper_icon.png"},
    "3": {"name": "Carnificina", "icon": "assets/classes/gunner_icon.png"},
    "4": {"name": "Manchado de Sangue", "icon": "assets/classes/swordman_icon.png"},
    "5": {"name": "Akasha", "icon": "assets/classes/fighter_icon.png"},
    "": {"name": "Universal", "icon": "assets/items/skill_bg_costume.png"}
}

def clean_skill_text(text):
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = re.sub(r"\{[0-9.]+%?\}%?", "", cleaned)
    return cleaned.strip()

def format_costume_ops(gid):
    if not gid or gid not in static_ops:
        return []
    res = []
    for op in static_ops[gid]:
        code = op["Type"]
        enum_name = eop_map.get(code, "")
        pt_name = op_pt_map.get(enum_name, enum_name or f"Stat_{code}")
        is_pct = op_is_percentage.get(code, False)
        val = float(op["Min"])
        if is_pct:
            val_str = f"+{val/100:.2f}%".replace(".00%", "%").replace(".0%", "%")
            val_num = val / 100.0
        else:
            val_str = f"+{int(val)}" if val.is_integer() else f"+{val}"
            val_num = val
        res.append({
            "code": code,
            "stat_name": pt_name,
            "enum_name": enum_name,
            "value_str": val_str,
            "value": val_num,
            "is_percentage": is_pct
        })
    return res

def find_bloodshape_icon(c):
    cid = c["Id"]
    res = c.get("Resource", "").lower()
    img = c.get("Img", "").lower()
    img_clean = img.replace("img_costumeicon_", "")
    candidates = [
        f"costumeitemicon_{res}_m.png",
        f"costumeitemicon_{res}_f.png",
        f"costumeitemicon_{res}.png",
        f"costumeitemicon_{img_clean}_m.png",
        f"costumeitemicon_{img_clean}_f.png",
        f"costumeitemicon_{img_clean}.png",
        f"costumeicon_{img_clean}.png",
        f"{img}.png",
        f"costumeitemicon_{cid}.png"
    ]
    for cand in candidates:
        if cand in item_pngs:
            return f"assets/items/{cand}"
    return "assets/items/skill_bg_costume.png"

bloodshapes_list = []
for c in costume_rows:
    cid = c["Id"]
    r_code = int(c.get("Rarity", 0))
    cls_id = c.get("OptimumClassInfoId", "")
    cls_meta = BLOODSHAPE_CLASSES.get(cls_id, BLOODSHAPE_CLASSES[""])
    r_meta = get_rarity_info(r_code)
    
    g1 = format_costume_ops(c.get("StaticOperationGroupId1"))
    g2 = format_costume_ops(c.get("StaticOperationGroupId2"))
    g3 = format_costume_ops(c.get("StaticOperationGroupId3"))
    
    # Exclusive skills
    ex_skills = []
    for sid in skill_sets.get(c.get("SkillSetGroupId", ""), []):
        srow = skill_names.get(sid, {})
        ex_skills.append({
            "id": sid,
            "name": srow.get("Name", f"Habilidade {sid}"),
            "desc": clean_skill_text(srow.get("Description", "")),
            "effect_desc": clean_skill_text(srow.get("EffectDescription", ""))
        })
        
    # Optimum skills
    opt_skills = []
    for sid in skill_sets.get(c.get("OptimumSkillSetGroupId", ""), []):
        srow = skill_names.get(sid, {})
        opt_skills.append({
            "id": sid,
            "name": srow.get("Name", f"Habilidade {sid}"),
            "desc": clean_skill_text(srow.get("Description", "")),
            "effect_desc": clean_skill_text(srow.get("EffectDescription", ""))
        })
        
    # Limit break steps
    lb_steps = []
    for lb in costume_limit_breaks.get(cid, []):
        lb_lvl = int(lb.get("LimitBreakLevel", 1))
        lb_steps.append({
            "level": lb_lvl,
            "resource": lb.get("Resource", ""),
            "stats_group_1": format_costume_ops(lb.get("StaticOperationGroupId1")),
            "stats_group_2": format_costume_ops(lb.get("StaticOperationGroupId2")),
            "stats_group_3": format_costume_ops(lb.get("StaticOperationGroupId3"))
        })
    lb_steps.sort(key=lambda x: x["level"])
    
    bloodshapes_list.append({
        "id": cid,
        "name": costume_names_map.get(cid, f"Hemorforma {cid}"),
        "rarity": r_code,
        "rarity_info": r_meta,
        "class_id": cls_id,
        "class_name": cls_meta["name"],
        "class_icon": cls_meta["icon"],
        "icon": find_bloodshape_icon(c),
        "item_info_id": c.get("ItemInfoId", ""),
        "tile_collection_group_id": c.get("TileCollectionGroupId", ""),
        "only_skin": c.get("OnlySkin", "0") == "1",
        "max_limit_break": int(c.get("MaxLimitBreak") or 0),
        "stats_group_1": g1,
        "stats_group_2": g2,
        "stats_group_3": g3,
        "all_stats": g1 + g2 + g3,
        "exclusive_skills": ex_skills,
        "optimum_skills": opt_skills,
        "limit_breaks": lb_steps,
        "raw": {
            "Category": c.get("Category"),
            "Order": c.get("Order"),
            "VisualEffectInfoId": c.get("VisualEffectInfoId"),
            "Resource": c.get("Resource")
        }
    })

# Sort bloodshapes by Rarity (descending) and Id (ascending)
bloodshapes_list.sort(key=lambda x: (-x["rarity"] if x["rarity"] != 101 else -3.5, int(x["id"])))

bloodshapes_catalog = {
    "stats": {
        "total": len(bloodshapes_list),
        "by_class": dict(Counter(b["class_name"] for b in bloodshapes_list)),
        "by_rarity": dict(Counter(b["rarity_info"]["name"] for b in bloodshapes_list)),
        "classes_order": ["Todas as Classes", "Víbora", "Ceifador", "Carnificina", "Manchado de Sangue", "Akasha", "Universal"],
        "rarities_order": ["Todas as Raridades", "Comum", "Incomum", "Raro", "Heroico", "Lendário", "Mítico", "Sazonal"]
    },
    "items": bloodshapes_list
}

with open(os.path.join(OUT_DIR, "bloodshapes.json"), "w", encoding="utf-8") as f:
    json.dump(bloodshapes_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Bloodshapes catalog ({len(bloodshapes_list)} bloodshapes across {len(bloodshapes_catalog['stats']['by_class'])} classes).")

# ==========================================
# 23. MOUNTS (VEHICLES / MONTARIAS) CATALOG
# ==========================================
print("Processing Mounts (Montarias / Veículos) catalog...")

vehicle_names_map = {}
vehicle_name_csv = os.path.join(L10N_DIR, "Vehicle_Name.csv")
if os.path.exists(vehicle_name_csv):
    with open(vehicle_name_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            vehicle_names_map[row["Id"]] = row.get("Name", "")

vehicle_limit_breaks = defaultdict(list)
vehicle_lb_csv = os.path.join(CSV_DIR, "VehicleLimitBreak.csv")
if os.path.exists(vehicle_lb_csv):
    with open(vehicle_lb_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            vehicle_limit_breaks[row["VehicleId"]].append(row)

vehicle_rows = load_csv_list(os.path.join(CSV_DIR, "Vehicle.csv"))

def find_vehicle_icon(v):
    vid = v["Id"]
    img = v.get("Img", "").lower().replace("img_vehicleicon_", "")
    bp = v.get("Blueprint", "").lower()
    candidates = [
        f"vehicleitemicon_{img}.png",
        f"vehicleitemicon_{bp}.png",
        f"vehicleicon_{img}.png",
        f"vehicleicon_{bp}.png",
        f"vehicle_{img}.png",
        f"vehicleitemicon_{vid}.png"
    ]
    for cand in candidates:
        if cand in item_pngs:
            return f"assets/items/{cand}"
    return "assets/items/vehicleitemicon_mountaingoat_01.png"

mounts_list = []
for v in vehicle_rows:
    vid = v["Id"]
    r_code = int(v.get("Rarity", 0))
    r_meta = get_rarity_info(r_code)
    
    g1 = format_costume_ops(v.get("StaticOperationGroupId1"))
    g2 = format_costume_ops(v.get("StaticOperationGroupId2"))
    g3 = format_costume_ops(v.get("StaticOperationGroupId3"))
    acq = format_costume_ops(v.get("AcquireOperationGroupId"))
    
    lb_steps = []
    for lb in vehicle_limit_breaks.get(vid, []):
        lb_steps.append({
            "level": int(lb.get("LimitBreakLevel", 1)),
            "move_speed": int(lb.get("MoveSpeed") or v.get("MoveSpeed") or 0),
            "stats_group_1": format_costume_ops(lb.get("StaticOperationGroupId1")),
            "stats_group_2": format_costume_ops(lb.get("StaticOperationGroupId2")),
            "stats_group_3": format_costume_ops(lb.get("StaticOperationGroupId3"))
        })
    lb_steps.sort(key=lambda x: x["level"])
    
    mounts_list.append({
        "id": vid,
        "name": vehicle_names_map.get(vid, f"Montaria {vid}"),
        "rarity": r_code,
        "rarity_info": r_meta,
        "move_speed": int(v.get("MoveSpeed") or 0),
        "icon": find_vehicle_icon(v),
        "tile_collection_group_id": v.get("TileCollectionGroupId", ""),
        "item_info_id": v.get("ItemInfoId", ""),
        "max_limit_break": int(v.get("MaxLimitBreak") or 0),
        "only_skin": v.get("OnlySkin", "0") == "1",
        "stats_group_1": g1,
        "stats_group_2": g2,
        "stats_group_3": g3,
        "acquire_stats": acq,
        "all_stats": g1 + g2 + g3,
        "limit_breaks": lb_steps
    })

mounts_list.sort(key=lambda x: (-x["rarity"] if x["rarity"] != 101 else -3.5, int(x["id"])))

mounts_catalog = {
    "stats": {
        "total": len(mounts_list),
        "by_rarity": dict(Counter(m["rarity_info"]["name"] for m in mounts_list)),
        "speed_range": {
            "min": min(m["move_speed"] for m in mounts_list),
            "max": max(m["move_speed"] for m in mounts_list)
        },
        "rarities_order": ["Todas as Raridades", "Comum", "Incomum", "Raro", "Heroico", "Lendário", "Mítico", "Sazonal"]
    },
    "items": mounts_list
}

with open(os.path.join(OUT_DIR, "mounts.json"), "w", encoding="utf-8") as f:
    json.dump(mounts_catalog, f, ensure_ascii=False)
print(f"  ✓ Processed Mounts catalog ({len(mounts_list)} mounts across {len(mounts_catalog['stats']['by_rarity'])} rarities).")

# ==========================================
# 8. BUNDLE GENERATION
# ==========================================
print("Writing bundle.js...")
bundle_path = os.path.join(OUT_DIR, "bundle.js")
bundle_data = {
    "classes": classes_data,
    "builds": builds_data,
    "skills": skills_catalog,
    "bosses": bosses_catalog,
    "regions": all_regions_list,
    "dungeons": dungeons_catalog,
    "items": curated_items,
    "quests": quests_catalog,
    "crafting": crafting_catalog,
    "modes": modes_catalog,
    "pvp": pvp_catalog,
    "enchantment": enchantment_catalog,
    "shops": shops_catalog,
    "codex": codex_catalog,
    "research": research_catalog,
    "portraits": portraits_catalog,
    "artifacts": artifacts_catalog,
    "bloodline": bloodline_catalog,
    "bloodrealm": bloodrealm_catalog,
    "refinement": refinement_catalog,
    "lifetree": lifetree_catalog,
    "bloodshapes": bloodshapes_catalog,
    "mounts": mounts_catalog,
    "constants": constants_dict,
    "faq": faq_catalog
}

with open(bundle_path, "w", encoding="utf-8") as f:
    f.write("window.VAMPIR_DATA = " + json.dumps(bundle_data, ensure_ascii=False) + ";\n")

print(f"Data builder completed! bundle.js size: {os.path.getsize(bundle_path) / 1024:.1f} KB")
