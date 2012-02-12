::

      ____ ____      _    __  __ __  __ ___ _____
     / ___|  _ \    / \  |  \/  |  \/  |_ _|_   _|
    | |   | |_) |  / _ \ | |\/| | |\/| || |  | |
    | |___|  _ <  / ___ \| |  | | |  | || |  | |
     \____|_| \_\/_/   \_\_|  |_|_|  |_|___| |_|


What the heck is this?
======================

**Crammit** is a small tool that provides both CSS and JavaScript
concatenation, compression and some other asset management related
goodies. If you've heard of Jammit for Rails then you can think of it
as my attempt to provide a similar simple version in Python.

Installation
------------

::

    $ [sudo] pip install crammit

If you're adventurous you can install a bleeding edge version from
the git master branch:

::

    $ [sudo] pip install git+https://github.com/rspivak/crammit.git#egg=crammit

To install in development mode

::

    $ git clone https://github.com/rspivak/crammit.git
    $ python setup.py develop

Put it through its paces
------------------------
::

    $ crammit -c assets.yaml

See below about configuration file format and parameters

Configuration
-------------

Use YAML file to configure Crammit.
Here is a sample configuration file.

::

    output: assets       # directory path relative to the current directory
    fingerprint: true    # add sha1 hash to the output file name

    javascript:
      # 'common' is a bundle name, output file will have prefix 'common'
      common:
        - static/js/application.js
        - static/js/vendor/*.js
      utils:
        # paths are relative to the current directory
        - static/js/utils.js

    css:
      base:
        # you can use Unix shell-style wildcards in file names
        - static/css/*.css


- **output** - specifies relative path of an output directory where allgenerated files will be put.
- **fingerprint** - either true or false. If true then SHA1 hash will be added to output bundle file names. The hash is calculated on concatenated original files before minification and gzip compressionis applied.

Every bundle will output 3 files. Let's check out the output of
the javascript *common* bundle.

- common-{sha1}.js - concatenated original files
- common-{sha1}.min.js - concatenated and minified files
- common-{sha1}.min.js.gz - concatenated, minified, and gzipped files

Information file
----------------
Crammit produces a bundle information file in {output}/assetsinfo.yaml
that contains different details about all generated bundles.
The information includes SHA1 fingerprint (if enabled) for a bundle,
output file names and their corresponding sizes in bytes.

- *raw* - concatenated
- *min* - concatenated and minified
- *gz* - concatenated, minified, and gzipped

::

    css:
      base:
        fingerprint: 71fe4cba05a1a51023c6af4c4abf9c47ab21e357
        output:
          gz: base-71fe4cba05a1a51023c6af4c4abf9c47ab21e357.min.css.gz
          min: base-71fe4cba05a1a51023c6af4c4abf9c47ab21e357.min.css
          raw: base-71fe4cba05a1a51023c6af4c4abf9c47ab21e357.css
        size:
          gz: 108
          min: 235
          raw: 277
    javascript:
      common:
        fingerprint: 6493b619c73c49ce1f4dfe2c31d41902e98acaee
        output:
          gz: common-6493b619c73c49ce1f4dfe2c31d41902e98acaee.min.js.gz
          min: common-6493b619c73c49ce1f4dfe2c31d41902e98acaee.min.js
          raw: common-6493b619c73c49ce1f4dfe2c31d41902e98acaee.js
        size:
          gz: 56
          min: 41
          raw: 50
      utils:
        fingerprint: c3ef63280b954d99e8b13fc11ea3031caee77f1a
        output:
          gz: utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.min.js.gz
          min: utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.min.js
          raw: utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.js
        size:
          gz: 42
          min: 22
          raw: 24

Acknowledgments
---------------
- CSS minification - `cssmin <https://github.com/zacharyvoase/cssmin>`_
- Stole nice idea of bundle information file - `Squeezeit <https://github.com/samarudge/Squeezeit>`_
- JavaScript minifier - `SlimIt <https://github.com/rspivak/slimit>`_

License
-------
The MIT License (MIT)