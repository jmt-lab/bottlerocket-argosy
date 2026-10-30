#!/usr/bin/env python3
"""State machine driver for the implement-commit skill.

The driver is harness-agnostic: it never launches an agent itself. It runs
gates, formatters and `git commit` directly, and whenever an LLM is needed it
prints a `spawn` action (JSON) for the orchestrating agent to execute by
dispatching a subagent in whatever harness it runs in. The orchestrator then
reports the subagent's JSON result back.

Loop:  init -> (next -> [dispatch subagent] -> report)* -> done
Exit code 1 from `next`/`resume` means the driver needs LLM intervention;
the reason is printed as JSON on stderr. Fix the problem, then `resume`.

Requires Python 3.11+ (tomllib) or the `toml` package.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

MAX_GATE_RETRIES = 2
MAX_STYLE_CYCLES = 3
CMD_TIMEOUT_SECS = 1800

AGENTS_DIR = Path(__file__).resolve().parent / "agents"


class State(str, Enum):
    EXPLORE_GATES = "explore_gates"
    EXPLORE_FORMATTERS = "explore_formatters"
    DESIGNER_PHASE = "designer_phase"
    DESIGNER_GATE = "designer_gate"
    DESIGNER_STYLE = "designer_style"
    TESTER_PHASE = "tester_phase"
    TESTER_GATE = "tester_gate"
    TESTER_STYLE = "tester_style"
    IMPLEMENTOR_PHASE = "implementor_phase"
    IMPLEMENTOR_GATE = "implementor_gate"
    IMPLEMENTOR_STYLE = "implementor_style"
    SCOPE_REVIEW = "scope_review"
    FORMAT = "format"
    COMMIT = "commit"
    DONE = "done"
    NEEDS_LLM = "needs_llm"


STYLE_STATES = {
    State.DESIGNER_STYLE: ("designer", State.DESIGNER_PHASE, State.TESTER_PHASE),
    State.TESTER_STYLE: ("tester", State.TESTER_PHASE, State.IMPLEMENTOR_PHASE),
    State.IMPLEMENTOR_STYLE: ("implementor", State.IMPLEMENTOR_PHASE, State.SCOPE_REVIEW),
}


@dataclass
class CommitState:
    plan_path: str
    commit_id: int
    workspace: str
    feature_dir: str = ""
    state: str = State.EXPLORE_GATES.value
    # Discovered (or user-supplied) commands
    designer_gate: str = ""
    test_gate: str = ""
    fmt_cmd: str = ""
    lint_cmd: str = ""
    # Commit info (from plan)
    commit_title: str = ""
    commit_message: str = ""
    commit_files: list[str] = field(default_factory=list)
    commit_tests: list[str] = field(default_factory=list)
    commit_acceptance: list[str] = field(default_factory=list)
    commit_anti_patterns: list[str] = field(default_factory=list)
    # Tracking
    awaiting: str = ""  # kind of spawn whose result is expected: phase|style_review|style_fix|arbiter|scope_review|explore_gates|explore_formatters
    files_touched: list[str] = field(default_factory=list)
    gate_retries: int = 0
    style_cycles: int = 0
    last_gate_error: str = ""
    last_style_violations: list[str] = field(default_factory=list)
    style_debt: list[str] = field(default_factory=list)
    escalation_context: str = ""
    resume_state: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data: str) -> "CommitState":
        return cls(**json.loads(data))


# ─── prompts ────────────────────────────────────────────────────────────────

def commit_block(st: CommitState) -> str:
    return json.dumps(
        {
            "id": st.commit_id,
            "title": st.commit_title,
            "files": st.commit_files,
            "tests": st.commit_tests,
            "acceptance": st.commit_acceptance,
            "anti_patterns": st.commit_anti_patterns,
        },
        indent=2,
    )


def prompt_explore_gates(st):
    return f"""Determine build and test gate commands for this project.

Workspace: {st.workspace}
Files to be modified: {st.commit_files}

Gates VALIDATE code (compile, run tests); they never modify files.
Scope commands to the affected crates/packages when possible.
Respond with JSON only: {{"designer_gate": "<e.g. cargo check -p foo>", "test_gate": "<e.g. cargo test -p foo>"}}"""


def prompt_explore_formatters(st):
    return f"""Determine format and lint-fix commands for this project.

Workspace: {st.workspace}
Files to be modified: {st.commit_files}

