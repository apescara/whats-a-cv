from whats_a_cv.repository import SourceLocation


def test_source_location_round_trips() -> None:
    location = SourceLocation(
        relative_path="experience/falabella-senior-data-engineer.md",
        section_heading="Achievements",
    )

    assert SourceLocation.model_validate(location.model_dump()) == location
