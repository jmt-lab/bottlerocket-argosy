---
type: Guide
description: How Bottlerocket settings (datastore) migrations work and how to write one — the Migration trait and forward/backward semantics, the migration-helpers common_migrations types and when to use each, crate naming and the sources/settings-migrations/v<X.Y.Z>/ layout, variant-conditional builds, wiring into sources/Cargo.toml and Release.toml, unit and local datastore testing, and a full upgrade/downgrade test on EC2 through a self-hosted TUF repo.
---

# Settings migrations

A migration transforms the on-disk settings datastore when a node moves between OS versions. Where migrations sit in the build (the `settings-migrations` RPM, static linking, `Release.toml`) is covered in `document/bottlerocket/architecture`; the short "add a migration" checklist is in `document/bottlerocket/development`. This guide is the detailed version.

## When you need one

Any change to the persisted data model between releases:

- **New setting** (with a default or generated) — old versions don't understand it, so it must be removed on downgrade.
- **New settings under a user-defined map prefix** (e.g. `settings.kernel.sysctl`, `settings.host-containers`) — key names are unknown, remove by prefix on downgrade.
- **Setting removed from the model** — new version would reject it, so remove on upgrade.
- **Value renamed/replaced** (a string or list of strings), or new allowed values added to a list setting.
- **Anything structural** (rename a key, move a value) — custom migration.

`configuration-files.*` and `services.*` metadata no longer need migrations: since core-kit 6.4.0 the migrator deletes and re-populates them on every run. The v1.37.0 migration `delete-configs-and-services-on-downgrade` covers downgrades to releases older than that.

## How they run

- A migration is a small Rust binary that implements `migration_helpers::Migration` (`forward` for upgrade, `backward` for downgrade) and calls `migrate(...)` from `main`.
- The **migrator** (in `bottlerocket-core-kit`, `sources/api/migration/migrator`) runs on boot when the datastore version does not match the OS version. It fetches the needed migrations from the TUF repo (lz4-compressed), runs them in order, and writes a new versioned datastore before flipping the `current` link.
- Each binary is called with `--source-datastore PATH --target-datastore PATH (--forward | --backward)`; source and target must differ.
- `migrate()` runs the migration over **live** data and over **every pending transaction**. Pending data is usually sparse, so a migration **must not assume any key exists**, and must not add a key unconditionally (you would inject it into an unrelated pending transaction).
- `MigrationData` = `data: HashMap<String, serde_json::Value>` (dotted keys such as `settings.ntp.time-servers`) + `metadata: HashMap<String, HashMap<String, Value>>`.
- Migrations run serially, ordered as listed in `Release.toml`.

## Layout and naming

```
sources/
  Cargo.toml                                   # workspace; every active migration is a member
  api/migration/migration-helpers/             # Migration trait, migrate(), common_migrations
  settings-migrations/
    v1.66.0/
      nvidia-driver-branch-setting/            # crate name == directory name
        Cargo.toml
        src/main.rs
    archived/                                  # old migrations, not built
packages/settings-migrations/settings-migrations.spec
Release.toml
```

- The version directory is the release in which the migration first applies (the "to" side of the version pair). It must match the `version` in `Release.toml` for that release.
- The spec builds every crate under `sources/settings-migrations/v[0-9]*/` statically and installs it as `%{_cross_datadir}/migrations/migrate_<version>_<crate-name>`. Publishing adds `.lz4`, giving the names used in `Release.toml`, e.g. `migrate_v1.66.0_nvidia-driver-branch-setting.lz4`.
- Use a descriptive kebab-case name that says what changed (`kubernetes-memory-qos-settings`, `container-runtime-snapshotter-setting`).

## migration-helpers common migrations

All in `migration_helpers::common_migrations` (`sources/api/migration/migration-helpers/src/common_migrations.rs`):

| Type | Upgrade | Downgrade | Use for |
|---|---|---|---|
| `AddSettingsMigration(&[...])` | no-op | removes listed keys | new settings with known names (most common) |
| `AddPrefixesMigration(vec![...])` | no-op | removes keys under prefixes | new user-defined keys in a map |
| `AddPrefixSuffixMigration(vec![PrefixSuffix{prefix, suffix}])` | no-op | removes keys matching `prefix*suffix` | new sub-key added inside every entry of a map |
| `RemoveSettingsMigration(&[...])` | removes listed keys | no-op | setting dropped from the model |
| `ReplaceStringMigration { setting, old_val, new_val }` | old → new if it matches | new → old | changed string value |
| `ReplaceListsMigration(vec![ListReplacement{..}])` | replaces matching list | reverses | changed list-of-strings value |
| `RestrictListsMigration(vec![ListRestriction{setting, allowed_vals}])` | no-op | filters list to values the old version accepts | new allowed values in a list setting |
| `RemoveMatchingString { setting, old_val }` | removes the setting if it equals `old_val` | no-op | dropping a stale value so the new default/generator applies |
| `NoOpMigration` | no-op | no-op | the "doesn't apply" branch of a variant-conditional migration |

