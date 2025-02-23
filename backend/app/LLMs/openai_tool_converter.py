import json
from app.utils.tools_details import tool_mapper

def map_python_type(py_type):
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }
    return mapping.get(py_type, "string")

def convert_tool(tool):
    properties = {}
    required = []
    
    # Each tool has input_parameters, input_types, input_descriptions & default_inputs.
    for param, ptype, desc, default in zip(tool["input_parameters"],
                                           tool["input_types"],
                                           tool["input_descriptions"],
                                           tool["default_inputs"]):
        # If the parameter signifies a list (e.g., ends with '_list'), set type to array
        if param.endswith("_list"):
            param_schema = {
                "type": "array",
                "items": {
                    "type": map_python_type(ptype)
                },
                "description": desc
            }
        else:
            param_schema = {
                "type": map_python_type(ptype),
                "description": desc
            }
        # Add default if provided; otherwise consider parameter required.
        if default is not None:
            param_schema["default"] = default
        else:
            required.append(param)
        properties[param] = param_schema
    
    parameters = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": True 
    }
    
    function_declaration = {
        "type": "function",
        "function": {
            "name": tool["map"],
            "description": tool["description"].strip(),
            "parameters": parameters,
            "strict": True
        }
    }
    return function_declaration

def convert_tools_to_openai_format(tools):
    return [convert_tool(tool) for tool in tools]

if __name__ == "__main__":
    openai_tools = convert_tools_to_openai_format(tool_mapper)
    print(json.dumps(openai_tools, indent=4))