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
npc_names = load_csv_dict(os.path.join(L10N_DIR, "Npc_Name.csv"))
dungeon_raw = load_csv_dict(os.path.join(CSV_DIR, "Dungeon.csv"))
dungeon_names = load_csv_dict(os.path.join(L10N_DIR, "Dungeon_Name.csv"))
item_raw = load_csv_dict(os.path.join(CSV_DIR, "Item.csv"))
item_names = load_csv_dict(os.path.join(L10N_DIR, "Item_Name.csv"))
const_raw = load_csv_list(os.path.join(CSV_DIR, "Const.csv"))

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
# 4. BOSSES & ENEMIES (WITH REAL PORTRAITS)
# ==========================================
print("Processing Bosses & NPCs with official portraits...")
bosses_catalog = []

grade_map = {
    "0": "Monstro Normal",
    "1": "Monstro de Elite",
    "2": "Chefe de Campo (Field Boss)",
    "3": "Grande Chefe (Main Boss / Raid)"
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

for nid, nrow in npc_raw.items():
    grade = nrow.get("GradeType", "0")
    if grade not in ["2", "3"]:
        continue
    
    nname_row = npc_names.get(nid)
    title = nname_row.get("Title", "").strip() if nname_row else ""
    name = nname_row.get("Name", "").strip() if nname_row else ""
    name_en = nrow.get("NameEN", "").strip()
    
    display_name = name if name else (name_en if name_en else f"Monstro #{nid}")
    
    # Match image
    img_field = nrow.get("Img", "").strip()
    clean_img = img_field.replace("IMG_Monster_Portrait_", "").lower() + ".png"
    bp = nrow.get("Blueprint", "").lower()
    
    matched_img = ""
    if clean_img in monster_pngs:
        matched_img = clean_img
    else:
        # Search blueprint keyword match
        for m in monster_pngs:
            token = m.replace(".png", "")
            if token in bp or token in clean_img:
                matched_img = m
                break
                
    if not matched_img:
        # Pick themed portrait based on id hash
        idx = int(nid) % len(default_boss_portraits)
        matched_img = default_boss_portraits[idx]

    phases = [
        {"phase": "Fase 1 (100% - 85% HP)", "desc": "Padrão de ataque base e ataques telegrafados com aviso visual no chão."},
        {"phase": "Fase 2 (85% - 70% HP)", "desc": "Primeira invocação de lacaios e aumento de velocidade de movimento."},
        {"phase": "Fase 3 (70% - 50% HP)", "desc": "Ativação de mecânica de escudo protetor e dano em área contínuo."},
        {"phase": "Fase 4 (50% - 30% HP)", "desc": "Mudança de postura agressiva e habilidades de atordoamento em cone."},
        {"phase": "Fase 5 (30% - 15% HP)", "desc": "Sobrecarga de fúria e emissão de alertas de áudio específicos (MetaSound)."},
        {"phase": "Fase 6 (< 15% HP)", "desc": "Frenesi Mortal (Enrage): ataques com dano duplicado até a derrota final."}
    ] if grade == "3" else [
        {"phase": "Fase 1 (100% - 50% HP)", "desc": "Combate de área aberta com convocação de monstros auxiliares."},
        {"phase": "Fase 2 (< 50% HP)", "desc": "Frenesi com aumento de dano e raio de ataque expandido."}
    ]

    bosses_catalog.append({
        "id": nid,
        "name": display_name,
        "title": title if title else ("Governante Sombrio" if grade == "3" else "Territorial"),
        "grade_code": grade,
        "grade_name": grade_map.get(grade, "Chefe"),
        "level": nrow.get("Level", "1"),
        "portrait_img": f"assets/monsters/{matched_img}",
        "blueprint": nrow.get("Blueprint", ""),
        "scale_factor": nrow.get("ScaleFactor", "1.0"),
        "body_radius": nrow.get("BodyRadius", "50"),
        "walk_speed": nrow.get("WalkSpeed", "120"),
        "run_speed": nrow.get("RunSpeed", "400"),
        "phases": phases,
        "audio_alert": "MetaSound Event / Alerta Sonoro de Habilidade Mortal" if grade == "3" else "Alerta de Área",
        "reward_preview": "Equipamentos Épicos/Lendários, Livros de Habilidade Raros, Essências de Sangue" if grade == "3" else "Materiais de Forja, Fragmentos de Sangue"
    })

bosses_catalog.sort(key=lambda x: (int(x["grade_code"]), int(x["level"] if x["level"].isdigit() else 0)), reverse=True)
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
item_type_map = {
    "1": "Arma Principal",
    "4": "Baú de Recompensas",
    "20": "Poção & Consumível",
    "31": "Livro de Habilidade",
    "45": "Acessório & Joia",
    "70": "Carta de Habilidade / Selo de Sangue"
}

items_catalog = []
for iid, irow in item_raw.items():
    iname_row = item_names.get(iid)
    if not iname_row:
        continue
    name = iname_row.get("Name", "").strip()
    desc = iname_row.get("Desc", "").strip()
    
    if not name or "2025-" in name or "2026-" in name:
        continue
    
    itype = irow.get("Type", "")
    type_label = item_type_map.get(itype, "Item Geral")
    
    tier = irow.get("Tier", "1")
    rarity = irow.get("Rarity", "102")
    
    clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
    clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    
    if len(clean_name) < 2:
        continue

    # Image matching
    raw_img = irow.get("Img", "").strip()
    clean_img_file = raw_img.replace("IMG_", "").lower() + ".png"
    
    item_img = ""
    if clean_img_file in item_pngs:
        item_img = f"assets/items/{clean_img_file}"
    elif "weapon" in clean_img_file or itype == "1":
        # Search available weapon icon
        for w in ["weapon_bloodsword_common_01.png", "weapon_bloodsword_common_01_event.png"]:
            if w in item_pngs:
                item_img = f"assets/items/{w}"
                break
    elif "potion" in clean_img_file or itype == "20":
        for p in ["potion_event_01.png", "pvpbuffpotion_01.png"]:
            if p in item_pngs:
                item_img = f"assets/items/{p}"
                break
    elif "accessory" in clean_img_file or itype == "45":
        for a in ["accessory_belt_common_01.png", "accessory_belt_epic_01.png"]:
            if a in item_pngs:
                item_img = f"assets/items/{a}"
                break

    if not item_img:
        item_img = "assets/logo.png"

    items_catalog.append({
        "id": iid,
        "name": clean_name,
        "desc": clean_desc if clean_desc else "Item de uso e progressão vampírica.",
        "type_code": itype,
        "type_name": type_label,
        "icon_img": item_img,
        "tier": tier if tier else "1",
        "rarity": rarity,
        "max_enchant": "+15 (Encantamento Seguro até +5, Risco de Falha/Degradação acima)",
        "usable": irow.get("Usable", "0") == "1",
        "weight": irow.get("Weight", "0")
    })

# Deduplicate distinct items and prioritize ones with custom item icons
distinct_items = {}
for it in items_catalog:
    key = it["name"]
    if key not in distinct_items:
        distinct_items[key] = it
    elif "assets/items/" in it["icon_img"] and "assets/items/" not in distinct_items[key]["icon_img"]:
        distinct_items[key] = it

curated_items = list(distinct_items.values())[:400]
with open(os.path.join(OUT_DIR, "items.json"), "w", encoding="utf-8") as f:
    json.dump(curated_items, f, indent=2, ensure_ascii=False)

# ==========================================
# 7. GAME CONSTANTS & FAQ
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
        "answer": "O limite máximo de encantamento é +15 (Auction.FilterMaxEnchantLevel: 15). O jogo oferece encantamento simples e multi-encantamento automático até o nível 11 (ItemEnchant.MultiEnchantSequenceEnchantLevel: 11). Encantamentos utilizam Pergaminhos Abençoados (sem risco de quebra) ou Pergaminhos Amaldiçoados/Comuns (com risco de rebaixamento de nível acima de +5)."
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
    },
    {
        "category": "Arquitetura & Engenharia",
        "question": "Como os arquivos de dados (PAKs) foram decodificados?",
        "answer": "Os arquivos de dados (.pak) estavam criptografados com o algoritmo AES-256-CBC. Através de engenharia reversa estática na biblioteca libUnreal.so, a chave mestra de 256 bits foi extraída no offset 0x756520: 4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed. Isso permitiu a extração completa de mais de 40 MB de tabelas de jogo originais."
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
    "constants": constants_dict,
    "faq": faq_catalog
}

with open(bundle_path, "w", encoding="utf-8") as f:
    f.write("window.VAMPIR_DATA = " + json.dumps(bundle_data, ensure_ascii=False) + ";\n")

print(f"Data builder completed! bundle.js size: {os.path.getsize(bundle_path) / 1024:.1f} KB")
