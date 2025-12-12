'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { useChatStore, Message } from '@/store/chatStore'
import { useCartStore } from '@/store/cartStore'
import { useAuthStore } from '@/store/authStore'

interface ChatInterfaceProps {
  onProductsUpdate?: (products: any[]) => void
}

export default function ChatInterface({ onProductsUpdate }: ChatInterfaceProps) {
  const { messages, addMessage } = useChatStore()
  const { items, clearCart } = useCartStore()
  const { user } = useAuthStore()

  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Restore products from last message on mount
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage?.data?.products && onProductsUpdate) {
      onProductsUpdate(lastMessage.data.products)
    }
  }, []) // Run once on mount

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/api/agent/chat', {
        message: input,
        customer_id: user?.customer_id,
        context: {
          cart_items: items,
          page_context: window.location.pathname
        }
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        agent: response.data.agent_name,
        data: response.data.data
      }

      addMessage(assistantMessage)

      // Handle client-side actions based on agent response
      if (response.data.data?.clear_cart) {
        clearCart()
      }

      // Update products if search results
      if (response.data.data?.products && onProductsUpdate) {
        onProductsUpdate(response.data.data.products)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        agent: 'error'
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              <div className={`max-w-[80%] rounded-2xl px-4 py-2 ${message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
                }`}>
                <p className="text-sm cursor-text selection:bg-blue-200 selection:text-blue-900">{message.content}</p>
                {message.agent && message.agent !== 'orchestrator' && (
                  <p className="text-xs mt-1 opacity-70">
                    via {message.agent} agent
                  </p>
                )}
              </div>

              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-gray-600" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="bg-gray-100 rounded-2xl px-4 py-2">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything about products, styling, or orders..."
          className="flex-1 px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50 backdrop-blur-sm"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

