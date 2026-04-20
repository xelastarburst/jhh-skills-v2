"""HTML page fetcher — hash-based change detection.

For pages that don't expose RSS (e.g. NVIDIA investor events). The fetcher
returns a single item if the page's content hash differs from the last seen
hash, otherwise an empty list.
"""

from __future__ import annotations

import hashlib
import re
from typing import List


def fetch(source: dict, *, http_get) -> List[dict]:
    url = source["url"]
    body = http_get(url)
    # strip boilerplate scripts and whitespace for a stable content hash
    text = re.sub(r"<script.*?</script>", "", body, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    digest = hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()
    return [{
        "id": digest,
        "title": source.get("name", url),
        "url": url,
        "published": None,
        "summary": text[:500],
    }]
