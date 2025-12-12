import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

export interface CartItem {
    product_id: number
    product_name: string
    price: number
    quantity: number
    image_url?: string
    brand_name: string
}

interface CartState {
    items: CartItem[]
    addToCart: (product: any) => void
    removeFromCart: (productId: number) => void
    updateQuantity: (productId: number, quantity: number) => void
    clearCart: () => void
    totalItems: () => number
    totalPrice: () => number
    checkout: (customerId: number, token: string) => Promise<any>
}

export const useCartStore = create<CartState>()(
    persist(
        (set, get) => ({
            items: [],
            addToCart: (product) => set((state) => {
                const existing = state.items.find((item) => item.product_id === product.product_id)
                if (existing) {
                    return {
                        items: state.items.map((item) =>
                            item.product_id === product.product_id
                                ? { ...item, quantity: item.quantity + 1 }
                                : item
                        ),
                    }
                }
                return {
                    items: [...state.items, {
                        product_id: product.product_id,
                        product_name: product.product_name,
                        price: product.price_from || 0,
                        quantity: 1,
                        brand_name: product.brand_name
                    }],
                }
            }),
            removeFromCart: (productId) => set((state) => ({
                items: state.items.filter((item) => item.product_id !== productId),
            })),
            updateQuantity: (productId, quantity) => set((state) => ({
                items: state.items.map((item) =>
                    item.product_id === productId ? { ...item, quantity } : item
                ),
            })),
            clearCart: () => set({ items: [] }),
            totalItems: () => get().items.reduce((acc, item) => acc + item.quantity, 0),
            totalPrice: () => get().items.reduce((acc, item) => acc + (item.price || 0) * item.quantity, 0),
            checkout: async (customerId, token) => {
                const items = get().items
                if (items.length === 0) throw new Error("Cart is empty")

                // Mock SKU ID as product_id for now since we don't have SKU selection in UI yet
                const line_items = items.map(item => ({
                    sku_id: item.product_id, // TODO: Real SKU mapping
                    quantity: item.quantity,
                    unit_price: item.price || 0
                }))

                const payload = {
                    customer_id: customerId,
                    line_items,
                    payment_method: "Credit Card",
                    shipping_address: { "line1": "123 Main St", "city": "New York", "state": "NY" } // Mock address
                }

                const response = await axios.post('http://localhost:8000/api/orders', payload, {
                    headers: { Authorization: `Bearer ${token}` }
                })

                set({ items: [] })
                return response.data
            }
        }),
        {
            name: 'shopping-assistant-cart',
        }
    )
)
