# Inline the embedded dashboard data into index.html for single-file deploy.
# Usage:  python data/inline_data.py
# Reads:  index.html (must contain /*__CEE_DATA_BEGIN__*/ ... /*__CEE_DATA_END__*/)
#         data/data_embedded.json, data/meta_embedded.json (strict JSON)
# Writes: index.html with window.DATA / window.META injected between markers.
# Idempotent: re-running replaces the previous payload (markers are stable).
# With inlined data the app runs from file:// with zero fetches; the fetch
# fallback in loadData() stays for dev without a build step.

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
DATA_JSON = ROOT / "data" / "data_embedded.json"
META_JSON = ROOT / "meta_embedded.json" if (ROOT / "meta_embedded.json").exists() \
    else ROOT / "data" / "meta_embedded.json"

BEGIN = "/*__CEE_DATA_BEGIN__*/"
END = "/*__CEE_DATA_END__*/"


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    if BEGIN not in html or END not in html:
        raise SystemExit("Payload markers missing in index.html")
    data = DATA_JSON.read_text(encoding="utf-8").strip()
    meta = META_JSON.read_text(encoding="utf-8").strip()
    # Guard against a literal </script> sequence inside JSON strings.
    payload = (f"\nwindow.DATA={data};\nwindow.META={meta};\n").replace("</", "<\\/")
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                  lambda _: BEGIN + payload + END,
                  html, flags=re.DOTALL, count=1)
    INDEX.write_text(html, encoding="utf-8")
    kb = INDEX.stat().st_size / 1024
    print(f"Inlined {DATA_JSON.name} + {META_JSON.name} -> index.html ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
