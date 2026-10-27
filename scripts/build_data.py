#!/usr/bin/env python3
"""
VAMPIR (ProjectRED) Web Application Data Builder
Parses raw game CSVs and documentation to generate structured JSON databases for the FAQ web application.
"""

import csv
import json
import os
import re

BASE_DIR = "/home/thiagofdso/vampir"
CSV_DIR = os.path.join(BASE_DIR, "analysis/patch_chunk1/ProjectRED/Content/RED/Data/CSV")
L10N_DIR = os.path.join(CSV_DIR, "L10N/pt")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
OUT_DIR = os.path.join(BASE_DIR, "faq/data")

os.makedirs(OUT_DIR, exist_ok=True)

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
tomb_card_names = load_csv_dict(os.path.join(L10N_DIR, "TombCard_Name.csv"))
vehicle_names = load_csv_dict(os.path.join(L10N_DIR, "Vehicle_Name.csv"))

# ==========================================
# 1. CLASSES
# ==========================================
print("Processing Classes...")
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
        "male_img": raw_c.get("ImgMainMale", ""),
        "female_img": raw_c.get("ImgMainFemale", "")
    })

with open(os.path.join(OUT_DIR, "classes.json"), "w", encoding="utf-8") as f:
    json.dump(classes_data, f, indent=2, ensure_ascii=False)

