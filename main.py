# main.py
import os, json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --- 0) Loading CSV ---
DF_PATH = "titanic.csv"
df = pd.read_csv(DF_PATH)

# --- 1) Defining tools as small, concise commands ---
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
        # Check if it's a number (first N columns)
        if input_str.isdigit():
            n = int(input_str)
            cols = list(df.columns[:n])
            schema = {col: schema[col] for col in cols}
        else:
            # Assume comma-separated column names
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

# --- 2) Registering tools for LangChain ---
tools = [tool_schema, tool_nulls, tool_describe]

# --- 3) Configure LLM (Gemini) ---
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- 4) Narrow Policy/Prompt (Agent Behavior) ---
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = (
    "You are a data-focused assistant that helps users analyze CSV data. "
    "When a question requires information from the CSV, use the appropriate tool. "
    "Use only one tool call per step if possible. "
    "IMPORTANT: After receiving a tool result, interpret it and provide a clear, "
    "human-readable answer. Do NOT show code or function calls in your response. "
    "Format your answers in a structured and easy-to-read way.\n\n"
    "Available tools:\n{tools}\n"
    "Use only these tools: {tool_names}."
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

_tool_desc = "\n".join(f"- {t.name}: {t.description}" for t in tools)
_tool_names = ", ".join(t.name for t in tools)
prompt = prompt.partial(tools=_tool_desc, tool_names=_tool_names)

# --- 5) Create & Run Tool-Calling Agent ---
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

if __name__ == "__main__":
    user_query = "Give me a statistical summary of the ‘age’ column."
    try:
        result = agent_executor.invoke({"messages": [("human", user_query)]})
        print("\n=== AGENT ANSWER ===")
        # Get the last message from the result
        last_message = result["messages"][-1]
        print(last_message.content)
    except Exception as e:
        print(f"\n=== ERROR: {e} ===")
        print("\nIf you see a quota error, wait a few seconds and try again.")
