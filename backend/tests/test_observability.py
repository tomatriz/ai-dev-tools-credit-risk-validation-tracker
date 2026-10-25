from __future__ import annotations

import json
import logging
from dataclasses import replace

from app.config import get_settings
from app.observability import configure_logging, trace_id_context


def test_structured_log_can_be_written_to_jsonl(tmp_path):
    log_file = tmp_path / "nested" / "backend.jsonl"
    logger = configure_logging(replace(get_settings(), log_file=str(log_file)))
    token = trace_id_context.set("correlated-trace-123")
    try:
        logger.info(
            "observable event",
            extra={"event": "test_event", "outcome": "success"},
        )
        for handler in logger.handlers:
            handler.flush()
    finally:
        trace_id_context.reset(token)

    payload = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert payload["message"] == "observable event"
    assert payload["trace_id"] == "correlated-trace-123"
    assert payload["event"] == "test_event"
    assert payload["outcome"] == "success"

    # Avoid retaining an open Windows file handle after this isolated test.
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
