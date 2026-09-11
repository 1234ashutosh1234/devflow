import re
from dataclasses import dataclass


@dataclass
class ReviewFindingResult:
    category: str
    severity: str
    title: str
    description: str
    line_number: int | None
    suggestion: str | None
    confidence: float


class AIReviewAgent:
    """
    Deterministic local baseline review engine.

    This component is intentionally independent from FastAPI,
    SQLAlchemy, and any specific LLM provider.
    """

    SECRET_PATTERN = re.compile(
        r"\b(password|passwd|api[_-]?key|secret|token)\b"
        r"\s*=\s*[\"'][^\"']{6,}[\"']",
        re.IGNORECASE,
    )

    def analyze(
        self,
        content: str,
        filename: str | None = None,
    ) -> list[ReviewFindingResult]:
        findings: list[ReviewFindingResult] = []

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            self._check_hardcoded_secret(
                stripped,
                line_number,
                findings,
            )

            self._check_eval(
                stripped,
                line_number,
                findings,
            )

            self._check_exec(
                stripped,
                line_number,
                findings,
            )

            self._check_shell_true(
                stripped,
                line_number,
                findings,
            )

            self._check_bare_except(
                stripped,
                line_number,
                findings,
            )

            self._check_todo(
                stripped,
                line_number,
                findings,
            )

            self._check_range_len(
                stripped,
                line_number,
                findings,
            )

        return findings

    @staticmethod
    def _check_hardcoded_secret(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if AIReviewAgent.SECRET_PATTERN.search(line):
            findings.append(
                ReviewFindingResult(
                    category="security",
                    severity="high",
                    title="Possible hardcoded secret",
                    description=(
                        "A credential-like value appears to be "
                        "hardcoded directly in source code."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Move the secret to an environment variable "
                        "or a managed secret store."
                    ),
                    confidence=0.97,
                )
            )

    @staticmethod
    def _check_eval(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.search(r"\beval\s*\(", line):
            findings.append(
                ReviewFindingResult(
                    category="security",
                    severity="critical",
                    title="Use of eval() detected",
                    description=(
                        "eval() can execute dynamically supplied "
                        "Python expressions and may introduce code "
                        "execution vulnerabilities."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Replace eval() with explicit parsing "
                        "or another safe approach."
                    ),
                    confidence=0.99,
                )
            )

    @staticmethod
    def _check_exec(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.search(r"\bexec\s*\(", line):
            findings.append(
                ReviewFindingResult(
                    category="security",
                    severity="critical",
                    title="Use of exec() detected",
                    description=(
                        "exec() executes dynamically generated "
                        "Python code and can introduce serious "
                        "security risks."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Avoid exec(); use explicit functions "
                        "or validated dispatch logic."
                    ),
                    confidence=0.99,
                )
            )

    @staticmethod
    def _check_shell_true(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.search(r"\bshell\s*=\s*True\b", line):
            findings.append(
                ReviewFindingResult(
                    category="security",
                    severity="high",
                    title="shell=True detected",
                    description=(
                        "Using shell=True can allow command injection "
                        "when command input is influenced by untrusted data."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Prefer subprocess argument lists with "
                        "shell=False whenever possible."
                    ),
                    confidence=0.95,
                )
            )

    @staticmethod
    def _check_bare_except(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.match(r"^except\s*:", line):
            findings.append(
                ReviewFindingResult(
                    category="maintainability",
                    severity="medium",
                    title="Bare except detected",
                    description=(
                        "A bare except catches every exception and "
                        "can hide unexpected failures."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Catch the specific exception types "
                        "the application expects."
                    ),
                    confidence=0.96,
                )
            )

    @staticmethod
    def _check_todo(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.search(r"\b(TODO|FIXME)\b", line, re.IGNORECASE):
            findings.append(
                ReviewFindingResult(
                    category="maintainability",
                    severity="low",
                    title="TODO/FIXME marker found",
                    description=(
                        "This line contains an unresolved "
                        "TODO or FIXME marker."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Create a tracked task or issue for the "
                        "remaining work."
                    ),
                    confidence=0.90,
                )
            )

    @staticmethod
    def _check_range_len(
        line: str,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if re.search(
            r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(",
            line,
        ):
            findings.append(
                ReviewFindingResult(
                    category="performance",
                    severity="low",
                    title="range(len(...)) pattern detected",
                    description=(
                        "Index-based iteration can be less readable "
                        "than direct iteration or enumerate()."
                    ),
                    line_number=line_number,
                    suggestion=(
                        "Consider direct iteration or enumerate() "
                        "when the index is required."
                    ),
                    confidence=0.88,
                )
            )