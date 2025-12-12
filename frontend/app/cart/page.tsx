'use client'

import Header from '@/components/Header'
import { useCartStore } from '@/store/cartStore'
import { useAuthStore } from '@/store/authStore'
import { motion } from 'framer-motion'
import { Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function CartPage() {
    const { items, removeFromCart, checkout, totalPrice } = useCartStore()
    const { user, token } = useAuthStore()
    const router = useRouter()
    const [loading, setLoading] = useState(false)

    const handleCheckout = async () => {
        if (!user || !token) {
            router.push('/login')
            return
        }

        setLoading(true)
        try {
            await checkout(user.customer_id, token)
            router.push('/orders')
        } catch (err) {
            console.error('Checkout failed', err)
            alert('Checkout failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

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
                    <h1 className="text-3xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Shopping Cart
                    </h1>

                    {items.length === 0 ? (
                        <p className="text-gray-500 text-lg">Your cart is empty.</p>
                    ) : (
                        <>
                            <div className="space-y-4 mb-8">
                                {items.map((item) => (
                                    <div key={item.product_id} className="flex items-center justify-between bg-white p-4 rounded-xl shadow-sm">
                                        <div>
                                            <h3 className="font-semibold text-lg">{item.product_name}</h3>
                                            <p className="text-gray-500">{item.brand_name}</p>
                                            <p className="text-sm text-blue-600 font-medium">${(item.price || 0).toFixed(2)} x {item.quantity}</p>
                                        </div>
                                        <button
                                            onClick={() => removeFromCart(item.product_id)}
                                            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                ))}
                            </div>

                            <div className="border-t pt-6 flex flex-col items-end">
                                <div className="text-2xl font-bold mb-4">
                                    Total: ${totalPrice().toFixed(2)}
                                </div>
                                <button
                                    onClick={handleCheckout}
                                    disabled={loading}
                                    className="px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium text-lg disabled:opacity-50"
                                >
                                    {loading ? 'Processing...' : 'Checkout'}
                                </button>
                            </div>
                        </>
                    )}
                </motion.div>
            </main>
        </div>
    )
}
