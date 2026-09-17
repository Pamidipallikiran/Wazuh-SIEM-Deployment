# Wazuh Agent Configuration

The Wazuh Agent is deployed on the same Ubuntu system as Suricata.

## Architecture

    Suricata
       |
       | /var/log/suricata/eve.json
       v
    Wazuh Agent
       |
       | TCP 1514
       v
    Wazuh Manager

## Wazuh Manager Connection

The deployed agent connects to the Wazuh Manager using TCP port 1514.

Manager address used in the lab:

    192.168.1.7

Protocol:

    TCP

Port:

    1514

## Suricata EVE JSON Collection

The Wazuh Agent collects Suricata events from:

    /var/log/suricata/eve.json

The relevant Wazuh Agent configuration is:

    <localfile>
      <log_format>json</log_format>
      <location>/var/log/suricata/eve.json</location>
    </localfile>

## Verification

The Wazuh log collector was verified to analyze the Suricata EVE JSON file.

The agent successfully connected to the Wazuh Manager:

    (4102): Connected to the server ([192.168.1.7]:1514/tcp).

Agent ID used in the lab:

    007
