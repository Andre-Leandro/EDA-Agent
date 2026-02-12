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
from .utils import validate_and_match_columns, get_correction_message

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
        
        # Validate and match columns using fuzzy matching
        all_requested_cols = [(x_col, "x"), (y_col, "y"), (hue_col, "hue")]
        corrections_made = []
        
        for col, param_name in all_requested_cols:
            if col:
                matched, corrections, not_found = validate_and_match_columns(
                    [col], list(df.columns), cutoff=0.6
                )
                
                if not_found:
                    # Try with a lower cutoff for suggestions
                    suggestions, _, _ = validate_and_match_columns(
                        [col], list(df.columns), cutoff=0.4
                    )
                    error_msg = f"Column '{col}' not found in dataset."
                    if suggestions:
                        suggestion_names = [f"'{s}'" for s in suggestions[:3]]
                        error_msg += f" Did you mean: {', '.join(suggestion_names)}?"
                    return json.dumps({
                        "error": error_msg,
                        "available_columns": list(df.columns)
                    })
                
                # Update the column variable with the matched name
                if corrections:
                    corrections_made.extend(corrections)
                    matched_col = matched[0]
                    if param_name == "x":
                        x_col = matched_col
                    elif param_name == "y":
                        y_col = matched_col
                    elif param_name == "hue":
                        hue_col = matched_col
        
        # Create figure
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Variables to store data insights
        data_summary = {}
        
        # Generate plot based on type
        if plot_type == "histogram":
            if not x_col:
                return json.dumps({"error": "'x' column is required for histogram"})
            sns.histplot(data=df, x=x_col, hue=hue_col, kde=True)
            if not title:
                title = f"Distribution of {x_col}"
            
            # Add data summary for histogram
            col_data = df[x_col].dropna()
            if col_data.dtype in ['int64', 'float64']:
                data_summary = {
                    "column": x_col,
                    "count": int(len(col_data)),
                    "mean": round(float(col_data.mean()), 2),
                    "median": round(float(col_data.median()), 2),
                    "std": round(float(col_data.std()), 2),
                    "min": round(float(col_data.min()), 2),
                    "max": round(float(col_data.max()), 2)
                }
            else:
                # Categorical column
                value_counts = col_data.value_counts().to_dict()
                data_summary = {
                    "column": x_col,
                    "count": int(len(col_data)),
                    "unique_values": int(col_data.nunique()),
                    "frequencies": {str(k): int(v) for k, v in list(value_counts.items())[:10]}
                }
                
        elif plot_type == "bar":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for bar plot"})
            sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"{y_col} by {x_col}"
            
            # Add data summary for bar plot
            grouped = df.groupby(x_col)[y_col].agg(['mean', 'count']).round(2)
            data_summary = {
                "x_column": x_col,
                "y_column": y_col,
                "groups": {str(k): {"mean": float(v['mean']), "count": int(v['count'])} 
                          for k, v in grouped.iterrows()}
            }
                
        elif plot_type == "boxplot":
            if not y_col:
                return json.dumps({"error": "'y' column is required for boxplot"})
            sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"Box Plot of {y_col}" + (f" by {x_col}" if x_col else "")
            
            # Add data summary for boxplot
            col_data = df[y_col].dropna()
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            data_summary = {
                "column": y_col,
                "count": int(len(col_data)),
                "min": round(float(col_data.min()), 2),
                "q1": round(float(q1), 2),
                "median": round(float(col_data.median()), 2),
                "q3": round(float(q3), 2),
                "max": round(float(col_data.max()), 2),
                "iqr": round(float(iqr), 2),
                "outliers_count": int(((col_data < (q1 - 1.5 * iqr)) | (col_data > (q3 + 1.5 * iqr))).sum())
            }
            if x_col:
                data_summary["grouped_by"] = x_col
                
        elif plot_type == "scatter":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for scatter plot"})
            sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, alpha=0.6)
            if not title:
                title = f"{y_col} vs {x_col}"
            
            # Add data summary for scatter plot
            plot_data = df[[x_col, y_col]].dropna()
            correlation = plot_data[x_col].corr(plot_data[y_col])
            data_summary = {
                "x_column": x_col,
                "y_column": y_col,
                "count": int(len(plot_data)),
                "correlation": round(float(correlation), 3)
            }
                
        elif plot_type == "line":
            if not x_col or not y_col:
                return json.dumps({"error": "'x' and 'y' columns are required for line plot"})
            sns.lineplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"{y_col} over {x_col}"
            
            # Add data summary for line plot
            plot_data = df[[x_col, y_col]].dropna()
            data_summary = {
                "x_column": x_col,
                "y_column": y_col,
                "count": int(len(plot_data)),
                "y_mean": round(float(plot_data[y_col].mean()), 2),
                "y_range": [round(float(plot_data[y_col].min()), 2), round(float(plot_data[y_col].max()), 2)]
            }
                
        elif plot_type == "countplot":
            if not x_col:
                return json.dumps({"error": "'x' column is required for countplot"})
            sns.countplot(data=df, x=x_col, hue=hue_col)
            if not title:
                title = f"Count of {x_col}"
            
            # Add data summary for countplot
            col_data = df[x_col].dropna()
            value_counts = col_data.value_counts().to_dict()
            data_summary = {
                "column": x_col,
                "total_count": int(len(col_data)),
                "unique_values": int(col_data.nunique()),
                "frequencies": {str(k): int(v) for k, v in value_counts.items()}
            }
                
        elif plot_type == "violin":
            if not y_col:
                return json.dumps({"error": "'y' column is required for violin plot"})
            sns.violinplot(data=df, x=x_col, y=y_col, hue=hue_col)
            if not title:
                title = f"Violin Plot of {y_col}" + (f" by {x_col}" if x_col else "")
            
            # Add data summary for violin plot
            col_data = df[y_col].dropna()
            data_summary = {
                "column": y_col,
                "count": int(len(col_data)),
                "mean": round(float(col_data.mean()), 2),
                "median": round(float(col_data.median()), 2),
                "std": round(float(col_data.std()), 2),
                "range": [round(float(col_data.min()), 2), round(float(col_data.max()), 2)]
            }
            if x_col:
                data_summary["grouped_by"] = x_col
                
        elif plot_type == "heatmap":
            # Select columns for correlation heatmap
            if columns_list:
                # Use fuzzy matching for the column list
                matched_cols, heatmap_corrections, not_found = validate_and_match_columns(
                    columns_list, list(df.columns), cutoff=0.6
                )
                
                if not_found:
                    # Try with lower cutoff for suggestions
                    suggestions = []
                    for nf in not_found:
                        sugg, _, _ = validate_and_match_columns([nf], list(df.columns), cutoff=0.4)
                        if sugg:
                            suggestions.append("'{}' -> maybe '{}'".format(nf, sugg[0]))
                        else:
                            suggestions.append("'{}' (no match found)".format(nf))
                    
                    suggestions_text = ", ".join(suggestions)
                    return json.dumps({
                        "error": f"Some columns could not be matched: {suggestions_text}",
                        "available_columns": list(df.columns)
                    })
                
                if heatmap_corrections:
                    corrections_made.extend(heatmap_corrections)
                
                numeric_df = df[matched_cols].select_dtypes(include=['number'])
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
            
            # Add data summary for heatmap
            # Find strongest positive and negative correlations
            corr_values = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    corr_values.append({
                        "pair": f"{corr.columns[i]} - {corr.columns[j]}",
                        "correlation": round(float(corr.iloc[i, j]), 3)
                    })
            corr_values.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            data_summary = {
                "columns": list(corr.columns),
                "num_columns": len(corr.columns),
                "strongest_correlations": corr_values[:5] if corr_values else []
            }
                
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
            
            # Add data summary for pairplot
            plot_df = df[cols_to_plot].select_dtypes(include=['number'])
            data_summary = {
                "columns": list(plot_df.columns),
                "num_columns": len(plot_df.columns),
                "total_observations": int(len(plot_df))
            }
            
            return json.dumps({
                "success": True,
                "plot_path": filepath,
                "plot_url": f"/plots/{filename}",
                "data_summary": data_summary,
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
        
        # Build success message with corrections if any
        message = f"{plot_type.capitalize()} plot generated successfully!"
        if corrections_made:
            message += " " + get_correction_message(corrections_made)
        
        return json.dumps({
            "success": True,
            "plot_path": filepath,
            "plot_url": f"/plots/{filename}",
            "data_summary": data_summary,
            "message": message
        })
        
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON format in input. Please provide valid JSON."})
    except Exception as e:
        return json.dumps({"error": f"Failed to generate plot: {str(e)}"})
