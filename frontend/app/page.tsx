'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import ProductGrid from '@/components/ProductGrid'
import Header from '@/components/Header'
import { motion } from 'framer-motion'

export default function Home() {
  const [selectedProducts, setSelectedProducts] = useState<any[]>([])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            AI Shopping Assistant
          </h1>
          <p className="text-gray-600">
            Your personal shopping companion powered by multi-agent AI
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-1"
          >
            <div className="glass rounded-2xl p-6 h-[600px] flex flex-col">
              <ChatInterface onProductsUpdate={setSelectedProducts} />
            </div>
          </motion.div>

          {/* Product Grid */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="lg:col-span-2"
          >
            <ProductGrid products={selectedProducts} />
          </motion.div>
        </div>
      </main>
    </div>
  )
}

