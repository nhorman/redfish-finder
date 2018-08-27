GITSHASH := $(shell git log --format=%h HEAD^..HEAD)
GITHASH := $(shell git log --format=%H HEAD^..HEAD)
GITDATE := $(shell date -s `git log --format=%ad --date=short HEAD^..HEAD` +%Y%m%d)

all: rpm

rpm: srpm
	rpmbuild --define='githash ${GITHASH}' --define='gitdate ${GITDATE}' --define='_topdir ${PWD}' --rebuild ./SRPMS/redfish-finder-0-0.1.${GITDATE}git${GITSHASH}.src.rpm

srpm: tarball
	rpmbuild --define='githash ${GITHASH}' --define='gitdate ${GITDATE}' --define='_topdir ${PWD}' -ts ./SOURCES/redfish-finder-${GITSHASH}.tar.gz

tarball:
	mkdir -p ./SOURCES
	git archive --format=tar.gz --prefix=redfish-finder-${GITHASH}/ -o ./SOURCES/redfish-finder-${GITSHASH}.tar.gz ${GITHASH}

clean:
	rm -rf SOURCES BUILD BUILDROOT RPMS SRPMS SPECS
