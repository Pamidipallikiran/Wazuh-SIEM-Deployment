# ICMP Detection Test

## Objective

Verify the complete Suricata to Wazuh detection pipeline.

## Test Environment

    Wazuh Manager:       192.168.1.7
    Wazuh Agent:         192.168.1.5
    Wazuh Agent ID:      007
    Wazuh Agent Port:    TCP 1514
    Suricata Interface:  enp0s3
    Suricata Custom SID: 1000001

## Detection Rule

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP Echo Request Detected"; itype:8; sid:1000001; rev:1;)

## Test Command

The controlled test was executed from the Wazuh Manager:

    ping -c 1 192.168.1.5

## Suricata Result

Suricata generated an EVE JSON alert containing:

    event_type: alert
    src_ip: 192.168.1.7
    dest_ip: 192.168.1.5
    proto: ICMP
    icmp_type: 8
    signature_id: 1000001
    signature: LAB ICMP Echo Request Detected

The original controlled test was generated from the Wazuh Manager (192.168.1.7).

Additional live verification events were later observed from source 192.168.1.14.

## Wazuh Result

The Wazuh Manager processed the Suricata alert using Wazuh rule 86601.

The resulting event identified:

    Agent: 007
    Suricata SID: 1000001
    Signature: LAB ICMP Echo Request Detected

## End-to-End Flow

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
       alerts.json
           |
           v
     Wazuh Dashboard

## Result

The controlled test successfully demonstrated end-to-end event collection and detection.