Read the struct's doc comment and tests in `common_migrations.rs` before using the less common ones; their exact field names are defined there.

## Writing a migration

`Cargo.toml` (dependencies come from the workspace):
```toml
[package]
name = "my-new-setting"
version = "0.1.0"
license = "Apache-2.0 OR MIT"
edition = "2021"
publish = false
# Don't rebuild crate just because of changes to README.
exclude = ["README.md"]

[dependencies]
migration-helpers.workspace = true
```

`src/main.rs`, using a common helper:
```rust
use migration_helpers::common_migrations::AddSettingsMigration;
use migration_helpers::{migrate, Result};
use std::process;

/// We added a new setting for <feature>:
/// - settings.my-service.new-setting
fn run() -> Result<()> {
    migrate(AddSettingsMigration(&["settings.my-service.new-setting"]))
}

// Returning a Result from main makes it print a Debug representation of the error, but with Snafu
// we have nice Display representations of the error, so we wrap "main" (run) and print any error.
// https://github.com/shepmaster/snafu/issues/110
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        process::exit(1);
    }
}
```

Custom migration — implement the trait yourself and only touch keys that are present:
```rust
use migration_helpers::{migrate, Migration, MigrationData, Result};

/// We renamed settings.old-name to settings.new-name, preserving the value.
struct RenameSetting;

impl Migration for RenameSetting {
    fn forward(&mut self, mut input: MigrationData) -> Result<MigrationData> {
        if let Some(val) = input.data.remove("settings.old-name") {
            println!("Renamed settings.old-name -> settings.new-name");
            input.data.insert("settings.new-name".to_string(), val);
        }
        Ok(input)
    }

    fn backward(&mut self, mut input: MigrationData) -> Result<MigrationData> {
        if let Some(val) = input.data.remove("settings.new-name") {
            println!("Renamed settings.new-name -> settings.old-name");
            input.data.insert("settings.old-name".to_string(), val);
        }
        Ok(input)
    }
}

#[snafu::report]
fn main() -> Result<()> {
    migrate(RenameSetting)
}
```
(`v1.37.0/delete-configs-and-services-on-downgrade` is a real custom migration with `#[cfg(test)]` unit tests using `maplit::hashmap!`; copy its shape.)

### Variant-conditional migrations

Sometimes a change applies only to some variants. The pattern (see `sources/settings-migrations/archived/v1.11.0/aws-creds`) is a `build.rs` that emits variant `cfg`s, then `cfg!()` branches in `run()`, with `NoOpMigration` (or a different helper) for variants where the change does not apply — every variant must still get a binary so the migrator can build the intermediate datastore.

```rust
// build.rs
use bottlerocket_variant::Variant;

fn main() {
    let variant = Variant::from_env().unwrap();
    variant.emit_cfgs();
}
```
```rust
// src/main.rs (excerpt)
fn run() -> Result<()> {
    if cfg!(variant_family = "aws-k8s") && cfg!(variant_flavor = "nvidia") {
        migrate(AddPrefixesMigration(vec!["settings.some-prefix"]))
    } else {
        migrate(NoOpMigration)
    }
}
```
`emit_cfgs()` sets `variant`, `variant_platform`, `variant_runtime`, `variant_family`, `variant_version`, `variant_flavor`. Caveat: no active migration currently uses this, and the `bottlerocket-variant` crate now lives in the Twoliter repo (`tools/bottlerocket-variant`) rather than in `sources/`; the archived crates' `path = "../../../../../bottlerocket-variant"` build-dependency no longer resolves. Prefer a variant-agnostic migration (e.g. `AddSettingsMigration` is harmless on variants that never had the key); if you truly need variant cfgs, agree the dependency source with maintainers first.

## Wiring it in

1. **Workspace:** add `"settings-migrations/v<X.Y.Z>/<name>"` to `members` in `sources/Cargo.toml`, after the line `# (all previous migrations archived; add new ones after this line)`.
2. **Release.toml:** add `"migrate_v<X.Y.Z>_<name>.lz4"` to the list for the `"(<prev>, <X.Y.Z>)"` key under `[migrations]`, creating the key if this is the first migration for the release. The top-level `version` in `Release.toml` (and `release-version` in `Twoliter.toml`) must be `<X.Y.Z>` for the release that ships it.
3. **Check:** `cargo build -p <name>` in `sources/`, then `cargo make check-migrations` at the repo root.

