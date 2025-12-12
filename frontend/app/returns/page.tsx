'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Header from '@/components/Header'
import { motion } from 'framer-motion'
import { RefreshCw, Package, ArrowLeft } from 'lucide-react'
import { API_URL } from '@/lib/config'

export default function ReturnsPage() {
  const { user, token } = useAuthStore()
  const router = useRouter()
  const [returns, setReturns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || !token) {
      router.push('/login')
      return
    }

    const fetchReturns = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/returns?customer_id=${user.customer_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setReturns(res.data)
      } catch (err) {
        console.error("Failed to fetch returns", err)
      } finally {
        setLoading(false)
      }
    }

    fetchReturns()
  }, [user, token, router])

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
            <RefreshCw className="w-8 h-8 text-blue-600" />
            My Returns
          </h1>

          {loading ? (
            <p>Loading returns...</p>
          ) : returns.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-gray-500 text-lg mb-4">No active return requests.</p>
              <button onClick={() => router.push('/orders')} className="text-blue-600 hover:underline">Go to Orders</button>
            </div>
          ) : (
            <div className="space-y-6">
              {returns.map((req) => (
                <div key={req.return_id} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                  <div className="flex flex-wrap justify-between items-start gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Return Requested</p>
                      <p className="font-medium">{new Date(req.requested_date).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Reason</p>
                      <p className="font-medium">{req.return_reason}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span className={`px-2 py-1 rounded-full text-xs font-bold ${req.return_status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                        req.return_status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                        {req.return_status}
                      </span>
                    </div>
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
