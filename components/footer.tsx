import { Github, Linkedin, Mail, Twitter } from "lucide-react";

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
            <a
              href="#"
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary border border-border text-muted-foreground hover:text-primary hover:border-primary/50 transition-all"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary border border-border text-muted-foreground hover:text-primary hover:border-primary/50 transition-all"
            >
              <Linkedin className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary border border-border text-muted-foreground hover:text-primary hover:border-primary/50 transition-all"
            >
              <Twitter className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary border border-border text-muted-foreground hover:text-primary hover:border-primary/50 transition-all"
            >
              <Mail className="w-5 h-5" />
            </a>
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
