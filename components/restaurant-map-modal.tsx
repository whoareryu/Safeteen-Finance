"use client";

import { X } from "lucide-react";
import KakaoMap from "@/components/kakao-map";

type RestaurantMapModalProps = {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  onClose: () => void;
};

export default function RestaurantMapModal({
  name,
  address,
  latitude,
  longitude,
  onClose,
}: RestaurantMapModalProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-2xl bg-card p-4 shadow-2xl sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold text-foreground">{name}</h3>
            <p className="mt-0.5 text-xs text-muted-foreground">{address}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-full p-1.5 text-muted-foreground hover:bg-secondary"
            aria-label="닫기"
          >
            <X className="size-4" />
          </button>
        </div>
        <KakaoMap latitude={latitude} longitude={longitude} level={4} className="h-56 w-full" />
      </div>
    </div>
  );
}
