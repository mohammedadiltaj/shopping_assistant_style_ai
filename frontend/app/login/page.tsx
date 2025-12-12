'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import Header from '@/components/Header'
import { AlertCircle } from 'lucide-react'

export default function LoginPage() {
    const router = useRouter()
    const { login } = useAuthStore()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            // 1. Login to get token
            const loginRes = await axios.post('http://localhost:8000/api/auth/login', {
                email,
                password
            })

            const token = loginRes.data.access_token

            // 2. Mock getting user details (In a real app, we'd have a /me endpoint or decode token)
            // For now, let's just use the email and a placeholder ID or fetch customer by email if possible
            // But we don't have a "get me" endpoint yet. Let's assume we can fetch by email if we add that endpoint?
            // Or we can just store the token and fetch user data later. 
            // Actually, let's decode the token to get user_id if we have a decoder, or request the backend to return user info. 
            // Simplest for now: We won't fetch full user details immediately, just store token.
            // But authStore expects a user object. 

            // Let's decode the base64 payload manually
            const base64Url = token.split('.')[1]
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
            }).join(''))
            const payload = JSON.parse(jsonPayload)

            login(token, {
                customer_id: payload.user_id,
                email: payload.sub,
                first_name: 'User' // Placeholder until we fetch profile
            })

            router.push('/')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
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
                        Welcome Back
                    </h1>

                    {error && (
                        <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-4 flex items-center gap-2 text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                                placeholder="you@example.com"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/50"
                                placeholder="••••••••"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-sm text-gray-600">
                        Don't have an account?{' '}
                        <Link href="/register" className="text-blue-600 hover:underline">
                            Sign up
                        </Link>
                    </p>
                </motion.div>
            </main>
        </div>
    )
}
