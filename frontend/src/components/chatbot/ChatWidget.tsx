'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Send, Bot, User, Loader2 } from 'lucide-react'

const API_BASE = '/api/chatbot'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
}

function getSessionId(): string {
  if (typeof window === 'undefined') return ''
  let id = localStorage.getItem('chatbot_session_id')
  if (!id) {
    id = crypto.randomUUID().replace(/-/g, '').slice(0, 32)
    localStorage.setItem('chatbot_session_id', id)
  }
  return id
}

function uid(): string {
  return Math.random().toString(36).slice(2, 10)
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [quickReplies, setQuickReplies] = useState<string[]>([])
  const [isOnline, setIsOnline] = useState(true)
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }))
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(r => r.json())
      .then(data => {
        setIsOnline(data.is_active)
        setQuickReplies(data.quick_replies || [])
        if (messages.length === 0 && data.welcome_message) {
          setMessages([{
            id: uid(),
            role: 'assistant',
            content: data.welcome_message,
          }])
        }
      })
      .catch(() => setIsOnline(false))
  }, [])

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300)
  }, [isOpen])

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isLoading) return

    const userMsg: Message = { id: uid(), role: 'user', content: trimmed }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(`${API_BASE}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          session_id: getSessionId(),
        }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()

      if (data.session_id) {
        localStorage.setItem('chatbot_session_id', data.session_id)
      }

      setMessages(prev => [...prev, {
        id: uid(),
        role: 'assistant',
        content: data.reply,
      }])

      if (data.quick_replies?.length) {
        setQuickReplies(data.quick_replies)
      }
    } catch {
      setMessages(prev => [...prev, {
        id: uid(),
        role: 'assistant',
        content: 'متأسفم، مشکلی پیش آمد. لطفاً دوباره تلاش کنید. 🙏',
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const bubbleVariants = {
    hidden: { opacity: 0, y: 12, scale: 0.95 },
    visible: { opacity: 1, y: 0, scale: 1 },
  }

  return (
    <div className="fixed bottom-6 right-6 z-[150]" dir="rtl">
      {/* ── Panel ──────────────────────────────────────────── */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="panel"
            initial={{ opacity: 0, y: 24, scale: 0.92 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.92 }}
            transition={{ type: 'spring', stiffness: 340, damping: 26 }}
            className="absolute bottom-[72px] right-0 w-[380px] max-w-[calc(100vw-32px)] h-[520px] max-h-[calc(100vh-120px)] rounded-[20px] overflow-hidden flex flex-col"
            style={{
              background: 'rgba(255,255,255,0.92)',
              backdropFilter: 'blur(20px) saturate(180%)',
              WebkitBackdropFilter: 'blur(20px) saturate(180%)',
              border: '1px solid rgba(255,255,255,0.4)',
              boxShadow: '0 24px 80px -12px rgba(0,0,0,0.18), 0 0 0 1px rgba(0,0,0,0.04)',
            }}
          >
            {/* Header */}
            <div
              className="relative px-5 py-4 flex items-center gap-3 shrink-0"
              style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)' }}
            >
              <div className="w-9 h-9 rounded-full bg-white/15 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-bold text-sm">دستیار فروش آتی فرزام</h3>
                <p className="text-emerald-300 text-xs mt-0.5">
                  {isOnline ? 'آنلاین — آماده پاسخگویی' : 'آفلاین'}
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                aria-label="بستن چت"
              >
                <X className="w-4 h-4 text-white" />
              </button>
              <div className="absolute bottom-0 left-0 right-0 h-[3px]"
                style={{ background: 'linear-gradient(90deg, #10b981, #059669, #f59e0b)' }}
              />
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3" style={{ overscrollBehavior: 'contain' }}>
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  variants={bubbleVariants}
                  initial="hidden"
                  animate="visible"
                  transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                  className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-7 h-7 rounded-full shrink-0 mt-1 flex items-center justify-center"
                      style={{ background: 'linear-gradient(135deg, #0f172a, #1e3a5f)' }}>
                      <Bot className="w-3.5 h-3.5 text-white" />
                    </div>
                  )}
                  <div
                    className={`max-w-[82%] px-4 py-2.5 text-[13px] leading-relaxed ${
                      msg.role === 'user'
                        ? 'rounded-[16px_16px_4px_16px] text-white'
                        : 'rounded-[16px_16px_16px_4px] text-[var(--text-heading)]'
                    }`}
                    style={
                      msg.role === 'user'
                        ? { background: 'linear-gradient(135deg, #059669, #10b981)' }
                        : {
                            background: 'rgba(255,255,255,0.85)',
                            border: '1px solid rgba(0,0,0,0.06)',
                            boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
                          }
                    }
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-7 h-7 rounded-full bg-emerald-100 shrink-0 mt-1 flex items-center justify-center">
                      <User className="w-3.5 h-3.5 text-emerald-700" />
                    </div>
                  )}
                </motion.div>
              ))}

              {/* Typing indicator */}
              <AnimatePresence>
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    className="flex gap-2 items-start"
                  >
                    <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center"
                      style={{ background: 'linear-gradient(135deg, #0f172a, #1e3a5f)' }}>
                      <Bot className="w-3.5 h-3.5 text-white" />
                    </div>
                    <div className="rounded-[16px_16px_16px_4px] px-4 py-3 flex gap-1.5"
                      style={{
                        background: 'rgba(255,255,255,0.85)',
                        border: '1px solid rgba(0,0,0,0.06)',
                      }}
                    >
                      {[0, 1, 2].map(i => (
                        <motion.span
                          key={i}
                          className="w-2 h-2 rounded-full bg-[#94a3b8]"
                          animate={{ y: [0, -6, 0] }}
                          transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            delay: i * 0.15,
                            ease: 'easeInOut',
                          }}
                        />
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div ref={endRef} />
            </div>

            {/* Quick Replies */}
            {quickReplies.length > 0 && !isLoading && (
              <div className="px-4 pb-2 flex flex-wrap gap-1.5 shrink-0">
                {quickReplies.map((qr, i) => (
                  <motion.button
                    key={qr}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => sendMessage(qr)}
                    className="px-3 py-1.5 text-xs font-medium rounded-full transition-all duration-200 cursor-pointer"
                    style={{
                      background: 'rgba(16,185,129,0.06)',
                      border: '1px solid rgba(16,185,129,0.2)',
                      color: '#059669',
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'linear-gradient(135deg, #059669, #10b981)'
                      e.currentTarget.style.color = '#fff'
                      e.currentTarget.style.borderColor = 'transparent'
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'rgba(16,185,129,0.06)'
                      e.currentTarget.style.color = '#059669'
                      e.currentTarget.style.borderColor = 'rgba(16,185,129,0.2)'
                    }}
                  >
                    {qr}
                  </motion.button>
                ))}
              </div>
            )}

            {/* Input */}
            <form
              onSubmit={handleSubmit}
              className="px-4 py-3 flex items-center gap-2 shrink-0"
              style={{ borderTop: '1px solid rgba(0,0,0,0.06)', background: 'rgba(248,250,252,0.6)' }}
            >
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="پیام خود را بنویسید…"
                disabled={isLoading || !isOnline}
                className="flex-1 px-4 py-2.5 rounded-2xl text-sm bg-white outline-none transition-all duration-200 placeholder:text-[#94a3b8] disabled:opacity-50"
                style={{
                  border: '1px solid #e2e8f0',
                  fontFamily: "'Vazirmatn', system-ui, sans-serif",
                }}
                onFocus={e => {
                  e.currentTarget.style.borderColor = '#10b981'
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(16,185,129,0.12)'
                }}
                onBlur={e => {
                  e.currentTarget.style.borderColor = '#e2e8f0'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              />
              <motion.button
                type="submit"
                disabled={!input.trim() || isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.92 }}
                className="w-10 h-10 rounded-full flex items-center justify-center text-white shrink-0 transition-opacity disabled:opacity-40"
                style={{ background: 'linear-gradient(135deg, #059669, #10b981)' }}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4 rotate-180" />
                )}
              </motion.button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Toggle Button ──────────────────────────────────── */}
      <div className="relative">
        {/* Pulse rings */}
        {!isOpen && (
          <>
            <span className="absolute inset-0 rounded-full animate-ping opacity-20"
              style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }} />
            <span className="absolute -inset-1 rounded-full"
              style={{
                background: 'linear-gradient(135deg, #10b981, #059669)',
                opacity: 0.15,
                animation: 'breathe 2s ease-in-out infinite',
              }} />
          </>
        )}
        <motion.button
          onClick={() => setIsOpen(v => !v)}
          whileHover={{ scale: 1.08, y: -2 }}
          whileTap={{ scale: 0.92 }}
          className="relative w-14 h-14 rounded-full flex items-center justify-center text-white"
          style={{
            background: isOpen
              ? 'linear-gradient(135deg, #ef4444, #dc2626)'
              : 'linear-gradient(135deg, #0f172a, #1e3a5f)',
            boxShadow: isOpen
              ? '0 8px 32px rgba(239,68,68,0.35)'
              : '0 8px 32px rgba(30,58,95,0.35)',
          }}
          aria-label={isOpen ? 'بستن چت' : 'باز کردن چت'}
        >
          <AnimatePresence mode="wait" initial={false}>
            {isOpen ? (
              <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.2 }}>
                <X className="w-6 h-6" />
              </motion.div>
            ) : (
              <motion.div key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.2 }}>
                <MessageCircle className="w-6 h-6" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>
      </div>
    </div>
  )
}
