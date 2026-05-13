import { Bot, ExternalLink, Github } from "lucide-react";

interface AgentCardProps {
  name: string;
  description: string;
  tags: string[];
  status: "active" | "development" | "coming-soon";
  demoUrl?: string;
  githubUrl?: string;
}

export default function AgentCard({
  name,
  description,
  tags,
  status,
  demoUrl,
  githubUrl,
}: AgentCardProps) {
  const statusColors = {
    active: "bg-green-500/20 text-green-400 border-green-500/30",
    development: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    "coming-soon": "bg-blue-500/20 text-blue-400 border-blue-500/30",
  };

  const statusLabels = {
    active: "Active",
    development: "In Development",
    "coming-soon": "Coming Soon",
  };

  return (
    <div className="group relative">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-500/50 via-pink-500/50 to-cyan-500/50 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <div className="relative bg-card border border-border rounded-2xl p-6 hover:border-primary/50 transition-all duration-300">
        <div className="flex items-start justify-between mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 flex items-center justify-center border border-border">
            <Bot className="w-6 h-6 text-primary" />
          </div>
          <span
            className={`px-3 py-1 text-xs font-medium rounded-full border ${statusColors[status]}`}
          >
            {statusLabels[status]}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
          {name}
        </h3>
        <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
          {description}
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs bg-secondary text-secondary-foreground rounded-md"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-3 pt-4 border-t border-border">
          {demoUrl && (
            <a
              href={demoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              Demo
            </a>
          )}
          {githubUrl && (
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              <Github className="w-4 h-4" />
              Code
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
