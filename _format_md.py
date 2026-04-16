#!/usr/bin/env python3
"""Format Obsidian Markdown files: fix spacing around headings, code blocks,
blockquotes, remove trailing whitespace, collapse consecutive blank lines,
ensure single trailing newline. Preserves code block internals."""

import re
import sys
import os


def format_md(text: str) -> str:
    lines = text.split('\n')
    # Remove trailing whitespace from each line (but preserve code block internals)
    in_code = False
    cleaned = []
    for line in lines:
        if re.match(r'^(`{3,}|~{3,})', line.strip()):
            in_code = not in_code
            cleaned.append(line.rstrip())
        elif in_code:
            cleaned.append(line)  # preserve code block internals exactly
        else:
            cleaned.append(line.rstrip())
    lines = cleaned

    # Collapse consecutive blank lines into single blank lines
    result = []
    prev_blank = False
    for line in lines:
        is_blank = line == ''
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    lines = result

    # Ensure blank line before and after headings (outside code blocks)
    result = []
    in_code = False
    for i, line in enumerate(lines):
        if re.match(r'^(`{3,}|~{3,})', line.strip()):
            in_code = not in_code
            result.append(line)
            continue
        if in_code:
            result.append(line)
            continue

        is_heading = re.match(r'^#{1,6}\s', line)
        if is_heading and i > 0:
            # Ensure blank line before heading
            if result and result[-1] != '':
                result.append('')
        result.append(line)
        if is_heading and i < len(lines) - 1:
            # Ensure blank line after heading (will be added; next iteration handles it)
            pass  # handled below

    lines = result

    # Ensure blank line after headings
    result = []
    in_code = False
    for i, line in enumerate(lines):
        if re.match(r'^(`{3,}|~{3,})', line.strip()):
            in_code = not in_code
        result.append(line)
        if not in_code and re.match(r'^#{1,6}\s', line):
            if i + 1 < len(lines) and lines[i + 1] != '':
                result.append('')
    lines = result

    # Ensure blank line before and after code block delimiters (outside code blocks)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        is_fence = bool(re.match(r'^(`{3,}|~{3,})', line.strip()))
        if is_fence:
            # blank line before fence if needed
            if result and result[-1] != '':
                result.append('')
            result.append(line)
            # blank line after fence if needed (only for closing fences or opening fences)
            if i + 1 < len(lines) and lines[i + 1] != '':
                # But don't add blank after opening fence (content follows)
                # and don't add blank after closing fence if next is also blank
                pass
        else:
            result.append(line)
        i += 1
    lines = result

    # Ensure blank line after closing code fence
    result = []
    in_code = False
    for i, line in enumerate(lines):
        is_fence = bool(re.match(r'^(`{3,}|~{3+})', line.strip()))
        if is_fence:
            if in_code:
                # closing fence
                result.append(line)
                in_code = False
                if i + 1 < len(lines) and lines[i + 1] != '':
                    result.append('')
            else:
                # opening fence
                in_code = True
                result.append(line)
        else:
            result.append(line)
    lines = result

    # Ensure blank line before and after blockquotes (outside code blocks)
    result = []
    in_code = False
    for i, line in enumerate(lines):
        if re.match(r'^(`{3,}|~{3,})', line.strip()):
            in_code = not in_code
        if not in_code:
            is_bq = line.startswith('>')
            prev_is_bq = result and result[-1].startswith('>') if result else False
            # blank line before blockquote start
            if is_bq and result and not prev_is_bq and result[-1] != '':
                result.append('')
            # blank line after blockquote end
            if not is_bq and result and prev_is_bq and line != '' and result[-1] != '':
                result.append('')
        result.append(line)
    lines = result

    # Final pass: collapse any consecutive blank lines that may have been introduced
    result = []
    prev_blank = False
    for line in lines:
        is_blank = line == ''
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    lines = result

    # Remove leading blank line if file starts with one
    while lines and lines[0] == '':
        lines.pop(0)

    # Remove trailing blank lines and ensure single trailing newline
    while lines and lines[-1] == '':
        lines.pop()

    return '\n'.join(lines) + '\n'


def process_file(filepath: str) -> bool:
    """Process a single file. Returns True if modified."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='gb18030') as f:
                original = f.read()
        except Exception:
            print(f"  SKIP (encoding error): {filepath}")
            return False

    formatted = format_md(original)
    if formatted != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
        return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python _format_md.py <directory>")
        sys.exit(1)

    root = sys.argv[1]
    modified = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip .git
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in sorted(filenames):
            if fn.endswith('.md'):
                filepath = os.path.join(dirpath, fn)
                total += 1
                if process_file(filepath):
                    modified += 1
                    print(f"  MODIFIED: {filepath}")

    print(f"\nDone. {modified}/{total} files modified.")


if __name__ == '__main__':
    main()
