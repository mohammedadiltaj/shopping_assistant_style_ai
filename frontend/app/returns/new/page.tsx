'use client'

import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useRouter, useSearchParams } from 'next/navigation'
import axios from 'axios'
import Header from '@/components/Header'
import { motion } from 'framer-motion'
import { ArrowLeft, AlertCircle } from 'lucide-react'

export default function NewReturnPage() {
    const { user, token } = useAuthStore()
    const router = useRouter()
    const searchParams = useSearchParams()
    const orderId = searchParams.get('order_id')

    const [reason, setReason] = useState('Size doesn\'t fit')
    const [notes, setNotes] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!user || !token) return

        setLoading(true)
        try {
            await axios.post('http://localhost:8000/api/returns', {
                order_id: Number(orderId),
                return_reason: reason,
                notes: notes
            }, {
                headers: { Authorization: `Bearer ${token}` }
            })
            router.push('/returns')
        } catch (err) {
            console.error("Return request failed", err)
            setError("Failed to submit return request.")
        } finally {
            setLoading(false)
        }
    }

    if (!orderId) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p>Invalid Order ID</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            <Header />
            <main className="container mx-auto px-4 py-10 flex justify-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass rounded-2xl p-8 w-full max-w-lg"
                >
                    <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-500 hover:text-gray-800 mb-6">
                        <ArrowLeft className="w-4 h-4" /> Back
                    </button>

                    <h1 className="text-2xl font-bold mb-6">Request Return</h1>

                    {error && (
                        <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-4 flex items-center gap-2 text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Return</label>
                            <select
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                            >
                                <option>Size doesn't fit</option>
                                <option>Color not as expected</option>
                                <option>Quality issues</option>
                                <option>Changed mind</option>
                                <option>Defective item</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
                            <textarea
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50 min-h-[100px]"
                                placeholder="Tell us more about the issue..."
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
                        >
                            {loading ? 'Submitting...' : 'Submit Request'}
                        </button>
                    </form>
                </motion.div>
            </main>
        </div>
    )
}
