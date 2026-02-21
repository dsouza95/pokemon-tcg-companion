#!/usr/bin/env python3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
# Ensure backend package dir is importable (backend/pokemon-tcg-companion)
sys.path.insert(0, os.path.abspath(os.path.join(SCRIPT_DIR, "..")))

try:
    from main import app
except Exception as e:
    print("Failed to import app:", e, file=sys.stderr)
    raise

spec = app.openapi()

# write to webapp/lib/openapi.json in the repo root
OUT_PATH = os.path.abspath(
    os.path.join(SCRIPT_DIR, "..", "..", "..", "webapp", "lib", "openapi.json")
)
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(spec, f, indent=2)

print("Wrote OpenAPI spec to", OUT_PATH)
