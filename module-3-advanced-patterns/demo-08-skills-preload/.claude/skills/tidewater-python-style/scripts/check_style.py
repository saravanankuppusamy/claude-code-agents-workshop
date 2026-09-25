#!/usr/bin/env python3
"""AST-based checker for the Tidewater style rules (TW-N1/N2/F1/E1/E2/D1).

    python3 check_style.py file.py [more.py ...] [--max-lines 20]

A skill can ship scripts like this one so the agent gets deterministic facts
instead of estimating line counts by eye.
"""
import ast
import re
import sys

SNAKE = re.compile(r"^_?[a-z][a-z0-9_]*$")
UPPER = re.compile(r"^_?[A-Z][A-Z0-9_]*$")
IO_CALLS = {"open", "urlopen", "connect", "execute", "get", "post", "load", "dump"}


def body_lines(fn):
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    lines = set()
    for node in body:
        for sub in ast.walk(node):
            if hasattr(sub, "lineno"):
                lines.add(sub.lineno)
    return len(lines)


def call_name(call):
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def in_try(node, parents):
    p = parents.get(node)
    while p is not None:
        if isinstance(p, ast.Try):
            return any(h.type is not None for h in p.handlers)
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        p = parents.get(p)
    return False


def check(path, max_lines):
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and not UPPER.match(t.id) and not t.id.startswith("__"):
                    out.append(("TW-N2", node.lineno, t.id, "module-level constant should be UPPER_SNAKE_CASE"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not SNAKE.match(node.name):
                out.append(("TW-N1", node.lineno, node.name, "function name should be snake_case"))
            n = body_lines(node)
            if n > max_lines:
                out.append(("TW-F1", node.lineno, node.name, f"{n} lines > {max_lines}"))
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                out.append(("TW-D1", node.lineno, node.name, "missing docstring"))
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append(("TW-E1", node.lineno, "except:", "bare except"))
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name == "open" and not isinstance(parents.get(node), ast.withitem):
                out.append(("TW-E2", node.lineno, "open()", "open() not used in a with block"))
            if name in IO_CALLS and not in_try(node, parents):
                out.append(("TW-E1", node.lineno, f"{name}()", "I/O call not inside try/except with a specific type"))
    return sorted(out, key=lambda r: r[1])


def main(argv):
    max_lines = 20
    if "--max-lines" in argv:
        i = argv.index("--max-lines")
        max_lines = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    total = 0
    for path in argv:
        for rule, line, name, msg in check(path, max_lines):
            print(f"{rule:6} {path}:{line:<4} {name:<22} {msg}")
            total += 1
    print(f"-- {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
