"""Tests for refined types"""

from pytype.tests import test_base


class TestRefined(test_base.BaseTest):
  """Tests for refined types."""

  def test_refined_simple(self):
    self.Check("""
      from typing_extensions import Annotated
      x: Annotated[float, "a"]
      x = 1
    """)
    

if __name__ == "__main__":
  test_base.main()
