import { useState } from "react"

const API_URL = `https://${window.location.hostname}:5000/api/define`

interface HistoryItem {
  term: string
  definition: string
}

export function Terminologist() {
  const [query, setQuery] = useState("")
  const [result, setResult] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])

  const handleSearch = async () => {
    const term = query.trim()
    if (!term || loading) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: term }),
      })
      const data = await res.json()
      if (data.error) {
        setError(data.error)
      } else {
        setResult(data.result)
        setHistory(prev => {
          const filtered = prev.filter(h => h.term !== term)
          return [{ term, definition: data.result }, ...filtered].slice(0, 10)
        })
      }
    } catch (e: any) {
      setError("Не удалось подключиться к агенту: " + e.message)
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = (item: HistoryItem) => {
    setQuery(item.term)
    setResult(item.definition)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 px-8 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-bold select-none">Т</div>
          <span className="font-semibold text-lg tracking-tight">Терминолог</span>
          <span className="text-xs text-slate-500 border border-slate-700 rounded px-2 py-0.5">ГОСТ-стиль</span>
        </div>
        <span className="text-xs text-slate-500">GPT-4o-mini · OpenRouter</span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 border-r border-slate-800 p-4 flex flex-col gap-1 overflow-y-auto shrink-0">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">История запросов</p>
          {history.length === 0 && (
            <p className="text-xs text-slate-700 px-3 py-2">Запросов ещё нет</p>
          )}
          {history.map((item, i) => (
            <button
              key={i}
              onClick={() => loadHistory(item)}
              className="text-left px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors group"
            >
              <p className="text-sm font-medium text-slate-200 group-hover:text-blue-400 transition-colors">{item.term}</p>
              <p className="text-xs text-slate-500 line-clamp-1 mt-0.5">{item.definition}</p>
            </button>
          ))}
        </aside>

        <main className="flex-1 flex flex-col p-8 gap-6 overflow-y-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="Введите термин..."
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors disabled:opacity-50"
            />
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-xl font-medium transition-colors whitespace-nowrap"
            >
              {loading ? "Поиск..." : "Определить"}
            </button>
          </div>

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-slate-500">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm">Агент ищет определение в ГОСТах...</p>
            </div>
          )}

          {error && !loading && (
            <div className="bg-red-950 border border-red-800 rounded-xl p-5 text-red-300 text-sm">
              {error}
            </div>
          )}

          {result && !loading && !error && (
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-medium text-blue-400 bg-blue-950 border border-blue-800 rounded px-2 py-0.5">Термин</span>
                <h2 className="text-xl font-bold text-white">{query}</h2>
              </div>
              <p className="text-slate-300 leading-relaxed">{result}</p>
              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center gap-4 text-xs text-slate-500">
                <span>Источник: DuckDuckGo + ГОСТы</span>
                <span>·</span>
                <span>openai/gpt-4o-mini</span>
              </div>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <p className="text-5xl mb-4 select-none">📖</p>
              <p className="text-sm text-slate-600">Введите термин и нажмите «Определить»</p>
              <p className="text-xs text-slate-700 mt-1">Агент найдёт определение по ГОСТам</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
