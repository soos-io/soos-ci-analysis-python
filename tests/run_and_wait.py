import unittest
import subprocess
import os


class RunAndWaitTestCase(unittest.TestCase):
    def test_with_issues(self):
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/with_issues/script.sh"], capture_output=True, text=True)
        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count("Analysis complete - Failures reported."), 1)
        self.assertEqual(process.stdout.count("Vulnerabilities: 22"), 1)
        self.assertEqual(process.stdout.count("Violations: 5"), 1)


if __name__ == '__main__':
    unittest.main()
