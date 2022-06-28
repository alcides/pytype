"""Tests for refined types"""

from pytype.tests import test_base


class TestRefined(test_base.BaseTest):
  """Tests for refined types."""

  def test_refined_simple(self):
    self.Check("""
      from typing_extensions import Annotated
      x: Annotated[int, "_ > 0"]
      y: Annotated[int,"_ < 10"]
      x = 1
      x = 2
      y = x
      
    """)
    

if __name__ == "__main__":
  test_base.main()
