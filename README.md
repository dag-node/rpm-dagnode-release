# dagnode-release

One-step bootstrap for the [DagNode RPM repository](https://rpm.dagnode.com/). Installs the
`.repo` definition and the org signing key so `dnf install <package>` just works.

## Install

```bash
# EL 9, EL 10
sudo dnf install https://rpm.dagnode.com/dagnode-release-latest.noarch.rpm
# Fedora
sudo dnf install https://rpm.dagnode.com/fedora/dagnode-release-latest.noarch.rpm
# then any package
sudo dnf install <package>
```

The first line installs `dagnode-release`, which places:

- `/etc/yum.repos.d/dagnode.repo` — the repository definition, `gpgcheck=1` and
  `repo_gpgcheck=1`
- `/etc/pki/rpm-gpg/RPM-GPG-KEY-dag-node` — the signing key the definition trusts through
  `gpgkey=file://`

No `rpm --import` and no hand-written `.repo`. A signing-key rotation ships as an ordinary
`dnf upgrade` of this package. The package is built per family, EL and Fedora, and within a
family one definition covers every release and architecture through `$releasever` and
`$basearch`.

> **Security note.** The bootstrap RPM is fetched over HTTPS. Verify the org key's primary
> fingerprint out-of-band before trusting the repository — see
> [Signing key](https://github.com/dag-node/rpm/blob/main/README.md#signing-key). The fingerprint
> is stable across subkey rotations.

To configure the repository by hand instead, follow the manual `.repo` steps in the
[repository README](https://github.com/dag-node/rpm/blob/main/README.md#configure-the-repository-manually).

## What it installs

| Path | Contents |
|---|---|
| `/etc/yum.repos.d/dagnode.repo` | the `[dagnode]` repository definition for the host's family (`%config(noreplace)`) |
| `/etc/pki/rpm-gpg/RPM-GPG-KEY-dag-node` | the DagNode public signing key |

The package is `noarch` and carries no code. The key is exported from the org signing secret at
build time, never committed, so it cannot drift from the key that signs the packages.

## How it is built and served

`dag-node/rpm-dagnode-release` builds and signs its own RPM, publishes it as a GitHub Release, and
notifies the central `dag-node/rpm` pipeline, which verifies and serves it at `rpm.dagnode.com` —
the same signed, single-writer path every DagNode project uses.

- `vX.Y.Z` → stable
- `vX.Y.Z-rc.N` → GitHub prerelease

## Releasing

A maintainer signs and pushes a tag; the tag does the rest:

```bash
git tag -s v1.2.0 -m "v1.2.0" && git push origin v1.2.0
```

The release job runs inside the `release` environment, which admits a `v*.*.*` tag alone and
holds the three secrets the job reads: the signing-subkey export, its passphrase, and the token
that dispatches `dag-node/rpm`. A branch or pull-request run cannot reference the environment,
so it signs nothing. `main` takes changes by pull request with the `build-test` check green; a
maintainer merging their own change uses the admin bypass the merge button offers.
