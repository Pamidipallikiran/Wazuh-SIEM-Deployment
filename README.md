# SIEM Deployment Lab

A practical **Security Information and Event Management (SIEM)** deployment project using **Wazuh SIEM** and **Suricata IDS** for centralized security monitoring, endpoint visibility, network threat detection, alert analysis, and incident investigation.

---

## 📌 Project Overview

This project demonstrates the deployment and integration of a security monitoring environment using Wazuh and Suricata.

The environment is designed to simulate a real-world SOC monitoring workflow where security events from endpoints and network traffic are collected, analyzed, correlated, and presented to security analysts through the Wazuh Dashboard.

### Primary Objectives

* Deploy a functional Wazuh SIEM environment.
* Collect and monitor endpoint security events.
* Deploy Suricata as a Network Intrusion Detection System (NIDS).
* Integrate Suricata alerts with Wazuh.
* Create and test custom detection rules.
* Monitor authentication and system activity.
* Detect suspicious network activity.
* Investigate generated security alerts.
* Document the complete SIEM deployment and detection workflow.

---

## 🏗️ Architecture


This project uses a distributed SIEM architecture in which the Wazuh Manager and Wazuh Dashboard are deployed on a dedicated SIEM server, while the Wazuh Agent and Suricata IDS are deployed on a monitored endpoint.

```text
                         NETWORK TRAFFIC
                               |
                               v
                    +----------------------+
                    |     Suricata IDS     |
                    |   Network Detection  |
                    +----------+-----------+
                               |
                          eve.json
                               |
                               v
                    +----------------------+
                    |      Wazuh Agent     |
                    |                      |
                    |  Log Collection      |
                    |  File Integrity      |
                    |  System Monitoring   |
                    +----------+-----------+
                               |
                               | Security Events
                               |
                               v
                    +----------------------+
                    |    Wazuh Manager     |
                    |                      |
                    | Event Processing     |
                    | Detection Rules      |
                    | Alert Generation     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Wazuh Dashboard    |
                    | Monitoring & Analysis |
                    +----------+-----------+
                               |
                               v
                       SOC ANALYST
                    Investigation & Response
---

## 🔄 Security Event Flow

The project follows this general security monitoring process:

```text
Endpoint / Network Activity
            |
            v
     Log / Network Event
            |
            v
       Data Collection
            |
            v
       Wazuh Processing
            |
            v
      Detection Rules
            |
            v
       Security Alert
            |
            v
    Wazuh Dashboard
            |
            v
     SOC Investigation
            |
            v
   Incident Identification
```

For network-based detections:

```text
Network Traffic
      |
      v
Suricata IDS
      |
      v
Suricata Detection Rule
      |
      v
eve.json
      |
      v
Wazuh Agent
      |
      v
Wazuh Manager
      |
      v
Wazuh Alert
      |
      v
Wazuh Dashboard
      |
      v
SOC Analyst Investigation
```

---

## 🛠️ Technologies Used

| Technology          | Purpose                                              |
| ------------------- | ---------------------------------------------------- |
| **Wazuh**           | SIEM, endpoint monitoring and security analytics     |
| **Wazuh Manager**   | Event processing, rule matching and alert generation |
| **Wazuh Agent**     | Endpoint log collection and monitoring               |
| **Wazuh Dashboard** | Security monitoring and alert visualization          |
| **Suricata**        | Network Intrusion Detection System                   |
| **Ubuntu Linux**    | SIEM and security monitoring platform                |
| **Syslog**          | Security and system log collection                   |
| **EVE JSON**        | Suricata structured event logging                    |
| **Custom Rules**    | Organization-specific threat detection               |
| **MITRE ATT&CK**    | Threat technique classification                      |

---

## 🔐 Wazuh SIEM

Wazuh is used as the central security monitoring platform.

The Wazuh environment provides:

* Endpoint monitoring
* Security event collection
* Log analysis
* Authentication monitoring
* File Integrity Monitoring
* Vulnerability monitoring
* Custom detection rules
* Security alert generation
* Dashboard-based investigation

### Wazuh Components

```text
Wazuh Agent
     |
     | Security Events
     v
Wazuh Manager
     |
     | Detection / Processing
     v
Wazuh Indexer
     |
     v
