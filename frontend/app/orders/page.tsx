'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Header from '@/components/Header'
import { motion } from 'framer-motion'
import { Package, Truck, Clock, RefreshCw } from 'lucide-react'

interface OrderLineItem {
  sku_id: number
  quantity: number
  unit_price: number
  line_total: number
}

interface Order {
  order_id: number
  order_number: string
  order_date: string
  order_status: string
  total_amount: number
  line_items: OrderLineItem[] // Backend might not return line items in listing unless eager loaded?
}

export default function OrdersPage() {
  const { user, token } = useAuthStore()
  const router = useRouter()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || !token) {
      router.push('/login')
      return
    }

    const fetchOrders = async () => {
      try {
        // Backend endpoint implemented: GET /api/orders?customer_id=...
        // But main.py implementation was:
        // @app.get("/api/orders", response_model=List[OrderResponse])
        // async def get_orders(customer_id: int, db: Session = Depends(get_db)):
        // It requires customer_id as query param.
        const res = await axios.get(`http://localhost:8000/api/orders?customer_id=${user.customer_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setOrders(res.data)
      } catch (err) {
        console.error("Failed to fetch orders", err)
      } finally {
        setLoading(false)
      }
    }

    fetchOrders()
  }, [user, token, router])

  const handleReturn = async (orderId: number) => {
    // Navigate to return page with orderId
    // Or open a modal.
    // Requirement: "Once we click on return option then it should appear in return page."
    // Maybe navigate to /returns/new?order_id=...
    router.push(`/returns/new?order_id=${orderId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      <main className="container mx-auto px-4 py-10">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-8"
        >
          <h1 className="text-3xl font-bold mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center gap-3">
            <Package className="w-8 h-8 text-blue-600" />
            My Orders
          </h1>

          {loading ? (
            <p>Loading orders...</p>
          ) : orders.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-gray-500 text-lg mb-4">You haven't placed any orders yet.</p>
              <button onClick={() => router.push('/')} className="text-blue-600 hover:underline">Start Shopping</button>
            </div>
          ) : (
            <div className="space-y-6">
              {orders.map((order) => (
                <div key={order.order_id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                  <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Order Placed</p>
                      <p className="font-medium">{new Date(order.order_date).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Order Number</p>
                      <p className="font-medium">{order.order_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total</p>
                      <p className="font-bold text-blue-600">${order.total_amount}</p>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                      <Truck className="w-4 h-4" />
                      {order.order_status}
                    </div>
                  </div>

                  <div className="flex justify-end pt-4 border-t border-gray-100">
                    <button
                      onClick={() => handleReturn(order.order_id)}
                      className="flex items-center gap-2 text-gray-600 hover:text-red-600 text-sm font-medium transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Return Order
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
