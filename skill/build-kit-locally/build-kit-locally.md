---
type: Skill
description: Build a Bottlerocket kit (core-kit or kernel-kit), publish it to a local OCI registry, and build a variant image from it — use when testing kit package changes end-to-end in a variant without cloud credentials or publishing to a shared registry.
---

# Build a kit locally and consume it from a variant

Background, file formats and troubleshooting: `document/bottlerocket/local-kit-workflow`. Repo specifics: `document/core-kit/development`, `document/kernel-kit/development`, `document/bottlerocket/development`. Assumes sibling checkouts of the kit repo and `bottlerocket`. Use the repos' `make` / `cargo make` targets; do not call `twoliter` directly except `./tools/twoliter/twoliter update` in `bottlerocket`.

## 1. Start (or reuse) a local registry

```bash
docker ps --filter name=kit-registry --format '{{.Names}}' | grep -q kit-registry \
  || docker run -d --name kit-registry -p 5000:5000 -v kit-registry-data:/var/lib/registry registry:2
curl -sf localhost:5000/v2/_catalog
```
If port 5000 is taken, pick another and use it everywhere below. The registry binds only for local use; do not publish it beyond the host.

## 2. Build and publish the kit

In the kit repo, create a git-ignored `Infra.toml` if absent:
```toml
[vendor.local]
registry = "localhost:5000"
```
```bash
make build                          # add ARCH=x86_64|aarch64; UPSTREAM_SOURCE_FALLBACK=true for restricted sources
make publish VENDOR=local
curl -s localhost:5000/v2/_catalog  # kit repository must appear
```
Note the kit version: `release-version` in the kit's `Twoliter.toml`.

## 3. Point the variant at the local kit

In `bottlerocket`:
1. Set that kit's `version` in `Twoliter.toml` to the published version.
2. Create a git-ignored `Twoliter.override` redirecting only that kit:
   ```toml
   [bottlerocket.bottlerocket-core-kit]   # <vendor in Twoliter.toml>.<kit name>
   registry = "localhost:5000"
   ```
3. `./tools/twoliter/twoliter update`

## 4. Build the variant

```bash
cargo make -e BUILDSYS_VARIANT=<variant> -e BUILDSYS_ARCH=<arch>
ls -lh build/images/
```
Success = the build finishes and an image appears under `build/images/<arch>-<variant>/`.

To iterate: edit kit packages, repeat step 2 (only changed packages rebuild), rerun `twoliter update`, rebuild the variant.

## 5. Clean up

- `bottlerocket`: `rm Twoliter.override`; revert `Twoliter.toml` and `Twoliter.lock`.
- Kit repo: `rm Infra.toml` if you created it.
- `docker rm -f kit-registry` (plus `docker volume rm kit-registry-data` to discard published kits).

Never commit `Infra.toml`, `Twoliter.override`, or a lock resolved against the local registry.

## On failure

Match the symptom against the troubleshooting table in `document/bottlerocket/local-kit-workflow` (registry not running, `vendor 'local' not found`, kit not found / version mismatch, stale lock, stale cache, docker permissions).
