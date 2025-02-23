from openai import OpenAI
import json

class OpenAILLMAgent:
    def __init__(self,
                 api_key: str,
                 model_name: str,
                 formatter,
                 tools: list,
                 tool_map: list,
                 persist: bool = False,
                 history: list = None):
        if history is None:
            history = []
        self.model_name = model_name
        self.formatter = formatter
        self.tools = tools           # List of function definitions as per OpenAI function calling spec
        self.tool_map = tool_map     # List mapping tool identifiers to actual callables
        self.history = history
        self.persist = persist
        self.client = OpenAI(api_key)

    def call_tool(self, tool_identifier, params):
        print("Tool identifier:", tool_identifier)
        # Find the tool with a "map" value matching the identifier
        tool_object = [tool for tool in self.tool_map if tool["map"] == tool_identifier][0]
        print("Tool object:", tool_object)
        tool_return = tool_object["callable"](**params)
        tool_details = {k: v for k, v in tool_object.items() if k in ["name", "description"]}
        tool_response = {"result": tool_return, "details": tool_details}
        return tool_response

    def respond(self, query, **kwargs):
        instruction_dict = kwargs.get("instruction_dict", {})
        system_text = self.formatter.format("", instruction_dict=instruction_dict, history=self.history)
        
        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": query})

        # Pass the tools to enable function calling
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            functions=self.tools,
            function_call="auto"  # Let the model decide if a function should be called
        )

        message = response.choices[0].message

        # If model makes a function call, then call the corresponding tool
        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])
            function_response = self.call_tool(function_name, arguments)
            
            # Append the function call and its result to the conversation history
            messages.append(message)
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_response)
            })
            
            final_response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages
            )
            final_message = final_response.choices[0].message.get("content", "")
        else:
            final_message = message.get("content", "")

        if self.persist:
            self.history.append({"user": query, "assistant": final_message})
        return final_message

    def stream_respond(self, query, **kwargs):
        """
        Streams the response text. If a function call is triggered, the tool will be called and the final
        response (from a follow-up non-streamed call) will be yielded.
        """
        instruction_dict = kwargs.get("instruction_dict", {})
        system_text = self.formatter.format("", instruction_dict=instruction_dict, history=self.history)
        
        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": query})
        
        # Start the streaming ChatCompletion call with function calling enabled.
        stream = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            functions=self.tools,
            function_call="auto",
            stream=True
        )
        
        is_function_call = False
        collected_function_call = {"name": "", "arguments": ""}
        final_text = ""
        
        for event in stream:
            delta = event.choices[0].delta
            # Capture function_call parts if present
            if "function_call" in delta:
                is_function_call = True
                fc = delta["function_call"]
                if "name" in fc:
                    collected_function_call["name"] = fc["name"]
                if "arguments" in fc:
                    collected_function_call["arguments"] += fc["arguments"]
            # Stream text content if available and not part of a function call.
            if "content" in delta:
                # If a function call was initiated, ignore intermediate content.
                if not is_function_call:
                    chunk = delta["content"]
                    final_text += chunk
                    yield chunk
        
        # If a function call was triggered, call the tool and get the final answer
        if is_function_call:
            try:
                args = json.loads(collected_function_call["arguments"])
            except json.JSONDecodeError:
                args = {}
            function_response = self.call_tool(collected_function_call["name"], args)
            messages.append({
                "role": "function",
                "name": collected_function_call["name"],
                "content": json.dumps(function_response)
            })
            # Get the final text response (non-streamed) from the model
            final_response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages
            )
            final_message = final_response.choices[0].message.get("content", "")
            yield final_message
            final_text += final_message

        if self.persist:
            self.history.append({"user": query, "assistant": final_text})