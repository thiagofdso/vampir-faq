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
from collections import defaultdict

BASE_DIR = "/home/thiagofdso/vampir"
CSV_DIR = os.path.join(BASE_DIR, "analysis/patch_chunk1/ProjectRED/Content/RED/Data/CSV")
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
# 3. SKILLS DATABASE
# ==========================================
print("Processing Skills...")
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
        "mobile": srow.get("Mobile", "0") == "1"
    })

with open(os.path.join(OUT_DIR, "skills.json"), "w", encoding="utf-8") as f:
    json.dump(skills_catalog, f, indent=2, ensure_ascii=False)

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
    if n.get("GradeType") in ["1", "2", "3"] and "invisible" not in n.get("Blueprint", "").lower()
]

# Deduplicate into unique combat profiles
groups = defaultdict(list)
for n in visible_npcs:
    nid = n.get("Id", "").strip()
    name_row = npc_names.get(nid, {})
    name = name_row.get("Name", "").strip() or n.get("NameEN", "").strip() or f"Monstro #{nid}"
    bp = n.get("Blueprint", "").strip()
    grade = n.get("GradeType", "0")

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
        title = "Chefe Mundial" if grade == "3" else ("Guardião de Masmorra" if grade == "2" else "Inimigo de Elite")

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
        "spawn_schedule": ", ".join(sched_list),
        "dungeons": dung_list,
        "skills": skills_data,
        "hp_raw": str(peak_tier["hp"]),
        "atk_raw": str(peak_tier["atk"]),
        "def_raw": str(peak_tier["def"]),
        "reward_preview": "Equipamentos Épicos/Lendários, Livros Raros, Essências de Sangue" if grade in ["2", "3"] else "Materiais de Refino, Fragmentos de Sangue"
    })

bosses_catalog.sort(key=lambda x: (int(x["grade_code"]), int(x["level"])), reverse=True)
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

items_by_cat = defaultdict(list)

for iid, irow in item_raw.items():
    iname_row = item_names.get(iid)
    if not iname_row:
        continue
    name = iname_row.get("Name", "").strip()
    desc = iname_row.get("Desc", "").strip()
    
    if not name or "2025-" in name or "2026-" in name:
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
    elif itype == "31":
        cat = "31"
        type_label = "Livro de Habilidade"
        clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
        clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
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

    if not item_img:
        item_img = "assets/logo.png"

    items_by_cat[cat].append({
        "id": iid,
        "name": clean_name,
        "desc": clean_desc if clean_desc else "Item de uso e progressão vampírica.",
        "type_code": itype,
        "category": cat,
        "type_name": type_label,
        "icon_img": item_img,
        "tier": tier if tier else "1",
        "rarity": rarity,
        "max_enchant": "+15 (Encantamento Seguro até +5, Risco de Falha/Degradação acima)",
        "usable": irow.get("Usable", "0") == "1",
        "weight": irow.get("Weight", "0")
    })

# Curate a balanced collection across ALL categories with real extracted icons prioritized:
curated_items = []

# 1. All Potions & Consumables (56 items)
curated_items.extend(items_by_cat["potion"])

# 2. Skill Cards (120 cards with skill levels)
curated_items.extend(items_by_cat["70"][:120])

# 3. Weapons & Gear (120 items)
curated_items.extend(items_by_cat["1"][:120])

# 4. Skill Books (80 items)
curated_items.extend(items_by_cat["31"][:80])

# 5. Chests & Baús (80 items with authentic icons)
curated_items.extend(items_by_cat["4"][:80])

# 6. Sephiras Místicas (72 items - all core Sephiras)
curated_items.extend(items_by_cat["32"][:72])

# 7. Relíquias & Equipamento Fúnebre (60 items)
curated_items.extend(items_by_cat["relic"][:60])

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
        target_rarity = "0"
        if succ_list:
            target_name = succ_list[0].get('item_nome_pt', '').strip() or f"Item #{succ_list[0].get('Param')}"
            target_param = succ_list[0].get('Param', '')
            target_rarity = succ_list[0].get('RewardRank', '0')

        # Target Icon matching directly from Item.csv
        target_row = item_raw.get(target_param, {})
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

            clean_mats.append({
                "name": mname,
                "amount": m.get('CostValue', '1'),
                "type": m.get('custo_tipo_nome_enum', 'Item'),
                "icon": mat_icon
            })

        succ_rate = (int(r.get('SuccessRate') or 0)) // 10000
        big_rate = (int(r.get('BigSuccessRate') or 0)) // 10000
        
        tab_num = int(tab_id) if tab_id.isdigit() else 0
        if tab_num in range(101, 106) or tab_num in range(601, 606):
            recipe_category = "weapons"
            cat_label = "Armas de Classe"
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

        crafting_catalog.append({
            "id": rid,
            "target_name": target_name,
            "target_item_id": target_param,
            "rarity": target_rarity,
            "tab_id": tab_id,
            "tab_name": tab_name,
            "category": recipe_category,
            "category_label": cat_label,
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
    ]
}

with open(os.path.join(OUT_DIR, "enchantment.json"), "w", encoding="utf-8") as f:
    json.dump(enchantment_catalog, f, indent=2, ensure_ascii=False)
print("  ✓ Processed Item Enchantment catalog (5,071 rules).")


# ==========================================
# 12. GAME CONSTANTS & FAQ
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
        "category": "Arquitetura & Engenharia",
        "question": "Qual motor gráfico e arquitetura de segurança o jogo utiliza?",
        "answer": "O VAMPIR foi desenvolvido na Unreal Engine 5.5.4 em ARM64 (libUnreal.so), utilizando o Gameplay Ability System (GAS), MetaSound para áudio espacial, e FluidNinja para simulação volumétrica de sangue e magia negra. Toda a lógica de combate é Server-Authoritative: cálculos de vida, recarga e dano são validados no servidor, impedindo modificações ilegais de memória de cliente."
    }
]

with open(os.path.join(OUT_DIR, "faq.json"), "w", encoding="utf-8") as f:
    json.dump(faq_catalog, f, indent=2, ensure_ascii=False)

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
    "dungeons": dungeons_catalog,
    "items": curated_items,
    "quests": quests_catalog,
    "crafting": crafting_catalog,
    "modes": modes_catalog,
    "pvp": pvp_catalog,
    "enchantment": enchantment_catalog,
    "constants": constants_dict,
    "faq": faq_catalog
}

with open(bundle_path, "w", encoding="utf-8") as f:
    f.write("window.VAMPIR_DATA = " + json.dumps(bundle_data, ensure_ascii=False) + ";\n")

print(f"Data builder completed! bundle.js size: {os.path.getsize(bundle_path) / 1024:.1f} KB")
