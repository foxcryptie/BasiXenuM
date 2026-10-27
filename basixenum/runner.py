import subprocess
from pathlib import Path
from basixenum.tasks.base import TaskResult, ReconTask


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value or ""


def run_task(task: ReconTask, outdir: Path) -> TaskResult:
    stdout_file = outdir / f"{task.name}.stdout.txt"
    stderr_file = outdir / f"{task.name}.stderr.txt"

    try:
        proc = subprocess.run(
            task.command,
            capture_output=True,
            text=True,
            timeout=task.timeout
        )
        stdout = proc.stdout
        stderr = proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = _text(e.stdout)
        stderr = _text(e.stderr) + "\n[TIMEOUT]"
        rc = -1
    except FileNotFoundError:
        stdout = ""
        stderr = f"Required command not found: {task.command[0]}"
        rc = 127

    stdout_file.write_text(stdout, encoding="utf-8", errors="ignore")
    stderr_file.write_text(stderr, encoding="utf-8", errors="ignore")

    findings = task.parse_output(stdout, stderr)

    return TaskResult(
        name=task.name,
        command=task.command,
        returncode=rc,
        stdout=stdout,
        stderr=stderr,
        findings=findings,
        artifacts=[str(stdout_file), str(stderr_file)]
    )



