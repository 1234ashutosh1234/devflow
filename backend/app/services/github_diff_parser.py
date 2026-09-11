from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedDiffFile:
    filename: str
    content: str
    reviewable_lines: frozenset[int]


_HUNK_RE = re.compile(
    r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,(\d+))? @@"
)


def parse_unified_diff(diff: str) -> list[ParsedDiffFile]:
    files: list[ParsedDiffFile] = []

    current_filename: str | None = None
    current_lines: dict[int, str] = {}
    current_reviewable_lines: set[int] = set()
    current_new_line = 0

    def flush_current_file() -> None:
        nonlocal current_filename
        nonlocal current_lines
        nonlocal current_reviewable_lines
        nonlocal current_new_line

        if current_filename is None:
            return

        if current_lines:
            max_line = max(current_lines)

            content_lines = [
                current_lines.get(line_number, "")
                for line_number in range(1, max_line + 1)
            ]

            content = "\n".join(content_lines)
        else:
            content = ""

        files.append(
            ParsedDiffFile(
                filename=current_filename,
                content=content,
                reviewable_lines=frozenset(
                    current_reviewable_lines
                ),
            )
        )

        current_filename = None
        current_lines = {}
        current_reviewable_lines = set()
        current_new_line = 0

    for raw_line in diff.splitlines():
        if raw_line.startswith("diff --git "):
            flush_current_file()
            continue

        if raw_line.startswith("+++ b/"):
            current_filename = raw_line[6:]
            current_lines = {}
            current_reviewable_lines = set()
            current_new_line = 0
            continue

        if raw_line.startswith("+++ /dev/null"):
            current_filename = None
            continue

        if raw_line.startswith("@@ "):
            match = _HUNK_RE.match(raw_line)

            if match is None:
                raise ValueError(
                    f"Unable to parse diff hunk header: {raw_line}"
                )

            current_new_line = int(match.group(2))
            continue

        if current_filename is None:
            continue

        if raw_line.startswith("+"):
            current_lines[current_new_line] = raw_line[1:]
            current_reviewable_lines.add(current_new_line)
            current_new_line += 1
            continue

        if raw_line.startswith("-"):
            continue

        if raw_line.startswith("\\ No newline"):
            continue

        current_lines[current_new_line] = raw_line
        current_reviewable_lines.add(current_new_line)
        current_new_line += 1

    flush_current_file()

    return files