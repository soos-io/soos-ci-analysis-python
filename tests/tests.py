import os
import subprocess
import unittest

test_complete_success = "Analysis Completed Successfully"
test_complete_fail = "Analysis complete - Failures reported"


def vulnerabilities(x):
    return f"Vulnerabilities: {x}"


def violations(x):
    return f"Violations: {x}"


class GemfileTestCases(unittest.TestCase):
    def test_gemfile(self):
        print("testing gemfile")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/gemfile/script.sh"], capture_output=True,
                                 text=True)
        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(4)), 1)
        self.assertEqual(process.stdout.count(violations(4)), 1)


class DartTestCases(unittest.TestCase):
    def test_dart(self):
        print("testing dart")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/dart/script.sh"], capture_output=True,
                                 text=True)

        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(2)), 1)
        self.assertEqual(process.stdout.count(violations(5)), 1)


class GradleTestCases(unittest.TestCase):
    def test_gradle(self):
        print("testing gradle")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/gradle/script.sh"], capture_output=True,
                                 text=True)

        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(59)), 1)
        self.assertEqual(process.stdout.count(violations(5)), 1)


class RustTestCases(unittest.TestCase):
    def test_rust(self):
        print("testing rust")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/rust/script.sh"], capture_output=True,
                                 text=True)

        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(7)), 1)
        self.assertEqual(process.stdout.count(violations(5)), 1)


class NugetTestCases(unittest.TestCase):
    def test_nuget(self):
        print("testing nuget")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/nuget/script.sh"], capture_output=True,
                                 text=True)

        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(1)), 1)
        self.assertEqual(process.stdout.count(violations(5)), 1)


# class MavenTestCases(unittest.TestCase):
#     def test_maven(self):
#         print("testing maven")
#         process = subprocess.run(["sh", f"{os.getcwd()}/manifests/maven/script.sh"], capture_output=True,
#                                  text=True)
#
#         self.assertEqual(process.returncode, 0)


class ComposerTestCases(unittest.TestCase):
    def test_composer(self):
        print("testing composer")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/composer/script.sh"], capture_output=True,
                                 text=True)

        print(process.stdout)
        self.assertEqual(process.returncode, 0)


class NPMTestCases(unittest.TestCase):
    def test_with_issues(self):
        print("testing with issues")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/with_issues/script.sh"], capture_output=True,
                                 text=True)
        print(process.stdout)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout.count(test_complete_fail), 1)
        self.assertEqual(process.stdout.count(vulnerabilities(22)), 1)
        self.assertEqual(process.stdout.count(violations(5)), 1)

    def test_no_issues(self):
        print("testing without issues")
        process = subprocess.run(["sh", f"{os.getcwd()}/manifests/no_issues/script.sh"], capture_output=True, text=True)
        print(process.stdout)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(process.stdout.count("Analysis Completed Successfully"), 1)
