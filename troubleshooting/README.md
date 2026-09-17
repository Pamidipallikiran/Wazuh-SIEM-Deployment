# Troubleshooting Guide

## 1. Wazuh Agent Cannot Connect to Manager

### Symptoms

The Wazuh Agent repeatedly attempts to connect to the manager but does not establish a session.

### Checks

On the agent:

    sudo grep -E "Trying to connect|Connected to the server" /var/ossec/logs/ossec.log | tail -20

On the manager:

    sudo ss -lntp | grep ":1514"

Verify the agent configuration points to the correct manager address and TCP port 1514.

## 2. Suricata Is Not Running

### Checks

    sudo systemctl status suricata --no-pager
    sudo systemctl is-active suricata

Validate the configuration before restarting:

    sudo suricata -T -c /etc/suricata/suricata.yaml

## 3. Custom Suricata Rule Is Not Loaded

Verify the rule exists:

    sudo cat /etc/suricata/rules/local.rules

Verify that the local rule file is referenced by suricata.yaml.

The deployed configuration contains:

    rule-files:
      - suricata.rules
      - /etc/suricata/rules/local.rules

Then validate:

    sudo suricata -T -c /etc/suricata/suricata.yaml

## 4. Suricata Generates Events but Wazuh Does Not Receive Them

Verify that Suricata is generating the expected event:

    sudo grep -a "\"signature_id\":1000001" /var/log/suricata/eve.json | tail -5

Verify the Wazuh Agent is configured to monitor the EVE JSON file:

    /var/log/suricata/eve.json

Check the Wazuh log collector:

    sudo grep "Analyzing file" /var/ossec/logs/ossec.log | grep suricata

## 5. Wazuh Alert Exists but Dashboard Does Not Show It

Verify the Wazuh Manager is running:

    sudo systemctl is-active wazuh-manager

Verify that alerts are being generated:

    sudo tail -n 50 /var/ossec/logs/alerts/alerts.json

Verify the Dashboard service:

    sudo systemctl is-active wazuh-dashboard
    sudo ss -lntp | grep ":443"

## 6. Suricata Service Restart Problems

The lab uses a systemd override so that the Suricata service can be stopped cleanly without relying on the Suricata control socket.

The override uses SIGTERM for service termination and provides the runtime directory required by the service.

After modifying the service configuration:

    sudo systemctl daemon-reload
    sudo systemctl restart suricata

Verify:

    sudo systemctl is-active suricata
    pgrep -a -f suricata

## 7. Noisy Suricata Alerts

The lab observed Suricata alerts such as "SURICATA Ethertype unknown" in addition to the controlled ICMP detection.

These events demonstrate that the managed Suricata rules are also active.

The lab custom rule was kept separate and was not added to the managed rule file.

No suppression or modification of the managed detection was performed during the initial deployment validation.

## 8. Large EVE JSON File

Suricata EVE JSON can grow significantly in an active lab environment.

Inspect recent events rather than repeatedly scanning the entire file:

    sudo tail -n 100 /var/log/suricata/eve.json

For the custom detection, use a targeted search:

    sudo grep -a "\"signature_id\":1000001" /var/log/suricata/eve.json | tail -5

Runtime logs and EVE JSON files are intentionally excluded from this Git repository.

## 9. General Recovery Procedure

When troubleshooting the pipeline, verify each layer in order:

    1. Network traffic
    2. Suricata service
    3. Suricata EVE JSON event
    4. Wazuh Agent log collector
    5. Wazuh Agent connection to Manager
    6. Wazuh Manager alert processing
    7. Wazuh Dashboard

This layered approach helps identify which component is responsible for an event-collection failure.
