import unittest
from web import app


class TestWebApp(unittest.TestCase):
    @classmethod
    def setUp(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        if response.status_code == 200:
            print("✅ Home page success")
        else:
            print("❌ Home page not found")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
