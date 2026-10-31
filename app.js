/**
 * VAMPIR (ProjectRED) - Web Application Client Logic
 * Handles interactive tabs, real-time filtering, data rendering and inspection modal.
 */

(function () {
  'use strict';

  // Application State
  const state = {
    currentTab: 'overview',
    data: window.VAMPIR_DATA || {},
    skillsClassFilter: 'all',
    skillsSearchTerm: '',
    skillsPage: 1,
    skillsPerPage: 36,
    bossesFilter: 'all',
    bossesRegion: 'all',
    bossesSearchTerm: '',
    bossesPage: 1,
    dungeonsFilter: 'all',
    dungeonsSearchTerm: '',
    itemsFilter: 'all',
    itemsSearchTerm: '',
    itemsPage: 1,
    itemsPerPage: 36,
    questsFilter: 'all',
    questsSearchTerm: '',
    questsPage: 1,
    questsPerPage: 24,
    craftingFilter: 'all',
    craftingSearchTerm: '',
    craftingPage: 1,
    craftingPerPage: 24,
    shopsFilter: 'all',
    shopsSearchTerm: '',
    shopsPage: 1,
    shopsPerPage: 24,
    codexTab: 'collections',
    codexFilter: 'all',
    codexRarity: 'all',
    codexSearchTerm: '',
    codexPage: 1,
    codexPerPage: 24,
    codexEntriesFilter: 'all',
    codexEntriesSearchTerm: '',
    codexEntriesPage: 1,
    codexEntriesPerPage: 36,
    researchFilter: 'all',
    researchSearchTerm: '',
    researchPage: 1,
    researchPerPage: 18,
    portraitsFilter: 'all',
    portraitsType: 'all',
    portraitsSearchTerm: '',
    portraitsPage: 1,
    portraitsPerPage: 18,
    artifactsFilter: 'all',
    artifactsSearchTerm: '',
    bloodlineFilter: 'all',
    bloodlineSearchTerm: '',
    modesFilter: 'all',
    pvpTab: 'arena',
    enchantTab: 'scrolls',
    activeBuildIndex: 0,
    activeVariantIndex: 0
  };

  function formatBigNumber(val) {
    if (!val || val === '0') return '—';
    const n = Number(val);
    if (isNaN(n)) return val;
    if (n >= 1000000000) return (n / 1000000000).toFixed(2) + 'B';
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(0) + 'k';
    return n.toLocaleString();
  }

  // DOM Elements
  const navItems = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.view-section');
  const globalSearch = document.getElementById('globalSearch');
  const detailModal = document.getElementById('detailModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalTitle = document.getElementById('modalTitle');
  const modalSubtitle = document.getElementById('modalSubtitle');
  const modalBody = document.getElementById('modalBody');

  // Async data fallback if bundle was not loaded
  async function ensureDataLoaded() {
    if (state.data && state.data.classes) {
      initApp();
      return;
    }

    try {
      const [classes, builds, skills, bosses, dungeons, items, quests, crafting, modes, pvp, enchantment, shops, codex, research, portraits, artifacts, bloodline, faq, constants] = await Promise.all([
        fetch('data/classes.json').then(r => r.json()),
        fetch('data/builds.json').then(r => r.json()),
        fetch('data/skills.json').then(r => r.json()),
        fetch('data/bosses.json').then(r => r.json()),
        fetch('data/dungeons.json').then(r => r.json()),
        fetch('data/items.json').then(r => r.json()),
        fetch('data/quests.json').then(r => r.json()),
        fetch('data/crafting.json').then(r => r.json()),
        fetch('data/modes.json').then(r => r.json()),
        fetch('data/pvp.json').then(r => r.json()),
        fetch('data/enchantment.json').then(r => r.json()),
        fetch('data/shops.json').then(r => r.json()),
        fetch('data/codex.json').then(r => r.json()),
        fetch('data/research.json').then(r => r.json()),
        fetch('data/portraits.json').then(r => r.json()),
        fetch('data/artifacts.json').then(r => r.json()),
        fetch('data/bloodline.json').then(r => r.json()),
        fetch('data/faq.json').then(r => r.json()),
        fetch('data/constants.json').then(r => r.json())
      ]);

      state.data = { classes, builds, skills, bosses, dungeons, items, quests, crafting, modes, pvp, enchantment, shops, codex, research, portraits, artifacts, bloodline, faq, constants };
      initApp();
    } catch (e) {
      console.error('Failed to load JSON data asynchronously:', e);
    }
  }

  // Navigation Logic
  function switchTab(tabId) {
    state.currentTab = tabId;

    navItems.forEach(item => {
      item.classList.toggle('active', item.dataset.target === tabId);
    });

    sections.forEach(sec => {
      sec.classList.toggle('active', sec.id === tabId);
    });

    const wrapper = document.querySelector('.main-wrapper');
    if (wrapper) wrapper.scrollTop = 0;

    if (tabId === 'skills') renderSkills();
    if (tabId === 'bosses') renderBosses();
    if (tabId === 'dungeons') renderDungeons();
    if (tabId === 'items') renderItems();
    if (tabId === 'builds') renderBuilds();
    if (tabId === 'quests') renderQuests();
    if (tabId === 'crafting') renderCrafting();
    if (tabId === 'modes') renderModes();
    if (tabId === 'pvp') renderPvP();
    if (tabId === 'enchantment') renderEnchantment();
    if (tabId === 'shops') renderShops();
    if (tabId === 'codex') renderCodex();
    if (tabId === 'research') renderResearch();
    if (tabId === 'portraits') renderPortraits();
    if (tabId === 'artifacts') renderArtifacts();
    if (tabId === 'bloodline') renderBloodline();
  }

  window.navTo = function(tabId) {
    switchTab(tabId);
  };

  // Render Classes with Official Portraits and Icons
  function renderClasses() {
    const container = document.getElementById('classesContainer');
    if (!container || !state.data.classes) return;

    container.innerHTML = state.data.classes.map(cls => `
      <div class="class-card">
        <div class="class-header-bar">
          <div style="display: flex; align-items: center; gap: 14px;">
            <img src="${cls.icon_img}" alt="${cls.name} Icon" class="class-badge-img" onerror="this.src='assets/logo.png'">
            <div class="class-title-group">
              <h3>${cls.name}</h3>
              <span class="class-subtitle">${cls.archetype}</span>
            </div>
          </div>
          <span class="entity-badge badge-crimson">${cls.resource}</span>
        </div>

        <!-- Official Character Artwork Showcase -->
        ${cls.male_img || cls.female_img ? `
          <div class="class-art-showcase">
            ${cls.male_img ? `
              <div class="portrait-card">
                <img src="${cls.male_img}" alt="${cls.name} Masculino" class="portrait-img">
                <span class="portrait-label">Masculino</span>
              </div>
            ` : ''}
            ${cls.female_img ? `
              <div class="portrait-card">
                <img src="${cls.female_img}" alt="${cls.name} Feminino" class="portrait-img">
                <span class="portrait-label">Feminino</span>
              </div>
            ` : ''}
          </div>
        ` : ''}

        <div class="class-body">
          <div class="class-lore">${cls.desc}</div>
          
          <div style="margin-bottom: 16px;">
            <div style="font-size: 0.82rem; color: var(--gold-primary); font-weight: 600; margin-bottom: 6px;">
              ⚔️ Arma & Papel Tático:
            </div>
            <div style="font-size: 0.88rem; color: #fff;">
              ${cls.weapon} — <em>${cls.role}</em>
            </div>
          </div>

          <div class="class-stats-list">
            ${Object.entries(cls.radar).map(([stat, val]) => `
              <div class="stat-bar-container">
                <span class="stat-name">${stat.toUpperCase()}</span>
                <div class="stat-track">
                  <div class="stat-fill" style="width: ${val}%;"></div>
                </div>
                <span class="stat-num">${val}</span>
              </div>
            `).join('')}
          </div>

          <div class="highlights-title">Destaques da Linhagem:</div>
          <div>
            ${cls.highlights.map(h => `<div class="highlight-item">${h}</div>`).join('')}
          </div>

          <div style="margin-top: 20px;">
            <button class="filter-btn active" style="width: 100%;" onclick="window.selectBuildByClass(${cls.id})">
              Ver Build PvE Recomendada →
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  // Render Builds and Specialized Variants
  function renderBuilds() {
    const tabsContainer = document.getElementById('buildsTabs');
    const detailContainer = document.getElementById('buildDetailContainer');
    if (!tabsContainer || !detailContainer || !state.data.builds) return;

    tabsContainer.innerHTML = state.data.builds.map((b, idx) => `
      <button class="build-tab-btn ${idx === state.activeBuildIndex ? 'active' : ''}" onclick="window.selectBuild(${idx})">
        <img src="${b.icon_img}" alt="icon" style="width: 22px; height: 22px; border-radius: 4px;" onerror="this.src='assets/logo.png'">
        <span>${b.class_name}</span>
      </button>
    `).join('');

    const b = state.data.builds[state.activeBuildIndex];
    if (!b || !b.variants) return;

    const vIdx = state.activeVariantIndex || 0;
    const variant = b.variants[vIdx] || b.variants[0];

    detailContainer.innerHTML = `
      <div class="build-detail-card">
        <!-- Variant Sub-Tabs (Geral, Farm, Chefe, PvP) -->
        <div style="display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px;">
          ${b.variants.map((v, idx) => `
            <button class="filter-btn ${idx === vIdx ? 'active' : ''}" onclick="window.selectVariant(${idx})">
              ${v.badge}
            </button>
          `).join('')}
        </div>

        <div class="build-header">
          <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
              <h2>${variant.title}</h2>
              <div class="build-objective">🎯 <strong>Objetivo:</strong> ${variant.objective}</div>
            </div>
            <span class="entity-badge badge-crimson" style="font-size: 0.85rem; padding: 6px 14px;">${variant.badge}</span>
          </div>
        </div>

        <div class="build-grid-columns">
          <div>
            <h3 style="font-family: var(--font-serif); font-size: 1.25rem; color: #fff; margin-bottom: 14px;">
              Habilidades Recomendadas da Variante
            </h3>
            <table class="skills-table">
              <thead>
                <tr>
                  <th>Habilidade</th>
                  <th>Função Tática</th>
                  <th>Recarga & Custo</th>
                  <th>Slot / Raridade</th>
                </tr>
              </thead>
              <tbody>
                ${variant.skills.map(s => `
                  <tr>
                    <td class="skill-name-cell" onclick="window.inspectSkill('${s.id}')" style="cursor: pointer;">
                      <div style="color: #fff; font-weight: 600;">${s.name}</div>
                      <span class="skill-id-tag">ID #${s.id}</span>
                      ${s.book ? `<span class="book-tag">📖 ${s.book}</span>` : ''}
                    </td>
                    <td style="color: #cbd5e1; font-size: 0.85rem;">${s.role}</td>
                    <td style="font-size: 0.82rem;">
                      <div style="color: var(--crimson-light); font-weight: 600;">⏱️ ${s.cooldown || 'Padrão'}</div>
                      ${s.mp ? `<div style="color: #93c5fd;">💧 MP: ${s.mp}</div>` : ''}
                      ${s.range ? `<div style="color: var(--text-dim);">🎯 ${s.range}</div>` : ''}
                    </td>
                    <td>
                      <span class="entity-badge badge-crimson">Slot ${s.slot || '1'}</span>
                      ${s.rarity ? `<div style="font-size: 0.72rem; color: var(--gold-primary); margin-top: 4px;">${s.rarity}</div>` : ''}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>

            <!-- Candidate Equipment Table -->
            ${variant.equipment && variant.equipment.length > 0 ? `
              <div style="margin-top: 28px;">
                <h3 style="font-family: var(--font-serif); font-size: 1.25rem; color: var(--gold-primary); margin-bottom: 14px;">
                  ⚔️ Equipamentos & Armas Candidatas
                </h3>
                <table class="skills-table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Raridade</th>
                      <th>Atributos Associados & Bônus</th>
                      <th>Requisitos</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${variant.equipment.map(eq => `
                      <tr>
                        <td style="font-weight: 600; color: #fff;">${eq.item}</td>
                        <td><span class="entity-badge badge-gold">${eq.rarity}</span></td>
                        <td style="color: #cbd5e1; font-size: 0.85rem;">${eq.attributes}</td>
                        <td style="font-size: 0.78rem; color: var(--text-dim);">${eq.level_limits || 'Natural'}</td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            ` : ''}
          </div>

          <div class="build-sidebar-panel">
            <div class="panel-box">
              <div class="panel-title">Prioridade de Atributos</div>
              <div class="stat-pills-list">
                ${variant.stat_priority.map((st, i) => `
                  <div class="stat-pill-row">
                    <span style="color: #fff; font-weight: 500;">${i + 1}. ${st}</span>
                    <span style="color: var(--gold-primary);">★</span>
                  </div>
                `).join('')}
              </div>
            </div>

            <div class="panel-box">
              <div class="panel-title">Guia de Otimização</div>
              <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
                Esta variante foi formulada com base nas tabelas extraídas do <code>pakchunk1</code>. 
                Para maximizar o desempenho, priorize armas com os afixos indicados (Dano a Chefes para Raides/Masmorras, Dano a Monstros para Farm e Redução de Dano para PvP).
              </p>
              <div style="margin-top: 12px; font-size: 0.78rem; color: var(--gold-primary);">
                ✦ Encantamento seguro até +5; multi-encantamento sequencial até +11.
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  window.selectBuild = function(idx) {
    state.activeBuildIndex = idx;
    state.activeVariantIndex = 0;
    renderBuilds();
  };

  window.selectVariant = function(vIdx) {
    state.activeVariantIndex = vIdx;
    renderBuilds();
  };

  window.selectBuildByClass = function(classId) {
    const idx = state.data.builds.findIndex(b => b.class_id === classId);
    if (idx !== -1) {
      state.activeBuildIndex = idx;
      state.activeVariantIndex = 0;
      switchTab('builds');
    }
  };

  // Render Skills
  function renderSkills() {
    const container = document.getElementById('skillsContainer');
    const pagination = document.getElementById('skillsPagination');
    if (!container || !state.data.skills) return;

    let filtered = state.data.skills;

    if (state.skillsClassFilter !== 'all') {
      const cid = parseInt(state.skillsClassFilter, 10);
      filtered = filtered.filter(s => s.class_id === cid);
    }

    if (state.skillsSearchTerm.trim()) {
      const q = state.skillsSearchTerm.toLowerCase();
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q) ||
        s.id.includes(q) ||
        s.class_name.toLowerCase().includes(q)
      );
    }

    const totalFiltered = filtered.length;
    const paginated = filtered.slice(0, state.skillsPage * state.skillsPerPage);

    container.innerHTML = paginated.map(s => `
      <div class="entity-card" onclick="window.inspectSkill('${s.id}')">
        <div class="entity-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <img src="${s.icon_img || 'assets/logo.png'}" alt="Icon" class="mini-skill-icon" onerror="this.src='assets/logo.png'">
            <span class="entity-badge badge-purple">${s.class_name}</span>
          </div>
          <span class="entity-id">ID ${s.id}</span>
        </div>
        <div class="entity-title">${s.name}</div>
        <p class="entity-desc">${s.description || s.effect_description || 'Habilidade de combate vampírica.'}</p>
        
        <div class="entity-meta-row">
          <span>⏱️ ${s.cooldown}</span>
          <span>💧 MP: ${s.mp_cost}</span>
          <span>🎯 ${s.range}</span>
        </div>
      </div>
    `).join('');

    if (paginated.length < totalFiltered) {
      pagination.innerHTML = `
        <button class="filter-btn active" onclick="window.loadMoreSkills()">
          Carregar Mais Habilidades (${paginated.length} de ${totalFiltered})
        </button>
      `;
    } else {
      pagination.innerHTML = `<span style="font-size: 0.85rem; color: var(--text-dim);">Exibindo todas as ${totalFiltered} habilidades correspondentes.</span>`;
    }
  }

  window.loadMoreSkills = function() {
    state.skillsPage++;
    renderSkills();
  };

  // Render Bosses with Official High-Res Portraits & Deduplication
  function renderBosses() {
    const container = document.getElementById('bossesContainer');
    const pagination = document.getElementById('bossesPagination');
    if (!container || !state.data.bosses) return;

    let filtered = state.data.bosses;

    if (state.bossesFilter === 'drops_only') {
      filtered = filtered.filter(b => b.drops && b.drops.length > 0);
    } else if (state.bossesFilter !== 'all') {
      filtered = filtered.filter(b => b.grade_code === state.bossesFilter);
    }

    if (state.bossesRegion && state.bossesRegion !== 'all') {
      filtered = filtered.filter(b => (b.regions && b.regions.includes(state.bossesRegion)) || (b.world_map && b.world_map.includes(state.bossesRegion)));
    }

    if (state.bossesSearchTerm.trim()) {
      const q = state.bossesSearchTerm.toLowerCase();
      filtered = filtered.filter(b =>
        b.name.toLowerCase().includes(q) ||
        b.title.toLowerCase().includes(q) ||
        b.id.includes(q) ||
        (b.instance_ids && b.instance_ids.some(id => id.includes(q))) ||
        (b.blueprint && b.blueprint.toLowerCase().includes(q)) ||
        (b.world_map && b.world_map.toLowerCase().includes(q)) ||
        (b.drops && b.drops.some(d => d.name.toLowerCase().includes(q)))
      );
    }

    const totalFiltered = filtered.length;
    const pageSize = 48;
    const paginated = filtered.slice(0, state.bossesPage * pageSize);

    container.innerHTML = paginated.map(b => {
      const badgeColor = b.grade_code === '3' ? 'badge-crimson' : (b.grade_code === '2' ? 'badge-gold' : (b.grade_code === '1' ? 'badge-blue' : 'badge-gray'));
      return `
        <div class="entity-card boss-card" onclick="window.inspectBoss('${b.id}')">
          <!-- Boss Official Artwork Banner -->
          <div class="boss-banner-frame">
            <img src="${b.portrait_img}" alt="${b.name}" class="boss-portrait-banner" onerror="this.src='assets/splash.png'">
            <div class="boss-banner-overlay"></div>
            <span class="entity-badge ${badgeColor} boss-grade-tag">
              ${b.grade_name}
            </span>
            <span class="entity-badge badge-blue boss-level-tag">${b.level_display || 'Nv. ' + b.level}</span>
          </div>

          <div style="padding: 16px 20px 20px;">
            <div class="entity-title" style="margin-top: 4px;">${b.name}</div>
            <div style="font-size: 0.82rem; color: var(--gold-primary); margin-bottom: 8px;">
              ${b.title}
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px;">
              ${b.instance_count > 1 ? `<span class="entity-badge badge-gold" style="font-size: 0.72rem;">👥 ${b.instance_count} Instâncias</span>` : ''}
              ${b.drops && b.drops.length ? `<span class="entity-badge badge-gold" style="font-size: 0.72rem;">📦 ${b.drops.length} Drops</span>` : ''}
              ${b.skills && b.skills.length ? `<span class="entity-badge badge-crimson" style="font-size: 0.72rem;">⚔️ ${b.skills.length} Golpes</span>` : ''}
              ${b.spawn_schedule ? `<span class="entity-badge badge-blue" style="font-size: 0.72rem;">⏰ ${b.spawn_schedule}</span>` : ''}
            </div>

            <p class="entity-desc">
              <strong>Local:</strong> ${b.world_map || 'Masmorra / Campo Dimensional'}<br>
              <strong>Atributo:</strong> ${b.attribute} • <strong>Aggro:</strong> ${b.is_aggressive ? 'Hostil' : 'Passivo'}
            </p>
            <div class="entity-meta-row">
              <span>❤️ HP: <strong style="color: #ef4444;">${formatBigNumber(b.hp_raw)}</strong></span>
              <span>⚔️ ATQ: <strong style="color: #eab308;">${formatBigNumber(b.atk_raw)}</strong></span>
              <span style="color: var(--crimson-light); font-weight: 600;">Detalhes →</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    if (pagination) {
      if (paginated.length < totalFiltered) {
        pagination.innerHTML = `
          <button class="filter-btn active" onclick="window.loadMoreBosses()">
            Carregar Mais Inimigos (${paginated.length} de ${totalFiltered})
          </button>
        `;
      } else {
        pagination.innerHTML = `<span style="font-size: 0.85rem; color: var(--text-dim);">Exibindo todos os ${totalFiltered} inimigos correspondentes.</span>`;
      }
    }
  }

  window.loadMoreBosses = function() {
    state.bossesPage++;
    renderBosses();
  };

  // Render Dungeons with Background Artworks
  function renderDungeons() {
    const container = document.getElementById('dungeonsContainer');
    if (!container || !state.data.dungeons) return;

    let filtered = state.data.dungeons;

    if (state.dungeonsFilter !== 'all') {
      filtered = filtered.filter(d => d.type_code === state.dungeonsFilter);
    }

    if (state.dungeonsSearchTerm.trim()) {
      const q = state.dungeonsSearchTerm.toLowerCase();
      filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(q) ||
        d.description.toLowerCase().includes(q) ||
        d.type_name.toLowerCase().includes(q)
      );
    }

    container.innerHTML = filtered.map(d => `
      <div class="entity-card dungeon-card" onclick="window.inspectDungeon('${d.id}')">
        <!-- Dungeon Artwork Banner -->
        <div class="dungeon-banner-frame">
          <img src="${d.bg_img}" alt="${d.name}" class="dungeon-banner-img" onerror="this.src='assets/splash.png'">
          <div class="dungeon-banner-overlay"></div>
          <span class="entity-badge badge-blue dungeon-type-tag">${d.type_name}</span>
        </div>

        <div style="padding: 16px 20px 20px;">
          <div class="entity-title">${d.name}</div>
          <p class="entity-desc">${d.description}</p>
          <div class="entity-meta-row">
            <span>Nv. Mínimo: <strong>${d.req_level}</strong></span>
            <span>Recomendado: <strong>${d.rec_level}</strong></span>
            <span style="color: var(--gold-primary);">Grau SS</span>
          </div>
        </div>
      </div>
    `).join('');
  }

  // Render Items with Official Weapon, Box, Sephira & Relic Icons
  function renderItems() {
    const container = document.getElementById('itemsContainer');
    const pagination = document.getElementById('itemsPagination');
    if (!container || !state.data.items) return;

    let filtered = state.data.items;

    if (state.itemsFilter !== 'all') {
      filtered = filtered.filter(i => i.category === state.itemsFilter || i.type_code === state.itemsFilter);
    }

    if (state.itemsSearchTerm.trim()) {
      const q = state.itemsSearchTerm.toLowerCase();
      filtered = filtered.filter(i =>
        i.name.toLowerCase().includes(q) ||
        i.desc.toLowerCase().includes(q) ||
        i.id.includes(q) ||
        i.type_name.toLowerCase().includes(q) ||
        (i.droppers && i.droppers.some(d => d.name.toLowerCase().includes(q) || (d.world && d.world.toLowerCase().includes(q))))
      );
    }

    const total = filtered.length;
    const pages = Math.ceil(total / state.itemsPerPage) || 1;
    if (state.itemsPage > pages) state.itemsPage = 1;

    const start = (state.itemsPage - 1) * state.itemsPerPage;
    const currentList = filtered.slice(start, start + state.itemsPerPage);

    container.innerHTML = currentList.map(item => `
      <div class="entity-card item-card" onclick="window.inspectItem('${item.id}')">
        <div class="entity-header">
          <div class="item-slot-frame">
            <img src="${item.icon_img}" alt="${item.name}" class="item-slot-img" onerror="this.src='assets/logo.png'">
          </div>
          <div style="flex: 1; margin-left: 14px;">
            <div class="entity-title" style="font-size: 1.05rem;">${item.name}</div>
            <div style="display: flex; gap: 8px; margin-top: 4px; flex-wrap: wrap;">
              <span class="entity-badge badge-gold" style="font-size: 0.7rem;">${item.type_name}</span>
              <span class="entity-badge badge-crimson" style="font-size: 0.7rem;">Tier ${item.tier}</span>
              ${item.droppers && item.droppers.length ? `<span class="entity-badge badge-blue" style="font-size: 0.68rem;">💀 ${item.droppers.length} Monstros</span>` : ''}
            </div>
          </div>
        </div>
        <p class="entity-desc">${item.desc}</p>
        <div class="entity-meta-row">
          <span>Peso: ${item.weight || '0'}</span>
          <span style="color: var(--crimson-light);">${item.max_enchant}</span>
        </div>
      </div>
    `).join('');

    renderPagination(pagination, state.itemsPage, pages, 'window.changeItemsPage');
  }

  window.changeItemsPage = function(page) {
    state.itemsPage = page;
    renderItems();
    document.getElementById('items').scrollIntoView({ behavior: 'smooth' });
  };

  // Shared Numeric Pagination Component
  function renderPagination(container, currentPage, totalPages, callbackName) {
    if (!container) return;
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    let html = `<div style="display: flex; justify-content: center; align-items: center; gap: 6px; flex-wrap: wrap;">`;

    // Previous Button
    if (currentPage > 1) {
      html += `<button class="filter-btn" onclick="${callbackName}(${currentPage - 1})">← Anterior</button>`;
    } else {
      html += `<button class="filter-btn" disabled style="opacity: 0.35; cursor: not-allowed;">← Anterior</button>`;
    }

    // Page window
    const delta = 2;
    const range = [];
    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }

    // Page 1
    html += `<button class="filter-btn ${currentPage === 1 ? 'active' : ''}" onclick="${callbackName}(1)">1</button>`;

    if (range.length && range[0] > 2) {
      html += `<span style="color: var(--text-dim); padding: 0 4px;">...</span>`;
    }

    range.forEach(p => {
      html += `<button class="filter-btn ${currentPage === p ? 'active' : ''}" onclick="${callbackName}(${p})">${p}</button>`;
    });

    if (range.length && range[range.length - 1] < totalPages - 1) {
      html += `<span style="color: var(--text-dim); padding: 0 4px;">...</span>`;
    }

    // Last Page
    if (totalPages > 1) {
      html += `<button class="filter-btn ${currentPage === totalPages ? 'active' : ''}" onclick="${callbackName}(${totalPages})">${totalPages}</button>`;
    }

    // Next Button
    if (currentPage < totalPages) {
      html += `<button class="filter-btn" onclick="${callbackName}(${currentPage + 1})">Próxima →</button>`;
    } else {
      html += `<button class="filter-btn" disabled style="opacity: 0.35; cursor: not-allowed;">Próxima →</button>`;
    }

    html += `</div>`;
    html += `<div style="margin-top: 8px; font-size: 0.8rem; color: var(--text-dim); text-align: center;">Página ${currentPage} de ${totalPages}</div>`;

    container.innerHTML = html;
  }

  // Render Quests & Tasks
  function renderQuests() {
    const container = document.getElementById('questsContainer');
    const pagination = document.getElementById('questsPagination');
    if (!container || !state.data.quests) return;

    let filtered = state.data.quests;

    if (state.questsFilter !== 'all') {
      filtered = filtered.filter(q => q.type === state.questsFilter);
    }

    if (state.questsSearchTerm.trim()) {
      const s = state.questsSearchTerm.toLowerCase();
      filtered = filtered.filter(q =>
        q.name.toLowerCase().includes(s) ||
        q.id.includes(s) ||
        q.type_pt.toLowerCase().includes(s)
      );
    }

    const total = filtered.length;
    const pages = Math.ceil(total / state.questsPerPage) || 1;
    if (state.questsPage > pages) state.questsPage = 1;

    const start = (state.questsPage - 1) * state.questsPerPage;
    const currentList = filtered.slice(start, start + state.questsPerPage);

    container.innerHTML = currentList.map(q => `
      <div class="entity-card quest-card" onclick="window.inspectQuest('${q.id}')">
        <div class="entity-header">
          <span class="entity-badge ${q.type === 'Scenario' ? 'badge-crimson' : q.type === 'Daily' ? 'badge-gold' : 'badge-blue'}">
            ${q.type_pt}
          </span>
          <span class="entity-id">Nv. ${q.req_level} Requerido</span>
        </div>
        <div class="entity-title" style="margin-top: 6px; font-size: 1.05rem;">${q.name}</div>
        <p class="entity-desc">
          ${q.has_instance ? '<strong>🎬 Instância Cinematográfica:</strong> Batalha com cutscenes narrativas privadas.<br>' : ''}
          ${q.pre_quest ? `<strong>Pré-requisito:</strong> Requer conclusão da Missão #${q.pre_quest}.<br>` : ''}
          Esta jornada envolve <strong>${q.tasks_count} etapas de tarefas</strong> sequenciais e concede até <strong>${q.rewards_count} grupos de recompensas</strong> de EXP e espólios.
        </p>
        <div class="entity-meta-row">
          <span>${q.tasks_count} Tarefas</span>
          <span style="color: var(--gold-primary);">${q.rewards_count} Recompensas</span>
          <span style="color: var(--crimson-light); font-weight: 600;">Ver Detalhes →</span>
        </div>
      </div>
    `).join('');

    renderPagination(pagination, state.questsPage, pages, 'window.changeQuestsPage');
  }

  window.changeQuestsPage = function(page) {
    state.questsPage = page;
    renderQuests();
    document.getElementById('quests').scrollIntoView({ behavior: 'smooth' });
  };

  // Render Crafting & Forge
  function renderCrafting() {
    const container = document.getElementById('craftingContainer');
    const pagination = document.getElementById('craftingPagination');
    if (!container || !state.data.crafting) return;

    let filtered = state.data.crafting;

    if (state.craftingFilter !== 'all') {
      filtered = filtered.filter(c => c.category === state.craftingFilter);
    }

    if (state.craftingSearchTerm.trim()) {
      const s = state.craftingSearchTerm.toLowerCase();
      filtered = filtered.filter(c =>
        c.target_name.toLowerCase().includes(s) ||
        c.tab_name.toLowerCase().includes(s) ||
        c.id.includes(s) ||
        c.materials.some(m => m.name.toLowerCase().includes(s))
      );
    }

    const total = filtered.length;
    const pages = Math.ceil(total / state.craftingPerPage) || 1;
    if (state.craftingPage > pages) state.craftingPage = 1;

    const start = (state.craftingPage - 1) * state.craftingPerPage;
    const currentList = filtered.slice(start, start + state.craftingPerPage);

    container.innerHTML = currentList.map(c => `
      <div class="entity-card craft-card" onclick="window.inspectRecipe('${c.id}')">
        <div class="entity-header">
          <div class="item-slot-frame" style="width: 44px; height: 44px;">
            <img src="${c.icon_img}" alt="${c.target_name}" class="item-slot-img" onerror="this.src='assets/logo.png'">
          </div>
          <div style="flex: 1; margin-left: 12px;">
            <div class="entity-title" style="font-size: 1rem;">${c.target_name}</div>
            <div style="display: flex; gap: 6px; margin-top: 3px;">
              <span class="entity-badge badge-gold" style="font-size: 0.68rem;">${c.tab_name}</span>
              <span class="entity-badge ${c.big_success_rate !== '0%' ? 'badge-blue' : 'badge-crimson'}" style="font-size: 0.68rem;">
                Sucesso: ${c.success_rate} ${c.big_success_rate !== '0%' ? '• Gr. Sucesso: ' + c.big_success_rate : ''}
              </span>
            </div>
          </div>
        </div>
        <div style="margin: 12px 0 8px; font-size: 0.82rem; color: #94a3b8;">
          <div style="font-weight: 700; color: #cbd5e1; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
            <span>Materiais Necessários:</span>
            <span style="font-size: 0.72rem; color: #94a3b8;">${c.materials.length} insumos</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 4px;">
            ${c.materials.slice(0, 3).map(m => `
              <div style="display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.25); padding: 3px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04);">
                <img src="${m.icon || 'assets/items/flat_itemcraft.png'}" alt="${m.name}" style="width: 20px; height: 20px; border-radius: 3px; object-fit: contain; background: rgba(0,0,0,0.3);" onerror="this.src='assets/logo.png'">
                <span style="flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #cbd5e1; font-size: 0.78rem;">${m.name}</span>
                <span style="font-weight: 700; color: #f59e0b; font-family: monospace; font-size: 0.8rem;">×${Number(m.amount).toLocaleString('pt-BR')}</span>
              </div>
            `).join('')}
            ${c.materials.length > 3 ? `<div style="font-size: 0.72rem; color: var(--crimson-light); text-align: right; padding-right: 4px;">+ mais ${c.materials.length - 3} insumos...</div>` : ''}
          </div>
        </div>
        <div class="entity-meta-row" style="margin-top: 10px;">
          <span>${c.materials.length} Insumos</span>
          <span style="color: ${c.tradeable_on_big ? '#38bdf8' : '#94a3b8'};">
            ${c.tradeable_on_big ? '💎 Negociável no Leilão' : '🔒 Vinculado'}
          </span>
          <span style="color: var(--crimson-light); font-weight: 600;">Forjar →</span>
        </div>
      </div>
    `).join('');

    renderPagination(pagination, state.craftingPage, pages, 'window.changeCraftingPage');
  }

  window.changeCraftingPage = function(page) {
    state.craftingPage = page;
    renderCrafting();
    document.getElementById('crafting').scrollIntoView({ behavior: 'smooth' });
  };

  // Render Game Modes
  function renderModes() {
    const container = document.getElementById('modesContainer');
    if (!container || !state.data.modes) return;

    let filtered = state.data.modes;
    if (state.modesFilter !== 'all') {
      filtered = filtered.filter(m => m.category === state.modesFilter);
    }

    container.innerHTML = filtered.map(m => `
      <div class="entity-card mode-card" onclick="window.inspectMode('${m.id}')" style="display: flex; flex-direction: column;">
        <div class="entity-header">
          <div class="item-slot-frame" style="width: 52px; height: 52px; border-color: rgba(212,175,55,0.4);">
            <img src="${m.icon_img}" alt="${m.title}" class="item-slot-img" onerror="this.src='assets/logo.png'">
          </div>
          <div style="flex: 1; margin-left: 12px;">
            <div class="entity-title" style="font-size: 1.05rem;">${m.title}</div>
            <div style="display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap;">
              <span class="entity-badge badge-gold" style="font-size: 0.68rem;">${m.category_label}</span>
              <span class="entity-badge badge-crimson" style="font-size: 0.68rem;">${m.badge}</span>
            </div>
          </div>
        </div>

        <div style="margin: 12px 0; font-size: 0.83rem; color: #cbd5e1; line-height: 1.5; flex: 1;">
          ${m.description}
        </div>

        <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.78rem; display: flex; flex-direction: column; gap: 4px; border: 1px solid rgba(255,255,255,0.05);">
          <div style="display: flex; justify-content: space-between;"><strong style="color: #94a3b8;">Capacidade:</strong> <span style="color: #38bdf8;">${m.capacity}</span></div>
          <div style="display: flex; justify-content: space-between;"><strong style="color: #94a3b8;">Nível Recomendado:</strong> <span style="color: #fbbf24;">${m.level_range}</span></div>
          <div style="display: flex; justify-content: space-between;"><strong style="color: #94a3b8;">Requisito de Entrada:</strong> <span style="color: #e2e8f0; font-size: 0.72rem;">${m.cost}</span></div>
        </div>

        <div class="entity-meta-row" style="margin-top: auto;">
          <span>${m.instances_count} Instâncias</span>
          <span style="color: var(--crimson-light); font-weight: 600;">Ver Detalhes →</span>
        </div>
      </div>
    `).join('');
  }

  // Render PvP Systems
  function renderPvP() {
    const container = document.getElementById('pvpContentContainer');
    if (!container || !state.data.pvp) return;

    const p = state.data.pvp;

    if (state.pvpTab === 'arena') {
      const a = p.arena;
      container.innerHTML = `
        <div style="background: rgba(138, 3, 3, 0.12); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
            <div>
              <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${a.title}</h3>
              <p style="color: var(--gold-primary); font-size: 0.9rem; margin-bottom: 8px;">${a.subtitle}</p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <span class="entity-badge badge-crimson" style="font-size: 0.8rem;">Formato: ${a.format}</span>
              <span class="entity-badge badge-gold" style="font-size: 0.8rem;">Duração: ${a.duration}</span>
              <span class="entity-badge badge-blue" style="font-size: 0.8rem;">Vitória: ${a.target_score}</span>
            </div>
          </div>
          <div style="font-size: 0.85rem; color: #cbd5e1; margin-top: 10px; line-height: 1.5;">
            <strong>Mecânicas de Combate:</strong> Partida de 5v5 cronometrada em arena espelhada (Vermelho vs Azul) com barreiras de spawn mágicas e controle de relíquias ativas. A primeira equipe a somar 10 mortes conquista a vitória.
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; margin-bottom: 24px;">
          <div>
            <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
              <span>🗺️ Mapa Tático da Arena</span>
              <span style="font-size: 0.75rem; color: var(--gold-primary);">(${a.map_name})</span>
            </h4>
            <div class="tactical-map-container">
              <img src="${a.map_image}" alt="Mapa da Arena" class="tactical-map-img" onerror="this.src='assets/logo.png'">
            </div>
          </div>

          <div>
            <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 12px;">🏆 As 5 Ligas Competitivas</h4>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              ${a.leagues.map(l => `
                <div class="league-row">
                  <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <strong style="color: #fff; font-size: 0.95rem;">${l.name}</strong>
                      <span class="entity-badge ${l.badge}" style="font-size: 0.7rem;">${l.bp_req}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 3px;">${l.desc}</div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 14px;">⚡ As 4 Especializações de Arena (Arena Traits)</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
          ${a.traits.map(t => `
            <div class="trait-card">
              <div class="item-slot-frame" style="width: 48px; height: 48px;">
                <img src="${t.icon}" alt="${t.name}" class="item-slot-img" onerror="this.src='assets/logo.png'">
              </div>
              <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                  <strong style="color: #fff; font-size: 0.92rem;">${t.name}</strong>
                  <span style="font-size: 0.68rem; color: #38bdf8;">${t.skillset}</span>
                </div>
                <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 4px; line-height: 1.4;">
                  ${t.desc}
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    } else if (state.pvpTab === 'conquest') {
      const c = p.conquest;
      container.innerHTML = `
        <div style="background: rgba(138, 3, 3, 0.12); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;">
          <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${c.title}</h3>
          <p style="color: var(--gold-primary); font-size: 0.9rem; margin-bottom: 10px;">${c.subtitle}</p>
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <span class="entity-badge badge-crimson" style="font-size: 0.8rem;">🗓️ ${c.schedule}</span>
            <span class="entity-badge badge-gold" style="font-size: 0.8rem;">⏱️ ${c.countdown}</span>
          </div>
        </div>

        <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 14px;">🗺️ Mapas de Guerra & Fortificações</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; margin-bottom: 24px;">
          ${c.maps.map(m => `
            <div style="background: rgba(15,20,30,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md); overflow: hidden;">
              <div class="tactical-map-container" style="border: none; border-radius: 0; margin-bottom: 0;">
                <img src="${m.image}" alt="${m.name}" class="tactical-map-img" style="max-height: 320px;" onerror="this.src='assets/logo.png'">
              </div>
              <div style="padding: 16px;">
                <h5 style="color: #fff; font-size: 1rem; margin-bottom: 2px;">${m.name}</h5>
                <span class="entity-badge badge-blue" style="font-size: 0.7rem; margin-bottom: 8px;">${m.type}</span>
                <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; margin-top: 6px;">${m.desc}</p>
              </div>
            </div>
          `).join('')}
        </div>

        <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 12px;">💎 Tiers de Conquista & Privilégios de Guilda</h4>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${c.tiers.map(t => `
            <div class="league-row">
              <span class="entity-badge ${t.badge}" style="font-size: 0.8rem; width: 130px; text-align: center;">${t.name}</span>
              <strong style="color: #fbbf24; width: 120px; font-family: monospace;">${t.points}</strong>
              <div style="flex: 1; font-size: 0.82rem; color: #cbd5e1;">${t.privilege}</div>
            </div>
          `).join('')}
        </div>
      `;
    } else if (state.pvpTab === 'pk') {
      const k = p.pk_system;
      container.innerHTML = `
        <div style="background: rgba(138, 3, 3, 0.12); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;">
          <div style="display: flex; align-items: center; gap: 14px;">
            <img src="${k.penalty_mark}" alt="Marca de Penalidade" style="width: 48px; height: 48px; object-fit: contain;" onerror="this.src='assets/logo.png'">
            <div>
              <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${k.title}</h3>
              <p style="color: var(--gold-primary); font-size: 0.9rem;">${k.subtitle}</p>
            </div>
          </div>
        </div>

        <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 14px;">💀 Os 5 Níveis de Penalidade de Karma (PvpPenaltySetting)</h4>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px;">
          ${k.penalty_levels.map(l => `
            <div style="background: rgba(0,0,0,0.35); border-left: 4px solid ${l.color}; border-radius: 6px; padding: 12px 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
              <span class="entity-badge" style="background: ${l.color}; color: #fff; font-weight: 700;">Nível ${l.level}</span>
              <strong style="color: #fbbf24; font-family: monospace; width: 100px;">${l.points}</strong>
              <div style="font-weight: 600; color: #fff; width: 180px;">${l.status}</div>
              <div style="flex: 1; font-size: 0.82rem; color: #cbd5e1; min-width: 250px;">${l.effects}</div>
            </div>
          `).join('')}
        </div>

        <div style="background: rgba(15,20,30,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md); padding: 18px; margin-bottom: 24px;">
          <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 8px;">📡 ${k.revenge_radar.title}</h4>
          <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 12px;">${k.revenge_radar.desc}</p>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
            <div><strong style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">Capacidade</strong><div style="color: #38bdf8; font-weight: 600;">${k.revenge_radar.max_targets}</div></div>
            <div><strong style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">Alcance de Detecção</strong><div style="color: #fbbf24; font-weight: 600;">${k.revenge_radar.radar_range}</div></div>
            <div><strong style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">Duração do Alerta</strong><div style="color: #a78bfa; font-weight: 600;">${k.revenge_radar.duration}</div></div>
            <div><strong style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">Taxa de Atualização</strong><div style="color: #34d399; font-weight: 600;">${k.revenge_radar.refresh_rate}</div></div>
          </div>
        </div>

        <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 12px;">⚔️ Atributos Exclusivos de Combate PvP (EStat)</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 10px;">
          ${k.pvp_stats.map(s => `
            <div style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 10px 14px;">
              <div style="color: #f87171; font-weight: 600; font-size: 0.88rem;">${s.name}</div>
              <div style="font-size: 0.7rem; color: #94a3b8; font-family: monospace;">${s.stat}</div>
              <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 4px;">${s.desc}</div>
            </div>
          `).join('')}
        </div>
      `;
    } else if (state.pvpTab === 'tournament') {
      const t = p.world_tournament;
      container.innerHTML = `
        <div style="background: rgba(138, 3, 3, 0.12); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;">
          <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${t.title}</h3>
          <p style="color: var(--gold-primary); font-size: 0.9rem; margin-bottom: 8px;">${t.subtitle}</p>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="entity-badge badge-crimson">${t.format}</span>
            <span class="entity-badge badge-gold">${t.schedule}</span>
          </div>
        </div>
        <div style="background: rgba(15,20,30,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md); padding: 18px; margin-bottom: 20px;">
          <h4 style="font-size: 1.1rem; color: #fff; margin-bottom: 8px;">Regras do Campeonato Inter-Servidores</h4>
          <p style="font-size: 0.86rem; color: #cbd5e1; line-height: 1.6;">${t.desc}</p>
        </div>
        <div style="background: rgba(0,0,0,0.3); border-radius: var(--radius-md); padding: 16px; border: 1px solid rgba(212,175,55,0.2);">
          <h5 style="color: #fbbf24; margin-bottom: 6px;">Premiações de Soberania</h5>
          <p style="color: #34d399; font-size: 0.85rem;">${t.rewards_sample}</p>
        </div>
      `;
    } else if (state.pvpTab === 'nobility') {
      const n = p.nobility_titles;
      if (!n) return;
      container.innerHTML = `
        <div style="background: rgba(138, 3, 3, 0.12); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: var(--radius-md); padding: 20px; margin-bottom: 24px;">
          <div style="display: flex; align-items: center; gap: 16px;">
            <img src="${n.icon}" alt="Títulos de Nobreza" style="width: 52px; height: 52px; object-fit: contain;" onerror="this.src='assets/logo.png'">
            <div>
              <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: #fff; margin-bottom: 4px;">${n.title}</h3>
              <p style="color: var(--gold-primary); font-size: 0.9rem;">${n.subtitle}</p>
            </div>
          </div>
        </div>

        <!-- Technical Divergence Alert -->
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #f59e0b; border-radius: var(--radius-md); padding: 14px 18px; margin-bottom: 24px;">
          <strong style="color: #fbbf24; font-size: 0.92rem; display: block; margin-bottom: 4px;">⚠️ Análise Técnica de Engenharia Reversa: Divergência de Atributos</strong>
          <p style="font-size: 0.84rem; color: #cbd5e1; line-height: 1.5; margin: 0;">
            ${n.rules.divergence_note}
          </p>
        </div>

        <h4 style="font-size: 1.15rem; color: #fff; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
          <span>👑 Os 5 Títulos de Nobreza da Temporada</span>
          <span style="font-size: 0.75rem; color: var(--gold-primary); font-weight: normal;">(RankingRewardId 39 a 43)</span>
        </h4>

        <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 28px;">
          ${n.rankings.map(r => `
            <div style="background: rgba(15,20,30,0.65); border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid ${r.color}; border-radius: var(--radius-md); padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
              <div style="display: flex; align-items: center; gap: 16px; min-width: 220px;">
                <div class="item-slot-frame" style="width: 52px; height: 52px; border-color: ${r.color};">
                  <img src="${r.icon}" alt="${r.title}" class="item-slot-img" onerror="this.src='assets/logo.png'">
                </div>
                <div>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <strong style="font-size: 1.15rem; color: #fff;">${r.title}</strong>
                    <span class="entity-badge ${r.badge}">${r.position}</span>
                  </div>
                  <div style="font-size: 0.74rem; color: #94a3b8; font-family: monospace; margin-top: 3px;">
                    Skill: ${r.skill_id} • Efeito: ${r.effect_id}
                  </div>
                </div>
              </div>

              <div style="flex: 1; min-width: 260px;">
                <div style="font-size: 0.78rem; color: #38bdf8; font-weight: 600; margin-bottom: 2px;">
                  ✨ Passiva de Nobreza: ${r.bonus_skill}
                </div>
                <div style="font-size: 0.83rem; color: #cbd5e1; line-height: 1.4;">
                  ${r.effects_summary}
                </div>
              </div>

              <div style="text-align: right; min-width: 110px;">
                <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim);">Recompensa RP</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #fbbf24; font-family: monospace;">${r.rp_reward}</div>
              </div>
            </div>
          `).join('')}
        </div>

        <h4 style="font-size: 1.15rem; color: #fff; margin-bottom: 14px;">📊 Os 4 Pilares de Pontuação do Ranking Geral</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 28px;">
          ${n.ranking_pillars.map(pill => `
            <div style="background: rgba(15,20,30,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md); padding: 18px;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <img src="${pill.icon}" alt="${pill.name}" style="width: 32px; height: 32px; object-fit: contain;">
                <strong style="color: #fff; font-size: 0.95rem;">${pill.name}</strong>
              </div>
              <p style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5; margin: 0;">${pill.desc}</p>
            </div>
          `).join('')}
        </div>

        <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(212,175,55,0.25); border-radius: var(--radius-md); padding: 20px;">
          <h4 style="font-size: 1.05rem; color: var(--gold-primary); margin-bottom: 12px;">📜 Regras de Concessão, Renovação e Desempate</h4>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; font-size: 0.84rem; color: #cbd5e1; line-height: 1.6;">
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 3px;">🗓️ Ciclo Sazonal e Reset</strong>
              ${n.rules.schedule}. O título dura rigorosamente até o encerramento da temporada ativa.
            </div>
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 3px;">👤 Menu de Personagem</strong>
              ${n.rules.menu_location}. Ao conquistar um novo título na temporada seguinte, os benefícios e bônus do título anterior são substituídos.
            </div>
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 3px;">⚖️ Critério de Desempate</strong>
              ${n.rules.tiebreaker}
            </div>
          </div>
        </div>
      `;
    }
  }

  // Render Item Enchantment / Upgrade
  function renderEnchantment() {
    const container = document.getElementById('enchantmentContentContainer');
    if (!container || !state.data.enchantment) return;

    const enc = state.data.enchantment;

    if (state.enchantTab === 'scrolls') {
      container.innerHTML = `
        <!-- Summary Metric Badges -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px;">
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 14px; text-align: center;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px;">Regras Mapeadas</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: var(--gold-primary); font-family: monospace;">${enc.summary.total_rules.toLocaleString()}</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Extraídas de ItemEnchant.csv</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 14px; text-align: center;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px;">Tipos de Equipamentos</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #38bdf8; font-family: monospace;">${enc.summary.equipment_types_count} Categorias</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Armas, Armaduras, Joias, Relíquias</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 14px; text-align: center;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px;">Zona Segura Garantida</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #34d399; font-family: monospace;">+0 até +5</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">100% Sucesso • 0% Quebra</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 14px; text-align: center;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px;">Multi-Encantamento</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #a78bfa; font-family: monospace;">Até +11</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">ItemEnchant.MultiEnchant... = 11</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-sm); padding: 14px; text-align: center;">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px;">Nível Máximo do Jogo</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: var(--crimson-light); font-family: monospace;">+15</div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Auction.FilterMaxEnchantLevel</div>
          </div>
        </div>

        <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
          <span>📜 Os 3 Pergaminhos de Aprimoramento</span>
          <span style="font-size: 0.75rem; color: var(--gold-primary); font-weight: normal;">(EOperationType)</span>
        </h3>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 28px;">
          ${enc.scrolls.map(s => `
            <div style="background: rgba(15,20,30,0.65); border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius-md); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; position: relative;">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                  <div style="display: flex; gap: 10px;">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                      <img src="${s.weapon_icon}" alt="Arma" title="Versão de Armas" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 0 6px rgba(0,0,0,0.8));">
                      <span style="font-size: 0.65rem; color: #94a3b8;">Arma</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                      <img src="${s.armor_icon}" alt="Armadura" title="Versão de Armaduras" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 0 6px rgba(0,0,0,0.8));">
                      <span style="font-size: 0.65rem; color: #94a3b8;">Armadura</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
                      <img src="${s.acc_icon}" alt="Acessório" title="Versão de Acessórios" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 0 6px rgba(0,0,0,0.8));">
                      <span style="font-size: 0.65rem; color: #94a3b8;">Acessório</span>
                    </div>
                  </div>
                  <span class="entity-badge ${s.badge}">${s.tag}</span>
                </div>

                <h4 style="color: #fff; font-size: 1.1rem; margin-bottom: 6px;">${s.name}</h4>
                <div style="font-size: 0.75rem; color: var(--gold-primary); font-family: monospace; margin-bottom: 12px;">EOperationType: ${s.type_code}</div>
                <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 16px;">${s.description}</p>
              </div>

              <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 12px; font-size: 0.8rem; display: flex; flex-direction: column; gap: 6px;">
                <div style="display: flex; justify-content: space-between;">
                  <span style="color: #94a3b8;">Zona Segura:</span>
                  <strong style="color: #34d399;">${s.safe_zone}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span style="color: #94a3b8;">Regra de Risco:</span>
                  <strong style="color: #f87171;">${s.risk_start}</strong>
                </div>
              </div>
            </div>
          `).join('')}
        </div>

        <!-- Technical Mechanics Breakdown -->
        <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(212,175,55,0.25); border-radius: var(--radius-md); padding: 20px;">
          <h4 style="font-size: 1.05rem; color: var(--gold-primary); margin-bottom: 10px;">⚙️ Modos de Aprimoramento no Cliente</h4>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 4px;">1. Aprimoramento Simples (Single Step)</strong>
              Consome 1 pergaminho e ouro proporcional à categoria. Em caso de sucesso, o item ganha +1 nível. A partir do +6, se falhar na rolagem de BreakRate, o item quebra e é destruído irreversivelmente.
            </div>
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 4px;">2. Multi-Encantamento Sequencial (Auto-Enchant)</strong>
              O jogo permite definir uma meta automática de nível até o limite de <strong>+11</strong> (<code style="color: #fbbf24;">MultiEnchantSequenceEnchantLevel</code>). A sequência para automaticamente se a meta for atingida ou se o item quebrar.
            </div>
            <div>
              <strong style="color: #fff; display: block; margin-bottom: 4px;">3. Estratégia do Pergaminho Amaldiçoado</strong>
              Com 100% de taxa de redução (<code style="color: #f87171;">CurseRate = 10.000</code>), ele é empregado por jogadores avançados para rebaixar itens do +7 de volta ao +6 para tentar novamente o salto duplo do pergaminho abençoado (+6 ➔ +8).
            </div>
          </div>
        </div>
      `;
    } else if (state.enchantTab === 'rates') {
      container.innerHTML = `
        <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 6px;">⚖️ Análise Comparativa de Taxas no Primeiro Nível de Risco (+6)</h3>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 18px;">
          Do +0 ao +5 todas as categorias possuem 100% de sucesso. Ao tentar elevar para +6, entram em vigor as taxas de quebra e diferenciação de custos:
        </p>

        <div style="overflow-x: auto; margin-bottom: 24px;">
          <table class="skills-table" style="background: rgba(15,20,30,0.6); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <thead>
              <tr style="background: rgba(0,0,0,0.5);">
                <th style="padding: 14px;">Categoria de Equipamento</th>
                <th style="padding: 14px;">Custo em Ouro</th>
                <th style="padding: 14px;">Sucesso Normal</th>
                <th style="padding: 14px;">Taxa de Quebra (BreakRate)</th>
                <th style="padding: 14px;">Salto Duplo (Abençoado)</th>
                <th style="padding: 14px;">Perfil de Risco</th>
              </tr>
            </thead>
            <tbody>
              ${enc.transition_rates.map(r => `
                <tr>
                  <td style="padding: 14px; font-weight: 600; color: #fff;">${r.category}</td>
                  <td style="padding: 14px; color: #fbbf24; font-family: monospace; font-weight: 600;">${r.gold_cost}</td>
                  <td style="padding: 14px; color: #34d399; font-weight: 600;">${r.normal_success}</td>
                  <td style="padding: 14px; color: #f87171; font-weight: 700;">${r.break_rate}</td>
                  <td style="padding: 14px; color: #a78bfa; font-weight: 600;">${r.big_success}</td>
                  <td style="padding: 14px;"><span class="entity-badge ${r.risk_badge}">${r.risk_profile}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
          <div style="background: rgba(0,0,0,0.25); border-left: 3px solid #34d399; padding: 14px 18px; border-radius: 4px;">
            <strong style="color: #34d399; display: block; margin-bottom: 4px;">Armas: Maior Tolerância Inicial</strong>
            <p style="font-size: 0.82rem; color: #cbd5e1; margin: 0; line-height: 1.5;">
              As armas possuem 85% de sucesso e apenas 15% de quebra no +6. Isso incentiva os jogadores a buscarem o +7 para desbloquear o salto de dano e precisão com menor receio de perda imediata.
            </p>
          </div>
          <div style="background: rgba(0,0,0,0.25); border-left: 3px solid #f87171; padding: 14px 18px; border-radius: 4px;">
            <strong style="color: #f87171; display: block; margin-bottom: 4px;">Acessórios: Os Mais Arriscados</strong>
            <p style="font-size: 0.82rem; color: #cbd5e1; margin: 0; line-height: 1.5;">
              Com 60% de taxa de quebra já no +6 e custo elevado (8.500 Gold), os anéis e braceletes representam o maior sumidouro de recursos do jogo, tornando joias +7 ou superiores raríssimas no mercado.
            </p>
          </div>
          <div style="background: rgba(0,0,0,0.25); border-left: 3px solid var(--gold-primary); padding: 14px 18px; border-radius: 4px;">
            <strong style="color: var(--gold-primary); display: block; margin-bottom: 4px;">Relíquias Funerárias: Custo Máximo</strong>
            <p style="font-size: 0.82rem; color: #cbd5e1; margin: 0; line-height: 1.5;">
              Máscaras, Cálices e Perfumes cobram 15.000 Gold por tentativa com taxa de 50/50 no +6, configurando investimentos de ponta para a linhagem de sangue no end-game.
            </p>
          </div>
        </div>
      `;
    } else if (state.enchantTab === 'progression_weapon') {
      container.innerHTML = `
        <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 6px;">🗡️ Tabela de Progressão de Armas (+0 a +15)</h3>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 18px;">
          Exemplo com a Espada Comum (ItemEnchantLevel 0 a 15). Atributos cumulativos com marcos de precisão e bônus de ataque:
        </p>

        <div style="overflow-x: auto;">
          <table class="skills-table" style="background: rgba(15,20,30,0.6); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <thead>
              <tr style="background: rgba(0,0,0,0.5);">
                <th style="padding: 12px 14px;">Nível</th>
                <th style="padding: 12px 14px;">Sucesso</th>
                <th style="padding: 12px 14px;">Quebra</th>
                <th style="padding: 12px 14px;">Custo (Gold)</th>
                <th style="padding: 12px 14px;">Poder de Ataque</th>
                <th style="padding: 12px 14px;">Precisão (HitValue)</th>
                <th style="padding: 12px 14px;">Crítico</th>
                <th style="padding: 12px 14px;">Status / Marco</th>
              </tr>
            </thead>
            <tbody>
              ${enc.sword_progression.map(s => {
                const isSafe = s.break === '0%';
                const isMilestone = s.level === '+7' || s.level === '+10' || s.level === '+15';
                const rowBg = isMilestone ? 'background: rgba(212, 175, 55, 0.08);' : (isSafe ? '' : 'background: rgba(220, 38, 38, 0.04);');
                return `
                  <tr style="${rowBg}">
                    <td style="padding: 12px 14px; font-weight: 700; color: ${isSafe ? '#34d399' : (isMilestone ? 'var(--gold-primary)' : '#f87171')}; font-size: 1rem; font-family: monospace;">${s.level}</td>
                    <td style="padding: 12px 14px; color: #34d399; font-weight: 600;">${s.succ}</td>
                    <td style="padding: 12px 14px; color: ${isSafe ? '#94a3b8' : '#f87171'}; font-weight: ${isSafe ? 'normal' : '700'};">${s.break}</td>
                    <td style="padding: 12px 14px; color: #fbbf24; font-family: monospace;">${s.gold}</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #fff;">${s.atk}</td>
                    <td style="padding: 12px 14px; color: ${s.hit !== '—' ? '#38bdf8' : '#64748b'}; font-weight: ${s.hit !== '—' ? '700' : 'normal'};">${s.hit}</td>
                    <td style="padding: 12px 14px; color: #cbd5e1;">${s.crit}</td>
                    <td style="padding: 12px 14px; font-size: 0.8rem; color: ${isMilestone ? 'var(--gold-primary)' : '#94a3b8'}; font-weight: ${isMilestone ? '600' : 'normal'};">${s.status}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    } else if (state.enchantTab === 'progression_acc') {
      container.innerHTML = `
        <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 6px;">💍 Tabela de Progressão de Acessórios & Joias</h3>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 18px;">
          Exemplo com Cinto/Bracelete Ancestral. Acessórios concedem mitigação direta de dano físico e precisão contra magias inimigas:
        </p>

        <div style="overflow-x: auto;">
          <table class="skills-table" style="background: rgba(15,20,30,0.6); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <thead>
              <tr style="background: rgba(0,0,0,0.5);">
                <th style="padding: 12px 14px;">Nível</th>
                <th style="padding: 12px 14px;">Redução de Dano (AttackPowerReduction)</th>
                <th style="padding: 12px 14px;">Precisão de Habilidade (HitValueSkill)</th>
                <th style="padding: 12px 14px;">Redução Crítica (CriticalRateReduction)</th>
                <th style="padding: 12px 14px;">Status / Marco</th>
              </tr>
            </thead>
            <tbody>
              ${enc.accessory_progression.map(a => {
                const isMilestone = a.level === '+5' || a.level === '+10' || a.level === '+15';
                const rowBg = isMilestone ? 'background: rgba(56, 189, 248, 0.08);' : '';
                return `
                  <tr style="${rowBg}">
                    <td style="padding: 12px 14px; font-weight: 700; color: ${isMilestone ? '#38bdf8' : '#fff'}; font-size: 1rem; font-family: monospace;">${a.level}</td>
                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700;">${a.dmg_red}</td>
                    <td style="padding: 12px 14px; color: ${a.skill_hit !== '—' ? '#38bdf8' : '#64748b'}; font-weight: ${a.skill_hit !== '—' ? '700' : 'normal'};">${a.skill_hit}</td>
                    <td style="padding: 12px 14px; color: #cbd5e1;">${a.crit_red}</td>
                    <td style="padding: 12px 14px; font-size: 0.8rem; color: ${isMilestone ? '#38bdf8' : '#94a3b8'}; font-weight: ${isMilestone ? '600' : 'normal'};">${a.status}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    } else if (state.enchantTab === 'artifacts') {
      const art = enc.artifact_transformation || {
        name: "Transformação I (Óleo de Unção de Olga)",
        unlock_level: 100,
        unlock_lock_id: "91010",
        craft_recipe_reqs: "180x Pedra de Aprimoramento de Artefato, 25x Trindade, 30.000 Gold",
        progression: []
      };

      container.innerHTML = `
        <div style="background: rgba(15,20,30,0.7); border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 22px; margin-bottom: 24px; position: relative; overflow: hidden;">
          <div style="position: absolute; right: -20px; top: -20px; font-size: 8rem; opacity: 0.05; pointer-events: none;">🏺</div>
          <div style="display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap;">
            <img src="${art.material_icon || 'assets/items/materials_artifactenchantmaterial_04.png'}" style="width: 72px; height: 72px; border-radius: 10px; border: 2px solid var(--gold-primary); background: rgba(0,0,0,0.5); padding: 4px;" onerror="this.src='assets/logo.png'">
            <div style="flex: 1; min-width: 260px;">
              <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">
                <span class="entity-badge badge-gold" style="font-size: 0.75rem;">🌟 Novo Artefato (Patch 31/10/2026)</span>
                <span class="entity-badge badge-crimson" style="font-size: 0.75rem;">🔓 Desbloqueio: Nível ${art.unlock_level} (ContentsLock ${art.unlock_lock_id})</span>
                <span class="entity-badge badge-blue" style="font-size: 0.75rem;">🛡️ 0% Falha / Sem Quebra</span>
              </div>
              <h3 style="font-size: 1.4rem; color: #fff; margin: 0 0 8px 0;">${art.name}</h3>
              <p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.5; margin: 0 0 12px 0;">
                ${art.description}
              </p>
              <div style="background: rgba(0,0,0,0.4); border-left: 3px solid #38bdf8; padding: 10px 14px; border-radius: 6px; font-size: 0.82rem; color: #94a3b8;">
                <strong style="color: #38bdf8;">🔨 Receita na Forja (ID ${art.craft_recipe_id}):</strong> Confeccione a <em>${art.material_name}</em> usando <strong style="color: #fff;">${art.craft_recipe_reqs}</strong> na aba de Criação de Materiais (402).
              </div>
            </div>
          </div>
        </div>

        <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 6px;">📊 Ciclo de Mitigação dos 20 Níveis de Aprimoramento</h3>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 18px;">
          O aprimoramento avança em ciclos ordenados de 4 níveis por disciplina defensiva. Não há risco de quebra (<code style="color: #34d399;">EnchantFailRate = 0</code>):
        </p>

        <div style="overflow-x: auto;">
          <table class="skills-table" style="background: rgba(15,20,30,0.6); border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <thead>
              <tr style="background: rgba(0,0,0,0.5);">
                <th style="padding: 12px 14px;">Nível</th>
                <th style="padding: 12px 14px;">Disciplina</th>
                <th style="padding: 12px 14px;">Atributo Reduzido</th>
                <th style="padding: 12px 14px;">Bônus</th>
                <th style="padding: 12px 14px;">Custo (Pedras)</th>
                <th style="padding: 12px 14px;">Custo (Gold)</th>
                <th style="padding: 12px 14px;">Sucesso Nv 1/2/3</th>
                <th style="padding: 12px 14px;">Falha</th>
              </tr>
            </thead>
            <tbody>
              ${(art.progression || []).map(p => {
                const isDisciplineStart = p.level === '+1' || p.level === '+5' || p.level === '+9' || p.level === '+13' || p.level === '+17';
                const rowBg = isDisciplineStart ? 'background: rgba(245, 158, 11, 0.06);' : '';
                return `
                  <tr style="${rowBg}">
                    <td style="padding: 12px 14px; font-weight: 700; color: #fbbf24; font-family: monospace; font-size: 0.95rem;">${p.level}</td>
                    <td style="padding: 12px 14px;"><span class="entity-badge ${p.discipline_badge}" style="font-size: 0.72rem;">${p.discipline}</span></td>
                    <td style="padding: 12px 14px; color: #fff; font-weight: 600;">${p.stat_name} <span style="font-size: 0.75rem; color: #64748b; font-family: monospace; display: block;">${p.stat_key}</span></td>
                    <td style="padding: 12px 14px; color: #34d399; font-weight: 700; font-size: 1rem; font-family: monospace;">${p.bonus}</td>
                    <td style="padding: 12px 14px; color: #38bdf8; font-family: monospace; font-weight: 600;">${p.cost_stones}x Pedras</td>
                    <td style="padding: 12px 14px; color: #fbbf24; font-family: monospace;">${p.cost_gold}</td>
                    <td style="padding: 12px 14px; color: #cbd5e1; font-size: 0.8rem; font-family: monospace;">${p.rates}</td>
                    <td style="padding: 12px 14px; color: #34d399; font-size: 0.8rem; font-weight: 600;">${p.fail}</td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      `;
    }
  }

  // Render Shops and Mercantile Catalog
  function renderShops() {
    const container = document.getElementById('shopsContainer');
    const pagination = document.getElementById('shopsPagination');
    if (!container || !state.data.shops) return;

    let offers = state.data.shops.offers || [];

    // Filter by Category
    if (state.shopsFilter !== 'all') {
      offers = offers.filter(o => o.cid === state.shopsFilter);
    }

    // Filter by Search Term
    if (state.shopsSearchTerm) {
      const q = state.shopsSearchTerm.toLowerCase();
      offers = offers.filter(o =>
        (o.name && o.name.toLowerCase().includes(q)) ||
        (o.tab && o.tab.toLowerCase().includes(q)) ||
        (o.cat && o.cat.toLowerCase().includes(q)) ||
        (o.iap && o.iap.toLowerCase().includes(q)) ||
        (o.cost_param && o.cost_param.toLowerCase().includes(q))
      );
    }

    const total = offers.length;
    const pages = Math.ceil(total / state.shopsPerPage) || 1;
    if (state.shopsPage > pages) state.shopsPage = 1;

    const start = (state.shopsPage - 1) * state.shopsPerPage;
    const currentList = offers.slice(start, start + state.shopsPerPage);

    if (currentList.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px; color: #94a3b8;">
          <div style="font-size: 2.2rem; margin-bottom: 8px;">🔍</div>
          <div style="font-size: 1.1rem; color: #fff; margin-bottom: 4px;">Nenhuma oferta encontrada</div>
          <p style="font-size: 0.85rem;">Tente ajustar os filtros de categoria ou termo de busca.</p>
        </div>
      `;
      if (pagination) pagination.innerHTML = '';
      return;
    }

    container.innerHTML = currentList.map(o => {
      let costHtml = '';
      if (o.cost_type === 'InAppPurchase') {
        costHtml = `<span class="entity-badge badge-crimson" style="font-size: 0.72rem;">💳 Compra no App</span>`;
      } else if (o.cost_type === 'Asset') {
        const paramLabel = o.cost_param === 'Diamond' ? '💎 Diamantes' : (o.cost_param === 'Gold' ? '🪙 Ouro' : o.cost_param);
        costHtml = `<span class="entity-badge badge-gold" style="font-size: 0.72rem;">${formatBigNumber(o.cost_val)} ${paramLabel}</span>`;
      } else {
        costHtml = `<span class="entity-badge badge-blue" style="font-size: 0.72rem;">📦 Troca (${o.cost_val}x)</span>`;
      }

      let rewPreview = '';
      if (o.rewards && o.rewards.length > 0) {
        rewPreview = `
          <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.76rem; color: #cbd5e1;">
            <div style="font-size: 0.68rem; text-transform: uppercase; color: #94a3b8; margin-bottom: 4px;">Contém:</div>
            ${o.rewards.map(r => `<div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">• ${r[1]}x ${r[0]}</div>`).join('')}
          </div>
        `;
      }

      return `
        <div class="entity-card" onclick="window.inspectShopOffer('${o.id}')" style="cursor: pointer; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div class="entity-header">
              <div class="item-slot-frame" style="width: 48px; height: 48px;">
                <img src="${o.icon}" alt="${o.name}" class="item-slot-img" onerror="this.src='assets/items/flat_shop.png'">
              </div>
              <div style="flex: 1; margin-left: 12px; min-width: 0;">
                <div class="entity-title" style="font-size: 0.98rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${o.name}">${o.name}</div>
                <div style="display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap;">
                  <span class="entity-badge badge-gray" style="font-size: 0.68rem;">${o.cat}</span>
                  <span class="entity-badge badge-blue" style="font-size: 0.68rem;">${o.tab}</span>
                </div>
              </div>
            </div>

            ${o.desc ? `<p class="entity-desc" style="font-size: 0.8rem; margin-top: 8px; max-height: 40px; overflow: hidden;">${o.desc}</p>` : ''}
          </div>

          <div>
            ${rewPreview}
            <div class="entity-meta-row" style="margin-top: 10px;">
              ${costHtml}
              <span style="font-size: 0.72rem; color: #94a3b8;">${o.limit || (o.iap ? 'ID: ' + o.iap : 'ID #' + o.id)}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    renderPagination(pagination, state.shopsPage, pages, 'window.changeShopsPage');
  }

  window.changeShopsPage = function(page) {
    state.shopsPage = page;
    renderShops();
    document.getElementById('shops').scrollIntoView({ behavior: 'smooth' });
  };

  // Inspect Shop Offer Modal
  window.inspectShopOffer = function(id) {
    if (!state.data.shops) return;
    const o = state.data.shops.offers.find(x => x.id === id);
    if (!o) return;

    modalTitle.textContent = o.name;
    modalSubtitle.textContent = `Oferta ID #${o.id} • ${o.cat} > ${o.tab}`;

    let costDetails = '';
    if (o.cost_type === 'InAppPurchase') {
      costDetails = `
        <div style="background: rgba(220, 38, 38, 0.1); border: 1px solid rgba(220, 38, 38, 0.3); border-radius: 6px; padding: 12px; margin-bottom: 16px;">
          <div style="font-size: 0.72rem; color: var(--crimson-light); text-transform: uppercase; font-weight: 700;">Tipo de Cobrança</div>
          <div style="font-size: 1.1rem; color: #fff; font-weight: 600; margin-top: 2px;">💳 Compra no Aplicativo (IAP)</div>
          <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px; font-family: monospace;">Identificador Netmarble: ${o.iap || 'Não especificado'}</div>
          <div style="font-size: 0.74rem; color: #94a3b8; margin-top: 4px;">O valor em moeda local (BRL/USD) é negociado pela loja oficial (Google Play / App Store).</div>
        </div>
      `;
    } else {
      costDetails = `
        <div style="background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 6px; padding: 12px; margin-bottom: 16px;">
          <div style="font-size: 0.72rem; color: var(--gold-primary); text-transform: uppercase; font-weight: 700;">Custo do Produto</div>
          <div style="font-size: 1.25rem; color: #fbbf24; font-weight: 700; margin-top: 2px; font-family: monospace;">${formatBigNumber(o.cost_val)} ${o.cost_param}</div>
          <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px;">Tipo de Transação: ${o.cost_type}</div>
        </div>
      `;
    }

    let rewardsHtml = '';
    if (o.rewards && o.rewards.length > 0) {
      rewardsHtml = `
        <h5 style="color: #fff; font-size: 0.95rem; margin-bottom: 8px;">🎁 Conteúdo do Pacote / Recompensas Base:</h5>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px;">
          ${o.rewards.map(r => `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #fff; font-size: 0.88rem;">${r[0]}</span>
              <strong style="color: #38bdf8; font-family: monospace;">x${r[1]}</strong>
            </div>
          `).join('')}
        </div>
      `;
    }

    modalBody.innerHTML = `
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 18px;">
        <div class="item-slot-frame" style="width: 64px; height: 64px;">
          <img src="${o.icon}" alt="${o.name}" class="item-slot-img" onerror="this.src='assets/items/flat_shop.png'">
        </div>
        <div>
          <h4 style="font-size: 1.15rem; color: #fff; margin-bottom: 4px;">${o.name}</h4>
          <div style="display: flex; gap: 8px;">
            <span class="entity-badge badge-gold">${o.cat}</span>
            <span class="entity-badge badge-blue">${o.tab}</span>
            ${o.limit ? `<span class="entity-badge badge-crimson">${o.limit}</span>` : ''}
          </div>
        </div>
      </div>

      ${o.desc ? `<p style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.5; margin-bottom: 16px;">${o.desc}</p>` : ''}

      ${costDetails}
      ${rewardsHtml}

      <div style="font-size: 0.74rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 12px;">
        Registro extraído do pacote local de assets (Shop.csv • Netmarble Corporation).
      </div>
    `;

    detailModal.classList.add('open');
  };

  // ==========================================
  // CODEX & ANCESTRAL COLLECTIONS
  // ==========================================
  function renderCodex() {
    if (!state.data.codex) return;

    // Toggle subview visibility
    const views = {
      collections: document.getElementById('codexCollectionsView'),
      entries: document.getElementById('codexEntriesView'),
      character: document.getElementById('codexCharacterView'),
      tomb: document.getElementById('codexTombView')
    };

    Object.keys(views).forEach(tabKey => {
      if (views[tabKey]) {
        views[tabKey].style.display = (state.codexTab === tabKey) ? 'block' : 'none';
      }
    });

    if (state.codexTab === 'collections') {
      renderCodexCollections();
    } else if (state.codexTab === 'entries') {
      renderCodexEntries();
    } else if (state.codexTab === 'character') {
      renderCodexCharacter();
    } else if (state.codexTab === 'tomb') {
      renderCodexTomb();
    }
  }

  function renderCodexCollections() {
    const container = document.getElementById('codexCollectionsContainer');
    const pagination = document.getElementById('codexCollectionsPagination');
    if (!container || !state.data.codex || !state.data.codex.collections) return;

    let list = state.data.codex.collections;

    // Filter by Tab (Category)
    if (state.codexFilter !== 'all') {
      list = list.filter(c => c.tab === Number(state.codexFilter));
    }

    // Filter by Rarity
    if (state.codexRarity !== 'all') {
      list = list.filter(c => c.rarity === Number(state.codexRarity));
    }

    // Search query
    if (state.codexSearchTerm.trim()) {
      const q = state.codexSearchTerm.toLowerCase();
      list = list.filter(c =>
        c.name.toLowerCase().includes(q) ||
        c.id.includes(q) ||
        (c.reqs && c.reqs.some(req => req.name.toLowerCase().includes(q) || req.id.includes(q))) ||
        (c.effects && c.effects.some(eff => eff.name.toLowerCase().includes(q) || eff.raw_type.toLowerCase().includes(q)))
      );
    }

    const total = list.length;
    const pages = Math.ceil(total / state.codexPerPage) || 1;
    if (state.codexPage > pages) state.codexPage = 1;

    const start = (state.codexPage - 1) * state.codexPerPage;
    const currentList = list.slice(start, start + state.codexPerPage);

    container.innerHTML = currentList.map(c => {
      const rarityBadgeColor = c.rarity === 5 ? 'badge-crimson' : (c.rarity === 4 ? 'badge-gold' : (c.rarity === 3 ? 'badge-blue' : 'badge-gray'));

      return `
        <div class="entity-card" style="display: flex; flex-direction: column; justify-content: space-between; border-left: 3px solid var(--border-gold);">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 8px;">
              <div>
                <div class="entity-title" style="font-size: 1.0rem; color: #fff; margin-bottom: 2px;">${c.name}</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">
                  <span class="entity-badge badge-blue" style="font-size: 0.65rem;">${c.tab_name}</span>
                  <span class="entity-badge ${rarityBadgeColor}" style="font-size: 0.65rem; margin-left: 4px;">${c.rarity_name}</span>
                  <span style="margin-left: 6px;">ID #${c.id}</span>
                </div>
              </div>
            </div>

            <!-- Required Items Frame -->
            <div style="background: rgba(0,0,0,0.35); border-radius: 6px; padding: 10px; margin: 10px 0; border: 1px solid rgba(255,255,255,0.06);">
              <div style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">
                Requisitos (${c.reqs.length} itens):
              </div>
              <div style="display: flex; flex-direction: column; gap: 6px;">
                ${c.reqs.map(q => `
                  <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 0.78rem;">
                    <div style="display: flex; align-items: center; gap: 6px; min-width: 0;">
                      <img src="${q.icon}" style="width: 24px; height: 24px; border-radius: 4px; object-fit: contain; background: rgba(0,0,0,0.5); padding: 1px;" onerror="this.src='assets/logo.png'">
                      <span style="color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer;" onclick="window.inspectItem('${q.id}')" title="Clique para ver o item">${q.name}</span>
                    </div>
                    <div style="display: flex; gap: 4px; align-items: center; flex-shrink: 0;">
                      ${q.ench > 0 ? `<span class="entity-badge badge-gold" style="font-size: 0.68rem; padding: 1px 5px;">+${q.ench}</span>` : `<span class="entity-badge badge-gray" style="font-size: 0.65rem; padding: 1px 4px;">+0</span>`}
                      <span style="color: #94a3b8; font-size: 0.72rem;">x${q.qty}</span>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>

          <!-- Applied Effects Frame -->
          <div>
            <div style="background: rgba(234, 179, 8, 0.08); border: 1px solid rgba(234, 179, 8, 0.2); border-radius: 6px; padding: 8px 10px;">
              <div style="font-size: 0.72rem; font-weight: 700; color: var(--gold-primary); margin-bottom: 4px;">
                ✨ Bônus Permanente de Atributos:
              </div>
              <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                ${c.effects.map(eff => `
                  <span class="entity-badge badge-gold" style="font-size: 0.72rem; padding: 2px 6px;">
                    ${eff.name}: <strong>${eff.val}</strong>
                  </span>
                `).join('')}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');

    renderPagination(pagination, state.codexPage, pages, 'window.changeCodexPage');
  }

  window.changeCodexPage = function(page) {
    state.codexPage = page;
    renderCodexCollections();
    document.getElementById('codex').scrollIntoView({ behavior: 'smooth' });
  };

  function renderCodexEntries() {
    const container = document.getElementById('codexEntriesContainer');
    const pagination = document.getElementById('codexEntriesPagination');
    if (!container || !state.data.codex || !state.data.codex.entries) return;

    let list = state.data.codex.entries;

    // Filter by Entry Type
    if (state.codexEntriesFilter === 'unmatched') {
      list = list.filter(e => !e.matched);
    } else if (state.codexEntriesFilter !== 'all') {
      list = list.filter(e => e.type === state.codexEntriesFilter);
    }

    // Search
    if (state.codexEntriesSearchTerm.trim()) {
      const q = state.codexEntriesSearchTerm.toLowerCase();
      list = list.filter(e =>
        e.name.toLowerCase().includes(q) ||
        (e.param && e.param.toLowerCase().includes(q)) ||
        (e.group_id && e.group_id.toLowerCase().includes(q)) ||
        e.table.toLowerCase().includes(q)
      );
    }

    const total = list.length;
    const pages = Math.ceil(total / state.codexEntriesPerPage) || 1;
    if (state.codexEntriesPage > pages) state.codexEntriesPage = 1;

    const start = (state.codexEntriesPage - 1) * state.codexEntriesPerPage;
    const currentList = list.slice(start, start + state.codexEntriesPerPage);

    container.innerHTML = currentList.map(e => {
      const statusBadge = e.matched ?
        '<span class="entity-badge badge-blue" style="font-size: 0.68rem;">✅ Identificado</span>' :
        '<span class="entity-badge badge-crimson" style="font-size: 0.68rem;">⏳ ID Preservado</span>';

      return `
        <div class="entity-card" style="border-left: 3px solid ${e.matched ? 'var(--blue-primary)' : 'var(--crimson-primary)'};">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
            <div>
              <div class="entity-title" style="font-size: 0.95rem; color: #fff;">${e.name}</div>
              <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 4px;">
                <span class="entity-badge badge-gray" style="font-size: 0.65rem;">${e.type_name}</span>
                <span style="margin-left: 6px;">Posição Tile: <strong>#${e.tile_num}</strong></span>
              </div>
            </div>
            ${statusBadge}
          </div>

          <div style="background: rgba(0,0,0,0.35); border-radius: 6px; padding: 8px 10px; margin-top: 10px; font-size: 0.75rem; color: #cbd5e1; font-family: monospace; line-height: 1.5;">
            <div>Tabela Alvo: <strong>${e.table}</strong></div>
            <div>Grupo de Códex: <strong>${e.group_id || '—'}</strong></div>
            <div>Parâmetro / ID do Item: <strong>${e.param || 'Não especificado (Reservado)'}</strong></div>
          </div>
        </div>
      `;
    }).join('');

    renderPagination(pagination, state.codexEntriesPage, pages, 'window.changeCodexEntriesPage');
  }

  window.changeCodexEntriesPage = function(page) {
    state.codexEntriesPage = page;
    renderCodexEntries();
    document.getElementById('codex').scrollIntoView({ behavior: 'smooth' });
  };

  function renderCodexCharacter() {
    const container = document.getElementById('codexCharacterContainer');
    if (!container || !state.data.codex || !state.data.codex.character) return;

    const chars = state.data.codex.character;

    container.innerHTML = `
      <div style="grid-column: 1 / -1; margin-bottom: 10px;">
        <div class="panel-box" style="border-left: 3px solid var(--gold-primary);">
          <div class="panel-title">📜 Mecânica do Códex de Personagem (Tutorial #41101)</div>
          <p style="font-size: 0.86rem; color: #cbd5e1; line-height: 1.6; margin-top: 4px;">
            As abas de território do Códex de Personagem são ativadas ao concluir a primeira missão principal da região correspondente.
            As informações de personagens e seus relacionamentos são desvendadas ao completar missões secundárias locais, acumulando Pontos de Episódio que desbloqueiam até 5 etapas sucessivas de recompensas permanentes.
          </p>
        </div>
      </div>
      ${chars.map(c => `
        <div class="entity-card" style="border-left: 3px solid var(--gold-primary);">
          <div class="entity-title" style="font-size: 1.15rem; color: var(--gold-primary);">
            🏰 Território: ${c.name}
          </div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 12px;">
            Desbloqueio de Território: <strong>Missão Principal #${c.quest_id}</strong>
          </p>

          <div style="background: rgba(0,0,0,0.35); border-radius: 6px; padding: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;">
              Etapas de Pontos de Episódio & Recompensas:
            </div>
            <div style="display: flex; flex-direction: column; gap: 6px;">
              ${c.points.map((pt, idx) => `
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
                  <span style="color: #cbd5e1;">Etapa ${idx + 1} (${pt} Pontos Necessários)</span>
                  <span class="entity-badge badge-gold" style="font-size: 0.7rem;">Recompensa #${c.rewards[idx]}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `).join('')}
    `;
  }

  function renderCodexTomb() {
    const container = document.getElementById('codexTombContainer');
    if (!container || !state.data.codex || !state.data.codex.tomb_cards) return;

    const groups = state.data.codex.tomb_cards;

    container.innerHTML = `
      <div style="grid-column: 1 / -1; margin-bottom: 10px;">
        <div class="panel-box" style="border-left: 3px solid #38bdf8;">
          <div class="panel-title">⚰️ Coleção de Cartas da Tumba & Árvore da Linhagem (Bloodline)</div>
          <p style="font-size: 0.86rem; color: #cbd5e1; line-height: 1.6; margin-top: 4px;">
            A Coleção Fúnebre organiza 96 cartas de tumba ancestrais divididas em <strong>29 grupos temáticos</strong>, com 290 etapas de coleção acumulativas e 960 regras de evolução de nível.
            Ao registrar cartas fúnebres na tumba, seus atributos são aplicados permanentemente a todos os personagens da conta.
          </p>
        </div>
      </div>
      ${groups.map(g => `
        <div class="entity-card" style="border-left: 3px solid #38bdf8;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="entity-title" style="font-size: 0.98rem; color: #fff;">${g.name}</div>
            <span class="entity-badge badge-blue" style="font-size: 0.68rem;">Ordem: ${g.order}</span>
          </div>
          <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 6px;">
            ID do Grupo Fúnebre: <strong>#${g.id}</strong>
          </div>
        </div>
      `).join('')}
    `;
  }

  window.openCodexFromItem = function(collectionId) {
    detailModal.classList.remove('open');
    switchTab('codex');
    state.codexTab = 'collections';
    document.querySelectorAll('#codexSubNav .pvp-subnav-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.codextab === 'collections');
    });
    document.querySelectorAll('.codex-subview').forEach(v => v.style.display = 'none');
    const view = document.getElementById('codexCollectionsView');
    if (view) view.style.display = 'block';
    state.codexSearchTerm = collectionId;
    state.codexPage = 1;
    renderCodex();
  };

  // ==========================================
  // MAGIC RESEARCH (EXTRACT SYSTEM)
  // ==========================================
  function renderResearch() {
    const container = document.getElementById('researchContainer');
    const pagination = document.getElementById('researchPagination');
    if (!container || !state.data.research || !state.data.research.flasks) return;

    let flasks = state.data.research.flasks;

    // Filter by Magic Line
    if (state.researchFilter !== 'all') {
      flasks = flasks.filter(f => f.line_id === state.researchFilter);
    }

    // Search query
    if (state.researchSearchTerm.trim()) {
      const q = state.researchSearchTerm.toLowerCase();
      flasks = flasks.filter(f =>
        f.name.toLowerCase().includes(q) ||
        f.line_name.toLowerCase().includes(q) ||
        f.id.includes(q) ||
        (f.effects && f.effects.some(e => e.name.toLowerCase().includes(q))) ||
        (f.steps && f.steps.some(s => s.cost_name.toLowerCase().includes(q) || s.effects.some(se => se.name.toLowerCase().includes(q))))
      );
    }

    const total = flasks.length;
    const pages = Math.ceil(total / state.researchPerPage) || 1;
    if (state.researchPage > pages) state.researchPage = 1;

    const start = (state.researchPage - 1) * state.researchPerPage;
    const currentList = flasks.slice(start, start + state.researchPerPage);

    const LINE_COLORS = {
      '100': 'badge-blue',
      '200': 'badge-gray',
      '300': 'badge-gold',
      '400': 'badge-crimson',
      '500': 'badge-gold',
      '600': 'badge-blue'
    };

    container.innerHTML = currentList.map(f => {
      const badgeColor = LINE_COLORS[f.line_id] || 'badge-blue';

      return `
        <div class="entity-card" style="display: flex; flex-direction: column; justify-content: space-between; border-left: 3px solid var(--border-gold); cursor: pointer;" onclick="window.inspectFlask('${f.id}')">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
              <div style="min-width: 0;">
                <div class="entity-title" style="font-size: 1.02rem; color: #fff; margin-bottom: 2px;">${f.name}</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">
                  <span class="entity-badge ${badgeColor}" style="font-size: 0.65rem;">${f.line_name}</span>
                  <span class="entity-badge badge-gray" style="font-size: 0.65rem; margin-left: 4px;">Nv. ${f.level}</span>
                  <span style="margin-left: 6px;">ID #${f.id}</span>
                </div>
              </div>
              <span class="entity-badge badge-gold" style="font-size: 0.72rem; flex-shrink: 0;" title="Taxa base de sucesso na Pesquisa">
                🎯 ${f.rate_display}
              </span>
            </div>

            <!-- Infusion Steps Preview -->
            <div style="background: rgba(0,0,0,0.35); border-radius: 6px; padding: 10px; margin: 12px 0 8px; border: 1px solid rgba(255,255,255,0.06);">
              <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #cbd5e1;">
                <span>⚗️ <strong>${f.steps.length} Etapas de Infusão</strong></span>
                <span style="color: #38bdf8;">${f.steps[0]?.cost_name || 'Orbes Mágicas'}</span>
              </div>
            </div>

            <!-- Permanent Bonus Effects -->
            <div style="margin-top: 8px;">
              <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--gold-primary); font-weight: 700; margin-bottom: 6px;">
                ✨ Bônus de Conclusão da Pesquisa:
              </div>
              <div style="display: flex; flex-direction: column; gap: 4px;">
                ${f.effects.map(eff => `
                  <div style="font-size: 0.78rem; color: #cbd5e1; display: flex; justify-content: space-between;">
                    <span>${eff.name}:</span>
                    <strong style="color: var(--gold-light);">${eff.val}</strong>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>

          <!-- Research Costs Footer -->
          <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
            <div style="color: #94a3b8;">
              Custo: <strong style="color: #fbbf24;">${formatBigNumber(f.trinity)}x Trindade</strong> ou <strong style="color: #38bdf8;">${f.catalyst}x Catalisador</strong>
            </div>
            <button class="filter-btn" style="padding: 3px 8px; font-size: 0.7rem;">Inspecionar ⚗️</button>
          </div>
        </div>
      `;
    }).join('');

    renderPagination(pagination, state.researchPage, pages, 'window.changeResearchPage');
  }

  window.changeResearchPage = function(page) {
    state.researchPage = page;
    renderResearch();
    document.getElementById('research').scrollIntoView({ behavior: 'smooth' });
  };

  window.inspectFlask = function(id) {
    if (!state.data.research || !state.data.research.flasks) return;
    const f = state.data.research.flasks.find(x => x.id === id);
    if (!f) return;

    modalTitle.innerText = f.name;
    modalSubtitle.innerText = `${f.line_name} • Nível ${f.level} (Frasco ID #${f.id})`;

    const stepsHtml = f.steps.map(s => `
      <div style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <div style="font-weight: 700; color: #fff; font-size: 0.88rem;">
            Etapa ${s.step} ${s.step === 0 ? '(Início)' : ''}
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <span class="entity-badge badge-gold" style="font-size: 0.7rem;">🎯 Taxa: ${(s.rate/100).toFixed(1)}%</span>
            ${s.cost_val > 0 ? `<span class="entity-badge badge-blue" style="font-size: 0.7rem;">🧪 Custo: ${s.cost_val}x ${s.cost_name}</span>` : ''}
          </div>
        </div>
        ${s.effects && s.effects.length > 0 ? `
          <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px;">
            ${s.effects.map(e => `
              <span class="entity-badge badge-gray" style="font-size: 0.72rem;">
                ${e.name}: <strong style="color: var(--gold-light);">${e.val}</strong>
              </span>
            `).join('')}
          </div>
        ` : '<div style="font-size: 0.75rem; color: #94a3b8;">Etapa preparatória de ativação.</div>'}
      </div>
    `).join('');

    modalBody.innerHTML = `
      <!-- Research & Success Summary -->
      <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid var(--gold-primary);">
        <div class="panel-title" style="display: flex; justify-content: space-between;">
          <span>🔬 Conclusão da Pesquisa do Frasco</span>
          <span style="color: var(--gold-light); font-weight: 700;">Taxa Base: ${f.rate_display}</span>
        </div>
        <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; margin: 6px 0 10px;">
          O sucesso na pesquisa sela permanentemente o frasco e desbloqueia o próximo nível da <strong>${f.line_name}</strong>.
          Em caso de falha, o sistema concede uma chance bônus cumulativa (<code>EXTRACT_BONUS_RATE</code>).
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
          <div style="background: rgba(0,0,0,0.4); border-radius: 6px; padding: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.72rem; color: #fbbf24; font-weight: 700; text-transform: uppercase;">Custo Padrão</div>
            <div style="font-size: 1.05rem; color: #fff; font-weight: 700; margin: 2px 0;">${formatBigNumber(f.trinity)}x Trindade (Trinity)</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Obtido no desmanche de equipamentos Raros ou superiores.</div>
          </div>
          <div style="background: rgba(0,0,0,0.4); border-radius: 6px; padding: 10px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.72rem; color: #38bdf8; font-weight: 700; text-transform: uppercase;">Custo Substituto Alternativo</div>
            <div style="font-size: 1.05rem; color: #fff; font-weight: 700; margin: 2px 0;">${f.catalyst}x Catalisador de Pesquisa</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Item especial consumido no lugar da Trindade.</div>
          </div>
        </div>
      </div>

      <!-- Permanent Research Effects -->
      <div class="panel-box" style="margin-bottom: 20px; border-left: 3px solid #10b981;">
        <div class="panel-title">✨ Bônus Permanentes Adquiridos ao Selar o Frasco</div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
          ${f.effects.map(eff => `
            <span class="entity-badge badge-gold" style="font-size: 0.8rem; padding: 4px 10px;">
              ${eff.name}: <strong style="color: #fff; margin-left: 4px;">${eff.val}</strong>
            </span>
          `).join('')}
        </div>
      </div>

      <!-- Infusion Steps List -->
      <div class="panel-box" style="border-left: 3px solid #38bdf8;">
        <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span>⚗️ Roteiro das ${f.steps.length} Etapas de Infusão Mágica</span>
          <span style="font-size: 0.75rem; color: #94a3b8; font-weight: normal;">Fonte: ExtractStep.csv</span>
        </div>
        <div style="max-height: 340px; overflow-y: auto; padding-right: 4px;">
          ${stepsHtml}
        </div>
      </div>
    `;

    detailModal.classList.add('open');
  };

  // ==========================================
  // PORTRAITS & FRAGMENTS SYSTEM
  // ==========================================
  function renderPortraits() {
    const container = document.getElementById('portraitsContainer');
    const pagination = document.getElementById('portraitsPagination');
    if (!container || !state.data.portraits || !state.data.portraits.portraits) return;

    let portraits = state.data.portraits.portraits;

    // Filter by Rarity
    if (state.portraitsFilter === 'defaults') {
      portraits = portraits.filter(p => p.is_default);
    } else if (state.portraitsFilter !== 'all') {
      portraits = portraits.filter(p => p.rarity === state.portraitsFilter);
    }

    // Filter by Type
    if (state.portraitsType !== 'all') {
      portraits = portraits.filter(p => p.type_code === state.portraitsType);
    }

    // Search query
    if (state.portraitsSearchTerm.trim()) {
      const q = state.portraitsSearchTerm.toLowerCase();
      portraits = portraits.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.id.includes(q) ||
        p.type.toLowerCase().includes(q) ||
        p.rarity.toLowerCase().includes(q) ||
        (p.fragments && p.fragments.some(f => f.mat_name.toLowerCase().includes(q))) ||
        (p.summary_effects && p.summary_effects.some(e => e.name.toLowerCase().includes(q)))
      );
    }

    const total = portraits.length;
    const pages = Math.ceil(total / state.portraitsPerPage) || 1;
    if (state.portraitsPage > pages) state.portraitsPage = 1;

    const start = (state.portraitsPage - 1) * state.portraitsPerPage;
    const currentList = portraits.slice(start, start + state.portraitsPerPage);

    const RARITY_BADGE_MAP = {
      'Comum': 'badge-gray',
      'Incomum': 'badge-blue',
      'Raro': 'badge-blue',
      'Heroico': 'badge-purple',
      'Lendário': 'badge-gold',
      'Mítico': 'badge-crimson'
    };

    container.innerHTML = currentList.map(p => {
      const rarityBadgeColor = RARITY_BADGE_MAP[p.rarity] || 'badge-blue';

      let statsHtml = '';
      if (p.summary_effects && p.summary_effects.length > 0) {
        statsHtml = `
          <div style="margin-top: 10px;">
            <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--gold-primary); font-weight: 700; margin-bottom: 6px;">
              ✨ Atributos Totais de Restauração:
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              ${p.summary_effects.map(eff => `
                <span class="entity-badge badge-gold" style="font-size: 0.72rem; padding: 2px 6px;">
                  ${eff.name}: <strong>${eff.total}</strong>
                </span>
              `).join('')}
            </div>
          </div>
        `;
      } else if (p.is_default) {
        statsHtml = `
          <div style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8; font-style: italic;">
            Retrato padrão inicial concedido automaticamente ao criar o personagem.
          </div>
        `;
      }

      return `
        <div class="entity-card" style="display: flex; flex-direction: column; justify-content: space-between; border-left: 3px solid var(--border-gold); cursor: pointer;" onclick="window.inspectPortrait('${p.id}')">
          <div>
            <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 8px;">
              <div style="width: 52px; height: 52px; border-radius: 8px; overflow: hidden; background: #000; border: 1px solid rgba(255,255,255,0.15); flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                <img src="${p.icon}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/portraits/flat_portrait.png'">
              </div>
              <div style="flex: 1; min-width: 0;">
                <div class="entity-title" style="font-size: 1.05rem; color: #fff; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${p.name}">${p.name}</div>
                <div style="font-size: 0.72rem; color: #94a3b8; display: flex; gap: 4px; align-items: center; flex-wrap: wrap;">
                  <span class="entity-badge ${rarityBadgeColor}" style="font-size: 0.65rem;">${p.rarity}</span>
                  <span class="entity-badge badge-gray" style="font-size: 0.65rem;">${p.type}</span>
                  <span>ID #${p.id}</span>
                </div>
              </div>
              <span class="entity-badge badge-blue" style="font-size: 0.68rem; flex-shrink: 0;">
                🎯 ${p.rate_display}
              </span>
            </div>

            <!-- Restoration Status Preview -->
            <div style="background: rgba(0,0,0,0.35); border-radius: 6px; padding: 10px; margin: 12px 0 8px; border: 1px solid rgba(255,255,255,0.06);">
              <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem;">
                <span style="color: #cbd5e1;">
                  🧩 <strong>${p.frags_count > 0 ? p.frags_count + ' Fragmentos' : 'Retrato Base'}</strong>
                </span>
                <span style="color: #38bdf8; font-size: 0.75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px;">
                  ${p.fragments[0]?.mat_name || 'Desbloqueio Livre'}
                </span>
              </div>
            </div>

            ${statsHtml}
          </div>

          <!-- Card Footer -->
          <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
            <div style="color: #94a3b8;">
              ${p.frags_count > 0 ? `${p.fragments[0]?.qty || '20'}x Kit por etapa` : 'Sem custo de kit'}
            </div>
            <button class="filter-btn" style="padding: 3px 8px; font-size: 0.7rem;">Inspecionar 🧩</button>
          </div>
        </div>
      `;
    }).join('');

    renderPagination(pagination, state.portraitsPage, pages, 'window.changePortraitsPage');
  }

  window.changePortraitsPage = function(page) {
    state.portraitsPage = page;
    renderPortraits();
    document.getElementById('portraits').scrollIntoView({ behavior: 'smooth' });
  };

  window.inspectPortrait = function(id) {
    if (!state.data.portraits || !state.data.portraits.portraits) return;
    const p = state.data.portraits.portraits.find(x => x.id === id);
    if (!p) return;

    modalTitle.innerText = p.name;
    modalSubtitle.innerText = `${p.rarity} • ${p.type} (Retrato ID #${p.id})`;

    let summaryStatsHtml = '';
    if (p.summary_effects && p.summary_effects.length > 0) {
      summaryStatsHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid var(--gold-primary);">
          <div class="panel-title">✨ Atributos Totais Concedidos ao Completar</div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 10px; line-height: 1.4;">
            Soma acumulada de todos os bônus permanentes adquiridos ao restaurar os ${p.frags_count} fragmentos:
          </p>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            ${p.summary_effects.map(eff => `
              <span class="entity-badge badge-gold" style="font-size: 0.82rem; padding: 4px 10px;">
                ${eff.name}: <strong style="color: #fff; margin-left: 4px;">${eff.total}</strong>
              </span>
            `).join('')}
          </div>
        </div>
      `;
    }

    let fragsListHtml = '';
    if (p.fragments && p.fragments.length > 0) {
      fragsListHtml = `
        <div class="panel-box" style="border-left: 3px solid #38bdf8;">
          <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span>🧩 Roteiro de Restauração dos ${p.fragments.length} Fragmentos</span>
            <span style="font-size: 0.75rem; color: #94a3b8; font-weight: normal;">Fonte: PortraitPiece.csv / PortraitRetention.csv</span>
          </div>
          <div style="max-height: 360px; overflow-y: auto; padding-right: 4px;">
            ${p.fragments.map((fr, idx) => {
              const ret = p.retention && p.retention[idx];
              let retEffectHtml = '';
              if (ret) {
                if (ret.effects && ret.effects.length > 0) {
                  retEffectHtml = ret.effects.map(e => `
                    <span class="entity-badge badge-gold" style="font-size: 0.72rem;">
                      ${e.name}: <strong>${e.val}</strong>
                    </span>
                  `).join(' ');
                } else if (ret.rewards && ret.rewards.length > 0) {
                  retEffectHtml = ret.rewards.map(rw => `
                    <span class="entity-badge badge-blue" style="font-size: 0.72rem;">
                      🎁 ${rw.count}x ${rw.name}
                    </span>
                  `).join(' ');
                }
              }

              return `
                <div style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="font-weight: 700; color: #fff; font-size: 0.88rem;">
                      Fragmento ${fr.num} de ${p.fragments.length}
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <img src="${fr.icon}" style="width: 22px; height: 22px; border-radius: 4px; object-fit: contain;" onerror="this.src='assets/items/flat_relic.png'">
                      <span style="color: #38bdf8; font-size: 0.8rem; font-weight: 600;">
                        ${fr.qty}x ${fr.mat_name}
                      </span>
                    </div>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Marco ${fr.num}:</span>
                    <div>${retEffectHtml || '<span style="font-size: 0.75rem; color: #64748b;">Nenhum efeito registrado</span>'}</div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    } else {
      fragsListHtml = `
        <div class="panel-box" style="border-left: 3px solid #64748b;">
          <div class="panel-title">👤 Retrato Inicial Padrão</div>
          <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; margin-top: 4px;">
            Este retrato é concedido por padrão no início do jogo para sua classe correspondente, sem necessidade de restauração de fragmentos.
          </p>
        </div>
      `;
    }

    modalBody.innerHTML = `
      <div style="display: flex; gap: 16px; align-items: center; background: rgba(0,0,0,0.4); border-radius: 12px; padding: 14px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.08);">
        <div style="width: 88px; height: 88px; border-radius: 10px; overflow: hidden; border: 2px solid var(--border-gold); flex-shrink: 0; background: #000; box-shadow: 0 4px 12px rgba(0,0,0,0.6);">
          <img src="${p.art || p.icon}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/portraits/flat_portrait.png'">
        </div>
        <div>
          <div style="font-size: 1.15rem; font-weight: 700; color: #fff; margin-bottom: 4px;">${p.name}</div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px;">
            <span class="entity-badge ${RARITY_BADGE_MAP[p.rarity] || 'badge-blue'}">${p.rarity}</span>
            <span class="entity-badge badge-gray">${p.type}</span>
            <span class="entity-badge badge-gold">Taxa: ${p.rate_display}</span>
          </div>
          <div style="font-size: 0.78rem; color: #94a3b8;">ID Oficial #${p.id} • ${p.frags_count > 0 ? p.frags_count + ' Fragmentos de Restauração' : 'Retrato Inicial Padrão'}</div>
        </div>
      </div>

      <!-- Portrait Overview & Equipment Rules -->
      <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid #10b981;">
        <div class="panel-title" style="display: flex; justify-content: space-between;">
          <span>👑 Obtenção & Equipamento de Perfil</span>
          <span style="color: #10b981; font-weight: 700;">Taxa de Obtenção: ${p.rate_display}</span>
        </div>
        <p style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; margin: 6px 0 0;">
          Após restaurar todos os fragmentos, o retrato pode ser obtido e equipado no menu de personagem. Ele substitui seu ícone exibido na barra de status superior, no chat público de clã/mundo e nas telas de classificação de temporada.
        </p>
      </div>

      ${summaryStatsHtml}
      ${fragsListHtml}
    `;

    detailModal.classList.add('open');
  };

  // ==========================================
  // ARTIFACTS SYSTEM (5 ORIGINAIS + TRANSFORMAÇÃO I)
  // ==========================================
  function renderArtifacts() {
    const container = document.getElementById('artifactsContainer');
    if (!container || !state.data.artifacts || !state.data.artifacts.artifacts) return;

    let artifacts = state.data.artifacts.artifacts;

    // Filter by type (0 = Original, 1 = Transformação)
    if (state.artifactsFilter !== 'all') {
      const typeNum = Number(state.artifactsFilter);
      artifacts = artifacts.filter(a => a.type === typeNum);
    }

    // Search filter
    if (state.artifactsSearchTerm) {
      const q = state.artifactsSearchTerm.toLowerCase();
      artifacts = artifacts.filter(a => 
        a.name.toLowerCase().includes(q) ||
        a.category_name.toLowerCase().includes(q) ||
        (a.unlock_text && a.unlock_text.toLowerCase().includes(q)) ||
        (a.divergence && a.divergence.toLowerCase().includes(q)) ||
        a.summary_effects.some(e => e.name.toLowerCase().includes(q) || e.total.toLowerCase().includes(q))
      );
    }

    if (artifacts.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #94a3b8;">
          <p style="font-size: 1.1rem; margin-bottom: 8px;">Nenhum artefato encontrado para o filtro selecionado.</p>
          <p style="font-size: 0.85rem; color: #64748b;">Tente ajustar o termo de busca ou alternar para "Todos os Artefatos".</p>
        </div>`;
      return;
    }

    container.innerHTML = artifacts.map(art => {
      const isTransform = art.type === 1;
      const typeBadge = isTransform
        ? `<span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4);">⚡ Transformação I</span>`
        : `<span class="badge" style="background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4);">💎 Original</span>`;

      const levelBadge = `<span class="badge" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4);">Nv. Máx ${art.max_level}</span>`;
      
      const attemptsBadge = art.enchant_limit
        ? `<span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4);">🎯 ${art.enchant_limit} Tentativas</span>`
        : '';

      const divergenceBadge = art.divergence
        ? `<div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 6px 10px; font-size: 0.78rem; color: #fca5a5; margin-top: 10px; display: flex; align-items: center; gap: 6px;">
             <span>⚠️</span>
             <span><strong>Divergência:</strong> Texto diz Nv. 90 / Condição exige Nv. 100</span>
           </div>`
        : '';

      const topStats = art.summary_effects.slice(0, 4).map(e => `
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 3px 0; border-bottom: 1px dashed rgba(255,255,255,0.08);">
          <span style="color: #94a3b8;">${e.name}</span>
          <strong style="color: ${e.is_pct ? '#fbbf24' : '#34d399'}; font-family: monospace;">${e.total}</strong>
        </div>
      `).join('');

      const matsHtml = art.materials.map(m => `
        <div style="display: inline-flex; align-items: center; gap: 5px; background: rgba(0,0,0,0.3); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; color: #cbd5e1; border: 1px solid rgba(255,255,255,0.06);">
          <img src="${m.icon}" style="width: 14px; height: 14px; object-fit: contain;" onerror="this.outerHTML='🔹'">
          <span>${m.name}</span>
        </div>
      `).join('');

      return `
        <div class="entity-card" style="background: rgba(15, 20, 30, 0.75); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.25s ease;" onmouseover="this.style.borderColor='rgba(168,85,247,0.5)'; this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.transform='none'">
          <div>
            <div style="display: flex; gap: 14px; align-items: center; margin-bottom: 14px;">
              <div style="width: 58px; height: 58px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; flex-shrink: 0;">
                <img src="${art.art}" style="width: 46px; height: 46px; object-fit: contain;" onerror="this.outerHTML='🏺'">
                <img src="${art.icon}" style="position: absolute; bottom: 2px; right: 2px; width: 20px; height: 20px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8));" title="Material de Aprimoramento">
              </div>
              <div style="flex: 1; min-width: 0;">
                <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 4px;">
                  ${typeBadge}
                  ${levelBadge}
                  ${attemptsBadge}
                </div>
                <h3 style="margin: 0; font-size: 1.05rem; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${art.name}">${art.name}</h3>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">ID: #${art.id} • Servidor: ${art.server_group}</div>
              </div>
            </div>

            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; font-size: 0.8rem; margin-bottom: 12px; color: #cbd5e1;">
              <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 2px;">🔓 Desbloqueio</div>
              <div style="line-height: 1.3;">${art.unlock_text || 'Disponível no jogo'}</div>
            </div>

            ${divergenceBadge}

            <div style="margin-top: 12px; margin-bottom: 14px;">
              <div style="color: #a855f7; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; display: flex; justify-content: space-between;">
                <span>Atributos Acumulados (Nv. Máx)</span>
                <span style="color: #64748b;">${art.summary_effects.length} status</span>
              </div>
              <div style="background: rgba(0,0,0,0.25); border-radius: 6px; padding: 8px 10px;">
                ${topStats}
              </div>
            </div>

            <div style="margin-bottom: 16px;">
              <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">Insumos Requeridos</div>
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                ${matsHtml}
              </div>
            </div>
          </div>

          <button class="btn btn-primary" onclick="window.inspectArtifact('${art.id}')" style="width: 100%; justify-content: center; font-size: 0.85rem; padding: 8px 12px; margin-top: 10px; background: linear-gradient(135deg, #7c3aed, #4f46e5); border: none; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer;">
            🔍 Inspecionar Níveis & Progressão (${art.levels_count} estágios)
          </button>
        </div>
      `;
    }).join('');
  }

  window.inspectArtifact = function(id) {
    if (!state.data.artifacts || !state.data.artifacts.artifacts) return;
    const art = state.data.artifacts.artifacts.find(x => x.id === id);
    if (!art) return;

    modalTitle.innerText = art.name;
    modalSubtitle.innerText = `${art.type_label} • Nv. Máx ${art.max_level} • ID #${art.id}`;

    let divergenceHtml = '';
    if (art.divergence) {
      divergenceHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.08);">
          <div class="panel-title" style="color: #f87171;">⚠️ Divergência Técnica Documentada</div>
          <p style="font-size: 0.85rem; color: #fca5a5; margin: 4px 0 0; line-height: 1.4;">
            ${art.divergence}
          </p>
        </div>
      `;
    }

    let transformHtml = '';
    if (art.transform_info) {
      const tf = art.transform_info;
      transformHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid #f59e0b; background: rgba(245, 158, 11, 0.08);">
          <div class="panel-title" style="color: #fbbf24; display: flex; justify-content: space-between; align-items: center;">
            <span>⚡ Mecânica Especial de Transformação I (20 Tentativas)</span>
            <span style="font-size: 0.8rem; font-weight: normal; color: #fcd34d;">0% Taxa de Falha</span>
          </div>
          <p style="font-size: 0.84rem; color: #cbd5e1; margin: 6px 0 10px; line-height: 1.4;">
            Diferente dos artefatos convencionais, a Transformação I possui um ciclo de <strong>20 tentativas fixas</strong> sem risco de falha (55% de chance de +1, 24% de +2 e 21% de +3). Ao término das tentativas, você pode preservar ou reiniciar:
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 10px;">
            <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.2);">
              <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">💾 Salvar Progresso</div>
              <div style="font-size: 0.95rem; font-weight: 700; color: #fbbf24;">${tf.save_cost}</div>
              <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 2px;">Substitui o nível salvo pelo atual se for superior.</div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.2);">
              <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">📂 Carregar Progresso</div>
              <div style="font-size: 0.95rem; font-weight: 700; color: #fbbf24;">${tf.load_cost}</div>
              <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 2px;">Restaura o melhor nível salvo (mantém 0 tentativas).</div>
            </div>
            <div style="background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.2);">
              <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">🔄 Redefinir Ciclo</div>
              <div style="font-size: 0.95rem; font-weight: 700; color: #fbbf24;">${tf.reset_cost}</div>
              <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 2px;">Restaura 20 tentativas para buscar novos saltos de +2/+3.</div>
            </div>
          </div>
        </div>
      `;
    }

    let generalMechanicsHtml = '';
    if (art.type === 0) {
      generalMechanicsHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid #10b981; background: rgba(16, 185, 129, 0.06);">
          <div class="panel-title" style="color: #34d399; display: flex; justify-content: space-between;">
            <span>🛡️ Regras de Aprimoramento & Retenção de Nível</span>
            <span style="font-size: 0.8rem; color: #6ee7b7; font-weight: normal;">Fonte: TutorialGuide (40501)</span>
          </div>
          <p style="font-size: 0.84rem; color: #cbd5e1; margin: 6px 0 0; line-height: 1.4;">
            Cada tentativa consome <strong>Pedras de Aprimoramento</strong> e <strong>Ouro</strong>. Sucessos avançam aleatoriamente <strong>+1, +2 ou +3 estágios</strong>. Em caso de falha, <strong>o nível atual de aprimoramento é estritamente mantido</strong> (sem perda de nível ou risco de destruição).
          </p>
        </div>
      `;
    }

    let summaryStatsHtml = '';
    if (art.summary_effects && art.summary_effects.length > 0) {
      summaryStatsHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid var(--gold-primary);">
          <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>✨ Atributos Totais Cumulativos no Nível Máximo (${art.max_level})</span>
            <span style="font-size: 0.75rem; color: #94a3b8;">${art.summary_effects.length} status</span>
          </div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 10px; line-height: 1.4;">
            Total somado de todos os efeitos permanentes desbloqueados ao completar o artefato:
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 8px;">
            ${art.summary_effects.map(eff => `
              <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.78rem; color: #cbd5e1;">${eff.name}</span>
                <strong style="font-size: 0.85rem; color: ${eff.is_pct ? '#fbbf24' : '#34d399'}; font-family: monospace;">${eff.total}</strong>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    let milestonesHtml = '';
    if (art.milestones && art.milestones.length > 0) {
      milestonesHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid #a855f7;">
          <div class="panel-title">🏆 Marcos de Progressão & Recompensas Especiais</div>
          <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px;">
            ${art.milestones.map(m => `
              <div style="background: rgba(168,85,247,0.15); border: 1px solid rgba(168,85,247,0.3); border-radius: 6px; padding: 6px 12px; font-size: 0.82rem; display: flex; align-items: center; gap: 6px;">
                <span style="font-weight: 700; color: #c084fc;">Nv. ${m.level}</span>
                <span style="color: #94a3b8;">•</span>
                <span style="color: #e2e8f0;">${m.is_final ? '🎉 Conclusão Final do Artefato' : (m.rewards.map(r => r.name).join(', ') || 'Marco de Aprimoramento')}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    modalBody.innerHTML = `
      <div style="display: flex; gap: 18px; align-items: center; background: linear-gradient(135deg, rgba(30,20,40,0.8), rgba(15,20,30,0.9)); border-radius: 12px; padding: 16px; margin-bottom: 16px; border: 1px solid rgba(168,85,247,0.3);">
        <div style="width: 96px; height: 96px; border-radius: 12px; overflow: hidden; border: 2px solid var(--border-gold); flex-shrink: 0; background: #000; box-shadow: 0 4px 16px rgba(0,0,0,0.8); position: relative;">
          <img src="${art.art}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/artifacts/flat_artifact.png'">
          <img src="${art.icon}" style="position: absolute; bottom: 4px; right: 4px; width: 28px; height: 28px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.9));" title="Ícone Oficial">
        </div>
        <div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 4px;">${art.name}</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
            <span class="badge" style="background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4);">${art.type_label}</span>
            <span class="badge" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4);">Nv. Máx ${art.max_level}</span>
            <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);">Servidor: ${art.server_group}</span>
          </div>
          <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.4;">
            🔓 <strong>Desbloqueio:</strong> ${art.unlock_text || 'Disponível no jogo'}
          </div>
        </div>
      </div>

      ${divergenceHtml}
      ${transformHtml}
      ${generalMechanicsHtml}
      ${summaryStatsHtml}
      ${milestonesHtml}

      <div class="panel-box" style="border-left: 3px solid #38bdf8;">
        <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
          <span>📈 Tabela Completa de Níveis & Aprimoramento (${art.levels.length} registros)</span>
          <div style="display: flex; gap: 6px; align-items: center;">
            <span style="font-size: 0.78rem; color: #94a3b8;">Filtrar Faixa:</span>
            <select id="artifactLevelFilterSelect" onchange="window.filterArtifactLevels('${art.id}', this.value)" style="background: rgba(15,20,30,0.9); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 0.78rem; cursor: pointer;">
              <option value="all">Todos os Níveis (0 - ${art.max_level})</option>
              <option value="milestones">Apenas Marcos com Recompensa</option>
              ${art.max_level <= 50 ? `
                <option value="0-25">Níveis 0 a 25</option>
                <option value="26-50">Níveis 26 a 50</option>
              ` : art.max_level <= 100 ? `
                <option value="0-25">Níveis 0 a 25</option>
                <option value="26-50">Níveis 26 a 50</option>
                <option value="51-75">Níveis 51 a 75</option>
                <option value="76-100">Níveis 76 a 100</option>
              ` : `
                <option value="0-50">Níveis 0 a 50</option>
                <option value="51-100">Níveis 51 a 100</option>
                <option value="101-150">Níveis 101 a 150</option>
                <option value="151-200">Níveis 151 a 200</option>
                <option value="201-250">Níveis 201 a 250</option>
                <option value="251-300">Níveis 251 a 300</option>
              `}
            </select>
          </div>
        </div>

        <div id="artifactLevelsContainer" style="max-height: 420px; overflow-y: auto; padding-right: 4px;">
        </div>
      </div>
    `;

    window.filterArtifactLevels(art.id, 'all');
    detailModal.classList.add('open');
  };

  window.filterArtifactLevels = function(id, rangeKey) {
    const container = document.getElementById('artifactLevelsContainer');
    if (!container || !state.data.artifacts || !state.data.artifacts.artifacts) return;
    const art = state.data.artifacts.artifacts.find(x => x.id === id);
    if (!art) return;

    let levels = art.levels;
    if (rangeKey === 'milestones') {
      levels = levels.filter(l => (l.rewards && l.rewards.length > 0) || l.final);
    } else if (rangeKey.includes('-')) {
      const [minStr, maxStr] = rangeKey.split('-');
      const min = Number(minStr);
      const max = Number(maxStr);
      levels = levels.filter(l => l.level >= min && l.level <= max);
    }

    if (levels.length === 0) {
      container.innerHTML = `<div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 0.85rem;">Nenhum nível nesta faixa selecionada.</div>`;
      return;
    }

    container.innerHTML = `
      <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left;">
        <thead>
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.15); color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">
            <th style="padding: 6px 8px;">Nível</th>
            <th style="padding: 6px 8px;">Custos</th>
            <th style="padding: 6px 8px;">Taxas de Sucesso / Falha</th>
            <th style="padding: 6px 8px;">Efeito Concedido</th>
            <th style="padding: 6px 8px;">Marco / Recompensa</th>
          </tr>
        </thead>
        <tbody>
          ${levels.map(l => {
            const isFinal = l.final;
            const hasMilestone = l.rewards && l.rewards.length > 0;
            const rowBg = isFinal ? 'background: rgba(168,85,247,0.12);' : hasMilestone ? 'background: rgba(245,158,11,0.08);' : '';

            const costsHtml = l.costs && l.costs.length > 0 ? l.costs.map(c => `
              <span style="display: inline-flex; align-items: center; gap: 4px; margin-right: 6px;">
                <img src="${c.icon}" style="width: 14px; height: 14px; object-fit: contain;">
                <span>${c.amount.toLocaleString()}</span>
              </span>
            `).join('') : '<span style="color: #64748b;">— (Nível Terminal)</span>';

            let ratesHtml = '';
            if (l.costs && l.costs.length > 0) {
              const failStyle = l.fail > 0 ? 'color: #f87171;' : 'color: #94a3b8;';
              ratesHtml = `
                <div style="display: flex; gap: 6px; font-size: 0.75rem; font-family: monospace;">
                  <span style="${failStyle}" title="Chance de Falha (Mantém Nível)">F:${l.fail}%</span>
                  <span style="color: #60a5fa;" title="Avanço de +1 Estágio">+1:${l.s1}%</span>
                  <span style="color: #c084fc;" title="Avanço de +2 Estágios">+2:${l.s2}%</span>
                  <span style="color: #fbbf24;" title="Avanço de +3 Estágios">+3:${l.s3}%</span>
                </div>
              `;
            } else {
              ratesHtml = '<span style="color: #64748b;">—</span>';
            }

            const effectsHtml = l.effects && l.effects.length > 0 ? l.effects.map(e => `
              <span style="color: #34d399; font-weight: 600;">${e.name}: <strong>${e.val}</strong></span>
            `).join(', ') : '<span style="color: #64748b;">Nível Base</span>';

            let milestoneHtml = '';
            if (isFinal) {
              milestoneHtml = `<span class="badge" style="background: rgba(168,85,247,0.25); color: #c084fc; border: 1px solid rgba(168,85,247,0.4); font-size: 0.7rem;">🎉 Evento Final</span>`;
            } else if (hasMilestone) {
              milestoneHtml = l.rewards.map(r => `<span class="badge" style="background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4); font-size: 0.7rem;">🏆 ${r.name}</span>`).join(' ');
            } else {
              milestoneHtml = '<span style="color: #475569;">—</span>';
            }

            return `
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); ${rowBg}">
                <td style="padding: 6px 8px; font-weight: 700; color: #fff; font-family: monospace;">Nv. ${l.level}</td>
                <td style="padding: 6px 8px;">${costsHtml}</td>
                <td style="padding: 6px 8px;">${ratesHtml}</td>
                <td style="padding: 6px 8px;">${effectsHtml}</td>
                <td style="padding: 6px 8px;">${milestoneHtml}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `;
  };

  // ==========================================
  // 18. BLOODLINE (LINHAGEM) RENDERING
  // ==========================================
  function renderBloodline() {
    const container = document.getElementById('bloodlineContainer');
    if (!container || !state.data.bloodline) return;

    let chapters = state.data.bloodline.chapters || [];

    // Filter by chapter range
    if (state.bloodlineFilter === 'early') {
      chapters = chapters.filter(c => c.chapter >= 1 && c.chapter <= 5);
    } else if (state.bloodlineFilter === 'late') {
      chapters = chapters.filter(c => c.chapter >= 6 && c.chapter <= 10);
    }

    // Search query
    const q = (state.bloodlineSearchTerm || '').toLowerCase().trim();
    if (q) {
      chapters = chapters.filter(c => 
        c.name.toLowerCase().includes(q) ||
        c.quest_name.toLowerCase().includes(q) ||
        c.prerequisite_quest_name.toLowerCase().includes(q) ||
        c.boss.name.toLowerCase().includes(q) ||
        String(c.dungeon_id).includes(q) ||
        c.transformations.some(t => t.name.toLowerCase().includes(q) || t.title.toLowerCase().includes(q) || t.class_name.toLowerCase().includes(q))
      );
    }

    if (chapters.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px; color: #94a3b8; background: rgba(0,0,0,0.2); border-radius: 12px;">
          <p style="font-size: 1.1rem; margin-bottom: 8px;">Nenhuma memória de Linhagem encontrada para os filtros atuais.</p>
          <p style="font-size: 0.85rem;">Tente ajustar sua busca ou selecionar "Todas as Memórias".</p>
        </div>
      `;
      return;
    }

    container.innerHTML = chapters.map(c => {
      const boss = c.boss;
      const rewardsPreview = c.rewards.slice(0, 4);

      // Unique transforms mini badges
      const transformsBadges = c.transformations.map(t => `
        <span class="badge" style="background: rgba(255,255,255,0.06); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1); font-size: 0.72rem; display: inline-flex; align-items: center; gap: 4px; padding: 2px 6px;">
          <img src="${t.class_icon}" style="width: 12px; height: 12px; object-fit: contain;">
          <span>${t.name}</span>
        </span>
      `).join('');

      return `
        <div class="entity-card" style="display: flex; flex-direction: column; justify-content: space-between; border-color: rgba(239,68,68,0.25); background: linear-gradient(180deg, rgba(25,15,20,0.7) 0%, rgba(15,10,15,0.85) 100%);">
          <div>
            <!-- Header Badges -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span class="badge" style="background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4); font-weight: 700;">
                Capítulo ${c.chapter}
              </span>
              <span class="badge" style="background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); font-size: 0.75rem;">
                ⏱️ 15 min (900s)
              </span>
            </div>

            <!-- Memory Title & Quest -->
            <div style="display: flex; gap: 14px; margin-bottom: 14px;">
              <div style="width: 72px; height: 72px; flex-shrink: 0; border-radius: 8px; overflow: hidden; background: rgba(0,0,0,0.5); border: 1px solid rgba(239,68,68,0.3); position: relative;">
                <img src="${boss.img}" alt="${boss.name}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='assets/monsters/raab_01.png'">
                <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.75); font-size: 0.65rem; color: #fca5a5; text-align: center; padding: 1px 0; font-weight: 600;">
                  ${boss.name}
                </div>
              </div>
              <div style="flex: 1; min-width: 0;">
                <h3 style="font-size: 1.1rem; color: #fff; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${c.name}">
                  ${c.name}
                </h3>
                <div style="font-size: 0.82rem; color: #f87171; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                  <img src="assets/bloodline/quest_bloodline.png" style="width: 14px; height: 14px; object-fit: contain;">
                  <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${c.quest_name}</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="Missão pré-requisito da campanha: ${c.prerequisite_quest_name}">
                  📜 Requer: <strong style="color: #cbd5e1;">${c.prerequisite_quest_name}</strong>
                </div>
              </div>
            </div>

            <!-- Key Features / Scaling -->
            <div style="background: rgba(0,0,0,0.3); border-radius: 6px; padding: 8px 10px; margin-bottom: 12px; font-size: 0.78rem; display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #94a3b8;">Herança de Atributos:</span>
              <strong style="color: #34d399;">+25% dos Atributos do PC</strong>
            </div>

            <!-- Transformations Preview -->
            <div style="margin-bottom: 12px;">
              <div style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">
                5 Guerreiros Elottarvizianos:
              </div>
              <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                ${transformsBadges}
              </div>
            </div>

            <!-- Rewards Preview -->
            <div style="margin-bottom: 14px;">
              <div style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px;">
                Recompensas Destacadas:
              </div>
              <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                ${rewardsPreview.map(r => `
                  <span class="badge" style="background: rgba(0,0,0,0.4); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.08); font-size: 0.72rem; display: inline-flex; align-items: center; gap: 4px;">
                    <img src="${r.icon}" style="width: 13px; height: 13px; object-fit: contain;">
                    <span>${r.name === 'EXP' || r.name === 'Ouro' ? r.count_display + ' ' + r.name : r.name}</span>
                  </span>
                `).join('')}
                ${c.rewards.length > 4 ? `<span style="font-size: 0.72rem; color: #94a3b8; align-self: center;">+${c.rewards.length - 4}</span>` : ''}
              </div>
            </div>
          </div>

          <!-- Action Button -->
          <button class="btn btn-primary" onclick="window.inspectBloodline('${c.dungeon_id}')" style="width: 100%; justify-content: center; background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%); border: 1px solid rgba(239,68,68,0.5); color: #fff;">
            <span>Inspecionar Memória & Habilidades</span>
            <span>➔</span>
          </button>
        </div>
      `;
    }).join('');
  }

  // Inspect Bloodline Chapter Details in Modal
  window.inspectBloodline = function(dungeonId) {
    if (!state.data.bloodline) return;
    const chapter = state.data.bloodline.chapters.find(c => String(c.dungeon_id) === String(dungeonId));
    if (!chapter) return;

    modalTitle.textContent = `Capítulo ${chapter.chapter}: ${chapter.name}`;
    modalSubtitle.textContent = `Instância de Memória #${chapter.dungeon_id} • Missão: ${chapter.quest_name}`;

    const boss = chapter.boss;

    modalBody.innerHTML = `
      <!-- Showcase Header Banner -->
      <div style="position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 24px; border: 1px solid rgba(239,68,68,0.3); background: #000;">
        <div style="position: absolute; inset: 0; background: url('assets/bloodline/bloodline_dungeon_bg.png') center/cover no-repeat; opacity: 0.35;"></div>
        <div style="position: relative; z-index: 1; padding: 24px; display: flex; flex-direction: column; gap: 16px; background: linear-gradient(180deg, rgba(20,10,15,0.7) 0%, rgba(10,5,10,0.95) 100%);">
          <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
            <div style="width: 96px; height: 96px; border-radius: 12px; overflow: hidden; border: 2px solid #ef4444; box-shadow: 0 0 20px rgba(239,68,68,0.4); flex-shrink: 0; background: #000;">
              <img src="${boss.img}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div style="flex: 1; min-width: 240px;">
              <div style="display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
                <span class="badge" style="background: rgba(239,68,68,0.3); color: #fca5a5; border: 1px solid rgba(239,68,68,0.5); font-weight: 700;">
                  Capítulo ${chapter.chapter} de 10
                </span>
                <span class="badge" style="background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4);">
                  ⏱️ Tempo Limite: 15 min (900s)
                </span>
                <span class="badge" style="background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.4);">
                  ⚡ Herança: +25% dos Atributos
                </span>
              </div>
              <h2 style="font-size: 1.5rem; color: #fff; margin-bottom: 4px; font-family: var(--font-serif);">${chapter.name}</h2>
              <div style="color: #cbd5e1; font-size: 0.88rem;">
                Chefe da Memória: <strong style="color: #f87171;">${boss.name}</strong> (${boss.title})
              </div>
            </div>
          </div>

          <!-- Rules bar -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; background: rgba(0,0,0,0.4); border-radius: 8px; padding: 12px; border: 1px solid rgba(255,255,255,0.08); font-size: 0.8rem;">
            <div>
              <span style="color: #94a3b8;">Missão Narrativa:</span>
              <div style="font-weight: 600; color: #fca5a5;">${chapter.quest_name} (#${chapter.quest_id})</div>
            </div>
            <div>
              <span style="color: #94a3b8;">Missão Prévia Exigida:</span>
              <div style="font-weight: 600; color: #60a5fa;">${chapter.prerequisite_quest_name} (#${chapter.prerequisite_quest_id})</div>
            </div>
            <div>
              <span style="color: #94a3b8;">Restrições de Grupo:</span>
              <div style="font-weight: 600; color: #f87171;">Saída de Grupo • Anti-AFK</div>
            </div>
            <div>
              <span style="color: #94a3b8;">Condição de Entrada:</span>
              <div style="font-weight: 600; color: #34d399;">Nv. Rec: 20+ (Restrito: Nv. 1)</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recompensas da Memória -->
      <div style="margin-bottom: 24px;">
        <h3 style="font-size: 1.1rem; color: #fbbf24; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
          <span>🎁</span>
          <span>Recompensas da Conclusão</span>
        </h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">
          ${chapter.rewards.map(r => `
            <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; display: flex; align-items: center; gap: 12px;">
              <img src="${r.icon}" style="width: 32px; height: 32px; object-fit: contain; flex-shrink: 0;">
              <div>
                <div style="font-weight: 700; color: #fff; font-size: 0.88rem;">${r.count_display}x</div>
                <div style="font-size: 0.78rem; color: #cbd5e1; word-break: break-word;">${r.name}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- As 5 Transformações Elottarvizianas -->
      <div>
        <h3 style="font-size: 1.1rem; color: #f87171; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
          <span>⚔️</span>
          <span>Transformações Elottarvizianas & Habilidades (${chapter.transformations.length} Classes)</span>
        </h3>
        
        <!-- Class Selector Tabs -->
        <div style="display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 4px;">
          ${chapter.transformations.map((t, idx) => `
            <button class="filter-btn ${idx === 0 ? 'active' : ''}" 
                    id="bTabBtn-${chapter.dungeon_id}-${t.class_id}" 
                    onclick="window.switchBloodlineTransform('${chapter.dungeon_id}', '${t.class_id}')"
                    style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px;">
              <img src="${t.class_icon}" style="width: 16px; height: 16px; object-fit: contain;">
              <span>${t.name} (${t.class_name.split(' ')[0]})</span>
            </button>
          `).join('')}
        </div>

        <!-- Transform Details Container -->
        <div id="bloodlineTransformDetails">
          ${renderTransformDetailsHtml(chapter.transformations[0])}
        </div>
      </div>
    `;

    detailModal.classList.add('active');
  };

  function renderTransformDetailsHtml(t) {
    return `
      <div style="background: rgba(0,0,0,0.35); border: 1px solid rgba(239,68,68,0.25); border-radius: 10px; padding: 16px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <img src="${t.class_icon}" style="width: 24px; height: 24px; object-fit: contain;">
              <h4 style="font-size: 1.2rem; color: #fff; margin: 0;">${t.full_name}</h4>
              <span class="badge" style="background: rgba(239,68,68,0.2); color: #fca5a5; border: 1px solid rgba(239,68,68,0.4); font-size: 0.75rem;">
                ${t.class_name}
              </span>
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
              Modelo: <code>${t.resource}</code> • Gênero: ${t.gender}
            </div>
          </div>
          <div style="display: flex; gap: 8px;">
            <div style="background: rgba(0,0,0,0.4); border-radius: 6px; padding: 6px 10px; text-align: center; border: 1px solid rgba(255,255,255,0.08);">
              <div style="font-size: 0.68rem; color: #94a3b8;">Vel. Movimento</div>
              <div style="font-weight: 700; color: #60a5fa; font-size: 0.85rem;">${t.move_speed}</div>
            </div>
            <div style="background: rgba(0,0,0,0.4); border-radius: 6px; padding: 6px 10px; text-align: center; border: 1px solid rgba(255,255,255,0.08);">
              <div style="font-size: 0.68rem; color: #94a3b8;">Raio do Corpo</div>
              <div style="font-weight: 700; color: #fbbf24; font-size: 0.85rem;">${t.body_radius}</div>
            </div>
            <div style="background: rgba(0,0,0,0.4); border-radius: 6px; padding: 6px 10px; text-align: center; border: 1px solid rgba(16,185,129,0.3);">
              <div style="font-size: 0.68rem; color: #94a3b8;">Herança de Status</div>
              <div style="font-weight: 700; color: #34d399; font-size: 0.85rem;">+${t.character_operation_add_rate}% PC</div>
            </div>
          </div>
        </div>

        <!-- Skills Deck -->
        <h5 style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 10px; text-transform: uppercase; font-weight: 700;">
          Deck de Combate do Guerreiro (${t.skills.length} Habilidades)
        </h5>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${t.skills.map(s => {
            const isDeadly = s.is_deadly;
            const borderCol = isDeadly ? 'rgba(239,68,68,0.5)' : 'rgba(255,255,255,0.08)';
            const bgCol = isDeadly ? 'rgba(239,68,68,0.1)' : 'rgba(0,0,0,0.25)';
            return `
              <div style="background: ${bgCol}; border: 1px solid ${borderCol}; border-radius: 8px; padding: 10px; display: flex; gap: 12px; align-items: flex-start;">
                <img src="${s.icon}" style="width: 36px; height: 36px; object-fit: contain; border-radius: 6px; flex-shrink: 0; background: rgba(0,0,0,0.3);" onerror="this.src='assets/classes/logo.png'">
                <div style="flex: 1; min-width: 0;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; flex-wrap: wrap; gap: 6px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                      <strong style="color: ${isDeadly ? '#fca5a5' : '#fff'}; font-size: 0.9rem;">${s.name}</strong>
                      <span class="badge" style="font-size: 0.68rem; padding: 1px 5px; background: rgba(255,255,255,0.06); color: ${isDeadly ? '#ef4444' : '#94a3b8'}; border: 1px solid rgba(255,255,255,0.1);">
                        ${s.category}
                      </span>
                    </div>
                    <div style="display: flex; gap: 8px; font-size: 0.75rem; color: #94a3b8;">
                      <span>⏳ CD: <strong style="color: #60a5fa;">${s.cooldown}</strong></span>
                      <span>🎯 Alcance: <strong style="color: #fbbf24;">${s.range}</strong></span>
                      <span>💧 ${s.mp}</span>
                    </div>
                  </div>
                  <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.4;">
                    ${s.description || s.effect_description || 'Habilidade de combate corporal do Elottarviziano.'}
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  window.switchBloodlineTransform = function(dungeonId, classId) {
    if (!state.data.bloodline) return;
    const chapter = state.data.bloodline.chapters.find(c => String(c.dungeon_id) === String(dungeonId));
    if (!chapter) return;

    const transform = chapter.transformations.find(t => String(t.class_id) === String(classId));
    if (!transform) return;

    // Update active tab buttons
    chapter.transformations.forEach(t => {
      const btn = document.getElementById(`bTabBtn-${dungeonId}-${t.class_id}`);
      if (btn) btn.classList.toggle('active', String(t.class_id) === String(classId));
    });

    const container = document.getElementById('bloodlineTransformDetails');
    if (container) {
      container.innerHTML = renderTransformDetailsHtml(transform);
    }
  };

  // Render FAQ
  function renderFaq() {
    const container = document.getElementById('faqContainer');
    if (!container || !state.data.faq) return;

    container.innerHTML = state.data.faq.map((item, idx) => `
      <div class="faq-item" id="faqItem-${idx}">
        <div class="faq-question" onclick="window.toggleFaq(${idx})">
          <span>${item.question}</span>
          <span class="faq-chevron">▼</span>
        </div>
        <div class="faq-answer">
          <div class="faq-answer-inner">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--gold-primary); margin-bottom: 6px; font-weight: 700;">
              Categoria: ${item.category}
            </div>
            ${item.answer}
          </div>
        </div>
      </div>
    `).join('');
  }

  window.toggleFaq = function(idx) {
    const el = document.getElementById(`faqItem-${idx}`);
    if (el) el.classList.toggle('open');
  };

  // Inspect Modal Handlers
  window.inspectSkill = function(id) {
    const s = state.data.skills.find(x => x.id === id);
    if (!s) return;

    modalTitle.innerText = s.name;
    modalSubtitle.innerText = `${s.class_name} • Habilidade ID #${s.id}`;

    modalBody.innerHTML = `
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <img src="${s.icon_img || 'assets/logo.png'}" alt="${s.name}" style="width: 56px; height: 56px; border-radius: 8px; border: 1px solid var(--border-gold);" onerror="this.src='assets/logo.png'">
        <div style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.6;">
          ${s.description || s.effect_description || 'Sem descrição adicional.'}
        </div>
      </div>
      <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px;">
        <div class="panel-box">
          <div class="panel-title">Recarga (Cooldown)</div>
          <div style="font-size: 1.2rem; color: #fff; font-weight: 700;">${s.cooldown}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Custo de Mana</div>
          <div style="font-size: 1.2rem; color: #fff; font-weight: 700;">${s.mp_cost}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Alcance Máximo</div>
          <div style="font-size: 1.2rem; color: #fff; font-weight: 700;">${s.range}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Tipo de Alvo</div>
          <div style="font-size: 1.2rem; color: #fff; font-weight: 700;">${s.target_type}</div>
        </div>
      </div>
      <div class="panel-box">
        <div class="panel-title">Parâmetros de Motor & Código</div>
        <div style="font-size: 0.85rem; color: var(--text-muted); font-family: monospace;">
          Stack Count: ${s.stack_count} | Mobile Cast: ${s.mobile ? 'Sim (Permite Andar)' : 'Não'} | Dash Offset: ${s.dash_offset}
        </div>
      </div>
    `;

    detailModal.classList.add('open');
  };

  window.inspectBoss = function(id) {
    const b = state.data.bosses.find(x => x.id === id || (x.instance_ids && x.instance_ids.includes(id)));
    if (!b) return;

    modalTitle.innerText = b.name;
    modalSubtitle.innerText = `${b.title} • ${b.level_display || 'Nv. ' + b.level} (${b.grade_name})`;

    // Multi-tier table
    let tiersHtml = '';
    if (b.tiers && b.tiers.length > 1) {
      tiersHtml = `
        <div style="margin-bottom: 20px;">
          <h4 style="font-family: var(--font-serif); color: var(--gold-primary); margin-bottom: 10px;">
            📊 Variações de Nível & Andar (${b.tiers.length} Tiers)
          </h4>
          <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left;">
              <thead>
                <tr style="border-bottom: 1px solid var(--border-gold); color: var(--gold-light);">
                  <th style="padding: 6px 8px;">Nível</th>
                  <th style="padding: 6px 8px;">Vida (HP)</th>
                  <th style="padding: 6px 8px;">Ataque</th>
                  <th style="padding: 6px 8px;">Defesa</th>
                  <th style="padding: 6px 8px;">Masmorra / Instância</th>
                  <th style="padding: 6px 8px;">ID do Registro</th>
                </tr>
              </thead>
              <tbody>
                ${b.tiers.map(t => `
                  <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 6px 8px; color: var(--blue-primary); font-weight: 700;">Nv. ${t.level}</td>
                    <td style="padding: 6px 8px; color: #ef4444; font-weight: 600;">${formatBigNumber(t.hp)}</td>
                    <td style="padding: 6px 8px; color: #eab308;">${formatBigNumber(t.atk)}</td>
                    <td style="padding: 6px 8px; color: #3b82f6;">${formatBigNumber(t.def)}</td>
                    <td style="padding: 6px 8px; color: var(--text-muted);">${t.dungeon || '-'}</td>
                    <td style="padding: 6px 8px; color: var(--text-dim); font-family: monospace;">#${t.id}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;
    }

    // Real Combat Skills
    let skillsHtml = '';
    if (b.skills && b.skills.length > 0) {
      skillsHtml = `
        <div style="margin-bottom: 20px;">
          <h4 style="font-family: var(--font-serif); color: var(--gold-primary); margin-bottom: 10px;">
            ⚔️ Habilidades de Combate do Chefe (${b.skills.length})
          </h4>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            ${b.skills.map(s => `
              <div class="panel-box" style="border-left: 3px solid var(--crimson-primary);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: 700; color: #fff; font-size: 0.95rem;">${s.name}</span>
                  <div style="display: flex; gap: 8px;">
                    ${s.cooldown !== '-' ? `<span class="entity-badge badge-gold">⏱️ Recarga: ${s.cooldown}</span>` : ''}
                    ${s.range !== '-' ? `<span class="entity-badge badge-blue">🎯 Alcance: ${s.range}</span>` : ''}
                  </div>
                </div>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 6px; line-height: 1.4;">
                  ${s.desc}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // Spawns & Schedule Box
    let spawnHtml = '';
    if (b.spawn_schedule || b.world_map) {
      spawnHtml = `
        <div class="panel-box" style="margin-bottom: 16px; border-left: 3px solid var(--gold-primary);">
          <div class="panel-title">🗺️ Aparição & Horários de Respawn</div>
          <div style="color: #fff; font-size: 0.9rem; line-height: 1.6; margin-top: 4px;">
            <strong>Mundo / Mapa:</strong> ${b.world_map || 'Masmorra / Campo Dimensional'}<br>
            ${b.spawn_schedule ? `<strong>Horário Programado:</strong> <span style="color: var(--gold-light); font-weight: 700;">${b.spawn_schedule}</span><br>` : ''}
            ${b.dungeons && b.dungeons.length ? `<strong>Masmorras Vinculadas:</strong> ${b.dungeons.join(', ')}<br>` : ''}
            ${b.instance_count > 1 ? `<strong>Instâncias Registradas:</strong> <span style="color: var(--blue-primary);">${b.instance_count} nós/cópias ativos</span> (IDs: ${b.instance_ids.slice(0, 10).join(', ')}${b.instance_ids.length > 10 ? '...' : ''})` : `<strong>ID do Registro:</strong> #${b.id}`}
          </div>
        </div>
      `;
    }

    // Monster Drops & Rewards
    let dropsHtml = '';
    if (b.drops && b.drops.length > 0) {
      dropsHtml = `
        <div class="panel-box" style="margin-bottom: 20px; border-left: 3px solid var(--gold-primary);">
          <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>📦 Drops & Recompensas Confirmadas (${b.drops.length} itens)</span>
            <span style="font-size: 0.72rem; color: #94a3b8; font-weight: normal;">Fonte: NpcReward.csv</span>
          </div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 12px; line-height: 1.4;">
            Itens e equipamentos cadastrados no grupo de recompensa deste monstro. Clique em <strong>Ver Item</strong> para inspecionar os detalhes do item.
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px; max-height: 320px; overflow-y: auto; padding-right: 4px;">
            ${b.drops.map(d => `
              <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
                  <img src="${d.icon}" style="width: 34px; height: 34px; border-radius: 6px; object-fit: contain; background: rgba(0,0,0,0.4); padding: 2px;" onerror="this.src='assets/logo.png'">
                  <div style="min-width: 0;">
                    <div style="font-size: 0.82rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${d.name}">${d.name}</div>
                    <div style="font-size: 0.72rem; color: #fbbf24;">Qtd: <strong>${d.qty}</strong></div>
                  </div>
                </div>
                <button class="filter-btn" style="padding: 3px 8px; font-size: 0.72rem; flex-shrink: 0;" onclick="window.openItemFromBoss('${d.id}')">Ver Item 🎒</button>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    modalBody.innerHTML = `
      <div style="margin-bottom: 20px; text-align: center;">
        <img src="${b.portrait_img}" alt="${b.name}" style="max-height: 220px; border-radius: 8px; border: 1px solid var(--border-gold); box-shadow: 0 0 20px rgba(0,0,0,0.8);" onerror="this.src='assets/splash.png'">
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 20px;">
        <div class="panel-box">
          <div class="panel-title">Vida (HP)</div>
          <div style="font-size: 1.1rem; color: #ef4444; font-weight: 700;">${formatBigNumber(b.hp_raw)}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Poder de Ataque</div>
          <div style="font-size: 1.1rem; color: #eab308; font-weight: 700;">${formatBigNumber(b.atk_raw)}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Defesa</div>
          <div style="font-size: 1.1rem; color: #3b82f6; font-weight: 700;">${formatBigNumber(b.def_raw)}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Raio de Visão</div>
          <div style="font-size: 1.1rem; color: #fff; font-weight: 700;">${b.sight_range}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Comportamento</div>
          <div style="font-size: 1.0rem; color: ${b.is_aggressive ? '#ef4444' : '#10b981'}; font-weight: 700;">${b.is_aggressive ? 'Hostil (Aggro)' : 'Passivo'}</div>
        </div>
        <div class="panel-box">
          <div class="panel-title">Elemento / Tipo</div>
          <div style="font-size: 1.0rem; color: var(--gold-primary); font-weight: 700;">${b.attribute}</div>
        </div>
      </div>

      ${tiersHtml}
      ${skillsHtml}
      ${spawnHtml}
      ${dropsHtml}

      <div class="panel-box">
        <div class="panel-title">⚙️ Parâmetros de Motor & IA (Unreal Engine 5)</div>
        <div style="font-size: 0.85rem; color: var(--text-muted); font-family: monospace; line-height: 1.6;">
          Blueprint: <strong>${b.blueprint || 'Padrão'}</strong><br>
          Mecânica Especial / Animação: <strong>${b.appearance_type}</strong><br>
          Escala de Modelo: ${b.scale_factor}x | Raio do Corpo: ${b.body_radius} | Velocidade (Caminhar: ${b.walk_speed} / Corrida: ${b.run_speed})
        </div>
      </div>
    `;

    detailModal.classList.add('open');
  };

  window.inspectDungeon = function(id) {
    const d = state.data.dungeons.find(x => x.id === id);
    if (!d) return;

    modalTitle.innerText = d.name;
    modalSubtitle.innerText = `${d.type_name} • ID #${d.id}`;

    modalBody.innerHTML = `
      <div style="margin-bottom: 20px; text-align: center;">
        <img src="${d.bg_img}" alt="${d.name}" style="max-height: 200px; width: 100%; object-fit: cover; border-radius: 8px; border: 1px solid var(--border-gold);" onerror="this.src='assets/splash.png'">
      </div>
      <div style="margin-bottom: 20px; font-size: 0.95rem; color: #cbd5e1; line-height: 1.6;">
        ${d.description}
      </div>
      <div class="panel-box" style="margin-bottom: 16px;">
        <div class="panel-title">Requisitos de Nível</div>
        <div style="color: #fff; font-size: 1rem;">
          Nível Mínimo Restrito: <strong>${d.req_level}</strong> | Nível Recomendado: <strong>${d.rec_level}</strong>
        </div>
      </div>
      <div class="panel-box">
        <div class="panel-title">Sistema de Avaliação</div>
        <div style="color: var(--gold-primary); font-size: 0.95rem;">
          ${d.max_clear_grade}
        </div>
      </div>
    `;

    detailModal.classList.add('open');
  };

  window.openItemFromBoss = function(itemId) {
    detailModal.classList.remove('open');
    switchTab('items');
    setTimeout(() => {
      window.inspectItem(itemId);
    }, 120);
  };

  window.openBossFromItem = function(bossId) {
    detailModal.classList.remove('open');
    switchTab('bosses');
    setTimeout(() => {
      window.inspectBoss(bossId);
    }, 120);
  };

  window.inspectItem = function(id) {
    const item = state.data.items.find(x => x.id === id);
    if (!item) return;

    modalTitle.innerText = item.name;
    modalSubtitle.innerText = `${item.type_name} • Tier ${item.tier} (ID #${item.id})`;

    let droppersHtml = '';
    if (item.droppers && item.droppers.length > 0) {
      droppersHtml = `
        <div class="panel-box" style="margin-top: 16px; border-left: 3px solid #38bdf8;">
          <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>💀 Monstros que Dropam este Item (${item.droppers.length} fontes)</span>
            <span style="font-size: 0.72rem; color: #94a3b8; font-weight: normal;">Fonte: NpcReward.csv</span>
          </div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 10px; line-height: 1.4;">
            Monstros e chefes de campo com drop direto catalogado. Clique em <strong>Ver Monstro</strong> para ver horários, habilidades e localização.
          </p>
          <div style="display: flex; flex-direction: column; gap: 8px; max-height: 280px; overflow-y: auto; padding-right: 4px;">
            ${item.droppers.map(dr => {
              const gradeClass = dr.grade_code === '3' ? 'badge-crimson' : (dr.grade_code === '2' ? 'badge-gold' : (dr.grade_code === '1' ? 'badge-blue' : 'badge-gray'));
              return `
                <div style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 12px; display: flex; align-items: center; justify-content: space-between; gap: 10px;">
                  <div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: #fff;">
                      ${dr.name} <span class="entity-badge ${gradeClass}" style="font-size: 0.68rem; margin-left: 4px;">${dr.grade}</span>
                      ${dr.lvl ? `<span style="font-size: 0.75rem; color: #38bdf8; margin-left: 4px;">(Nv. ${dr.lvl})</span>` : ''}
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">
                      <strong>Região:</strong> ${dr.world || 'Campo / Masmorra'} • <strong>Qtd:</strong> ${dr.qty}
                    </div>
                  </div>
                  <button class="filter-btn" style="padding: 4px 10px; font-size: 0.75rem; flex-shrink: 0;" onclick="window.openBossFromItem('${dr.id}')">Ver Monstro 💀</button>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    } else {
      droppersHtml = `
        <div class="panel-box" style="margin-top: 16px; border-left: 3px solid #64748b;">
          <div class="panel-title">💀 Monstros que Dropam este Item</div>
          <p style="font-size: 0.84rem; color: #94a3b8; margin: 4px 0 0; line-height: 1.4;">
            Este item não possui drop direto registrado na tabela de NPCs locais (obtido através de Forja, Missão de Campanha, Baús de Evento ou Lojas do Jogo).
          </p>
        </div>
      `;
    }

    let collectionsHtml = '';
    if (item.collections && item.collections.length > 0) {
      collectionsHtml = `
        <div class="panel-box" style="margin-top: 16px; border-left: 3px solid #eab308;">
          <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center;">
            <span>📖 Coleções do Códex que Utilizam este Item (${item.collections.length} conjuntos)</span>
            <span style="font-size: 0.72rem; color: #94a3b8; font-weight: normal;">Fonte: CollectionGroup.csv</span>
          </div>
          <p style="font-size: 0.82rem; color: #94a3b8; margin: 4px 0 10px; line-height: 1.4;">
            Este item é requisito para completar conjuntos no Códex e obter bônus permanentes.
          </p>
          <div style="display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; padding-right: 4px;">
            ${item.collections.map(c => `
              <div style="background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; gap: 10px;">
                <div>
                  <div style="font-size: 0.85rem; font-weight: 600; color: #fff;">${c.name}</div>
                  <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">
                    <span>${c.tab}</span> • Exige: <span style="color: #fbbf24; font-weight: 700;">+${c.ench}</span> (Qtd: ${c.qty})
                  </div>
                </div>
                <button class="filter-btn" style="padding: 4px 10px; font-size: 0.75rem; flex-shrink: 0;" onclick="window.openCodexFromItem('${c.id}')">Ver no Códex 📖</button>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    modalBody.innerHTML = `
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <div class="item-slot-frame" style="width: 64px; height: 64px;">
          <img src="${item.icon_img}" alt="${item.name}" class="item-slot-img" onerror="this.src='assets/logo.png'">
        </div>
        <div style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.6;">
          ${item.desc}
        </div>
      </div>
      <div class="panel-box">
        <div class="panel-title">Encantamento e Restrições</div>
        <div style="color: var(--crimson-light); font-size: 0.9rem;">
          ${item.max_enchant}
        </div>
      </div>
      ${droppersHtml}
      ${collectionsHtml}
    `;

    detailModal.classList.add('open');
  };

  window.inspectQuest = function(id) {
    const q = state.data.quests.find(x => x.id === id);
    if (!q) return;

    modalTitle.innerText = q.name;
    modalSubtitle.innerText = `${q.type_pt} • Nível ${q.req_level} (Missão ID #${q.id})`;

    modalBody.innerHTML = `
      <div class="panel-box" style="margin-bottom: 16px;">
        <div class="panel-title">Parâmetros da Jornada</div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 0.88rem; color: #cbd5e1;">
          <div>Tipo da Missão: <strong style="color: var(--gold-primary);">${q.type_pt}</strong></div>
          <div>Nível Requerido: <strong>Nv. ${q.req_level}</strong></div>
          <div>Tarefas Sequenciais: <strong>${q.tasks_count} etapas</strong></div>
          <div>Grupos de Recompensa: <strong>${q.rewards_count} grupos</strong></div>
          <div>Cópia Instanciada: <strong>${q.has_instance ? 'Sim (Cinemática Privada)' : 'Não (Mundo Aberto)'}</strong></div>
          <div>Missão Anterior: <strong>${q.pre_quest ? '#' + q.pre_quest : 'Nenhuma (Início de Linha)'}</strong></div>
        </div>
      </div>
      <div style="font-size: 0.9rem; color: #94a3b8; line-height: 1.6;">
        Esta missão integra o sistema mestre de 1.353 missões extraídas de <code>Quest.csv</code> e vinculadas a 5.944 registros de tarefas em <code>QuestTask.csv</code>. As tarefas incluem objetivos de diálogo, eliminação de monstros com contadores e acionamento de bandeiras narrativas.
      </div>
    `;

    detailModal.classList.add('open');
  };

  window.inspectRecipe = function(id) {
    const c = state.data.crafting.find(x => x.id === id);
    if (!c) return;

    modalTitle.innerText = `Forja: ${c.target_name}`;
    modalSubtitle.innerText = `${c.tab_name} • Receita ID #${c.id}`;

    modalBody.innerHTML = `
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <div class="item-slot-frame" style="width: 56px; height: 56px;">
          <img src="${c.icon_img}" alt="${c.target_name}" class="item-slot-img" onerror="this.src='assets/logo.png'">
        </div>
        <div style="flex: 1;">
          <div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 4px;">${c.target_name}</div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            <span class="entity-badge badge-gold">${c.tab_name}</span>
            <span class="entity-badge ${c.big_success_rate !== '0%' ? 'badge-blue' : 'badge-crimson'}">
              Sucesso: ${c.success_rate} ${c.big_success_rate !== '0%' ? '• Gr. Sucesso: ' + c.big_success_rate : ''}
            </span>
          </div>
        </div>
      </div>
      <div class="panel-box">
        <div class="panel-title" style="display: flex; align-items: center; gap: 8px;">
          <img src="assets/items/flat_itemcraft.png" style="width: 18px; height: 18px; vertical-align: middle;" onerror="this.src='assets/logo.png'">
          Materiais e Recursos Exigidos
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px; margin: 12px 0;">
          ${c.materials.map(m => `
            <div style="display: flex; align-items: center; gap: 12px; background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
              <img src="${m.icon || 'assets/items/flat_itemcraft.png'}" style="width: 32px; height: 32px; border-radius: 6px; object-fit: contain; background: rgba(0,0,0,0.4);" onerror="this.src='assets/logo.png'">
              <div style="flex: 1;">
                <div style="font-weight: 600; color: #f1f5f9;">${m.name}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">${m.type}</div>
              </div>
              <div style="font-weight: 700; color: #fbbf24; font-size: 1rem; font-family: monospace;">
                × ${Number(m.amount).toLocaleString('pt-BR')}
              </div>
            </div>
          `).join('')}
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08);">
          ${c.tradeable_on_big ? '💎 Em caso de Grande Sucesso, o item gerado possui FreeTradeRate=10000 e pode ser vendido livremente no Mercado de Leilões.' : '🔒 O item forjado é vinculado à conta do personagem.'}
        </div>
      </div>
    `;

    detailModal.classList.add('open');
  };

  window.inspectMode = function(id) {
    const m = state.data.modes.find(x => x.id === id);
    if (!m) return;

    modalTitle.innerText = m.title;
    modalSubtitle.innerText = `${m.category_label} • ${m.capacity} • ${m.level_range}`;

    modalBody.innerHTML = `
      <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <div class="item-slot-frame" style="width: 64px; height: 64px;">
          <img src="${m.icon_img}" alt="${m.title}" class="item-slot-img" onerror="this.src='assets/logo.png'">
        </div>
        <div style="flex: 1;">
          <div style="font-size: 1.15rem; font-weight: 700; color: #fff; margin-bottom: 4px;">${m.title}</div>
          <div style="font-size: 0.85rem; color: #94a3b8;">${m.subtitle}</div>
        </div>
      </div>

      <div class="panel-box" style="margin-bottom: 16px;">
        <div class="panel-title">Mecânica & Diretrizes do Modo</div>
        <div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.6; margin-top: 6px;">
          ${m.description}
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 14px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;">
          <div><strong style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Capacidade de Grupo</strong><div style="color: #38bdf8; font-weight: 600;">${m.capacity}</div></div>
          <div><strong style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Faixa de Nível</strong><div style="color: #fbbf24; font-weight: 600;">${m.level_range}</div></div>
          <div><strong style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Custo / Ingresso</strong><div style="color: #e2e8f0; font-size: 0.82rem;">${m.cost}</div></div>
          <div><strong style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Ciclo de Reinício</strong><div style="color: #a78bfa; font-size: 0.82rem;">${m.reset_type}</div></div>
        </div>
      </div>

      <div class="panel-box" style="margin-bottom: 16px;">
        <div class="panel-title">Principais Zonas e Cenários</div>
        <ul style="padding-left: 20px; margin: 8px 0; color: #e2e8f0; font-size: 0.88rem; line-height: 1.6;">
          ${m.key_locations.map(loc => `<li>${loc}</li>`).join('')}
        </ul>
      </div>

      <div class="panel-box" style="margin-bottom: 16px;">
        <div class="panel-title">Principais Recompensas & Espólios</div>
        <ul style="padding-left: 20px; margin: 8px 0; color: #34d399; font-size: 0.88rem; line-height: 1.6;">
          ${m.rewards.map(r => `<li>${r}</li>`).join('')}
        </ul>
      </div>
    `;

    detailModal.classList.add('open');
  };

  // Setup Event Listeners
  function setupListeners() {
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const target = item.dataset.target;
        switchTab(target);
      });
    });

    modalCloseBtn.addEventListener('click', () => detailModal.classList.remove('open'));
    detailModal.addEventListener('click', e => {
      if (e.target === detailModal) detailModal.classList.remove('open');
    });

    globalSearch.addEventListener('input', e => {
      const q = e.target.value;
      if (state.currentTab === 'skills') {
        state.skillsSearchTerm = q;
        state.skillsPage = 1;
        renderSkills();
      } else if (state.currentTab === 'bosses') {
        state.bossesSearchTerm = q;
        state.bossesPage = 1;
        renderBosses();
      } else if (state.currentTab === 'dungeons') {
        state.dungeonsSearchTerm = q;
        renderDungeons();
      } else if (state.currentTab === 'items') {
        state.itemsSearchTerm = q;
        state.itemsPage = 1;
        renderItems();
      } else if (state.currentTab === 'quests') {
        state.questsSearchTerm = q;
        state.questsPage = 1;
        renderQuests();
      } else if (state.currentTab === 'crafting') {
        state.craftingSearchTerm = q;
        state.craftingPage = 1;
        renderCrafting();
      } else if (state.currentTab === 'shops') {
        state.shopsSearchTerm = q;
        state.shopsPage = 1;
        renderShops();
      } else if (state.currentTab === 'codex') {
        if (state.codexTab === 'collections') {
          state.codexSearchTerm = q;
          state.codexPage = 1;
        } else if (state.codexTab === 'entries') {
          state.codexEntriesSearchTerm = q;
          state.codexEntriesPage = 1;
        }
        renderCodex();
      } else if (state.currentTab === 'research') {
        state.researchSearchTerm = q;
        state.researchPage = 1;
        renderResearch();
      } else if (state.currentTab === 'portraits') {
        state.portraitsSearchTerm = q;
        state.portraitsPage = 1;
        renderPortraits();
      } else if (state.currentTab === 'artifacts') {
        state.artifactsSearchTerm = q;
        renderArtifacts();
      }
    });

    document.getElementById('skillsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#skillsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.skillsClassFilter = e.target.dataset.class;
        state.skillsPage = 1;
        renderSkills();
      }
    });

    const regionSelect = document.getElementById('bossesRegionSelect');
    if (regionSelect) {
      const regions = state.data.regions || Array.from(new Set((state.data.bosses || []).flatMap(b => b.regions || []))).filter(Boolean).sort();
      regionSelect.innerHTML = `<option value="all">Todas as Regiões (${regions.length})</option>` +
        regions.map(r => `<option value="${r}">${r}</option>`).join('');
      regionSelect.addEventListener('change', e => {
        state.bossesRegion = e.target.value;
        state.bossesPage = 1;
        renderBosses();
      });
    }

    document.getElementById('bossesFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#bossesFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.bossesFilter = e.target.dataset.grade;
        state.bossesPage = 1;
        renderBosses();
      }
    });

    document.getElementById('dungeonsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#dungeonsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.dungeonsFilter = e.target.dataset.dtype;
        renderDungeons();
      }
    });

    document.getElementById('itemsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#itemsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.itemsFilter = e.target.dataset.itype;
        state.itemsPage = 1;
        renderItems();
      }
    });

    document.getElementById('questsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#questsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.questsFilter = e.target.dataset.qtype;
        state.questsPage = 1;
        renderQuests();
      }
    });

    document.getElementById('craftingFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#craftingFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.craftingFilter = e.target.dataset.ccat;
        state.craftingPage = 1;
        renderCrafting();
      }
    });

    document.getElementById('modesFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#modesFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.modesFilter = e.target.dataset.mcat;
        renderModes();
      }
    });

    document.getElementById('pvpSubNav')?.addEventListener('click', e => {
      const btn = e.target.closest('button');
      if (btn) {
        document.querySelectorAll('#pvpSubNav .pvp-subnav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.pvpTab = btn.dataset.pvptab;
        renderPvP();
      }
    });

    document.getElementById('enchantSubNav')?.addEventListener('click', e => {
      const btn = e.target.closest('button');
      if (btn) {
        document.querySelectorAll('#enchantSubNav .pvp-subnav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.enchantTab = btn.dataset.enchtab;
        renderEnchantment();
      }
    });

    document.getElementById('shopsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#shopsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.shopsFilter = e.target.dataset.scat;
        state.shopsPage = 1;
        renderShops();
      }
    });

    document.getElementById('codexSubNav')?.addEventListener('click', e => {
      const btn = e.target.closest('button');
      if (btn) {
        document.querySelectorAll('#codexSubNav .pvp-subnav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.codexTab = btn.dataset.codextab;
        renderCodex();
      }
    });

    document.getElementById('codexFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#codexFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.codexFilter = e.target.dataset.tabid;
        state.codexPage = 1;
        renderCodexCollections();
      }
    });

    document.getElementById('codexRaritySelect')?.addEventListener('change', e => {
      state.codexRarity = e.target.value;
      state.codexPage = 1;
      renderCodexCollections();
    });

    document.getElementById('codexEntriesFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#codexEntriesFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.codexEntriesFilter = e.target.dataset.etype;
        state.codexEntriesPage = 1;
        renderCodexEntries();
      }
    });

    document.getElementById('researchFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#researchFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.researchFilter = e.target.dataset.mline;
        state.researchPage = 1;
        renderResearch();
      }
    });

    document.getElementById('portraitsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#portraitsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.portraitsFilter = e.target.dataset.prarity;
        state.portraitsPage = 1;
        renderPortraits();
      }
    });

    document.getElementById('portraitsTypeSelect')?.addEventListener('change', e => {
      state.portraitsType = e.target.value;
      state.portraitsPage = 1;
      renderPortraits();
    });

    document.getElementById('artifactsFilterBar')?.addEventListener('click', e => {
      if (e.target.tagName === 'BUTTON') {
        document.querySelectorAll('#artifactsFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        state.artifactsFilter = e.target.dataset.atype;
        renderArtifacts();
      }
    });

    document.getElementById('bloodlineFilterBar')?.addEventListener('click', e => {
      const btn = e.target.closest('button');
      if (btn && btn.dataset.bchapter) {
        document.querySelectorAll('#bloodlineFilterBar .filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.bloodlineFilter = btn.dataset.bchapter;
        renderBloodline();
      }
    });

    document.getElementById('bloodlineSearchInput')?.addEventListener('input', e => {
      state.bloodlineSearchTerm = e.target.value;
      renderBloodline();
    });
  }

  function initApp() {
    renderClasses();
    renderBuilds();
    renderSkills();
    renderBosses();
    renderDungeons();
    renderItems();
    renderQuests();
    renderCrafting();
    renderModes();
    renderPvP();
    renderEnchantment();
    renderShops();
    renderCodex();
    renderResearch();
    renderPortraits();
    renderArtifacts();
    renderBloodline();
    renderFaq();
    setupListeners();
  }

  ensureDataLoaded();
})();
