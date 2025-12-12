import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface LookbookItem {
    product_id: number
    product_name: string
    brand_name: string
    price_from?: number
    image_url?: string
}

interface LookbookState {
    items: LookbookItem[]
    addToLookbook: (product: any) => void
    removeFromLookbook: (productId: number) => void
    isInLookbook: (productId: number) => boolean
}

export const useLookbookStore = create<LookbookState>()(
    persist(
        (set, get) => ({
            items: [],
            addToLookbook: (product) => set((state) => {
                if (state.items.some(i => i.product_id === product.product_id)) {
                    return state
                }
                return { items: [...state.items, product] }
            }),
            removeFromLookbook: (productId) => set((state) => ({
                items: state.items.filter(i => i.product_id !== productId)
            })),
            isInLookbook: (productId) => get().items.some(i => i.product_id === productId)
        }),
        {
            name: 'shopping-assistant-lookbook',
        }
    )
)
