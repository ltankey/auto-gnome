"""
The testing strategy for the IP validator is:
 * create mock of methog that fetches hook_blocks from GitHub (return own hook blocks)
 * positive test: ip strings from GOOD_MOCK_ADDRESSES should return True
 * netagive test: ip strings from BAD_MOCK_ADDRESSES shoulr return False
 * also test the 127.0.0.1 address
"""
import unittest
import json
from mocks import mock_get

# hackery
import sys
import os.path
sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir)))

# patchery
import gh
gh.requests.get = mock_get


# actual test code...
BAD_MOCK_ADDRESSES = ('193.21.243.7', '185.198.107.43')
GOOD_MOCK_ADDRESSES = (
    '192.30.252.1', '192.30.252.254','192.30.252.13',
    '185.199.108.1', '185.199.108.254', '185.199.108.78')

class IPValidationTestCase(unittest.TestCase):
    def test_localhost_is_valid(self):
        val = gh.EventSourceValidator()
        validity = val.ip_str_is_valid('127.0.0.1')
        self.assertTrue(validity)

    def test_good_addresses_are_valid(self):
        val = gh.EventSourceValidator()
        for addr in GOOD_MOCK_ADDRESSES:
            validity = val.ip_str_is_valid(addr)
            self.assertTrue(validity)

    def test_bad_addresses_are_invalid(self):
        val = gh.EventSourceValidator()
        for addr in BAD_MOCK_ADDRESSES:
            validity = val.ip_str_is_valid(addr)
            self.assertFalse(validity)


if __name__ == '__main__':
    unittest.main()