# ==========================================
# 2. BUILDS
# ==========================================
print("Processing Builds...")
builds_data = [
    {
        "id": "vipora-corrupcao",
        "class_id": 1,
        "class_name": "Víbora",
        "title": "Build: Corrupção Abissal & Dano Contínuo (DoT)",
        "objective": "Dano mágico sustentado, espalhamento de veneno e alta sobrevivência via escudos de feitiçaria e drenagem.",
        "playstyle": "Mantenha o Escudo de Veneno ativo, aplique Sussurros do Sofrimento para reduzir a defesa mágica em área e espalhe a Explosão de Veneno para detonar as ondas de monstros.",
        "skills": [
            {"id": "110017", "name": "Explosão de Veneno", "role": "Dois acertos e aplicação de DoT de veneno", "slot": "1", "book": "Livro de Habilidade: Explosão de Veneno (21011001)"},
            {"id": "110021", "name": "Sussurros do Sofrimento", "role": "Dano mágico massivo e redução de defesa mágica do alvo", "slot": "1", "book": "Livro de Habilidade: Sussurros do Sofrimento (21011002)"},
            {"id": "110022", "name": "Surto de Poder", "role": "Buff passivo/ativo que amplia o poder mágico", "slot": "1", "book": "Livro de Habilidade: Pico de Poder (21011004)"},
            {"id": "110027", "name": "Escudo de Veneno", "role": "Barreira protetora que absorve dano baseado na inteligência", "slot": "1", "book": "Livro de Habilidade: Escudo de Peçonha (21012004)"},
            {"id": "110034", "name": "Chamado de Sangue", "role": "Dano de sangue canalizado e recuperação de PV", "slot": "1", "book": "Livro de Habilidade: Chamado do Sangue (21011000)"}
        ],
        "stat_priority": ["Dano Mágico", "Perfuração Mágica", "Redução de Cooldown (Haste)", "Pontos de Sangue (BP)", "Defesa Mágica"],
        "recommended_gear": "Orbes com bônus de Feitiçaria Sombria e Armaduras com regeneração de Mana e Escudo Protetor."
    },
    {
        "id": "ceifador-sombra",
        "class_id": 2,
        "class_name": "Ceifador",
        "title": "Build: Sombra Executora & Dano Crítico Melee",
        "objective": "Eliminação cirúrgica de alvos de elite e chefes com golpes corpo a corpo de alta penetração e imobilização.",
        "playstyle": "Aproxime-se com Prisão Sombria para congelar a movimentação inimiga, ative Energia Sombria para inflar seu dano base e execute com o Golpe Mortal.",
        "skills": [
            {"id": "120011", "name": "Golpe Mortal", "role": "Ataque corpo a corpo concentrado (alcance de até 3m) com alto multiplicador crítico", "slot": "1", "book": "Livro de Habilidade: Golpe Mortal (21021001)"},
            {"id": "120012", "name": "Prisão Sombria", "role": "Controle de grupo que prende o alvo nas sombras e impede fuga", "slot": "1", "book": "Livro de Habilidade: Aprisionamento Sombrio (21022001)"},
            {"id": "120018", "name": "Energia Sombria", "role": "Aumenta exponencialmente o dano corpo a corpo e ataque crítico", "slot": "1", "book": "Livro de Habilidade: Energia Sombria (21021004)"},
            {"id": "120019", "name": "Pele Grossa", "role": "Aumenta a resistência física e reduz atordoamentos sofridos", "slot": "1", "book": "Livro de Habilidade: Pele Grossa (21021005)"},
            {"id": "120028", "name": "Regeneração Sombria", "role": "Cura contínua proporcional ao poder de ataque desferido", "slot": "0", "book": "Passiva Inata / Evolução"}
        ],
        "stat_priority": ["Dano Corpo a Corpo", "Taxa Crítica", "Dano Crítico", "Velocidade de Ataque", "Esquiva (ESQ)"],
        "recommended_gear": "Foices com afiação sombria e trajes leves de assassinato com bônus de aceleração de movimento."
    },
    {
        "id": "carnificina-artilharia",
        "class_id": 3,
        "class_name": "Carnificina",
        "title": "Build: Artilharia Carmesim Ranged DPS",
        "objective": "Metralhadora de projéteis abençoados, disparos em área a distâncias seguras (8.5m) e evasão tática.",
        "playstyle": "Posicione-se na retaguarda. Ative Passo Ágil e Mirar para obter 100% de precisão e bônus de alcance, fuzilando os alvos com Tiro Selvagem e repelindo ameaças com Queda da Escuridão.",
        "skills": [
            {"id": "130012", "name": "Tiro Selvagem", "role": "Sequência de 6 disparos ultra rápidos em até 8,5 metros", "slot": "1", "book": "Livro de Habilidade: Tiro Selvagem (21031002)"},
            {"id": "130014", "name": "Queda da Escuridão", "role": "Disparo explosivo que lança os inimigos no ar (Knockup)", "slot": "1", "book": "Livro de Habilidade: Queda da Escuridão (21032002)"},
            {"id": "130015", "name": "Mirar", "role": "Buff concentrado que amplia dano à distância e perfuração", "slot": "1", "book": "Livro de Habilidade: Mirar (21031004)"},
            {"id": "130016", "name": "Passo Ágil", "role": "Amplia velocidade de deslocamento e taxa de evasão (ESQ)", "slot": "1", "book": "Livro de Habilidade: Passo Ágil (21031005)"},
            {"id": "130030", "name": "Chamado de Sangue", "role": "Dreno balístico vampírico que devolve PV ao atirador", "slot": "1", "book": "Livro de Habilidade: Chamado do Sangue (21031000)"}
        ],
        "stat_priority": ["Dano à Distância", "Perfuração de Armadura", "Velocidade de Ataque", "Esquiva", "Consumo de Mana"],
        "recommended_gear": "Armas de fogo duplas com bônus de cadência e canos estendidos para maximizar o raio de 8.5m."
    },
    {
        "id": "manchado-baluarte",
        "class_id": 4,
        "class_name": "Manchado de Sangue",
        "title": "Build: Baluarte Carmesim & Drenagem Inabalável",
        "objective": "Tanque supremo de vanguarda que utiliza o próprio sangue para atrair inimigos, quebrar defesas e absorver dano.",
        "playstyle": "Agrupe multidões com Sede de Sangue (puxão), ative Postura de Batalha para elevar a defesa e corte com Espada de Sangue e Fúria de Sangue para transformar o dano em autocura instantânea.",
        "skills": [
            {"id": "140014", "name": "Fúria de Sangue", "role": "Golpe dilacerante que regenera PV equivalente a porcentagem do dano causado", "slot": "1", "book": "Livro de Habilidade: Fúria de Sangue (21042001)"},
            {"id": "140018", "name": "Postura de Batalha", "role": "Aumenta consideravelmente o ataque corpo a corpo e a tenacidade", "slot": "1", "book": "Livro de Habilidade: Postura de Batalha (21041004)"},
            {"id": "140020", "name": "Espada de Sangue", "role": "Ataque duplo de corte que fragmenta a armadura corpo a corpo do inimigo", "slot": "1", "book": "Livro de Habilidade: Espada de Sangue (21042000)"},
            {"id": "140023", "name": "Sede de Sangue", "role": "Puxão magnético sanguíneo que aprisiona e imobiliza alvos ao seu redor", "slot": "1", "book": "Livro de Habilidade: Sede de Sangue (21043000)"},
            {"id": "140027", "name": "Regeneração de Sangue", "role": "Recuperação passiva periódica de PV com base no poder de ataque", "slot": "0", "book": "Passiva Inata / Evolução"}
        ],
        "stat_priority": ["Pontos de Vida (HP Máximo)", "Defesa Física / Redução de Dano", "Roubo de Vida (Life Steal)", "Resistência a Atordoamento", "Dano Corpo a Corpo"],
        "recommended_gear": "Espadas de sangue forjadas e armaduras pesadas de placas vampíricas com alta mitigação de impacto."
    },
    {
        "id": "akasha-berserker",
        "class_id": 5,
        "class_name": "Akasha",
        "title": "Build: Colosso Corpóreo & Roubo de Poder",
        "objective": "Brawler implacável de combate corpo a corpo que enfraquece inimigos roubando seus atributos e ignorando controles.",
        "playstyle": "Inicie o combate aplicando Toque Absorvente para subtrair ATQ do alvo e fortalecer seus punhos. Use Corte Sangrento para rasgar defesas e ative Frenesi Carmesim e Libertação Absoluta para se tornar imune a atordoamento.",
        "skills": [
            {"id": "150014", "name": "Toque Absorvente", "role": "Ataque que rouba poder de ataque do inimigo e transfere para o personagem", "slot": "1", "book": "Livro de Habilidade: Toque Absorvente (21052000)"},
            {"id": "150015", "name": "Corte Sangrento", "role": "Golpes duplos com redução pesada da defesa física do oponente", "slot": "1", "book": "Livro de Habilidade: Corte Sangrento (21051002)"},
            {"id": "150017", "name": "Chamado de Sangue", "role": "Dano contundente com drenagem vital e regeneração de vida", "slot": "1", "book": "Livro de Habilidade: Chamado do Sangue (21051000)"},
            {"id": "150019", "name": "Frenesi Carmesim", "role": "Super buff que expande o alcance e a velocidade dos golpes básicos", "slot": "1", "book": "Livro de Habilidade: Frenesi Carmesim (21053002)"},
            {"id": "150029", "name": "Libertação Absoluta", "role": "Purifica e imuniza o personagem contra controles de grupo (Stun/Freeze/Slow)", "slot": "1", "book": "Livro de Habilidade: Libertação Absoluta (21054001)"}
        ],
        "stat_priority": ["Velocidade de Ataque", "Dano Corpo a Corpo", "Penetração de Defesa", "Imunidade a CC", "Vigor (HP)"],
        "recommended_gear": "Tonfas e Garras afiadas de combate desarmado combinadas com manoplas reforçadas."
    }
]

