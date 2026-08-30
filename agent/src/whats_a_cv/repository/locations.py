from pydantic import BaseModel


class SourceLocation(BaseModel):
    relative_path: str
    section_heading: str | None = None
