import sys
from pathlib import Path

if sys.version_info < (3, 13):  # noqa: UP036 - friendly error on unsupported Python
    print(
        "sloperator requires Python 3.13 or newer; run it with 'uv run sloperator.py'",
        file=sys.stderr,
    )
    raise SystemExit(2)

from sloperator.runner import check_source, run_program  # noqa: E402

USAGE = "usage: uv run sloperator.py [--check] <file.slop>"


def main(argv: list[str]) -> int:
    args = argv[1:]
    check = "--check" in args
    if check:
        args = [arg for arg in args if arg != "--check"]
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2

    path = Path(args[0])
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"could not read '{path}': {error.strerror}", file=sys.stderr)
        return 2

    error = check_source(source) if check else run_program(source, sys.stdout)
    if error is not None:
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
