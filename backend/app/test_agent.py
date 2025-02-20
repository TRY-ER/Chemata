from LLMs.gemini import GeminiLLMAgent
from utils.tools_details import tools
from utils.gemini_tools_converters import convert_tool_to_function_declaration
from LLMs.formatter import PromptFormatter

if __name__ == "__main__":
    function_declarations = [convert_tool_to_function_declaration(tool) for tool in tools]
    agent = GeminiLLMAgent(api_key="GOOGLE_CLOUD_PROJECT_API_KEY",
                           model_name="gemini-2.0-flash-exp",
                           formatter=PromptFormatter(),
                           tools=function_declarations,
                           persist=False)
    response = agent.respond("What is the boiling point of water?")
    print('agent response >>', response)
    # agent.stream_respond("What is the boiling point of water?")