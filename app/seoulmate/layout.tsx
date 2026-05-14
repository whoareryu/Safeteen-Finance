import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SeoulMate | Whoareryu",
  description: "서울 자연·역사·놀이·체험·맛집 추천 (준비 중)",
};

export default function SeoulmateLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
