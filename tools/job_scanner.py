"""Read a local text job posting or fetch a public web page safely (best-effort)."""
from html import unescape
from html.parser import HTMLParser
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse

import requests
from langchain_core.tools import tool

MAX_CHARS = 6000
MAX_BYTES = 1_500_000
TIMEOUT_SECONDS = 12


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg", "iframe"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg", "iframe"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth and data.strip():
            self.parts.append(data.strip())


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Use a valid public http:// or https:// URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded credentials are not allowed.")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local/internal hostnames are not allowed.")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None)}
        except (OSError, ValueError) as exc:
            raise ValueError("Could not resolve the URL host.") from exc
    if not addresses or any(not addr.is_global for addr in addresses):
        raise ValueError("Private, local, and non-public IP addresses are not allowed.")


def _read_url(url: str) -> str:
    _validate_public_url(url)
    # Redirects are disabled to avoid redirect-based access to internal hosts.
    with requests.get(
        url,
        timeout=TIMEOUT_SECONDS,
        allow_redirects=False,
        stream=True,
        headers={"User-Agent": "JobAgent/1.0 (job-posting reader)"},
    ) as response:
        if 300 <= response.status_code < 400:
            raise ValueError("Redirected job URLs are not followed. Paste the final public URL instead.")
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if not any(kind in content_type for kind in ("text/html", "text/plain", "application/xhtml+xml")):
            raise ValueError("URL must return an HTML or plain-text job posting.")
        chunks, total = [], 0
        for chunk in response.iter_content(chunk_size=16384, decode_unicode=False):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError("Job page is too large to process (limit 1.5 MB).")
            chunks.append(chunk)
        raw = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
    if "html" in content_type or "xhtml" in content_type:
        parser = _TextExtractor()
        parser.feed(raw)
        raw = " ".join(parser.parts)
    return " ".join(unescape(raw).split())[:MAX_CHARS]


@tool
def read_job_posting(source: str) -> str:
    """Read a job posting from a local .txt file path or a public HTTP(S) URL."""
    source = source.strip()
    if not source:
        raise ValueError("Provide a .txt file path or public job-posting URL.")
    if source.startswith(("http://", "https://")):
        return _read_url(source)
    path = Path(source).expanduser().resolve()
    if path.suffix.lower() != ".txt":
        raise ValueError("Local job posting files must use the .txt extension.")
    if not path.is_file():
        raise FileNotFoundError(f"Job posting file not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    return " ".join(text.split())[:MAX_CHARS]
