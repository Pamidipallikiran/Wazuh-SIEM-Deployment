# Changelog

All notable changes to this repository are recorded here.

## Unreleased

### Added
- Detection rules for TCP SYN scan (SID 1000002), SSH connection burst (SID 1000003) and ICMP
  flood (SID 1000004), with matching Wazuh rules 910011 to 910013 mapped to MITRE ATT&CK
  T1046, T1110 and T1498. **Not yet verified against live lab traffic.**
- `scripts/validate_rules.py`: dependency-free validator for Suricata rules, Wazuh rules,
  cross-references between them, and sample events.
- `scripts/check-pipeline.sh`: layered health check for the agent and manager hosts.
- `scripts/generate-test-events.sh`: bounded test-traffic generator (private targets only,
  explicit authorization flag required).
- `wazuh/manager/rules/tests/`: sample EVE alert events and `wazuh-logtest` instructions.
- `.github/workflows/validate.yml`: CI running the validator, XML checks, shell syntax checks
  and a Suricata `-T` rule load test.
- `detection/README.md`: detection catalog with status, ATT&CK mapping, promotion checklist
  and known limitations.
- `docs/soc/investigation-playbooks.md`: triage playbooks and an incident record template.
- `docs/hardening/hardening.md`: production hardening checklist.
- Troubleshooting sections for custom rules that do not fire, VM capture problems, and
  threshold behavior.

### Changed
- README: fixed an unclosed code block that swallowed the "Security Event Flow" section;
  added a detection coverage table, validation section and updated repository tree.
- `suricata.yaml.example`: documented the rule-file configuration already described in the docs.

### Unchanged on purpose
- SID 1000001 and Wazuh rules 910009 / 910010 are untouched, because the deployment
  verification records them as tested in their current form.
