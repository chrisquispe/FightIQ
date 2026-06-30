"use client"

import Link from "next/link"

export default function Navbar() {
  return (
    <nav className="border-b border-[var(--steel-gray)] bg-[var(--arena-dark)] sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-display text-2xl font-bold tracking-wider">
          FIGHT<span className="text-[var(--blood-red)]">IQ</span>
        </Link>
        <div className="flex gap-8 font-display text-sm uppercase tracking-widest">
          <Link href="/chat" className="hover:text-[var(--blood-red)] transition">Chat</Link>
          <Link href="/compare" className="hover:text-[var(--blood-red)] transition">Compare</Link>
          <Link href="/predict" className="hover:text-[var(--blood-red)] transition">Predict</Link>
        </div>
      </div>
    </nav>
  )
}