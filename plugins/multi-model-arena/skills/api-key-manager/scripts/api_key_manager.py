"""
API Key Manager — Multi-Model Arena

.env 파일에서 OPENAI/GOOGLE API 키를 안전하게 로드하고 마스킹한다.
LLM을 사용하지 않는다.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List


def find_env_file() -> Optional[Path]:
    """우선순위에 따라 .env 파일을 탐색."""
    candidates: List[Path] = []

    if env_path := os.environ.get("ARENA_ENV_FILE"):
        candidates.append(Path(env_path).expanduser().resolve())

    cwd = Path.cwd().resolve()
    candidates.append(cwd / ".env")

    # 워크스페이스 루트 추정 (현재 위치에서 .env 또는 plugins/ 폴더가 있는 부모를 찾음)
    for ancestor in [cwd] + list(cwd.parents):
        if (ancestor / ".env").exists():
            candidates.append(ancestor / ".env")
            break
        if (ancestor / "plugins").is_dir():
            candidates.append(ancestor / ".env")
            break

    candidates.append(cwd.parent / ".env")
    candidates.append(Path.home() / ".config" / "multi-model-arena" / ".env")

    seen = set()
    for c in candidates:
        try:
            c = c.resolve()
        except (OSError, RuntimeError):
            continue
        if c in seen:
            continue
        seen.add(c)
        if c.exists() and c.is_file():
            return c

    return None


def load_env(verbose: bool = True) -> Optional[Path]:
    """`.env`를 찾아 환경변수에 적재. 사용된 경로를 반환."""
    env_path = find_env_file()
    if not env_path:
        if verbose:
            print(
                "[api-key-manager] .env 파일을 찾을 수 없습니다.",
                file=sys.stderr,
            )
        return None

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        # python-dotenv 미설치 시 수동 파싱
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip("\"'")
                os.environ.setdefault(k, v)

    if verbose:
        print(f"[api-key-manager] .env loaded from: {env_path}", file=sys.stderr)
    return env_path


def get_key(name: str, required: bool = False) -> Optional[str]:
    """환경변수에서 키를 안전하게 가져옴."""
    val = os.environ.get(name)
    if val:
        val = val.strip()
        if val and not val.startswith("your-") and not val.endswith("-here"):
            return val
    if required:
        raise RuntimeError(
            f"환경변수 {name}이(가) 설정되지 않았거나 placeholder 값입니다. "
            f".env 파일을 확인하세요."
        )
    return None


def mask(key: Optional[str], head: int = 4, tail: int = 4) -> str:
    """키를 마스킹: sk-pr...abc1 형식."""
    if not key:
        return "<NOT SET>"
    if len(key) <= head + tail:
        return "*" * len(key)
    return f"{key[:head]}...{key[-tail:]}"


def get_model_config() -> dict:
    """OpenAI/Google 모델 설정을 dict로 반환."""
    return {
        "openai": {
            "model": os.environ.get("OPENAI_MODEL", "gpt-5.5"),
            "fallback": os.environ.get("OPENAI_FALLBACK_MODEL", "gpt-4.1"),
            "reasoning_effort": os.environ.get("OPENAI_REASONING_EFFORT", "high"),
        },
        "google": {
            "model": os.environ.get("GOOGLE_MODEL", "gemini-3.1"),
            "fallback": os.environ.get("GOOGLE_FALLBACK_MODEL", "gemini-2.5-pro"),
            "deep_think": os.environ.get("GOOGLE_DEEP_THINK", "true").lower()
            in ("true", "1", "yes"),
        },
        "limits": {
            "max_cost_usd": float(os.environ.get("ARENA_MAX_COST_USD", "2.00")),
        },
    }


if __name__ == "__main__":
    # 직접 실행 시 키 상태 출력
    path = load_env()
    cfg = get_model_config()
    openai_k = get_key("OPENAI_API_KEY")
    google_k = get_key("GOOGLE_API_KEY")

    print()
    print("=== Multi-Model Arena 키 상태 ===")
    print(f"  .env: {path or '<not found>'}")
    print(f"  OPENAI_API_KEY: {mask(openai_k)} (model={cfg['openai']['model']})")
    print(f"  GOOGLE_API_KEY: {mask(google_k)} (model={cfg['google']['model']})")
    print(f"  Max cost per arena: ${cfg['limits']['max_cost_usd']:.2f}")

    if not openai_k:
        print("  ⚠️  OPENAI_API_KEY 누락")
    if not google_k:
        print("  ⚠️  GOOGLE_API_KEY 누락")
    if openai_k and google_k:
        print("  ✅ 두 키 모두 로드됨")
