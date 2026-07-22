# dagnode-release -- the bootstrap package for the DagNode DNF repository.
#
# Payload is two config files, no code: the [dagnode] .repo definition and the org public
# signing key it trusts. Installing it makes `dnf install <package>` from rpm.dagnode.com
# resolve and verify against a locally trusted key, so a new host needs no manual .repo or
# `rpm --import` step. The package is noarch and identical across EL majors; it is built once
# per major only so the dist tag routes it into each served el/N tree (dag-node/rpm publish.yml
# keys on the .elN filename). The shipped key is NOT committed -- CI exports it from the signing
# secret at build time (github-org-dag-node/org/GPG-HINTS.md S3), so the copy in the package can
# never drift from the key that signs the packages it verifies.

Name:           dagnode-release
# Single source of the version: packaging/VERSION (the Makefile reads the same file), so a
# release bump touches one place. A bare spec parse without --define "_sourcedir packaging"
# yields an empty Version; the Makefile and CI pass it.
Version:        %(cat %{_sourcedir}/VERSION)
# Plain "1" for a final vX.Y.Z release; CI's RPM_RELEASE overrides it to an rc prerelease
# ("0.rcN") or a dev/rehearsal snapshot. The leading "0." on a pre-release Release is the Fedora
# convention: rpm's version comparison then ranks a real release (Release "1") above any snapshot
# that preceded it.
Release:        %{!?rpm_release:1}%{?rpm_release}%{?dist}
Summary:        DagNode DNF repository configuration and signing key

License:        AGPL-3.0-or-later
URL:            https://rpm.dagnode.com/
Source0:        dagnode.repo
Source1:        RPM-GPG-KEY-dag-node
Source2:        VERSION

BuildArch:      noarch

# Config files only: no ELF, so suppress the debuginfo subpackage and the binary build-root
# policy steps (ldconfig/strip) that do not apply to a code-free noarch package.
%global debug_package %{nil}
%global __brp_ldconfig %{nil}
%global __brp_strip %{nil}
%global __brp_strip_static_archive %{nil}
%global __brp_strip_comment_note %{nil}

%global _repofile   %{_sysconfdir}/yum.repos.d/dagnode.repo
%global _gpgkeyfile %{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-dag-node

%description
Configures the DagNode DNF/YUM repository (https://rpm.dagnode.com/) and installs the
organization's public signing key at %{_gpgkeyfile}. With this package installed,
`dnf install <package>` from the DagNode repository resolves without a hand-written .repo file
and verifies package and repository-metadata signatures (gpgcheck, repo_gpgcheck) against a
locally trusted key. One .repo serves every Enterprise Linux major and arch via $releasever
and $basearch.

%prep
# No sources are unpacked: the two payload files are placed verbatim by the install section.

%install
install -Dpm 0644 %{SOURCE0} %{buildroot}%{_repofile}
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_gpgkeyfile}

%files
# noreplace: a host that hand-edits the .repo (a mirror, a disabled state) keeps its version on
# upgrade; a changed shipped file lands as dagnode.repo.rpmnew for the admin to reconcile.
%config(noreplace) %{_repofile}
%{_gpgkeyfile}

%changelog
* Wed Jul 22 2026 DagNode Package Signing <tools@dagnode.com> - 1.0.0-1
- Initial release: [dagnode] repository definition and the org signing key, so a new host
  installs the repo and its trust root in one `dnf install dagnode-release`.
