from ai_reviewer.agents.code_review_agent import AIReviewAgent


def get_finding(findings, title):
    for finding in findings:
        if finding.title == title:
            return finding
    return None


def test_clean_code_has_no_findings():
    agent = AIReviewAgent()

    content = """
def add_numbers(a, b):
    return a + b
"""

    findings = agent.analyze(content, "clean.py")

    assert findings == []


def test_detects_hardcoded_secret():
    agent = AIReviewAgent()

    content = 'api_key = "SECRET-12345"'

    findings = agent.analyze(content, "secrets.py")

    finding = get_finding(findings, "Possible hardcoded secret")

    assert finding is not None
    assert finding.category == "security"
    assert finding.severity == "high"
    assert finding.line_number == 1
    assert finding.confidence == 0.97


def test_detects_eval():
    agent = AIReviewAgent()

    content = """
user_input = input()
eval(user_input)
"""

    findings = agent.analyze(content, "eval_test.py")

    finding = get_finding(findings, "Use of eval() detected")

    assert finding is not None
    assert finding.category == "security"
    assert finding.severity == "critical"
    assert finding.line_number == 3
    assert finding.confidence == 0.99


def test_detects_exec():
    agent = AIReviewAgent()

    content = """
command = get_command()
exec(command)
"""

    findings = agent.analyze(content, "exec_test.py")

    finding = get_finding(findings, "Use of exec() detected")

    assert finding is not None
    assert finding.category == "security"
    assert finding.severity == "critical"
    assert finding.line_number == 3
    assert finding.confidence == 0.99


def test_detects_bare_except():
    agent = AIReviewAgent()

    content = """
try:
    do_work()
except:
    pass
"""

    findings = agent.analyze(content, "except_test.py")

    finding = get_finding(findings, "Bare except detected")

    assert finding is not None
    assert finding.category == "maintainability"
    assert finding.severity == "medium"
    assert finding.line_number == 4
    assert finding.confidence == 0.96


def test_detects_todo_marker():
    agent = AIReviewAgent()

    content = """
def process():
    # TODO: improve this
    return True
"""

    findings = agent.analyze(content, "todo_test.py")

    finding = get_finding(findings, "TODO/FIXME marker found")

    assert finding is not None
    assert finding.category == "maintainability"
    assert finding.severity == "low"
    assert finding.line_number == 3
    assert finding.confidence == 0.90


def test_detects_range_len_pattern():
    agent = AIReviewAgent()

    content = """
users = ["A", "B"]

for i in range(len(users)):
    print(users[i])
"""

    findings = agent.analyze(content, "range_len_test.py")

    finding = get_finding(findings, "range(len(...)) pattern detected")

    assert finding is not None
    assert finding.category == "performance"
    assert finding.severity == "low"
    assert finding.line_number == 4
    assert finding.confidence == 0.88


def test_detects_multiple_findings():
    agent = AIReviewAgent()

    content = """
api_key = "SECRET-12345"

eval(user_input)

for i in range(len(users)):
    print(users[i])

# TODO: improve this
"""

    findings = agent.analyze(content, "multiple.py")

    titles = {finding.title for finding in findings}

    assert "Possible hardcoded secret" in titles
    assert "Use of eval() detected" in titles
    assert "range(len(...)) pattern detected" in titles
    assert "TODO/FIXME marker found" in titles

    assert len(findings) == 4


def test_filename_does_not_break_analysis():
    agent = AIReviewAgent()

    content = 'password = "MY-PASSWORD-123"'

    findings = agent.analyze(
        content,
        "github-review-demo/example.py",
    )

    assert len(findings) == 1
    assert findings[0].title == "Possible hardcoded secret"


def test_line_numbers_are_correct():
    agent = AIReviewAgent()

    content = """
def example():
    value = 123

    eval(value)
"""

    findings = agent.analyze(content, "lines.py")

    finding = get_finding(findings, "Use of eval() detected")

    assert finding is not None
    assert finding.line_number == 5