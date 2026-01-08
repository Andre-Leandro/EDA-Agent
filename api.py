# api.py - FastAPI backend for EDA Agent
import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# --- Load CSV ---
DF_PATH = "titanic.csv"
df = pd.read_csv(DF_PATH)

# --- Tools ---
from langchain_core.tools import tool

@tool
def tool_schema(input_str: str) -> str:
    """
    Returns column names and data types as JSON.
    Optional: input_str can contain a number N to return only the first N columns,
    or a comma-separated list of column names to filter specific columns.
    Examples: "3" returns first 3 columns, "age, fare" returns only those columns.
    If empty, returns all columns.
    """
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    if input_str and input_str.strip():
        input_str = input_str.strip()
        if input_str.isdigit():
            n = int(input_str)
            cols = list(df.columns[:n])
            schema = {col: schema[col] for col in cols}
        else:
            cols = [c.strip() for c in input_str.split(",") if c.strip() in df.columns]
            if cols:
                schema = {col: schema[col] for col in cols}
    
    return json.dumps(schema)

@tool
def tool_nulls(dummy: str) -> str:
    """Returns columns with the number of missing values as JSON (only columns with >0 missing values)."""
    nulls = df.isna().sum()
    result = {col: int(n) for col, n in nulls.items() if n > 0}
    return json.dumps(result)

@tool
def tool_describe(input_str: str) -> str:
    """
    Returns describe() statistics.
    Optional: input_str can contain a comma-separated list of columns, e.g. "age, fare".
    """
    cols = None
    if input_str and input_str.strip():
        cols = [c.strip() for c in input_str.split(",") if c.strip() in df.columns]
    stats = df[cols].describe() if cols else df.describe()
    return stats.to_csv(index=True)

tools = [tool_schema, tool_nulls, tool_describe]

# --- LLM (Gemini) ---
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- Agent ---
from langchain.agents import create_agent

SYSTEM_PROMPT_TEXT = (
    "You are a data-focused assistant that helps users analyze CSV data. "
    "When a question requires information from the CSV, use the appropriate tool. "
    "Use only one tool call per step if possible. "
    "IMPORTANT: After receiving a tool result, interpret it and provide a clear, "
    "human-readable answer. Do NOT show raw JSON or code blocks in your response. "
    "Format lists as bullet points. For example, instead of showing {'Age': 177}, "
    "write '- Age: 177 missing values'."
)

agent_executor = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT_TEXT)

# --- FastAPI App ---
app = FastAPI(title="EDA Agent API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    success: bool

@app.get("/")
def root():
    return {"message": "EDA Agent API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        result = agent_executor.invoke({"messages": [("human", request.question)]})
        last_message = result["messages"][-1]
        return AnswerResponse(answer=last_message.content, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
