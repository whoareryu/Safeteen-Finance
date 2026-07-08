// 카카오맵 JS SDK — 사용하는 최소 표면만 선언 (strict, any 금지).
export {};

declare global {
  interface Window {
    kakao: typeof kakao;
  }

  namespace kakao.maps {
    function load(callback: () => void): void;

    class LatLng {
      constructor(latitude: number, longitude: number);
    }

    class Map {
      constructor(
        container: HTMLElement,
        options: { center: LatLng; level: number },
      );
      setCenter(latlng: LatLng): void;
    }

    class Marker {
      constructor(options: { position: LatLng; map?: Map });
      setMap(map: Map | null): void;
    }
  }
}
