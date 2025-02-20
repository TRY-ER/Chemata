from .formatter import PromptFormatter
from google import genai
from vertexai.generative_models import Tool

class GeminiLLM():

    def __init__(self,
                 api_key: str,
                 model_name: str,
                 formatter,
                 persist: bool = True,
                 history: list = []):
        self.model_name = model_name
        self.formatter = formatter
        self.history = history
        self.client = genai.Client(api_key=api_key)
        self.persist = persist

    def respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        query = self.formatter.format(query, instruction_dict=instruction_dict, history=self.history)
        response = self.client.models.generate_content(
            model=self.model_name, contents=query
        )
        if len(response.candidates) > 0:
            response_text = response.candidates[0].content.parts[0].text
            if self.presist:
                self.history.append({"human: ": query, "assistant: ": response_text})
            return response_text 
        else:
            return ""

    def stream_respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        # print("instruction_dict >>", instruction_dict)
        query = self.formatter.format(query, instruction_dict=instruction_dict, history=self.history)
        print("query >>", query)
        response = self.client.models.generate_content_stream(
            model=self.model_name, contents=query
        )
        for r in response:
            if len(r.candidates) > 0:
                response_text = r.candidates[0].content.parts[0].text
                if self.persist:
                    self.history.append({"human: ": query, "assistant: ": response_text})
                yield response_text 
            else:
                yield ""

class GeminiLLMAgent():

    def __init__(self,
                 api_key: str,
                 model_name: str,
                 formatter,
                 tools: list,
                 persist: bool = True,
                 history: list = []):
        self.model_name = model_name
        self.formatter = formatter
        self.history = history
        self.client = genai.Client(api_key=api_key)
        self.persist = persist
        self.tools = Tool(function_declarations=tools)

    def respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        query = self.formatter.format(query, instruction_dict=instruction_dict, history=self.history)
        response = self.client.models.generate_content(
            model=self.model_name, contents=query,
            tools = [self.tools]
        )
        if len(response.candidates) > 0:
            response_text = response.candidates[0].content.parts[0].text
            if self.presist:
                self.history.append({"human: ": query, "assistant: ": response_text})
            return response_text 
        else:
            return ""

    def stream_respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        # print("instruction_dict >>", instruction_dict)
        query = self.formatter.format(query, instruction_dict=instruction_dict, history=self.history)
        print("query >>", query)
        response = self.client.models.generate_content_stream(
            model=self.model_name, contents=query,
            tools = [self.tools]
        )
        for r in response:
            if len(r.candidates) > 0:
                response_text = r.candidates[0].content.parts[0].text
                if self.persist:
                    self.history.append({"human: ": query, "assistant: ": response_text})
                yield response_text 
            else:
                yield ""




if __name__ == "__main__":
    API_KEY = None

    # read .env to get the api key
    with open("../../.env") as f:
        lines = f.readlines()
        for l in lines:
            vals = l.strip().split("=")
            if len(vals) == 2:
                if vals[0] == "GOOGLE_CLOUD_PROJECT_API_KEY":
                    API_KEY = vals[1]
                    break
    
    # assert API_KEY is not None, "API_KEY not found in .env file"
    # llm = GeminiLLM(api_key=API_KEY, model_name="gemini-2.0-flash-exp", formatter=PromptFormatter())
    # text_responses = llm.stream_respond("write me a small poem !")
    # for t in text_responses:
    #     print(t)

    agent = GeminiLLMAgent(api_key=API_KEY, model_name="gemini-2.0-flash-exp", formatter=PromptFormatter(), tools=[])