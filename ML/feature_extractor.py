"""
Feature extractor for logic classification.
Counts conditions, loops, functions, operators, length, complexity.
Language-agnostic (works on Python / C / C++ / Java / JS).
"""
import re

FEATURE_ORDER = [
    "num_conditions", "num_loops", "num_functions",
    "num_operators", "code_length", "complexity_score",
]

COND_RE = re.compile(r"\b(if|elif|else if|switch|case)\b")
LOOP_RE = re.compile(r"\b(for|while|do)\b")
FUNC_RE = re.compile(
    r"(\bdef\s+\w+\s*\(|\bfunction\s+\w+\s*\(|\b(?:public|private|static)?\s*[\w<>\[\]]+\s+\w+\s*\([^;]*\)\s*\{)"
)
OP_RE = re.compile(r"==|!=|<=|>=|&&|\|\||[+\-*/%=<>!]")
NEST_RE = re.compile(r"^[ \t]+(if|for|while)\b", re.MULTILINE)


def extract_features(code: str) -> dict:
    conditions = len(COND_RE.findall(code))
    loops = len(LOOP_RE.findall(code))
    functions = len(FUNC_RE.findall(code))
    operators = len(OP_RE.findall(code))
    length = len(code)
    nested = len(NEST_RE.findall(code))
    # Cyclomatic-ish complexity: 1 + decision points + nesting weight
    complexity = 1 + conditions + loops + nested
    return {
        "num_conditions": conditions,
        "num_loops": loops,
        "num_functions": functions,
        "num_operators": operators,
        "code_length": length,
        "complexity_score": complexity,
    }