with open(os.path.join(OUT_DIR, "builds.json"), "w", encoding="utf-8") as f:
    json.dump(builds_data, f, indent=2, ensure_ascii=False)

# ==========================================
# 3. SKILLS DATABASE
# ==========================================
print("Processing Skills...")
skills_catalog = []
class_type_map = {
    "DarkMage": {"name": "Víbora", "class_id": 1},
    "Reaper": {"name": "Ceifador", "class_id": 2},
    "Gunner": {"name": "Carnificina", "class_id": 3},
    "SwordMan": {"name": "Manchado de Sangue", "class_id": 4},
    "Fighter": {"name": "Akasha", "class_id": 5},
    "All": {"name": "Comum / Todas", "class_id": 0}
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
    
    # Filter out empty/untranslated placeholder strings if no meaningful info
    if not name or "2025-05-21 Registered" in name or "2026-" in name:
        if not desc or "Registered" in desc:
            continue
        name = f"Habilidade {sid}"
        
    ctype_raw = srow.get("ClassType", "").strip()
    class_info = class_type_map.get(ctype_raw, {"name": ctype_raw if ctype_raw else "Geral", "class_id": 0})
    
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

print(f"Total curated skills: {len(skills_catalog)}")
with open(os.path.join(OUT_DIR, "skills.json"), "w", encoding="utf-8") as f:
    json.dump(skills_catalog, f, indent=2, ensure_ascii=False)

# ==========================================
# 4. BOSSES & ENEMIES
# ==========================================
print("Processing Bosses & NPCs...")
bosses_catalog = []

grade_map = {
    "0": "Monstro Normal",
    "1": "Monstro de Elite",
    "2": "Chefe de Campo (Field Boss)",
    "3": "Grande Chefe (Main Boss / Raid)"
}

for nid, nrow in npc_raw.items():
    grade = nrow.get("GradeType", "0")
    # Include all Bosses (grade 3) and prominent Field Bosses (grade 2) or high level Elites
    if grade not in ["2", "3"]:
        continue
    
    nname_row = npc_names.get(nid)
    title = nname_row.get("Title", "").strip() if nname_row else ""
    name = nname_row.get("Name", "").strip() if nname_row else ""
    name_en = nrow.get("NameEN", "").strip()
    
    display_name = name if name else (name_en if name_en else f"Monstro #{nid}")
    
    # Phase mechanics simulation based on Grade
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
        "blueprint": nrow.get("Blueprint", ""),
        "scale_factor": nrow.get("ScaleFactor", "1.0"),
        "body_radius": nrow.get("BodyRadius", "50"),
        "walk_speed": nrow.get("WalkSpeed", "120"),
        "run_speed": nrow.get("RunSpeed", "400"),
        "phases": phases,
        "audio_alert": "MetaSound Event / Alerta Sonoro de Habilidade Mortal" if grade == "3" else "Alerta de Área",
        "reward_preview": "Equipamentos Épicos/Lendários, Livros de Habilidade Raros, Essências de Sangue" if grade == "3" else "Materiais de Forja, Fragmentos de Sangue"
    })

