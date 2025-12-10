import os, json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --- Load dataframe ---
df = pd.read_csv("titanic.csv")

# --- Tools ---
from langchain_core.tools import tool

@tool
def tool_schema(dummy: str = "") -> str:
    """Returns column names and data types as JSON."""
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return json.dumps(schema)

@tool
def tool_nulls(dummy: str = "") -> str:
    """Returns columns with the number of missing values as JSON (only columns with >0 missing values)."""
    nulls = df.isna().sum()
    result = {col: int(n) for col, n in nulls.items() if n > 0}
    return json.dumps(result)

@tool
def tool_describe(input_str: str = "") -> str:
    """Returns describe() statistics. Optional: input_str can contain a comma-separated list of columns."""
    cols = None
    if input_str and input_str.strip():
        cols = [c.strip() for c in input_str.split(",") if c.strip() in df.columns]
    stats = df[cols].describe() if cols else df.describe()
    return stats.to_csv(index=True)

tools = [tool_schema, tool_nulls, tool_describe]

# --- LLM (Ollama) ---
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2", temperature=0)

# --- ReAct agent configuration ---
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

react_template = """You are a data analysis assistant. Use the provided tools to answer questions about the CSV dataset.\n\nAvailable tools:\n{tools}\n\nIMPORTANT: Always follow this format strictly:\nQuestion: the input question you must answer\nThought: your reasoning about what you need to do\nAction: the action to take, which must be one of the tools [{tool_names}]\nAction Input: the JSON input for the action\nObservation: the result of the action\nThought: I now know the final answer\nFinal Answer: <your final answer>\n\nCritical rules:\n- Use at most one tool call per question unless explicitly told otherwise.\n- For tools with no arguments, pass an empty string "" as Action Input.\n- After you receive the Observation from tool_nulls, do not call any additional tools. Immediately provide the Final Answer.\n- Format the final answer so every column with missing values appears on its own line as `Column: Count`.\n- The final output MUST start with exactly "Final Answer: " followed by the formatted lines.\n\nBegin!\n\nQuestion: {input}\nThought:{agent_scratchpad}"""

_tool_desc = "\n".join(f"- {t.name}: {t.description}" for t in tools)
_tool_names = ", ".join(t.name for t in tools)
react_prompt = PromptTemplate.from_template(react_template).partial(
    tools=_tool_desc,
    tool_names=_tool_names,
)

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=4,
    handle_parsing_errors=True,
)

if __name__ == "__main__":
    user_query = "Which columns have missing values? List 'Column: Count'."
    
    try:
        result = agent_executor.invoke({"input": user_query})
        print("\n=== AGENT ANSWER ===")
        print(result.get("output", "No output"))
    except Exception as e:
        print(f"\n=== ERROR: {e} ===")
        print("\n=== Using direct approach ===")
        # Fallback directo
        nulls_data = json.loads(tool_nulls.invoke(""))
        print("\nColumns with missing values:")
        for col, count in nulls_data.items():
            print(f"{col}: {count}")
