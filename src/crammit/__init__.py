###############################################################################
#
# Copyright (c) 2012 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import os
import fnmatch
import hashlib
import sys
import optparse
import StringIO
import gzip
from collections import defaultdict

import yaml
import slimit
import cssmin

CONFIG_FILE = 'assets.yaml'
ASSETS_INFO_FILE = 'assetsinfo.yaml'

def _log(msg):
    sys.stderr.write('%s\n' % msg)

def load_config(path):
    return yaml.load(open(path))


class AssetManager(object):
    """I manage assets bundles."""
    def __init__(self, config, basedir=None):
        self.config = config
        self.basedir = basedir or os.getcwd()

    def _get_bundles_by_type(self, type):
        """Get a dictionary of bundles for requested type.

        Args:
            type: 'javascript' or 'css'
        """
        bundles = {}
        bundle_definitions = self.config.get(type)
        if bundle_definitions is None:
            return bundles
        # bundle name: common
        for bundle_name, paths in bundle_definitions.items():
            bundle_files = []
            # path: static/js/vendor/*.js
            for path in paths:
                # pattern: /tmp/static/js/vendor/*.js
                pattern = abspath = os.path.join(self.basedir, path)
                # assetdir: /tmp/static/js/vendor
                # assetdir contents:
                #  - /tmp/static/js/vendor/t1.js
                #  - /tmp/static/js/vendor/t2.js
                #  - /tmp/static/js/vendor/index.html
                assetdir = os.path.dirname(abspath)
                # expanded_fnames after filtering using the pattern:
                #  - /tmp/static/js/vendor/t1.js
                #  - /tmp/static/js/vendor/t2.js
                fnames = [os.path.join(assetdir, fname)
                          for fname in os.listdir(assetdir)]
                expanded_fnames = fnmatch.filter(fnames, pattern)
                bundle_files.extend(expanded_fnames)
            bundles[bundle_name] = bundle_files

        return bundles

    def _compress(self, data):
        compresslevel = 9 # max
        buffer = StringIO.StringIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb',
                           compresslevel=compresslevel) as fout:
            fout.write(data)
        return buffer.getvalue()

    def _process_bundle(self, name, paths, type):
        sha1, sep = '', ''
        raw_data = ''.join(open(path).read() for path in paths)
        if self.config['fingerprint']:
            sha1 = hashlib.sha1(raw_data).hexdigest()
            sep = '-'
        file_ext = {
            'javascript': '.js',
            'css': '.css',
            }.get(type)
        fname_template = '%s%s%s{suffix}%s{gz}' % (name, sep, sha1, file_ext)
        raw_fname = fname_template.format(suffix='', gz='')
        self.write(raw_fname, raw_data)

        if type == 'javascript':
            minified_data = slimit.minify(raw_data, mangle=True)
        elif type == 'css':
            minified_data = cssmin.cssmin(raw_data)
        minifed_fname = fname_template.format(suffix='.min', gz='')
        self.write(minifed_fname, minified_data)

        gzipped_data = self._compress(minified_data)
        gzipped_fname = fname_template.format(suffix='.min', gz='.gz')
        self.write(gzipped_fname, gzipped_data)

        bundle_info = {
            name: {
                'fingerprint': sha1,
                'output': {
                    'raw': raw_fname,
                    'min': minifed_fname,
                    'gz': gzipped_fname,
                    },
                'size': {
                    'raw': len(raw_data),
                    'min': len(minified_data),
                    'gz': len(gzipped_data),
                    },
                }
            }
        return bundle_info

    def write(self, fname, data):
        output = os.path.abspath(self.config['output'])
        if not os.path.exists(output):
            os.makedirs(output)
        path = os.path.join(output, fname)
        with open(path, 'w') as fout:
            fout.write(data)

    def write_info(self, bundles_info):
        self.write(ASSETS_INFO_FILE,
                   yaml.dump(dict(bundles_info), default_flow_style=False))

    def get_bundles(self):
        bundles = {
            'javascript': self._get_bundles_by_type('javascript'),
            'css': self._get_bundles_by_type('css'),
            }
        return bundles

    def process_bundles(self):
        info = defaultdict(dict)
        bundles = self.get_bundles()
        for bundle_type in bundles:
            for name, paths in bundles[bundle_type].items():
                bundle_info = self._process_bundle(name, paths, bundle_type)
                info[bundle_type].update(bundle_info)
        return info


def main():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config',
                      help='path to assets.yaml (default: ./assets.yaml)')
    parser.add_option('-b', '--basedir', dest='basedir',
                      help=('base directory to which all '
                            'assets paths are relative (default: ./)'))
    options, args = parser.parse_args()

    config_path = options.config
    if config_path is None:
        config_path = os.path.join(os.getcwd(), CONFIG_FILE)

    if not os.path.exists(config_path):
        _log('Could not find the asset configuration file "%s"' % config_path)
        sys.exit(1)

    config = load_config(config_path)
    manager = AssetManager(config, options.basedir)
    bundles_info = manager.process_bundles()
    manager.write_info(bundles_info)
