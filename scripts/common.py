"""Shared helpers."""
from pathlib import Path


def build_deliverable(rdir: Path) -> str:
    """Everything the agent produced for a run: its final reply plus every file it wrote.

    Some agents answer in the chat, others save the work to files (and sometimes both). Grading
    only the reply would score saved work as missing, so checks and the judge read this instead.
    Written to <run>/deliverable.md.
    """
    rdir = Path(rdir)
    reply = (rdir / "response.md").read_text() if (rdir / "response.md").exists() else ""
    parts = [reply.strip()]
    ws = rdir / "workspace"
    written = sorted(p for p in ws.rglob("*") if p.is_file() and "inputs" not in p.relative_to(ws).parts) if ws.exists() else []
    for f in written:
        try:
            body = f.read_text()
        except UnicodeDecodeError:
            body = "(binary file)"
        parts.append(f"--- File written by the agent: {f.relative_to(ws)} ---\n{body.strip()}")
    text = "\n\n".join(p for p in parts if p)
    (rdir / "deliverable.md").write_text(text)
    return text


def files_written(rdir: Path) -> int:
    ws = Path(rdir) / "workspace"
    return sum(1 for p in ws.rglob("*") if p.is_file() and "inputs" not in p.relative_to(ws).parts) if ws.exists() else 0
