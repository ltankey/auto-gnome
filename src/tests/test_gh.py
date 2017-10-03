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

class EventSourceValidatorTestCase(unittest.TestCase):
    def test_localhost_is_valid(self):
        """
        Given the ip string is 127.0.0.1
        When testing ip_str_is_valid
        Then validity is True
        """
        val = gh.EventSourceValidator()
        validity = val.ip_str_is_valid('127.0.0.1')
        self.assertTrue(validity)

    def test_good_addresses_are_valid(self):
        """
        Given the ip string is valid
        When testing ip_str_is_valid
        Then validity is True
        """
        val = gh.EventSourceValidator()
        for addr in GOOD_MOCK_ADDRESSES:
            validity = val.ip_str_is_valid(addr)
            self.assertTrue(validity)

    def test_bad_addresses_are_invalid(self):
        """
        Given the ip string is not valid
        When testing ip_str_is_valid
        Then validity is False
        """
        val = gh.EventSourceValidator()
        for addr in BAD_MOCK_ADDRESSES:
            validity = val.ip_str_is_valid(addr)
            self.assertFalse(validity)


class RepoTestCase(unittest.TestCase):
    def test_init_no_error(self):
        """
        Given I have a valid callback payload
        When I initiate a Repo
        Then no errors are raised
        """
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
        repo.milestone_exists = MagicMock(return_value=True)
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
        repo.milestone_exists = MagicMock(return_value=False)
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
        repo.milestone_exists = MagicMock(return_value=True)
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=None)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)

        repo.ensure_milestone_has_due_date('foo', DATE)
        mm.set_due_date.assert_called_with(DATE)

    def test_do_nothing_if_date_OK(self):
        """
        Given a malestone already has a specified due date
        When I call repo.ensure_milestone_has_due_date
        Then the due date is not updated
        """
        DATE =  '2012-10-09T23:39:01Z'
        repo = gh.repo_from_callback(MockCallback())
        repo.milestone_exists = MagicMock(return_value=True)
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=DATE)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)

        repo.ensure_milestone_has_due_date('foo', DATE)
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
        repo.milestone_exists = MagicMock(return_value=True)
        mm = gh.Milestone('some/repo', '_milestone')
        mm.get_due_date = MagicMock(return_value=WRONG_DATE)
        mm.set_due_date = MagicMock()
        repo.get_milestone = MagicMock(return_value=mm)

        repo.ensure_milestone_has_due_date('foo', DATE)
        mm.set_due_date.assert_called_with(DATE)


# TODO: FIXME: move next to classes into mocks.py
class MockMilestoneFoo:
    """
    Dummy pygithub.Milestone.Milestone thing for testing.

    Always titled "foo", exists to support the
    MockFooMilestoneWrapper. 
    """
    EXPECTED_TICKETS = ('A', 'B', 'C')

    def __init__(self):
        self.title = 'foo'
        

class MockFooMilestoneWrapper:
    """
    Dummy gh.Milestone for testing. Has a private _milestone
    attribute that is a MockMilestoneFoo.

    Exists to be monkeypatched into a gh.Repo to block
    some extranious calls to GitHub during testing.
    """
    def __init__(self):
        self._milestone = MockMilestoneFoo()
        self.repo = gh.repo_from_callback(MockCallback())
        self.repo._repo.get_issues = MagicMock(
            return_val=self._milestone.EXPECTED_TICKETS)


class RepoMilestoneExistsTestCase(unittest.TestCase):
    def test_true_if_milestone_exists(self):
        """
        Given a milestone exists
        When I call repo.milestone_exists
        Then True is returned
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        self.assertTrue(repo.milestone_exists('foo'))


    def test_false_if_milestone_not_exists(self):
        """
        Given a milestone does not exist
        When I call repo.milestone_exists
        Then False is returned
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        self.assertFalse(repo.milestone_exists('bar'))


class RepoGetMilestoneTestCase(unittest.TestCase):
    def test_returns_none_if_not_exists(self):
        """
        Given a milestone does not exist
        When I call repo.get_milestone on it's name
        Then None is returned
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        found = repo.get_milestone('bar')  # not 'foo'
        self.assertFalse(found)

    def test_returns_milestone_if_exists(self):
        """
        Given a milestone exists,
        when I call repo.get_milestone on it's name
        then not None is returned
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        found = repo.get_milestone('foo')
        self.assertTrue(found)