Wazuh Dashboard
```

---

## 🛡️ Suricata IDS

Suricata is deployed as the network intrusion detection component of the environment.

It monitors network traffic and generates security events when traffic matches configured detection rules.

Suricata provides:

* Network traffic monitoring
* Intrusion detection
* Protocol analysis
* Custom detection rules
* Network security alerts
* Structured EVE JSON logging

### Suricata Log

The primary structured event log used in this project is:

```text
/var/log/suricata/eve.json
```

The EVE JSON format allows security events to be consumed and analyzed by other security monitoring components.

---

## 🚨 Detection Capabilities

The lab can be used to demonstrate detection of different types of security activity.

### Network-Based Detection

* ICMP activity
* ICMP flood / suspicious ICMP traffic
* Port scanning
* Suspicious network traffic
* Custom Suricata signatures
* Network reconnaissance

### Endpoint-Based Detection

* Failed authentication attempts
* Successful authentication events
* Privilege-related activity
* File modifications
* Suspicious system activity
* File Integrity Monitoring events

---

## 🧪 Detection Testing

Security detections are tested in the lab environment by generating controlled events and verifying that the complete detection pipeline works correctly.

Example:

```text
Test Activity
      |
      v
Security Event Generated
      |
      v
Suricata / Wazuh Collects Event
      |
      v
Detection Rule Matches
      |
      v
Alert Generated
      |
      v
Wazuh Dashboard
      |
      v
SOC Analyst Investigation
```

Each detection test can be documented with:

* Test objective
* Attack simulation
* Detection rule
* Generated log
* Wazuh alert
* Severity
* MITRE ATT&CK mapping
* Analyst investigation
* Recommended response

---

## 📁 Repository Structure

```text
siem-deployment/
│
├── README.md
├── .gitignore
│
├── deployment/
│   ├── install-wazuh.sh
│   ├── install-suricata.sh
│   └── configure-siem.sh
│
├── detection/
│   ├── network-attacks.md
│   ├── custom-rules.md
│   └── alert-examples.md
│
├── docs/
│   ├── architecture/
│   │   └── siem-architecture.png
│   │
│   ├── installation/
│   │   └── installation-guide.md
│   │
│   └── screenshots/
│
├── suricata/
│   ├── suricata.yaml
│   ├── rules/
│   │   └── local.rules
│   │
│   └── eve-json/
│       └── README.md
│
├── wazuh/
│   ├── manager/
│   │   ├── ossec.conf
│   │   └── rules/
│   │       └── local_rules.xml
│   │
│   ├── agent/
│   │   └── agent-config.md
│   │
│   └── dashboard/
│
└── troubleshooting/
    └── common-issues.md
```

---

## 📚 Documentation

The repository contains documentation covering:

### Installation

Step-by-step installation and configuration of:

* Wazuh Manager
* Wazuh Agent
* Wazuh Dashboard
* Suricata IDS

### Configuration

Configuration examples for:

* Wazuh Manager
* Wazuh Agents
* Suricata
* Custom detection rules
* Log collection

### Detection Engineering

Documentation of:

* Custom Wazuh rules
* Custom Suricata rules
* Detection testing
* Alert investigation
* MITRE ATT&CK mapping

### Troubleshooting

Common deployment and integration problems are documented along with their solutions.

---

## 📸 Screenshots

Screenshots of the deployment and detection results will be added under:

```text
docs/screenshots/
```

Examples include:

* Wazuh Dashboard
* Wazuh agents
* Security alerts
* Suricata alerts
* Custom rule detections
* Detection test results

---

## 🔎 Example SOC Investigation Workflow

A typical investigation in this lab follows:

```text
1. Alert Generated
        |
        v
2. Analyst Reviews Alert
        |
        v
3. Identify Source IP / Host
        |
        v
4. Analyze Event Details
        |
        v
5. Identify Detection Rule
        |
        v
6. Map Activity to MITRE ATT&CK
        |
        v
7. Determine Severity
        |
        v
8. Investigate Related Events
        |
        v
9. Containment / Response
        |
        v
10. Document the Incident
```

---

## 🎯 Project Outcomes

This project demonstrates practical experience with:

* SIEM deployment
* Security monitoring
* Endpoint log collection
* Network intrusion detection
* Detection engineering
* Custom security rules
* Security alert analysis
* Log investigation
* SOC workflows
* Network security monitoring
* Linux security administration
* Incident investigation

---

## 🚀 Future Improvements

Planned improvements include:

* Automated incident response
* SOAR integration
* TheHive case management
* Cortex analyzer integration
* MISP threat intelligence enrichment
* Automated IOC enrichment
* Additional MITRE ATT&CK mappings
* Advanced detection rules
* Threat hunting workflows
* Automated alert correlation
* Security dashboards and reports

---

## ⚠️ Disclaimer

This project is intended for **educational purposes and authorized security testing only**.

All security testing should be performed in an isolated lab environment or on systems for which you have explicit authorization.

No real-world systems or networks should be targeted without appropriate permission.

---

## 👨‍💻 Author

**Kiran Pamidipalli**

Cybersecurity | SOC | SIEM | Network Security

---

## ⭐ Project Focus

> Building a practical SOC monitoring environment for detecting, investigating, and responding to security events using open-source security technologies.
