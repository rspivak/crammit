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

from mock import Mock


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

    def test_bundles_info(self):
        import yaml
        config = yaml.load("""
        output: assets
        fingerprint: true
        javascript:
          common:
            - static/js/vendor/*.js
            - static/js/application.js
          utils:
            - static/js/utils.js
        css:
          common:
            - static/css/*.css
        """)
        basedir = os.path.dirname(os.path.abspath(__file__))
        manager = self._makeOne(config, basedir)
        manager.write = Mock()
        manager.write.return_value = None
        expected = {
            'css': {
                'common': {
                    'fingerprint': '30bb64bb4cb1b9620066398df4852f6a2ceec8c5',
                    'output': {
                        'gz': 'common-30bb64bb4cb1b9620066398df4852f6a2ceec8c5.min.css.gz',
                        'min': 'common-30bb64bb4cb1b9620066398df4852f6a2ceec8c5.min.css',
                        'raw': 'common-30bb64bb4cb1b9620066398df4852f6a2ceec8c5.css'
                        },
                    'size': {
                        'gz': 106,
                        'min': 235,
                        'raw': 277
                        }
                    }
                },
            'javascript': {
                'common': {
                    'fingerprint': '551e83e1705c9b1441413c23391dfebad541ee85',
                    'output': {
                        'gz': 'common-551e83e1705c9b1441413c23391dfebad541ee85.min.js.gz',
                        'min': 'common-551e83e1705c9b1441413c23391dfebad541ee85.min.js',
                        'raw': 'common-551e83e1705c9b1441413c23391dfebad541ee85.js'
                        },
                    'size': {
                        'gz': 56,
                        'min': 41,
                        'raw': 50
                        }
                    },
                'utils': {
                    'fingerprint': 'c3ef63280b954d99e8b13fc11ea3031caee77f1a',
                    'output': {
                        'gz': 'utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.min.js.gz',
                        'min': 'utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.min.js',
                        'raw': 'utils-c3ef63280b954d99e8b13fc11ea3031caee77f1a.js'
                        },
                    'size': {
                        'gz': 42,
                        'min': 22,
                        'raw': 24
                        }
                    }
                }
            }
        bundles_info = manager.process_bundles()
        self.assertEqual(expected, bundles_info)

