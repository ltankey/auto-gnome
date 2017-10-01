"""
The testing strategy for the IP validator is:
 * create mock of methog that fetches hook_blocks from GitHub (return own hook blocks)
 * positive test: ip strings from GOOD_MOCK_ADDRESSES should return True
 * netagive test: ip strings from BAD_MOCK_ADDRESSES shoulr return False
 * also test the 127.0.0.1 address
"""
import unittest
import json
from mocks import mock_get, MockCallback
# hackery
import sys
import os.path
sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir)))
# patchery
import util
util.requests.get = mock_get

class ConfigGetYamlTestCase(unittest.TestCase):
    def test_config_no_exceptions_getting_yaml(self):
        try:
            ce = MockCallback()
            cfg = util.Config(ce)
            init_raised = False
            try:
                yml = cfg.get_yaml()
                yml_raised = False
            except:
                yml_raised =True
        except:
            init_raised = True
        self.assertFalse(init_raised, "Config.__init__ raised an exception")
        self.assertFalse(yml_raised, "Config.get_yml raised an exception")

# TODO: figure out what is the right thing to do if get_yaml encounters non 200 responses
# FIXME: ensure we do the right thing if yet_yaml encounters non 200 response

# TODO: figure out if we want to iterate over config file names in precedence order?
# FIXME: test precedence-ordered iteration over config file names
# FIXME: ensure we do the right thing if payload not valid

class ConfigGetActivitiesTestCase(unittest.TestCase):
    # raise error if attempting to get_activities when config yaml is not valid
    # TODO figure out what to do with bad news
    # expect a list of instances to be returned, and
    # those instances are of classes that inherit Policy
    # and those instances have dispatch_gnome method
    pass


GOOD_SAMPLE_YAML = ('''policies:
 - VerboseCallbackLogging
 - NonExistantPolicy
 - SortingHat''', '''policies:
 - SortingHat''')
BAD_SAMPLE_YAML = ('''police_cars:
 - VerboseCallbackLogging
 - NonExistantPolicy
 - SortingHat''',)
# should this be considered invalid yaml?
# '''policies: SortingHat'''
# (single value, expecting list?)

class ConfigYAMLIsValidTestCase(unittest.TestCase):
    def test_true_if_valid_input(self):
        ce = MockCallback()
        cfg = util.Config(ce)
        for yml in GOOD_SAMPLE_YAML:
            def mock_get_yaml():
                return yml
            cfg.get_yaml = mock_get_yaml
            self.assertTrue(
                cfg.yaml_is_valid(),
                "found the following yaml invalid\n{}".format(yml))
            
    def test_false_if_invalid_input(self):
        ce = MockCallback()
        cfg = util.Config(ce)
        for yml in BAD_SAMPLE_YAML:
            def mock_get_yaml():
                return yml
            cfg.get_yaml = mock_get_yaml
            self.assertFalse(
                cfg.yaml_is_valid(),
                "found the following yaml valid\n{}".format(yml))


if __name__ == '__main__':
    unittest.main()
