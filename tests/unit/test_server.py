
from initserver import server
import unittest


class CloudInitServerTestCase(unittest.TestCase):

    def test__add_route(self):
        s = server.CloudInitServer(None)
