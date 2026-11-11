#!/usr/bin/env python3
"""Static validation for the detection content in this repository.

Checks (standard library only, no Suricata or Wazuh install required):

  * Suricata rules   - header/option structure, mandatory msg/sid/rev, unique SIDs
  * Wazuh rules      - well-formed XML, unique IDs, valid levels, local references
  * Cross-references - every Wazuh rule that matches a Suricata SID points at a SID
                       that exists, and every local SID has a Wazuh rule
  * Sample events    - valid JSON, alert events, SIDs present in local.rules
  * Agent config     - well-formed XML

This is a fast pre-commit / CI gate. It does NOT replace the real engines:
    suricata -T -c /etc/suricata/suricata.yaml
    /var/ossec/bin/wazuh-analysisd -t

Usage:
    python3 scripts/validate_rules.py [--root PATH]
Exit status is 0 when no errors are found, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

LOCAL_SID_RANGE = (1_000_000, 1_999_999)  # Suricata local rule SID space
VALID_ACTIONS = {"alert", "drop", "reject", "rejectsrc", "rejectdst", "rejectboth", "pass", "config"}
SIG_ID_REGEX = re.compile(r"^\^(\d+)\$$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# --------------------------------------------------------------------------- #
# Suricata
# --------------------------------------------------------------------------- #
def split_options(body: str, where: str = "rule") -> list[str]:
    """Split a Suricata option block on ';', honouring quotes and backslash escapes."""
    options, current = [], []
    in_quotes = False
    escaped = False
    for ch in body:
        if escaped:
            current.append(ch)
            escaped = False
        elif ch == "\\":
            current.append(ch)
            escaped = True
        elif ch == '"':
            current.append(ch)
            in_quotes = not in_quotes
        elif ch == ";" and not in_quotes:
            options.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        options.append(tail)  # missing trailing ';'
        err(f"{where}: option '{tail[:40]}' is not terminated with ';'")
    if in_quotes:
        err(f"{where}: unbalanced double quote in rule options")
    return [o for o in options if o]


def parse_suricata(path: Path) -> dict[int, str]:
    sids: dict[int, str] = {}
    if not path.exists():
        err(f"{path}: file not found")
        return sids

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        where = f"{path.name}:{lineno}"
        before = len(errors)

        if "(" not in line or not line.endswith(")"):
            err(f"{where}: rule must have an option block ending in ')'")
            continue
        header, _, rest = line.partition("(")
        body = rest[:-1]

        tokens = re.findall(r"\[[^\]]*\]|\S+", header)
        if len(tokens) != 7:
            err(f"{where}: header needs 7 fields (action proto src sport dir dst dport), found {len(tokens)}")
        else:
            action, _proto, _src, _sport, direction, _dst, _dport = tokens
            if action not in VALID_ACTIONS:
                err(f"{where}: unknown action '{action}'")
            if direction not in {"->", "<>"}:
                err(f"{where}: direction must be '->' or '<>', found '{direction}'")

        opts = {}
        for opt in split_options(body, where):
            key, _, value = opt.partition(":")
            opts.setdefault(key.strip(), value.strip())

        for required in ("msg", "sid", "rev"):
            if required not in opts:
                err(f"{where}: missing mandatory option '{required}'")

        msg = opts.get("msg", "")
        if msg and not (msg.startswith('"') and msg.endswith('"')):
            err(f"{where}: msg must be double-quoted")

        sid_text = opts.get("sid", "")
        if sid_text:
            if not sid_text.isdigit():
                err(f"{where}: sid must be numeric, found '{sid_text}'")
            else:
                sid = int(sid_text)
                if not LOCAL_SID_RANGE[0] <= sid <= LOCAL_SID_RANGE[1]:
                    warn(f"{where}: SID {sid} is outside the local range {LOCAL_SID_RANGE[0]}-{LOCAL_SID_RANGE[1]}")
                if sid in sids:
                    err(f"{where}: duplicate SID {sid}")
                elif len(errors) == before:
                    sids[sid] = msg.strip('"')
        if opts.get("rev", "x") and not opts.get("rev", "0").isdigit():
            err(f"{where}: rev must be numeric")
        if "classtype" not in opts:
            warn(f"{where}: no classtype set (SID {sid_text or '?'})")
    return sids


# --------------------------------------------------------------------------- #
# Wazuh
# --------------------------------------------------------------------------- #
def parse_wazuh(path: Path) -> tuple[dict[int, ET.Element], set[int]]:
    rules: dict[int, ET.Element] = {}
    referenced_sids: set[int] = set()
    if not path.exists():
        err(f"{path}: file not found")
        return rules, referenced_sids

    # Wazuh rule files contain several top-level <group> elements, so wrap them.
    try:
        root = ET.fromstring(f"<root>{path.read_text(encoding='utf-8')}</root>")
    except ET.ParseError as exc:
        err(f"{path.name}: not well-formed XML ({exc})")
        return rules, referenced_sids

    for rule in root.iter("rule"):
        rid_text = rule.get("id", "")
        where = f"{path.name}: rule id={rid_text or '?'}"
        if not rid_text.isdigit():
            err(f"{where}: id must be numeric")
            continue
        rid = int(rid_text)
        if rid in rules:
            err(f"{where}: duplicate rule id")
        rules[rid] = rule

        level = rule.get("level")
        if level is None or not level.isdigit() or not 0 <= int(level) <= 15:
            err(f"{where}: level must be an integer from 0 to 15")
        if rule.findtext("description", "").strip() == "":
            err(f"{where}: missing <description>")
        if rule.get("frequency") and not rule.get("timeframe"):
            err(f"{where}: frequency requires timeframe")

        for field in rule.findall("field"):
            if field.get("name") == "alert.signature_id":
                match = SIG_ID_REGEX.match((field.text or "").strip())
                if match:
                    referenced_sids.add(int(match.group(1)))
                else:
                    warn(f"{where}: alert.signature_id regex is not of the form ^NNN$")

        for mitre_id in rule.findall("./mitre/id"):
            if not re.fullmatch(r"T\d{4}(\.\d{3})?", (mitre_id.text or "").strip()):
                err(f"{where}: invalid MITRE technique id '{mitre_id.text}'")

    # Second pass: local references must resolve (built-in IDs in if_sid are allowed).
    for rid, rule in rules.items():
        for tag in ("if_matched_sid", "if_matched_group"):
            for ref in rule.findall(tag):
                if tag == "if_matched_sid" and ref.text and ref.text.strip().isdigit():
                    if int(ref.text.strip()) not in rules:
                        err(f"rule {rid}: if_matched_sid {ref.text.strip()} is not defined in this file")
    return rules, referenced_sids


# --------------------------------------------------------------------------- #
# Samples and agent config
# --------------------------------------------------------------------------- #
def check_samples(path: Path, known_sids: set[int]) -> set[int]:
    seen: set[int] = set()
    if not path.exists():
        warn(f"{path}: no sample events found")
        return seen
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        where = f"{path.name}:{lineno}"
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            err(f"{where}: invalid JSON ({exc})")
            continue
        for needed in ("timestamp", "event_type"):
            if needed not in event:
                err(f"{where}: missing '{needed}' (the Wazuh Suricata decoder expects it)")
        if event.get("event_type") != "alert":
            err(f"{where}: event_type must be 'alert'")
        sid = event.get("alert", {}).get("signature_id")
        if not isinstance(sid, int):
            err(f"{where}: alert.signature_id missing or not an integer")
        else:
            seen.add(sid)
            if sid not in known_sids:
                err(f"{where}: signature_id {sid} not defined in local.rules")
    return seen


def check_xml(path: Path) -> None:
    if not path.exists():
        err(f"{path}: file not found")
        return
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        err(f"{path.name}: not well-formed XML ({exc})")


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    root = parser.parse_args().root

    sids = parse_suricata(root / "suricata/rules/local.rules")
    rules, referenced = parse_wazuh(root / "wazuh/manager/rules/local_rules.xml")
    check_xml(root / "wazuh/agent/suricata-eve-integration.xml")
    sample_sids = check_samples(root / "wazuh/manager/rules/tests/sample-eve-events.jsonl", set(sids))

    for sid in sorted(referenced - set(sids)):
        err(f"Wazuh rules reference Suricata SID {sid}, which is not defined in local.rules")
    for sid in sorted(set(sids) - referenced):
        warn(f"Suricata SID {sid} has no matching Wazuh rule (alerts will use the generic rule 86601)")
    for sid in sorted(referenced - sample_sids):
        warn(f"No sample event covers Suricata SID {sid}; add one to the tests directory")

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR:   {e}")
    print(
        f"\nChecked {len(sids)} Suricata rule(s), {len(rules)} Wazuh rule(s): "
        f"{len(errors)} error(s), {len(warnings)} warning(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
