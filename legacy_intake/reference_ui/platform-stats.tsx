"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Users, FileText, Trophy, Heart } from "lucide-react"
import { motion } from "framer-motion"

const stats = [
  {
    icon: Users,
    label: "Active Creators",
    value: "12,543",
    change: "+12%",
    color: "text-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900/20",
  },
  {
    icon: FileText,
    label: "Shots Created",
    value: "45,231",
    change: "+23%",
    color: "text-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/20",
  },
  {
    icon: Trophy,
    label: "Challenges Won",
    value: "1,234",
    change: "+8%",
    color: "text-yellow-600",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/20",
  },
  {
    icon: Heart,
    label: "Total Likes",
    value: "234,567",
    change: "+15%",
    color: "text-red-600",
    bgColor: "bg-red-100 dark:bg-red-900/20",
  },
]

export function PlatformStats() {
  return (
    <section className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold tracking-tight">Platform Statistics</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Join a thriving community of creators and discover amazing interactive experiences
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <Card className="hover:shadow-lg transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                    <div className="flex items-center space-x-2">
                      <p className="text-2xl font-bold">{stat.value}</p>
                      <span className="text-sm text-green-600 font-medium">{stat.change}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
