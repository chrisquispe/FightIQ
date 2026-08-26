"use client"

import { useState } from "react"
import Navbar from "../components/Navbar"
import ReactMarkdown from "react-markdown"


export default function ChatPage() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    if (!question.trim()) return
    setLoading(true)
    setAnswer("")
    setSources([])

    // "http://localhost:8000/chat" - This is for local testing
    const response = await fetch("http://3.133.95.6:8000/chat", { 
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
    })

    const data = await response.json()
    setAnswer(data.answer)
    setSources(data.sources || [])
    setLoading(false)
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <main className="min-h-screen bg-[var(--arena-black)]">
      <Navbar />

      <div className="max-w-2xl mx-auto px-6 py-16">
        <h1 className="font-display text-4xl font-bold mb-2 text-center">
          ASK THE <span className="text-[var(--blood-red)]">EXPERT</span>
        </h1>
        <p className="text-[var(--text-muted)] text-center mb-10 font-display uppercase text-sm tracking-widest">
          Real fight data. Zero guesswork.
        </p>

        <div className="flex gap-3 mb-8">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="How did Islam beat Oliveira?"
            className="flex-1 px-5 py-3 rounded bg-[var(--arena-card)] border border-[var(--steel-gray)] text-white placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--blood-red)] transition"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-8 py-3 bg-[var(--blood-red)] hover:bg-[var(--blood-red-dark)] disabled:opacity-40 font-display font-semibold uppercase tracking-wide rounded transition glow-red"
          >
            {loading ? "..." : "Ask"}
          </button>
        </div>

        {answer && (
          <div className="bg-[var(--arena-card)] border border-[var(--steel-gray)] rounded p-6 mb-6 octagon-border">
            <p className="text-[10px] font-display uppercase tracking-widest text-[var(--blood-red)] mb-3">
              FightIQ says
            </p>
            <div className="leading-relaxed prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{answer}</ReactMarkdown>
            </div>
          </div>
        )}

        {sources.length > 0 && (
          <div>
            <p className="text-[10px] font-display uppercase tracking-widest text-[var(--text-muted)] mb-3">
              Sourced from
            </p>
            <div className="space-y-2">
              {sources.map((source, i) => (
                <div key={i} className="text-sm text-[var(--text-muted)] bg-[var(--arena-dark)] border border-[var(--steel-gray)] rounded px-4 py-2">
                  {source}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}