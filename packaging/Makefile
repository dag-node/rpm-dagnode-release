# Build the dagnode-release RPM/SRPM. Single-sources the rpmbuild invocation so a local build
# and CI use the identical command. The payload key packaging/RPM-GPG-KEY-dag-node must exist
# before `make rpm` -- CI exports it from the signing secret; for a local test build, export the
# org public key there yourself (it is never committed; see .gitignore).
#
#   make rpm  DIST=.el9   RPM_RELEASE=0.rc1     # build a specific EL major / pre-release
#   make srpm                                   # source RPM
#   make clean

PKG        := dagnode-release
TOPDIR     := $(CURDIR)/rpmbuild
DIST       ?=
RPM_RELEASE ?=

RPMBUILD_ARGS := --define "_topdir $(TOPDIR)" --define "_sourcedir $(CURDIR)" \
	$(if $(DIST),--define "dist $(DIST)") \
	$(if $(RPM_RELEASE),--define "rpm_release $(RPM_RELEASE)")

.PHONY: rpm srpm clean

rpm:
	rpmbuild -bb $(RPMBUILD_ARGS) $(PKG).spec

srpm:
	rpmbuild -bs $(RPMBUILD_ARGS) $(PKG).spec

clean:
	rm -rf $(TOPDIR)
