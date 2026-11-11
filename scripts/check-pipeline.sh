#!/usr/bin/env bash
# Layered health check for the Suricata -> Wazuh Agent -> Wazuh Manager pipeline.
# Mirrors the "General Recovery Procedure" in troubleshooting/README.md.
#
# Usage (run as root on the relevant host):
#   sudo ./scripts/check-pipeline.sh --role agent     # Suricata + Wazuh Agent endpoint
#   sudo ./scripts/check-pipeline.sh --role manager   # Wazuh Manager + Dashboard host
#
# Exit status is the number of failed checks (0 = healthy).

set -u

ROLE=""
EVE_LOG="/var/log/suricata/eve.json"
MAX_EVE_AGE=600   # seconds; warn if EVE JSON has not been written to recently

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --role) ROLE="${2:-}"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done
case "$ROLE" in agent|manager) ;; *) usage ;; esac

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root (sudo) so service state, ports and logs can be inspected." >&2
  exit 2
fi

FAILS=0
pass() { printf '  [ OK ] %s\n' "$1"; }
fail() { printf '  [FAIL] %s\n' "$1"; FAILS=$((FAILS + 1)); }
warn() { printf '  [WARN] %s\n' "$1"; }
section() { printf '\n== %s ==\n' "$1"; }

check_service() {
  local svc="$1"
  if systemctl is-active --quiet "$svc"; then pass "$svc is active"; else fail "$svc is not active"; fi
  if systemctl is-enabled --quiet "$svc" 2>/dev/null; then pass "$svc is enabled at boot"; else warn "$svc is not enabled at boot"; fi
}

check_listening() {
  local port="$1" label="$2"
  if ss -lnt | awk '{print $4}' | grep -Eq "[:.]${port}\$"; then pass "TCP ${port} listening (${label})"; else fail "nothing listening on TCP ${port} (${label})"; fi
}

if [ "$ROLE" = "agent" ]; then
  section "1. Suricata service"
  check_service suricata
  if command -v suricata >/dev/null 2>&1; then
    if suricata -T -c /etc/suricata/suricata.yaml >/dev/null 2>&1; then pass "suricata -T configuration test passed"; else fail "suricata -T failed (run it manually to see the error)"; fi
  else
    fail "suricata binary not found"
  fi

  section "2. Suricata EVE JSON output"
  if [ -f "$EVE_LOG" ]; then
    age=$(( $(date +%s) - $(stat -c %Y "$EVE_LOG") ))
    pass "$EVE_LOG exists"
    if [ "$age" -le "$MAX_EVE_AGE" ]; then pass "EVE JSON written ${age}s ago"; else warn "EVE JSON last written ${age}s ago (quiet network or Suricata stalled)"; fi
  else
    fail "$EVE_LOG not found"
  fi

  section "3. Wazuh Agent log collector"
  check_service wazuh-agent
  if /var/ossec/bin/wazuh-agentd -t >/dev/null 2>&1; then pass "wazuh-agentd -t configuration test passed"; else fail "wazuh-agentd -t reported a configuration error"; fi
  if grep -q "Analyzing file: '$EVE_LOG'" /var/ossec/logs/ossec.log 2>/dev/null; then pass "agent is analyzing $EVE_LOG"; else fail "no 'Analyzing file' entry for $EVE_LOG in ossec.log (check the <localfile> block)"; fi

  section "4. Agent to manager connection"
  if grep -E "Connected to the server" /var/ossec/logs/ossec.log 2>/dev/null | tail -1 | grep -q .; then pass "agent has connected to the manager"; else fail "no 'Connected to the server' entry in ossec.log"; fi
  if ss -nt state established 2>/dev/null | awk '{print $4}' | grep -Eq ':1514$'; then pass "established TCP session to port 1514"; else fail "no established session to manager port 1514"; fi
fi

if [ "$ROLE" = "manager" ]; then
  section "1. Wazuh Manager"
  check_service wazuh-manager
  check_listening 1514 "agent events"
  check_listening 1515 "agent enrollment"
  if /var/ossec/bin/wazuh-analysisd -t >/dev/null 2>&1; then pass "wazuh-analysisd -t: rules and decoders load cleanly"; else fail "wazuh-analysisd -t failed (a rule file has an error)"; fi
  if [ -f /var/ossec/etc/rules/local_rules.xml ]; then pass "local_rules.xml is installed"; else fail "/var/ossec/etc/rules/local_rules.xml missing"; fi

  section "2. Registered agents"
  if /var/ossec/bin/agent_control -l 2>/dev/null | grep -q "Active"; then pass "at least one agent is Active"; else fail "no Active agents reported by agent_control -l"; fi

  section "3. Alert generation"
  alerts="/var/ossec/logs/alerts/alerts.json"
  if [ -f "$alerts" ]; then
    age=$(( $(date +%s) - $(stat -c %Y "$alerts") ))
    if [ "$age" -le "$MAX_EVE_AGE" ]; then pass "alerts.json updated ${age}s ago"; else warn "alerts.json last updated ${age}s ago"; fi
  else
    fail "$alerts not found"
  fi

  section "4. Dashboard"
  check_service wazuh-dashboard
  check_listening 443 "dashboard HTTPS"
fi

printf '\n%s\n' "Result: ${FAILS} failed check(s)."
exit "$FAILS"
