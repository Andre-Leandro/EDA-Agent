"""
Agent configuration for EDA Agent.
Sets up the LLM and creates the agent with tools.
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools import ALL_TOOLS

load_dotenv()

# System prompt for the agent
SYSTEM_PROMPT = (
    "You are a data-focused assistant that helps users analyze CSV data. "
    "When a question requires information from the CSV, use the appropriate tool. "
    "Use only one tool call per step if possible. "
    "IMPORTANT: After receiving a tool result, interpret it and provide a clear, "
    "human-readable answer. Do NOT show raw JSON or code blocks in your response. "
    "Format lists as bullet points. For example, instead of showing {'Age': 177}, "
    "write '- Age: 177 missing values'.\n\n"
    "VISUALIZATION: When users ask for charts or plots, use tool_plot. "
    "First, use tool_schema to check available columns, then generate the appropriate plot. "
    "When a plot is generated successfully, inform the user that the visualization has been created "
    "and describe what it shows. "
    "NEVER mention file paths, directories, or technical implementation details like where files are saved. "
    "Just describe the visualization naturally."
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Create agent with tools
agent_executor = create_agent(model=llm, tools=ALL_TOOLS, system_prompt=SYSTEM_PROMPT)
