'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { ShoppingBag, Search, Menu, User, LogOut } from 'lucide-react'
import { motion } from 'framer-motion'
import { useCartStore } from '@/store/cartStore'
import { useAuthStore } from '@/store/authStore'

export default function Header() {
  const { totalItems } = useCartStore()
  const { user, logout } = useAuthStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            StyleAI
          </Link>
          {mounted && user && (
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
              <Link href="/" className="hover:text-blue-600 transition-colors">Chat</Link>
              <Link href="/lookbook" className="hover:text-blue-600 transition-colors">Lookbook</Link>
              <Link href="/orders" className="hover:text-blue-600 transition-colors">Orders</Link>
              <Link href="/returns" className="hover:text-blue-600 transition-colors">Returns</Link>
            </nav>
          )}
        </div>

        <div className="flex items-center gap-4">
          {mounted && user && (
            <>


              <Link href="/cart" className="p-2 hover:bg-gray-100 rounded-full transition-colors relative group">
                <ShoppingBag className="w-5 h-5 text-gray-600" />
                {totalItems() > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                    {totalItems()}
                  </span>
                )}
              </Link>
            </>
          )}

          {mounted && user ? (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 hidden sm:block">
                Hi, {user.first_name || user.email.split('@')[0]}
              </span>
              <button
                onClick={() => logout()}
                className="p-2 hover:bg-red-50 text-gray-600 hover:text-red-500 rounded-full transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            // Only show simple header or Sign In isn't needed here if we redirect? 
            // But redirect goes to /login, which has this header. 
            // On /login, user is null. We want to show NOTHING or just Logo? 
            // "Just provide login page."
            // If we are on /login, we might want to hide everything except logo.
            // But existing code showed "Sign In" link.
            // On /login page, having a "Sign In" link is redundant but harmless.
            // Hiding it is cleaner.
            // Let's keep it simple: Hide tabs/icons.
            <div className="flex items-center gap-2">
              {/* Optional: Add help/support link here if needed */}
            </div>
          )}

          {mounted && user && (
            <button className="md:hidden p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
