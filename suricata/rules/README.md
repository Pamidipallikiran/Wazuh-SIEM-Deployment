# Suricata Custom Rules

This directory contains custom Suricata detection rules used by the SIEM lab.

## Custom Rule

The lab uses SID `1000001` to detect ICMP Echo Request traffic:

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo Request Detected"; itype:8; sid:1000001; rev:1;)

## Additional Lab Rules

`local.rules` also contains three threshold-based rules. They have been reviewed for syntax
but not yet run against live traffic in the lab (see `detection/README.md` for status).

| SID | Message | Condition | classtype |
|---|---|---|---|
| 1000002 | LAB TCP SYN Scan Detected | 20+ SYNs from one source in 10 s | attempted-recon |
| 1000003 | LAB SSH Connection Burst (possible brute force) | 5+ SYNs to TCP/22 from one source in 60 s | attempted-admin |
| 1000004 | LAB ICMP Echo Request Flood | 20+ Echo Requests from one source in 5 s | attempted-dos |

These use `threshold: type both, track by_src`, so the alert is raised once when the count is
reached, per source address, in each window. `flags:S,12` matches SYN packets while ignoring the
ECN bits, and `flow:stateless` allows matching on the first packet of a connection.

## Rule Loading

The custom rule is loaded in addition to the managed Suricata rules.

The deployed configuration contains:

    default-rule-path: /var/lib/suricata/rules

    rule-files:
      - suricata.rules
      - /etc/suricata/rules/local.rules

The managed rule file is not modified.

## Validation

The deployed configuration was validated with:

    sudo suricata -T -c /etc/suricata/suricata.yaml

Successful validation confirms that the configuration and custom rule set can be loaded.

## Testing

A controlled ICMP Echo Request was generated from the Wazuh Manager to the Wazuh Agent:

    ping -c 1 192.168.1.5

Suricata generated an EVE JSON alert containing:

    signature_id: 1000001
    signature: LAB ICMP Echo Request Detected
