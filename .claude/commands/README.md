# Claude Code Skills

Custom slash commands for this project. Each `.md` file in this directory becomes a `/command-name` skill available in Claude Code sessions.

## Usage

```
/<skill-name>              # run with no arguments
/<skill-name> <argument>   # run with an argument (available as $ARGUMENTS inside the skill)
```

## Available Skills

| Command | Description |
|---------|-------------|
| `/fix-ci` | Finds the most recent failing GitHub Actions run, diagnoses the root cause, applies a fix, and pushes. Optionally accepts a run ID: `/fix-ci 12345678`. |

## Adding a New Skill

1. Create `.claude/commands/<name>.md`
2. Write the skill as a prompt — describe the goal, the steps Claude should follow, and how `$ARGUMENTS` should be interpreted
3. Add a row to the table above
4. Commit the file — skills are version-controlled alongside the code they operate on

## Conventions

- Keep skills focused on one task
- Use shell code blocks to show the exact commands Claude should run
- Document the expected output or success condition so Claude knows when it is done
- Prefer skills that verify their own outcome (e.g. check CI status after pushing a fix)
