'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import axios from 'axios'
import Header from '@/components/Header'
import { AlertCircle } from 'lucide-react'

export default function RegisterPage() {
    const router = useRouter()
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: ''
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await axios.post('http://localhost:8000/api/auth/register', formData)
            router.push('/login?registered=true')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            <Header />
            <main className="container mx-auto px-4 py-10 flex items-center justify-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass rounded-2xl p-8 w-full max-w-md"
                >
                    <h1 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Create Account
                    </h1>

                    {error && (
                        <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-4 flex items-center gap-2 text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input
                                type="email"
                                required
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                            <input
                                type="password"
                                required
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
                        >
                            {loading ? 'Creating Account...' : 'Sign Up'}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-sm text-gray-600">
                        Already have an account?{' '}
                        <Link href="/login" className="text-blue-600 hover:underline">
                            Sign in
                        </Link>
                    </p>
                </motion.div>
            </main>
        </div>
    )
}
