import os, json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Configuration ---
MODEL = "OLLAMA"  # Options: "GPT" or "OLLAMA" (default)

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

# --- 2) Initialize LLM ---
from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="llama3.2", temperature=0.1)

# --- 3) Create ReAct Agent ---
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

# ReAct prompt template
react_template = """Answer the following question as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: After you see an Observation, you MUST either:
- Do another Action if you need more information, OR
- Provide a Final Answer if you have enough information

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

react_prompt = PromptTemplate.from_template(react_template)
agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
    early_stopping_method="generate",
)

if __name__ == "__main__":
    user_query = "Which columns have missing values? List 'Column: Count'."
    result = agent_executor.invoke({"input": user_query})
    print("\n=== AGENT ANSWER ===")
    print(result["output"])