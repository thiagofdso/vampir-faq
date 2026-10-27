# 🩸 VAMPIR: ProjectRED — Codex & Guia Oficial (FAQ)

> Enciclopédia interativa, base de dados e guia completo para o MMORPG **VAMPIR** (ProjectRED).

🌐 **Acesse online via GitHub Pages:** [https://thiagofdso.github.io/vampir-faq/](https://thiagofdso.github.io/vampir-faq/)

---

## 📌 Visão Geral

Este projeto é uma aplicação web estática, leve e responsiva contendo dados extraídos e estruturados dos arquivos oficiais do jogo, oferecendo:

- **Visão Geral & Sistemas:** Mecânicas de combate, fórmulas de dano, status e progressão.
- **Classes:** Detalhamento completo das classes (Víbora, Ceifador, Carnificina, Manchado de Sangue, Akasha) com atributos base, radares de performance e builds recomendadas.
- **Builds PvE:** Guias de distribuição de atributos, prioridades de habilidades e cartas de sinergia.
- **Habilidades (Skills):** Consulta a mais de 1.300 habilidades com tempos de recarga, custos, alvos e efeitos detalhados.
- **Inimigos & Chefes:** Base de dados com mais de 550 chefes e monstros, incluindo níveis, raças e status de combate.
- **Masmorras:** Informações sobre masmorras, requisitos de entrada e recompensas.
- **Itens & Forja:** Catálogo de equipamentos, materiais de forja e consumíveis.
- **Perguntas Frequentes (FAQ):** Dúvidas comuns e elucidação de mecânicas obscuras do jogo.

---

## 🚀 Como Executar Localmente

Não é necessário nenhum build complexo. Basta servir os arquivos estáticos com qualquer servidor web:

```bash
# Usando Python:
python3 -m http.server 8080

# Ou usando Node (npx serve):
npx serve .
```

Abra seu navegador em `http://localhost:8080`.

---

## 🛠️ Estrutura do Repositório

```
vampir-faq/
├── assets/          # Ícones, logotipo e imagens do jogo
├── data/            # Bases de dados em JSON e bundle unificado
│   ├── bundle.js    # Dados embutidos para execução sem problemas de CORS
│   ├── classes.json
│   ├── builds.json
│   ├── skills.json
│   ├── bosses.json
│   ├── dungeons.json
│   ├── items.json
│   ├── faq.json
│   └── constants.json
├── scripts/         # Scripts de extração e processamento de dados (Python)
├── index.html       # Estrutura principal da página (Single Page Application)
├── styles.css       # Tema visual gótico estilizado (Vampir Dark)
└── app.js           # Lógica de navegação, filtragem, busca e renderização
```

---

## 📜 Licença

Distribuído sob a licença MIT. Consulte o arquivo de licença para mais detalhes.
