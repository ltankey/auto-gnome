"""
The testing strategy for the IP validator is:
 * create mock of methog that fetches hook_blocks from GitHub (return own hook blocks)
 * positive test: ip strings from GOOD_MOCK_ADDRESSES should return True
 * netagive test: ip strings from BAD_MOCK_ADDRESSES shoulr return False
 * also test the 127.0.0.1 address
"""
import unittest
import json

# hackery
import sys
import os.path
sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir)))

import util

# patchery
class MockResponse:
    """
    Mock response object that always returns the same canned json
    """
    def json(self):
        return json.loads('''{
  "verifiable_password_authentication": true,
  "github_services_sha": "c8675558dc838e7a771f482c0636f607e1d9d920",
  "hooks": [
    "192.30.252.0/22",
    "185.199.108.0/22"
  ],
  "git": [
    "192.30.252.0/22",
    "185.199.108.0/22"
  ],
  "pages": [
    "192.30.252.153/32",
    "192.30.252.154/32"
  ],
  "importer": [
    "54.87.5.173",
    "54.166.52.62",
    "23.20.92.3"
  ]
}''')

def mock_get(x):
    """
    Mock get method that ignores it's parameter and returns
    the same mock response regardless.
    """
    return MockResponse()

util.requests.get = mock_get

#
# now the actual test code...
#
BAD_MOCK_ADDRESSES = ('193.21.243.7', '185.198.107.43')
GOOD_MOCK_ADDRESSES = (
    '192.30.252.1', '192.30.252.254','192.30.252.13',
    '185.199.108.1', '185.199.108.254', '185.199.108.78')


class IPValidationTestCase(unittest.TestCase):
    def test_localhost_is_valid(self):
        validity = util.gh_event_source_is_valid('127.0.0.1')
        self.assertTrue(validity)

    def test_good_addresses_are_valid(self):
        for addr in GOOD_MOCK_ADDRESSES:
            validity = util.gh_event_source_is_valid(addr)
            self.assertTrue(validity)

    def test_bad_addresses_are_invalid(self):
        for addr in BAD_MOCK_ADDRESSES:
            validity = util.gh_event_source_is_valid(addr)
            self.assertFalse(validity)


if __name__ == '__main__':
    unittest.main()
