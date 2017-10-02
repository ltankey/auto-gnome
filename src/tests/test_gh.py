"""
The testing strategy for the IP validator is:
 * create mock of methog that fetches hook_blocks from GitHub (return own hook blocks)
 * positive test: ip strings from GOOD_MOCK_ADDRESSES should return True
 * netagive test: ip strings from BAD_MOCK_ADDRESSES shoulr return False
 * also test the 127.0.0.1 address
"""
import unittest
import json
from unittest.mock import MagicMock
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


class RepoTestCase(unittest.TestCase):
    def test_init(self):
        cb = MockCallback()
        payload = cb.payload()
        # we require construction without exception
        try:
            repo = gh.Repo(payload['repository']['full_name'])
            was_error = False
        except:
            was_error = True
        self.assertFalse(was_error)


class RepoEnsureMilestoneExistsTestCase(unittest.TestCase):
    def test_does_nothig_if_it_exists(self):
        """
        Given the milestone exists
        When I call repo.ensure_milestone_exists
        Then no new milestone is created
        """
        repo = gh.repo_from_callback(MockCallback())
        # if the milestone exists
        repo.milestone_exists = MagicMock(return_value=True)
        # it should not try to create it
        repo.create_milestone = MagicMock()
        repo.ensure_milestone_exists('foo')
        repo.create_milestone.assert_not_called()

    def test_creates_milestone_if_not_exist(self):
        """
        Given the milestone does not exist
        When I call repo.ensure_milestone_exists
        Then a new milestone is created
        """
        repo = gh.repo_from_callback(MockCallback())
        # if the milestone does not exist
        repo.milestone_exists = MagicMock(return_value=False)
        # it should be created
        repo.create_milestone = MagicMock()
        repo.ensure_milestone_exists('foo')
        repo.create_milestone.assert_called()


class RepoEnsureMilestoneHasDueDateTestCase(unittest.TestCase):
    def test_set_date_if_none(self):
        """
        Given a milestone has no due date
        When I call repo.ensure_milestone_has_due_date
        Then the due date is updated as specified
        """
        DATE =  '2012-10-09T23:39:01Z'
        repo = gh.repo_from_callback(MockCallback())
        # if the milestone exists
        repo.milestone_exists = MagicMock(return_value=True)
        # and has no due date
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=None)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)
        # then ensure the date is set
        repo.ensure_milestone_has_due_date('foo', DATE)
        # was the date updated right?
        mm.set_due_date.assert_called_with(DATE)

    def test_do_nothing_if_date_OK(self):
        """
        Given a malestone already has a specified due date
        When I call repo.ensure_milestone_has_due_date
        Then the due date is not updated
        """
        DATE =  '2012-10-09T23:39:01Z'
        repo = gh.repo_from_callback(MockCallback())
        # if the milestone exists
        repo.milestone_exists = MagicMock(return_value=True)
        # and has no due date
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=DATE)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)
        # then ensure the date is set
        repo.ensure_milestone_has_due_date('foo', DATE)
        # was the date updated right?
        mm.set_due_date.assert_not_called()

    def test_update_if_wrong_date(self):
        """
        Given a milestone exists with a due date
        And the due date is not the specified due date
        When I call repo.ensure_milestone_has_due_date
        Then the due date is updated
        """
        DATE =  '2012-10-09T23:39:01Z'
        WRONG_DATE = '2030-10-09T23:39:01Z'
        repo = gh.repo_from_callback(MockCallback())
        # if the milestone exists
        repo.milestone_exists = MagicMock(return_value=True)
        # and has no due date
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=WRONG_DATE)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)
        # then ensure the date is set
        repo.ensure_milestone_has_due_date('foo', DATE)
        # was the date updated right?
        mm.set_due_date.assert_called_with(DATE)


class RepoMilestoneExistsTestCase(unittest.TestCase):
    def test_true_if_milestone_exists(self):
        """
        Given a milestone exists
        When I call repo.milestone_exists
        Then True is returned
        """
        # givem a milestone exists
        MILESTONE_NAME = "foo"
        repo = gh.repo_from_callback(MockCallback())
        class MockMilestoneWrapper:
            def __init__(self):
                self._milestone = MockMilestone()
        class MockMilestone:
            def __init__(self):
                self.title = MILESTONE_NAME
        repo._milestones = (MockMilestoneWrapper(),)
        # then milestone exists
        self.assertTrue(repo.milestone_exists(MILESTONE_NAME))


    def test_false_if_milestone_not_exists(self):
        """
        Given a milestone does not exist
        When I call repo.milestone_exists
        Then False is returned
        """
        # givem a milestone exists
        MILESTONE_NAME = "foo"
        OTHER_MILESTONE_NAME = "bar"
        repo = gh.repo_from_callback(MockCallback())
        class MockMilestoneWrapper:
            def __init__(self):
                self._milestone = MockMilestone()
        class MockMilestone:
            def __init__(self):
                # this is not the milestone you are looking for
                self.title = OTHER_MILESTONE_NAME
        repo._milestones = (MockMilestoneWrapper(),)
        # then the milestone does not exist
        self.assertFalse(repo.milestone_exists(MILESTONE_NAME))


class RepoGetMilestoneTestCase(unittest.TestCase):
    def test_returns_non_if_not_exists(self):
        pass  # FIXME
    def test_returns_milestone_if_exists(self):
        pass  # FIXME


class RepoCreateMilestoneTestCase(unittest.TestCase):
    def test_creates_if_not_exist(self):
        pass  # FIXME
    def test_error_if_already_exists(self):
        pass  # FIXME
    def test_date_none_if_none_provided(self):
        pass  # FIXME
    def test_date_matches_supplied(self):
        pass  # FIXME


if __name__ == '__main__':
    unittest.main()
