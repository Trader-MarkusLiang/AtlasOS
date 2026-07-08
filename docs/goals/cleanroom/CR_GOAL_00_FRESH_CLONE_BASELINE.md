# CR_GOAL_00 - FRESH CLONE BASELINE

## Objective

Create a truly independent clean-room environment.

## Required Tests

1. Verify the remote candidate commit exists.
2. Create a fresh clone outside the existing working tree.
3. Checkout exact candidate commit `ed63678793bdc5d10c1469433e461a6c20db7927`.
4. Do not copy runtime SQLite, telemetry logs, PID files, local portfolio files, old inbox, old
   state, old artifacts, or generated caches.
5. Use fresh paths for runtime DB, logs, inbox, telemetry, PID, and temp config.
6. Record clone path, commit, branch/detached state, Python version, macOS version, dependencies,
   ports, and environment variable names only.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_00_Fresh_Clone_Baseline.md`

## Acceptance

- fresh clone proven;
- exact commit proven;
- no runtime-state reuse;
- no prior DB reuse;
- no prior telemetry reuse.

