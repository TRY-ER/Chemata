from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4
from engine.chat.llm import GeminiLLM
from engine.chat.formatter import PromptFormatter
from get_env_vars import GOOGLE_CLOUD_PROJECT_API_KEY
from engine.chat.utils import postproces_response_for_stream
from utils.chat_utils import format_tool_config_to_prompt
from app.prompts.instruction import instructions
import json

router = APIRouter()

# variable to store the tool configs

TOOL_CONFIG = [] 

# Simple in-memory store of user queries
queries = {}

class Query(BaseModel):
    query: str
    config: Dict[str, Any]

# handing generation of events
def event_generator(query: str, config: Dict[str, Any]):
    model_name = "gemini-2.0-flash-exp"
    if "model_name" in config:
        model_name = config["model_name"] 
    llm = GeminiLLM(api_key=GOOGLE_CLOUD_PROJECT_API_KEY,
                    model_name=model_name,
                    formatter=PromptFormatter(),
                    persist=False)
    instructions["Tools"]  = format_tool_config_to_prompt(TOOL_CONFIG)
    text_responses = llm.stream_respond(query, instruction_dict=instructions)   
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
    id = str(uuid4())
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

@router.post("/config")
def set_config(data: dict):
    """
    A POST endpoint to save the tool config in memory.
    """
    global TOOL_CONFIG
    TOOL_CONFIG = data["data"]
    return {"status": "success"}