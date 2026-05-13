import { GraduationCap } from "lucide-react";
import ChatInput from "./chat-input";
import SocialFooter from "./social-footer";

export default function HeroSection() {
  return (
    <section className="h-screen flex flex-col items-center justify-between px-6 pt-20 pb-6 overflow-hidden">
      <div className="flex-1 flex flex-col items-center justify-center text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-secondary/50 border border-border rounded-full mb-6">
          <GraduationCap className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-muted-foreground">
            IBM x RedHat AI Academy
          </span>
        </div>

        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 leading-tight text-balance">
          <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
            MSA Architecture
          </span>
          <span className="text-foreground"> meets </span>
          <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
            Hexagonal Strategy
          </span>
        </h1>

        <p className="text-base md:text-lg text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed text-pretty">
          Harness Engineering과 OOP 프로그래밍을 기반으로, 
          <span className="text-primary font-medium"> 헥사고날 아키텍처</span>를 적용한 
          <span className="text-primary font-medium"> MSA 설계</span>로 확장 가능하고 유지보수하기 쉬운 시스템을 구축합니다.
        </p>

        <div className="w-full max-w-2xl">
          <ChatInput />
        </div>
      </div>

      <SocialFooter />
    </section>
  );
}
