"""
Convert source code (Python / C / C++ / Java / JavaScript) to a Mermaid flowchart.
Heuristic line-based parser — robust enough for educational snippets.
"""
import re

LANG_KEYWORDS = {
    "if": ["if "],
    "elif": ["elif ", "else if"],
    "else": ["else:", "else {", "else "],
    "for": ["for "],
    "while": ["while "],
    "func": ["def ", "function ", "void ", "int ", "public ", "private "],
    "return": ["return"],
}


def _norm(line: str) -> str:
    return line.strip().rstrip("{").rstrip(":").strip()


def code_to_mermaid(code: str, language: str = "python") -> str:
    lines = [l for l in code.splitlines() if l.strip()]
    nodes = ["flowchart TD", "Start([Start])"]
    prev = "Start"
    counter = 0
    stack = []  # track open conditionals/loops -> (kind, node_id, merge_id)

    def nid(prefix):
        nonlocal counter
        counter += 1
        return f"{prefix}{counter}"

    for raw in lines:
        line = _norm(raw)
        indent = len(raw) - len(raw.lstrip())

        # close blocks that have ended (Python uses indent; braces close on `}`)
        while stack and indent <= stack[-1]["indent"] and not raw.strip().startswith(("elif", "else")):
            top = stack.pop()
            nodes.append(f"{prev} --> {top['merge']}")
            prev = top["merge"]

        if raw.strip().startswith("}"):
            if stack:
                top = stack.pop()
                nodes.append(f"{prev} --> {top['merge']}")
                prev = top["merge"]
            continue

        low = line.lower()
        if low.startswith(("if ", "if(")):
            cond = nid("Cond")
            merge = nid("Merge")
            label = line.replace('"', "'")
            nodes.append(f"{cond}{{\"{label}\"}}")
            nodes.append(f"{prev} --> {cond}")
            nodes.append(f"{cond} -- Yes --> ")  # placeholder, fixed below
            # use simpler edge model:
            nodes.pop()
            stack.append({"kind": "if", "node": cond, "merge": merge, "indent": indent})
            prev = cond
            # next statement becomes Yes branch — handled by edge from cond
            nodes.append(f"%% if-block opened at {cond}")
        elif low.startswith(("elif", "else if")):
            # close current yes branch into merge, open new condition branch
            if stack:
                top = stack[-1]
                nodes.append(f"{prev} --> {top['merge']}")
                cond = nid("Cond")
                label = line.replace('"', "'")
                nodes.append(f"{cond}{{\"{label}\"}}")
                nodes.append(f"{top['node']} -- No --> {cond}")
                top["node"] = cond
                prev = cond
        elif low.startswith("else"):
            if stack:
                top = stack[-1]
                nodes.append(f"{prev} --> {top['merge']}")
                els = nid("Else")
                nodes.append(f"{els}[\"else branch\"]")
                nodes.append(f"{top['node']} -- No --> {els}")
                prev = els
        elif low.startswith(("for ", "for(", "while ", "while(")):
            loop = nid("Loop")
            merge = nid("Merge")
            label = line.replace('"', "'")
            nodes.append(f"{loop}{{\"{label}\"}}")
            nodes.append(f"{prev} --> {loop}")
            stack.append({"kind": "loop", "node": loop, "merge": merge, "indent": indent})
            prev = loop
        elif any(low.startswith(k) for k in ("def ", "function ", "public ", "private ")):
            fn = nid("Fn")
            label = line.replace('"', "'")
            nodes.append(f"{fn}[/\"{label}\"/]")
            nodes.append(f"{prev} --> {fn}")
            prev = fn
        elif low.startswith("return"):
            ret = nid("Ret")
            label = line.replace('"', "'")
            nodes.append(f"{ret}([\"{label}\"])")
            nodes.append(f"{prev} --> {ret}")
            prev = ret
        else:
            stmt = nid("Stmt")
            label = line.replace('"', "'")[:80]
            nodes.append(f"{stmt}[\"{label}\"]")
            # if we just opened an if/loop, this is the yes/body branch
            if stack and stack[-1]["node"] == prev and stack[-1]["kind"] in ("if", "loop"):
                nodes.append(f"{prev} -- Yes --> {stmt}")
            else:
                nodes.append(f"{prev} --> {stmt}")
            prev = stmt

    # close any open blocks
    while stack:
        top = stack.pop()
        nodes.append(f"{prev} --> {top['merge']}")
        prev = top["merge"]

    end = "End([End])"
    nodes.append(end)
    nodes.append(f"{prev} --> End")
    # dedupe comment placeholders
    cleaned = [n for n in nodes if not n.startswith("%%")]
    return "\n".join(cleaned)
