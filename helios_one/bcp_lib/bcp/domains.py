"""
BCP Domain Presets - Pre-configured scenarios for various domains.

These presets are validated across Phase 72-73 experiments demonstrating
universal BCP behavior.
"""

from typing import List, Dict, Callable
from .core import AttentionItem


def create_generic_scenario(items: List[Dict]) -> List[AttentionItem]:
    """
    Create a scenario from a list of item specifications.

    Args:
        items: List of dicts with 'name', 'gain', 'cost' keys

    Returns:
        List of AttentionItem objects
    """
    return [
        AttentionItem(
            name=item['name'],
            gain=item['gain'],
            cost=item['cost']
        )
        for item in items
    ]


# ============================================================================
# DOMAIN PRESETS (Validated in Phase 72-73)
# ============================================================================

def _finance_portfolio() -> List[AttentionItem]:
    """Gate 196: Investment portfolio attention allocation."""
    return [
        AttentionItem("TECH", gain=0.15, cost=1.0),
        AttentionItem("BONDS", gain=0.05, cost=0.3),
        AttentionItem("GOLD", gain=0.08, cost=0.5),
        AttentionItem("CRYPTO", gain=0.25, cost=2.0),
        AttentionItem("REITS", gain=0.10, cost=0.7),
    ]


def _medical_triage() -> List[AttentionItem]:
    """Gate 197: Medical diagnosis priority allocation."""
    return [
        AttentionItem("IMMEDIATE", gain=1.0, cost=0.8),
        AttentionItem("EMERGENT", gain=0.8, cost=0.6),
        AttentionItem("URGENT", gain=0.6, cost=0.4),
        AttentionItem("STANDARD", gain=0.4, cost=0.3),
        AttentionItem("NON_URGENT", gain=0.2, cost=0.2),
    ]


def _education_students() -> List[AttentionItem]:
    """Gate 198: Student attention allocation."""
    return [
        AttentionItem("Struggling", gain=0.8, cost=1.0),
        AttentionItem("Average", gain=0.6, cost=0.5),
        AttentionItem("Above_Avg", gain=0.4, cost=0.3),
        AttentionItem("Advanced", gain=0.2, cost=0.8),
    ]


def _diplomacy_topics() -> List[AttentionItem]:
    """Gate 199: Negotiation topic prioritization."""
    return [
        AttentionItem("Price", gain=0.95, cost=0.5),
        AttentionItem("Timeline", gain=0.7, cost=0.4),
        AttentionItem("Quality", gain=0.6, cost=0.3),
        AttentionItem("Support", gain=0.4, cost=0.3),
        AttentionItem("Warranty", gain=0.3, cost=0.2),
    ]


def _ecosystem_species() -> List[AttentionItem]:
    """Gate 203: Conservation species prioritization."""
    return [
        AttentionItem("Flagship", gain=1.0, cost=0.8),
        AttentionItem("Critical", gain=0.9, cost=0.7),
        AttentionItem("Keystone", gain=0.85, cost=0.5),
        AttentionItem("Pollinator", gain=0.8, cost=0.3),
        AttentionItem("Apex", gain=0.7, cost=0.6),
        AttentionItem("Indicator", gain=0.5, cost=0.2),
    ]


def _software_bugs() -> List[AttentionItem]:
    """Gate 203: Bug triage prioritization."""
    return [
        AttentionItem("Security_P0", gain=1.0, cost=0.5),
        AttentionItem("DataLoss_P0", gain=0.95, cost=0.6),
        AttentionItem("Crash_P1", gain=0.8, cost=0.4),
        AttentionItem("Perf_P1", gain=0.7, cost=0.7),
        AttentionItem("UI_P2", gain=0.4, cost=0.2),
        AttentionItem("Edge_P2", gain=0.3, cost=0.3),
        AttentionItem("Cosmetic_P3", gain=0.15, cost=0.1),
    ]


def _emergency_response() -> List[AttentionItem]:
    """Gate 203: Disaster resource allocation."""
    return [
        AttentionItem("Hospital", gain=1.0, cost=0.8),
        AttentionItem("School", gain=0.95, cost=0.6),
        AttentionItem("Bridge", gain=0.7, cost=0.9),
        AttentionItem("Shelter", gain=0.6, cost=0.3),
        AttentionItem("Road", gain=0.5, cost=0.4),
        AttentionItem("Power", gain=0.45, cost=0.5),
    ]


def _content_moderation() -> List[AttentionItem]:
    """Gate 203: Social media moderation prioritization."""
    return [
        AttentionItem("CSAM", gain=1.0, cost=0.3),
        AttentionItem("Violence", gain=0.9, cost=0.4),
        AttentionItem("Terrorism", gain=0.85, cost=0.5),
        AttentionItem("Harassment", gain=0.6, cost=0.3),
        AttentionItem("Misinfo", gain=0.5, cost=0.6),
        AttentionItem("Copyright", gain=0.4, cost=0.2),
        AttentionItem("Spam", gain=0.2, cost=0.1),
    ]


def _manufacturing_qc() -> List[AttentionItem]:
    """Gate 203: Quality control prioritization."""
    return [
        AttentionItem("Medical_Device", gain=1.0, cost=0.8),
        AttentionItem("Auto_Safety", gain=0.9, cost=0.7),
        AttentionItem("Electronics", gain=0.7, cost=0.5),
        AttentionItem("Food", gain=0.65, cost=0.4),
        AttentionItem("Consumer", gain=0.4, cost=0.3),
        AttentionItem("Packaging", gain=0.25, cost=0.15),
    ]


# Domain preset registry
DOMAIN_PRESETS: Dict[str, Callable[[], List[AttentionItem]]] = {
    "finance": _finance_portfolio,
    "medical": _medical_triage,
    "education": _education_students,
    "diplomacy": _diplomacy_topics,
    "ecosystem": _ecosystem_species,
    "software": _software_bugs,
    "emergency": _emergency_response,
    "moderation": _content_moderation,
    "manufacturing": _manufacturing_qc,
}


def get_domain_preset(name: str) -> Callable[[], List[AttentionItem]]:
    """
    Get a domain preset by name.

    Args:
        name: Domain name (finance, medical, education, etc.)

    Returns:
        Function that returns list of AttentionItems

    Raises:
        KeyError: If domain name not found
    """
    if name not in DOMAIN_PRESETS:
        available = ", ".join(DOMAIN_PRESETS.keys())
        raise KeyError(f"Unknown domain '{name}'. Available: {available}")
    return DOMAIN_PRESETS[name]