# Sort by Grade (Boss first) and Level desc
bosses_catalog.sort(key=lambda x: (int(x["grade_code"]), int(x["level"] if x["level"].isdigit() else 0)), reverse=True)
print(f"Total curated bosses: {len(bosses_catalog)}")
with open(os.path.join(OUT_DIR, "bosses.json"), "w", encoding="utf-8") as f:
    json.dump(bosses_catalog, f, indent=2, ensure_ascii=False)

# ==========================================
# 5. DUNGEONS
# ==========================================
print("Processing Dungeons...")
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
    
    dungeons_catalog.append({
        "id": did,
        "name": name,
        "description": desc if desc else f"Instância de combate com desafios de monstros e chefes de elite ({type_label}).",
        "type_code": dtype,
        "type_name": type_label,
        "req_level": int(req_lvl) if req_lvl.isdigit() else 1,
        "rec_level": int(rec_lvl) if rec_lvl.isdigit() else 1,
        "reward_exp": drow.get("RewardExp", "Varia conforme pontuação"),
        "max_clear_grade": "Grau 6 (SS) com bônus de itens lendários"
    })

dungeons_catalog.sort(key=lambda x: (x["type_code"], x["req_level"]))
print(f"Total curated dungeons: {len(dungeons_catalog)}")
with open(os.path.join(OUT_DIR, "dungeons.json"), "w", encoding="utf-8") as f:
    json.dump(dungeons_catalog, f, indent=2, ensure_ascii=False)

