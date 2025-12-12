'use client'

import { useLookbookStore } from '@/store/lookbookStore'
import Header from '@/components/Header'
import { motion, AnimatePresence } from 'framer-motion'
import { Trash2, Heart } from 'lucide-react'

export default function LookbookPage() {
  const { items, removeFromLookbook } = useLookbookStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      <main className="container mx-auto px-4 py-10">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="glass rounded-2xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <Heart className="w-8 h-8 text-pink-500 fill-pink-500" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              My Lookbook
            </h1>
          </div>

          {items.length === 0 ? (
            <p className="text-gray-500 text-lg">Your lookbook is empty. Heart items to add them here!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AnimatePresence>
                {items.map((item) => (
                  <motion.div
                    key={item.product_id}
                    layout
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="bg-white rounded-xl overflow-hidden shadow-lg p-4"
                  >
                    <div className="h-40 bg-gray-100 rounded-lg mb-4 flex items-center justify-center">
                      <span className="text-3xl font-bold text-gray-300">{item.brand_name.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800 line-clamp-1">{item.product_name}</h3>
                      <p className="text-sm text-gray-500 mb-3">{item.brand_name}</p>
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-blue-600">${item.price_from?.toFixed(2)}</span>
                        <button
                          onClick={() => removeFromLookbook(item.product_id)}
                          className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                          title="Remove from Lookbook"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}

