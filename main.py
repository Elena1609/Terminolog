import os
from dotenv import load_dotenv
load_dotenv()

from smolagents import DuckDuckGoSearchTool, HfApiModel, ToolCallingAgent, VisitWebpageTool, OpenAIServerModel, PromptTemplates

model = OpenAIServerModel(
    model_id="openai/gpt-4o-mini",
    api_key=os.environ.get("OPENAI_API_KEY"),
    api_base=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
)

tools = [
    DuckDuckGoSearchTool(max_results=5), # поиск в интернете через бесплатный поисковик
    VisitWebpageTool() # чтение текста с веб-страницы
]

prompt_templates = PromptTemplates(system_prompt="""
Ты иcполняешь роль терминолога.
Ты должен предлагать определения терминов в соответствии со стилем ГОСТов.
У тебя есть инструмент DuckDuckGoSearchTool,  который позволяет искать информацию в интернете. Используй его, если тебе нужно быстро найти свежую или общую информацию по теме.
У тебя есть инструмент VisitWebpageTool, который позволяет прочитать содержимое веб-страницы. Используй его, если в результате поиска ты получил ссылку и хочешь узнать, что на ней написано.
Когда находишь ответ,  вызывай инструмент final_answer, и пиши его в ответе.
""")

agent = ToolCallingAgent(
    tools=tools,
    model=model,
    prompt_templates=prompt_templates,
    max_steps=6 # ограничение от зацикливания
)

while True:
    query = input("\nВведите термин (или 'выход' для завершения): ").strip()
    if query.lower() in ("выход", "exit", "quit"):
        break
    if not query:
        continue
    output = agent.run(query)
    print("Executor result:", output)
