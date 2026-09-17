# SIEM Deployment Architecture

## Overview

This project implements a distributed SIEM lab using Wazuh and Suricata.

Suricata and the Wazuh Agent run together on the monitored Ubuntu endpoint. The Wazuh Manager and Wazuh Dashboard run on a separate system.

## Architecture

    NETWORK TRAFFIC
          |
          v
    +-------------+
    |  Suricata   |
    |     IDS     |
    +-------------+
          |
          | EVE JSON
          v
    /var/log/suricata/eve.json
          |
          v
    +-------------+
    | Wazuh Agent |
    |    ID 007   |
    +-------------+
          |
          | TCP 1514
          v
    +-------------+
    |    Wazuh    |
    |   Manager   |
    +-------------+
          |
          | Processed Alerts
          v
    +-------------+
    |    Wazuh    |
    |  Dashboard  |
    +-------------+
          |
          v
     SOC Analyst

## Lab Systems

### Wazuh Manager

    IP Address: 192.168.1.7
    Services:
      - Wazuh Manager
      - Wazuh Dashboard

### Monitored Endpoint

    IP Address: 192.168.1.5
    Agent ID: 007
    Services:
      - Wazuh Agent
      - Suricata IDS

## Event Flow

1. Network traffic reaches the monitored endpoint.
2. Suricata inspects the traffic using its IDS rules.
3. Matching traffic generates an EVE JSON event.
4. Wazuh Agent reads /var/log/suricata/eve.json.
5. The agent forwards the event to the Wazuh Manager over TCP 1514.
6. Wazuh processes the event using its Suricata rules.
7. The alert becomes available to the Wazuh Dashboard.
8. A SOC analyst can investigate the resulting security event.

## Custom Detection

The lab maintains custom Suricata rules separately from the managed rule set.

Custom rule location on the monitored endpoint:

    /etc/suricata/rules/local.rules

The custom ICMP rule uses SID 1000001.

## Design Principle

The managed Suricata rule file is not modified. Local detection rules are maintained separately so that managed rules and lab-specific detections remain distinct.