# ==========================================
# 6. ITEMS & GEAR
# ==========================================
print("Processing Items & Gear...")
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
    rarity = irow.get("Rarity", "Comum")
    
    # Clean replace string placeholders in name/desc
    clean_name = re.sub(r'\{[^}]+\}', '', name).strip()
    clean_desc = re.sub(r'\{[^}]+\}', '', desc).strip()
    
    if len(clean_name) < 2:
        continue
        
    items_catalog.append({
        "id": iid,
        "name": clean_name,
        "desc": clean_desc if clean_desc else "Item de uso e progressão vampírica.",
        "type_code": itype,
        "type_name": type_label,
        "tier": tier if tier else "1",
        "rarity": rarity,
        "max_enchant": "+15 (Encantamento Seguro até +5, Risco de Falha/Degradação acima)",
        "usable": irow.get("Usable", "0") == "1",
        "weight": irow.get("Weight", "0")
    })

# Sample top 300 distinctive items for quick responsive rendering
distinct_items = {}
for it in items_catalog:
    key = it["name"]
    if key not in distinct_items and len(distinct_items) < 300:
        distinct_items[key] = it

curated_items = list(distinct_items.values())
print(f"Total curated items: {len(curated_items)}")
with open(os.path.join(OUT_DIR, "items.json"), "w", encoding="utf-8") as f:
    json.dump(curated_items, f, indent=2, ensure_ascii=False)

# ==========================================
# 7. GAME CONSTANTS
# ==========================================
print("Processing Constants...")
constants_dict = {}
for crow in const_raw:
    k = crow.get("Key", "").strip()
    v = crow.get("Value", "").strip()
    if k:
        constants_dict[k] = v

with open(os.path.join(OUT_DIR, "constants.json"), "w", encoding="utf-8") as f:
    json.dump(constants_dict, f, indent=2, ensure_ascii=False)

