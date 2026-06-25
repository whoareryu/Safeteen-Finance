#!/usr/bin/env python3
"""
validate_harness.py — 스타 토폴로지 온톨로지 하네스 검증기

카파시 하네스 엔지니어링 철학 적용:
  - MD 파일의 frontmatter(type: hub|spoke, links: [])를 파싱
  - 토폴로지 위반(스포크→스포크 직접 링크, 고립 노드, 순환 참조) 탐지
  - 위반 발견 시 non-zero exit code 반환 (CI 차단 가능)

사용법:
  python scripts/validate_harness.py [--docs-root PATH]
  python scripts/validate_harness.py --docs-root fastapi/_docs

지원 링크 형식:
  - Obsidian WikiLink: [[node-name]] 또는 [[node-name|별칭]]
  - Frontmatter links 필드: links: [node-a, node-b]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML이 필요합니다. pip install pyyaml", file=sys.stderr)
    sys.exit(1)


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]")


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def collect_wikilinks(text: str) -> list[str]:
    """본문에서 [[WikiLink]] 형태 링크를 수집한다."""
    return WIKILINK_RE.findall(text)


def load_nodes(docs_root: Path) -> dict[str, dict]:
    """docs_root 하위 모든 .md 파일을 파싱하여 노드 맵을 반환한다."""
    nodes: dict[str, dict] = {}
    for md_file in sorted(docs_root.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        node_type = meta.get("type", "unknown")
        fm_links = meta.get("links") or []
        if isinstance(fm_links, str):
            fm_links = [fm_links]
        body_links = collect_wikilinks(text)
        all_links = list({*fm_links, *body_links})
        node_id = md_file.stem
        nodes[node_id] = {
            "path": str(md_file.relative_to(docs_root)),
            "type": node_type,
            "links": all_links,
        }
    return nodes


def validate(nodes: dict[str, dict]) -> list[str]:
    errors: list[str] = []

    hub_nodes = {k for k, v in nodes.items() if v["type"] == "hub"}
    spoke_nodes = {k for k, v in nodes.items() if v["type"] == "spoke"}
    known_nodes = set(nodes.keys())

    if not hub_nodes:
        errors.append("TOPOLOGY: hub 노드가 없습니다. type: hub 인 MD 파일이 필요합니다.")

    # 1. 스포크 → 스포크 직접 링크 금지
    for node_id, info in nodes.items():
        if node_id not in spoke_nodes:
            continue
        for link in info["links"]:
            target = link.strip()
            if target in spoke_nodes and target != node_id:
                errors.append(
                    f"SPOKE→SPOKE: [{info['path']}] 가 허브를 거치지 않고 "
                    f"스포크 [{target}] 를 직접 참조합니다."
                )

    # 2. 고립 노드 탐지 (아무도 링크하지 않고 자신도 링크가 없는 노드)
    referenced: set[str] = set()
    for info in nodes.values():
        referenced.update(info["links"])
    for node_id, info in nodes.items():
        if node_id not in referenced and not info["links"]:
            errors.append(
                f"ISOLATED: [{info['path']}] 는 고립 노드입니다 "
                f"(incoming·outgoing 링크 모두 없음)."
            )

    # 3. 끊어진 링크 탐지 (존재하지 않는 노드 참조)
    for node_id, info in nodes.items():
        for link in info["links"]:
            target = link.strip()
            if target and target not in known_nodes:
                errors.append(
                    f"BROKEN-LINK: [{info['path']}] 가 존재하지 않는 노드 "
                    f"[{target}] 를 참조합니다."
                )

    # 4. 순환 참조 탐지 (DFS)
    adj: dict[str, list[str]] = defaultdict(list)
    for node_id, info in nodes.items():
        for link in info["links"]:
            target = link.strip()
            if target in known_nodes:
                adj[node_id].append(target)

    visited: set[str] = set()
    in_stack: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        in_stack.add(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in in_stack:
                cycle = " → ".join(path + [neighbor])
                errors.append(f"CYCLE: 순환 참조 탐지 — {cycle}")
        in_stack.discard(node)

    for node_id in nodes:
        if node_id not in visited:
            dfs(node_id, [node_id])

    # 5. type 미지정 노드 경고
    for node_id, info in nodes.items():
        if info["type"] == "unknown":
            errors.append(
                f"NO-TYPE: [{info['path']}] 에 frontmatter type 필드가 없습니다 "
                f"(hub 또는 spoke 로 지정해주세요)."
            )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Star topology harness validator")
    parser.add_argument(
        "--docs-root",
        default=".",
        help="MD 파일 탐색 루트 디렉토리 (기본값: 현재 디렉토리)",
    )
    args = parser.parse_args()

    docs_root = Path(args.docs_root).resolve()
    if not docs_root.exists():
        print(f"ERROR: 경로가 존재하지 않습니다: {docs_root}", file=sys.stderr)
        sys.exit(1)

    nodes = load_nodes(docs_root)
    if not nodes:
        print(f"WARNING: {docs_root} 에서 MD 파일을 찾지 못했습니다.")
        sys.exit(0)

    print(f"하네스 검증 시작 — {len(nodes)}개 노드 ({docs_root})")
    hub_count = sum(1 for v in nodes.values() if v["type"] == "hub")
    spoke_count = sum(1 for v in nodes.values() if v["type"] == "spoke")
    print(f"  Hub: {hub_count}개 | Spoke: {spoke_count}개\n")

    errors = validate(nodes)

    if errors:
        print(f"[FAIL] {len(errors)}개 위반 발견:\n")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        sys.exit(1)
    else:
        print("[PASS] 토폴로지 위반 없음.")
        sys.exit(0)


if __name__ == "__main__":
    main()
