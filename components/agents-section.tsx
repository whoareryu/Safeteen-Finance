import AgentCard from "./agent-card";
import { Cpu } from "lucide-react";

const agents = [
  {
    name: "Code Review Agent",
    description:
      "An intelligent agent that analyzes code, suggests improvements, and helps maintain code quality across your projects.",
    tags: ["Python", "LangChain", "GPT-4"],
    status: "active" as const,
    demoUrl: "#",
    githubUrl: "#",
  },
  {
    name: "Document Assistant",
    description:
      "RAG-powered assistant that helps you search, summarize, and interact with your documents using natural language.",
    tags: ["RAG", "Vector DB", "OpenAI"],
    status: "active" as const,
    demoUrl: "#",
    githubUrl: "#",
  },
  {
    name: "Data Analysis Agent",
    description:
      "Automated data analysis pipeline that generates insights, visualizations, and reports from your datasets.",
    tags: ["Pandas", "AutoGen", "Charts"],
    status: "development" as const,
    githubUrl: "#",
  },
  {
    name: "Multi-Agent System",
    description:
      "A collaborative system where multiple specialized agents work together to solve complex problems.",
    tags: ["CrewAI", "Multi-Agent", "Orchestration"],
    status: "coming-soon" as const,
  },
];

export default function AgentsSection() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary border border-border rounded-full mb-4">
            <Cpu className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-muted-foreground">
              AI Agents Portfolio
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
              My AI Agents
            </span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Explore the intelligent agents I&apos;ve built during my journey at IBM x
            RedHat AI Academy. Each agent is designed to solve real-world
            problems using cutting-edge AI technologies.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent, index) => (
            <AgentCard key={index} {...agent} />
          ))}
        </div>
      </div>
    </section>
  );
}
