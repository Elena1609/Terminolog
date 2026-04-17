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
  header { border-bottom: 1px solid #1e293b; padding: 14px 28px; display: flex; align-items: center; justify-content: space-between; }
  .logo { display: flex; align-items: center; gap: 10px; }
  .logo-icon { width: 32px; height: 32px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
  .logo-name { font-size: 17px; font-weight: 600; letter-spacing: -0.3px; }
  .logo-badge { font-size: 11px; color: #64748b; border: 1px solid #1e293b; border-radius: 4px; padding: 2px 7px; }
  .meta { font-size: 12px; color: #475569; }
  .layout { display: flex; flex: 1; overflow: hidden; }
  aside { width: 260px; border-right: 1px solid #1e293b; padding: 16px; overflow-y: auto; }
  .aside-title { font-size: 11px; font-weight: 500; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; }
  .history-item { padding: 10px 12px; border-radius: 8px; cursor: pointer; transition: background 0.15s; margin-bottom: 4px; }
  .history-item:hover { background: #1e293b; }
  .history-term { font-size: 13px; font-weight: 500; color: #cbd5e1; }
  .history-item:hover .history-term { color: #60a5fa; }
  .history-def { font-size: 11px; color: #475569; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  main { flex: 1; padding: 28px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
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
  .result-footer { margin-top: 16px; padding-top: 16px; border-top: 1px solid #1e293b; font-size: 12px; color: #334155; display: flex; gap: 12px; }
  .empty { flex: 1; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 10px; color: #1e293b; }
  .empty-icon { font-size: 48px; }
  .empty-text { font-size: 14px; color: #334155; }
  .spinner { width: 32px; height: 32px; border: 2px solid #1e293b; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
  .loading-text { font-size: 13px; color: #475569; }
  .error-card { background: #1a0f0f; border: 1px solid #7f1d1d; border-radius: 14px; padding: 20px; color: #fca5a5; font-size: 14px; }
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
    <div class="search-row">
      <input type="text" id="queryInput" placeholder="Введите термин..." />
      <button id="searchBtn" onclick="search()">Определить</button>
    </div>
    <div id="content">
      <div class="empty">
        <div class="empty-icon">📖</div>
        <p class="empty-text">Введите термин и нажмите «Определить»</p>
      </div>
    </div>
  </main>
</div>
<script>
  const history = [];

  document.getElementById('queryInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') search();
  });

  function addHistory(term, definition) {
    history.unshift({ term, definition });
    if (history.length > 10) history.pop();
    renderHistory();
  }

  function renderHistory() {
    const el = document.getElementById('history');
    el.innerHTML = history.map((item, i) => `
      <div class="history-item" onclick="loadHistory(${i})">
        <div class="history-term">${item.term}</div>
        <div class="history-def">${item.definition}</div>
      </div>
    `).join('');
  }

  function loadHistory(i) {
    const item = history[i];
    document.getElementById('queryInput').value = item.term;
    showResult(item.term, item.definition);
  }

  function showLoading() {
    document.getElementById('content').innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
        <p class="loading-text">Агент ищет определение...</p>
      </div>`;
  }

  function showResult(term, definition) {
    document.getElementById('content').innerHTML = `
      <div class="result-card">
        <div class="result-header">
          <span class="result-badge">Термин</span>
          <h2 class="result-term">${term}</h2>
        </div>
        <p class="result-text">${definition}</p>
        <div class="result-footer">
          <span>Источник: DuckDuckGo + ГОСТы</span>
          <span>·</span>
          <span>Модель: openai/gpt-4o-mini</span>
        </div>
      </div>`;
  }

  function showError(msg) {
    document.getElementById('content').innerHTML = `
      <div class="error-card">Ошибка: ${msg}</div>`;
  }

  async function search() {
    const input = document.getElementById('queryInput');
    const btn = document.getElementById('searchBtn');
    const query = input.value.trim();
    if (!query) return;

    btn.disabled = true;
    btn.textContent = 'Поиск...';
    showLoading();

    try {
      const res = await fetch('/api/define', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (data.error) {
        showError(data.error);
      } else {
        showResult(query, data.result);
        addHistory(query, data.result);
      }
    } catch (e) {
      showError(e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Определить';
    }
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
