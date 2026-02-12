"""
FastAPI backend for EDA Agent.
Handles HTTP endpoints and routes requests to the agent.
"""
import os
import json
import pandas as pd
import io
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import agent_executor
from tools.context import set_dataframe

# --- Configuration ---
# Use absolute path relative to this file
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(BACKEND_DIR, "titanic.csv")
PLOTS_DIR = os.path.join(BACKEND_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
# --- Pydantic Models ---
class AnswerResponse(BaseModel):
    answer: str
    success: bool
    plot_url: str | None = None


# --- FastAPI App ---
app = FastAPI(title="EDA Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your Vercel domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---
@app.get("/")
def root():
    """Root endpoint - health check."""
    return {"message": "EDA Agent API is running", "status": "ok"}


@app.get("/health")
def health():
    """Health check endpoint."""
    has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
    has_csv = os.path.exists(DEFAULT_CSV_PATH)
    return {
        "status": "healthy",
        "google_api_key_configured": has_api_key,
        "default_csv_exists": has_csv,
        "csv_path": DEFAULT_CSV_PATH
    }


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(
    question: str = Form(...),
    dataset_type: str = Form("default"),
    file: UploadFile = File(None)
):
    """
    Process a question about the dataset.
    
    Args:
        question: The user's question
        dataset_type: Either 'default' or 'custom'
        file: Optional CSV file for custom datasets
        
    Returns:
        AnswerResponse with the answer and optional plot URL
    """
    try:
        # Load the appropriate CSV based on the request
        if dataset_type == "custom" and file:
            # Read the uploaded CSV file
            contents = await file.read()
            
            # Try different encodings and parse CSV with better type inference
            try:
                df = pd.read_csv(
                    io.BytesIO(contents),
                    encoding='utf-8',
                    sep=None,  # Auto-detect separator (comma, semicolon, tab, etc.)
                    engine='python',  # More flexible parser
                    skipinitialspace=True,  # Remove spaces after delimiter
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None', '-', '?']  # Common null values
                )
            except UnicodeDecodeError:
                # Try with latin-1 encoding if utf-8 fails
                df = pd.read_csv(
                    io.BytesIO(contents),
                    encoding='latin-1',
                    sep=None,
                    engine='python',
                    skipinitialspace=True,
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None', '-', '?']
                )
            
            print(f"[DEBUG] Loaded custom CSV: {file.filename}, shape: {df.shape}")
            print(f"[DEBUG] Initial dtypes: {df.dtypes.to_dict()}")
            
            # Try to convert columns to numeric when possible
            for col in df.columns:
                if df[col].dtype == 'object':  # If column is string/object type
                    try:
                        # Try to convert to numeric, keeping non-numeric as NaN
                        converted = pd.to_numeric(df[col], errors='coerce')
                        # Only replace if at least 50% of values are numeric
                        if converted.notna().sum() / len(df) > 0.5:
                            df[col] = converted
                            print(f"[DEBUG] Converted column '{col}' to numeric")
                    except Exception as e:
                        print(f"[DEBUG] Could not convert '{col}' to numeric: {e}")
            
            print(f"[DEBUG] Final dtypes after conversion: {df.dtypes.to_dict()}")
            print(f"[DEBUG] Numeric columns: {df.select_dtypes(include=['number']).columns.tolist()}")
            
        else:
            # Use default Titanic dataset
            df = pd.read_csv(DEFAULT_CSV_PATH)
            print(f"[DEBUG] Loaded default CSV: {DEFAULT_CSV_PATH}, shape: {df.shape}")
        
        # Set the dataframe in the context for tools to use
        set_dataframe(df)
        
        # Process the question with the agent
        result = agent_executor.invoke({"messages": [("human", question)]})
        last_message = result["messages"][-1]
        
        # Extract plot URL from tool responses
        plot_url = None
        for msg in result["messages"]:
            if hasattr(msg, 'name') and msg.name == 'tool_plot':
                try:
                    tool_result = json.loads(msg.content)
                    if tool_result.get("success") and tool_result.get("plot_url"):
                        plot_url = tool_result["plot_url"]
                        print(f"[DEBUG] Plot URL extracted from tool: {plot_url}")
                        break
                except (json.JSONDecodeError, AttributeError):
                    continue
        
        return AnswerResponse(answer=last_message.content, success=True, plot_url=plot_url)
    except Exception as e:
        print(f"[ERROR] Exception in /ask endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Handle specific API quota/rate limit errors
        error_message = str(e)
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. The Google Gemini API has rate limits. Please wait a moment and try again, or upgrade your API key for higher limits."
            )
        elif "RATE_LIMIT_EXCEEDED" in error_message:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a moment before trying again."
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/plots/{filename}")
def get_plot(filename: str):
    """
    Serve generated plot images.
    
    Args:
        filename: Name of the plot file
        
    Returns:
        FileResponse with the plot image
    """
    filepath = os.path.join(PLOTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(filepath, media_type="image/png")


# --- Main ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
