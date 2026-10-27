"""Turn Nmap's open-port list into a short, factual scan summary."""

from pathlib import Path


PORT_LABELS = {
    "WEB": {80, 443, 8000, 8080, 8443, 8888},
    "SMB": {139, 445},
    "DNS": {53},
    "LDAP": {389, 636},
    "KERBEROS": {88},
    "WINRM": {5985, 5986},
    "RDP": {3389},
    "NFS": {2049},
}


def detect_focus_labels(port_entries: list[dict]) -> list[str]:
    """Group services for optional follow-up commands; these are hints only."""
    labels = set()
    for entry in port_entries:
        port = entry["port"]
        service = entry["service"].lower()
        version = entry["version"].lower()
        for label, ports in PORT_LABELS.items():
            if port in ports:
                labels.add(label)
        if "http" in service or any(name in version for name in ("apache", "nginx", "iis")):
            labels.add("WEB")
        if "smb" in service or "netbios" in service or "samba" in version:
            labels.add("SMB")
    return sorted(labels)


def render_triage_report(
    target: str,
    outdir: Path,
    port_entries: list[dict],
    scan_time: str,
) -> str:
    """Report what Nmap found without inferring an exploit or vulnerability."""
    lines = [
        "BasiXenuM scan report",
        f"Target: {target}",
        f"Scan time: {scan_time}",
        "Command: nmap -sS -sC -sV",
        f"Output: {outdir}",
        "",
        "OPEN PORTS",
    ]

    if port_entries:
        for entry in port_entries:
            version = f" {entry['version']}" if entry["version"] else ""
            lines.append(f"- {entry['port']}/{entry['proto']} {entry['service']}{version}")
    else:
        lines.append("- None found in the Nmap text output.")

    lines.extend(["", "SERVICE GROUPS"])
    labels = detect_focus_labels(port_entries)
    lines.append(", ".join(labels) if labels else "None")
    lines.extend([
        "",
        "Service groups come from port numbers and Nmap labels. Read the raw",
        "Nmap output before deciding what to inspect next. This report does",
        "not check for vulnerabilities or confirm that a service is exploitable.",
        "",
    ])
    return "\n".join(lines)