Formatters MODIFY code to fix style. Respond with JSON only:
{{"fmt_cmd": "<e.g. cargo fmt>", "lint_cmd": "<e.g. cargo clippy --fix --allow-dirty --allow-staged>"}}"""


def prompt_phase(phase, st, retry=""):
    gate = st.designer_gate if phase == "designer" else st.test_gate
    text = f"""Execute the {phase} phase for commit {st.commit_id}: {st.commit_title}

Follow the instructions in {AGENTS_DIR / (phase + '.md')}.
Workspace (run commands here; plan paths are relative to it): {st.workspace}
Feature dir (design.md, test-plan.md): {st.feature_dir}
Gate command: {gate}

Commit:
{commit_block(st)}"""
    if retry:
        text += f"\n\nPREVIOUS ATTEMPT FAILED THE GATE:\n{retry[-4000:]}"
    return text


def prompt_style_review(phase, st):
    return f"""Review the {phase} phase of commit {st.commit_id} for style compliance (pass/fail gate, no suggestions).

Workspace: {st.workspace}
Files to review: {sorted(set(st.files_touched))}
Use the project's style rules and this argosy's styleguide rules for the language.
Respond with JSON only: {{"status": "accept" | "violations", "violations": ["<file:line - rule - problem>", ...]}}"""


def prompt_style_fix(phase, st):
    return f"""Fix style violations from the {phase} phase of commit {st.commit_id}, keeping behaviour and gates green.

Follow the instructions in {AGENTS_DIR / (phase + '.md')} (including the review-feedback section).
Workspace: {st.workspace}
Files: {sorted(set(st.files_touched))}
Violations:
{json.dumps(st.last_style_violations, indent=2)}

For each violation either fix it (RESOLVED) or explain a concrete technical reason not to (DISPUTED).
Respond with JSON only: {{"status": "ok" | "problems", "files_created": [], "files_modified": [], "notes": "<RESOLVED/DISPUTED per violation>"}}"""


def prompt_scope_review(st):
    return f"""Review scope compliance for commit {st.commit_id}: {st.commit_title} (pass/fail gate).

Workspace: {st.workspace}
Inspect the uncommitted diff (`git status`, `git diff`, untracked files).
Allowed files: {st.commit_files}
Files reported as touched: {sorted(set(st.files_touched))}
Commit:
{commit_block(st)}

Reject changes outside the commit's scope or files, unrelated refactors, and missing pieces of the commit.
Respond with JSON only: {{"status": "accept" | "violations", "violations": [...]}}"""


def prompt_arbiter(st):
    return f"""Style review of commit {st.commit_id} exceeded {MAX_STYLE_CYCLES} cycles.

Follow the instructions in {AGENTS_DIR / 'arbiter.md'}.
Workspace: {st.workspace}
Files: {sorted(set(st.files_touched))}
Remaining violations:
{json.dumps(st.last_style_violations, indent=2)}

