# OpenBrick EDU — Project Instructions

Open-source, LEGO Technic-compatible educational robotics platform.
ESP32-S3 hub + 3D-printed housings + Web IDE (Blockly + MicroPython).
Target: ages 10–14 | BOM < $60 USD | Turkey-sourced components.

## Architecture

Three layers: Web IDE (React/TS/Blockly) → BLE/USB Transport (framed binary, CRC-16) → ESP32-S3 Firmware (MicroPython + C extensions).
See @docs/architecture.md for full diagram.

Firmware modules: boot/ → ble/ → hal/ → drivers/ → executor/ → matrix/ → audio/ → storage/
IDE modules: src/blockly/ → src/editor/ → src/ble/ → src/dashboard/ → src/i18n/ → src/projects/

## CRITICAL: LEGO Dimensions (NEVER hardcode without checking)

| Parameter | Dimension | Tolerance |
|---|---|---|
| Stud pitch | 8.0 mm | ±0.05 mm |
| Pin hole diameter | 4.9 mm | ±0.1 mm |
| Axle cross-hole | 5.6 mm | ±0.1 mm |
| Pin hole (3D print) | 5.1–5.3 mm | Calibrate per printer |
| Beam width | 7.8 mm | ±0.1 mm |
| Brick height | 9.6 mm | ±0.1 mm |

Full spec: @docs/lego-specs.md | Calibration jig: @hardware/test-jigs/

## Languages & Tools

- Firmware: MicroPython + C extensions | Lint: ruff, clang-tidy | Types: mypy strict
- IDE: TypeScript strict + React + Blockly | Lint: ESLint strict + Prettier | Test: Jest + Playwright
- 3D: FreeCAD/OpenSCAD parametric models | PCB: KiCad 8+
- CI/CD: GitHub Actions | Version Control: Trunk-based, short-lived feature branches (max 1–2 days)

## Workflow Rules

- Conventional Commits: feat:, fix:, docs:, refactor:, test:, chore:, ci:
- ALWAYS write a failing test before implementing (TDD is non-negotiable)
- ALWAYS run lint + type-check + tests before committing
- Commit after each passing test (small, frequent commits — ≥1/day target)
- Update docs/changelog.md when completing any task
- Flag code smells as GitHub issues with tech-debt label during every session
- At 50% context usage, /compact or start a fresh session with a written handoff note
- After 2 corrections on the same issue, start a fresh session

## Plan Before You Build

- Use plan mode first — analyze relevant code, propose approach, identify files to modify
- Approve the plan before any code changes
- Reference existing code as style examples (one example > 100 words of explanation)
- Use CIF prompts: Context (files, state) → Intent (what + acceptance criteria) → Format (tests first, follow pattern in X)

## When Uncertain

- Hardware specs: STOP and check @docs/lego-specs.md or @docs/bom.md — never guess dimensions
- Architecture: STOP and check @docs/adr/ for prior decisions
- No ADR exists: Flag the decision and ask before proceeding
- Sensor/motor details: Reference datasheets in @docs/sensors/ or @docs/motors/

## Quality Gates (CI enforces all)

- Zero lint warnings (ruff + ESLint strict)
- mypy strict / TypeScript strict pass — no `any` without `// JUSTIFIED:` comment
- Coverage: ≥80% firmware, ≥75% IDE (fail on decrease)
- Cyclomatic complexity ≤ 10 per function
- IDE bundle size < 500KB gzipped (size-limit check)
- Hub boot time < 3 seconds (QEMU bench on firmware PRs)
- Dependency audit: npm audit / pip-audit clean
- Duplication: flag files with >15% similar blocks

## Non-Functional Requirements (first-class deliverables)

Track in docs/nfr-status.md (red/amber/green). Check NFR impacts when modifying perf-critical paths.

| ID | Requirement | Criteria | Automated? |
|---|---|---|---|
| NFR-P01 | Hub boot time | < 3s power-on to BLE-ready | Yes (CI) |
| NFR-P02 | Sensor polling rate | ≥ 50 Hz all 6 ports | Manual |
| NFR-P04 | IDE page load | < 3s on 10 Mbps | Yes (Lighthouse CI) |
| NFR-P05 | BLE upload speed | < 5s for <10KB program | Yes (bench) |
| NFR-R01 | Crash recovery | Watchdog reset < 5s | Yes (test) |
| NFR-R02 | Battery safety | BMS cutoff 2.8V/4.2V/60°C | Manual checklist |
| NFR-R04 | Child safety | No sharp edges, ≥0.5mm fillet | Manual checklist |
| NFR-U01 | First-time setup | ≤ 5 steps, age 10+ | Manual test |
| NFR-M01 | New sensor driver | < 200 LOC via HAL | Review |

Safety NFRs (R02, R03, R04): complete docs/safety-checklist.md at every hardware phase end. Photograph and commit.

## Key File References

- @docs/plan.md — Current sprint plan (review at session start)
- @docs/adr/ — Architecture Decision Records (Origin: Human | AI-Suggested & Human-Approved)
- @docs/changelog.md — What shipped
- @docs/nfr-status.md — NFR dashboard
- @docs/metrics.md — Weekly project health
- @docs/validation-log.md — Hardware test results
- @docs/safety-checklist.md — Physical safety verification
- @.claude/skills/ — Domain knowledge (loaded on demand)

## What NOT to Do

- NEVER hardcode LEGO dimensions without referencing the tolerance table
- NEVER merge to main without CI green
- NEVER skip tests because the code "looks right"
- NEVER let the agent investigate broadly — scope narrowly or use a subagent
- NEVER commit .env files, API keys, tokens, passwords, or secrets
- NEVER accept agent-suggested packages without verifying they exist and are maintained
