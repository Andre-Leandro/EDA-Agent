import os, json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- 0) Loading CSV ---
DF_PATH = "titanic.csv"
df = pd.read_csv(DF_PATH)

# --- 1) Defining tools as small, concise commands ---
# IMPORTANT: Tools return strings (in this case, JSON strings) so that the LLM sees clearly structured responses.

from langchain_core.tools import tool

@tool
def tool_schema(dummy: str) -> str:
    """Returns column names and data types as JSON."""
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
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
    # describe() has a MultiIndex. Flatten it for the LLM to keep it readable:
    return stats.to_csv(index=True)

tools = [tool_schema, tool_nulls, tool_describe]


from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = (
    "You are a data-focused assistant. "
    "If a question requires information from the CSV, first use an appropriate tool. "
    "Use only one tool call per step if possible. "
    "Answer concisely and in a structured way. "
    "If no tool fits, briefly explain why.\n\n"
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
from langchain.agents import create_tool_calling_agent, AgentExecutor

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,   # optional: True for debug logs
    max_iterations=3,
)

if __name__ == "__main__":
    user_query = "Which columns have missing values? List 'Column: Count'."
    result = agent_executor.invoke({"input": user_query})
    print("\n=== AGENT ANSWER ===")
    print(result["output"])