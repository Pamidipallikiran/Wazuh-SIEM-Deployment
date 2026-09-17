# Suricata Custom Rules

This directory contains custom Suricata detection rules used by the SIEM lab.

## Custom Rule

The lab uses SID `1000001` to detect ICMP Echo Request traffic:

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo Request Detected"; itype:8; sid:1000001; rev:1;)

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
