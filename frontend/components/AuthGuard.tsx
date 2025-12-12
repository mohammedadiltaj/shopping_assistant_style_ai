'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useRouter, usePathname } from 'next/navigation'

const PUBLIC_PATHS = ['/login', '/register']

export default function AuthGuard({ children }: { children: React.ReactNode }) {
    const { user } = useAuthStore()
    const router = useRouter()
    const pathname = usePathname()
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    useEffect(() => {
        if (!mounted) return

        // If user is NOT logged in and trying to access a restricted page
        if (!user && !PUBLIC_PATHS.includes(pathname)) {
            router.push('/login')
        }

        // If user IS logged in and trying to access login/register, redirect to home
        if (user && PUBLIC_PATHS.includes(pathname)) {
            router.push('/')
        }
    }, [user, pathname, router, mounted])

    if (!mounted) {
        return null
    }

    // Hide protected content while redirecting
    if (!user && !PUBLIC_PATHS.includes(pathname)) {
        return null
    }

    return <>{children}</>
}
