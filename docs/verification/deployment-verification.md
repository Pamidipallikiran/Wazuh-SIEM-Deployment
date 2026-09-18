# Deployment Verification

## Verification Date

2026-09-18

## Lab Topology

| Component | Host | IP | Status |
|---|---|---|---|
| Wazuh Manager | kiran-VirtualBox | 192.168.1.7 | Active |
| Wazuh Dashboard | kiran-VirtualBox | 192.168.1.7 | Active |
| Wazuh Agent | roshan-VirtualBox | 192.168.1.5 | Active |
| Suricata IDS | roshan-VirtualBox | 192.168.1.5 | Active |

## Wazuh Manager Verification

The Wazuh Manager service was verified as active.

The manager is listening on:

- TCP 1514 — Wazuh agent communication
- TCP 1515 — Wazuh agent enrollment/authentication

The Wazuh Dashboard is listening on:

- TCP 443 — HTTPS

## Agent Verification

Wazuh Agent ID `007` (`roshan-VirtualBox`) was verified as Active.

The agent successfully established TCP connections to:

`192.168.1.7:1514`

The agent configuration was tested with:

    sudo /var/ossec/bin/wazuh-agentd -t

No configuration error was reported.

## Suricata Verification

Suricata was verified as active on the monitored endpoint.

Version:

    Suricata 8.0.0 RELEASE

The configuration was validated successfully with:

    sudo suricata -T -c /etc/suricata/suricata.yaml

The deployed interface is:

    enp0s3

## Custom Detection

The lab custom Suricata rule uses SID `1000001`:

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo Request Detected"; itype:8; sid:1000001; rev:1;)

Suricata generated EVE JSON events containing:

    event_type: alert
    proto: ICMP
    icmp_type: 8
    signature_id: 1000001
    signature: LAB ICMP Echo Request Detected

## Wazuh Custom Rules

The Wazuh Manager contains the following custom rules:

- `910009` — matches Suricata SID `1000001`
- `910010` — aggregates repeated matching events within 30 seconds

The built-in Suricata processing rule used by the custom rule chain is:

- `86601`

## End-to-End Pipeline

    ICMP Echo Request
            |
            v
        Suricata
            |
            | SID 1000001
            v
    /var/log/suricata/eve.json
            |
            v
      Wazuh Agent 007
            |
            | TCP 1514
            v
      Wazuh Manager
            |
            | Rule 86601
            v
        Rule 910009
            |
            | repeated events
            v
        Rule 910010
            |
            v
      Wazuh Dashboard

## Verification Result

The Wazuh Manager, Wazuh Agent, and Suricata services were verified as operational.

The Suricata custom detection generated live EVE JSON events, and the Wazuh Agent successfully maintained communication with the Wazuh Manager.

The end-to-end Suricata-to-Wazuh detection pipeline is operational for the documented ICMP test case.

## Known Separate Issue

The Wazuh Agent has previously reported a journald log-collector message:

    Failed to get the message from the journal

This does not prevent collection of the Suricata EVE JSON file and is documented separately in the troubleshooting documentation.

## Scope

This verification covers:

- Wazuh Manager
- Wazuh Dashboard service
- Wazuh Agent 007
- Suricata IDS
- Suricata EVE JSON collection
- Custom Suricata SID 1000001
- Wazuh custom rules 910009 and 910010

TheHive/Cortex integration is not included in this verification because it has not been separately validated in this deployment.
