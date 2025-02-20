from vertexai.generative_models import FunctionDeclaration

def type_to_string(t):
    if t == str:
        return "string"
    if t == int:
        return "number"

def convert_tool_to_function_declaration(tool):
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param, param_type, param_desc in zip(tool["input_parameters"], tool["input_types"], tool["input_descriptions"]):
        param_details = {
            "type": type_to_string(param_type),
            "description": param_desc
        }
        if param_type == list:
            param_details["items"] = {
                "type": "object",
                "properties": {},
                "required": []
            }
        parameters["properties"][param] = param_details
        parameters["required"].append(param)

    function_declaration = {
        "name": tool["map"],
        "description": tool["description"].strip(),
        "parameters": parameters
    }

    return FunctionDeclaration(**function_declaration)


if __name__ == "__main__":
    from tools_details import tools
    function_declarations = [convert_tool_to_function_declaration(tool) for tool in tools]

    for fd in function_declarations:
        print(fd)