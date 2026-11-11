# Hardening Checklist

The lab is intentionally simple. Before using this design on anything resembling a
production network, work through the items below. Each item is a recommendation to
apply and test in your own environment; none of it has been applied to the lab described
in the verification document unless stated there.

## Wazuh Manager, Indexer and Dashboard

- [ ] Replace every default password (indexer, dashboard, API users) using the Wazuh
      password-change tooling for your installed version, then restart the affected services.
- [ ] Replace the demo TLS certificates with certificates from your own CA.
- [ ] Restrict the Dashboard (TCP 443) to the analyst subnet, not the whole network.
- [ ] Require a password for agent enrollment (TCP 1515): set `<use_password>yes</use_password>`
      in the manager's `<auth>` block and store the secret in `/var/ossec/etc/authd.pass`.
- [ ] Keep Manager, Indexer, Dashboard and agents on matching, supported versions; upgrade
      the Manager before the agents.
- [ ] Back up `/var/ossec/etc/` (including `rules/local_rules.xml`), and the Indexer data or snapshots.

## Network exposure

Allow only what the pipeline needs. Example with `ufw` on the manager (adjust addresses):

```bash
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.5 to any port 1514 proto tcp   # agent events
sudo ufw allow from 192.168.1.5 to any port 1515 proto tcp   # enrollment (remove after enrolling)
sudo ufw allow from <analyst-subnet> to any port 443 proto tcp
sudo ufw allow from <admin-host> to any port 22 proto tcp
sudo ufw enable
```

Close TCP 1515 once all agents are enrolled, and re-open it only when adding agents.

## Suricata endpoint

- [ ] Keep managed rules current with `suricata-update` and keep local rules in a separate file
      (already the design here: `/etc/suricata/rules/local.rules`).
- [ ] Set `HOME_NET` in `suricata.yaml` to the networks you actually own so rules using `$HOME_NET` match correctly.
- [ ] If running in a VM, disable NIC checksum offload on the monitored interface or Suricata may
      ignore packets with "bad" checksums (see `troubleshooting/README.md`).
- [ ] Plan log retention: confirm `eve.json` is rotated and that rotation makes Suricata reopen the file.
      Because this lab's service override avoids the Suricata control socket, test the rotation
      end to end instead of assuming the packaged logrotate hook works.
- [ ] Review which EVE `types` you actually need. Fewer event types means less disk usage and less
      noise sent to the SIEM; the `alert` type is the only one the custom rules require.

## Endpoint SSH (supports the SSH detection)

- [ ] Prefer key-based authentication and set `PasswordAuthentication no` where practical.
- [ ] Set `PermitRootLogin no`.
- [ ] Consider `MaxAuthTries` and a rate limiter (`ufw limit 22/tcp` or fail2ban) as a preventive
      control alongside the detection.

## Detection operations

- [ ] Review the Dashboard daily for levels 10 and above; tune levels and thresholds from observed noise.
- [ ] Suppress known-good scanners and monitors explicitly, and document each suppression.
- [ ] Re-run `scripts/validate_rules.py` and the verification checklist after every rule change.
- [ ] Alert on the pipeline itself: use `scripts/check-pipeline.sh` (or a Wazuh rule on agent
      disconnects) so a silent sensor is noticed.
