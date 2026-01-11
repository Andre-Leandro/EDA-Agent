# 🔍 EDA-Agent

Agente inteligente de Análisis Exploratorio de Datos con capacidades de visualización usando Gemini AI.

## ✨ Características

- 🤖 **Agente IA Conversacional**: Powered by Gemini 2.0 Flash
- 📊 **Visualización de Datos**: Genera gráficos estadísticos automáticamente
- 🔎 **Análisis de Esquema**: Consulta dinámica de columnas y tipos de datos
- 📈 **Múltiples Tipos de Gráficos**: Histogramas, boxplots, scatter plots, heatmaps, y más
- 🎯 **Sin Hardcodeo**: El agente consulta el esquema dinámicamente
- 🌐 **Interfaz Web**: Frontend React con visualización de gráficos
- 🚀 **API REST**: FastAPI backend con endpoints para consultas y gráficos

## 🛠️ Tecnologías

### Backend
- Python 3.12+
- LangChain
- Google Gemini AI (gemini-2.0-flash)
- FastAPI
- Pandas
- Matplotlib & Seaborn

### Frontend
- React 18
- Vite
- CSS moderno

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd EDA-Agent
```

### 2. Configurar el entorno Python

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
GOOGLE_API_KEY=tu_api_key_de_gemini
```

### 4. Configurar el frontend

```bash
cd frontend
npm install
```

## 🚀 Uso

### Iniciar el Backend

```bash
# En la raíz del proyecto
source .venv/bin/activate
python api.py
```

El servidor estará disponible en `http://localhost:8000`

### Iniciar el Frontend

```bash
# En el directorio frontend
cd frontend
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## 📊 Herramientas del Agente

### 1. `tool_schema`
Retorna columnas y tipos de datos del CSV.

**Ejemplos**:
- "¿Qué columnas hay en el dataset?"
- "Muéstrame las primeras 3 columnas"
- "¿Cuál es el tipo de dato de age?"

### 2. `tool_nulls`
Identifica columnas con valores faltantes.

**Ejemplos**:
- "¿Qué columnas tienen valores nulos?"
- "Muéstrame los valores faltantes"

### 3. `tool_describe`
Genera estadísticas descriptivas.

**Ejemplos**:
- "Dame estadísticas de la columna age"
- "Describe todas las columnas numéricas"

### 4. `tool_plot` ⭐ NUEVO
Genera visualizaciones estadísticas automáticas.

**Tipos de gráficos soportados**:
- 📊 **Histogram**: Distribución de variables numéricas
- 📦 **Boxplot**: Diagramas de cajas y bigotes
- 🔵 **Scatter**: Gráficos de dispersión
- 📈 **Bar**: Gráficos de barras
- 🔢 **Countplot**: Conteo de categorías
- 🎻 **Violin**: Violin plots
- 🔥 **Heatmap**: Mapas de calor de correlaciones
- 📌 **Pairplot**: Matriz de dispersión

**Ejemplos de uso**:
- "Muéstrame la distribución de edades"
- "Crea un boxplot de tarifas por clase"
- "Genera un scatter plot de edad vs tarifa coloreado por supervivencia"
- "Haz un heatmap de correlaciones"

## 🧪 Testing

### Probar las herramientas individualmente

```bash
python main.py
```

### Probar la funcionalidad de gráficos

```bash
python test_plots.py
```

Este script genera múltiples gráficos de ejemplo en el directorio `plots/`.

### Verificar tests básicos

```bash
python test.py
```

## 📁 Estructura del Proyecto

```
EDA-Agent/
├── .venv/                    # Entorno virtual Python
├── plots/                    # Gráficos generados automáticamente
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── App.jsx          # Componente principal con soporte de imágenes
│   │   ├── App.css          # Estilos incluyendo plot-container
│   │   └── main.jsx
│   └── package.json
├── api.py                    # FastAPI backend con endpoint de gráficos
├── main.py                   # Script principal del agente
├── test_plots.py            # Tests de visualización
├── titanic.csv              # Dataset de ejemplo
├── VISUALIZATION_GUIDE.md   # Guía completa de visualización
└── README.md                # Este archivo
```

## 🎨 Ejemplos de Preguntas

### Análisis de Datos
```
"¿Qué columnas tiene el dataset?"
"¿Cuántos valores faltantes hay en cada columna?"
"Dame estadísticas de la columna age"
```

### Visualizaciones
```
"Muestra la distribución de edades con un histograma"
"Crea un boxplot comparando tarifas entre clases"
"Genera un scatter plot de edad vs tarifa"
"Muéstrame un heatmap de correlaciones"
"Haz un countplot de supervivientes por sexo"
```

## 🔧 API Endpoints

### POST /ask
Envía una pregunta al agente.

**Request**:
```json
{
  "question": "Show me a histogram of ages"
}
```

**Response**:
```json
{
  "answer": "I've generated a histogram showing the age distribution...",
  "success": true
}
```

### GET /plots/{filename}
Obtiene una imagen de gráfico generado.

**Ejemplo**: `GET /plots/plot_histogram_20260111_143025.png`

## 🎯 Cómo Funciona la Visualización

1. **Usuario pregunta**: "Muestra la distribución de edades"
2. **Agente consulta esquema**: Usa `tool_schema()` para verificar que la columna "age" existe
3. **Agente decide el gráfico**: Determina que un histograma es apropiado
4. **Genera el gráfico**: Llama a `tool_plot()` con parámetros JSON
5. **Guarda la imagen**: El gráfico se guarda en `plots/`
6. **Retorna la ruta**: El frontend detecta la URL y muestra la imagen

## 📚 Documentación Adicional

- **[VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)**: Guía completa de visualización con ejemplos detallados

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

## 👏 Agradecimientos

- Google Gemini AI por el modelo de lenguaje
- LangChain por el framework de agentes
- Seaborn y Matplotlib por las capacidades de visualización

---

**¡Explora tus datos con el poder de la IA! 🚀📊**
