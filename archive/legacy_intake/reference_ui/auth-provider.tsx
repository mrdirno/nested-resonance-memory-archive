"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { useRouter } from "next/navigation"

interface User {
  id: string
  name: string
  email: string
  avatar: string
}

interface AuthContextType {
  user: User | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (name: string, email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  loading: boolean
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()
  const router = useRouter()

  useEffect(() => {
    const getUser = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (session?.user) {
        const { data: userData } = await supabase.from("users").select("*").eq("id", session.user.id).single()

        if (userData) {
          setUser({
            id: userData.id,
            name: userData.name,
            email: userData.email,
            avatar: userData.avatar_url || "/default-avatar.png",
          })
        }
      }

      setLoading(false)
    }

    getUser()

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "SIGNED_IN" && session) {
        const { data: userData } = await supabase.from("users").select("*").eq("id", session.user.id).single()

        if (userData) {
          setUser({
            id: userData.id,
            name: userData.name,
            email: userData.email,
            avatar: userData.avatar_url || "/default-avatar.png",
          })
        }
      } else if (event === "SIGNED_OUT") {
        setUser(null)
      }

      router.refresh()
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [supabase, router])

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) {
      throw error
    }

    setLoading(false)
  }

  const signUp = async (name: string, email: string, password: string) => {
    setLoading(true)

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: name,
        },
      },
    })

    if (error) {
      throw error
    }

    setLoading(false)
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, signIn, signUp, signOut, loading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
