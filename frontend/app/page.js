"use client"

import Link from "next/link"
import Navbar from "./components/Navbar"

export default function Home() {
  return (
    <main className="min-h-screen bg-[var(--arena-black)]">
      <Navbar />

      <div className="max-w-4xl mx-auto px-6 py-24 text-center">
        <p className="font-display text-sm uppercase tracking-widest text-[var(--blood-red)] mb-4">
          AI-powered MMA intelligence
        </p>

        <h1 className="font-display text-6xl font-bold mb-6 leading-tight">
          KNOW THE FIGHT<br />BEFORE IT HAPPENS
        </h1>

        <p className="text-[var(--text-muted)] text-lg mb-12 max-w-xl mx-auto">
          Real fighter stats. Real fight history. Real predictions.
          No guessing, just data.
        </p>

        <div className="flex gap-4 justify-center">
          <Link
            href="/chat"
            className="px-8 py-3 bg-[var(--blood-red)] hover:bg-[var(--blood-red-dark)] font-display font-semibold uppercase tracking-wide rounded transition glow-red"
          >
            Ask FightIQ
          </Link>
          <Link
            href="/compare"
            className="px-8 py-3 border border-[var(--steel-gray)] hover:border-[var(--blood-red)] font-display font-semibold uppercase tracking-wide rounded transition"
          >
            Compare fighters
          </Link>
        </div>

        <div className="grid grid-cols-3 gap-6 mt-24">
          <div className="bg-[var(--arena-card)] border border-[var(--steel-gray)] rounded p-6 octagon-border">
            <p className="font-display text-3xl font-bold text-[var(--blood-red)] mb-1">2,241</p>
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide">Fighters tracked</p>
          </div>
          <div className="bg-[var(--arena-card)] border border-[var(--steel-gray)] rounded p-6 octagon-border">
            <p className="font-display text-3xl font-bold text-[var(--blood-red)] mb-1">7,177</p>
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide">Fights analyzed</p>
          </div>
          <div className="bg-[var(--arena-card)] border border-[var(--steel-gray)] rounded p-6 octagon-border">
            <p className="font-display text-3xl font-bold text-[var(--blood-red)] mb-1">75%</p>
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide">Model accuracy</p>
          </div>
        </div>
      </div>
    </main>
  )
}