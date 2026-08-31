from __future__ import annotations

import html
import ipaddress
import re
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from pydantic import BaseModel, ConfigDict, Field

from .frontmatter import parse_frontmatter, serialize_frontmatter, split_frontmatter
from .paths import proposal_path
from .proposals import ProposalStore


EXPECTED_FILES = {"job-post.md", "cv.tex", "cv.pdf", "next-steps.md", "next-steps.mdx"}
OPTIONAL_FILES = {"status.md", "notes.md"}
APPLICATION_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ArtifactPaths(BaseModel):
    job_post: str = "job-post.md"
    cv_source: str = "cv.tex"
    pdf: str = "cv.pdf"
    next_steps: str | None = None
    status: str | None = None
    notes: str | None = None


class ApplicationMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    company: str
    role: str
    location: str = ""
    date: str = ""
    language: str = ""
    source_url: str = ""
    retrieved: str = ""
    status: str = ""
    artifacts: ArtifactPaths = Field(default_factory=ArtifactPaths)


class ApplicationSummary(BaseModel):
    slug: str
    path: str
    company: str
    role: str
    date: str = ""
    status: str = ""
    has_pdf: bool = False
    has_todo: bool = False


class ApplicationBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    path: str
    metadata: ApplicationMetadata
    files: list[str]
    extra_files: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: str | None = None


class JobDraft(BaseModel):
    text: str
    metadata: ApplicationMetadata
    source_url: str = ""
    retrieved: str = ""


def _safe_slug(slug: str) -> str:
    if not APPLICATION_SLUG.fullmatch(slug):
        raise ValueError("invalid application slug")
    return slug


def _application_path(root: Path, slug: str) -> Path:
    _safe_slug(slug)
    applications = (root / "applications").resolve()
    path = (applications / slug).resolve()
    if path.parent != applications or not path.is_relative_to(applications):
        raise ValueError("application path escapes applications root")
    return path


def _metadata(path: Path) -> ApplicationMetadata:
    job_post = path / "job-post.md"
    if not job_post.is_file() or job_post.is_symlink():
        raise ValueError("application is missing job-post.md")
    text = job_post.read_text(encoding="utf-8")
    data = parse_frontmatter(text, str(job_post))
    next_steps = "next-steps.mdx" if (path / "next-steps.mdx").is_file() else (
        "next-steps.md" if (path / "next-steps.md").is_file() else None
    )
    status = "status.md" if (path / "status.md").is_file() else None
    notes = "notes.md" if (path / "notes.md").is_file() else None
    data.setdefault("date", data.get("application_date", ""))
    data.setdefault("retrieved", data.get("retrieval_date", ""))
    data["date"] = str(data["date"] or "")
    data["retrieved"] = str(data["retrieved"] or "")
    data["artifacts"] = {"next_steps": next_steps, "status": status, "notes": notes}
    if status:
        status_data = parse_frontmatter((path / status).read_text(encoding="utf-8"), str(path / status))
        data["status"] = str(status_data.get("status", data.get("status", "")))
    return ApplicationMetadata.model_validate(data)


def read_application(root: Path, slug: str, *, include_notes: bool = False) -> ApplicationBundle:
    path = _application_path(root, slug)
    if not path.is_dir() or path.is_symlink():
        raise FileNotFoundError(f"application not found: {slug}")
    names = sorted(p.name for p in path.iterdir() if p.is_file() and not p.is_symlink())
    allowed = EXPECTED_FILES | OPTIONAL_FILES
    extra = sorted(name for name in names if name not in allowed)
    warnings = []
    metadata = _metadata(path)
    if "cv.tex" not in names:
        warnings.append("missing cv.tex")
    if "cv.pdf" not in names:
        warnings.append("missing cv.pdf")
    if metadata.artifacts.next_steps is None:
        warnings.append("missing next-steps.mdx or next-steps.md")
    notes = (path / metadata.artifacts.notes).read_text(encoding="utf-8") if include_notes and metadata.artifacts.notes else None
    return ApplicationBundle(slug=slug, path=str(path.relative_to(root)), metadata=metadata, files=names, extra_files=extra, warnings=warnings, notes=notes)


