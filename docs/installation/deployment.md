# Installation and Deployment

## 1. Wazuh Manager

The Wazuh Manager is deployed on the management system.

Lab Manager address:

    192.168.1.7

Verify the manager service:

    sudo systemctl is-active wazuh-manager
    sudo systemctl is-enabled wazuh-manager

The expected state is:

    active
    enabled

## 2. Wazuh Dashboard

The Wazuh Dashboard is deployed on the manager system and is exposed through HTTPS.

Verify the dashboard service:

    sudo systemctl is-active wazuh-dashboard
    sudo systemctl is-enabled wazuh-dashboard

Verify HTTPS listening:

    sudo ss -lntp | grep ":443"

## 3. Wazuh Agent

The Wazuh Agent is installed on the monitored endpoint together with Suricata.

Lab Agent address:

    192.168.1.5

Lab Agent ID:

    007

The agent connects to the Wazuh Manager using TCP 1514.

Verify the agent service:

    sudo systemctl is-active wazuh-agent
    sudo systemctl is-enabled wazuh-agent

## 4. Suricata

Suricata is installed on the same endpoint as the Wazuh Agent.

The lab uses the enp0s3 network interface.

Verify Suricata:

    sudo systemctl is-active suricata
    sudo systemctl is-enabled suricata

Validate the Suricata configuration:

    sudo suricata -T -c /etc/suricata/suricata.yaml

## 5. Custom Suricata Rule

The lab custom rule is stored separately from the managed rule set:

    /etc/suricata/rules/local.rules

The custom rule uses SID 1000001:

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo Request Detected"; itype:8; sid:1000001; rev:1;)

The Suricata configuration loads both the managed rules and the local rule file.

## 6. Suricata EVE JSON

Suricata writes JSON events to:

    /var/log/suricata/eve.json

The Wazuh Agent reads this file using a JSON localfile configuration.

## 7. Wazuh Agent to Manager Verification

On the manager, verify the registered agent:

    sudo /var/ossec/bin/agent_control -l

The lab verification showed Agent 007 as Active.

Verify that Wazuh Manager is listening on TCP 1514:

    sudo ss -lntp | grep ":1514"

## 8. End-to-End Test

From the Wazuh Manager, generate one controlled ICMP request:

    ping -c 1 192.168.1.5

On the agent, verify the Suricata alert:

    sudo grep -a "\"signature_id\":1000001" /var/log/suricata/eve.json | tail

On the manager, verify the corresponding Wazuh alert in alerts.json.

## 9. Validation Result

The deployment was successfully validated from network traffic through Suricata, Wazuh Agent, Wazuh Manager, and the Wazuh Dashboard.
