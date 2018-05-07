"""Tests for the analysis phase matcher (match_var_against_type)."""

from pytype import utils
from pytype.tests import test_base


class MatchTest(test_base.TargetIndependentTest):
  """Tests for matching types."""

  def testTypeAgainstCallable(self):
    with utils.Tempdir() as d:
      d.create_file("foo.pyi", """
        from typing import Callable
        def f(x: Callable) -> str
      """)
      ty = self.Infer("""
        import foo
        def f():
          return foo.f(int)
      """, pythonpath=[d.path])
      self.assertTypesMatchPytd(ty, """
        foo = ...  # type: module
        def f() -> str
      """)

  def testMatchStatic(self):
    ty = self.Infer("""
      s = {1}
      def f(x):
        # set.intersection is a static method:
        return s.intersection(x)
    """)
    self.assertTypesMatchPytd(ty, """
      from typing import Set
      s = ...  # type: Set[int]

      def f(x) -> set: ...
    """)

  def testGenericHierarchy(self):
    with utils.Tempdir() as d:
      d.create_file("a.pyi", """
        from typing import Iterable
        def f(x: Iterable[str]) -> str
      """)
      ty = self.Infer("""
        import a
        x = a.f(["a", "b", "c"])
      """, pythonpath=[d.path])
      self.assertTypesMatchPytd(ty, """
        a = ...  # type: module
        x = ...  # type: str
      """)

  def testGeneric(self):
    with utils.Tempdir() as d:
      d.create_file("a.pyi", """
        from typing import Generic, Iterable
        K = TypeVar("K")
        V = TypeVar("V")
        Q = TypeVar("Q")
        class A(Iterable[V], Generic[K, V]): ...
        class B(A[K, V]):
          def __init__(self):
            self := B[bool, str]
        def f(x: Iterable[Q]) -> Q
      """)
      ty = self.Infer("""
        import a
        x = a.f(a.B())
      """, deep=False, pythonpath=[d.path])
      self.assertTypesMatchPytd(ty, """
        a = ...  # type: module
        x = ...  # type: str
      """)

  def testMatchIdentityFunction(self):
    with utils.Tempdir() as d:
      d.create_file("foo.pyi", """
        from typing import TypeVar
        T = TypeVar("T")
        def f(x: T) -> T: ...
      """)
      ty = self.Infer("""
        import foo
        v = foo.f(__any_object__)
      """, pythonpath=[d.path])
      self.assertTypesMatchPytd(ty, """
        from typing import Any
        foo = ...  # type: module
        v = ...  # type: Any
      """)

  def testCallableReturn(self):
    with utils.Tempdir() as d:
      d.create_file("foo.pyi", """
        from typing import Callable, TypeVar
        T = TypeVar("T")
        def foo(func: Callable[[], T]) -> T: ...
      """)
      self.Check("""
        import foo
        class Foo(object):
          def __init__(self):
            self.x = 42
        foo.foo(Foo).x
      """, pythonpath=[d.path])

  def testCallableUnionReturn(self):
    with utils.Tempdir() as d:
      d.create_file("foo.pyi", """
        from typing import Callable, TypeVar
        T1 = TypeVar("T1")
        T2 = TypeVar("T2")
        def foo(func: Callable[[], T1]) -> T1 or T2: ...
      """)
      self.Check("""
        import foo
        class Foo(object):
          def __init__(self):
            self.x = 42
        v = foo.foo(Foo)
        if isinstance(v, Foo):
          v.x
      """, pythonpath=[d.path])

  def testAnyBaseClass(self):
    with utils.Tempdir() as d:
      d.create_file("foo.pyi", """
        from typing import Any
        class Foo(Any): pass
        class Bar(object): pass
        def f(x: Bar) -> None
      """)
      self.Check("""
        import foo
        foo.f(foo.Foo())
      """, pythonpath=[d.path])

  def testMaybeParameterized(self):
    self.Check("""
      import collections
      class Foo(collections.MutableMapping):
        pass
      dict.__delitem__(Foo(), __any_object__)  # pytype: disable=wrong-arg-types
    """)


if __name__ == "__main__":
  test_base.main()
