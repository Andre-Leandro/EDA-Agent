import { useState } from 'react'
import pokerCard from './assets/poker-card.jpg'
import { Button } from './components/ui/button'
import { Textarea } from './components/ui/textarea'
import { Card, CardContent } from './components/ui/card'

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

  const downloadImage = async (url) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `plot_${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (error) {
      console.error('Error downloading image:', error)
    }
  }

  return (
    <div className="min-h-screen w-full text-black">
      <header className="sticky top-0 z-20 w-full border-b border-black/10 bg-white/70 shadow-md backdrop-blur-xl">
        <div className="flex items-center gap-3 px-4 py-3">
          <img src={pokerCard} alt="App icon" className="h-12 w-12 rounded-xl border border-black/10 object-cover shadow" />
          <div className="flex flex-col items-start">
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-500">EDA Agent</span>
            <h1 className="text-xl font-semibold leading-tight text-black">Data chat with attitude</h1>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col pb-48 pt-4">
        <div className="flex-1 space-y-4 overflow-y-auto px-4">
          {history.length === 0 && !answer && (
            <div className="flex h-full flex-col items-center justify-center gap-4 py-20">
              <div className="rounded-2xl bg-black/90 px-6 py-4 text-center shadow-lg">
                <h2 className="text-2xl font-semibold text-white">Ready to explore your data?</h2>
                <p className="mt-2 text-sm text-white/70">Ask a question below or pick a quick prompt to get started.</p>
              </div>
            </div>
          )}

          {history.length > 0 &&
            history.map((item, index) => (
              <div key={index} className="flex flex-col gap-3">
                <div className="flex justify-end">
                  <div className="max-w-[80%] rounded-2xl bg-black/90 px-4 py-3 text-sm text-white shadow-lg">
                    <p className="mb-1 text-[11px] uppercase tracking-wide text-white/70">You</p>
                    <p className="leading-relaxed">{item.question}</p>
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-[90%] rounded-2xl border border-black/10 bg-white/90 px-4 py-3 text-sm text-black shadow">
                    <p className="mb-1 text-[11px] uppercase tracking-wide text-neutral-500">Agent</p>
                    <div
                      className="leading-relaxed"
                      dangerouslySetInnerHTML={renderMarkdown(item.answer)}
                    />
                    {item.plotUrl && (
                      <div className="mt-3 overflow-hidden rounded-xl border border-black/10 bg-white/80">
                        <img src={item.plotUrl} alt="Generated plot" className="w-full" />
                        <div className="flex justify-end border-t border-black/10 bg-white/90 px-3 py-2">
                          <button
                            onClick={() => downloadImage(item.plotUrl)}
                            className="inline-flex items-center gap-1 rounded-full bg-black px-3 py-1 text-xs font-medium text-white transition hover:bg-neutral-800"
                          >
                            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                            Download
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

          {history.length === 0 && answer && (
            <div className="max-w-[90%] rounded-2xl border border-black/10 bg-white/90 px-4 py-3 text-sm text-black shadow">
              <p className="mb-1 text-[11px] uppercase tracking-wide text-neutral-500">Agent</p>
              <div dangerouslySetInnerHTML={renderMarkdown(answer)} />
            </div>
          )}

          {error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              ❌ {error}
            </div>
          )}
        </div>
      </main>

      <div className="fixed bottom-0 left-0 right-0 z-10 border-t border-black/10 bg-white/75 shadow-2xl backdrop-blur-xl">
        <div className="mx-auto w-full max-w-5xl px-4 py-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-end">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the data..."
              disabled={loading}
              rows={2}
              className="min-h-[64px] max-h-[200px] resize-none"
            />
            <Button
              onClick={askQuestion}
              disabled={loading || !question.trim()}
              className="md:self-stretch md:px-6"
            >
              {loading ? 'Thinking…' : 'Ask'}
            </Button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {exampleQuestions.map((q, i) => (
              <Button
                key={i}
                variant="ghost"
                size="sm"
                className="border border-black/10 bg-white/80 text-xs font-medium text-black hover:border-black hover:bg-white"
                onClick={() => setQuestion(q)}
              >
                {q}
              </Button>
            ))}
          </div>
        </div>
      </div>

      <footer className="fixed bottom-1 left-0 right-0 z-0 pb-2 text-center text-xs text-neutral-500">
        Powered by Gemini AI 🤖
      </footer>
    </div>
  )
}

export default App
