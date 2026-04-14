import os
import time
from dotenv import load_dotenv
load_dotenv()

from smolagents import DuckDuckGoSearchTool, HfApiModel, ToolCallingAgent, VisitWebpageTool, OpenAIServerModel, PromptTemplates

model = HfApiModel(model_id="Qwen/Qwen2.5-72B-Instruct")

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

query = "Балка"
output = agent.run(query)

print("Executor result:", output)
