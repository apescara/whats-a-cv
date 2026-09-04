from .kinds import RecordKind
from .locations import SourceLocation
from .frontmatter import parse_frontmatter, serialize_frontmatter, split_frontmatter
from .slugs import validate_slug
from .dates import validate_date
from .paths import proposal_path, record_path
from .atomic import atomic_write
from .diffs import unified_diff
from .records import (
    Record, ExperienceRecord, EducationRecord, CertificationRecord,
    ProjectRecord, ExpertiseRecord, LanguageRecord, ContactRecord, Preferences,
)
from .service import list_records, load_record, validate_profile, RecordNotFoundError
from .proposals import ProposalStore, content_hash
from .preferences import read_preferences, serialize_preferences
from .applications import (
    ApplicationBundle, ApplicationMetadata, ApplicationSummary, ArtifactPaths, JobDraft,
    compile_latex, fetch_job_url, list_applications, normalize_job_html,
    read_application, read_artifact, render_inert_markdown, application_metadata_proposal,
    delete_draft_application,
)

__all__ = [
    "RecordKind",
    "SourceLocation",
    "parse_frontmatter",
    "serialize_frontmatter",
    "split_frontmatter",
    "validate_slug",
    "validate_date",
    "record_path",
    "proposal_path",
    "atomic_write",
    "unified_diff",
    "Record", "ExperienceRecord", "EducationRecord", "CertificationRecord",
    "ProjectRecord", "ExpertiseRecord", "LanguageRecord", "ContactRecord", "Preferences",
    "list_records", "load_record", "validate_profile", "RecordNotFoundError",
    "ProposalStore", "content_hash", "read_preferences", "serialize_preferences",
    "ArtifactPaths", "ApplicationMetadata", "ApplicationSummary", "ApplicationBundle", "JobDraft",
    "list_applications", "read_application", "read_artifact", "render_inert_markdown",
    "fetch_job_url", "normalize_job_html", "compile_latex",
    "application_metadata_proposal",
    "delete_draft_application",
]
