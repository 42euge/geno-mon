# geno-mon — agent observability for agentic harnesses

geno-mon parses session logs from coding agents and computes observability metrics: loop efficiency, tool use patterns, context/cache behavior, and planning signals. It answers the question most benchmarks ignore — not *what* the agent produced, but *how* it got there.

## Skills

| Skill | Sub-skillset | Slash command |
|-------|-------------|---------------|
| geno-mon | -- | /geno-mon (umbrella) |

## Repo structure

```
geno-mon/
├── GENO.md              # agent instructions (this file)
├── SKILL.md             # root pointer → skills/geno-mon/SKILL.md
├── genotools.yaml       # geno-tools manifest
├── pyproject.toml       # Python package (click-based CLI)
├── skills/
│   └── geno-mon/        # umbrella skill
│       └── SKILL.md
├── geno_mon/            # Python package
│   ├── cli.py           # Click CLI — entry point, display, formatting
│   ├── parser.py        # JSONL → dataclasses, session discovery
│   ├── models.py        # Dataclass definitions (Session, Turn, ToolCall, etc.)
│   └── metrics.py       # Metrics computed from a parsed Session
├── tests/
├── docs/                # MkDocs Material site
└── mkdocs.yml
```

## Architecture

Data flows through three layers:

```
JSONL file → parser.py → models.py (dataclasses) → metrics.py → cli.py (display)
```

1. **`parser.py`** reads raw JSONL and constructs a `Session` object with linked `Turn`s, `ToolCall`s, and `SubagentSpawn`s
2. **`models.py`** defines the data model — pure dataclasses with computed properties
3. **`metrics.py`** takes a `Session` and computes `SessionMetrics` (loop efficiency, tool patterns, context, planning)
4. **`cli.py`** handles all I/O — session discovery, interactive picker, formatted output, JSON serialization

Each layer only depends on the one before it.

## Conventions

- **Entry point**: `geno_mon.cli:entry_point` (Click-based)
- **No heavy dependencies**: only runtime dep is `click`; everything else is stdlib
- **Dataclasses over dicts**: parsed data is typed dataclasses, not raw dicts
- **Metrics are computed, not stored**: always derived fresh from the parsed session
- **Type hints** on all function signatures
- **Prefix aliasing**: slash commands use the canonical `geno-` prefix (e.g. `/geno-mon`). Short aliases like `/gt-mon` are configured per-install in `~/.geno/config.yaml` and are not hardcoded in this repo. See the [geno-tools alias docs](https://github.com/42euge/geno-tools) for details.

### Adding a new skill

To add a new skill (sub-skillset) to this repo:

1. Create a directory under `skills/<skill-name>/` with a `SKILL.md` following the standard frontmatter schema (name, description, allowed-tools, argument-hint, metadata).
2. Register the skill in `genotools.yaml` if it requires additional venv deps or install hooks.
3. Add the skill to the **Skills** table in this file.
4. If the skill is the repo's primary (umbrella) skill, update the root `SKILL.md` symlink to point to it.

## Dependencies and runtime

- Python >= 3.10
- Runtime dependency: `click >= 8.0`
- Install via: `geno-tools install geno-mon`
