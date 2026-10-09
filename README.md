# BasiXenuM

BasiXenuM is a Python CLI for baseline reconnaissance in **authorized labs and CTFs**. It runs Nmap, organizes the output, and writes a triage report to help decide what to inspect next.

## What it currently does

- Runs `nmap -sS -sC -sV` against one target.
- Saves Nmap's normal, greppable, and XML output in a timestamped folder.
- Parses open ports and writes a service-focused triage report.
- Optionally runs `ffuf` for detected web services and `netexec` for detected SMB services, then adds their findings to the report.

The tool does not exploit targets. Only scan systems you own or are authorized to test.

## Requirements

- Python 3.10 or newer
- Nmap on your `PATH`; SYN scanning may require elevated privileges
- Optional: `ffuf`, `netexec`, and the wordlist at `/usr/share/seclists/Discovery/Web-Content/raft-medium-files-lowercase.txt` for follow-up tasks

## Install

```bash
git clone https://github.com/foxcryptie/BasiXenuM.git
cd BasiXenuM
python -m pip install -e .
basixenum version
```

## Run

Interactive:

```bash
basixenum
```

With a target:

```bash
basixenum enum 10.10.10.10 --profile lab
```

The current CLI still asks whether to save a text log and run follow-up tasks. To request follow-up tasks with a flag:

```bash
basixenum enum 10.10.10.10 --profile lab --run-followups
```

Outputs are written under `out/<profile>/<target>/<timestamp>/`. A typical run produces `nmap.nmap`, `nmap.gnmap`, `nmap.xml`, and `triage_report.txt`. Optional follow-ups produce their own output files.

## Current limits

The scan command is currently fixed to `nmap -sS -sC -sV`. The CLI accepts mode, RustScan, custom Nmap, and UDP options, but those options are not yet connected to the scan command. The web follow-up currently assumes HTTP on the target's default port and a local SecLists wordlist. No automated tests are included yet.

## Next improvements

- Connect scan flags to the Nmap/RustScan workflow.
- Make web follow-ups use detected schemes and ports.
- Add parser and CLI tests.
