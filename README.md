# BasiXenuM

BasiXenuM runs one Nmap scan, keeps its output in a dated folder, and turns the open-port list into a text report. It is for authorized labs and CTF targets; it does not exploit anything.

## Install

You need Python 3.10+ and `nmap` on your `PATH`. The scan uses `-sS -sC -sV`, so SYN scanning may need elevated privileges.

```bash
git clone https://github.com/foxcryptie/BasiXenuM.git
cd BasiXenuM
python -m pip install -e .
basixenum version
```

## Run a scan

```bash
basixenum enum 10.10.10.10 --profile lab
```

The target and profile become part of the output path: `out/lab/10.10.10.10/<timestamp>/`. Nmap writes `.nmap`, `.gnmap`, and `.xml` files there; BasiXenuM writes `triage_report.txt`. You can change the root folder with `--out`.

Run `basixenum` without arguments to enter the target interactively. With a target on the command line, the command runs without prompts. `--dry-run` prints the Nmap command without starting a scan or writing output files.

Follow-up tools are opt-in for command-line runs:

```bash
basixenum enum 10.10.10.10 --profile lab --run-followups
```

If the scan detects a web or SMB service, the follow-up step tries `ffuf` or `netexec`. Those tools are optional; install them separately before using the flag. `ffuf` also expects `/usr/share/seclists/Discovery/Web-Content/raft-medium-files-lowercase.txt`.

## Limits

- The Nmap flags are fixed. There is no RustScan or UDP workflow yet.
- The web follow-up currently builds `http://<target>/FUZZ`, so it misses HTTPS and non-default ports. Check the detected service before using it.
- The report is a set of leads from service names and banners. It does not verify vulnerabilities or tell you whether a target is exploitable.

Run the parser, CLI, and follow-up runner tests with `python -m unittest discover -s tests -v`.

Only scan systems you own or have permission to test.


