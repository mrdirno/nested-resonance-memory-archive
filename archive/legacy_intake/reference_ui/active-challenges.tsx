"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Trophy, Users, Calendar, ArrowRight } from "lucide-react"
import Link from "next/link"
import { mockChallenges } from "@/lib/mock-data"

export function ActiveChallenges() {
  const activeChallenges = mockChallenges.filter((challenge) => challenge.status === "active").slice(0, 3)

  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Trophy className="h-6 w-6 text-yellow-500" />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Active Challenges</h2>
            <p className="text-muted-foreground">Join the community and win prizes</p>
          </div>
        </div>
        <Button variant="outline" asChild>
          <Link href="/challenges">View All</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {activeChallenges.map((challenge) => (
          <Card key={challenge.id} className="group hover:shadow-lg transition-all duration-300">
            <div className="relative aspect-video bg-gradient-to-br from-yellow-100 to-orange-100 dark:from-yellow-900 dark:to-orange-900">
              <img
                src={challenge.thumbnail || "/placeholder.svg"}
                alt={challenge.title}
                className="w-full h-full object-cover rounded-t-lg"
              />
              <Badge className="absolute top-3 right-3 bg-yellow-600 hover:bg-yellow-600">{challenge.prize}</Badge>
            </div>

            <CardHeader className="pb-3">
              <CardTitle className="line-clamp-1">{challenge.title}</CardTitle>
              <p className="text-sm text-muted-foreground line-clamp-2">{challenge.description}</p>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">
                    {challenge.submissions}/{challenge.maxSubmissions}
                  </span>
                </div>
                <Progress value={(challenge.submissions / challenge.maxSubmissions) * 100} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span>{challenge.participants} joined</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>{challenge.daysLeft} days left</span>
                </div>
              </div>

              <Button className="w-full group" asChild>
                <Link href={`/challenges/${challenge.id}`}>
                  Join Challenge
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  )
}
