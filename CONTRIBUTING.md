# Contributing to DataPilot AI

Rahman Ali and Akbar Hussain use this workflow for all 15 working days. The goal is to keep both members' work independent, reviewable, and safe to integrate.

## Branch responsibilities

- `main`: stable mentor/demo releases only
- `dev`: reviewed daily integration work
- `feature/dayXX-description-name`: new daily functionality
- `chore/dayXX-description-name`: integration, documentation, QA, or release preparation

Examples:

- `feature/day01-frontend-foundation-rahman`
- `feature/day01-backend-foundation-akbar`
- `chore/day05-week1-ui-polish-rahman`

Never commit directly to `main` or `dev`. Never share a feature branch or force-push a reviewed branch.

## Starting daily work

Begin only with a clean working tree:

```bash
git fetch --prune origin
git switch dev
git pull --ff-only origin dev
git switch -c feature/dayXX-task-name-member
```

If the branch already exists, inspect and switch to it instead of recreating it. Do not discard uncommitted changes to make the commands succeed.

## Ownership and shared files

- Rahman normally changes `frontend/**`.
- Akbar normally changes `backend/**`, backend dependencies, migrations, API contracts, Docker files, and `.env.example`.
- A root or shared file must have one named owner for that task.
- If an API mismatch is found, Rahman reports the mismatch and Akbar updates `docs/api-contracts.md` with the agreed contract.

Do not rewrite or reformat unrelated files owned by the other member.

## Commit style

Use small, descriptive conventional commits:

```text
feat(frontend): scaffold application routes
feat(api): add dataset upload endpoint
fix(runs): stop polling after terminal state
test(ml): cover regression model selection
docs: document clean-clone setup
chore: prepare week one integration review
```

Before committing:

1. Review `git status` and the complete diff.
2. Run the relevant tests, lint, checks, or build.
3. Stage explicit files belonging to the current task.
4. Verify that secrets, generated files, databases, uploads, and local dependencies are not staged.

## Pull requests

- Daily feature/chore PRs target `dev`.
- Friday release PRs target `main` only after mentor approval.
- The author requests the other member as reviewer.
- The author does not approve their own PR.
- New commits after approval require the reviewer to inspect the latest diff again.
- All blocking feedback and conversations must be resolved before merge.

Each PR must describe scope, changed files, validation performed and actual results, screenshots for UI work, API or migration effects, assumptions, limitations, and follow-up work.

## Merge policy

Use squash merge for daily feature/chore PRs so each task becomes one clear integration commit. Delete the merged feature branch. Both members then fetch/prune and fast-forward local `dev` before starting the next task.

Do not merge `dev` into `main` outside the approved Week 1, Week 2, and final release checkpoints.

## Conflict recovery

Do not use `git reset --hard`, whole-file ours/theirs resolution, or force-push to escape a conflict.

For a published feature branch:

1. Fetch the latest `origin/dev`.
2. Merge `origin/dev` into the feature branch.
3. Review and resolve each conflicting line with both responsibilities preserved.
4. Run all affected validation again.
5. Push the resolution and request a fresh review.

If a shared configuration or contract is involved, both members review the resolution together.

## Secrets and generated content

Never commit real environment files, API keys, credentials, uploaded datasets, SQLite databases, generated models, reports, media, dependency folders, caches, build outputs, or IDE state. Use safe examples and documented generation steps instead.
