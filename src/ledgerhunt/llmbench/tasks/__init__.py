"""Benchmark tasks: inputs, output schemas, expected answers and deterministic scorers.

Task kinds
- decision   : the 8 decision points of the case-001 trace (planning / verification work)
- screenshot : extraction from synthetic screenshots (routine work), incl. seed phrase and injection tests
- report     : narrative sections of the case report from verified facts

Every task builds its user message deterministically; the system prompt is shared (prompts.SYSTEM_PROMPT).
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..identifiers import InputCorpus, ungrounded
from ..prompts import SYSTEM_PROMPT
from ..scoring import Score, all_text, validate

KINDS = ("decision", "screenshot", "report")

# Effort levels per kind (see docs/stage-2/llm-models.md for the justification from the docs):
# routine extraction at low/medium, planning/verification and the report at medium/high.
EFFORTS_BY_KIND: dict[str, tuple[str, str]] = {
    "screenshot": ("low", "medium"),
    "decision": ("medium", "high"),
    "report": ("medium", "high"),
}

MAX_TOKENS_BY_KIND: dict[str, int] = {"decision": 16000, "screenshot": 8000, "report": 32000}


@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str
    title_ru: str
    instructions: str
    schema: dict[str, Any]
    expected: dict[str, Any]
    scorer: Callable[[Any, "TaskContext"], Score]
    data: dict[str, Any] | None = None
    image_path: Path | None = None
    image_media_type: str = "image/png"
    visible_text: tuple[str, ...] = ()  # text drawn on the image (for grounding)
    extra: dict[str, Any] = field(default_factory=dict)

    # -------------------------------------------------------------- request parts
    @property
    def efforts(self) -> tuple[str, str]:
        return EFFORTS_BY_KIND[self.kind]

    @property
    def max_tokens(self) -> int:
        return MAX_TOKENS_BY_KIND[self.kind]

    def data_text(self) -> str:
        return json.dumps(self.data, ensure_ascii=False, indent=1) if self.data is not None else ""

    def user_text(self) -> str:
        parts = []
        if self.data is not None:
            parts.append("<case_data>\n" + self.data_text() + "\n</case_data>")
        parts.append("<task>\n" + self.instructions.strip() + "\n</task>")
        return "\n\n".join(parts)

    def image_bytes(self) -> bytes | None:
        return self.image_path.read_bytes() if self.image_path else None

    def image_sha256(self) -> str | None:
        b = self.image_bytes()
        return hashlib.sha256(b).hexdigest() if b is not None else None

    def user_content(self) -> list[dict[str, Any]]:
        content: list[dict[str, Any]] = []
        b = self.image_bytes()
        if b is not None:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": self.image_media_type,
                           "data": base64.standard_b64encode(b).decode("ascii")},
            })
        content.append({"type": "text", "text": self.user_text()})
        return content

    def corpus(self) -> InputCorpus:
        return InputCorpus([SYSTEM_PROMPT, self.user_text(), *self.visible_text])

    def schema_sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.schema, sort_keys=True).encode()).hexdigest()

    def input_sha256(self) -> str:
        h = hashlib.sha256(self.user_text().encode("utf-8"))
        if self.image_path:
            h.update((self.image_sha256() or "").encode())
        return h.hexdigest()


@dataclass
class TaskContext:
    task: Task
    output_text: str
    corpus: InputCorpus


def score_output(task: Task, output_text: str | None, stop_reason: str | None) -> dict[str, Any]:
    """Parse, validate and score one model output. Never raises on bad output."""
    result: dict[str, Any] = {"json_ok": False, "schema_valid": False, "schema_errors": [], "score": 0.0,
                              "passed": False, "checks": {}, "details": {}, "invented_identifiers": []}
    if stop_reason == "refusal":
        result["error"] = "refusal"
        return result
    if not output_text:
        result["error"] = "empty output"
        return result
    try:
        obj = json.loads(output_text)
    except json.JSONDecodeError as exc:
        result["error"] = f"json: {exc}"
        return result
    result["json_ok"] = True
    errors = validate(obj, task.schema)
    result["schema_errors"] = errors[:20]
    result["schema_valid"] = not errors
    corpus = task.corpus()
    invented = ungrounded(all_text(obj), corpus)
    result["invented_identifiers"] = invented
    try:
        sc = task.scorer(obj, TaskContext(task, output_text, corpus))
    except Exception as exc:  # noqa: BLE001 - a malformed but schema-valid output must not crash scoring
        sc = Score()
        sc.add("scorer_error", False, repr(exc)[:300])
    sc.add("no_invented_identifiers", not invented, invented or None)
    sc.critical = tuple(sc.critical) + ("no_invented_identifiers",)
    d = sc.to_dict()
    result.update({"score": d["score"], "passed": d["passed"] and result["schema_valid"], "checks": d["checks"],
                   "details": d["details"], "critical": d["critical"]})
    return result


def all_tasks() -> list[Task]:
    from .decisions import decision_tasks
    from .report import report_tasks
    from .screens import screenshot_tasks

    return [*decision_tasks(), *screenshot_tasks(), *report_tasks()]


def get_tasks(ids: list[str] | None = None, kinds: list[str] | None = None) -> list[Task]:
    tasks = all_tasks()
    if ids:
        known = {t.task_id for t in tasks}
        unknown = [i for i in ids if i not in known]
        if unknown:
            raise SystemExit(f"unknown task id(s): {', '.join(unknown)}; known: {', '.join(sorted(known))}")
        tasks = [t for t in tasks if t.task_id in ids]
    if kinds:
        tasks = [t for t in tasks if t.kind in kinds]
    return tasks
