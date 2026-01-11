"""
Script de demostración completo de las capacidades de visualización del EDA Agent.
Este script muestra cómo el agente puede generar diversos tipos de gráficos
consultando dinámicamente el esquema de datos.
"""
from main import agent_executor
import os

def demo_visualization_capabilities():
    """
    Demuestra todas las capacidades de visualización del agente.
    """
    
    demos = [
        {
            "title": "1. Histograma de Distribución de Edades",
            "query": "Create a histogram showing the distribution of passenger ages",
            "description": "Visualiza cómo se distribuyen las edades en el Titanic"
        },
        {
            "title": "2. Boxplot de Tarifas por Clase",
            "query": "Generate a boxplot comparing fares across different passenger classes",
            "description": "Compara las tarifas pagadas entre las diferentes clases"
        },
        {
            "title": "3. Scatter Plot: Edad vs Tarifa con Supervivencia",
            "query": "Show me a scatter plot of age versus fare, colored by survival status",
            "description": "Explora la relación entre edad, tarifa y supervivencia"
        },
        {
            "title": "4. Countplot: Distribución de Pasajeros por Sexo",
            "query": "Create a count plot showing the distribution of passengers by sex, grouped by survival",
            "description": "Analiza la supervivencia por género"
        },
        {
            "title": "5. Heatmap de Correlaciones",
            "query": "Generate a correlation heatmap for all numeric columns in the dataset",
            "description": "Visualiza las correlaciones entre variables numéricas"
        },
        {
            "title": "6. Violin Plot: Edad por Clase",
            "query": "Show a violin plot of passenger ages across different classes",
            "description": "Muestra la distribución de edades en cada clase con densidad"
        },
    ]
    
    print("=" * 100)
    print(" " * 25 + "🎨 DEMOSTRACIÓN DE VISUALIZACIÓN DEL EDA AGENT 🎨")
    print("=" * 100)
    print("\nEste agente puede generar gráficos estadísticos de manera inteligente.")
    print("NO está hardcodeado - consulta el esquema de datos dinámicamente!\n")
    
    for i, demo in enumerate(demos, 1):
        print("\n" + "=" * 100)
        print(f"\n{demo['title']}")
        print(f"📝 {demo['description']}")
        print(f"\n❓ Pregunta: \"{demo['query']}\"")
        print("\n" + "-" * 100)
        
        try:
            result = agent_executor.invoke({"messages": [("human", demo["query"])]})
            last_message = result["messages"][-1]
            print(f"\n🤖 Respuesta del Agente:\n{last_message.content}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        print("\n" + "-" * 100)
    
    print("\n" + "=" * 100)
    print(" " * 35 + "✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 100)
    
    # List generated plots
    plots_dir = "plots"
    if os.path.exists(plots_dir):
        plots = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        print(f"\n📊 Gráficos generados ({len(plots)}):")
        for plot in sorted(plots):
            print(f"   • {plot}")
    
    print("\n" + "=" * 100)
    print("\n🎯 CARACTERÍSTICAS CLAVE:")
    print("   ✓ El agente consulta el esquema DINÁMICAMENTE usando tool_schema()")
    print("   ✓ Valida que las columnas existan antes de generar gráficos")
    print("   ✓ Soporta 8 tipos diferentes de gráficos")
    print("   ✓ Genera títulos descriptivos automáticamente")
    print("   ✓ Maneja errores elegantemente con mensajes útiles")
    print("   ✓ Guarda gráficos con timestamps únicos")
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Inicia el backend: python api.py")
    print("   2. Inicia el frontend: cd frontend && npm run dev")
    print("   3. Abre http://localhost:5173 y prueba con preguntas como:")
    print("      • 'Muéstrame la distribución de edades'")
    print("      • 'Crea un boxplot de tarifas por clase'")
    print("      • 'Genera un heatmap de correlaciones'")
    print("\n" + "=" * 100 + "\n")

if __name__ == "__main__":
    demo_visualization_capabilities()
