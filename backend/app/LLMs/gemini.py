from .formatter import PromptFormatter
from google import genai
from vertexai.generative_models import Tool
import json


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
        query = self.formatter.format(
            query, instruction_dict=instruction_dict, history=self.history)
        response = self.client.models.generate_content(
            model=self.model_name, contents=query
        )
        if len(response.candidates) > 0:
            response_text = response.candidates[0].content.parts[0].text
            if self.presist:
                self.history.append(
                    {"user: ": query, "model: ": response_text})
            return response_text
        else:
            return ""

    def stream_respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        # print("instruction_dict >>", instruction_dict)
        query = self.formatter.format(
            query, instruction_dict=instruction_dict, history=self.history)
        response = self.client.models.generate_content_stream(
            model=self.model_name, contents=query
        )
        for r in response:
            if len(r.candidates) > 0:
                response_text = r.candidates[0].content.parts[0].text
                if self.persist:
                    self.history.append(
                        {"user: ": query, "model: ": response_text})
                yield response_text
            else:
                yield ""


class GeminiLLMAgent():

    def __init__(self,
                 api_key: str,
                 model_name: str,
                 formatter,
                 tools: list,
                 tool_map: list,
                 persist: bool = False,
                 history: list = []):
        self.model_name = model_name
        self.formatter = formatter
        self.history = history
        self.client = genai.Client(api_key=api_key)
        self.persist = persist
        self.tools = tools
        self.tool_map = tool_map

    def call_tool(self, tool_identifier, tool_map, params):
        # try:
        # map the dictionary that contains the "map" keyword value equal to the tool identifier give me that dict
        # print("tool map >>", tool_map)
        print("tool identifier>>", tool_identifier)
        tool_object = [
            tool for tool in tool_map if tool["map"] == tool_identifier][0]
        print("tool object >>", tool_object)
        tool_return = tool_object["callable"](**params)
        tool_details = {k: v for k, v in tool_object.items() if k in ["name", "description"]}
        tool_response = {"result": tool_return, "details": tool_details}
        # except (Exception) as e:
        #     tool_response = {"error": str(e)}
        return tool_response

    def respond(self, query, **kwargs):
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]

        system_prompt = self.formatter.format(
            "", instruction_dict=instruction_dict, history=self.history)
        
        system_prompt = genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=system_prompt)]
        )

        user_prompt_content = genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=query)]
        )

        response = self.client.models.generate_content(
            model=self.model_name, contents=[
                user_prompt_content,
                # system_prompt
            ],
            config=genai.types.GenerateContentConfig(
                tools=self.tools,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )
        )
        function_content = "<# Tool Response #>\n"
        if len(response.candidates) > 0:
            function_call = response.candidates[0].content.parts[0].function_call
            function_call_content = response.candidates[0].content.parts[0]
            if function_call:
                function_call_part = response.candidates[0].content.parts[0].function_call
                function_response = self.call_tool(function_call_part.name,
                                                   self.tool_map,
                                                   function_call_part.args)
                if "result" in function_response:
                    function_content += json.dumps(function_response)
                    function_content += "\n"
                    if "image" in function_response["result"] and type(function_response["result"]) is dict:
                        function_response["result"].pop("image", None)
                    if type(function_response["result"]) is list:
                        for item in function_response["result"]:
                            if "image" in item:
                                item.pop("image", None)

                print("tool call response mod >>", function_response)

                function_content += "<# Tool Response #>\n"

                function_response_part = genai.types.Part.from_function_response(
                    name=function_call_part.name,
                    response=function_response
                )

                user_prompt_content = genai.types.Content(
                    role="user",
                    parts=[genai.types.Part.from_text(text=query)]
                )

                function_response_content = genai.types.Content(
                    role="tool", parts=[function_response_part]
                )

                final_response = self.client.models.generate_content(
                    model=self.model_name, contents=[
                        user_prompt_content,
                        function_call_content,
                        function_response_content
                    ]
                )

                print("final response >>", final_response)
                res = function_content + final_response.candidates[0].content.parts[0].text
                if self.persist:
                    self.history.append(
                        {"human: ": query, "assistant: ": res})
                return res 
            else:
                res = response.candidates[0].content.parts[0].text
                if self.persist:
                        self.history.append(
                            {"human: ": query, "assistant: ": res})
                return res
        else:
            return ""

    def stream_respond(self, query, **kwargs):
    #     instruction_dict = {}
    #     if "instruction_dict" in kwargs:
    #         instruction_dict = kwargs["instruction_dict"]
    #     query = self.formatter.format(query, instruction_dict=instruction_dict, history=self.history)
    #     response = self.client.models.generate_content_stream(
    #         model=self.model_name, contents=query,
    #         config=genai.types.GenerateContentConfig(tools=self.tools)
    #     )
    #     for r in response:
    #         if len(r.candidates) > 0:
    #             response_text = r.candidates[0].content.parts[0].text
    #             if self.persist:
    #                 self.history.append({"human: ": query, "assistant: ": response_text})
    #             yield response_text
    #         else:
    #             yield ""
        instruction_dict = {}
        if "instruction_dict" in kwargs:
            instruction_dict = kwargs["instruction_dict"]
        system_prompt = self.formatter.format(
            "", instruction_dict=instruction_dict, history=self.history)
        
        system_prompt = genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=system_prompt)]
        )
        
        user_prompt_content = genai.types.Content(
            role="user",
            parts=[genai.types.Part.from_text(text=query)]
        )

        response = self.client.models.generate_content(
            model=self.model_name, contents=[
                # system_prompt,
                user_prompt_content
            ],
            config=genai.types.GenerateContentConfig(
                tools=self.tools,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            )
        )

        function_content = "<# Tool Response #>\n"
        if len(response.candidates) > 0:
            function_call = response.candidates[0].content.parts[0].function_call
            function_call_content = response.candidates[0].content.parts[0]
            if function_call:
                function_call_part = response.candidates[0].content.parts[0].function_call
                function_response = self.call_tool(function_call_part.name,
                                                   self.tool_map,
                                                   function_call_part.args)
                # if function_response:
                #     function_content += json.dumps(function_response)
                #     function_content += "\n"
                #     if "image" in function_response and type(function_response) is dict:
                #         function_response.pop("image", None)

                if "result" in function_response:
                    function_content += json.dumps(function_response)
                    function_content += "\n"
                    if "image" in function_response["result"] and type(function_response["result"]) is dict:
                        function_response["result"].pop("image", None)
                    if type(function_response["result"]) is list:
                        for item in function_response["result"]:
                            if "image" in item:
                                item.pop("image", None)

                print("function call part", function_call_part)
                print("tool call response mod >>", function_response)

                function_content += "<# Tool Response #>\n"

                yield function_content

                yield "<# Chat Response Start#>"

                if "details" in function_response:
                    function_response.pop("details", None)

                function_response_part = genai.types.Part.from_function_response(
                    name=function_call_part.name,
                    response=function_response
                )

                function_response_content = genai.types.Content(
                    role="tool", parts=[function_response_part]
                )

                final_response = self.client.models.generate_content_stream(
                    model=self.model_name, contents=[
                        user_prompt_content,
                        system_prompt,
                        function_call_content,
                        function_response_content
                    ]
                )

                for r in final_response:
                    if len(r.candidates) > 0:
                        response_text = r.candidates[0].content.parts[0].text
                        if self.persist:
                            self.history.append({"human: ": query, "assistant: ": response_text})
                        yield response_text
                    else:
                        yield ""

            else:
                yield "<# Chat Response Start#>"
                res = response.candidates[0].content.parts[0].text
                if self.persist:
                        self.history.append(
                            {"human: ": query, "assistant: ": res})
                yield res
        else:
            yield ""
        
        yield "<# Chat Response End#>"

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

    agent = GeminiLLMAgent(
        api_key=API_KEY, model_name="gemini-2.0-flash-exp", formatter=PromptFormatter(), tools=[])