## Testing

### Unit tests (fast, preferred for custom logic)
Add `#[cfg(test)]` tests that build a `MigrationData` with `maplit::hashmap!`, call `forward`/`backward`, and assert the resulting maps. Include a sparse input (key absent) to prove the migration doesn't assume keys. Run `cargo test -p <name>` in `sources/`.

### Local run against a datastore
The filesystem datastore stores each key as a file under `live/` whose path is the dotted key split on `.` (e.g. `live/settings/my-service/new-setting`), containing a JSON-encoded value; metadata is a `<key>.<meta-name>` file beside it; pending transactions are under `pending/<tx>/`. Either copy `/var/lib/bottlerocket/datastore/current/` from a test node or create a few files by hand, then:
```bash
cd sources
cargo run -p <name> -- --source-datastore /tmp/ds/v1 --target-datastore /tmp/ds/fwd --forward
cargo run -p <name> -- --source-datastore /tmp/ds/fwd --target-datastore /tmp/ds/back --backward
find /tmp/ds/fwd /tmp/ds/back -type f | sort      # compare against the input
```

### Full upgrade/downgrade on EC2 (qualification)
Proves the real migrator path. Do it from a single checkout (not git worktrees): the TUF keys and roles generated on the first build must be reused for both images. TestSys also has a `migration` test (`cargo make -e TESTSYS_TEST=migration test`, see `document/bottlerocket/development`).

1. **Host a TUF repo.** Any HTTPS-reachable static host works, e.g. an S3 bucket behind CloudFront. New buckets can take a while before CloudFront serves them cleanly.
2. **Infra.toml.** Copy `tools/pubsys/Infra.toml.example` to `Infra.toml` (git-ignored). In `[repo.default]` comment out `root_role_url`, `root_role_sha512`, `signing_keys`, `metadata_base_url`, `targets_url` so pubsys generates local keys; under `[aws]` keep a single region and drop `profile`/`ssm_prefix`/`role` unless you need them.
3. **Old image:** `git checkout tags/v<OLD>`, then
   `cargo make -e BUILDSYS_VARIANT=<variant> -e BUILDSYS_ARCH=<arch>` and
   `cargo make -e BUILDSYS_VARIANT=<variant> -e BUILDSYS_ARCH=<arch> -e PUBLISH_REGIONS=<region> ami` — record the AMI ID.
4. **New repo:** check out your branch, bump `Release.toml` `version` and `Twoliter.toml` `release-version` to `<NEW>`, build, then `cargo make clean-repos` and `cargo make -e BUILDSYS_VARIANT=<variant> -e BUILDSYS_ARCH=<arch> repo`. Sync `build/repos/default/latest/` to the host (e.g. `aws s3 sync build/repos/default/latest/ s3://<bucket>/migration-testing/`).
5. **Launch** the old AMI with user data:
   ```toml
   [settings.updates]
   metadata-base-url = "https://<host>/migration-testing/<variant>/<arch>"
   targets-base-url = "https://<host>/migration-testing/targets/"
   ignore-waves = true

   [settings.host-containers.admin]
   enabled = true
   ```
6. **Upgrade:** in the admin container, `sudo sheltie`, then `updog check-update -a --json` and `updog update -i <NEW> -r -n` (reboots). Verify with `apiclient get settings` and `ls /var/lib/bottlerocket/datastore/current/live/`.
7. **Downgrade:** `signpost rollback-to-inactive && reboot`, then verify `apiclient get settings` again — the new keys must be gone and the old version's API must start cleanly.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Metadata error: root metadata is expired` | The locally generated TUF root expired: remove the generated `keys/*` and `roles/*` and rebuild so pubsys creates new ones. |
| `Signature threshold of 1 not met for role root` | Keys changed between builds: `cargo make clean`, then rebuild the new repo (step 4). |
| Migration fails with a missing key | It assumed a key exists; use `if let Some(..)` / `.get()`. Remember pending transactions. |
| Old version's API rejects data after downgrade | The `backward` path didn't remove a new key or restore an old value. |

## Principles

1. Never assume keys exist; never add keys unconditionally.
2. Always implement both directions.
3. Be idempotent: input may already be in the target shape.
4. Prefer a common helper over custom code.
5. Version directory == `Release.toml` version that first ships the change.
