import { useState } from "react"

const sampleHistory = [
  { term: "Балка", definition: "Балка – горизонтальный или наклонный несущий элемент конструкции, воспринимающий поперечную нагрузку и передающий её на опоры." },
  { term: "Фундамент", definition: "Фундамент – подземная часть здания или сооружения, передающая нагрузку от вышележащих конструкций на основание." },
]

export function Terminologist() {
  const [query, setQuery] = useState("")
  const [result, setResult] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState(sampleHistory)

  const handleSearch = () => {
    if (!query.trim()) return
    setLoading(true)
    setTimeout(() => {
      const definition = `${query} – элемент или понятие, определение которого формируется агентом на основе поиска в открытых источниках и ГОСТах.`
      setResult(definition)
      setHistory(prev => [{ term: query, definition }, ...prev.slice(0, 4)])
      setLoading(false)
    }, 1500)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-bold">Т</div>
          <span className="font-semibold text-lg tracking-tight">Терминолог</span>
          <span className="text-xs text-slate-500 border border-slate-700 rounded px-2 py-0.5">ГОСТ-стиль</span>
        </div>
        <span className="text-xs text-slate-500">GPT-4o-mini · OpenRouter</span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-800 p-4 flex flex-col gap-2 overflow-y-auto">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">История запросов</p>
          {history.map((item, i) => (
            <button
              key={i}
              onClick={() => { setQuery(item.term); setResult(item.definition) }}
              className="text-left px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors group"
            >
              <p className="text-sm font-medium text-slate-200 group-hover:text-blue-400 transition-colors">{item.term}</p>
              <p className="text-xs text-slate-500 line-clamp-1 mt-0.5">{item.definition}</p>
            </button>
          ))}
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col p-8 gap-6">
          {/* Search */}
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="Введите термин..."
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-xl font-medium transition-colors"
            >
              {loading ? "Поиск..." : "Определить"}
            </button>
          </div>

          {/* Result */}
          {loading && (
            <div className="flex-1 flex items-center justify-center">
              <div className="flex flex-col items-center gap-4 text-slate-500">
                <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <p className="text-sm">Агент ищет определение...</p>
              </div>
            </div>
          )}

          {result && !loading && (
            <div className="flex-1 flex flex-col gap-4">
              <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xs font-medium text-blue-400 bg-blue-950 border border-blue-800 rounded px-2 py-0.5">Термин</span>
                  <h2 className="text-xl font-bold text-white">{query}</h2>
                </div>
                <p className="text-slate-300 leading-relaxed">{result}</p>
                <div className="mt-4 pt-4 border-t border-slate-800 flex items-center gap-4 text-xs text-slate-500">
                  <span>Источник: DuckDuckGo + ГОСТы</span>
                  <span>·</span>
                  <span>Модель: openai/gpt-4o-mini</span>
                </div>
              </div>
            </div>
          )}

          {!result && !loading && (
            <div className="flex-1 flex items-center justify-center text-slate-600">
              <div className="text-center">
                <p className="text-4xl mb-3">📖</p>
                <p className="text-sm">Введите термин и нажмите «Определить»</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
