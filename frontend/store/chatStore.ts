import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
    role: 'user' | 'assistant'
    content: string
    agent?: string
    data?: any
}

interface ChatState {
    messages: Message[]
    addMessage: (message: Message) => void
    setMessages: (messages: Message[]) => void
    clearMessages: () => void
}

export const useChatStore = create<ChatState>()(
    persist(
        (set) => ({
            messages: [
                {
                    role: 'assistant',
                    content: "Hi! I'm your AI shopping assistant. How can I help you today?",
                    agent: 'orchestrator'
                }
            ],
            addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
            setMessages: (messages) => set({ messages }),
            clearMessages: () => set({
                messages: [{
                    role: 'assistant',
                    content: "Hi! I'm your AI shopping assistant. How can I help you today?",
                    agent: 'orchestrator'
                }]
            })
        }),
        {
            name: 'shopping-assistant-chat',
        }
    )
)