def list_applications(root: Path) -> list[ApplicationSummary]:
    folder = root / "applications"
    if not folder.is_dir():
        return []
    result = []
    for path in sorted(folder.iterdir()):
        if not path.is_dir() or path.is_symlink() or not APPLICATION_SLUG.fullmatch(path.name):
            continue
        try:
            bundle = read_application(root, path.name)
            result.append(ApplicationSummary(
                slug=bundle.slug, path=bundle.path, company=bundle.metadata.company,
                role=bundle.metadata.role, date=bundle.metadata.date,
                status=bundle.metadata.status, has_pdf="cv.pdf" in bundle.files,
                has_todo="TODO" in " ".join((path / name).read_text(encoding="utf-8") for name in ("next-steps.mdx", "next-steps.md") if (path / name).is_file()),
            ))
        except (ValueError, OSError):
            continue
    return result


def read_artifact(root: Path, slug: str, filename: str) -> tuple[Path, bytes]:
    path = _application_path(root, slug)
    if Path(filename).name != filename or filename not in EXPECTED_FILES | OPTIONAL_FILES:
        raise ValueError("artifact is not approved")
    target = path / filename
    if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(path.resolve()):
        raise FileNotFoundError(f"artifact not found: {filename}")
    return target, target.read_bytes()


def application_metadata_proposal(store: ProposalStore, root: Path, slug: str, filename: str, value: str) -> int:
    path = _application_path(root, slug) / filename
    content = serialize_frontmatter({filename[:-3]: value}, "")
    return store.create(path, content)


def render_inert_markdown(text: str) -> str:
    """Escape Markdown source before the UI applies its deliberately tiny formatting."""
    return html.escape(text, quote=False)


def normalize_job_html(content: str) -> str:
    content = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", content, flags=re.I | re.S)
    content = re.sub(r"<style\b[^>]*>.*?</style\s*>", "", content, flags=re.I | re.S)
    content = re.sub(r"<[^>]+>", " ", content)
    return re.sub(r"\s+", " ", html.unescape(content)).strip()


def _public_host(hostname: str) -> bool:
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
    except OSError as error:
        raise ValueError("could not resolve job URL") from error
    return all(not ipaddress.ip_address(address).is_private and not ipaddress.ip_address(address).is_loopback and not ipaddress.ip_address(address).is_link_local for address in addresses)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_job_url(url: str, *, timeout: float = 8, max_bytes: int = 1_000_000) -> tuple[str, str]:
    opener = build_opener(_NoRedirect)
    for _ in range(4):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("job URL must use http or https")
        if not _public_host(parsed.hostname):
            raise ValueError("job URL points to a private network")
        request = Request(url, headers={"User-Agent": "whats-a-cv/1.0"})
        try:
            response = opener.open(request, timeout=timeout)
        except HTTPError as error:
            if error.code not in {301, 302, 303, 307, 308} or not error.headers.get("Location"):
                raise
            url = urljoin(url, error.headers["Location"])
            continue
        with response:
            data = response.read(max_bytes + 1)
        break
    else:
        raise ValueError("job URL redirected too many times")
    if len(data) > max_bytes:
        raise ValueError("job page is too large")
    charset = response.headers.get_content_charset() or "utf-8"
    return normalize_job_html(data.decode(charset, errors="replace")), url


def compile_latex(root: Path, slug: str, *, timeout: float = 30) -> dict:
    path = _application_path(root, slug)
    source = path / "cv.tex"
    if not source.is_file() or source.is_symlink():
        raise FileNotFoundError("cv.tex not found")
    started = time.monotonic()
    try:
        result = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", source.name], cwd=path, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        return {"status": "error", "error": "LaTeX compiler (latexmk) is not installed"}
    except subprocess.TimeoutExpired as error:
        return {"status": "error", "error": "LaTeX compilation timed out", "output": (error.stderr or "")[-4000:]}
    output = (result.stdout + "\n" + result.stderr)[-4000:]
    pdf = path / "cv.pdf"
    if result.returncode:
        return {"status": "error", "error": "LaTeX compilation failed", "output": output}
    pages = None
    if pdf.is_file():
        match = re.search(rb"/Type\s*/Pages[^>]*?/Count\s+(\d+)", pdf.read_bytes())
        pages = int(match.group(1)) if match else None
    return {"status": "ok", "pdf_path": str(pdf.relative_to(root)), "pages": pages, "warnings": [line[-200:] for line in output.splitlines() if "warning" in line.lower()], "elapsed_ms": round((time.monotonic() - started) * 1000)}
