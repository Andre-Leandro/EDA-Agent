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
DEFAULT_CSV_PATH = "titanic.csv"
PLOTS_DIR = "plots"
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
    return {"status": "healthy"}


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
            df = pd.read_csv(io.BytesIO(contents))
            print(f"[DEBUG] Loaded custom CSV: {file.filename}, shape: {df.shape}")
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