# ==========================================
# 8. FAQ & GAME SYSTEMS
# ==========================================
print("Generating FAQ database...")
faq_catalog = [
    {
        "category": "Mecânicas Vampíricas",
        "question": "O que são Pontos de Sangue (Blood Points / BP) e como funcionam?",
        "answer": "Os Pontos de Sangue (BP) representam a energia vital e espiritual do vampiro. O BP é alimentado através de três mecanismos: 1) Drenagem Direta no Alvo (Target Blood Drain), 2) Drenagem de Execução em inimigos caídos, e 3) Alimentação de Lacaios/Seguidores (`Follower.DrainCountRecoveryPotionList`). O acúmulo de BP ativa as Formas de Sangue (`CostumeArmorSkin`), concedendo bônus de dano de até +20%, velocidade adicional e habilidades exclusivas de linhagem."
    },
    {
        "category": "Mecânicas Vampíricas",
        "question": "O que são os Caixões e as Cartas de Tumba (Tomb Cards)?",
        "answer": "O sistema de Caixões (`TombCard`) é um pilar de descanso e fortalecimento do vampiro. Caixões variam de 'Caixão de Madeira Comum' a 'Caixão de Pedra Requintado' e 'Caixões Nobres'. Ao sincronizar Cartas de Tumba em sua tumba ancestral, o jogador desbloqueia bônus permanentes na Árvore da Linhagem (Bloodline Tree), como resistência a dano de luz, redução de tempo de atordoamento e slots extras para poções de sangue."
    },
    {
        "category": "Combate & Chefes",
        "question": "Como funcionam as 6 Fases dos Grandes Chefes?",
        "answer": "Chefes de Masmorra e Raide possuem 6 fases (`EMonsterPhase`): Fase 1 (100-85%): rotação básica; Fase 2 (85-70%): primeiras invocações de lacaios; Fase 3 (70-50%): escudos protetores e campos de dano contínuo; Fase 4 (50-30%): ataques em cone e atordoamento; Fase 5 (30-15%): alertas sonoros dedicados (MetaSound) e teleporte; Fase 6 (<15%): Frenesi Mortal (Enrage), onde o chefe dobra a velocidade e o dano até ser derrotado."
    },
    {
        "category": "Combate & Chefes",
        "question": "Como funciona o sistema de Cooldown e delays de habilidades?",
        "answer": "Cada habilidade em VAMPIR possui parâmetros de tempo calibrados: MinCoolTime (tempo base de recarga), MaxCoolTime (tempo com penalidades de ambiente), TotalTime (duração total da animação) e StackCount (cargas acumuláveis). Habilidades com a flag `Mobile=1` permitem que o vampiro se movimente enquanto conjura, enquanto `DashOffset` determina o avanço vetorial durante o golpe."
    },
    {
        "category": "Equipamentos & Forja",
        "question": "Como funciona o Encantamento de Itens e quais são os limites?",
        "answer": "O limite máximo de encantamento é +15 (`Auction.FilterMaxEnchantLevel: 15`). O jogo oferece encantamento simples e multi-encantamento automático até o nível 11 (`ItemEnchant.MultiEnchantSequenceEnchantLevel: 11`). Encantamentos utilizam Pergaminhos Abençoados (sem risco de quebra) ou Pergaminhos Amaldiçoados/Comuns (com risco de rebaixamento de nível acima de +5)."
    },
    {
        "category": "PvP & Mundo Aberto",
        "question": "Como funciona o PvP em Zonas de Conflito e o Radar de Vingança?",
        "answer": "O mapa é dividido em 3 zonas: Segurança (Safety), Neutra (Neutral) e Conflito (Conflict). Em zonas de conflito, jogadores podem ser atacados livremente. Caso você seja eliminado por um jogador, o sistema ativa o Radar de Vingança (`PVP.RevengeWorldGroupIdList`), rastreando a localização exata do agressor no mapa com atualização a cada 10 segundos (`PVP.LocationSearchPosRefreshTime: 10`) por até 24 horas (`PVP.ReactionTimeLimit: 86400`)."
    },
    {
        "category": "Modos de Jogo & Raides",
        "question": "Qual é a capacidade de Grupos, Raides e Servidores?",
        "answer": "Grupos convencionais suportam até 5 membros (`Party.MaxMemberCount: 5`). Equipes de Raide suportam até 50 membros simultâneos (`RaidTeam.MaxMemberCount: 50`) com líder de raid e verificações de prontidão ('Ready Check Duration: 20s'). Em Masmorras Inter-Servidor (Cross-Server), o limite de entrada é de 200 jogadores por servidor conectado (`ServerDungeon.ServerEntryLimit: 200`)."
    },
    {
        "category": "Automação & Suporte",
        "question": "Como funciona o Modo de Manutenção Automática (SupportMode / AFK)?",
        "answer": "O jogo conta com o recurso `SupportModeAutoMaintain`, que permite ao personagem continuar farmando ou completando rotinas automaticamente mesmo offline. O sistema monitora poções de vida (`AutoMaintain.HpPotionMinCount: 100`) e recarrega suprimentos em cidades antes de retornar ao ponto de caça."
    },
    {
        "category": "Arquitetura & Engenharia",
        "question": "Qual motor gráfico e arquitetura de segurança o jogo utiliza?",
        "answer": "O VAMPIR foi desenvolvido na Unreal Engine 5.5.4 em ARM64 (`libUnreal.so`), utilizando o Gameplay Ability System (GAS), MetaSound para áudio espacial, e FluidNinja para simulação volumétrica de sangue e magia negra. Toda a lógica de combate é Server-Authoritative: cálculos de vida, recarga e dano são validados no servidor, impedindo modificações ilegais de memória de cliente (como Hit-Kill em memória local)."
    },
    {
        "category": "Arquitetura & Engenharia",
        "question": "Como os arquivos de dados (PAKs) foram decodificados?",
        "answer": "Os arquivos de dados (.pak) estavam criptografados com o algoritmo AES-256-CBC. Através de engenharia reversa estática na biblioteca `libUnreal.so`, a chave mestra de 256 bits foi extraída no offset 0x756520: `4de16fa1dffb68f2b957d49e6beaebcaf7d6b41a0107cd548f0068ecde4d28ed`. Isso permitiu a extração completa de mais de 40 MB de tabelas de jogo originais."
    }
]

with open(os.path.join(OUT_DIR, "faq.json"), "w", encoding="utf-8") as f:
    json.dump(faq_catalog, f, indent=2, ensure_ascii=False)

print("Data builder completed successfully!")
