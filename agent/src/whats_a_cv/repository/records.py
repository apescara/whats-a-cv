from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .locations import SourceLocation


class Record(BaseModel):
    model_config = ConfigDict(extra="allow")
    slug: str = ""
    body: str = ""


class ExperienceRecord(Record):
    company: str
    role: str
    employment_type: str = ""
    location: str = ""
    start: str
    end: str


class EducationRecord(Record):
    institution: str
    qualification: str
    field: str = ""
    location: str = ""
    start: str = ""
    end: str = ""


class CertificationRecord(Record):
    name: str
    issuer: str
    issued: str = ""
    expires: str = ""
    credential_id: str = ""
    url: str = ""


class ProjectRecord(Record):
    name: str
    role: str = ""
    url: str = ""
    start: str = ""
    end: str = ""


class Evidence(BaseModel):
    text: str
    source: SourceLocation | None = None


class ExpertiseRecord(Record):
    name: str
    category: Literal["language", "framework", "cloud", "data", "tooling", "practice", "domain", ""]
    level: str = ""
    last_used: str = ""
    evidence: list[Evidence] = Field(default_factory=list)


class LanguageRecord(Record):
    language: str
    proficiency: str = ""
    certification: str = ""


class ContactRecord(Record):
    type: Literal["email", "phone", "location", "linkedin", "github", "portfolio"]
    label: str = "primary"
    value: str
    include_by_default: bool = True


class Preferences(BaseModel):
    model_config = ConfigDict(extra="allow")
    body: str = ""
