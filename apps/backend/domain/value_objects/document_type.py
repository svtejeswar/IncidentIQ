from enum import Enum


class DocumentType(str, Enum):
    INCIDENT_REPORT = "incident_report"
    RCA = "rca"
    RUNBOOK = "runbook"
    POSTMORTEM = "postmortem"
    ARCHITECTURE = "architecture"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    SERVICE_DOCUMENTATION = "service_documentation"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()
