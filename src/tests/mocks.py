import json

class MockResponse:
    """
    Mock response object that always returns the same canned data
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

    @classmethod
    def text(self):
        return 'some yaml'
    

class MockCallback(object):
    def payload(self):
        return {'repository':{"full_name": "billgates/windows95"}}


def mock_get(x):
    """
    Mock get method that ignores it's parameter and returns
    the same mock response regardless.
    """
    return MockResponse()
                

