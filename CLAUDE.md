# dag-node/rpm-dagnode-release

The bootstrap package for the DagNode RPM repository: a `noarch`, code-free RPM that ships the
`[dagnode]` `.repo` definition and the org public signing key, so a new host installs the
repository and its trust root in one `dnf install dagnode-release`. It is a normal DagNode
publishing project — it signs its own RPM and notifies `dag-node/rpm`, which serves
`rpm.dagnode.com`; this repo grows no path into that served tree of its own. The release-process
contract (tag grammar, channels, who signs) and the org setup live in
`github-org-dag-node/org/` — `DAGNODE-RELEASE-HINTS.md`, `RPM-REPO-HINTS.md`, `GPG-HINTS.md`.

## Invariants

- **The shipped key is exported from the signing secret at build time, never committed.** The
  package payload `packaging/RPM-GPG-KEY-dag-node` is `.gitignore`d and produced by CI from
  `GPG_SIGNING_KEY`, so the key the package ships is by construction the key that signs the
  packages it verifies (`github-org-dag-node/org/GPG-HINTS.md` S3). A committed copy could only
  drift.
- **The version lives in `packaging/VERSION`.** `dagnode-release.spec` and the Makefile read that
  one file; `check-version.sh` fails the release unless the tag, `VERSION`, and the newest
  `%changelog` entry all agree.
- **The channel follows the tag, never the branch.** `vX.Y.Z` publishes stable (GitHub Release +
  `rpm.dagnode.com`); `vX.Y.Z-rc.N` a GitHub prerelease; no tag publishes nothing. Built once per
  EL major only so the dist tag routes it into each served `el/N` tree.
- **Signing is mandatory and fail-closed.** A release builds and signs inside the matching-EL
  `rockylinux:elN` container, proves the whole sign+verify chain on a throwaway RPM first
  (`sign-rpms.sh --selftest`), then re-verifies every signed RPM on the runner against the
  exported key. A missing secret, a silent `rpmsign` no-op, or a signature that does not validate
  fails the job before anything publishes.
- **Secrets never touch disk or argv.** `GPG_SIGNING_KEY`/`GPG_SIGNING_PASSPHRASE` reach the
  container over stdin (`sign-rpms.sh --secrets-stdin`), never `-e`; the imported keyring lives in
  a tmpfs `GNUPGHOME` wiped on exit.

## Working conventions

- **PRs are required on `main`; the PR comes from `develop`.** `develop` is the integration
  branch: small fixes commit there directly, larger work branches as
  `feature/RPM-<yyMMdd>-<name>` and merges back to `develop` first. The operator merges and pushes
  and cuts tags — agents do neither.
- Commit messages follow Conventional Commits (`type(scope): summary`).
- **Actions are pinned to full-length commit SHAs**; the pins match the org's other projects.
- The `.repo` payload trusts the key via `gpgkey=file://`, so a rotated signing subkey reaches a
  host as an ordinary `dnf upgrade` of this package; the org key's primary fingerprint is stable
  across rotation (`GPG-HINTS.md` S6).
