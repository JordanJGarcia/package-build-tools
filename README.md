# package-build-tools

This package sets up a machine for building debian packages with pbuilder/cowbuilder.

You can either install the included .deb directly, or build it yourself:

1) Install these packages
```bash
sudo apt-get install --yes pbuilder cowbuilder debmake debhelper gdebi
```

2) You must have a compatible pbuilderrc file, mine is [here](https://github.com/JordanJGarcia/configs/blob/master/pbuilder/pbuilderrc)

3) Ensure you have build dependencies installed
```bash
sudo gdebi debian/control
```

4) Create a chroot (this could take a while) - available dists are found in /usr/share/debootstrap/scripts/
```bash
sudo DIST=<dist> pbuilder create && sudo DIST=<dist> cowbuilder create
```

5) Build the package
```bash
DIST=<dist> debmake --tar --yes --invoke 'pdebuild --pbuilder cowbuilder'
```

It will be placed in $BUILDRESULT as defined in your pbuilderrc, and you can install it onto
your machine directly from there.
