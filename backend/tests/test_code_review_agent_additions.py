
from ai_reviewer.agents.code_review_agent import AIReviewAgent


def test_ignores_eval_and_exec_inside_strings_and_comments():
    agent = AIReviewAgent()
    content = "\n".join([
        'example = "eval(user_input) and exec(command)"',
        "# eval(user_input)",
        "# exec(command)",
    ])
    assert agent.analyze(content, "examples.py") == []


def test_detects_eval_and_exec_as_python_calls():
    agent = AIReviewAgent()
    content = "\n".join(["eval(user_input)", "exec(command)"])
    findings = agent.analyze(content, "unsafe.py")
    assert [finding.title for finding in findings] == [
        "Use of eval() detected",
        "Use of exec() detected",
    ]


def test_ignores_obvious_placeholder_secret_values():
    agent = AIReviewAgent()
    content = "\n".join([
        'webhook_secret = "test-secret"',
        'api_token = "YOUR_API_KEY"',
        'secret = "replace-me"',
    ])
    assert agent.analyze(content, "fixtures.py") == []


def test_detects_credential_like_value_and_preserves_filename():
    agent = AIReviewAgent()
    content = 'github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD"'
    findings = agent.analyze(content, "settings.py")
    assert len(findings) == 1
    assert findings[0].title == "Possible hardcoded secret"
    assert findings[0].filename == "settings.py"


def test_python_rules_are_not_applied_to_markdown():
    agent = AIReviewAgent()
    content = "\n".join([
        "Run eval(user_input) in this example.",
        "# TODO: explain the example",
    ])
    assert agent.analyze(content, "README.md") == []


def test_ignores_string_call_but_finds_call_in_incomplete_diff():
    agent = AIReviewAgent()
    content = "\n".join([
        'example = "eval(user_input)"',
        "eval(user_input)",
        "def unfinished(",
    ])
    findings = agent.analyze(content, "partial.py")
    assert len(findings) == 1
    assert findings[0].title == "Use of eval() detected"
    assert findings[0].line_number == 2
    assert findings[0].filename == "partial.py"


def test_finds_bare_except_and_todo_comment_once_in_incomplete_diff():
    agent = AIReviewAgent()
    content = "\n".join([
        "try:",
        "    run()",
        "except:",
        "    # TODO: replace broad exception",
        "    pass",
        "def unfinished(",
    ])
    findings = agent.analyze(content, "partial.py")
    titles = [finding.title for finding in findings]
    assert titles.count("Bare except detected") == 1
    assert titles.count("TODO/FIXME marker found") == 1


def test_detects_range_len_pattern():
    agent = AIReviewAgent()
    content = "\n".join([
        'users = ["A", "B"]',
        "for index in range(len(users)):",
        "    print(users[index])",
    ])
    findings = agent.analyze(content, "loop.py")
    assert len(findings) == 1
    assert findings[0].title == "range(len(...)) pattern detected"
    assert findings[0].line_number == 2


def test_detects_shell_true_as_python_keyword_argument():
    agent = AIReviewAgent()
    findings = agent.analyze(
        "subprocess.run(command, shell=True)",
        "runner.py",
    )
    assert len(findings) == 1
    assert findings[0].title == "shell=True detected"


def test_ignores_non_builtin_method_named_eval():
    agent = AIReviewAgent()
    assert agent.analyze("parser.eval(expression)", "parser.py") == []
