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
    modesFilter: 'all',
    pvpTab: 'arena',
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
      const [classes, builds, skills, bosses, dungeons, items, faq, constants] = await Promise.all([
        fetch('data/classes.json').then(r => r.json()),
        fetch('data/builds.json').then(r => r.json()),
        fetch('data/skills.json').then(r => r.json()),
        fetch('data/bosses.json').then(r => r.json()),
        fetch('data/dungeons.json').then(r => r.json()),
        fetch('data/items.json').then(r => r.json()),
        fetch('data/faq.json').then(r => r.json()),
        fetch('data/constants.json').then(r => r.json())
      ]);

      state.data = { classes, builds, skills, bosses, dungeons, items, faq, constants };
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

    if (state.bossesFilter !== 'all') {
      filtered = filtered.filter(b => b.grade_code === state.bossesFilter);
    }

    if (state.bossesSearchTerm.trim()) {
      const q = state.bossesSearchTerm.toLowerCase();
      filtered = filtered.filter(b =>
        b.name.toLowerCase().includes(q) ||
        b.title.toLowerCase().includes(q) ||
        b.id.includes(q) ||
        (b.instance_ids && b.instance_ids.some(id => id.includes(q))) ||
        (b.blueprint && b.blueprint.toLowerCase().includes(q)) ||
        (b.world_map && b.world_map.toLowerCase().includes(q))
      );
    }

    const totalFiltered = filtered.length;
    const pageSize = 48;
    const paginated = filtered.slice(0, state.bossesPage * pageSize);

    container.innerHTML = paginated.map(b => {
      const badgeColor = b.grade_code === '3' ? 'badge-crimson' : (b.grade_code === '2' ? 'badge-gold' : 'badge-blue');
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
        i.type_name.toLowerCase().includes(q)
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
            <div style="display: flex; gap: 8px; margin-top: 4px;">
              <span class="entity-badge badge-gold" style="font-size: 0.7rem;">${item.type_name}</span>
              <span class="entity-badge badge-crimson" style="font-size: 0.7rem;">Tier ${item.tier}</span>
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
    }
  }

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

  window.inspectItem = function(id) {
    const item = state.data.items.find(x => x.id === id);
    if (!item) return;

    modalTitle.innerText = item.name;
    modalSubtitle.innerText = `${item.type_name} • Tier ${item.tier} (ID #${item.id})`;

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
    renderFaq();
    setupListeners();
  }

  ensureDataLoaded();
})();