Respond with JSON only: {{"proceed": true | false, "reasoning": "...", "style_debt": [...]}}"""


# ─── utilities ──────────────────────────────────────────────────────────────

def load_plan(path: str) -> dict:
    try:
        import tomllib

        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        import toml  # type: ignore

        with open(path, "r") as f:
            return toml.load(f)


def run_cmd(cmd: str, cwd: str) -> tuple[bool, str]:
    """Run a shell command; return (success, combined output)."""
    if not cmd:
        return False, "No command configured"
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=CMD_TIMEOUT_SECS
        )
        return r.returncode == 0, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {CMD_TIMEOUT_SECS}s: {cmd}"
    except OSError as e:
        return False, str(e)


def spawn(st: CommitState, kind: str, prompt: str, schema: str, **extra) -> dict:
    st.awaiting = kind
    return {"action": "spawn", "kind": kind, "prompt": prompt, "response_schema": schema, **extra}


def escalate(st: CommitState, reason: str, state_path: str, resume_state: State) -> None:
    """Persist state and exit 1 so the orchestrator can intervene."""
    st.state = State.NEEDS_LLM.value
    st.escalation_context = reason
    st.resume_state = resume_state.value
    Path(state_path).write_text(st.to_json())
    print(json.dumps({"error": reason, "resume_state": resume_state.value, "state_path": state_path}), file=sys.stderr)
    sys.exit(1)


def handle_gate_failure(st, error, retry_state: State, state_path):
    st.last_gate_error = error
    st.gate_retries += 1
    if st.gate_retries > MAX_GATE_RETRIES:
        escalate(st, f"{retry_state.value} gate failed after {MAX_GATE_RETRIES} retries: {error[-4000:]}", state_path, retry_state)
    st.state = retry_state.value
    return next_action(st, state_path)


# ─── next-action handlers ───────────────────────────────────────────────────

def handle_explore_gates(st, state_path):
    if st.designer_gate and st.test_gate:
        st.state = State.EXPLORE_FORMATTERS.value
        return next_action(st, state_path)
    return spawn(st, "explore_gates", prompt_explore_gates(st), "GateDiscovery", read_only=True)


def handle_explore_formatters(st, state_path):
    if st.fmt_cmd and st.lint_cmd:
        st.state = State.DESIGNER_PHASE.value
        return next_action(st, state_path)
    return spawn(st, "explore_formatters", prompt_explore_formatters(st), "FormatterDiscovery", read_only=True)


def handle_phase(phase: str):
    def handler(st, state_path):
        retry = st.last_gate_error if st.gate_retries > 0 else ""
        return spawn(
            st, "phase", prompt_phase(phase, st, retry), "PhaseResult",
            phase=phase, agent_file=str(AGENTS_DIR / f"{phase}.md"),
        )
    return handler


def handle_designer_gate(st, state_path):
    ok, out = run_cmd(st.designer_gate, st.workspace)
    if ok:
        st.state = State.DESIGNER_STYLE.value
        st.gate_retries = 0
        st.last_gate_error = ""
        return next_action(st, state_path)
    return handle_gate_failure(st, out, State.DESIGNER_PHASE, state_path)


def handle_tester_gate(st, state_path):
    if not st.commit_tests:
        st.state = State.TESTER_STYLE.value
        return next_action(st, state_path)
    ok, _ = run_cmd(st.test_gate, st.workspace)
    if not ok:  # TDD red: new tests must fail against todo!() stubs
        st.state = State.TESTER_STYLE.value
        st.gate_retries = 0
        st.last_gate_error = ""
        return next_action(st, state_path)
    escalate(st, "Tester gate passed but should fail (TDD red). Tests may be vacuous.", state_path, State.TESTER_PHASE)


def handle_implementor_gate(st, state_path):
    ok, out = run_cmd(st.test_gate, st.workspace)
    if ok:
        st.state = State.IMPLEMENTOR_STYLE.value
        st.gate_retries = 0
        st.last_gate_error = ""
        return next_action(st, state_path)
    return handle_gate_failure(st, out, State.IMPLEMENTOR_PHASE, state_path)


def handle_style(st, state_path):
    phase, _, _ = STYLE_STATES[State(st.state)]
    if st.last_style_violations and st.awaiting == "style_review":
        if st.style_cycles >= MAX_STYLE_CYCLES:
            return spawn(st, "arbiter", prompt_arbiter(st), "ArbiterResult",
                         read_only=True, agent_file=str(AGENTS_DIR / "arbiter.md"))
        return spawn(st, "style_fix", prompt_style_fix(phase, st), "PhaseResult",
                     phase=phase, agent_file=str(AGENTS_DIR / f"{phase}.md"))
    return spawn(st, "style_review", prompt_style_review(phase, st), "ReviewResult",
                 read_only=True, phase=phase, skill="review-style")


def handle_scope_review(st, state_path):
    return spawn(st, "scope_review", prompt_scope_review(st), "ReviewResult",
                 read_only=True, skill="review-scope")


def handle_format(st, state_path):
    run_cmd(st.fmt_cmd, st.workspace)
    run_cmd(st.lint_cmd, st.workspace)
    ok, out = run_cmd(st.test_gate, st.workspace)
    if not ok:
        escalate(st, f"Test gate failed after formatting/lint-fix: {out[-4000:]}", state_path, State.FORMAT)
    st.state = State.COMMIT.value
    return next_action(st, state_path)


def handle_commit(st, state_path):
    try:
        add = subprocess.run(["git", "add", "-A"], cwd=st.workspace, capture_output=True, text=True)
        r = subprocess.run(["git", "commit", "-F", "-"], cwd=st.workspace, input=st.commit_message,
                           capture_output=True, text=True)
        ok, out = add.returncode == 0 and r.returncode == 0, add.stderr + r.stdout + r.stderr
    except OSError as e:
        ok, out = False, str(e)
    if ok:
        st.state = State.DONE.value
        st.awaiting = ""
        return {"action": "done", "commit_id": st.commit_id, "style_debt": st.style_debt}
    escalate(st, f"Commit failed: {out}", state_path, State.COMMIT)


def handle_done(st, state_path):
    return {"action": "done", "commit_id": st.commit_id, "style_debt": st.style_debt}


def handle_needs_llm(st, state_path):
    escalate(st, st.escalation_context or "Driver needs intervention", state_path,
             State(st.resume_state or State.DESIGNER_PHASE.value))


STATE_HANDLERS = {
    State.EXPLORE_GATES: handle_explore_gates,
    State.EXPLORE_FORMATTERS: handle_explore_formatters,
    State.DESIGNER_PHASE: handle_phase("designer"),
    State.DESIGNER_GATE: handle_designer_gate,
    State.DESIGNER_STYLE: handle_style,
    State.TESTER_PHASE: handle_phase("tester"),
    State.TESTER_GATE: handle_tester_gate,
    State.TESTER_STYLE: handle_style,
    State.IMPLEMENTOR_PHASE: handle_phase("implementor"),
    State.IMPLEMENTOR_GATE: handle_implementor_gate,
    State.IMPLEMENTOR_STYLE: handle_style,
    State.SCOPE_REVIEW: handle_scope_review,
    State.FORMAT: handle_format,
    State.COMMIT: handle_commit,
    State.DONE: handle_done,
    State.NEEDS_LLM: handle_needs_llm,
}


def next_action(st: CommitState, state_path: str) -> dict:
    return STATE_HANDLERS[State(st.state)](st, state_path)


# ─── report processing ──────────────────────────────────────────────────────

PHASE_NEXT = {
    State.DESIGNER_PHASE: State.DESIGNER_GATE,
    State.TESTER_PHASE: State.TESTER_GATE,
    State.IMPLEMENTOR_PHASE: State.IMPLEMENTOR_GATE,
}


def record_files(st, result):
    st.files_touched.extend(result.get("files_created", []) or [])
    st.files_touched.extend(result.get("files_modified", []) or [])


def needs_llm(st, reason, resume_state: State):
    st.state = State.NEEDS_LLM.value
    st.escalation_context = reason
    st.resume_state = resume_state.value


def process_report(st: CommitState, result: dict) -> None:
    s = State(st.state)
    kind = st.awaiting
    if kind == "explore_gates":
        st.designer_gate = result.get("designer_gate") or "cargo check"
        st.test_gate = result.get("test_gate") or "cargo test"
        st.state = State.EXPLORE_FORMATTERS.value
    elif kind == "explore_formatters":
        st.fmt_cmd = result.get("fmt_cmd") or "cargo fmt"
        st.lint_cmd = result.get("lint_cmd") or "cargo clippy --fix --allow-dirty --allow-staged"
        st.state = State.DESIGNER_PHASE.value
    elif kind == "phase" and s in PHASE_NEXT:
        record_files(st, result)
        if result.get("status") == "problems":
            needs_llm(st, f"{s.value} reported problems: {result.get('notes', '')}", s)
        else:
            st.state = PHASE_NEXT[s].value
    elif kind == "style_review" and s in STYLE_STATES:
        if result.get("status") == "accept":
            st.style_cycles = 0
            st.last_style_violations = []
            st.state = STYLE_STATES[s][2].value
        else:
            st.last_style_violations = result.get("violations", []) or ["(unspecified violation)"]
            st.style_cycles += 1
    elif kind == "style_fix" and s in STYLE_STATES:
        record_files(st, result)
        # Re-run the phase's gate before re-reviewing: fixes must keep it green.
        gate = st.designer_gate if s == State.DESIGNER_STYLE else st.test_gate
        if s != State.TESTER_STYLE:
            ok, out = run_cmd(gate, st.workspace)
            if not ok:
                needs_llm(st, f"Gate broke after style fix in {s.value}: {out[-4000:]}", STYLE_STATES[s][1])
        st.last_style_violations = []
    elif kind == "arbiter" and s in STYLE_STATES:
        if result.get("proceed"):
            st.style_debt.extend(result.get("style_debt", []) or [])
            st.style_cycles = 0
            st.last_style_violations = []
            st.state = STYLE_STATES[s][2].value
        else:
            needs_llm(st, f"Arbiter rejected style in {s.value}: {result.get('reasoning', '')}", STYLE_STATES[s][1])
    elif kind == "scope_review" and s == State.SCOPE_REVIEW:
        status = str(result.get("status", result.get("response", ""))).lower()
        if "violation" in status:
            needs_llm(st, f"Scope violations: {result.get('violations', status)}", State.SCOPE_REVIEW)
        else:
            st.state = State.FORMAT.value
    else:
        print(json.dumps({"warning": f"unexpected report in state {s.value} (awaiting {kind!r}); ignored"}),
              file=sys.stderr)
        return
    st.awaiting = "" if kind != "style_review" else kind


# ─── CLI ────────────────────────────────────────────────────────────────────

def read_state(path):
    return CommitState.from_json(Path(path).read_text())


def write_state(path, st):
    Path(path).write_text(st.to_json())


def cmd_init(args):
    plan = load_plan(args.plan)
    meta = plan["meta"]
    commits = {c["id"]: c for c in plan["commits"]}
    if args.commit not in commits:
        sys.exit(f"commit {args.commit} not in plan (have {sorted(commits)})")
    c = commits[args.commit]
    st = CommitState(
        plan_path=args.plan,
        commit_id=args.commit,
        workspace=args.workspace or meta.get("workspace", "."),
        feature_dir=meta.get("feature_dir", str(Path(args.plan).parent)),
        commit_title=c["title"],
        commit_message=c["message"],
        commit_files=c.get("files", []),
        commit_tests=c.get("tests", []),
        commit_acceptance=c.get("acceptance", []),
        commit_anti_patterns=c.get("anti_patterns", []),
        designer_gate=args.designer_gate or "",
        test_gate=args.test_gate or "",
        fmt_cmd=args.fmt_cmd or "",
        lint_cmd=args.lint_cmd or "",
    )
    Path(args.state).parent.mkdir(parents=True, exist_ok=True)
    write_state(args.state, st)
    print(json.dumps({"initialized": args.state}))


def cmd_next(args):
    st = read_state(args.state)
    act = next_action(st, args.state)
    write_state(args.state, st)
    print(json.dumps(act))


def cmd_report(args):
    st = read_state(args.state)
    if args.result_file:
        raw = sys.stdin.read() if args.result_file == "-" else Path(args.result_file).read_text()
    else:
        raw = args.result
    process_report(st, json.loads(raw))
    write_state(args.state, st)
    print(json.dumps({"state": st.state}))


def cmd_resume(args):
    st = read_state(args.state)
    if st.state == State.NEEDS_LLM.value:
        st.state = args.to or st.resume_state or State.DESIGNER_PHASE.value
        st.escalation_context = ""
        st.resume_state = ""
        st.awaiting = ""
        st.gate_retries = 0
        st.style_cycles = 0
        st.last_style_violations = []
    write_state(args.state, st)
    cmd_next(args)


def cmd_status(args):
    print(read_state(args.state).to_json())


def main():
    p = argparse.ArgumentParser(description="implement-commit state machine driver")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="Initialize state for one commit")
    i.add_argument("--plan", required=True, help="Path to implementation-plan.toml")
    i.add_argument("--commit", type=int, required=True, help="Commit id from the plan")
    i.add_argument("--state", required=True, help="Path to the state file to create")
    i.add_argument("--workspace", help="Override [meta].workspace")
    i.add_argument("--designer-gate", help="Compile gate (skips gate discovery when set with --test-gate)")
    i.add_argument("--test-gate", help="Test gate")
    i.add_argument("--fmt-cmd", help="Formatter (skips formatter discovery when set with --lint-cmd)")
    i.add_argument("--lint-cmd", help="Lint-fix command")

    n = sub.add_parser("next", help="Get the next action")
    n.add_argument("--state", required=True)

    r = sub.add_parser("report", help="Report a subagent result")
    r.add_argument("--state", required=True)
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--result", help="JSON result string")
    g.add_argument("--result-file", help="File containing the JSON result, or - for stdin")

    s = sub.add_parser("resume", help="Resume after intervention")
    s.add_argument("--state", required=True)
    s.add_argument("--to", choices=[x.value for x in State if x not in (State.NEEDS_LLM,)],
                   help="State to resume in (default: the state recorded at escalation)")

    t = sub.add_parser("status", help="Print the state file")
    t.add_argument("--state", required=True)

    args = p.parse_args()
    {"init": cmd_init, "next": cmd_next, "report": cmd_report, "resume": cmd_resume, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    main()
