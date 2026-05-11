#!/usr/bin/env python3
"""
키 유효성 검증: OpenAI·Google API에 가벼운 ping을 보내 모델 가용성 확인.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from api_key_manager import load_env, get_key, mask, get_model_config


def check_openai(key: str, model: str, fallback: str) -> dict:
    """OpenAI 모델 list 호출로 검증."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        models = {m.id for m in client.models.list().data}
        if model in models:
            return {"ok": True, "model_used": model, "available": True}
        elif fallback in models:
            return {
                "ok": True,
                "model_used": fallback,
                "available": False,
                "warning": f"{model} unavailable, will use {fallback}",
            }
        else:
            return {
                "ok": False,
                "error": f"Neither {model} nor {fallback} available",
                "models_sample": sorted(models)[:5],
            }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def check_google(key: str, model: str, fallback: str) -> dict:
    """Google Generative AI list_models 호출로 검증."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        models = {m.name.split("/")[-1] for m in genai.list_models()}
        # Gemini 모델은 짝지어진 long-name이 많아 prefix matching
        def matches(target: str) -> bool:
            return any(target in m for m in models)

        if matches(model):
            return {"ok": True, "model_used": model, "available": True}
        elif matches(fallback):
            return {
                "ok": True,
                "model_used": fallback,
                "available": False,
                "warning": f"{model} unavailable, will use {fallback}",
            }
        else:
            return {
                "ok": False,
                "error": f"Neither {model} nor {fallback} matched",
                "models_sample": sorted(models)[:5],
            }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def main():
    load_env()
    cfg = get_model_config()
    openai_k = get_key("OPENAI_API_KEY")
    google_k = get_key("GOOGLE_API_KEY")

    print("=== API Key 검증 ===\n")

    print(f"OpenAI: {mask(openai_k)}")
    if openai_k:
        r = check_openai(openai_k, cfg["openai"]["model"], cfg["openai"]["fallback"])
        if r["ok"]:
            print(f"  ✅ {r['model_used']} 사용 가능")
            if r.get("warning"):
                print(f"  ⚠️  {r['warning']}")
        else:
            print(f"  ❌ {r['error']}")
            if r.get("models_sample"):
                print(f"     이용 가능 모델 예: {r['models_sample']}")
    else:
        print("  ⚠️  키 미설정")

    print()
    print(f"Google: {mask(google_k)}")
    if google_k:
        r = check_google(google_k, cfg["google"]["model"], cfg["google"]["fallback"])
        if r["ok"]:
            print(f"  ✅ {r['model_used']} 사용 가능")
            if r.get("warning"):
                print(f"  ⚠️  {r['warning']}")
        else:
            print(f"  ❌ {r['error']}")
            if r.get("models_sample"):
                print(f"     이용 가능 모델 예: {r['models_sample']}")
    else:
        print("  ⚠️  키 미설정")

    print()
    if openai_k and google_k:
        print(f"💰 비용 한도: ${cfg['limits']['max_cost_usd']:.2f}/arena")
        print("✅ 두 키 모두 설정됨 — arena 실행 가능")
        return 0
    else:
        print("❌ 키가 설정되지 않아 arena를 실행할 수 없습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
