# dagnode-release

One-step bootstrap for the [DagNode RPM repository](https://rpm.dagnode.com/) — installs the
`.repo` definition and the org signing key so `dnf install <package>` just works.

## Install

**Recommended — the bootstrap package.** It drops the `.repo` definition and the signing key in
one step, trusts the key from a local file, and carries key rotations forward as an ordinary
`dnf upgrade`:

```bash
sudo dnf install https://rpm.dagnode.com/dagnode-release-latest.noarch.rpm
sudo dnf install <package>
```

The first command installs `dagnode-release`, which drops
`/etc/yum.repos.d/dagnode.repo` and the signing key at
`/etc/pki/rpm-gpg/RPM-GPG-KEY-dag-node`. The `.repo` sets `gpgcheck=1` and
`repo_gpgcheck=1` with `gpgkey=file://` pointing at that key, so every subsequent install
verifies package and repository-metadata signatures against a locally trusted key — no manual
`rpm --import`, no hand-written `.repo`. One definition covers every Enterprise Linux major and
arch through `$releasever` and `$basearch`.

The bootstrap RPM is fetched over HTTPS; verify the org key's primary fingerprint out-of-band
before trusting the repository — see [Signing key](https://github.com/dag-node/rpm/blob/main/README.md#signing-key). The
fingerprint is stable across signing-subkey rotation, and each `dnf upgrade` of `dagnode-release`
ships the current key file, so a rotated subkey propagates as an ordinary update.

To configure the repository by hand instead — no bootstrap package, with the key trusted over
HTTPS — follow the manual `.repo` steps in the [repository README](https://github.com/dag-node/rpm/blob/main/README.md#configure-the-repository-manually).

## What it installs

| Path | Contents |
|---|---|
| `/etc/yum.repos.d/dagnode.repo` | the `[dagnode]` repository definition (`%config(noreplace)`) |
| `/etc/pki/rpm-gpg/RPM-GPG-KEY-dag-node` | the DagNode public signing key the `.repo` trusts |

The package is `noarch` and carries no code. The shipped key is exported from the org signing
secret at build time, never committed — the copy in the package cannot drift from the key that
signs the packages it verifies.

## How it is built and served

`dag-node/rpm-dagnode-release` builds and **signs** its own RPM, publishes it as a GitHub Release,
and notifies the central [`dag-node/rpm`](https://rpm.dagnode.com/) pipeline, which verifies and
serves it at `rpm.dagnode.com` — the same signed, single-writer path every DagNode project uses.
The channel follows the tag: `vX.Y.Z` publishes stable, `vX.Y.Z-rc.N` a GitHub prerelease.

Release process and org setup: `github-org-dag-node/org/` (`DAGNODE-RELEASE-HINTS.md`,
`RPM-REPO-HINTS.md`, `GPG-HINTS.md`).
