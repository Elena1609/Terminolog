from smolagents import DuckDuckGoSearchTool, HfApiModel, ToolCallingAgent, VisitWebpageTool, OpenAIServerModel, PromptTemplates

model = OpenAIServerModel(model_id="openai/gpt-4o-mini")

tools = [
    DuckDuckGoSearchTool(max_results=5), # поиск в интернете через бесплатный поисковик
    VisitWebpageTool() # чтение текста с веб-страницы
]
