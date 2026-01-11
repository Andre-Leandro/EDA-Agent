"""
Ejemplos de uso directo de la herramienta tool_plot.
Este archivo muestra la interfaz JSON que acepta la herramienta.
"""
import json
from main import tool_plot, tool_schema

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_plot_tool():
    """
    Prueba directa de la herramienta tool_plot con diferentes parámetros.
    """
    
    print_section("🔍 PASO 1: Consultar el esquema de datos")
    
    # Primero, consultamos qué columnas hay disponibles
    schema_result = tool_schema.invoke("")
    print("Columnas disponibles:")
    print(json.dumps(json.loads(schema_result), indent=2))
    
    print_section("📊 PASO 2: Generar diferentes tipos de gráficos")
    
    # Ejemplos de diferentes tipos de gráficos
    plot_examples = [
        {
            "name": "Histograma de Edades",
            "params": {
                "plot_type": "histogram",
                "x": "age",
                "title": "Distribución de Edades de Pasajeros del Titanic"
            }
        },
        {
            "name": "Boxplot de Tarifas por Clase",
            "params": {
                "plot_type": "boxplot",
                "x": "pclass",
                "y": "fare",
                "title": "Comparación de Tarifas por Clase"
            }
        },
        {
            "name": "Scatter Plot: Edad vs Tarifa",
            "params": {
                "plot_type": "scatter",
                "x": "age",
                "y": "fare",
                "hue": "survived",
                "title": "Relación entre Edad y Tarifa (coloreado por supervivencia)"
            }
        },
        {
            "name": "Countplot de Género con Supervivencia",
            "params": {
                "plot_type": "countplot",
                "x": "sex",
                "hue": "survived",
                "title": "Distribución de Pasajeros por Género y Supervivencia"
            }
        },
        {
            "name": "Violin Plot de Edad por Clase",
            "params": {
                "plot_type": "violin",
                "x": "pclass",
                "y": "age",
                "title": "Distribución de Edades por Clase de Pasajero"
            }
        },
        {
            "name": "Heatmap de Correlaciones",
            "params": {
                "plot_type": "heatmap",
                "title": "Mapa de Calor: Correlaciones entre Variables Numéricas"
            }
        },
    ]
    
    for i, example in enumerate(plot_examples, 1):
        print(f"\n{i}. {example['name']}")
        print("-" * 80)
        print("Parámetros JSON:")
        print(json.dumps(example['params'], indent=2))
        
        # Invocar la herramienta
        result_json = tool_plot.invoke(json.dumps(example['params']))
        result = json.loads(result_json)
        
        if result.get('success'):
            print(f"\n✅ {result['message']}")
            print(f"📁 Archivo: {result['plot_path']}")
            print(f"🔗 URL: {result['plot_url']}")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        print()
    
    print_section("🎯 RESUMEN DE LA INTERFAZ")
    
    print("""
La herramienta tool_plot acepta un string JSON con los siguientes campos:

CAMPOS REQUERIDOS (según el tipo de gráfico):
- plot_type: str   → Tipo de gráfico (histogram, bar, boxplot, scatter, etc.)

CAMPOS OPCIONALES:
- x: str          → Nombre de la columna para el eje X
- y: str          → Nombre de la columna para el eje Y
- hue: str        → Columna para agrupar/colorear
- title: str      → Título personalizado del gráfico

VALIDACIONES AUTOMÁTICAS:
✓ Verifica que las columnas existan en el dataset
✓ Valida que el tipo de gráfico sea soportado
✓ Asegura que se provean los parámetros necesarios para cada tipo

TIPOS DE GRÁFICOS SOPORTADOS:
1. histogram   → Requiere: x
2. bar         → Requiere: x, y
3. boxplot     → Requiere: y (x opcional)
4. scatter     → Requiere: x, y
5. line        → Requiere: x, y
6. countplot   → Requiere: x
7. violin      → Requiere: y (x opcional)
8. heatmap     → No requiere parámetros (usa todas las columnas numéricas)
9. pairplot    → Opcional: x, y, hue (usa columnas numéricas por defecto)

RESPUESTA DE LA HERRAMIENTA:
{
  "success": true/false,
  "plot_path": "plots/plot_*.png",
  "plot_url": "/plots/plot_*.png",
  "message": "Mensaje descriptivo"
}

En caso de error:
{
  "error": "Descripción del error",
  "available_columns": [...] (si el error es por columna no encontrada)
}
    """)
    
    print("=" * 80)
    print("\n✨ La herramienta es COMPLETAMENTE FLEXIBLE y NO está hardcodeada!")
    print("   El agente puede consultar tool_schema() primero para saber qué columnas usar.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_plot_tool()
