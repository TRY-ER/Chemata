from LLMs.gemini import GeminiLLMAgent
from utils.gemini_tools_converters import convert_tool_to_function_declaration
from LLMs.formatter import PromptFormatter
from utils.tool_repository import master_tools
from utils.tools_details import tool_mapper
from LLMs.instruction import instructions

if __name__ == "__main__":
    # read .env to get the api key
    API_KEY = None
    with open("../.env") as f:
        lines = f.readlines()
        for l in lines:
            vals = l.strip().split("=")
            if len(vals) == 2:
                if vals[0] == "GOOGLE_CLOUD_PROJECT_API_KEY":
                    API_KEY = vals[1]
                    break
    
    agent = GeminiLLMAgent(api_key=API_KEY,
                           model_name="gemini-2.0-flash-exp",
                           formatter=PromptFormatter(),
                           tools=master_tools,
                           tool_map = tool_mapper,
                           persist = False)
    response = agent.stream_respond(
        "get me some details for 1MO8",
        instruction_dict = instructions
        )
    # response = agent.stream_respond("What is the color of sky ?")
    for r in response:
        print("res >>", r)
    # agent.stream_respond("What is the boiling point of water?")