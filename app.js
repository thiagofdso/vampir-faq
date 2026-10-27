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
    dungeonsFilter: 'all',
    dungeonsSearchTerm: '',
    itemsFilter: 'all',
    itemsSearchTerm: '',
    activeBuildIndex: 0,
    activeVariantIndex: 0
  };

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

  // Render Bosses with Official High-Res Portraits
  function renderBosses() {
    const container = document.getElementById('bossesContainer');
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
        b.id.includes(q)
      );
    }

    container.innerHTML = filtered.slice(0, 100).map(b => `
      <div class="entity-card boss-card" onclick="window.inspectBoss('${b.id}')">
        <!-- Boss Official Artwork Banner -->
        <div class="boss-banner-frame">
          <img src="${b.portrait_img}" alt="${b.name}" class="boss-portrait-banner" onerror="this.src='assets/splash.png'">
          <div class="boss-banner-overlay"></div>
          <span class="entity-badge ${b.grade_code === '3' ? 'badge-crimson' : 'badge-gold'} boss-grade-tag">
            ${b.grade_name}
          </span>
          <span class="entity-badge badge-blue boss-level-tag">Nv. ${b.level}</span>
        </div>

        <div style="padding: 16px 20px 20px;">
          <div class="entity-title" style="margin-top: 4px;">${b.name}</div>
          <div style="font-size: 0.82rem; color: var(--gold-primary); margin-bottom: 8px;">
            ${b.title}
          </div>
          <p class="entity-desc">
            <strong>Aviso:</strong> ${b.audio_alert}<br>
            <strong>Recompensas:</strong> ${b.reward_preview}
          </p>
          <div class="entity-meta-row">
            <span>Escala: ${b.scale_factor}x</span>
            <span>Velocidade: ${b.run_speed}</span>
            <span style="color: var(--crimson-light); font-weight: 600;">Ver Fases →</span>
          </div>
        </div>
      </div>
    `).join('');
  }

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

  // Render Items with Official Weapon & Gear Icons
  function renderItems() {
    const container = document.getElementById('itemsContainer');
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
        i.id.includes(q)
      );
    }

    container.innerHTML = filtered.map(item => `
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
          <span>Peso: ${item.weight}</span>
          <span style="color: var(--crimson-light);">${item.max_enchant}</span>
        </div>
      </div>
    `).join('');
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
    const b = state.data.bosses.find(x => x.id === id);
    if (!b) return;

    modalTitle.innerText = b.name;
    modalSubtitle.innerText = `${b.title} • Nível ${b.level} (${b.grade_name})`;

    modalBody.innerHTML = `
      <div style="margin-bottom: 20px; text-align: center;">
        <img src="${b.portrait_img}" alt="${b.name}" style="max-height: 220px; border-radius: 8px; border: 1px solid var(--border-gold); box-shadow: 0 0 20px rgba(0,0,0,0.8);" onerror="this.src='assets/splash.png'">
      </div>
      <div style="margin-bottom: 20px;">
        <h4 style="font-family: var(--font-serif); color: var(--gold-primary); margin-bottom: 10px;">
          Mecânica de Fases de Combate (EMonsterPhase)
        </h4>
        <div style="display: flex; flex-direction: column; gap: 10px;">
          ${b.phases.map(p => `
            <div class="panel-box" style="border-left: 3px solid var(--crimson-primary);">
              <div style="font-weight: 700; color: #fff; font-size: 0.9rem;">${p.phase}</div>
              <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">${p.desc}</div>
            </div>
          `).join('')}
        </div>
      </div>
      <div class="panel-box">
        <div class="panel-title">Dados de Spawn & Dimensões</div>
        <div style="font-size: 0.85rem; color: var(--text-muted); font-family: monospace;">
          Blueprint: ${b.blueprint || 'Padrão'} | Escala: ${b.scale_factor}x | Velocidade Corrida: ${b.run_speed}
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
        renderBosses();
      } else if (state.currentTab === 'dungeons') {
        state.dungeonsSearchTerm = q;
        renderDungeons();
      } else if (state.currentTab === 'items') {
        state.itemsSearchTerm = q;
        renderItems();
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
        renderItems();
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
    renderFaq();
    setupListeners();
  }

  ensureDataLoaded();
})();
