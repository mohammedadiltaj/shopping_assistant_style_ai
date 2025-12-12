'use client'

import { motion } from 'framer-motion'
import { ShoppingCart, Star } from 'lucide-react'
import Image from 'next/image'

interface Product {
  product_id: number
  product_name: string
  brand_name: string
  product_type?: string
  price_from?: number
  rating?: number
}

interface ProductGridProps {
  products: Product[]
}

import { useCartStore } from '@/store/cartStore'
import { useLookbookStore } from '@/store/lookbookStore'
import { Heart } from 'lucide-react'

export default function ProductGrid({ products }: ProductGridProps) {
  const { addToCart } = useCartStore()
  const { addToLookbook, isInLookbook, removeFromLookbook } = useLookbookStore()
  if (products.length === 0) {
    return (
      <div className="glass rounded-2xl p-12 text-center">
        <p className="text-gray-500 text-lg">
          Start a conversation to see product recommendations!
        </p>
      </div>
    )
  }

  return (
    <div className="glass rounded-2xl p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        Recommended Products
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product, index) => (
          <motion.div
            key={product.product_id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow group"
          >
            {/* Product Image Placeholder */}
            <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 group-hover:scale-110 transition-transform duration-300"></div>
              <span className="text-4xl font-bold text-gray-300 z-10">
                {product.brand_name.charAt(0)}
              </span>
            </div>

            {/* Product Info */}
            <div className="p-4">
              <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                {product.product_name}
              </h3>
              <p className="text-sm text-gray-500 mb-2">{product.brand_name}</p>

              <div className="flex items-center justify-between">
                <div>
                  {product.price_from && (
                    <p className="text-lg font-bold text-blue-600">
                      ${product.price_from.toFixed(2)}
                    </p>
                  )}
                  {product.rating && (
                    <div className="flex items-center gap-1 mt-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm text-gray-600">{product.rating}</span>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => isInLookbook(product.product_id) ? removeFromLookbook(product.product_id) : addToLookbook(product)}
                  className={`p-2 rounded-lg transition-colors mr-2 ${isInLookbook(product.product_id)
                      ? 'bg-pink-50 text-pink-500 hover:bg-pink-100'
                      : 'bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-600'
                    }`}
                >
                  <Heart className={`w-5 h-5 ${isInLookbook(product.product_id) ? 'fill-current' : ''}`} />
                </button>
                <button
                  onClick={() => addToCart(product)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <ShoppingCart className="w-4 h-4" />
                  <span className="text-sm">Add</span>
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

