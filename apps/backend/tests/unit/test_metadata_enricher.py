"""Unit tests for the regex-based metadata enricher."""
from __future__ import annotations

import pytest

from ingestion.chunkers.text_chunker import TextChunk
from ingestion.enrichers.metadata_enricher import MetadataEnricher


def _make_chunk(text: str, index: int = 0) -> TextChunk:
    return TextChunk(text=text, chunk_index=index, start_char=0, end_char=len(text))


@pytest.fixture
def enricher() -> MetadataEnricher:
    return MetadataEnricher()


class TestSeverityExtraction:
    def test_critical_keyword(self, enricher):
        chunk = _make_chunk("This was a critical outage affecting all users.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "critical"

    def test_sev0_abbreviation(self, enricher):
        chunk = _make_chunk("Incident classified as SEV0.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "critical"

    def test_p0_abbreviation(self, enricher):
        chunk = _make_chunk("This is a P0 issue.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "critical"

    def test_high_severity(self, enricher):
        chunk = _make_chunk("Classified as high severity, affecting checkout flow.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "high"

    def test_sev1_abbreviation(self, enricher):
        chunk = _make_chunk("This is a sev1 issue.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "high"

    def test_medium_severity(self, enricher):
        chunk = _make_chunk("Medium severity degradation in background jobs.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "medium"

    def test_low_severity(self, enricher):
        chunk = _make_chunk("Low priority cosmetic issue on dashboard.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "low"

    def test_unknown_severity_when_no_match(self, enricher):
        chunk = _make_chunk("No severity information in this text.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "unknown"

    def test_case_insensitive_matching(self, enricher):
        chunk = _make_chunk("CRITICAL failure detected.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["severity"] == "critical"


class TestRootCauseExtraction:
    def test_root_cause_prefix(self, enricher):
        chunk = _make_chunk(
            "Root cause: The database connection pool was exhausted due to a misconfigured timeout."
        )
        result = enricher.enrich([chunk], "postmortem")
        assert result[0]["root_cause"] is not None
        assert "connection pool" in result[0]["root_cause"]

    def test_caused_by_prefix(self, enricher):
        chunk = _make_chunk(
            "The outage was caused by a memory leak in the auth service worker thread."
        )
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["root_cause"] is not None
        assert "memory leak" in result[0]["root_cause"]

    def test_reason_prefix(self, enricher):
        chunk = _make_chunk(
            "Reason: An expired SSL certificate triggered connection failures."
        )
        result = enricher.enrich([chunk], "rca")
        assert result[0]["root_cause"] is not None
        assert "SSL" in result[0]["root_cause"]

    def test_no_root_cause_returns_none(self, enricher):
        chunk = _make_chunk("The service experienced elevated error rates.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["root_cause"] is None

    def test_root_cause_is_truncated_to_200_chars(self, enricher):
        long_text = "x" * 300
        chunk = _make_chunk(f"Root cause: {long_text}")
        result = enricher.enrich([chunk], "incident_report")
        assert len(result[0]["root_cause"]) <= 200


class TestResolutionExtraction:
    def test_resolution_prefix(self, enricher):
        chunk = _make_chunk(
            "Resolution: We increased the connection pool size and deployed a config update."
        )
        result = enricher.enrich([chunk], "postmortem")
        assert result[0]["resolution"] is not None
        assert "connection pool" in result[0]["resolution"]

    def test_fixed_by_prefix(self, enricher):
        chunk = _make_chunk(
            "The issue was fixed by rolling back the deployment to the previous version."
        )
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["resolution"] is not None
        assert "rolling back" in result[0]["resolution"]

    def test_resolved_by_prefix(self, enricher):
        chunk = _make_chunk(
            "Incident resolved by restarting the affected Kubernetes pods."
        )
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["resolution"] is not None
        assert "Kubernetes" in result[0]["resolution"]

    def test_no_resolution_returns_none(self, enricher):
        chunk = _make_chunk("The incident is still under investigation.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["resolution"] is None


class TestAffectedServicesExtraction:
    def test_api_suffix(self, enricher):
        chunk = _make_chunk("The payment-api experienced elevated latency.")
        result = enricher.enrich([chunk], "incident_report")
        assert "payment-api" in result[0]["affected_services"]

    def test_service_suffix(self, enricher):
        chunk = _make_chunk("auth-service went down during the deployment window.")
        result = enricher.enrich([chunk], "incident_report")
        assert "auth-service" in result[0]["affected_services"]

    def test_known_infra_names(self, enricher):
        chunk = _make_chunk("redis and postgres were unresponsive for 3 minutes.")
        result = enricher.enrich([chunk], "incident_report")
        services = result[0]["affected_services"]
        assert "redis" in services
        assert "postgres" in services

    def test_kafka_detected(self, enricher):
        chunk = _make_chunk("kafka consumer lag spiked to 500k messages.")
        result = enricher.enrich([chunk], "incident_report")
        assert "kafka" in result[0]["affected_services"]

    def test_returns_lowercase(self, enricher):
        chunk = _make_chunk("AUTH-SERVICE was impacted.")
        result = enricher.enrich([chunk], "incident_report")
        services = result[0]["affected_services"]
        assert all(s == s.lower() for s in services)

    def test_deduplication(self, enricher):
        chunk = _make_chunk("auth-service failed and auth-service restarted.")
        result = enricher.enrich([chunk], "incident_report")
        services = result[0]["affected_services"]
        assert services.count("auth-service") == 1

    def test_no_services_returns_empty_list(self, enricher):
        chunk = _make_chunk("Users reported slow page loads in the browser.")
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["affected_services"] == []

    def test_max_ten_services(self, enricher):
        names = [f"svc{i}-service" for i in range(15)]
        chunk = _make_chunk(" ".join(names))
        result = enricher.enrich([chunk], "incident_report")
        assert len(result[0]["affected_services"]) <= 10


class TestEnrichMetadata:
    def test_document_type_is_preserved(self, enricher):
        chunk = _make_chunk("Some text.")
        result = enricher.enrich([chunk], "runbook")
        assert result[0]["document_type"] == "runbook"

    def test_chunk_index_is_preserved(self, enricher):
        chunk = _make_chunk("Some text.", index=3)
        result = enricher.enrich([chunk], "incident_report")
        assert result[0]["chunk_index"] == 3

    def test_returns_one_result_per_chunk(self, enricher):
        chunks = [_make_chunk(f"chunk {i}", index=i) for i in range(5)]
        result = enricher.enrich(chunks, "postmortem")
        assert len(result) == 5
