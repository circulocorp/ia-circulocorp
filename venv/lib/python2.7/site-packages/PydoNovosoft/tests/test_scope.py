from unittest import TestCase
import PydoNovosoft


class TestScope(TestCase):

    def test_mzone(self):
        m = PydoNovosoft.scope.MZone("", "", "")
        m.gettoken()
        self.assertTrue(m.check_token())

    def test_subscriptions(self):
        m = PydoNovosoft.scope.MZone("", "", "")
        m.gettoken()

