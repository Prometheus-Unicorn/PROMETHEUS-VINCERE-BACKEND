import unittest
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.discover(str(REPO_ROOT / "tests"), pattern="test_visual_helpers.py"))
suite.addTests(loader.discover(str(REPO_ROOT / "tests"), pattern="test_subject_safe_typography.py"))
suite.addTests(loader.discover(str(REPO_ROOT / "tests"), pattern="test_editorial_placement_refinements.py"))

runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)

if result.wasSuccessful():
    print("PASS_ALL_EDITORIAL_SUITE_OK")
    sys.exit(0)
else:
    sys.exit(1)
