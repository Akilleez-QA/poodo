#!/usr/bin/env python3
"""Agent-facing structural checks for POODO records, as CLI subcommands and a stdio MCP server."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

_SPEC = importlib.util.spec_from_file_location("poodo_check_capsule", Path(__file__).resolve().with_name("check_capsule.py"))
check_capsule = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(check_capsule)

SERVER_NAME = "poodo-tools"
TOOLS_VERSION = "1.0.0"
PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
DISCLAIMER = (
    "Structural check only: a pass is not a truth or quality judgement. "
    "Structural conformance is not runtime validation."
)
HASH_DISCLAIMER = (
    "A digest binds exact bytes only. It does not show that the precommit was written before observation, "
    "that its content is sound, or that anything it predicts happened."
)

MAX_TEXT_CHARS = 262_144
MAX_LINE_BYTES = 1_048_576
MAX_ITEMS = 200
MAX_NAME_CHARS = 200
MAX_LINE_CHARS = 2_000
MAX_URL_CHARS = 2_048
MAX_DEPTH = 32
ORIENT_PATH_COUNT = 20
NEAR_DUPLICATE_JACCARD = 0.75
MIN_RESEARCH_SOURCES = 2

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset({
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "into", "is", "it",
    "of", "on", "or", "the", "then", "to", "via", "with", "without",
})
SUCCESS_RE = re.compile(r"\b(fixed|fixes|fix|resolved|resolves|successful|successfully|validated|validates)\b", re.IGNORECASE)
NEGATORS = frozenset({
    "not", "no", "never", "without", "cannot", "nor", "unless", "isnt", "arent", "wasnt", "werent", "hasnt", "havent", "yet",
})
RECEIPT_RE = re.compile(r"^([0-9a-fA-F]{64})(?:\s+\*?(.*))?$")


class InputError(ValueError):
    pass


def _result(tool: str, errors: list[str], warnings: list[str], **fields: Any) -> dict[str, Any]:
    return {
        "tool": tool,
        "tools_version": TOOLS_VERSION,
        "status": "fail" if errors else "pass",
        "scope": "structural",
        "errors": errors,
        "warnings": warnings,
        **fields,
        "disclaimer": DISCLAIMER,
    }


def _depth_ok(value: Any, depth: int = 0) -> bool:
    if depth > MAX_DEPTH:
        return False
    if isinstance(value, dict):
        return all(_depth_ok(item, depth + 1) for item in value.values())
    if isinstance(value, list):
        return all(_depth_ok(item, depth + 1) for item in value)
    return True


def _text(value: Any, field: str, limit: int = MAX_TEXT_CHARS, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str):
        raise InputError(f"{field}: must be a string")
    if len(value) > limit:
        raise InputError(f"{field}: exceeds {limit} characters")
    return value


def _blank(value: Any) -> bool:
    return not isinstance(value, str) or not value.strip()


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise InputError(f"{field}: must be a list")
    if len(value) > MAX_ITEMS:
        raise InputError(f"{field}: exceeds {MAX_ITEMS} items")
    return value


def _check_args(arguments: Any, allowed: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise InputError("arguments: must be an object")
    unknown = sorted(set(arguments) - allowed)
    if unknown:
        raise InputError("arguments: unknown fields: " + ", ".join(unknown))
    missing = sorted(required - set(arguments))
    if missing:
        raise InputError("arguments: missing required fields: " + ", ".join(missing))
    if not _depth_ok(arguments):
        raise InputError(f"arguments: nesting exceeds depth {MAX_DEPTH}")
    return arguments


def _strip_delimiters(text: str) -> tuple[str, bool]:
    lines = text.strip().splitlines()
    opening = bool(lines) and lines[0].strip() == "POODO_CONTINUATION_V3_0"
    closing = bool(lines) and lines[-1].strip() == "END_POODO_CONTINUATION_V3_0"
    if opening != closing:
        raise InputError("capsule: has only one of the POODO_CONTINUATION_V3_0 delimiters")
    if opening:
        return "\n".join(lines[1:-1]) + "\n", True
    return text, False


def tool_check_capsule(arguments: Any) -> dict[str, Any]:
    args = _check_args(arguments, {"capsule", "hard_token_ceiling"}, {"capsule"})
    raw = _text(args["capsule"], "capsule")
    ceiling = args.get("hard_token_ceiling", 1800)
    if not isinstance(ceiling, int) or isinstance(ceiling, bool) or not 1 <= ceiling <= 100_000:
        raise InputError("hard_token_ceiling: must be an integer from 1 to 100000")
    payload, stripped = _strip_delimiters(raw)
    try:
        data = yaml.load(payload, Loader=check_capsule.UniqueKeyLoader)
    except (ValueError, yaml.YAMLError) as exc:
        raise InputError(f"capsule: could not load capsule: {exc}") from None
    errors = check_capsule.validate(data, payload, ceiling)
    return _result(
        "check_capsule", errors, [],
        delimiters_stripped=stripped,
        checker="scripts/check_capsule.py validate()",
        schema=check_capsule.SCHEMA,
        not_checked=["truth of claims", "evidence behind locators", "sibling capsules and forks", "reasoning quality"],
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _receipt_lines(receipt: str) -> list[tuple[int, str]]:
    found = []
    for number, line in enumerate(receipt.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        match = RECEIPT_RE.match(stripped)
        if match:
            found.append((number, match.group(1).lower()))
    return found


def precommit_digest(data: bytes, name: str, receipt: str | None, method: str) -> dict[str, Any]:
    digest = hashlib.sha256(data).hexdigest()
    result: dict[str, Any] = {
        "tool": "precommit_hash",
        "tools_version": TOOLS_VERSION,
        "status": "ok",
        "scope": "identity",
        "errors": [],
        "warnings": [],
        "method": method,
        "sha256": digest,
        "byte_length": len(data),
        "receipt_line": f"{digest}  {name}",
    }
    if receipt is not None:
        lines = _receipt_lines(receipt)
        matched = [number for number, value in lines if value == digest]
        result["receipt"] = {
            "digest_lines": [number for number, _ in lines],
            "matched_lines": matched,
            "matches_first": bool(lines) and lines[0][1] == digest,
            "matches_last": bool(lines) and lines[-1][1] == digest,
        }
        if not lines:
            result["errors"].append("receipt: no '<sha256>  <name>' line found")
        elif not matched:
            result["errors"].append("receipt: no recorded digest matches these bytes")
        result["status"] = "fail" if result["errors"] else "pass"
    result["disclaimer"] = HASH_DISCLAIMER
    return result


def tool_precommit_hash(arguments: Any) -> dict[str, Any]:
    args = _check_args(arguments, {"document", "record", "name", "receipt"}, set())
    if ("document" in args) == ("record" in args):
        raise InputError("arguments: give exactly one of document or record")
    name = _text(args.get("name", "PRECOMMIT.md"), "name", MAX_NAME_CHARS * 2)
    if not name.strip() or "\n" in name or "\r" in name:
        raise InputError("name: must be one non-empty line")
    receipt = _text(args.get("receipt"), "receipt", MAX_TEXT_CHARS, required=False)
    if "document" in args:
        document = _text(args["document"], "document")
        return precommit_digest(document.encode("utf-8"), name, receipt, "sha256 over the document's UTF-8 bytes, unnormalized")
    try:
        encoded = canonical_json(args["record"]).encode("ascii")
    except (ValueError, TypeError) as exc:
        raise InputError(f"record: cannot be represented as canonical JSON: {exc}") from None
    if len(encoded) > MAX_TEXT_CHARS:
        raise InputError(f"record: canonical form exceeds {MAX_TEXT_CHARS} bytes")
    return precommit_digest(encoded, name, receipt, "sha256 over canonical JSON (sorted keys, compact separators, ASCII)")


def _normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(TOKEN_RE.findall(folded))


def _tokens(text: str) -> frozenset[str]:
    return frozenset(token for token in _normalize(text).split() if token not in STOPWORDS)


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def tool_orient_paths_check(arguments: Any) -> dict[str, Any]:
    args = _check_args(arguments, {"paths"}, {"paths"})
    items = _list(args["paths"], "paths")
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[tuple[int, str, str]] = []
    for index, item in enumerate(items, 1):
        if isinstance(item, str):
            name, mechanism = item, ""
        elif isinstance(item, dict):
            unknown = sorted(set(item) - {"name", "mechanism"})
            if unknown:
                errors.append(f"paths[{index}]: unknown fields: {', '.join(unknown)}")
            name, mechanism = item.get("name"), item.get("mechanism", "")
        else:
            errors.append(f"paths[{index}]: must be a string or an object with name and mechanism")
            continue
        if _blank(name):
            errors.append(f"paths[{index}].name: must be a non-empty string")
            continue
        _text(name, f"paths[{index}].name", MAX_NAME_CHARS)
        if _blank(mechanism):
            errors.append(f"paths[{index}].mechanism: state the distinguishing mechanism or information gain")
            mechanism = ""
        else:
            _text(mechanism, f"paths[{index}].mechanism", MAX_LINE_CHARS)
            if "\n" in mechanism.strip():
                warnings.append(f"paths[{index}].mechanism: spans several lines; the method asks for one compact line")
        entries.append((index, name, mechanism))

    by_name: dict[str, int] = {}
    by_tokens: dict[frozenset[str], int] = {}
    by_mechanism: dict[str, int] = {}
    duplicates: list[dict[str, Any]] = []
    near: list[dict[str, Any]] = []
    duplicate_of: set[int] = set()
    for index, name, mechanism in entries:
        key = _normalize(name)
        tokens = _tokens(name)
        if key in by_name:
            duplicates.append({"paths": [by_name[key], index], "reason": "same name after normalization"})
            duplicate_of.add(index)
        elif tokens and tokens in by_tokens:
            duplicates.append({"paths": [by_tokens[tokens], index], "reason": "same name words in another order"})
            duplicate_of.add(index)
        mechanism_key = _normalize(mechanism)
        if mechanism_key and mechanism_key in by_mechanism and index not in duplicate_of:
            duplicates.append({"paths": [by_mechanism[mechanism_key], index], "reason": "same mechanism under another name"})
            duplicate_of.add(index)
        by_name.setdefault(key, index)
        if tokens:
            by_tokens.setdefault(tokens, index)
        if mechanism_key:
            by_mechanism.setdefault(mechanism_key, index)

    duplicate_pairs = {frozenset(pair["paths"]) for pair in duplicates}
    for position, (left_index, left_name, left_mechanism) in enumerate(entries):
        for right_index, right_name, right_mechanism in entries[position + 1:]:
            if frozenset((left_index, right_index)) in duplicate_pairs:
                continue
            name_score = _jaccard(_tokens(left_name), _tokens(right_name))
            mechanism_score = _jaccard(_tokens(left_mechanism), _tokens(right_mechanism))
            score = max(name_score, mechanism_score)
            if score >= NEAR_DUPLICATE_JACCARD:
                near.append({
                    "paths": [left_index, right_index],
                    "field": "name" if name_score >= mechanism_score else "mechanism",
                    "jaccard": round(score, 3),
                })

    for pair in duplicates:
        errors.append(f"paths {pair['paths'][0]} and {pair['paths'][1]}: duplicate ({pair['reason']})")
    for pair in near:
        warnings.append(
            f"paths {pair['paths'][0]} and {pair['paths'][1]}: possible near-duplicate "
            f"({pair['field']} word overlap {pair['jaccard']}); confirm they differ in mechanism, evidence, risk, "
            "reversibility, cost or authority"
        )
    distinct = len(entries) - len(duplicate_of)
    if len(items) != ORIENT_PATH_COUNT:
        errors.append(f"paths: {len(items)} entries given; exactly {ORIENT_PATH_COUNT} are required")
    elif distinct != ORIENT_PATH_COUNT:
        errors.append(f"paths: {distinct} distinct entries after duplicate removal; exactly {ORIENT_PATH_COUNT} are required")
    return _result(
        "orient_paths_check", errors, warnings,
        count=len(items), distinct_count=distinct, duplicates=duplicates, near_duplicates=near,
        comparison="NFKC casefold, alphanumeric tokens, stopwords removed; token-set Jaccard >= 0.75 is flagged",
        not_checked=["whether paths are materially distinct in substance", "whether paths are credible, safe or authorized",
                     "whether the list was generated from evidence rather than padding"],
    )


def _date_ok(value: Any) -> bool:
    if isinstance(value, date):
        return True
    if not isinstance(value, str) or not DATE_RE.fullmatch(value.strip()):
        return False
    try:
        date.fromisoformat(value.strip()[:10])
    except ValueError:
        return False
    return True


def _url_ok(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_URL_CHARS:
        return None
    try:
        parts = urlsplit(value.strip())
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return None
    return parts.hostname.lower()


def _string_list(value: Any, field: str, errors: list[str], require_items: bool) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field}: must be a list")
        return []
    if len(value) > MAX_ITEMS:
        raise InputError(f"{field}: exceeds {MAX_ITEMS} items")
    result = []
    for index, item in enumerate(value, 1):
        text = item.get("text") if isinstance(item, dict) else item
        if _blank(text):
            errors.append(f"{field}[{index}]: must be a non-empty string or an object with text")
            continue
        _text(text, f"{field}[{index}]", MAX_LINE_CHARS)
        result.append(text)
    if require_items and not result:
        errors.append(f"{field}: must name at least one entry")
    return result


def tool_research_gate_check(arguments: Any) -> dict[str, Any]:
    allowed = {"queries", "sources", "conflicts", "non_entailments", "implications", "semantic_additions", "applicability", "gate"}
    args = _check_args(arguments, allowed, {"queries", "sources", "conflicts", "non_entailments"})
    errors: list[str] = []
    warnings: list[str] = []

    queries = _list(args["queries"], "queries")
    disconfirming = 0
    query_count = 0
    for index, item in enumerate(queries, 1):
        if isinstance(item, dict):
            unknown = sorted(set(item) - {"query", "disconfirming"})
            if unknown:
                errors.append(f"queries[{index}]: unknown fields: {', '.join(unknown)}")
            text, flag = item.get("query"), item.get("disconfirming", False)
            if not isinstance(flag, bool):
                errors.append(f"queries[{index}].disconfirming: must be true or false")
            elif flag:
                disconfirming += 1
        else:
            text = item
        if _blank(text):
            errors.append(f"queries[{index}]: must be a non-empty query string")
            continue
        _text(text, f"queries[{index}]", MAX_LINE_CHARS)
        query_count += 1
    if not query_count:
        errors.append("queries: must name at least one query")
    if query_count and not disconfirming:
        warnings.append("queries: none is marked disconfirming; the gate asks for explicit disconfirmation searches")

    sources = _list(args["sources"], "sources")
    hosts: list[str] = []
    seen_urls: dict[str, int] = {}
    valid_sources = 0
    for index, source in enumerate(sources, 1):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{path}: must be an object with url and retrieved date")
            continue
        unknown = sorted(set(source) - {"url", "title", "published", "updated", "retrieved", "authority", "evidence_family", "scope"})
        if unknown:
            errors.append(f"{path}: unknown fields: {', '.join(unknown)}")
        host = _url_ok(source.get("url"))
        ok = True
        if host is None:
            errors.append(f"{path}.url: must be an http or https URL with a host, at most {MAX_URL_CHARS} characters")
            ok = False
        else:
            url_key = source["url"].strip().rstrip("/")
            if url_key in seen_urls:
                errors.append(f"{path}.url: repeats sources[{seen_urls[url_key]}]")
                ok = False
            else:
                seen_urls[url_key] = index
                hosts.append(host)
        if not _date_ok(source.get("retrieved")):
            errors.append(f"{path}.retrieved: must be an ISO 8601 date (YYYY-MM-DD or RFC 3339)")
            ok = False
        dated = [key for key in ("published", "updated") if key in source]
        for key in dated:
            if not _date_ok(source[key]):
                errors.append(f"{path}.{key}: must be an ISO 8601 date (YYYY-MM-DD or RFC 3339)")
                ok = False
        if not dated:
            warnings.append(f"{path}: no published or updated date recorded")
        for key in ("title", "authority", "evidence_family", "scope"):
            if key in source:
                _text(source[key], f"{path}.{key}", MAX_LINE_CHARS)
        if ok:
            valid_sources += 1
    if len(sources) < MIN_RESEARCH_SOURCES:
        errors.append(f"sources: {len(sources)} given; a single source cannot satisfy the gate (at least {MIN_RESEARCH_SOURCES})")
    elif hosts and len(set(hosts)) == 1:
        warnings.append("sources: every source is on one host; pages repeating one upstream statement are one evidence family")
    families = [source.get("evidence_family") for source in sources if isinstance(source, dict)]
    if len(families) >= MIN_RESEARCH_SOURCES and all(families) and len(set(families)) == 1:
        warnings.append("sources: every source declares the same evidence_family")

    conflicts = _string_list(args["conflicts"], "conflicts", errors, require_items=False)
    if isinstance(args["conflicts"], list) and not args["conflicts"]:
        warnings.append("conflicts: empty; state 'none found' with the disconfirmation queries that looked for them")
    non_entailments = _string_list(args["non_entailments"], "non_entailments", errors, require_items=True)
    implications = []
    if "implications" in args:
        implications = _string_list(args["implications"], "implications", errors, require_items=False)
    if not implications:
        warnings.append("implications: none recorded; the gate asks for at least one implication that could change a hypothesis, test or decision")
    for key in ("semantic_additions", "applicability"):
        if key in args:
            _string_list(args[key], key, errors, require_items=False)
    gate = args.get("gate")
    if gate is not None and gate not in {"satisfied", "unsatisfied"}:
        errors.append("gate: must be satisfied or unsatisfied")
    if gate == "satisfied" and errors:
        errors.append("gate: declared satisfied but the record is structurally incomplete")
    return _result(
        "research_gate_check", errors, warnings,
        query_count=query_count, disconfirming_query_count=disconfirming, source_count=len(sources),
        structurally_valid_sources=valid_sources, distinct_hosts=len(set(hosts)),
        conflict_count=len(conflicts), non_entailment_count=len(non_entailments),
        not_checked=["whether the URLs resolve or say what is claimed", "source authority and independence",
                     "whether research was actually performed", "depth or adequacy of the research"],
    )


def _success_words(text: str) -> list[str]:
    found = []
    for match in SUCCESS_RE.finditer(text):
        before = text[: match.start()].casefold().replace("'", "").replace("’", "")
        if not NEGATORS.intersection(TOKEN_RE.findall(before)[-3:]):
            found.append(match.group(0))
    return found


def tool_terminal_claim_check(arguments: Any) -> dict[str, Any]:
    fields = ("delivery_state", "outcome_state", "highest_justified_claim", "required_runtime_observation", "who_controls_next_test")
    args = _check_args(arguments, {*fields, "acceptance", "summary"}, set(fields))
    errors: list[str] = []
    warnings: list[str] = []
    for key in fields:
        if _blank(args[key]):
            errors.append(f"{key}: must be a non-empty string")
        else:
            _text(args[key], key, MAX_LINE_CHARS)
    if isinstance(args["delivery_state"], str) and args["delivery_state"] not in check_capsule.DELIVERY_STATES:
        errors.append("delivery_state: must be one of " + ", ".join(sorted(check_capsule.DELIVERY_STATES)))
    if isinstance(args["outcome_state"], str) and args["outcome_state"] not in check_capsule.OUTCOME_STATES:
        errors.append("outcome_state: must be one of " + ", ".join(sorted(check_capsule.OUTCOME_STATES)))

    observation = args["required_runtime_observation"] if isinstance(args["required_runtime_observation"], str) else ""
    no_remaining = re.match(r"^\s*none\b", observation, re.IGNORECASE) is not None
    evidence_ids = [token for token in re.findall(r"[A-Z]{1,4}-[A-Za-z0-9][A-Za-z0-9._-]*", observation) if check_capsule.ID_RE.fullmatch(token)]
    if no_remaining and not evidence_ids:
        errors.append("required_runtime_observation: 'none' must cite the evidence IDs that closed the runtime check")
    controller = args["who_controls_next_test"].strip().casefold() if isinstance(args["who_controls_next_test"], str) else ""
    if observation.strip() and not no_remaining and controller == "none":
        errors.append("who_controls_next_test: a runtime observation remains, so someone must control the next test")

    passed: list[str] = []
    if "acceptance" in args:
        for index, item in enumerate(_list(args["acceptance"], "acceptance"), 1):
            path = f"acceptance[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{path}: must be an object")
                continue
            unknown = sorted(set(item) - {"id", "criterion", "status", "artifact", "environment", "evidence"})
            if unknown:
                errors.append(f"{path}: unknown fields: {', '.join(unknown)}")
            for key in ("id", "criterion", "status"):
                if _blank(item.get(key)):
                    errors.append(f"{path}.{key}: must be a non-empty string")
                else:
                    _text(item[key], f"{path}.{key}", MAX_LINE_CHARS)
            status = item.get("status")
            if isinstance(status, str) and status not in check_capsule.PREDICTION_STATES:
                errors.append(f"{path}.status: must be one of " + ", ".join(sorted(check_capsule.PREDICTION_STATES)))
            if status == "passed":
                missing = [key for key in ("artifact", "environment") if _blank(item.get(key))]
                if missing:
                    errors.append(f"{path}: a passed criterion must name its {' and '.join(missing)}")
                else:
                    passed.append(str(item.get("id")))
    if args["outcome_state"] == "passed" and not passed:
        errors.append("outcome_state: 'passed' needs an acceptance entry with status passed naming artifact and environment")

    texts = {"highest_justified_claim": args["highest_justified_claim"]}
    if "summary" in args:
        texts["summary"] = _text(args["summary"], "summary", MAX_TEXT_CHARS)
    flagged: list[dict[str, str]] = []
    for key, value in texts.items():
        if not isinstance(value, str):
            continue
        for word in _success_words(value):
            flagged.append({"field": key, "word": word})
    if flagged and not (passed and args["outcome_state"] == "passed"):
        for item in flagged:
            errors.append(
                f"{item['field']}: unqualified '{item['word']}' without a passed intended-use criterion on a named "
                "artifact and environment"
            )
    return _result(
        "terminal_claim_check", errors, warnings,
        passed_criteria=passed, success_words=flagged,
        not_checked=["whether the stated states are true", "whether a passed criterion was the intended-use criterion",
                     "success language that avoids the checked words"],
    )


TOOLS: dict[str, dict[str, Any]] = {
    "check_capsule": {
        "handler": tool_check_capsule,
        "description": (
            "Check the structure and referential integrity of one POODO continuation capsule (YAML payload, delimiters "
            "optional) with scripts/check_capsule.py. Structural only: says nothing about whether its claims are true."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "capsule": {"type": "string", "maxLength": MAX_TEXT_CHARS, "description": "Capsule YAML payload"},
                "hard_token_ceiling": {"type": "integer", "minimum": 1, "maximum": 100000, "default": 1800},
            },
            "required": ["capsule"],
            "additionalProperties": False,
        },
    },
    "precommit_hash": {
        "handler": tool_precommit_hash,
        "description": (
            "SHA-256 of a precommit so receipts can bind to it. 'document' hashes the exact UTF-8 bytes, matching "
            "'sha256sum PRECOMMIT.md > receipt/precommit.sha256'; 'record' hashes canonical JSON (sorted keys, compact, "
            "ASCII). Optionally compare with a receipt. A digest binds bytes; it is not evidence of timing or truth."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "document": {"type": "string", "maxLength": MAX_TEXT_CHARS},
                "record": {"description": "JSON value hashed in canonical form"},
                "name": {"type": "string", "maxLength": MAX_NAME_CHARS * 2, "default": "PRECOMMIT.md"},
                "receipt": {"type": "string", "maxLength": MAX_TEXT_CHARS, "description": "sha256sum-format receipt text"},
            },
            "additionalProperties": False,
        },
    },
    "orient_paths_check": {
        "handler": tool_orient_paths_check,
        "description": (
            "Check an Orient path list: exactly 20 named entries, each with a distinguishing mechanism; duplicates "
            "(normalized name, reordered words or same mechanism) fail and word-overlap near-duplicates are flagged. "
            "Structural only: cannot judge material distinctness or quality."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "maxItems": MAX_ITEMS,
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "maxLength": MAX_NAME_CHARS},
                            "mechanism": {"type": "string", "maxLength": MAX_LINE_CHARS},
                        },
                        "required": ["name", "mechanism"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["paths"],
            "additionalProperties": False,
        },
    },
    "research_gate_check": {
        "handler": tool_research_gate_check,
        "description": (
            "Check that an Observe research record names its queries, at least two sources with http(s) URL and "
            "retrieved date, conflicts and non-entailments. Structural only: does not fetch URLs or judge the research."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "queries": {"type": "array", "maxItems": MAX_ITEMS, "items": {
                    "anyOf": [{"type": "string"}, {"type": "object", "properties": {
                        "query": {"type": "string"}, "disconfirming": {"type": "boolean"}},
                        "required": ["query"], "additionalProperties": False}]}},
                "sources": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "object", "properties": {
                    "url": {"type": "string", "maxLength": MAX_URL_CHARS}, "title": {"type": "string"},
                    "published": {"type": "string"}, "updated": {"type": "string"}, "retrieved": {"type": "string"},
                    "authority": {"type": "string"}, "evidence_family": {"type": "string"}, "scope": {"type": "string"}},
                    "required": ["url", "retrieved"], "additionalProperties": False}},
                "conflicts": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "string"}},
                "non_entailments": {"type": "array", "minItems": 1, "maxItems": MAX_ITEMS, "items": {"type": "string"}},
                "implications": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "string"}},
                "semantic_additions": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "string"}},
                "applicability": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "string"}},
                "gate": {"type": "string", "enum": ["satisfied", "unsatisfied"]},
            },
            "required": ["queries", "sources", "conflicts", "non_entailments"],
            "additionalProperties": False,
        },
    },
    "terminal_claim_check": {
        "handler": tool_terminal_claim_check,
        "description": (
            "Check a consequential handoff's terminal claim: delivery_state, outcome_state, highest_justified_claim, "
            "required_runtime_observation and who_controls_next_test present and well formed; flags unqualified "
            "fixed/resolved/successful/validated without a passed intended-use criterion. Structural and lexical only."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "delivery_state": {"type": "string", "enum": sorted(check_capsule.DELIVERY_STATES)},
                "outcome_state": {"type": "string", "enum": sorted(check_capsule.OUTCOME_STATES)},
                "highest_justified_claim": {"type": "string", "maxLength": MAX_LINE_CHARS},
                "required_runtime_observation": {"type": "string", "maxLength": MAX_LINE_CHARS},
                "who_controls_next_test": {"type": "string", "maxLength": MAX_LINE_CHARS},
                "acceptance": {"type": "array", "maxItems": MAX_ITEMS, "items": {"type": "object", "properties": {
                    "id": {"type": "string"}, "criterion": {"type": "string"},
                    "status": {"type": "string", "enum": sorted(check_capsule.PREDICTION_STATES)},
                    "artifact": {"type": "string"}, "environment": {"type": "string"}, "evidence": {"type": "string"}},
                    "required": ["id", "criterion", "status"], "additionalProperties": False}},
                "summary": {"type": "string", "maxLength": MAX_TEXT_CHARS},
            },
            "required": ["delivery_state", "outcome_state", "highest_justified_claim", "required_runtime_observation", "who_controls_next_test"],
            "additionalProperties": False,
        },
    },
}


def call_tool(name: str, arguments: Any) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        raise KeyError(name)
    handler: Callable[[Any], dict[str, Any]] = tool["handler"]
    return handler(arguments)


def input_error_result(name: str, message: str) -> dict[str, Any]:
    return {
        "tool": name,
        "tools_version": TOOLS_VERSION,
        "status": "error",
        "scope": "input",
        "errors": [message],
        "warnings": [],
        "disclaimer": "The input was rejected before any check ran.",
    }


def run_tool(name: str, arguments: Any) -> tuple[dict[str, Any], bool]:
    try:
        return call_tool(name, arguments), False
    except InputError as exc:
        return input_error_result(name, str(exc)), True
    except RecursionError:
        return input_error_result(name, "input nesting is too deep"), True


def _tool_listing() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "title": name.replace("_", " "),
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        }
        for name, spec in TOOLS.items()
    ]


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_message(message: Any) -> dict[str, Any] | None:
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        request_id = message.get("id") if isinstance(message, dict) else None
        return _error(request_id if isinstance(request_id, (str, int)) else None, -32600, "Invalid Request")
    method = message["method"]
    has_id = "id" in message
    request_id = message.get("id")
    if has_id and (isinstance(request_id, bool) or not isinstance(request_id, (str, int))):
        return _error(None, -32600, "Invalid Request: id must be a string or integer")
    if not has_id:
        return None
    params = message.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error(request_id, -32602, "Invalid params: params must be an object")
    if method == "initialize":
        requested = params.get("protocolVersion")
        version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": TOOLS_VERSION},
            "instructions": "Deterministic structural checks for POODO records. " + DISCLAIMER,
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": _tool_listing()}}
    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or name not in TOOLS:
            return _error(request_id, -32602, f"Unknown tool: {name}")
        result, is_error = run_tool(name, params.get("arguments", {}))
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "content": [{"type": "text", "text": json.dumps(result, indent=2, sort_keys=True)}],
            "structuredContent": result,
            "isError": is_error,
        }}
    return _error(request_id, -32601, f"Method not found: {method}")


def _dispatch(message: Any) -> dict[str, Any] | None:
    if isinstance(message, list):
        return _error(None, -32600, "Invalid Request: batches are not supported")
    try:
        return handle_message(message)
    except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as exc:
        request_id = message.get("id") if isinstance(message, dict) else None
        return _error(request_id if isinstance(request_id, (str, int)) else None, -32603, f"Internal error: {type(exc).__name__}")


def serve(stdin: Any = None, stdout: Any = None) -> int:
    source = stdin or sys.stdin.buffer
    sink = stdout or sys.stdout
    while True:
        line = source.readline(MAX_LINE_BYTES + 1)
        if not line:
            return 0
        if len(line) > MAX_LINE_BYTES and not line.endswith(b"\n"):
            while True:
                rest = source.readline(MAX_LINE_BYTES + 1)
                if not rest or rest.endswith(b"\n"):
                    break
            response: dict[str, Any] | None = _error(None, -32600, f"Invalid Request: message exceeds {MAX_LINE_BYTES} bytes")
        elif not line.strip():
            continue
        else:
            try:
                message = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, ValueError, RecursionError):
                response = _error(None, -32700, "Parse error")
            else:
                response = _dispatch(message)
        if response is not None:
            sink.write(json.dumps(response, separators=(",", ":")) + "\n")
            sink.flush()


def _load_file(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")
    if len(raw) > MAX_TEXT_CHARS:
        raise InputError(f"{path.name}: exceeds {MAX_TEXT_CHARS} characters")
    return yaml.load(raw, Loader=check_capsule.UniqueKeyLoader)


def _emit(result: dict[str, Any], as_json: bool) -> int:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['tool']}: {result['status']}")
        for key in ("sha256", "receipt_line"):
            if key in result:
                print(f"{key}: {result[key]}")
        for error in result["errors"]:
            print(f"- error: {error}")
        for warning in result["warnings"]:
            print(f"- warning: {warning}")
        print(result["disclaimer"])
    return {"pass": 0, "ok": 0, "fail": 1}.get(result["status"], 2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="POODO structural checks for agents. A pass is not a truth or quality judgement.")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="run the stdio MCP server (newline-delimited JSON-RPC 2.0)")
    capsule = sub.add_parser("check-capsule", help="check one capsule file")
    capsule.add_argument("file", type=Path)
    capsule.add_argument("--hard-token-ceiling", type=int, default=1800)
    digest = sub.add_parser("precommit-hash", help="SHA-256 of a precommit file's exact bytes, or of a JSON record")
    digest.add_argument("file", type=Path)
    digest.add_argument("--record", action="store_true", help="read the file as JSON or YAML and hash its canonical JSON form")
    digest.add_argument("--name", help="name written in the receipt line (default: the path as given)")
    digest.add_argument("--receipt", type=Path, help="sha256sum-format receipt to compare against")
    for command, helptext in (
        ("orient-paths-check", "check a JSON or YAML file holding {paths: [...]}"),
        ("research-gate-check", "check a JSON or YAML research record"),
        ("terminal-claim-check", "check a JSON or YAML terminal claim"),
    ):
        sub.add_parser(command, help=helptext).add_argument("file", type=Path)
    args = parser.parse_args(argv)
    if args.command == "serve":
        return serve()
    name = args.command.replace("-", "_")
    try:
        if args.command == "check-capsule":
            raw = args.file.read_text(encoding="utf-8")
            if len(raw) > MAX_TEXT_CHARS:
                raise InputError(f"{args.file.name}: exceeds {MAX_TEXT_CHARS} characters")
            result, _ = run_tool(name, {"capsule": raw, "hard_token_ceiling": args.hard_token_ceiling})
        elif args.command == "precommit-hash":
            receipt = args.receipt.read_text(encoding="utf-8") if args.receipt else None
            label = args.name or str(args.file)
            if args.record:
                result, _ = run_tool(name, {"record": _load_file(args.file), "name": label, **({"receipt": receipt} if receipt is not None else {})})
            else:
                data = args.file.read_bytes()
                if len(data) > MAX_TEXT_CHARS * 4:
                    raise InputError(f"{args.file.name}: exceeds {MAX_TEXT_CHARS * 4} bytes")
                result = precommit_digest(data, label, receipt, "sha256 over the file's exact bytes, unnormalized")
        else:
            result, _ = run_tool(name, _load_file(args.file))
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        result = input_error_result(name, f"could not load input: {exc}")
    return _emit(result, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
