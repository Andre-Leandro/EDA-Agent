# Tools Directory

Este directorio contiene todas las herramientas (tools) disponibles para el agente de EDA.

## Estructura

```
tools/
├── __init__.py                    # Exporta todas las tools
├── context.py                     # Manejo del dataframe global
├── schema.py                      # Tool: información de schema
├── nulls.py                       # Tool: valores faltantes
├── describe.py                    # Tool: estadísticas descriptivas
├── plot.py                        # Tool: visualizaciones
├── column_profile.py              # Tool: perfil de columnas
├── outliers.py                    # Tool: detección de outliers
├── correlation.py                 # Tool: matriz de correlación
└── categorical_distribution.py    # Tool: distribución categórica
```

## Cómo agregar una nueva tool

1. **Crea un nuevo archivo** en este directorio (ej: `my_new_tool.py`)

2. **Implementa la tool** usando el decorador `@tool` de LangChain:

```python
"""
Mi nueva tool - Descripción breve.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_my_feature(input_str: str) -> str:
    """
    Descripción detallada de lo que hace la tool.
    
    Args:
        input_str: Descripción del input esperado (puede ser JSON)
        
    Returns:
        Resultado en formato JSON string
    """
    df = get_dataframe()
    
    # Tu lógica aquí
    result = {"success": True, "data": "..."}
    
    return json.dumps(result)
```

3. **Exporta la tool** en `__init__.py`:

```python
from .my_new_tool import tool_my_feature

__all__ = [
    # ... otras tools
    "tool_my_feature",
]

ALL_TOOLS = [
    # ... otras tools
    tool_my_feature,
]
```

4. **La tool está lista** - el agente la usará automáticamente.

## Mejores prácticas

- **Una tool por archivo** para mejor organización
- **Usa `get_dataframe()`** para acceder al dataset actual
- **Retorna JSON** para respuestas estructuradas
- **Documenta bien** el docstring - el LLM lo usa para decidir cuándo usar la tool
- **Maneja errores** y retorna mensajes claros
- **Valida inputs** antes de procesarlos

## Context Management

El archivo `context.py` maneja el dataframe global:
- `set_dataframe(df)` - Establece el dataframe actual
- `get_dataframe()` - Obtiene el dataframe actual

El API llama a `set_dataframe()` en cada request, así las tools siempre trabajan con el dataset correcto.
