import unittest

class CallbackEventInit(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(1,1)
    # needs to be passed a valid request object
    # throw error if not passed a valid request object

class CallbackEventPayload(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(1,1)
    # throw InvalidPayloadJSONError if payload is not valid json
    # if initiated with request that has valid json payload, returns valid json object

class CallbackEventValidator(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(1,1)
    # invalid json returns false
    # false if payload has no repository
    # false if payload['repository'] has no full_name
    # valid payloads return true

if __name__ == "__main__":
    unittest.main()
