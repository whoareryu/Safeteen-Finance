import { Github, Linkedin, Mail, Twitter } from "lucide-react";
import { Button } from "@/components/ui/button";

const SOCIAL_ICON_CLASS =
  "h-10 w-10 rounded-lg bg-secondary border border-border text-muted-foreground hover:bg-secondary hover:text-primary hover:border-primary/50 transition-all";

export default function Footer() {
  return (
    <footer className="border-t border-border bg-card/50">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-center md:text-left">
            <h3 className="text-xl font-bold mb-2">
              <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
                Whoareryu
              </span>
            </h3>
            <p className="text-sm text-muted-foreground">
              AI Developer | IBM x RedHat AI Academy
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Button asChild variant="ghost" size="icon" className={SOCIAL_ICON_CLASS}>
              <a href="#">
                <Github className="w-5 h-5" />
              </a>
            </Button>
            <Button asChild variant="ghost" size="icon" className={SOCIAL_ICON_CLASS}>
              <a href="#">
                <Linkedin className="w-5 h-5" />
              </a>
            </Button>
            <Button asChild variant="ghost" size="icon" className={SOCIAL_ICON_CLASS}>
              <a href="#">
                <Twitter className="w-5 h-5" />
              </a>
            </Button>
            <Button asChild variant="ghost" size="icon" className={SOCIAL_ICON_CLASS}>
              <a href="#">
                <Mail className="w-5 h-5" />
              </a>
            </Button>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-border text-center">
          <p className="text-sm text-muted-foreground">
            Built with passion and AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
