import unittest
from unittest.mock import patch, MagicMock
from sweetcookiekit import get_cookies, CookieRecord, CookieStore

class TestSweetCookieKit(unittest.TestCase):
    @patch("subprocess.run")
    def test_get_cookies(self, mock_run):
        # Mocking the JSON payload output from the Swift CLI
        mock_stdout = """
        {
          "generatedAt" : "2023-10-27T10:00:00Z",
          "stores" : [
            {
              "browser" : "chrome",
              "browserDisplayName" : "Google Chrome",
              "kind" : "primary",
              "label" : "Profile 1",
              "profileId" : "Profile 1",
              "profileName" : "Profile 1",
              "records" : [
                {
                  "domain" : ".example.com",
                  "expires" : "2024-10-27T10:00:00Z",
                  "isHTTPOnly" : true,
                  "isSecure" : true,
                  "name" : "session_id",
                  "path" : "/",
                  "value" : "abcdef123456"
                }
              ]
            }
          ]
        }
        """

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_run.return_value = mock_result

        stores = get_cookies(domains=["example.com"], browsers=["chrome"], all_browsers=False, include_expired=True)

        mock_run.assert_called_once_with(
            ["SweetCookieCLI", "--format", "json", "--domains", "example.com", "--browser", "chrome", "--include-expired"],
            capture_output=True, text=True, check=True
        )

        self.assertEqual(len(stores), 1)
        store = stores[0]
        self.assertIsInstance(store, CookieStore)
        self.assertEqual(store.browser, "chrome")
        self.assertEqual(store.profileName, "Profile 1")

        self.assertEqual(len(store.records), 1)
        cookie = store.records[0]
        self.assertIsInstance(cookie, CookieRecord)
        self.assertEqual(cookie.name, "session_id")
        self.assertEqual(cookie.value, "abcdef123456")
        self.assertTrue(cookie.isSecure)

if __name__ == "__main__":
    unittest.main()
