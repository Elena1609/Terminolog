import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from smolagents import DuckDuckGoSearchTool, ToolCallingAgent, VisitWebpageTool, OpenAIServerModel, PromptTemplates

model = OpenAIServerModel(
    model_id="openai/gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_base=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
)

tools = [
    DuckDuckGoSearchTool(max_results=5),
    VisitWebpageTool()
]

prompt_templates = PromptTemplates(system_prompt="""
Ты иcполняешь роль терминолога.
Ты должен предлагать определения терминов в соответствии со стилем ГОСТов.
У тебя есть инструмент DuckDuckGoSearchTool, который позволяет искать информацию в интернете. Используй его, если тебе нужно быстро найти свежую или общую информацию по теме.
У тебя есть инструмент VisitWebpageTool, который позволяет прочитать содержимое веб-страницы. Используй его, если в результате поиска ты получил ссылку и хочешь узнать, что на ней написано.
Когда находишь ответ, вызывай инструмент final_answer, и пиши его в ответе.
""")

agent = ToolCallingAgent(
    tools=tools,
    model=model,
    prompt_templates=prompt_templates,
    max_steps=6
)

app = Flask(__name__)
CORS(app)

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Терминолог</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #0a0f1e; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; display: flex; flex-direction: column; height: 100vh; }
  header { border-bottom: 1px solid #1e293b; padding: 14px 28px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
  .logo { display: flex; align-items: center; gap: 10px; }
  .logo-icon { width: 32px; height: 32px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
  .logo-name { font-size: 17px; font-weight: 600; letter-spacing: -0.3px; }
  .logo-badge { font-size: 11px; color: #64748b; border: 1px solid #1e293b; border-radius: 4px; padding: 2px 7px; }
  .meta { font-size: 12px; color: #475569; }
  .layout { display: flex; flex: 1; overflow: hidden; }
  aside { width: 260px; border-right: 1px solid #1e293b; padding: 16px; overflow-y: auto; flex-shrink: 0; }
  .aside-title { font-size: 11px; font-weight: 500; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; }
  .history-item { padding: 10px 12px; border-radius: 8px; cursor: pointer; transition: background 0.15s; margin-bottom: 4px; }
  .history-item:hover { background: #1e293b; }
  .history-term { font-size: 13px; font-weight: 500; color: #cbd5e1; }
  .history-item:hover .history-term { color: #60a5fa; }
  .history-def { font-size: 11px; color: #475569; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  main { flex: 1; padding: 28px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
  /* Tabs */
  .tabs { display: flex; gap: 4px; background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 4px; width: fit-content; }
  .tab { padding: 7px 18px; border-radius: 7px; font-size: 13px; font-weight: 500; cursor: pointer; border: none; background: transparent; color: #64748b; transition: all 0.15s; }
  .tab.active { background: #2563eb; color: #fff; }
  .tab:not(.active):hover { color: #94a3b8; }
  /* Single mode */
  .search-row { display: flex; gap: 10px; }
  input[type=text] { flex: 1; background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 12px 16px; color: #e2e8f0; font-size: 15px; outline: none; transition: border-color 0.2s; }
  input[type=text]::placeholder { color: #334155; }
  input[type=text]:focus { border-color: #2563eb; }
  button { background: #2563eb; color: #fff; border: none; border-radius: 12px; padding: 12px 24px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
  button:hover { background: #3b82f6; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .result-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 24px; }
  .result-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
  .result-badge { font-size: 11px; color: #60a5fa; background: #0f2b57; border: 1px solid #1d4ed8; border-radius: 4px; padding: 2px 8px; }
  .result-term { font-size: 20px; font-weight: 700; }
  .result-text { color: #94a3b8; line-height: 1.7; font-size: 15px; }
  .result-footer { margin-top: 16px; padding-top: 16px; border-top: 1px solid #1e293b; font-size: 12px; color: #334155; display: flex; gap: 12px; align-items: center; }
  .empty { flex: 1; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 10px; }
  .empty-icon { font-size: 48px; }
  .empty-text { font-size: 14px; color: #334155; }
  .spinner { width: 32px; height: 32px; border: 2px solid #1e293b; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
  .loading-text { font-size: 13px; color: #475569; }
  .error-card { background: #1a0f0f; border: 1px solid #7f1d1d; border-radius: 14px; padding: 20px; color: #fca5a5; font-size: 14px; }
  .btn-save { background: transparent; color: #60a5fa; border: 1px solid #1e3a6e; border-radius: 8px; padding: 6px 14px; font-size: 12px; cursor: pointer; transition: background 0.15s; white-space: nowrap; }
  .btn-save:hover { background: #0f2b57; }
  .btn-save-all { background: transparent; color: #94a3b8; border: 1px solid #1e293b; border-radius: 8px; padding: 7px 12px; font-size: 12px; cursor: pointer; transition: background 0.15s; width: 100%; margin-bottom: 8px; }
  .btn-save-all:hover { background: #1e293b; color: #e2e8f0; }
  /* Batch mode */
  .drop-zone { border: 2px dashed #1e293b; border-radius: 14px; padding: 36px; text-align: center; cursor: pointer; transition: border-color 0.2s, background 0.2s; }
  .drop-zone:hover, .drop-zone.drag-over { border-color: #2563eb; background: #0f1f40; }
  .drop-zone input[type=file] { display: none; }
  .drop-zone-icon { font-size: 36px; margin-bottom: 10px; }
  .drop-zone-text { font-size: 14px; color: #64748b; }
  .drop-zone-hint { font-size: 12px; color: #334155; margin-top: 6px; }
  .terms-preview { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; max-height: 180px; overflow-y: auto; }
  .terms-preview-header { font-size: 12px; color: #475569; margin-bottom: 10px; display: flex; justify-content: space-between; }
  .term-chip { display: inline-block; background: #1e293b; border-radius: 6px; padding: 4px 10px; font-size: 12px; color: #94a3b8; margin: 3px; }
  .progress-box { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 24px; display: flex; flex-direction: column; gap: 14px; }
  .progress-bar-wrap { background: #1e293b; border-radius: 6px; height: 6px; overflow: hidden; }
  .progress-bar-fill { background: #2563eb; height: 100%; border-radius: 6px; transition: width 0.3s; }
  .progress-status { font-size: 13px; color: #64748b; }
  .progress-current { font-size: 14px; color: #94a3b8; }
  .batch-results { display: flex; flex-direction: column; gap: 12px; }
  .batch-result-item { background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; }
  .batch-result-term { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
  .batch-result-def { font-size: 13px; color: #64748b; line-height: 1.6; }
  .batch-result-err { font-size: 13px; color: #f87171; }
  .badge-ok { background: #052e16; color: #4ade80; border: 1px solid #166534; border-radius: 4px; font-size: 10px; padding: 1px 6px; }
  .badge-err { background: #1a0f0f; color: #f87171; border: 1px solid #7f1d1d; border-radius: 4px; font-size: 10px; padding: 1px 6px; }
  .batch-done-bar { display: flex; align-items: center; gap: 12px; padding: 14px; background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; }
  .batch-done-text { font-size: 13px; color: #94a3b8; flex: 1; }
</style>
</head>
<body>
<header>
  <div class="logo">
    <div class="logo-icon">Т</div>
    <span class="logo-name">Терминолог</span>
    <span class="logo-badge">ГОСТ-стиль</span>
  </div>
  <span class="meta">GPT-4o-mini · OpenRouter</span>
</header>
<div class="layout">
  <aside>
    <p class="aside-title">История запросов</p>
    <div id="history"></div>
  </aside>
  <main>
    <!-- Mode tabs -->
    <div class="tabs">
      <button class="tab active" onclick="switchMode('single')">Одиночный</button>
      <button class="tab" onclick="switchMode('batch')">Пакетный</button>
    </div>

    <!-- Single mode -->
    <div id="singleMode">
      <div class="search-row" style="margin-bottom:20px">
        <input type="text" id="queryInput" placeholder="Введите термин..." />
        <button id="searchBtn" onclick="search()">Определить</button>
      </div>
      <div id="content">
        <div class="empty">
          <div class="empty-icon">📖</div>
          <p class="empty-text">Введите термин и нажмите «Определить»</p>
        </div>
      </div>
    </div>

    <!-- Batch mode -->
    <div id="batchMode" style="display:none; display:flex; flex-direction:column; gap:16px; display:none">
      <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
        <input type="file" id="fileInput" accept=".txt" onchange="onFileSelect(this)">
        <div class="drop-zone-icon">📂</div>
        <p class="drop-zone-text">Нажмите или перетащите TXT-файл</p>
        <p class="drop-zone-hint">Один термин на каждой строке</p>
      </div>
      <div id="termsPreview" style="display:none"></div>
      <div id="batchActions" style="display:none">
        <button id="processBtn" onclick="processBatch()">Обработать</button>
      </div>
      <div id="batchProgress" style="display:none"></div>
      <div id="batchResults" style="display:none"></div>
    </div>
  </main>
</div>
<script>
  const history = [];
  let batchTerms = [];
  let batchRunning = false;

  // ── Mode switch ──────────────────────────────────────────────
  function switchMode(mode) {
    document.querySelectorAll('.tab').forEach((t, i) => {
      t.classList.toggle('active', (i === 0) === (mode === 'single'));
    });
    document.getElementById('singleMode').style.display = mode === 'single' ? 'block' : 'none';
    document.getElementById('batchMode').style.display  = mode === 'batch'  ? 'flex' : 'none';
    if (mode === 'batch') document.getElementById('batchMode').style.flexDirection = 'column';
  }

  // ── Single mode ──────────────────────────────────────────────
  document.getElementById('queryInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') search();
  });

  function addHistory(term, definition) {
    const idx = history.findIndex(h => h.term === term);
    if (idx !== -1) history.splice(idx, 1);
    history.unshift({ term, definition });
    if (history.length > 20) history.pop();
    renderHistory();
  }

  function renderHistory() {
    const el = document.getElementById('history');
    const saveAllBtn = history.length > 0
      ? `<button class="btn-save-all" onclick="saveAllTxt()">💾 Сохранить все (${history.length})</button>`
      : '';
    el.innerHTML = saveAllBtn + history.map((item, i) => `
      <div class="history-item" onclick="loadHistory(${i})">
        <div class="history-term">${esc(item.term)}</div>
        <div class="history-def">${esc(item.definition)}</div>
      </div>
    `).join('');
  }

  function loadHistory(i) {
    switchMode('single');
    const item = history[i];
    document.getElementById('queryInput').value = item.term;
    showResult(item.term, item.definition);
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function showLoading() {
    document.getElementById('content').innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
        <p class="loading-text">Агент ищет определение...</p>
      </div>`;
  }

  function showResult(term, definition) {
    window._lastTerm = term;
    window._lastDef = definition;
    document.getElementById('content').innerHTML = `
      <div class="result-card">
        <div class="result-header">
          <span class="result-badge">Термин</span>
          <h2 class="result-term">${esc(term)}</h2>
        </div>
        <p class="result-text">${esc(definition)}</p>
        <div class="result-footer">
          <span>Источник: DuckDuckGo + ГОСТы</span>
          <span>·</span>
          <span>openai/gpt-4o-mini</span>
          <button class="btn-save" onclick="saveTxt(window._lastTerm, window._lastDef)">💾 Сохранить в TXT</button>
        </div>
      </div>`;
  }

  function showError(msg) {
    document.getElementById('content').innerHTML = `
      <div class="error-card">Ошибка: ${esc(msg)}</div>`;
  }

  async function search() {
    const input = document.getElementById('queryInput');
    const btn   = document.getElementById('searchBtn');
    const query = input.value.trim();
    if (!query) return;
    btn.disabled = true; btn.textContent = 'Поиск...';
    showLoading();
    try {
      const res  = await fetch('/api/define', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ query }) });
      const data = await res.json();
      if (data.error) { showError(data.error); }
      else { showResult(query, data.result); addHistory(query, data.result); }
    } catch(e) { showError(e.message); }
    finally { btn.disabled = false; btn.textContent = 'Определить'; }
  }

  // ── Batch mode ───────────────────────────────────────────────
  const dropZone = document.getElementById('dropZone');
  dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault(); dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) readFile(file);
  });

  function onFileSelect(input) {
    if (input.files[0]) readFile(input.files[0]);
  }

  function readFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
      const terms = e.target.result.split(/\\r?\\n/).map(l => l.trim()).filter(l => l.length > 0);
      batchTerms = [...new Set(terms)];
      showTermsPreview();
    };
    reader.readAsText(file, 'utf-8');
  }

  function showTermsPreview() {
    const preview = document.getElementById('termsPreview');
    const actions = document.getElementById('batchActions');
    const btn     = document.getElementById('processBtn');
    preview.style.display = 'block';
    actions.style.display = 'block';
    document.getElementById('batchProgress').style.display = 'none';
    document.getElementById('batchResults').style.display  = 'none';
    preview.innerHTML = `
      <div class="terms-preview">
        <div class="terms-preview-header">
          <span>Найдено терминов: <b>${batchTerms.length}</b></span>
          <span style="color:#334155">из файла</span>
        </div>
        <div>${batchTerms.map(t => `<span class="term-chip">${esc(t)}</span>`).join('')}</div>
      </div>`;
    btn.textContent = `Обработать ${batchTerms.length} ${plural(batchTerms.length, 'термин','термина','терминов')}`;
    btn.disabled = false;
  }

  function plural(n, a, b, c) {
    const m = n % 100;
    if (m >= 11 && m <= 19) return c;
    const k = n % 10;
    if (k === 1) return a;
    if (k >= 2 && k <= 4) return b;
    return c;
  }

  async function processBatch() {
    if (batchRunning || !batchTerms.length) return;
    batchRunning = true;
    document.getElementById('processBtn').disabled = true;
    const total = batchTerms.length;
    const results = [];
    const progress = document.getElementById('batchProgress');
    const resultsEl = document.getElementById('batchResults');
    progress.style.display = 'block';
    resultsEl.style.display = 'none';

    for (let i = 0; i < total; i++) {
      const term = batchTerms[i];
      progress.innerHTML = `
        <div class="progress-box">
          <div class="progress-status">Обработка ${i + 1} из ${total}</div>
          <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:${Math.round(i/total*100)}%"></div></div>
          <div class="progress-current">⏳ ${esc(term)}</div>
        </div>`;
      try {
        const res  = await fetch('/api/define', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ query: term }) });
        const data = await res.json();
        if (data.error) { results.push({ term, error: data.error }); }
        else { results.push({ term, definition: data.result }); addHistory(term, data.result); }
      } catch(e) { results.push({ term, error: e.message }); }
    }

    // Done
    batchRunning = false;
    const ok  = results.filter(r => r.definition).length;
    const err = results.length - ok;
    progress.innerHTML = `
      <div class="progress-box">
        <div class="progress-status">Готово: ${ok} успешно${err ? ', ' + err + ' с ошибкой' : ''}</div>
        <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:100%"></div></div>
      </div>`;

    resultsEl.style.display = 'block';
    resultsEl.innerHTML = `
      <div class="batch-done-bar">
        <span class="batch-done-text">Обработано <b>${total}</b> ${plural(total,'термин','термина','терминов')}: ${ok} ✓${err ? ', ' + err + ' ✗' : ''}</span>
        <button class="btn-save" onclick="saveBatchTxt()" style="margin-left:auto">💾 Скачать все результаты</button>
      </div>
      <div class="batch-results">
        ${results.map(r => r.definition
          ? `<div class="batch-result-item">
               <div class="batch-result-term"><span class="badge-ok">✓</span>${esc(r.term)}</div>
               <div class="batch-result-def">${esc(r.definition)}</div>
             </div>`
          : `<div class="batch-result-item">
               <div class="batch-result-term"><span class="badge-err">✗</span>${esc(r.term)}</div>
               <div class="batch-result-err">${esc(r.error)}</div>
             </div>`
        ).join('')}
      </div>`;

    window._batchResults = results;
  }

  function saveBatchTxt() {
    const results = window._batchResults || [];
    const date = new Date().toLocaleDateString('ru-RU');
    const parts = [
      'Терминолог — пакетная обработка',
      '='.repeat(42),
      'Дата: ' + date,
      'Всего терминов: ' + results.length,
      ''
    ];
    results.forEach(r => {
      parts.push('');
      parts.push('Термин: ' + r.term);
      parts.push('-'.repeat(30));
      parts.push(r.definition || ('Ошибка: ' + r.error));
    });
    parts.push('');
    parts.push('='.repeat(42));
    parts.push('Источник: DuckDuckGo + ГОСТы  |  Модель: openai/gpt-4o-mini');
    download(parts.join('\\n'), 'терминолог_пакет_' + date.replace(/\\./g,'-') + '.txt');
  }

  // ── Shared helpers ───────────────────────────────────────────
  function saveTxt(term, definition) {
    const date = new Date().toLocaleDateString('ru-RU');
    const text = [
      'Терминолог — определение в стиле ГОСТ',
      '='.repeat(42), '',
      'Термин: ' + term,
      'Дата:   ' + date, '',
      definition, '',
      '='.repeat(42),
      'Источник: DuckDuckGo + ГОСТы  |  Модель: openai/gpt-4o-mini'
    ].join('\\n');
    download(text, term + '.txt');
  }

  function saveAllTxt() {
    if (!history.length) return;
    const date = new Date().toLocaleDateString('ru-RU');
    const parts = ['Терминолог — все определения', '='.repeat(42), 'Дата: ' + date, ''];
    history.forEach(item => {
      parts.push(''); parts.push('Термин: ' + item.term);
      parts.push('-'.repeat(30)); parts.push(item.definition);
    });
    parts.push(''); parts.push('='.repeat(42));
    parts.push('Источник: DuckDuckGo + ГОСТы  |  Модель: openai/gpt-4o-mini');
    download(parts.join('\\n'), 'терминолог_' + date.replace(/\\./g,'-') + '.txt');
  }

  function download(text, filename) {
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  }
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/define', methods=['POST'])
def define():
    data = request.get_json()
    query = (data or {}).get('query', '').strip()
    if not query:
        return jsonify({'error': 'Не указан термин'}), 400
    try:
        output = agent.run(query)
        return jsonify({'result': str(output)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
