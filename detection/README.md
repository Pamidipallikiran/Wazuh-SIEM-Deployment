# Detection Catalog

Single index of every custom detection in this repository, linking the network
signature (Suricata), the SIEM rule (Wazuh), ATT&CK mapping, and validation status.

## Pipeline

```text
Suricata SID  ->  eve.json  ->  Wazuh rule 86601 (built-in)  ->  Wazuh custom rule  ->  alert
```

All custom Wazuh rules chain from the built-in Suricata rule `86601` and select
the signature with `alert.signature_id`.

## Catalog

| Detection | Suricata SID | Wazuh rule | Level | MITRE ATT&CK | Trigger | Status |
|---|---|---|---|---|---|---|
| ICMP Echo Request | 1000001 | 910009 | 5 | not mapped (single ping is not malicious by itself) | any Echo Request to `$HOME_NET` | **Verified** (see [verification](../docs/verification/deployment-verification.md)) |
| ICMP Echo aggregation | n/a (Wazuh frequency rule) | 910010 | 12 | not mapped | 2 x rule 910009 within 30 s | **Verified** |
| TCP SYN scan | 1000002 | 910011 | 8 | T1046 Network Service Discovery | 20+ SYNs from one source in 10 s | Written, **not yet lab-verified** |
| SSH connection burst | 1000003 | 910012 | 10 | T1110 Brute Force | 5+ SYNs to TCP/22 from one source in 60 s | Written, **not yet lab-verified** |
| ICMP flood | 1000004 | 910013 | 10 | T1498 Network Denial of Service | 20+ Echo Requests from one source in 5 s | Written, **not yet lab-verified** |

"Verified" means it was exercised end to end in the lab and recorded in the
verification document. Rows marked "not yet lab-verified" pass static checks
(`scripts/validate_rules.py`) but must be run through the checklist below before
being promoted.

## Promoting a detection to Verified

1. `python3 scripts/validate_rules.py` passes.
2. On the endpoint: `sudo suricata -T -c /etc/suricata/suricata.yaml` passes with the rule installed.
3. On the manager: `sudo /var/ossec/bin/wazuh-analysisd -t` passes, and the matching sample in
   [`wazuh/manager/rules/tests/`](../wazuh/manager/rules/tests/) produces the expected rule in `wazuh-logtest`.
4. Generate traffic with `scripts/generate-test-events.sh` from a second host.
5. Confirm the Suricata event in `eve.json` and the Wazuh alert in `alerts.json` / the Dashboard.
6. Record date, source, and result in `docs/verification/deployment-verification.md`, then change the status above.

## Known limitations and tuning notes

- **Rule 910010 is not scoped per source.** It fires when two matching alerts occur within 30 s,
  regardless of which hosts sent them, so two different hosts each pinging once will trigger it.
  To scope it to a single source, add a `same_field` condition on the decoded source address.
  Verify the field name in `wazuh-logtest` first, then re-run the verification steps above:

  ```xml
  <rule id="910010" level="12" frequency="2" timeframe="30">
    <if_matched_sid>910009</if_matched_sid>
    <same_field>src_ip</same_field>
    ...
  ```

  The original rule is left unchanged here because it is the one recorded as verified.
- **Thresholds are lab-sized.** The scan/SSH/flood limits are intentionally low so they can be triggered
  with a handful of packets. Raise them on production networks, and suppress known scanners
  (vulnerability scanners, monitoring probes) with a Suricata `suppress` entry in `threshold.config`.
- **Rule IDs.** Wazuh reserves 100000-120000 for user rules. The lab uses 9100xx, which works but sits
  outside the conventional range. New rules in this repo continue the 9100xx sequence for consistency.
- **SID 1000001 has no `classtype`.** It predates the classification convention and is left at `rev:1`
  to match the verified documentation. Add one with a `rev:2` bump if you want it classified.
