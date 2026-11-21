import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERPRETER = ROOT / "sloperator.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTERPRETER), *args], capture_output=True, encoding="utf-8"
    )


def test_runs_a_file():
    completed = run_cli(str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stdout == "hello, slop\n"
    assert completed.stderr == ""


def test_error_goes_to_stderr_after_earlier_output(tmp_path: Path):
    program = tmp_path / "boom.slop"
    program.write_text("hallucinate(“before”)✨\nhallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == "before\n"
    assert completed.stderr == "SlopLang runtime error at line 2: undefined variable 'missing'\n"
    assert "Traceback" not in completed.stderr


def test_division_by_zero_is_a_clean_runtime_error(tmp_path: Path):
    program = tmp_path / "divzero.slop"
    program.write_text("hallucinate(1 / 0)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == "SlopLang runtime error at line 1: division by zero\n"
    assert "Traceback" not in completed.stderr


def test_missing_file_and_usage():
    usage = run_cli()
    assert usage.returncode == 2
    assert "usage:" in usage.stderr
    assert "--check" in usage.stderr
    missing = run_cli(str(ROOT / "nope.slop"))
    assert missing.returncode == 2
    assert "could not read" in missing.stderr


def test_check_accepts_valid_syntax_without_running(tmp_path: Path):
    program = tmp_path / "ok.slop"
    program.write_text("hallucinate(“hello”)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_ignores_runtime_errors(tmp_path: Path):
    program = tmp_path / "runtime.slop"
    program.write_text("hallucinate(1 / 0)✨\n", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_reports_syntax_errors(tmp_path: Path):
    program = tmp_path / "broken.slop"
    program.write_text("slop x = 1", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == (
        "SlopLang syntax error at line 1: "
        "expected ✨ after variable declaration, but reached end of file\n"
    )


def test_check_flag_may_follow_the_path(tmp_path: Path):
    program = tmp_path / "ok.slop"
    program.write_text("slop x = 1✨\n", encoding="utf-8")
    completed = run_cli(str(program), "--check")
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


def test_check_requires_a_file():
    completed = run_cli("--check")
    assert completed.returncode == 2
    assert "usage:" in completed.stderr
