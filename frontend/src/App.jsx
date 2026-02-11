import { useState, useEffect } from 'react'
import pokerCard from './assets/poker-card.png'
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
  const [datasetType, setDatasetType] = useState('default')
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null) // Store the actual file
  const [isDragging, setIsDragging] = useState(false)
  const [copiedMessageIndex, setCopiedMessageIndex] = useState(null)
  const [saveToLocalStorage, setSaveToLocalStorage] = useState(() => {
    // Load preference from localStorage
    const saved = localStorage.getItem('eda_save_preference')
    return saved ? JSON.parse(saved) : true // Default to enabled
  })
  const [sessionId] = useState(() => {
    // Generate unique session ID when component loads
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  })

  // Load history from localStorage on mount
  useEffect(() => {
    if (saveToLocalStorage) {
      const savedHistory = localStorage.getItem('eda_chat_history')
      if (savedHistory) {
        try {
          setHistory(JSON.parse(savedHistory))
        } catch (e) {
          console.error('Error loading history:', e)
        }
      }
    }
  }, [])

  // Save history to localStorage whenever it changes
  useEffect(() => {
    if (saveToLocalStorage && history.length > 0) {
      localStorage.setItem('eda_chat_history', JSON.stringify(history))
    }
  }, [history, saveToLocalStorage])

  // Save preference whenever it changes
  useEffect(() => {
    localStorage.setItem('eda_save_preference', JSON.stringify(saveToLocalStorage))
    if (!saveToLocalStorage) {
      // If disabled, clear history from localStorage
      localStorage.removeItem('eda_chat_history')
    }
  }, [saveToLocalStorage])

  const clearHistory = () => {
    setHistory([])
    setAnswer('')
    setPlotUrl(null)
    localStorage.removeItem('eda_chat_history')
  }

  const askQuestion = async () => {
    if (!question.trim()) return
    
    setLoading(true)
    setError('')
    
    try {
      const formData = new FormData()
      formData.append('question', question)
      formData.append('dataset_type', datasetType)
      
      // If custom dataset and file is uploaded, send the file
      if (datasetType === 'custom' && uploadedFile) {
        formData.append('file', uploadedFile)
      }
      
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        body: formData,
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
    "Give me basic information about the dataset",
    "Show me a correlation heatmap",
    "Create a histogram of the first numeric column",
    "Show me statistics for all numeric columns",
  ]

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageIndex(index)
      setTimeout(() => setCopiedMessageIndex(null), 2000)
    } catch (error) {
      console.error('Error copying to clipboard:', error)
    }
  }

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

  const handleFileUpload = async (file) => {
    if (!file || file.type !== 'text/csv') {
      setError('Please select a valid CSV file')
      return
    }

    // Store the file for later use in ask requests
    setUploadedFile(file)
    setUploadedFileName(file.name)
    setDatasetType('custom')
    setHistory([]) // Clear history when switching datasets
    setAnswer('')
    setPlotUrl(null)
    setError('')
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleDatasetChange = (type) => {
    if (type === 'default') {
      setDatasetType('default')
      setUploadedFileName('')
      setUploadedFile(null)
      setHistory([])
      setAnswer('')
      setPlotUrl(null)
      setError('')
    } else {
      setDatasetType('custom')
    }
  }

  return (
    <div className="min-h-screen w-full text-black">
      <header className="sticky top-0 z-20 w-full border-b border-black/10 bg-white/70 shadow-md backdrop-blur-xl">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <img src={pokerCard} alt="App icon" className="h-12 w-12 rounded-xl" />
            <div className="flex flex-col items-start">
              <span className="text-xs uppercase tracking-[0.3em] text-neutral-500">EDA Agent</span>
              <h1 className="text-xl font-semibold leading-tight text-black">Data chat</h1>
            </div>
          </div>
          
          {/* Dataset Selector and Controls */}
          <div className="flex items-center gap-3">
            {/* Save to Browser Toggle */}
            <button
              onClick={() => setSaveToLocalStorage(!saveToLocalStorage)}
              className={`flex items-center gap-2 rounded-lg border px-3 py-2.5 transition-all ${
                saveToLocalStorage 
                  ? 'border-green-500 bg-green-50 text-green-700' 
                  : 'border-black/20 bg-white/90 text-neutral-600'
              }`}
              title={saveToLocalStorage ? 'Saving to browser enabled' : 'Saving to browser disabled'}
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              <span className="text-xs font-medium">{saveToLocalStorage ? 'Save: ON' : 'Save: OFF'}</span>
            </button>
            
            {/* Clear History Button */}
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-red-700 transition-all hover:bg-red-100"
                title="Clear chat history"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span className="text-xs font-medium">Clear</span>
              </button>
            )}
            
            <div className="flex items-center gap-2 rounded-lg border border-black/20 bg-white/90 px-3 py-2">
              <span className="text-sm font-medium text-neutral-600">Dataset:</span>
              <select 
                value={datasetType} 
                onChange={(e) => handleDatasetChange(e.target.value)}
                className="bg-transparent text-sm font-medium text-black outline-none"
              >
                <option value="default">Default (Titanic)</option>
                <option value="custom">Upload Custom CSV</option>
              </select>
            </div>
            {datasetType === 'custom' && uploadedFileName && (
              <span className="text-xs text-green-600 font-medium">📄 {uploadedFileName}</span>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col pb-56 pt-4">
        <div className="flex-1 space-y-4 overflow-y-auto px-4 mb-4">
          {/* File Upload Area for Custom Dataset */}
          {datasetType === 'custom' && !uploadedFileName && (
            <div className="mx-auto max-w-md">
              <div 
                className={`rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
                  isDragging 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-black/20 bg-white/50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="mb-4">
                  <svg className="mx-auto h-12 w-12 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-black">Upload your CSV file</h3>
                <p className="mt-2 text-sm text-neutral-600">Drag and drop your CSV file here, or click to browse</p>
                <label className="mt-4 flex cursor-pointer items-center justify-center">
                  <input 
                    type="file" 
                    accept=".csv" 
                    onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0])}
                    className="hidden"
                    lang="en"
                  />
                  <span className="rounded-full border-0 bg-black px-6 py-2 text-sm font-medium text-white transition hover:bg-neutral-800">
                    Choose File
                  </span>
                </label>
              </div>
            </div>
          )}
          
          {history.length === 0 && !answer && (datasetType === 'default' || uploadedFileName) && (
            <div className="flex h-full flex-col items-center justify-center gap-4 py-20">
              <div className="rounded-2xl bg-black/90 px-6 py-4 text-center shadow-lg">
                <h2 className="text-2xl font-semibold text-white">Ready to explore your data?</h2>
                <p className="mt-2 text-sm text-white/70">
                  {datasetType === 'default' 
                    ? 'Ask a question about the Titanic dataset below or pick a quick prompt to get started.'
                    : `Ask a question about your ${uploadedFileName} dataset below.`
                  }
                </p>
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
                  <div className="group relative max-w-[90%] rounded-2xl border border-black/10 bg-white/90 px-4 py-3 text-sm text-black shadow">
                    <p className="mb-1 text-[11px] uppercase tracking-wide text-neutral-500">Agent</p>
                    <div
                      className="leading-relaxed"
                      dangerouslySetInnerHTML={renderMarkdown(item.answer)}
                    />
                    <button
                      onClick={() => copyToClipboard(item.answer, index)}
                      className="absolute right-2 top-2 rounded-lg bg-white/90 p-1.5 opacity-0 shadow-sm transition-opacity hover:bg-neutral-100 group-hover:opacity-100"
                      title="Copy message"
                    >
                      {copiedMessageIndex === index ? (
                        <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="h-4 w-4 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      )}
                    </button>
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
            <div className="group relative max-w-[90%] rounded-2xl border border-black/10 bg-white/90 px-4 py-3 text-sm text-black shadow">
              <p className="mb-1 text-[11px] uppercase tracking-wide text-neutral-500">Agent</p>
              <div dangerouslySetInnerHTML={renderMarkdown(answer)} />
              <button
                onClick={() => copyToClipboard(answer, 'single')}
                className="absolute right-2 top-2 rounded-lg bg-white/90 p-1.5 opacity-0 shadow-sm transition-opacity hover:bg-neutral-100 group-hover:opacity-100"
                title="Copy message"
              >
                {copiedMessageIndex === 'single' ? (
                  <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="h-4 w-4 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                )}
              </button>
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
