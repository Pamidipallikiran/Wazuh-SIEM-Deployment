# Rule Test Samples

`sample-eve-events.jsonl` contains one sanitized Suricata EVE `alert` event for each
custom Suricata SID (1000001 to 1000004). Use them to check that the Wazuh rules chain
correctly before generating live traffic.

## Test with wazuh-logtest

On the Wazuh Manager:

```bash
sudo /var/ossec/bin/wazuh-logtest
```

Paste one line from `sample-eve-events.jsonl` at the prompt and press Enter. In the output,
check **Phase 3** (filtering):

| Sample line | Expected rule | Expected level |
|---|---|---|
| 1 (SID 1000001) | 910009 | 5 |
| 2 (SID 1000002) | 910011 | 8 |
| 3 (SID 1000003) | 910012 | 10 |
| 4 (SID 1000004) | 910013 | 10 |

If the event only reaches rule `86601`, the custom rule did not match: check the
`alert.signature_id` value and that the rule file is installed at
`/var/ossec/etc/rules/local_rules.xml`. Restart the manager after changing rules:

```bash
sudo /var/ossec/bin/wazuh-analysisd -t && sudo systemctl restart wazuh-manager
```

## Static checks

Without a Wazuh install, `python3 scripts/validate_rules.py` confirms every sample is valid JSON,
is an `alert` event, and uses a SID defined in `suricata/rules/local.rules`.

The expected-rule table above is the intended behavior; it has not yet been confirmed with
`wazuh-logtest` on the lab manager. Record the result in the verification document when you do.
