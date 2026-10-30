---
type: Skill
description: Write and test a Bottlerocket settings (datastore) migration in the bottlerocket repo — choose the migration-helpers type, create the sources/settings-migrations/v<X.Y.Z>/<name> crate, register it in sources/Cargo.toml and Release.toml, unit/local test it, and optionally qualify it with a real upgrade/downgrade on EC2. Use whenever a change adds, removes, renames or re-values a persisted setting between releases.
---

# Write a migration

Background, helper semantics, layout and the full EC2 upgrade/downgrade procedure are in `document/bottlerocket/migrations`. Read it first; this is the procedure.

## Input

- What changed (settings added/removed/renamed/re-valued).
- Target release `X.Y.Z` (the release that first ships the change) and the previous release.
- Migration name (kebab-case, describes the change).
- Optional: variant scope.

## Procedure

1. **Confirm a migration is needed.** Changes to `configuration-files.*`/`services.*` don't need one. New keys, removed keys, changed values and structural changes do.
2. **Pick the type** from the helper table in `document/bottlerocket/migrations`: `AddSettingsMigration` for new keys with known names, `AddPrefixesMigration` for user-defined map keys, `RemoveSettingsMigration` for removed keys, `ReplaceStringMigration`/`ReplaceListsMigration`/`RestrictListsMigration` for value changes, a custom `Migration` impl for anything else. Read the helper's doc comment and tests in `sources/api/migration/migration-helpers/src/common_migrations.rs`.
3. **Avoid variant-conditional builds** unless unavoidable (see the caveat in the document); a variant-agnostic helper is usually safe on every variant.
4. **Create the crate** at `sources/settings-migrations/vX.Y.Z/<name>/` with `Cargo.toml` (`migration-helpers.workspace = true`) and `src/main.rs`, copying the most recent similar migration in `sources/settings-migrations/` and the templates in the document. Write a doc comment saying what changed and listing the keys.
5. **Custom logic:** touch only keys that exist (`if let Some`), never add keys unconditionally, implement both directions, and add `#[cfg(test)]` tests including a sparse-input case.
6. **Register:**
   - `sources/Cargo.toml` `members`: add `"settings-migrations/vX.Y.Z/<name>"` after the "add new ones after this line" comment.
   - `Release.toml` `[migrations]`: add `"migrate_vX.Y.Z_<name>.lz4"` to the `"(<prev>, X.Y.Z)"` entry (create it if missing). Make sure `version` in `Release.toml` and `release-version` in `Twoliter.toml` are `X.Y.Z` for that release.
7. **Build and check:** `cd sources && cargo build -p <name> && cargo test -p <name>`, then `cargo make check-migrations` from the repo root.
8. **Local run:** run the binary `--forward` then `--backward` against a small datastore directory (layout in the document) and diff the results against the input.
9. **Qualify (recommended for anything non-trivial):** follow "Full upgrade/downgrade on EC2" in the document — old AMI, new TUF repo, `updog update`, verify, `signpost rollback-to-inactive`, verify. Or run the TestSys `migration` test.
10. **Commit** with a header like `migrations: add <name>` (match recent history with `git log --oneline -- sources/settings-migrations`), signed off.

## Validation

- [ ] Crate under the correct `vX.Y.Z`, name == directory name
- [ ] Listed in `sources/Cargo.toml` and in the right `Release.toml` pair
- [ ] Both directions implemented; no key assumed to exist
- [ ] `cargo test`, `cargo make check-migrations` pass
- [ ] Forward/backward local run (and, if done, EC2 upgrade/downgrade) leave the expected settings
