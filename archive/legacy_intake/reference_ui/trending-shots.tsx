"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Eye, TrendingUp, Play } from "lucide-react"
import Link from "next/link"
import { mockShots } from "@/lib/mock-data"

export function TrendingShots() {
  const trendingShots = mockShots.sort((a, b) => b.views - a.views).slice(0, 8)

  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TrendingUp className="h-6 w-6 text-orange-500" />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Trending Now</h2>
            <p className="text-muted-foreground">Most viewed shots this week</p>
          </div>
        </div>
        <Button variant="outline" asChild>
          <Link href="/trending">View All</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {trendingShots.map((shot, index) => (
          <Card key={shot.id} className="group overflow-hidden hover:shadow-lg transition-all duration-300">
            <div className="relative aspect-video bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900 dark:to-red-900">
              <img src={shot.thumbnail || "/placeholder.svg"} alt={shot.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Button size="sm" className="bg-white/90 text-black hover:bg-white">
                  <Play className="h-4 w-4 mr-2" />
                  View
                </Button>
              </div>
              <Badge className="absolute top-2 left-2 bg-orange-600 hover:bg-orange-600 text-xs">#{index + 1}</Badge>
            </div>

            <CardContent className="p-3 space-y-2">
              <h3 className="font-semibold text-sm line-clamp-1">{shot.title}</h3>

              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-1">
                  <Avatar className="h-4 w-4">
                    <AvatarImage src={shot.author.avatar || "/placeholder.svg"} />
                    <AvatarFallback>{shot.author.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <span className="text-muted-foreground">{shot.author.name}</span>
                </div>

                <div className="flex items-center space-x-2 text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Eye className="h-3 w-3" />
                    <span>{shot.views}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  )
}
