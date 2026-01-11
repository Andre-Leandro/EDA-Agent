"""
Test script for the plotting functionality of the EDA Agent.
This demonstrates how the agent can generate various statistical plots.
"""
from main import agent_executor

# Test cases for different plot types
test_queries = [
    "Create a histogram of the age distribution",
    "Show me a boxplot of fare by passenger class",
    "Generate a scatter plot of age vs fare colored by survival status",
    "Make a count plot of sex with survival information",
    "Create a correlation heatmap of all numeric columns",
    "Show me the distribution of passenger classes",
]

def test_plot_generation():
    """Test the plot generation capabilities of the agent"""
    print("=" * 80)
    print("TESTING EDA AGENT PLOT GENERATION")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {query}")
        print(f"{'=' * 80}")
        
        try:
            result = agent_executor.invoke({"messages": [("human", query)]})
            last_message = result["messages"][-1]
            print(f"\n✓ AGENT RESPONSE:\n{last_message.content}\n")
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}\n")
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)
    print("\nCheck the 'plots' directory for generated visualizations!")

if __name__ == "__main__":
    test_plot_generation()
