# api.py - FastAPI backend for EDA Agent
import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# --- Load CSV ---
DF_PATH = "titanic.csv"
df = pd.read_csv(DF_PATH)

# --- Create plots directory ---
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

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

@tool
def tool_plot(input_str: str) -> str:
    """
    Generates statistical plots using seaborn/matplotlib.
    
    Input format (JSON string): {
        "plot_type": "histogram" | "bar" | "boxplot" | "scatter" | "line" | "countplot" | "violin" | "heatmap" | "pairplot",
        "x": "column_name",  # X-axis column (optional for some plots)
        "y": "column_name",  # Y-axis column (optional)
        "hue": "column_name",  # Color grouping (optional)
        "title": "Plot title"  # Optional custom title
    }
    
    Examples:
    - Histogram: {"plot_type": "histogram", "x": "age", "title": "Age Distribution"}
    - Boxplot: {"plot_type": "boxplot", "x": "pclass", "y": "fare"}
    - Scatter: {"plot_type": "scatter", "x": "age", "y": "fare", "hue": "survived"}
    - Countplot: {"plot_type": "countplot", "x": "sex", "hue": "survived"}
    - Correlation heatmap: {"plot_type": "heatmap"}
    
    Returns: Path to the generated plot image.
    """
    try:
        # Parse input JSON
        params = json.loads(input_str)
        plot_type = params.get("plot_type", "histogram").lower()
        x_col = params.get("x")
        y_col = params.get("y")
        hue_col = params.get("hue")
        title = params.get("title", "")
        
        # Validate columns exist
        for col, name in [(x_col, "x"), (y_col, "y"), (hue_col, "hue")]:
            if col and col not in df.columns:
                return json.dumps({
                    "error": f"Column '{col}' not found in dataset.",
                    "available_columns": list(df.columns)
                })
        
        # Create figure
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Generate plot based on type
        if plot_type == "histogram":
            if not x_col:
                return json.dumps({"error": "'x' column is required for histogram"})
            sns.histplot(data=df, x=x_col, hue=hue_col, kde=True)
            if not title:
                title = f"Distribution of {x_col}"
                
        elif plot_type == "bar":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for bar plot"})
            sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"{y_col} by {x_col}"
                
        elif plot_type == "boxplot":
            if not y_col:
                return json.dumps({"error": "'y' column is required for boxplot"})
            sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"Box Plot of {y_col}" + (f" by {x_col}" if x_col else "")
                
        elif plot_type == "scatter":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for scatter plot"})
            sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, alpha=0.6)
            if not title:
                title = f"{y_col} vs {x_col}"
                
        elif plot_type == "line":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for line plot"})
            sns.lineplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"{y_col} over {x_col}"
                
        elif plot_type == "countplot":
            if not x_col:
                return json.dumps({"error": "'x' column is required for countplot"})
            sns.countplot(data=df, x=x_col, hue=hue_col)
            if not title:
                title = f"Count of {x_col}"
                
        elif plot_type == "violin":
            if not y_col:
                return json.dumps({"error": "'y' column is required for violin plot"})
            sns.violinplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"Violin Plot of {y_col}" + (f" by {x_col}" if x_col else "")
                
        elif plot_type == "heatmap":
            # Select only numeric columns for correlation
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.empty:
                return json.dumps({"error": "No numeric columns found for correlation heatmap"})
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt='.2f')
            if not title:
                title = "Correlation Heatmap"
                
        elif plot_type == "pairplot":
            # For pairplot, we need to save differently
            cols_to_plot = [c for c in [x_col, y_col, hue_col] if c]
            if not cols_to_plot:
                # Use all numeric columns
                cols_to_plot = df.select_dtypes(include=['number']).columns.tolist()[:4]  # Limit to 4 for performance
            
            pairplot = sns.pairplot(df[cols_to_plot], hue=hue_col if hue_col in cols_to_plot else None)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plot_{plot_type}_{timestamp}.png"
            filepath = os.path.join(PLOTS_DIR, filename)
            pairplot.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close()
            
            return json.dumps({
                "success": True,
                "plot_path": filepath,
                "plot_url": f"/plots/{filename}",
                "message": f"Pairplot generated successfully for columns: {', '.join(cols_to_plot)}"
            })
        else:
            return json.dumps({
                "error": f"Unknown plot type: {plot_type}",
                "supported_types": ["histogram", "bar", "boxplot", "scatter", "line", "countplot", "violin", "heatmap", "pairplot"]
            })
        
        # Set title and labels
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plot_{plot_type}_{timestamp}.png"
        filepath = os.path.join(PLOTS_DIR, filename)
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        return json.dumps({
            "success": True,
            "plot_path": filepath,
            "plot_url": f"/plots/{filename}",
            "message": f"{plot_type.capitalize()} plot generated successfully!"
        })
        
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON format in input. Please provide valid JSON."})
    except Exception as e:
        return json.dumps({"error": f"Failed to generate plot: {str(e)}"})

tools = [tool_schema, tool_nulls, tool_describe, tool_plot]

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
    "write '- Age: 177 missing values'.\n\n"
    "VISUALIZATION: When users ask for charts or plots, use tool_plot. "
    "First, use tool_schema to check available columns, then generate the appropriate plot. "
    "When a plot is generated successfully, inform the user that the visualization has been created "
    "and describe what it shows. The plot URL will be available at the 'plot_url' field."
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
    plot_url: str | None = None  # URL of generated plot if any

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
        
        # Extract plot URL if present in the response
        import re
        plot_url = None
        url_match = re.search(r'plots/plot_\w+_\d+\.png', last_message.content)
        if url_match:
            plot_url = f"/plots/{url_match.group().split('/')[-1]}"
        
        return AnswerResponse(answer=last_message.content, success=True, plot_url=plot_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plots/{filename}")
def get_plot(filename: str):
    """Serve plot images"""
    filepath = os.path.join(PLOTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(filepath, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
