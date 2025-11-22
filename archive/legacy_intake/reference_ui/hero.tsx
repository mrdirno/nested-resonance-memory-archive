"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Play, Sparkles } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 dark:from-purple-950/20 dark:via-blue-950/20 dark:to-indigo-950/20">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5" />

      <div className="container mx-auto px-4 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <div className="space-y-4">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-medium">
                <Sparkles className="h-4 w-4 mr-2" />
                Interactive HTML Showcase
              </div>

              <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                Create, Share,{" "}
                <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Inspire
                </span>
              </h1>

              <p className="text-xl text-muted-foreground max-w-lg">
                Upload your interactive HTML creations, discover amazing projects from the community, and participate in
                creative challenges.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" asChild className="group">
                <Link href="/upload">
                  Start Creating
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>

              <Button size="lg" variant="outline" asChild className="group">
                <Link href="/explore">
                  <Play className="mr-2 h-4 w-4" />
                  Explore Shots
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 pt-8 border-t">
              <div>
                <div className="text-2xl font-bold">10K+</div>
                <div className="text-sm text-muted-foreground">Shots Created</div>
              </div>
              <div>
                <div className="text-2xl font-bold">5K+</div>
                <div className="text-sm text-muted-foreground">Creators</div>
              </div>
              <div>
                <div className="text-2xl font-bold">50+</div>
                <div className="text-sm text-muted-foreground">Challenges</div>
              </div>
            </div>
          </motion.div>

          {/* Visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 border">
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>

                <div className="space-y-3">
                  <div className="h-4 bg-gradient-to-r from-purple-200 to-blue-200 dark:from-purple-800 dark:to-blue-800 rounded" />
                  <div className="h-4 bg-gradient-to-r from-blue-200 to-indigo-200 dark:from-blue-800 dark:to-indigo-800 rounded w-3/4" />
                  <div className="h-4 bg-gradient-to-r from-indigo-200 to-purple-200 dark:from-indigo-800 dark:to-purple-800 rounded w-1/2" />
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <div className="h-20 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 rounded-lg" />
                  <div className="h-20 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900 dark:to-indigo-900 rounded-lg" />
                </div>
              </div>
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-purple-500 rounded-full animate-bounce" />
            <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-blue-500 rounded-full animate-pulse" />
          </motion.div>
        </div>
      </div>
    </section>
  )
}
