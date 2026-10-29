import pytest
from app.ingestion.extract_html import extract_html
from app.errors import AppError


def test_extraction_is_deterministic_without_script_or_navigation():
    body = (
        "<html><head><title>Study</title><script>alert('secret')</script></head><body><nav>Menu</nav><article><h1>Células</h1><p>"
        + "A célula é a unidade básica da vida e apresenta organização própria. " * 20
        + "</p></article></body></html>"
    ).encode()
    text, fingerprint = extract_html(body)
    assert "célula" in text and "alert(" not in text and "Menu" not in text
    assert extract_html(body) == (text, fingerprint)


def test_xml_external_entities_rejected():
    with pytest.raises(AppError):
        extract_html(b'<!DOCTYPE x SYSTEM "file:///etc/passwd"><html/>')
