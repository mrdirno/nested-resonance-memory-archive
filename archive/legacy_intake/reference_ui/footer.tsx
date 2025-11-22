import Link from "next/link"
import { Github, Twitter, DiscIcon as Discord, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Footer() {
  return (
    <footer className="bg-muted/50 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">1S</span>
              </div>
              <span className="font-bold text-xl">1Shot Alpha</span>
            </div>
            <p className="text-sm text-muted-foreground max-w-xs">
              The premier platform for sharing and discovering interactive HTML experiences.
            </p>
            <div className="flex space-x-2">
              <Button variant="ghost" size="icon">
                <Github className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Discord className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Mail className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Platform */}
          <div className="space-y-4">
            <h3 className="font-semibold">Platform</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/explore" className="text-muted-foreground hover:text-foreground">
                  Explore
                </Link>
              </li>
              <li>
                <Link href="/trending" className="text-muted-foreground hover:text-foreground">
                  Trending
                </Link>
              </li>
              <li>
                <Link href="/challenges" className="text-muted-foreground hover:text-foreground">
                  Challenges
                </Link>
              </li>
              <li>
                <Link href="/upload" className="text-muted-foreground hover:text-foreground">
                  Upload
                </Link>
              </li>
            </ul>
          </div>

          {/* Community */}
          <div className="space-y-4">
            <h3 className="font-semibold">Community</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/blog" className="text-muted-foreground hover:text-foreground">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/discord" className="text-muted-foreground hover:text-foreground">
                  Discord
                </Link>
              </li>
              <li>
                <Link href="/guidelines" className="text-muted-foreground hover:text-foreground">
                  Guidelines
                </Link>
              </li>
              <li>
                <Link href="/feedback" className="text-muted-foreground hover:text-foreground">
                  Feedback
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div className="space-y-4">
            <h3 className="font-semibold">Support</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/help" className="text-muted-foreground hover:text-foreground">
                  Help Center
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-muted-foreground hover:text-foreground">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-foreground">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-muted-foreground">© 2024 1Shot Alpha. All rights reserved.</p>
          <p className="text-sm text-muted-foreground">Made with ❤️ for the creative community</p>
        </div>
      </div>
    </footer>
  )
}
