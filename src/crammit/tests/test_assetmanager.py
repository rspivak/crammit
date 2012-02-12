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
import unittest


class AssetManagerTestCase(unittest.TestCase):

    def _getTargetClass(self):
        from crammit import AssetManager
        return AssetManager

    def _makeOne(self, config, basedir=None):
        return self._getTargetClass()(config, basedir)

    def test_js_bundles(self):
        import yaml
        config = yaml.load("""
        javascript:
          common:
            - static/js/vendor/*.js
            - static/js/application.js
          utils:
            - static/js/utils.js
        """)
        basedir = os.path.dirname(os.path.abspath(__file__))
        manager = self._makeOne(config, basedir)
        bundles = manager.get_bundles()['javascript']
        # Verify that we have 2 javascript bundles
        self.assertEquals(len(bundles), 2)
        self.assertTrue('common' in bundles)
        self.assertTrue('utils' in bundles)

        common_files = bundles['common']
        self.assertEqual(
            sorted([
                os.path.join(basedir, 'static/js/vendor/vendor1.js'),
                os.path.join(basedir, 'static/js/vendor/vendor2.js'),
                os.path.join(basedir, 'static/js/application.js'),
                ]),
            sorted(common_files)
            )

        util_files = bundles['utils']
        self.assertEqual(
            [os.path.join(basedir, 'static/js/utils.js')],
            util_files
            )

    def test_css_bundles(self):
        import yaml
        config = yaml.load("""
        css:
          common:
            - static/css/*.css
        """)
        basedir = os.path.dirname(os.path.abspath(__file__))
        manager = self._makeOne(config, basedir)
        bundles = manager.get_bundles()['css']
        # Verify that we have 1 CSS bundle
        self.assertEquals(len(bundles), 1)
        self.assertTrue('common' in bundles)

        common_files = bundles['common']
        self.assertEqual(
            sorted([
                os.path.join(basedir, 'static/css/test1.css'),
                os.path.join(basedir, 'static/css/test2.css'),
                ]),
            sorted(common_files)
            )
