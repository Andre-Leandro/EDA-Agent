"""
Plot tool - Generates statistical visualizations.
"""
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from langchain_core.tools import tool
from .context import get_dataframe

# Plots directory
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)


@tool
def tool_plot(input_str: str) -> str:
    """
    Generates statistical plots using seaborn/matplotlib.
    
    Input format (JSON string): {
        "plot_type": "histogram" | "bar" | "boxplot" | "scatter" | "line" | "countplot" | "violin" | "heatmap" | "pairplot",
        "x": "column_name",  # X-axis column (optional for histogram/boxplot - auto-detects first numeric)
        "y": "column_name",  # Y-axis column (optional for boxplot - auto-detects)
        "hue": "column_name",  # Color grouping (optional)
        "columns": ["col1", "col2", "col3"],  # List of columns for heatmap/pairplot (optional)
        "title": "Plot title"  # Optional custom title
    }
    
    Examples:
    - Histogram (auto): {"plot_type": "histogram"} # Uses first numeric column automatically
    - Histogram (specific): {"plot_type": "histogram", "x": "age", "title": "Age Distribution"}
    - Boxplot (auto): {"plot_type": "boxplot"} # Auto-detects numeric columns
    - Boxplot (specific): {"plot_type": "boxplot", "x": "pclass", "y": "fare"}
    - Scatter: {"plot_type": "scatter", "x": "age", "y": "fare", "hue": "survived"}
    - Countplot: {"plot_type": "countplot", "x": "sex", "hue": "survived"}
    - Correlation heatmap (all): {"plot_type": "heatmap"} # Uses all numeric columns
    - Correlation heatmap (specific): {"plot_type": "heatmap", "columns": ["age", "fare", "pclass"]}
    - Pairplot: {"plot_type": "pairplot"} # Automatically uses first 4 numeric columns
    
    Note: For histogram and boxplot, if columns are not specified, the tool automatically 
    detects and uses the first numeric column(s). For heatmap and pairplot, "columns" 
    parameter is optional and all numeric columns will be used if not specified.
    
    Returns: Path to the generated plot image.
    """
    df = get_dataframe()
    
    try:
        # Parse input JSON
        params = json.loads(input_str)
        plot_type = params.get("plot_type", "histogram").lower()
        x_col = params.get("x")
        y_col = params.get("y")
        hue_col = params.get("hue")
        columns_list = params.get("columns")  # List of columns for heatmap/pairplot
        title = params.get("title", "")
        
        # Get numeric columns for auto-detection
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Auto-detect first numeric column if not specified
        if not x_col and plot_type in ["histogram", "boxplot"]:
            if numeric_cols:
                x_col = numeric_cols[0]
            else:
                return json.dumps({"error": "No numeric columns found in dataset"})
        
        if not y_col and plot_type == "boxplot" and len(numeric_cols) > 1:
            # For boxplot, if x is specified but y is not, use first numeric as y
            y_col = numeric_cols[0] if x_col not in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
        
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
            # Select columns for correlation heatmap
            if columns_list:
                # Use specific columns if provided as a list
                missing_cols = [c for c in columns_list if c not in df.columns]
                if missing_cols:
                    return json.dumps({
                        "error": f"Columns not found: {missing_cols}",
                        "available_columns": list(df.columns)
                    })
                numeric_df = df[columns_list].select_dtypes(include=['number'])
            elif x_col or y_col:
                # Use x and y columns if provided
                cols_to_use = [c for c in [x_col, y_col] if c]
                numeric_df = df[cols_to_use].select_dtypes(include=['number'])
            else:
                # Use all numeric columns by default
                numeric_df = df.select_dtypes(include=['number'])
            
            if numeric_df.empty:
                return json.dumps({"error": "No numeric columns found for correlation heatmap"})
            
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt='.2f')
            if not title:
                if columns_list:
                    title = f"Correlation Heatmap ({', '.join(columns_list)})"
                else:
                    title = "Correlation Heatmap"
                
        elif plot_type == "pairplot":
            # For pairplot, we need to save differently
            if columns_list:
                # Use specific columns if provided as a list
                cols_to_plot = [c for c in columns_list if c in df.columns]
            else:
                # Try x, y, hue columns first
                cols_to_plot = [c for c in [x_col, y_col, hue_col] if c]
                
            if not cols_to_plot:
                # Use all numeric columns (limit to 4 for performance)
                cols_to_plot = df.select_dtypes(include=['number']).columns.tolist()[:4]
            
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
