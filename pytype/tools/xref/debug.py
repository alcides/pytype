"""Debug utils for working with the indexer and the AST."""

from pytype.ast import debug

# pylint: disable=protected-access
# We never care about protected access when writing debug code!


def format_loc(location):
  # location is (line, column)
  fmt = "%d:%2d" % location
  return fmt.rjust(8)


def format_def_with_location(defn, loc):
  return ("%s  | %s %s" % (
      format_loc(loc), defn.typ.ljust(15), defn.format()))


def format_ref(ref):
  return ("%s  | %s  %s.%s" % (
      format_loc(ref.location), ref.typ.ljust(15), ref.scope, ref.name))


def format_call(call):
  return ("%s  | %s  %s" % (
      format_loc(call.location), "Call".ljust(15), call.func))


def typename(node):
  return node.__class__.__name__


def show_defs(index):
  """Show definitions."""
  for def_id in index.locs:
    defn = index.defs[def_id]
    for loc in index.locs[def_id]:
      print(format_def_with_location(defn, loc.location))
      if defn.doc:
        print(" "*28 + str(defn.doc))


def show_refs(index):
  """Show references and associated definitions."""
  indent = "          :  "
  for ref, defn in index.links:
    print(format_ref(ref))
    if defn:
      print(indent, defn.format())
      for loc in index.locs[defn.id]:
        print(indent, format_def_with_location(defn, loc.location))
    else:
      print(indent, "None")
    continue


def show_calls(index):
  for call in index.calls:
    print(format_call(call))


def display_type(data):
  """Convert a pytype internal type to a display type."""
  name = "typing.Any"
  if data and data[0]:
    d = data[0][0]
    if d.cls:
      name = d.cls.full_name
  if name == "unsolveable":
    name = "typing.Any"
  elif name.startswith("z__pytype_partial"):
    name = "<unknown>"
  return name


def show_types(index):
  """Show inferred types."""
  out = []
  for def_id in index.locs:
    defn = index.defs[def_id]
    for loc in index.locs[def_id]:
      out.append((loc.location, defn.typ, defn.name, display_type(defn.data)))
  for ref, defn in index.links:
    out.append((ref.location, defn.typ, ref.name, display_type(ref.data)))
  # Sort by location
  for location, category, name, typ in sorted(out, key=lambda x: x[0]):
    # Filter out some noise
    if (category in ("FunctionDef", "IsInstance") or
        typ in ("builtins.module", "__future__._Feature")):
      continue
    print("%s  |  %s  %s" % (format_loc(location), name.ljust(35), typ))


def show_index(index):
  """Display output in human-readable format."""

  def separator():
    print("\n--------------------\n")

  show_defs(index)
  separator()
  show_refs(index)
  separator()
  show_calls(index)
  separator()


def show_map(name, mapping):
  print("%s: {" % name)
  for k, v in mapping.items():
    print("  ", k, v)
  print("}")


# reexport AST dumper

dump = debug.dump
