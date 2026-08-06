from typing import Final

import nox

nox.options.sessions = ["ruff", "mypy", "pip_audit", "lint_imports"]
nox.options.reuse_existing_virtualenvs = True

PACKAGE: Final[str] = "src/tasto"
PYTHON: Final[str] = "3.13"


@nox.session(python=PYTHON)
def ruff(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", ".")


@nox.session(python=PYTHON)
def mypy(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("mypy")
    session.run("mypy", PACKAGE)


@nox.session(python=PYTHON)
def pip_audit(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("pip-audit")
    session.run("pip-audit")


@nox.session(python=PYTHON, name="lint_imports")
def lint_imports(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("import-linter")
    session.run("lint-imports")
