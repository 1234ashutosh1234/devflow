
import ast
import io
import re
import tokenize
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
    filename: str | None = None


class AIReviewAgent:
    # Python rules use AST for complete files and tokenization for partial diffs.
    # Comments and string literals are never treated as executable Python code.

    SECRET_NAME_PATTERN = re.compile(
        r"(?:^|[_-])(password|passwd|api[_-]?key|secret|token)(?:$|[_-])",
        re.IGNORECASE,
    )
    PLACEHOLDER_SECRET_VALUES = {
        "test-secret",
        "test-token",
        "your-secret",
        "your-token",
        "your-api-key",
        "replace-me",
        "change-me",
        "changeme",
        "insert-token-here",
        "placeholder",
        "dummy",
        "example",
        "example-secret",
        "example-token",
        "dummy-secret",
        "fake-secret",
        "fake-token",
        "not-a-real-secret",
    }
    TODO_PATTERN = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)

    def analyze(
        self,
        content: str,
        filename: str | None = None,
    ) -> list[ReviewFindingResult]:
        if filename and not filename.lower().endswith((".py", ".pyi")):
            return []

        findings: list[ReviewFindingResult] = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            tree = None

        if tree is not None:
            self._analyze_ast(tree, findings)
            tokens = self._tokenize(content)
        else:
            tokens = self._tokenize(content)
            self._analyze_tokens(tokens, findings)

        self._check_todo_comments(tokens, findings)

        for finding in findings:
            finding.filename = filename

        findings.sort(
            key=lambda finding: (
                finding.line_number or 0,
                finding.title,
            )
        )
        return findings

    @classmethod
    def _is_placeholder_secret(cls, value: str) -> bool:
        normalized = re.sub(
            r"[^a-z0-9]+",
            "-",
            value.strip().casefold(),
        ).strip("-")

        if normalized in cls.PLACEHOLDER_SECRET_VALUES:
            return True

        return bool(
            re.fullmatch(
                r"(?:your|replace|change|insert|sample|example|dummy|fake|test)"
                r"(?:-[a-z0-9]+){0,5}",
                normalized,
            )
        )

    @classmethod
    def _target_names(cls, target: ast.AST) -> list[str]:
        names: list[str] = []
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Attribute):
            names.append(target.attr)
        elif isinstance(target, ast.Subscript):
            slice_node = target.slice
            if isinstance(slice_node, ast.Constant) and isinstance(
                slice_node.value, str
            ):
                names.append(slice_node.value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                names.extend(cls._target_names(element))
        return names

    @classmethod
    def _record_secret(
        cls,
        target_names: list[str],
        value_node: ast.AST,
        line_number: int,
        findings: list[ReviewFindingResult],
    ) -> None:
        if not isinstance(value_node, ast.Constant):
            return

        value = value_node.value
        if not isinstance(value, str) or len(value.strip()) < 10:
            return
        if cls._is_placeholder_secret(value):
            return
        if not any(
            cls.SECRET_NAME_PATTERN.search(name)
            for name in target_names
        ):
            return

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

    @classmethod
    def _analyze_ast(
        cls,
        tree: ast.AST,
        findings: list[ReviewFindingResult],
    ) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = cls._unsafe_builtin_name(node.func)

                if call_name == "eval":
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
                            line_number=node.lineno,
                            suggestion=(
                                "Replace eval() with explicit parsing "
                                "or another safe approach."
                            ),
                            confidence=0.99,
                        )
                    )
                elif call_name == "exec":
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
                            line_number=node.lineno,
                            suggestion=(
                                "Avoid exec(); use explicit functions "
                                "or validated dispatch logic."
                            ),
                            confidence=0.99,
                        )
                    )

                if any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                ):
                    findings.append(
                        ReviewFindingResult(
                            category="security",
                            severity="high",
                            title="shell=True detected",
                            description=(
                                "Using shell=True can allow command injection "
                                "when command input is influenced by untrusted data."
                            ),
                            line_number=node.lineno,
                            suggestion=(
                                "Prefer subprocess argument lists with "
                                "shell=False whenever possible."
                            ),
                            confidence=0.95,
                        )
                    )

            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append(
                    ReviewFindingResult(
                        category="maintainability",
                        severity="medium",
                        title="Bare except detected",
                        description=(
                            "A bare except catches every exception and "
                            "can hide unexpected failures."
                        ),
                        line_number=node.lineno,
                        suggestion=(
                            "Catch the specific exception types "
                            "the application expects."
                        ),
                        confidence=0.96,
                    )
                )

            elif isinstance(node, ast.For) and cls._is_range_len_call(node.iter):
                findings.append(
                    ReviewFindingResult(
                        category="performance",
                        severity="low",
                        title="range(len(...)) pattern detected",
                        description=(
                            "Index-based iteration can be less readable "
                            "than direct iteration or enumerate()."
                        ),
                        line_number=node.lineno,
                        suggestion=(
                            "Consider direct iteration or enumerate() "
                            "when the index is required."
                        ),
                        confidence=0.88,
                    )
                )

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    cls._record_secret(
                        cls._target_names(target),
                        node.value,
                        node.lineno,
                        findings,
                    )
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                cls._record_secret(
                    cls._target_names(node.target),
                    node.value,
                    node.lineno,
                    findings,
                )
            elif isinstance(node, ast.NamedExpr):
                cls._record_secret(
                    cls._target_names(node.target),
                    node.value,
                    node.lineno,
                    findings,
                )

    @staticmethod
    def _unsafe_builtin_name(function: ast.AST) -> str | None:
        if isinstance(function, ast.Name) and function.id in {"eval", "exec"}:
            return function.id
        if (
            isinstance(function, ast.Attribute)
            and isinstance(function.value, ast.Name)
            and function.value.id == "builtins"
            and function.attr in {"eval", "exec"}
        ):
            return function.attr
        return None

    @staticmethod
    def _is_range_len_call(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "range"
            and bool(node.args)
            and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Name)
            and node.args[0].func.id == "len"
        )

    @staticmethod
    def _tokenize(content: str) -> list[tokenize.TokenInfo]:
        result: list[tokenize.TokenInfo] = []
        generator = tokenize.generate_tokens(io.StringIO(content).readline)
        try:
            while True:
                result.append(next(generator))
        except StopIteration:
            pass
        except (tokenize.TokenError, IndentationError):
            # GitHub diffs can contain incomplete Python snippets.
            pass
        return result

    @staticmethod
    def _significant_tokens(
        tokens: list[tokenize.TokenInfo],
    ) -> list[tokenize.TokenInfo]:
        ignored = {
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.ENDMARKER,
            tokenize.COMMENT,
        }
        return [token for token in tokens if token.type not in ignored]

    @staticmethod
    def _assigned_string_token(
        tokens: list[tokenize.TokenInfo],
        index: int,
    ) -> tokenize.TokenInfo | None:
        if index + 2 >= len(tokens) or tokens[index + 1].string != "=":
            return None
        candidate = tokens[index + 2]
        return candidate if candidate.type == tokenize.STRING else None

    @staticmethod
    def _string_value(token_value: str) -> str | None:
        try:
            parsed = ast.literal_eval(token_value)
        except (SyntaxError, ValueError):
            return None
        return parsed if isinstance(parsed, str) else None

    @staticmethod
    def _tokens_contain_range_len(
        tokens: list[tokenize.TokenInfo],
        index: int,
    ) -> bool:
        sample = tokens[index:index + 7]
        return (
            len(sample) == 7
            and sample[0].string == "for"
            and sample[1].type == tokenize.NAME
            and sample[2].string == "in"
            and sample[3].string == "range"
            and sample[4].string == "("
            and sample[5].string == "len"
            and sample[6].string == "("
        )

    @classmethod
    def _analyze_tokens(
        cls,
        raw_tokens: list[tokenize.TokenInfo],
        findings: list[ReviewFindingResult],
    ) -> None:
        tokens = cls._significant_tokens(raw_tokens)

        for index, token in enumerate(tokens):
            if token.type == tokenize.NAME and token.string in {"eval", "exec"}:
                previous = tokens[index - 1].string if index > 0 else ""
                next_token = tokens[index + 1] if index + 1 < len(tokens) else None

                if previous == "def" or next_token is None or next_token.string != "(":
                    continue
                if previous == ".":
                    qualifier = tokens[index - 2].string if index > 1 else ""
                    if qualifier != "builtins":
                        continue

                is_eval = token.string == "eval"
                findings.append(
                    ReviewFindingResult(
                        category="security",
                        severity="critical",
                        title=(
                            "Use of eval() detected"
                            if is_eval
                            else "Use of exec() detected"
                        ),
                        description=(
                            "eval() can execute dynamically supplied Python "
                            "expressions and may introduce code execution vulnerabilities."
                            if is_eval
                            else "exec() executes dynamically generated Python code "
                            "and can introduce serious security risks."
                        ),
                        line_number=token.start[0],
                        suggestion=(
                            "Replace eval() with explicit parsing or another safe approach."
                            if is_eval
                            else "Avoid exec(); use explicit functions or validated dispatch logic."
                        ),
                        confidence=0.99,
                    )
                )

            if (
                token.type == tokenize.NAME
                and token.string == "shell"
                and index + 2 < len(tokens)
                and tokens[index + 1].string == "="
                and tokens[index + 2].string == "True"
            ):
                findings.append(
                    ReviewFindingResult(
                        category="security",
                        severity="high",
                        title="shell=True detected",
                        description=(
                            "Using shell=True can allow command injection "
                            "when command input is influenced by untrusted data."
                        ),
                        line_number=token.start[0],
                        suggestion=(
                            "Prefer subprocess argument lists with "
                            "shell=False whenever possible."
                        ),
                        confidence=0.95,
                    )
                )

            if (
                token.type == tokenize.NAME
                and token.string == "except"
                and index + 1 < len(tokens)
                and tokens[index + 1].string == ":"
            ):
                findings.append(
                    ReviewFindingResult(
                        category="maintainability",
                        severity="medium",
                        title="Bare except detected",
                        description=(
                            "A bare except catches every exception and "
                            "can hide unexpected failures."
                        ),
                        line_number=token.start[0],
                        suggestion=(
                            "Catch the specific exception types "
                            "the application expects."
                        ),
                        confidence=0.96,
                    )
                )

            if (
                token.type == tokenize.NAME
                and cls.SECRET_NAME_PATTERN.search(token.string)
            ):
                value_token = cls._assigned_string_token(tokens, index)
                if value_token is not None:
                    value = cls._string_value(value_token.string)
                    if value is not None and not cls._is_placeholder_secret(value):
                        cls._record_secret(
                            [token.string],
                            ast.Constant(value=value),
                            token.start[0],
                            findings,
                        )

            if token.string == "for" and cls._tokens_contain_range_len(tokens, index):
                findings.append(
                    ReviewFindingResult(
                        category="performance",
                        severity="low",
                        title="range(len(...)) pattern detected",
                        description=(
                            "Index-based iteration can be less readable "
                            "than direct iteration or enumerate()."
                        ),
                        line_number=token.start[0],
                        suggestion=(
                            "Consider direct iteration or enumerate() "
                            "when the index is required."
                        ),
                        confidence=0.88,
                    )
                )

    @classmethod
    def _check_todo_comments(
        cls,
        tokens: list[tokenize.TokenInfo],
        findings: list[ReviewFindingResult],
    ) -> None:
        for token in tokens:
            if token.type == tokenize.COMMENT and cls.TODO_PATTERN.search(token.string):
                findings.append(
                    ReviewFindingResult(
                        category="maintainability",
                        severity="low",
                        title="TODO/FIXME marker found",
                        description=(
                            "This line contains an unresolved "
                            "TODO or FIXME marker."
                        ),
                        line_number=token.start[0],
                        suggestion=(
                            "Create a tracked task or issue for the "
                            "remaining work."
                        ),
                        confidence=0.90,
                    )
                )
