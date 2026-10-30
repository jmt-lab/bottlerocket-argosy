---
type: Skill
description: Fast, cited answer to a specific factual question about Bottlerocket (configuration values and defaults, partition layout, systemd units, file paths, versions, dependencies) by searching this argosy and then the sibling repo checkouts, ending with a research-quality indicator. Use for "what is" / "where is" questions with a definitive answer; use deep-research for how-it-works explanations.
---

# Fact find

Fast, focused answers to specific factual questions about Bottlerocket, with citations.

Use when the question has a concrete, definitive answer ("what is", "where is"): configuration values and defaults, partition schemes and disk layouts, systemd units and targets, file paths, version numbers, dependencies. For architecture or design explanations, use `skill/deep-research`.

## Procedure

### 1. Search this argosy

Search this argosy (the `document/`, `skill/`, and `styleguide/` namespaces) with the key terms from the question. Good starting points are the per-repo `summary`, `architecture`, `glossary`, and `conventions` documents (e.g. `document/bottlerocket/architecture`, `document/kernel-kit/glossary`). Check the top 3-5 hits.

### 2. Read

Read the most relevant concepts or files to find the answer. Search hits often carry the matching passage; widen only as needed.

### 3. If the argosy is insufficient, search the sibling checkouts

Search the source in the sibling checkouts of the public repositories (`bottlerocket`, `bottlerocket-core-kit`, `bottlerocket-kernel-kit`, `twoliter`, `bottlerocket-sdk`). Always scope searches to a specific repository and subdirectory; unscoped searches over build outputs are slow.

```bash
rg "search_term" --type rust bottlerocket-core-kit/sources/
rg "search_term" bottlerocket-core-kit/packages/ bottlerocket/variants/
find bottlerocket-core-kit/sources -name "*relevant_name*"
```

Having to fall back to source indicates a documentation gap; note it in the quality indicator.

### 4. Answer with citations

Give a direct, concise answer (typically 2-4 sentences) with inline superscript citations and a Sources section:

```
Bottlerocket uses a dual partition scheme with sets A and B <sup>[1]</sup>. The default API socket is `/run/api.sock` <sup>[2]</sup>.

## Sources

<sup>[1]</sup> [`sources/updater/signpost/README.md`](https://github.com/bottlerocket-os/bottlerocket-core-kit/blob/develop/sources/updater/signpost/README.md)
- Partition set structure

<sup>[2]</sup> [`sources/api/README.md`](https://github.com/bottlerocket-os/bottlerocket-core-kit/blob/develop/sources/api/README.md)
- API socket configuration
```

Citation guidelines:
- `<sup>[1]</sup>`, `<sup>[2]</sup>`, ... inline with facts.
- Paths relative to the repository root, cited as argosy concept paths (e.g. `document/bottlerocket/architecture`) or GitHub URLs: `https://github.com/bottlerocket-os/<repo>/blob/develop/<path>`.
- A short bullet per source describing what it provided.

## Validation

A good answer directly answers the question, is concise, has inline citations and a numbered Sources section, and carries no unnecessary explanation.

## Research quality indicator

End with one of:

- **Answered from documentation** — found in this argosy, READMEs, or design docs.
- **Answered from source code** — had to read implementation files because documentation was insufficient.
- **Partial documentation** — needed both documentation and source code.
