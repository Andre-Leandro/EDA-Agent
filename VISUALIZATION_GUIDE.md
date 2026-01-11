# Guía de Visualización del EDA Agent

## 📊 Descripción General

El EDA Agent ahora cuenta con capacidades avanzadas de visualización de datos usando **Seaborn** y **Matplotlib**. El agente puede generar gráficos estadísticos de manera inteligente consultando el esquema de datos automáticamente.

## 🎯 Características

- ✅ **Flexible y No Hardcodeado**: El agente consulta dinámicamente el esquema de datos
- ✅ **Múltiples Tipos de Gráficos**: Histogramas, boxplots, scatter plots, heatmaps, y más
- ✅ **Inteligencia Contextual**: El agente elige las columnas apropiadas según el tipo de gráfico
- ✅ **Validación Automática**: Verifica que las columnas existan antes de generar gráficos
- ✅ **Guardado Automático**: Los gráficos se guardan en el directorio `plots/`

## 📈 Tipos de Gráficos Disponibles

### 1. **Histogram** (Histograma)
Muestra la distribución de una variable numérica.

**Uso Natural**: "Muéstrame la distribución de edades"

**Parámetros JSON**:
```json
{
  "plot_type": "histogram",
  "x": "age",
  "title": "Distribución de Edades"
}
```

### 2. **Boxplot** (Diagrama de Cajas y Bigotes)
Visualiza la distribución y valores atípicos.

**Uso Natural**: "Crea un boxplot de tarifas por clase de pasajero"

**Parámetros JSON**:
```json
{
  "plot_type": "boxplot",
  "x": "pclass",
  "y": "fare"
}
```

### 3. **Scatter Plot** (Gráfico de Dispersión)
Muestra la relación entre dos variables numéricas.

**Uso Natural**: "Genera un scatter plot de edad vs tarifa coloreado por supervivencia"

**Parámetros JSON**:
```json
{
  "plot_type": "scatter",
  "x": "age",
  "y": "fare",
  "hue": "survived"
}
```

### 4. **Bar Plot** (Gráfico de Barras)
Compara valores agregados entre categorías.

**Uso Natural**: "Muestra la tarifa promedio por clase"

**Parámetros JSON**:
```json
{
  "plot_type": "bar",
  "x": "pclass",
  "y": "fare"
}
```

### 5. **Count Plot** (Conteo)
Cuenta las ocurrencias de cada categoría.

**Uso Natural**: "Cuenta pasajeros por sexo y supervivencia"

**Parámetros JSON**:
```json
{
  "plot_type": "countplot",
  "x": "sex",
  "hue": "survived"
}
```

### 6. **Violin Plot**
Combinación de boxplot y distribución de densidad.

**Uso Natural**: "Crea un violin plot de edades por clase"

**Parámetros JSON**:
```json
{
  "plot_type": "violin",
  "x": "pclass",
  "y": "age"
}
```

### 7. **Heatmap** (Mapa de Calor)
Muestra correlaciones entre variables numéricas.

**Uso Natural**: "Genera un mapa de calor de correlaciones"

**Parámetros JSON**:
```json
{
  "plot_type": "heatmap"
}
```

### 8. **Pairplot**
Matriz de gráficos de dispersión para múltiples variables.

**Uso Natural**: "Muestra relaciones entre todas las variables numéricas"

**Parámetros JSON**:
```json
{
  "plot_type": "pairplot",
  "hue": "survived"
}
```

## 🤖 Cómo el Agente Usa la Herramienta

El agente sigue este flujo inteligente:

1. **Consulta el Esquema**: Usa `tool_schema()` para conocer las columnas disponibles
2. **Valida las Columnas**: Verifica que las columnas solicitadas existan
3. **Selecciona el Tipo de Gráfico**: Según la pregunta del usuario
4. **Genera el Gráfico**: Crea la visualización con parámetros apropiados
5. **Guarda y Retorna**: Guarda la imagen y proporciona la ruta

## 💬 Ejemplos de Preguntas para el Usuario

```
"Muéstrame la distribución de edades"
"Crea un boxplot de tarifas por clase de pasajero"
"Genera un scatter plot de edad vs tarifa"
"Haz un gráfico de barras de supervivencia por sexo"
"Muestra un heatmap de correlaciones"
"Visualiza la distribución de clases de pasajeros"
"Compara las edades entre sobrevivientes y no sobrevivientes"
```

## 🔧 Detalles Técnicos

### Estructura de la Herramienta `tool_plot`

```python
@tool
def tool_plot(input_str: str) -> str:
    """
    Generates statistical plots using seaborn/matplotlib.
    
    Input: JSON string with plot parameters
    Output: JSON with success status and plot path
    """
```

### Respuesta de la Herramienta

```json
{
  "success": true,
  "plot_path": "plots/plot_histogram_20260111_143025.png",
  "plot_url": "/plots/plot_histogram_20260111_143025.png",
  "message": "Histogram plot generated successfully!"
}
```

### Manejo de Errores

La herramienta maneja inteligentemente:
- ❌ Columnas inexistentes
- ❌ Tipos de gráficos no soportados
- ❌ Parámetros faltantes
- ❌ JSON malformado
- ❌ Datos incompatibles

## 📂 Estructura de Directorios

```
EDA-Agent/
├── plots/                          # Gráficos generados
│   ├── plot_histogram_*.png
│   ├── plot_boxplot_*.png
│   └── ...
├── api.py                          # API con endpoint /plots/{filename}
├── main.py                         # Script principal
└── test_plots.py                   # Tests de ejemplo
```

## 🚀 Uso en la API

### Endpoint para Servir Imágenes

```
GET /plots/{filename}
```

Retorna la imagen PNG del gráfico generado.

### Ejemplo de Request/Response

**Request**:
```json
POST /ask
{
  "question": "Muestra la distribución de edades"
}
```

**Response**:
```json
{
  "answer": "He generado un histograma que muestra la distribución de edades...",
  "success": true
}
```

## ✨ Ventajas del Diseño

1. **No Hardcodeado**: El agente consulta dinámicamente las columnas disponibles
2. **Flexible**: Soporta 8 tipos diferentes de gráficos
3. **Inteligente**: El LLM decide qué tipo de gráfico es más apropiado
4. **Validado**: Verifica columnas y parámetros antes de generar
5. **Escalable**: Fácil agregar nuevos tipos de gráficos

## 🧪 Testing

Ejecuta el script de prueba:

```bash
python test_plots.py
```

Esto generará múltiples gráficos de ejemplo en el directorio `plots/`.

## 📝 Notas Importantes

- Los gráficos se guardan con timestamp para evitar sobrescritura
- El backend usa `Agg` (non-interactive) para funcionar en servidores
- Los colores y estilos están configurados con `seaborn` para mejor apariencia
- Los gráficos se optimizan automáticamente con `tight_layout()`

---

**¡El agente ahora puede responder con visualizaciones profesionales de manera completamente automática!** 📊✨
