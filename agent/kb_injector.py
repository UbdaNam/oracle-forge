"""
Oracle Forge — KB Injector
Injects all 3 context layers into the DAB DataAgent system prompt at session start:
  Layer 1: Schema/metadata — loaded via --use_hints (db_description_withhint.txt)
  Layer 2: Domain knowledge — kb/domain/ documents
  Layer 3: Corrections memory — kb/corrections/corrections.md
"""
import os
from pathlib import Path

# Resolve KB path relative to this file
AGENT_DIR = Path(__file__).parent
KB_DIR = AGENT_DIR.parent / "kb"
KB_CORRECTIONS = KB_DIR / "corrections" / "corrections.md"
KB_DOMAIN_DIR = KB_DIR / "domain"


def load_corrections() -> str:
    """Layer 3: Load corrections log."""
    if KB_CORRECTIONS.exists():
        content = KB_CORRECTIONS.read_text().strip()
        if content:
            return f"\n\n## PAST FAILURES AND FIXES (read before answering)\n{content}"
    return ""


def load_domain_knowledge() -> str:
    """Layer 2: Load domain knowledge docs from kb/domain/."""
    parts = []
    if KB_DOMAIN_DIR.exists():
        for doc in sorted(KB_DOMAIN_DIR.glob("*.md")):
            if doc.name == "CHANGELOG.md":
                continue
            content = doc.read_text().strip()
            if content:
                parts.append(f"### {doc.stem}\n{content}")
    if parts:
        return "\n\n## DOMAIN KNOWLEDGE\n" + "\n\n".join(parts)
    return ""


def build_kb_context() -> str:
    """Combine all KB context layers."""
    return load_domain_knowledge() + load_corrections()


# ── Monkey-patch DataAgent.__init__ to inject KB context ─────────────────────
import common_scaffold.DataAgent as _da  # noqa: E402
_original_init = _da.DataAgent.__init__


def _patched_init(self, query_dir, db_description, db_config_path, deployment_name, **kwargs):
    kb_context = build_kb_context()
    enriched_description = db_description + kb_context
    print(f"[Oracle Forge] KB injected: {len(kb_context)} chars added to db_description")
    _original_init(self, query_dir, enriched_description, db_config_path, deployment_name, **kwargs)


_da.DataAgent.__init__ = _patched_init
