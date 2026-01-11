import { useState } from 'react'
import './App.css'

function App() {
  // Function to extract plot URLs from text
  const extractPlotUrl = (text) => {
    const urlMatch = text.match(/plots\/plot_\w+_\d+\.png/)
    return urlMatch ? `http://localhost:8000/${urlMatch[0]}` : null
  }

  // Function to convert markdown bold (**text**) to HTML
  const renderMarkdown = (text) => {
    if (!text) return text
    
    // Replace **text** with <strong>$1</strong>
    const boldText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    
    return { __html: boldText }
  }

  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [plotUrl, setPlotUrl] = useState(null)

  const askQuestion = async () => {
    if (!question.trim()) return
    
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
      })
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('API Response:', data) // Debug log
      setAnswer(data.answer)
      const plotUrl = data.plot_url ? `http://localhost:8000${data.plot_url}` : null
      console.log('Plot URL:', plotUrl) // Debug log
      setPlotUrl(plotUrl)
      setHistory([...history, { question, answer: data.answer, plotUrl }])
      setQuestion('')
    } catch (err) {
      setError(err.message || 'Failed to get answer')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      askQuestion()
    }
  }

  const exampleQuestions = [
    "What columns are in the dataset?",
    "Which columns have missing values?",
    "Give me statistics for the age column",
    "Show me a histogram of age distribution",
    "Create a boxplot of fare by passenger class",
    "Generate a correlation heatmap",
  ]

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 EDA Agent</h1>
        <p>Ask questions about your CSV data</p>
      </header>

      <main className="main">
        <div className="chat-container">
          {history.length > 0 && (
            <div className="history">
              {history.map((item, index) => (
                <div key={index} className="chat-item">
                  <div className="question-bubble">
                    <strong>You:</strong> {item.question}
                  </div>
                  <div className="answer-bubble">
                    <strong>Agent:</strong>
                    <div 
                      className="answer-content"
                      dangerouslySetInnerHTML={renderMarkdown(item.answer)}
                    />
                    {item.plotUrl && (
                      <div className="plot-container">
                        <img src={item.plotUrl} alt="Generated plot" className="plot-image" />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {answer && history.length === 0 && (
            <div className="answer-box">
              <h3>Answer:</h3>
              <div dangerouslySetInnerHTML={renderMarkdown(answer)} />
            </div>
          )}

          {error && (
            <div className="error-box">
              <p>❌ {error}</p>
            </div>
          )}
        </div>

        <div className="input-container">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the data..."
            disabled={loading}
            rows={2}
          />
          <button onClick={askQuestion} disabled={loading || !question.trim()}>
            {loading ? '⏳ Thinking...' : '📤 Ask'}
          </button>
        </div>

        <div className="examples">
          <p>Try these examples:</p>
          <div className="example-buttons">
            {exampleQuestions.map((q, i) => (
              <button key={i} onClick={() => setQuestion(q)} className="example-btn">
                {q}
              </button>
            ))}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Powered by Gemini AI 🤖</p>
      </footer>
    </div>
  )
}

export default App
