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

  return (
    <div className="min-h-screen w-full text-black">
      <header className="sticky top-0 z-20 w-full">
        <div className="mx-auto flex max-w-5xl items-center gap-3 rounded-2xl border border-white/40 bg-white/70 px-4 py-3 shadow-lg backdrop-blur-xl">
          <img src={pokerCard} alt="App icon" className="h-12 w-12 rounded-xl border border-black/10 object-cover shadow" />
          <div className="flex flex-col">
            <span className="text-xs uppercase tracking-[0.3em] text-neutral-500">EDA Agent</span>
            <h1 className="text-xl font-semibold leading-tight text-black">Data chat with attitude</h1>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-5 pb-10 pt-4">
        <Card className="flex-1 overflow-hidden border-white/50 bg-white/60 shadow-2xl">
          <CardContent className="flex h-full flex-col gap-4 p-4 md:p-6">
            <div className="flex-1 space-y-4 overflow-y-auto pr-1">
              {history.length > 0 ? (
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
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : answer ? (
                <div className="max-w-[90%] rounded-2xl border border-black/10 bg-white/90 px-4 py-3 text-sm text-black shadow">
                  <p className="mb-1 text-[11px] uppercase tracking-wide text-neutral-500">Agent</p>
                  <div dangerouslySetInnerHTML={renderMarkdown(answer)} />
                </div>
              ) : (
                <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-black/10 bg-white/50 p-6 text-sm text-neutral-500">
                  Ask something to start the session.
                </div>
              )}
            </div>

            {error && (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                ❌ {error}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="rounded-3xl border border-white/50 bg-white/70 p-4 shadow-xl backdrop-blur-xl">
          <div className="flex flex-col gap-3 md:flex-row md:items-end">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the data..."
              disabled={loading}
              rows={3}
              className="min-h-[96px]"
            />
            <Button
              onClick={askQuestion}
              disabled={loading || !question.trim()}
              className="md:self-stretch md:px-6"
            >
              {loading ? 'Thinking…' : 'Ask'}
            </Button>
          </div>
          <p className="mt-2 text-xs text-neutral-500">Enter to send · Shift+Enter for newline</p>
        </div>

        <div className="rounded-3xl border border-white/50 bg-white/70 p-4 shadow-xl backdrop-blur-xl">
          <p className="text-sm font-semibold text-neutral-700">Quick prompts</p>
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
      </main>

      <footer className="pb-6 text-center text-sm text-neutral-600">
        Powered by Gemini AI 🤖
      </footer>
    </div>
  )
}

export default App
