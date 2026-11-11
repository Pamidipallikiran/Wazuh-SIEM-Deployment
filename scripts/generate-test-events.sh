#!/usr/bin/env bash
# Generate small, bounded, controlled traffic to exercise the lab detections.
# Run it from a DIFFERENT host than the Suricata endpoint (for example the Wazuh
# Manager), because Suricata inspects traffic arriving on the monitored interface.
#
# Usage:
#   ./scripts/generate-test-events.sh --target 192.168.1.5 --test icmp --i-have-authorization
#
# Tests (SID in parentheses):
#   icmp   one Echo Request                          (1000001)
#   scan   25 quick TCP connection attempts          (1000002)
#   ssh    8 connection attempts to TCP/22           (1000003)
#   flood  40 Echo Requests at 0.2s intervals        (1000004)
#   all    run every test above, in order
#
# Safety: only private (RFC 1918) targets are accepted, traffic volume is capped,
# and --i-have-authorization is mandatory. Use only on systems you own or are
# explicitly authorized to test.

set -u

TARGET=""; TEST=""; AUTH="no"

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --test) TEST="${2:-}"; shift 2 ;;
    --i-have-authorization) AUTH="yes"; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "$TARGET" ] && [ -n "$TEST" ] || usage
[ "$AUTH" = "yes" ] || { echo "Refusing to run without --i-have-authorization." >&2; exit 2; }

is_private_ipv4() {
  local ip="$1" a b c d
  IFS=. read -r a b c d <<<"$ip"
  for octet in "$a" "$b" "$c" "$d"; do
    case "$octet" in ''|*[!0-9]*) return 1 ;; esac
    [ "$octet" -le 255 ] || return 1
  done
  [ "$a" -eq 10 ] && return 0
  [ "$a" -eq 172 ] && [ "$b" -ge 16 ] && [ "$b" -le 31 ] && return 0
  [ "$a" -eq 192 ] && [ "$b" -eq 168 ] && return 0
  return 1
}

is_private_ipv4 "$TARGET" || { echo "Target must be a private IPv4 address (RFC 1918)." >&2; exit 2; }
command -v ping >/dev/null 2>&1 || { echo "ping is required." >&2; exit 2; }

tcp_attempt() {  # tcp_attempt PORT -> a single short connection attempt (emits a SYN)
  timeout 1 bash -c "exec 3<>/dev/tcp/${TARGET}/$1" 2>/dev/null || true
}

run_icmp()  { echo "[icmp]  1 Echo Request  -> expect SID 1000001"; ping -c 1 -W 2 "$TARGET" >/dev/null 2>&1 || true; }
run_scan()  { echo "[scan]  25 TCP attempts -> expect SID 1000002"; for p in $(seq 1000 1024); do tcp_attempt "$p"; done; }
run_ssh()   { echo "[ssh]   8 attempts to 22 -> expect SID 1000003"; for _ in $(seq 1 8); do tcp_attempt 22; sleep 0.5; done; }
run_flood() { echo "[flood] 40 Echo Requests -> expect SID 1000004"; ping -c 40 -i 0.2 -W 1 "$TARGET" >/dev/null 2>&1 || true; }

case "$TEST" in
  icmp) run_icmp ;;
  scan) run_scan ;;
  ssh) run_ssh ;;
  flood) run_flood ;;
  all) run_icmp; sleep 3; run_scan; sleep 12; run_ssh; sleep 3; run_flood ;;
  *) echo "Unknown test: $TEST" >&2; usage ;;
esac

cat <<EOF

Done. Verify on the monitored endpoint:
  sudo grep -a '"signature_id":100000' /var/log/suricata/eve.json | tail
and on the Wazuh Manager:
  sudo grep -E '"id":"9100(09|10|11|12|13)"' /var/ossec/logs/alerts/alerts.json | tail
EOF
