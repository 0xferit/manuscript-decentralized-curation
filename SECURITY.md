# Security Policy

This repository publishes an academic manuscript and supporting simulations as a
static website on Cloudflare Pages. It has no backend, no user accounts, and no
user data. The primary security concerns are supply-chain integrity of the CI
pipeline and scope of the deployment credential.

## Reporting a vulnerability

For issues in this repository (build pipeline, leaked credentials, published
content integrity), open a GitHub issue at
`https://github.com/0xferit/manuscript-decentralized-curation/issues`. For
vulnerabilities that should not be disclosed publicly until triaged, email
`ferit@octantlabs.io` with `[security]` in the subject line.

Do not use this channel for vulnerabilities in third-party systems referenced
by the manuscript (e.g., Kleros, Ethereum); report those upstream.

## Deployment credential scope

The workflow `.github/workflows/publish-cloudflare-pages.yml` authenticates to
Cloudflare using one GitHub Actions secret and one public identifier:

- `CLOUDFLARE_API_TOKEN` (secret): Cloudflare API token used by
  `cloudflare/wrangler-action@v3` to run `pages deploy` against the
  `manuscript-decentralized-curation` Pages project.
- Cloudflare account ID (hardcoded in the workflow): not a secret. Account IDs
  are opaque identifiers that appear in dashboard URLs and are useless without
  a token scoped to the account.

### Expected `CLOUDFLARE_API_TOKEN` scope

The token stored in the `CLOUDFLARE_API_TOKEN` secret should be created from
the Cloudflare dashboard with the narrowest scope that lets the workflow run:

- Permission: `Account` > `Cloudflare Pages` > `Edit`.
- Account resources: `Include` > the single account that owns this Pages
  project. Do not grant `All accounts`.
- Zone resources: `All zones from an account` is not required for Pages
  deployment and should not be granted.
- Client IP filtering and TTL: optional; a finite TTL with a calendar reminder
  to rotate is preferred over an indefinite token.

The secret name (`CLOUDFLARE_API_TOKEN`) does not encode this scope. Renaming
the secret would require rotating the token in Cloudflare and updating the
secret value in this repository's settings simultaneously; that is tracked
separately and is not a prerequisite for this policy. Until a rename happens,
treat this document as the source of truth for the expected scope.

### Blast radius if the token leaks

A token scoped as above can: create, update, and delete Pages projects,
deployments, and custom domains within the single Cloudflare account. It
cannot: read or modify DNS records outside Pages, access R2 buckets, Workers
KV, D1, Workers scripts, or billing. The practical attack is defacement of the
published site or deletion of the Pages project, both of which are recoverable
from the repository by re-running the workflow.

A token scoped more broadly (for example `Account` > `Cloudflare Pages` >
`Edit` plus unrelated permissions, or applied to `All accounts`) expands the
blast radius proportionally. If the token in use today was created with
broader scope, re-create it at the narrow scope above, update the
`CLOUDFLARE_API_TOKEN` secret, and revoke the old token.

### Rotation

Rotate the token:

- On any suspected exposure (force-pushed commits containing the secret,
  compromised contributor machine, leaked CI logs).
- On contributor offboarding if the offboarded contributor had repository
  admin access.
- At the TTL set on the token, if any.

Rotation procedure: create a new token with the scope above, update the
`CLOUDFLARE_API_TOKEN` GitHub Actions secret, run the workflow once against a
non-`main` ref to confirm deployment, then revoke the old token from the
Cloudflare dashboard.

## Supply chain

The publish workflow pins third-party actions and toolchains to reduce
exposure to upstream compromise:

- Quarto is pinned to a specific version via
  `quarto-dev/quarto-actions/setup@v2` with an explicit `version` input. The
  previous install flow resolved Quarto's `latest` tag at build time and ran
  `dpkg -i` on an unverified `.deb`; it was replaced in PR
  [#94](https://github.com/0xferit/manuscript-decentralized-curation/pull/94).
- Other actions (`actions/checkout`, `actions/setup-python`, `actions/cache`,
  `cloudflare/wrangler-action`) are pinned to major tags. SHA-pinning is out
  of scope for a static-site workflow with this blast radius.
- Python dependencies are installed from `requirements.txt`. Simulation
  outputs are cached by the hash of `analysis/run_all.py`.

Bumping any of the pinned versions is a deliberate maintainer action, not a
silent acceptance of whatever ships as `latest`.

## Out of scope

- Vulnerabilities in the rendered manuscript's intellectual content
  (disagreements with a claim or citation): open a regular GitHub issue.
- Cloudflare Pages platform vulnerabilities: report to Cloudflare directly.
- Typos and broken links: open a regular GitHub issue or a pull request.
