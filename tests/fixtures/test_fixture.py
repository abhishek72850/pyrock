import time
from django.test import TestCase


class MyTestCase(TestCase):
    def test_long_running_task(self):
        # Simulate a long-running task
        time.sleep(1)
        # Add your actual test assertions here (if any)
        self.assertEqual(1 + 1, 2)


def test_iam_alone():
    assert 1 + 1 == 2
