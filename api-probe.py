#!/usr/bin/env python3
"""API aliveness probe."""
import os, json, urllib.request, urllib.error

KEYS = {
    "zai":   os.environ.get("ZAI_TOKEN"),
    "deepseek": os.environ.get("DEEPSEEK_TOKEN"),
    "deepinfra": os.environ.get("DEEPINFRA_TOKEN"),
    "cloudflare": os.environ.get("CLOUDFLARE_TOKEN"),
}

def probe(url, headers, body):
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            content = ""
            if "choices" in d and d["choices"]:
                content = d["choices"][0].get("message", {}).get("content", "")[:60]
            return f"OK ({len(content)} chars): {content}"
    except urllib.error.HTTPError as e:
        try: msg = json.loads(e.read()).get("message", "")[:50]
        except: msg = ""
        return f"FAIL {e.code}: {msg}"
    except Exception as e:
        return f"FAIL: {str(e)[:50]}"

prompt = [{"role": "user", "content": "One word: substrate walker"}]

# ZAI
if KEYS["zai"]:
    body = json.dumps({"model": "glm-4.5-flash", "messages": prompt, "max_tokens": 30, "thinking": {"type": "disabled"}}).encode()
    h = {"Authorization": f"Bearer {KEYS['zai']}", "Content-Type": "application/json", "User-Agent": "mavis/1"}
    print("zai       :", probe("https://api.z.ai/api/coding/paas/v4/chat/completions", h, body))

# DeepSeek
if KEYS["deepseek"]:
    body = json.dumps({"model": "deepseek-chat", "messages": prompt, "max_tokens": 30}).encode()
    h = {"Authorization": f"Bearer {KEYS['deepseek']}", "Content-Type": "application/json"}
    print("deepseek  :", probe("https://api.deepseek.com/v1/chat/completions", h, body))

# DeepInfra (try Qwen)
if KEYS["deepinfra"]:
    body = json.dumps({"model": "Qwen/Qwen2.5-72B-Instruct", "messages": prompt, "max_tokens": 30}).encode()
    h = {"Authorization": f"Bearer {KEYS['deepinfra']}", "Content-Type": "application/json"}
    print("deepinfra :", probe("https://api.deepinfra.com/v1/openai/chat/completions", h, body))

# Cloudflare workers AI
if KEYS["cloudflare"] and os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
    body = json.dumps({"messages": prompt, "max_tokens": 30}).encode()
    h = {"Authorization": f"Bearer {KEYS['cloudflare']}", "Content-Type": "application/json"}
    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/@cf/meta/llama-3.1-8b-instruct"
    print("cloudflare:", probe(cf_url, h, body))

# JEV
TKEY = os.environ.get("TYPESAFEAI_KEY")
if TKEY:
    body = json.dumps({"text": "substrate walker", "pool": "default", "k": 1, "probe":"canon"}).encode()
    h = {"Authorization": f"Bearer {TKEY}", "Content-Type": "application/json"}
    print("jev       :", probe("https://api.typesafe.ai/v1/embed", h, body))