class RepoCreateMilestoneTestCase(unittest.TestCase):
    def test_heisenmockbug_weirdness(self):
        """
        Don't ask.
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        # 'foo' != 'bar'
        self.assertFalse(repo.get_milestone('bar'))

    def test_create_with_defaults_if_not_exist(self):
        """
        Given a milestone does not exist
        When I call repo.create_milestone
        Then the milestone is created
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        create_milestone_mock = MagicMock()
        repo._repo.create_milestone = create_milestone_mock
        repo.create_milestone('bar')
        create_milestone_mock.assert_called()

    def test_do_nothing_if_already_exists(self):
        """
        Given a milestone,
        when I call repo.create_milestone;
        idempotency.
        """
        # I call that Haiku "then nothing happens"
        
        repo = gh.repo_from_callback(MockCallback())
        repo._milestones = (MockFooMilestoneWrapper(),)
        create_milestone_mock = MagicMock()
        repo._repo.create_milestone = create_milestone_mock
        repo.milestone_exists = MagicMock(return_value=True)
        repo.create_milestone('foo')
        repo._repo.create_milestone.assert_not_called()


class MilestoneInitTestCase(unittest.TestCase):
    def test_repo_validation(self):
        """
        Given I have a valid callback payload
        When I initiate a Milestone
        Then no errors are raised
        """
        repo = gh.repo_from_callback(MockCallback())
        repo._repo.create_milestone = MagicMock()
        gh_milestone = MockMilestoneFoo()
        try:
            mlstn = gh.Milestone(repo, gh_milestone)
            was_error = False
        except:
            was_error = True
        self.assertFalse(was_error)


class MilestoneOpenTicketsTestCase(unittest.TestCase):

    def test_all_open_tickets_returned(self):
        repo = gh.repo_from_callback(MockCallback())
        ghm = MockMilestoneFoo()
        m = gh.Milestone(repo, ghm)
        m.repo._repo.get_issues = MagicMock(
            return_value=MockMilestoneFoo.EXPECTED_TICKETS)
        found = []
        for t in m.open_tickets():
            found.append(t._issue)
        expected = MockMilestoneFoo.EXPECTED_TICKETS

        for t in expected:
            self.assertTrue(t in found)

    def test_no_extranious_tickets_returned(self):
        repo = gh.repo_from_callback(MockCallback())
        ghm = MockMilestoneFoo()
        m = gh.Milestone(repo, ghm)
        m.repo._repo.get_issues = MagicMock(
            return_value=MockMilestoneFoo.EXPECTED_TICKETS)
        found = []
        for t in m.open_tickets():
            found.append(t._issue)
        expected = MockMilestoneFoo.EXPECTED_TICKETS

        for t in found:
            self.assertTrue(t in expected)


class IssueInitTestCase(unittest.TestCase):
    def test_init(self):
        """
        Given I have a valid callback
        When I initiate an Issue
        Then no errors are raised
        """
        repo = gh.repo_from_callback(MockCallback())
        gh_issue = MagicMock()
        try:
            i = gh.Issue(repo, gh_issue)
            was_error = False
        except:
            was_error = True
        self.assertFalse(was_error)


class IssueHasMilestoneTestCase(unittest.TestCase):
    def test_false_if_no_milestone(self):
        repo = gh.repo_from_callback(MockCallback())
        gh_issue = MagicMock()
        gh_issue.milestone = False
        i = gh.Issue(repo, gh_issue)
        self.assertFalse(i.has_milestone())

    def test_true_if_has_milestone(self):
        repo = gh.repo_from_callback(MockCallback())
        gh_issue = MagicMock()
        gh_issue.milestone = MagicMock()
        i = gh.Issue(repo, gh_issue)
        self.assertTrue(i.has_milestone())


class IssueMoveToMilestoneTestCase(unittest.TestCase):
    def test_milestone_not_exists_then_created(self):
        repo = gh.repo_from_callback(MockCallback())
        gh_issue = MagicMock()
        #gh_issue.milestone = False
        repo.milestone_exists = MagicMock(return_value=False)
        repo.create_milestone = MagicMock()
        repo.get_milestone = MagicMock()

        i = gh.Issue(repo, gh_issue)
        i.move_to_milestone('x')

        repo.create_milestone.assert_called()

    def test_repo_exists_then_not_created(self):
        repo = gh.repo_from_callback(MockCallback())
        gh_issue = MagicMock()
        #gh_issue.milestone = False
        repo.milestone_exists = MagicMock(return_value=True)
        repo.create_milestone = MagicMock()
        repo.get_milestone = MagicMock()

        i = gh.Issue(repo, gh_issue)
        i.move_to_milestone('x')

        repo.create_milestone.assert_not_called()


if __name__ == '__main__':
    unittest.main()
