from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4
from app.LLMs.formatter import PromptFormatter
from app.LLMs.gemini import GeminiLLMAgent 
from get_env_vars import GOOGLE_CLOUD_PROJECT_API_KEY
from app.LLMs.instruction import instructions
import json
from app.utils.tool_repository import master_tools
from app.utils.tools_details import tool_mapper


router = APIRouter()

# Simple in-memory store of user queries
queries = {}

class Query(BaseModel):
    id: str 
    query: str
    config: Dict[str, Any]

# handing generation of events
def event_generator(query: str, config: Dict[str, Any]):
    model_name = "gemini-2.0-flash-exp"
    if "model_name" in config:
        model_name = config["model_name"]
    agent = GeminiLLMAgent(api_key=GOOGLE_CLOUD_PROJECT_API_KEY,
                           model_name=model_name,
                           formatter=PromptFormatter(),
                           tools=master_tools,
                           tool_map = tool_mapper,
                           persist = False)
    text_responses = agent.stream_respond(query, instruction_dict=instructions)
    for t in text_responses:
        # t = postproces_response_for_stream(t)
        print("data >>", json.dumps(t))
        yield f"data: {json.dumps(t)}\n\n"
    yield f"data: <|end|>\n\n"

@router.post("/init")
def store_query(payload: Query):
    """
    A POST endpoint to save the query in memory.
    """
    id = payload.id 
    queries[str(id)] = payload
    return {"status": "success", "id": id}


@router.get("/stream/{id}")
def stream_responses(id: str):
    """
    Returns a streaming response with text/event-stream.
    You can update the generator logic to produce actual AI responses in real time.
    """
    if id not in queries:
        return {"status": "error", "message": "Query not found"}
    Q = queries.get(id)
    del queries[id]
    return StreamingResponse(event_generator(Q.query, Q.config), media_type="text/event-stream")

# router = APIRouter()

# # Simple in-memory store of user queries
# queries = {}

# class Query(BaseModel):
#     query: str
#     config: Dict[str, Any]

# # handing generation of events
# def event_generator(query: str, config: Dict[str, Any]):
#     model_name = "gemini-2.0-flash-exp"
#     if "model_name" in config:
#         model_name = config["model_name"] 
#     llm = GeminiLLM(api_key=GOOGLE_CLOUD_PROJECT_API_KEY,
#                     model_name=model_name,
#                     formatter=PromptFormatter(),
#                     persist=False)
#     instructions["Tools"]  = format_tool_config_to_prompt(TOOL_CONFIG)
#     text_responses = llm.stream_respond(query, instruction_dict=instructions)   
#     for t in text_responses:
#         # t = postproces_response_for_stream(t)
#         print("data >>", json.dumps(t))
#         yield f"data: {json.dumps(t)}\n\n"
#     yield f"data: <|end|>\n\n"

# @router.post("/init")
# def store_query(payload: Query):
#     """
#     A POST endpoint to save the query in memory.
#     """
#     id = str(uuid4())
#     queries[str(id)] = payload 
#     return {"status": "success", "id": id}


# @router.get("/stream/{id}")
# def stream_responses(id: str):
#     """
#     Returns a streaming response with text/event-stream.
#     You can update the generator logic to produce actual AI responses in real time.
#     """
#     if id not in queries:
#         return {"status": "error", "message": "Query not found"}
#     Q = queries.get(id)
#     del queries[id]
#     return StreamingResponse(event_generator(Q.query, Q.config), media_type="text/event-stream")
