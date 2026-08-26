"use client"

import { useState } from "react"
import Navbar from "../components/Navbar"
import ReactMarkdown from "react-markdown"

export default function PredictPage() {
  const [name1, setName1] = useState("")
  const [name2, setName2] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handlePredict() {
    if (!name1.trim() || !name2.trim()) return
    setLoading(true)
    setResult(null)

    // "http://localhost:8000/chat" - This is for local testing
    const response = await fetch("http://3.133.95.6:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: `Who would win between ${name1} and ${name2}? Give me the win probability.`
      })
    })

    const data = await response.json()
    setResult(data.answer)
    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-[var(--arena-black)]">
      <Navbar />

      <div className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="font-display text-4xl font-bold mb-2 text-center">
          PREDICT THE <span className="text-[var(--blood-red)]">OUTCOME</span>
        </h1>
        <p className="text-[var(--text-muted)] text-center mb-10 font-display uppercase text-sm tracking-widest">
          Powered by a trained machine learning model
        </p>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <input
            type="text"
            value={name1}
            onChange={(e) => setName1(e.target.value)}
            placeholder="Fighter one"
            className="px-5 py-3 rounded bg-[var(--arena-card)] border border-[var(--steel-gray)] text-white placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--blood-red)] transition text-center"
          />
          <input
            type="text"
            value={name2}
            onChange={(e) => setName2(e.target.value)}
            placeholder="Fighter two"
            className="px-5 py-3 rounded bg-[var(--arena-card)] border border-[var(--steel-gray)] text-white placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--blood-red)] transition text-center"
          />
        </div>

        <div className="flex justify-center mb-10">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="px-10 py-3 bg-[var(--blood-red)] hover:bg-[var(--blood-red-dark)] disabled:opacity-40 font-display font-semibold uppercase tracking-wide rounded transition glow-red"
          >
            {loading ? "Calculating..." : "Predict winner"}
          </button>
        </div>

        {result && (
          <div className="bg-[var(--arena-card)] border border-[var(--steel-gray)] rounded p-6 octagon-border">
            <p className="text-[10px] font-display uppercase tracking-widest text-[var(--blood-red)] mb-3">
              Model prediction
            </p>
            <div className="leading-relaxed prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{result}</ReactMarkdown>
            </div>
          </div>
        )}

        <p className="text-[var(--text-muted)] text-xs text-center mt-8">
          Predictions based on height, reach, and win rate differences. Model trained on 7,019 historical fights. 75% test accuracy.
        </p>
      </div>
    </main>
  )
}