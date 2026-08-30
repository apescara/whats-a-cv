from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Type

from .frontmatter import parse_frontmatter, serialize_frontmatter, split_frontmatter
from .kinds import RecordKind
from .records import (CertificationRecord, ContactRecord, EducationRecord,
                      ExperienceRecord, ExpertiseRecord, LanguageRecord,
                      ProjectRecord, Record)
from .slugs import validate_slug


MODELS: dict[RecordKind, Type[Record]] = {
    RecordKind.EXPERIENCE: ExperienceRecord,
    RecordKind.EDUCATION: EducationRecord,
    RecordKind.CERTIFICATIONS: CertificationRecord,
    RecordKind.PROJECTS: ProjectRecord,
    RecordKind.EXPERTISE: ExpertiseRecord,
    RecordKind.LANGUAGES: LanguageRecord,
    RecordKind.CONTACT: ContactRecord,
}


@dataclass(frozen=True)
class RecordSummary:
    slug: str
    title: str
    valid: bool
    relative_path: str
    sort_date: str = ""
    error: str | None = None


class RecordNotFoundError(LookupError):
    pass


def sort_date(value: str) -> str:
    if value == "present":
        return "9999-12-31"
    for pattern in ("%Y-%m-%d", "%Y-%m", "%b %Y"):
        try:
            return datetime.strptime(value, pattern).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""


def load_record(root: Path, kind: RecordKind | str, slug: str) -> Record:
    kind = RecordKind(kind)
    validate_slug(slug)
    path = root / kind.value / f"{slug}.md"
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to((root / kind.value).resolve()):
        raise RecordNotFoundError(f"record not found: {kind.value}/{slug}")
    try:
        text = path.read_text(encoding="utf-8")
        data = parse_frontmatter(text, str(path))
        body = split_frontmatter(text)[1]
        return MODELS[kind].model_validate({**data, "slug": slug, "body": body})
    except Exception:
        if kind is RecordKind.CONTACT:
            raise ValueError("invalid contact record") from None
        raise


def list_records(root: Path, kind: RecordKind | str) -> list[RecordSummary]:
    kind = RecordKind(kind)
    folder = root / kind.value
    result = []
    for path in sorted(folder.glob("*.md")):
        if path.name == "_template.md":
            continue
        slug = path.stem
        try:
            record = load_record(root, kind, slug)
            title = next((getattr(record, field) for field in ("role", "name", "qualification", "language", "type") if getattr(record, field, "")), slug)
            date = next((str(getattr(record, field, "")) for field in ("start", "issued", "last_used") if getattr(record, field, "")), "")
            result.append(RecordSummary(slug, title, True, str(path.relative_to(root)), sort_date(date)))
        except Exception as error:
            message = "invalid contact record" if kind is RecordKind.CONTACT else str(error)
            result.append(RecordSummary(slug, slug, False, str(path.relative_to(root)), error=message))
    return result


def related_expertise(root: Path, record: Record) -> list[dict[str, str]]:
    """Return expertise explicitly named in an experience or project's Skills section."""
    if not isinstance(record, (ExperienceRecord, ProjectRecord)):
        return []
    skills = re.search(r"^## Skills\s*$([\s\S]*?)(?=^## |\Z)", record.body, re.MULTILINE)
    if not skills:
        return []
    linked = []
    for summary in list_records(root, RecordKind.EXPERTISE):
        if not summary.valid:
            continue
        expertise = load_record(root, RecordKind.EXPERTISE, summary.slug)
        if re.search(rf"(?<!\w){re.escape(expertise.name)}(?!\w)", skills.group(1), re.IGNORECASE):
            linked.append({"slug": expertise.slug, "name": expertise.name})
    return linked


def validate_profile(root: Path) -> list[RecordSummary]:
    return [summary for kind in RecordKind for summary in list_records(root, kind) if not summary.valid]


def serialize_record(record: Record) -> str:
    values = record.model_dump(exclude={"slug", "body"}, exclude_none=True)
    return serialize_frontmatter(values, record.body)
