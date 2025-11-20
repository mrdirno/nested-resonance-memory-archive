"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Heart, Eye, Play } from "lucide-react"
import Link from "next/link"
import { mockShots } from "@/lib/mock-data"

export function FeaturedShots() {
  const featuredShots = mockShots.filter((shot) => shot.featured).slice(0, 6)

  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Featured Shots</h2>
          <p className="text-muted-foreground">Handpicked interactive experiences</p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/explore?filter=featured">View All</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {featuredShots.map((shot) => (
          <Card key={shot.id} className="group overflow-hidden hover:shadow-lg transition-all duration-300">
            <div className="relative aspect-video bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900">
              <img src={shot.thumbnail || "/placeholder.svg"} alt={shot.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Button size="sm" className="bg-white/90 text-black hover:bg-white">
                  <Play className="h-4 w-4 mr-2" />
                  View Shot
                </Button>
              </div>
              <Badge className="absolute top-3 left-3 bg-purple-600 hover:bg-purple-600">Featured</Badge>
            </div>

            <CardContent className="p-4 space-y-3">
              <div className="space-y-2">
                <h3 className="font-semibold line-clamp-1">{shot.title}</h3>
                <p className="text-sm text-muted-foreground line-clamp-2">{shot.description}</p>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={shot.author.avatar || "/placeholder.svg"} />
                    <AvatarFallback>{shot.author.name.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <span className="text-sm font-medium">{shot.author.name}</span>
                </div>

                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Heart className="h-4 w-4" />
                    <span>{shot.likes}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Eye className="h-4 w-4" />
                    <span>{shot.views}</span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-1">
                {shot.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  )
}
