import unicodedata
from pathlib import Path
import pytest
from app.errors import AppError
from app.settings import Settings
from app.ingestion.validate import validate_markdown
from app.ingestion.normalize import normalize
from app.ingestion.chunk import chunk_text, pipeline_fingerprint


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "body"),
    [
        ("a.pdf", b"text"),
        ("a.md", b""),
        ("a.md", b"\x00binary"),
        ("a.md", b"\xff"),
        ("a.md", b"\x1bcontrol"),
    ],
)
def test_invalid_uploads(name, body):
    with pytest.raises(AppError):
        validate_markdown(name, body, Settings())


@pytest.mark.unit
def test_normalization_preserves_structure_and_maps_original():
    raw = "\ufeff# Cafe\u0301\r\n\r\n  code  \r\n"
    doc = normalize(raw)
    assert doc.text == "# Café\n\n  code  \n"
    assert doc.original == raw
    for i, (start, end) in enumerate(doc.spans):
        assert 0 <= start < end <= len(raw)
        assert doc.text[i] in unicodedata.normalize("NFC", raw[start:end]).replace(
            "\r\n", "\n"
        )


@pytest.mark.unit
def test_repeatable_chunks_exact_ranges_and_source_lines():
    raw = Path("tests/fixtures/markdown/structure.md").read_text()
    settings = Settings(chunk_target=100, chunk_max=160, chunk_overlap=20)
    doc = normalize(raw)
    chunks = chunk_text(doc, settings)
    assert chunks == chunk_text(normalize(raw), settings)
    assert chunks[0].locator.start_line == 1
    assert any("Etapas" in c.locator.section_path for c in chunks)
    assert all(
        c.text == doc.text[c.start : c.end] and len(c.text) <= 160 for c in chunks
    )
    assert any("  energia" in c.text for c in chunks)
    assert pipeline_fingerprint(settings) != pipeline_fingerprint(Settings())


@pytest.mark.unit
def test_large_code_block_and_unicode_graphemes_are_bounded():
    raw = "# Código\n\n```text\n" + ("  αβγ e\u0301 👩‍💻\n" * 100) + "```\n"
    doc = normalize(raw)
    chunks = chunk_text(
        doc, Settings(chunk_target=100, chunk_max=160, chunk_overlap=10)
    )
    assert len(chunks) > 1
    assert chunks[-1].end == len(doc.text)
    assert all(c.start < c.end and len(c.text) <= 160 for c in chunks)


@pytest.mark.unit
def test_upload_cap_checked_before_decode():
    with pytest.raises(AppError) as error:
        validate_markdown("../../a.md", b"a" * 11, Settings(max_upload_bytes=10))
    assert error.value.status == 413
