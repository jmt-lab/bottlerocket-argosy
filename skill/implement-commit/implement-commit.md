---
type: Skill
description: Implement the commits of an implementation-plan.toml one at a time through a mechanical TDD pipeline (designer → tester → implementor subagents, compile/test gates, style and scope review, format, git commit) driven by a harness-agnostic state-machine script; use once a feature has an approved implementation plan and you are ready to write code.
---

# Implement commit

Execute commits from `$FEATURE_DIR/implementation-plan.toml` (see `document/bottlerocket/feature-proposal-workflow`) using a TDD pipeline. The driver `references/ic-driver.py` owns all state transitions, runs gates/formatters/`git commit` itself, and tells you when to dispatch a subagent. It never launches agents, so it works with any harness.

## Your role

You are a mechanical orchestrator. You only:

1. Call driver commands.
2. Dispatch the subagents the driver asks for and pass back their JSON results.
3. Intervene when the driver escalates (exit 1).

Do not read the code or the feature docs yourself unless something fails — trust the driver and keep your context small.

## Prerequisites

- Python 3.11+ (for `tomllib`; on older Python install the `toml` package).
- `$FEATURE_DIR` containing `design.md`, `test-plan.md`, and `implementation-plan.toml` (from `skill/propose-implementation-plan` or `skill/ad-hoc-implementation-plan`).
- The workspace named by `[meta].workspace` (relative to where you run the driver) is a git checkout on a feature branch with a clean tree.
- A state directory **outside the workspace** (or git-ignored), because the commit step runs `git add -A`. Default suggestion: `${TMPDIR:-/tmp}/ic-<feature>/`. If `$FEATURE_DIR` is inside the workspace, its docs will be included in the first commit unless they are already committed or ignored; decide that with the user up front.

## Main loop

Process commits in dependency order (`[dependencies]` in the plan; commits whose dependencies are all done may run in parallel only if they touch disjoint files and use separate worktrees).

```bash
DRIVER=<this skill dir>/references/ic-driver.py
STATE=${TMPDIR:-/tmp}/ic-<feature>/commit-<N>.json

python3 "$DRIVER" init --plan "$FEATURE_DIR/implementation-plan.toml" --commit <N> --state "$STATE"
# Optional: skip gate/formatter discovery by passing them explicitly, e.g.
#   --designer-gate 'cargo check -p foo' --test-gate 'cargo test -p foo' \
#   --fmt-cmd 'cargo fmt -p foo' --lint-cmd 'cargo clippy -p foo --fix --allow-dirty --allow-staged'

python3 "$DRIVER" next --state "$STATE"
```

Repeat:

1. Run `next`. It prints one JSON action.
2. If `"action": "done"`, the commit is made; note any `style_debt` and move to the next commit.
3. If `"action": "spawn"`, dispatch a fresh subagent (see below), take its JSON result, and report it:

   ```bash
   python3 "$DRIVER" report --state "$STATE" --result-file - <<'EOF'
   {"status": "ok", "files_created": [...], "files_modified": [...]}
   EOF
   ```

4. If `next` exits 1, handle the escalation (below), then run `resume`.

## Dispatching a spawn action

Each spawn action has `kind`, `prompt`, `response_schema`, and optionally `phase`, `agent_file`, `skill`, `read_only`.

- Give the subagent the `prompt` verbatim. If `agent_file` is present, include that file's instructions (it lives in `references/agents/`). If `skill` is `review-style` or `review-scope`, load that skill from this argosy if available; otherwise the prompt is self-sufficient.
- Run the subagent in the workspace. When `read_only` is true, tell it not to modify files.
- Require a JSON-only reply matching `response_schema`:

| Schema | Shape |
|--------|-------|
| `GateDiscovery` | `{"designer_gate": str, "test_gate": str}` |
| `FormatterDiscovery` | `{"fmt_cmd": str, "lint_cmd": str}` |
| `PhaseResult` | `{"status": "ok"\|"problems", "files_created": [str], "files_modified": [str], "notes": str\|null}` |
| `ReviewResult` | `{"status": "accept"\|"violations", "violations": [str]}` |
| `ArbiterResult` | `{"proceed": bool, "reasoning": str, "style_debt": [str]}` |

Use a fresh subagent per spawn so each phase sees only its own instructions. If the reply is not valid JSON, extract the fields or re-ask; do not invent results.

## Pipeline

```
EXPLORE_GATES → EXPLORE_FORMATTERS →
DESIGNER_PHASE → DESIGNER_GATE → DESIGNER_STYLE →
TESTER_PHASE → TESTER_GATE (must FAIL: TDD red) → TESTER_STYLE →
IMPLEMENTOR_PHASE → IMPLEMENTOR_GATE → IMPLEMENTOR_STYLE →
SCOPE_REVIEW → FORMAT (fmt, lint-fix, re-run test gate) → COMMIT → DONE
```

- Gate failures re-dispatch the phase with the error (up to 2 retries), then escalate.
- Style violations alternate fix → re-review up to 3 cycles, then the arbiter decides proceed (recording style debt) or fail.
- The tester gate escalates if tests pass against stubs (vacuous tests).

## Handling escalation

`next`/`resume` exit 1 with `{"error": ..., "resume_state": ...}` on stderr. This is where you think:

- **Gate failed after retries** — read the error. If the code is wrong, dispatch a fixer subagent with the error, the phase's agent file, and the commit; if the gate command is wrong (wrong crate, needs a feature flag), fix it in the state file (`status` shows it) and resume.
- **Tester gate passed (vacuous tests)** — dispatch the tester again explaining the tests must fail against stubs, or confirm with the user that the commit's tests legitimately pass already.
- **Phase reported problems / arbiter rejected / scope violations** — summarise for the user and agree a fix; for scope violations, revert out-of-scope changes or, with user approval, update the plan's `files`.
- **Commit failed** — usually hooks or nothing to commit; inspect `git status`.

Then continue with `python3 "$DRIVER" resume --state "$STATE"` (resumes at the recorded state; override with `--to <state>`).

## Driver commands

| Command | Purpose |
|---------|---------|
| `init` | Create the state file for one commit (optional gate/format overrides) |
| `next` | Run gates/format/commit directly, or print the next spawn action |
| `report` | Record a subagent result (`--result JSON` or `--result-file FILE\|-`) |
| `resume` | Continue after intervention (`--to STATE` to override) |
| `status` | Print the state file |

## Finish

After the last commit, report the commits created (`git log --oneline`), any recorded style debt, and anything escalated. Do not push or open a PR unless the user asks.
