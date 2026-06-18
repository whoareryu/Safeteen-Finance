import sys
from pathlib import Path

_here = Path(__file__).parent

# whoareryu/apps/ → "titanic.*" 임포트 활성화
_apps_dir = str(_here.parent.parent)
if _apps_dir not in sys.path:
    sys.path.insert(0, _apps_dir)