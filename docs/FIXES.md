# What `--fix` infers

The [README](../README.md#use) has the options (`--fix`, `--diff` to preview, `--unsafe-fixes`,
`--likely`, `--show-fixes`). A guess below is applied with `--unsafe-fixes`; `--likely` applies
those whose mechanisms [LIKELY.md](LIKELY.md) measured to hold. `--fix` adds the annotation where
the value decides it, for a plain `name = value` in a function or module body:

- a literal: `count = 0` becomes `count: int = 0`; and `not x`, or a comparison by `in`, `not in`,
  `is` and `is not` alone (`"r" in mode`), always a `bool` whatever it compares (`==` and `<` may
  return anything, as numpy's arrays do), and any comparison of builtin values (`n < 3`,
  `len(xs) == 0`, `name != "x"`), a `bool` too;
- a container whose elements agree: `[1, 2]` gives `list[int]`, `{"a": (1, "b")}` gives
  `dict[str, tuple[int, str]]`; a tuple longer than `max-length` (4) is `tuple[T, ...]` if its
  elements agree, and untyped if not (it would be LVA011's). A starred element gives each of what it
  unpacks (`[*names, s]` is a `list[str]`, `(*names, s)` a `tuple[str, ...]`), and `**d` a `dict`'s
  keys and values (`{**d, k: v}`). A list, set or dict whose elements' types differ is their union,
  `None` last (`[1, "a"]` is a `list[int | str]`, `{"k": 1, "j": None}` a `dict[str, int | None]`):
  up to three, each a plain name (not a container or a union), and a guess (`joined`), since a
  checker joins them too, but not always to the same union (mypy to their common base);
- a call to a capitalised name (`path = Path(...)` gives `Path`, a guess; not a standard-library
  function, `ET.Comment(...)`), or to a class the checked files define whatever its name's case
  (`_Definitions()`), if it can be written as a type: a name or dotted name whose first name the
  module binds only by an import or a class statement (not `Klass = ...`, `self.api.X()`,
  `make().X()`); or to a plain function that declares its return type, by an annotation or a
  `# type:` signature comment (`# type: () -> List[str]`) (not a generic, async or redefined one,
  and not a return of `None`, `Any` or one that uses a `TypeVar`), in the same module or, with the
  CLI, in another file it's checking: `from pkg.util import f`, `import pkg.util as u` or
  `from pkg import util` then `u.f()`, relative imports and re-exports all work. A name in the type
  the file doesn't import is imported for type checking alone (see below). A decorated function
  counts (a method too) only under decorators that give it back: the standard library's
  (`functools.cache`, `lru_cache`, `wraps(...)`, `abc.abstractmethod`, `typing.final`, `override`,
  `deprecated(...)`), and a function whose own signature says so, taking `F` and returning `F`, or
  (called to decorate, as `@set_module("pandas")`) returning a `Callable[[F], F]`, where `F` is a
  type variable or a `Callable[P, T]` returning one. The module's own such decorators count
  anywhere; one it imports from a checked file or an installed package, with the CLI, which finds
  its type variables;
- a classmethod or staticmethod called on its class, by its declared return: `Box.make()` is a `Box`
  (`Self` is the class), for a top-level class defined once whose name the module binds no other
  way, and a class that takes the method from a base in the module (`Sub.make()` is a `Sub` where
  `make` returns `Self`); with the CLI, another checked file's class too, however it's imported or
  re-exported (`from pkg import Row`, `m.Row.make()`, `pkg.Row.make()`), and a class of the module's
  under one (`Sub.make()`, `make` its imported base's: a `Sub`, where it returns `Self`). On an
  instance it types the call as a method does (`self.info(stmt)`, a staticmethod). Under decorators
  that give the method back, as a function's (`@classmethod` over `@names_compat`); a property
  counts under them too;
- a builtin with a fixed result: `len(x)` is an `int`, `hex(n)` a `str`, `any(xs)` a `bool`, `dir()`
  a `list[str]`, `range(n)` a `range`, and so on; but not where the module binds the name itself (a
  parameter named `format`, a local `input`, its own `def dir()`), anywhere in it. `type(x)` is a
  `type[C]` for an `x` of one type `C` (not a union's, nor `None`'s), as `x.__class__` is (not a
  class's own, its metaclass), and a class's `__name__`, `__qualname__` and `__module__` read of
  either are `str`s, whatever `x` is (`type(x).__name__`, `self.__class__.__name__`);
- `enumerate(xs)`, `zip(xs, ys)`, `map(f, xs)` and `reversed(xs)` bound to a name, by what a loop
  over each binds: `enumerate[str]`, `zip[tuple[str, int]]`, `map[int]`, `reversed[str]` (`zip` of
  up to five iterables, as typeshed's overloads go). At module level, where an annotation is
  evaluated, `zip`'s, `map`'s and `reversed`'s are quoted: no Python subscripts them at run time.
  `iter(xs)` is an `Iterator` of the same (`Iterator[str]`), imported from `collections.abc` where
  the module doesn't name it, and left alone where the name is something else's;
- a builtin its arguments decide, as typeshed has it: `abs(n)`, `round(x)` (an `int`; with digits,
  `x`'s type), `divmod(n, 2)` (a `tuple[int, int]`) and `sum(xs)` of builtin numbers; `min` and
  `max` of several values of one type (of an `int` and a `float`, a `float`), or of something's
  elements (`max(names)`, `key=` or not; with `default=`, a value of that type, or `None` for
  `T | None`); `next(it)` of what yields a known type (`next(iter(names))`,
  `next((x for x in xs if x), None)` as `T | None`); and `dict(mapping)`, `dict(pairs)`
  (`dict(zip(names, ages))`) and `dict(a=1, b=2)` (a `dict[str, int]`). Not with arguments unpacked,
  nor where the module binds the name;
- a copy of a local whose type is already known (annotated, a parameter, or fixed earlier in the
  same scope): `y = x`;
- a name the module binds once, anywhere in it, at its top level, read in a function as it's typed
  there: `LIMIT = 10` is an `int` in every function, and `for name in NAMES` loops over what
  `NAMES = ["a", "b"]` holds. By its annotation (a `Final[T]`'s or a `ClassVar[T]`'s `T`; a bare
  `Final`'s value's type, in the module's own body too: `[A, B]` of a `B: Final = "b"` is a
  `list[str]`), or its one value's type, a guess where that's one; a name bound to what an
  unannotated function returns is typed in the same run. Not a name bound again anywhere (a
  parameter or a local of that name in any function, a `global` statement's), a type alias, nor one
  first `None`. A module's own `__file__` and `__name__` are `str`s;
- a member of any value whose type is known, a local or anything else here (`self.index`, `f()`,
  `xs[0]`, `", "`), however deep (`self.index.name.upper()`): a subscript (`nums[0]`; a slice, or an
  index typed `slice`, is the container's own type; a fixed-length tuple's part by a literal index,
  `pair[0]` or `pair[-1]`), an attribute (an annotated one, or a `@property` declaring its return)
  or method call of a class defined in the same module or another checked file (`p.x`, `p.norm()`),
  a `str`/`bytes` method with a fixed return (`s.strip()`, `", ".join(parts)`,
  `"k=v".partition("=")` as `tuple[str, str, str]`; an `int`'s or a `float`'s too, `n.bit_length()`,
  `x.is_integer()`), or a `list`/`set`/`dict` method that returns its own element type
  (`nums.pop()`, `d.get(k)` as `V | None`, `d.get(k, 0)` as `V` with a default of that type) or one
  type whatever it holds (`names.count(x)` and `pair.index(x)` are `int`s, `seen.issubset(other)` a
  `bool`, `seen.difference(other)` and `seen.intersection(other)` a `set` of `seen`'s own type);
  `self` is its class's instance in a method, and in a function defined in one that takes and binds
  no `self` of its own (not under a method whose signature says `Self`); in a classmethod, `cls` is
  `type[C]`, whose class attributes (`limit: int = 3`, `ClassVar[T]`) and classmethods' and
  staticmethods' declared returns type `cls.x` and `cls.m()`. A member of a guessed value is a guess
  too (`Box().name`), and its fix kinds include the value's. A member of an `X | None` (or
  `Optional[X]`) is `X`'s: a checker has narrowed the value there, or reports the access
  (`m = re.match(...)`, then `m.start()` is an `int`); not one `None` has too (`__class__`), nor a
  union of more types;
- a method a class doesn't define, called on `self` or any value typed as the class: the base's that
  defines it, in Python's method resolution order, among the module's own classes (each defined
  once, not generic) and then a class another checked file defines (the CLI only), which ends the
  search with what it takes from its own file's classes, or a standard-library class the tables hold
  whole (past which the order goes on, for what it doesn't have, to a second one that shares no
  ancestor with it: `class Both(threading.Thread, unittest.TestCase)`), by its members there
  (`self.id()` in a `unittest.TestCase` is a `str`, `self.name` in a `threading.Thread` a `str`),
  which another checked file's class is followed to as well, through its own bases in any checked
  file or installed package (one that declares no types is read for its classes' bases alone:
  `django.test.TestCase`), each line of them reaching a library class at most (a mixin beside it
  ends at none; two lines reaching one each give both, in order, where they share no ancestor): what
  none of them binds is the library class's (`self.id()` under a project's own
  `Case(unittest.TestCase)`), a method its arguments decide included
  (`self.assertRaises(ValueError)`). A declared return is certain, and a `Self` one is the
  receiver's class; `return`s are a guess, and not offered where their type names the base
  (`return self` gives the receiver's class): another checked file's method's too (the CLI only), a
  class there having those it takes from its own file's classes. Another checked file's mixin, whose
  line of bases ends at no library class, doesn't end the search: what that line doesn't bind is the
  next base's (`self.id()` under `class Tests(Mixin, unittest.TestCase)`). A generic library base
  given its arguments types what the class takes from it (`self.popitem()` under
  `collections.OrderedDict[str, int]` is a `tuple[str, int]`; a subscript, a loop and `.items()`
  too). Nothing for a name the class's body binds any other way, past a base out of sight (a
  computed one, a generic one without its arguments), or for another file's or the standard
  library's method returning its own class, which may be its `Self` (`self.resolve()` under `Path`);
- an attribute a class doesn't declare, read of `self` or any value typed as the class: the base's
  that does (an annotation, a `self.x: T`, a `@property`), found as an inherited method is, among
  the module's own classes and then a class another checked file defines (the CLI only), with what
  that takes from its own file's classes; a class's own attribute (`cls.limit`) the same way, among
  the module's classes. A property declared to return `Self` is the receiver's class. Nothing for a
  name a class before it binds another way, past a generic base or one out of sight, or for another
  file's attribute typed as its own class (a property's `Self`, perhaps);
- a function or a bound method bound to a name in a function (`dump = json.dumps`,
  `grow = item.grow`): a `Callable[..., R]`, `R` what its call gives whatever it's passed (a
  declared return, the module's, another checked file's, a builtin's or the standard library's),
  `Callable` imported from `collections.abc` if it must be; a lambda too, by its body, where that
  rests on none of its parameters or its function's names (`first = lambda: 1` is a
  `Callable[[], int]`). Its parameters are left open: a `Callable[[A], R]` would refuse the keywords
  and defaults a call through the name may use. They're listed (`Callable[[int, str], bytes]`) for a
  function or method of the module's whose parameters are all positional, annotated and without a
  default, where every call through the name in its function passes as many, none by keyword. Not a
  class, a callee typed only by its `return`s or whose arguments decide its type, nor a name the
  function reads an attribute of (`run.cache_clear()`). A lambda whose body rests on its parameters
  is typed by what its calls pass them (`double = lambda x: x * 2`, called only as `double(3)`, is a
  `Callable[..., int]`): every use of the name in its function a call, each parameter given one type
  by position; a guess (`callers`). A module's name bound so is a `Callable` too
  (`dump = json.dumps`, where the module reads no attribute of it), and a plain class's, as a guess
  (`member`), a method of its own included (`length = size`);
- what `with mock.patch(target) as m:` binds, and `patch.object`'s, given no `new` or
  `new_callable`: a `MagicMock | AsyncMock`, as typeshed declares it;
- a `TypedDict`'s key read by a literal, on a value typed as the class: `movie["year"]` is the key's
  declared type (less the `Required`, `NotRequired` or `ReadOnly` around it), `movie.get("year")`
  that or `None`, and `movie.get("year", 0)` the type itself, with a default of it. A class under
  `TypedDict`, or under one its module defines before it, with its bases' keys; not a generic one,
  nor one made by a call. In the module, another checked file (the CLI only), or an installed
  package that declares its types (`schema["ref"]` on a `core_schema.ModelSchema` is a `str`);
- a call of a value whose type says what calling it gives: a local, an attribute or anything else
  typed `Callable[..., R]` is an `R` (`handler(source)`, `self.handler(source)`, `hooks[0](x)`); one
  typed `type[C]` constructs a `C` (`cls()` in a classmethod, `type(self)()`), as does `__new__`
  given one (`cls.__new__(cls)`, `object.__new__(Row)`); and an instance of a class declaring
  `__call__`, what that returns (another checked file's class too). Not a callable that may be
  `None`, nor an `R` that is `None` or vague;
- `typing.cast(T, x)`, however `cast` is imported: `T`;
- a call of one of the module's `NewType`s (`Ref = NewType("Ref", str)` at its top level, however
  `NewType` is imported, the name bound nowhere else): `Ref(name)` is a `Ref`, in another checked
  file too, as a function declaring its return types its calls;
- the standard library, resolved through the imports (`import m`, `import m as a`,
  `from m import f`; a function's own too, in it and the functions inside it, for a name it binds no
  other way), by tables generated from typeshed's stubs when the package is built
  (`stdlib_tables/generate.py`, into `constricter/fix/tables/`, keeping what Linux, macOS and
  Windows and Python 3.11 to 3.14 agree on, where they have it: `os.getuid()` is an `int`): a
  function returning a builtin type whatever its arguments (`time.time()` is a `float`,
  `os.cpu_count()` an `int | None`); a non-generic class, or a function or classmethod returning
  one: `logging.getLogger()` is a `logging.Logger`, `datetime.now()` a `datetime.datetime`,
  `os.stat(p)` an `os.stat_result`, `sys._getframe()` (private, and called all the same) a
  `types.FrameType`; and on a value typed as such a class, its attributes and properties, and its
  methods' returns (`parser.prog` is a `str`, `dt.astimezone()` a `datetime.datetime`);
- a standard-library function or method whose arguments decide its type, by the signature they
  match, as a type checker picks among its overloads: `os.listdir(data)` with `data: bytes` is a
  `list[bytes]`, `ast.parse(s, mode="eval")` an `ast.Expression` (by the literal),
  `os.path.join(name, x)` a `str` whatever `x` is (only the `str` signature takes `name`),
  `os.getenv("X", 3)` a `str | int`, `re.compile("x")` a `re.Pattern[str]` (its type variable bound
  by the argument), `parser.parse_args()` an `argparse.Namespace`, and on a `re.Pattern[str]`,
  `pat.match(s)` a `re.Match[str] | None` (the class's type parameter bound by the receiver's type).
  A generic class returned bare is written with its type parameters' defaults, as a type checker
  reads it: `ET.SubElement(root, "x")` is an `ET.Element[str]`. A generic class's constructor is
  read the same way, from its `__new__` or `__init__`: `collections.deque(names)` with
  `names: list[str]` is a `collections.deque[str]`, `itertools.product(a, b)` an
  `itertools.product[tuple[str, int]]`, `array.array("i")` an `array.array[int]`, `weakref.ref(obj)`
  a `weakref.ReferenceType[Foo]`. Only when that's certain: every signature that may be the one (not
  certainly refusing the arguments, up to the first that certainly takes them) gives the same type,
  on every platform and version, with every type variable bound (`collections.deque()` isn't typed).
  An argument binds a type variable by its type: a builtin scalar (`str`, `bytes`, `int`, a literal,
  `None`, ...) wherever the parameter takes it; any other type only where the parameter is nothing
  but an unbounded type variable (`copy.copy(obj)` is a `Foo`), or a bound one where the function
  has one signature (`contextlib.closing(conn)` is a `contextlib.closing[Conn]`); a builtin
  container (`list[str]`, `dict[str, int]`'s keys, `tuple[str, ...]`) or a `str` by its element,
  where the parameter is a generic class of one (`Iterable[_T]`); a scalar by its method's return,
  where the parameter is a generic protocol (`math.floor(x)` is an `int` for a `float`, by
  `float.__floor__`); and a function by its declared return, where the parameter is a
  `Callable[..., _T]` (`functools.partial(helper, 1)` is a `functools.partial[str]`). Two arguments
  binding one differently leave the call alone (`itertools.chain(names, ids)`), as does unpacking
  `*args` or `**kwargs`. At module level, where an annotation is evaluated when the module runs, a
  class some supported Python can't subscript at run time is quoted
  (`counter: "itertools.count[int]"`), unless the module has `from __future__ import annotations`;
- a generic standard-library class's own attribute or property, by the receiver's type arguments:
  `m.string` on an `re.Match[str]` is a `str`, `p.pattern` on an `re.Pattern[bytes]` a `bytes`; and
  what it inherits with one type whatever they are: `f.read()` on an `io.TextIOWrapper` is a `str`
  (`TextIOBase`'s), `f.readlines()` on an `io.BufferedReader` a `list[bytes]`; and any other
  standard-library class's attribute or property typed with classes' own arguments, its own or one
  it inherits: `sig.parameters` on an `inspect.Signature` is a
  `MappingProxyType[str, inspect.Parameter]`, `tree.body` on an `ast.Module` a `list[ast.stmt]`;
- a standard-library method declared to return a type naming `Self`, by the receiver's own type:
  `path.iterdir()` on a `Path` is a `Generator[Path]` (so `for child in path.iterdir()` declares
  `child: Path`), `names.copy()` on a `collections.deque[str]` a `collections.deque[str]`; on a
  class of the module's under the library's, that class. Where Python versions declare a `Generator`
  and an `Iterator` of the same thing (`path.glob(...)`, an `Iterator` from 3.13), it's the
  `Iterator` every one of them is. Not on a generic class named without its arguments;
- a standard-library module's variable, by its annotation in typeshed: `sys.path` is a `list[str]`,
  `os.sep` a `str`, `sys.modules` a `dict[str, ModuleType]` (not `sys.stdout`, typeshed's
  `TextIO | Any`), and `os.environ["X"]` a `str`; a name a function binds itself (a parameter
  `getpid`) isn't the module's import;
- a subscript of a standard-library class's instance, by its `__getitem__` in typeshed, as a call
  passing it the index is typed: `proxy["k"]` on a `MappingProxyType[str, int]` is an `int`,
  `queue[0]` on a `deque[str]` a `str`, `parser["section"]` a `configparser.SectionProxy`, and
  `match[0]` on an `re.Match[str]` a `str` (not `match[i]`, typeshed's `str | Any`);
- `open(path, mode)` (or `io.open`), by its literal mode (`r` when there's none): a text mode gives
  an `io.TextIOWrapper`, a binary one an `io.BufferedReader` to read, an `io.BufferedWriter` to
  write, and an `io.BufferedRandom` for both (`+`). Not unbuffered (`buffering`, which gives an
  `io.FileIO`), with an `opener`, or when the module binds `open` itself; `path.open(mode)` on a
  `pathlib` path, the same way;
- `x = None`, when every later binding of `x` in the function has one certain type `T` (and nothing
  else writes it, nor reads it from a function or lambda inside, which would see `T | None` where a
  checker otherwise sees what `x` was narrowed to): `T | None`;
- a call to an unannotated function (or method) of the module, when every `return` it has gives one
  type and it can't fall off its end: that type, certain for a function and a guess for a method (a
  subclass may override it); a function whose `return`s are themselves guesses makes its calls
  guesses too. A generator function counts by its `yield`s instead: each a statement of its own
  (nothing is sent in), all of one type `T`, and no `return` of a value, give a
  `Generator[T, None, None]`, imported from `collections.abc` if it has to be; `yield from` gives
  its iterable's elements, and a `yield` of a local bound more than once is unknown. Chains (`f`
  returns `g()`) are followed, a few links deep. With the CLI, a module function in another checked
  file types its calls the same way, imported as a declared one is (and as long as the file can name
  its type): the files are checked callees first, and files calling each other's functions are
  checked again, up to 3 more times, while that types more;
- with `--unsafe-fixes`, an unannotated instance attribute (`self.x`, or `x` on any value typed as
  its class), when every `self.x = value` in the class's own methods gives one known type (numbers
  widen to the widest: `int`, then `float`): that type. A guess, since a subclass or outside code
  may assign it too; an attribute the class body binds, stored any other way (`+=`, an unpacking,
  `del`, a nested function's `self.x = ...`), or assigned a local bound more than once, is left
  alone. One bound to an empty container (`self.items = []`) is typed by what the class's own
  methods, and those of the module's classes under it, add to it, as a function's is below
  (`self.items.append(row)` in another method: a `list[Row]`), with any other value it's assigned;
  every read of it in the class counts as a use. One another checked file's class binds empty and
  does no more with is typed, for a class under it, by that class's own methods' additions (the CLI
  only);
- with `--unsafe-fixes`, a plain class's variable (`limit = 3` in its body), bound once there to a
  literal or a display of them, or to what the standard library gives as the module names it
  (`pattern = re.compile("x")`, `sep = os.sep`, `size = len(NAMES)`), and what reads it
  (`self.limit`, `cls.limit`, or `limit` on any value typed as the class or one inheriting it): the
  value's type. A plain class is defined once in its module, with no decorator, metaclass or other
  keyword, every base `object`, a `unittest` test case, `Generic[T]`, `abc.ABC` or another plain
  class, subscripted or not (`Box[int]`; another checked file's too, with the CLI), and no class
  that isn't plain inheriting from it (a model's mixin). A guess (`member`), since a subclass or
  outside code may bind it to another type; a variable the module stores as anything else is left
  alone (`self.limit = size`; not `self.limit = 5` or `self.limit += 1`, which keep an `int`), and
  so is every other class body, where an annotation can be more than a type (a dataclass's, a
  `NamedTuple`'s or a model's field). A builtin exception or value class is a base a plain class may
  have too (`ValueError`, `str`, `dict`; not one the module binds itself), and so is a framework's
  that reads no annotation in a class body: django's are built in (`per_page = 20` under
  `models.Model`, `paginate_by = 10` under a `ListView`; not its `Choices`, enums whose members a
  type checker won't have annotated), and `fix-plain-bases` lists more (`--fix-plain-bases BASES`):
  a class by its dotted path, or a package for every class in it, `!` before one to leave it out. A
  listed base counts where a checked file defines it too, decorated or under a metaclass as it may
  be (django's own files, checked);
- a module's type alias, declared one: `Json = dict[str, "Json"]` becomes `Json: TypeAlias = ...`
  (fix kind `alias`). Only a value that can be nothing but a type made of others: a subscript of
  what `typing`, `typing_extensions` or `collections.abc` define (`Union[A, B]`, `Callable[..., R]`,
  `Literal["a"]`), of a builtin generic (`dict[str, int]`) or of a generic class the module names
  (its own, another checked file's, the standard library's); or a union of those, of builtin
  classes, of classes the checked files define and of `None`; or a copy of a name the module
  declares an alias (`Rows = Table`). Not a bare class's alias (`Alias = Class`), a chained
  assignment, a name the module binds twice (a variable, to a type checker) or as a value somewhere,
  nor a function's or a class body's. `TypeAlias` is named as the module's imports can (`TypeAlias`,
  `t.TypeAlias`, where bound before the alias), else imported from `typing`, which has it from
  Python 3.10: certain where the module imports the name already (or `typing_extensions`), or
  `min-python` is 3.10 or later; a guess where `min-python` isn't known, and no fix where it's older
  (the import would fail there);
- an attribute, property or method of a class another checked file defines, its type imported as a
  declared return's is (the CLI only: the plugins see one file at a time);
- with `--unsafe-fixes` (the CLI only), what's computed from an unannotated parameter of a plain
  top-level function (undecorated, without `*args` or `**kwargs`) when every call in the checked
  files passes it an argument of the same type made of builtins alone (`int`, `list[str]`; not a
  union, nor a class another module may not name): `def greet(name)` called only as `greet("a")`
  types `line = name.upper()` as `str`. A guess (`callers`), since a caller outside the checked
  files may pass anything; never for a function used any way but called (a callback), one a call
  leaves a parameter to its default, can't be matched to, or unpacks its arguments for, nor a
  parameter the function binds again. The files defining such functions are checked again knowing
  those types, then the files calling them, knowing what they now return;
- with `--unsafe-fixes`, what's computed from a parameter pytest gives a test (a function named
  `test...`) or a fixture. One named as a fixture: its module's own, else the one in the
  `conftest.py` of the nearest package above it, else in a `conftest.py` outside any package, the
  file's directory's (or its top package's) then each one's above (the CLI only), typed by the
  fixture's declared return or the one its `return`s give (its declared return alone, in one of
  several `conftest.py`s outside a package), a generator's by what it yields (`Iterator[Frame]`
  gives a `Frame`), its class imported for type checking as another file's type is, with its
  members; else pytest's own, read from pytest as installed where a checked file imports it
  (`capsys` is a `pytest.CaptureFixture[str]`, `caplog.text` a `str`, and `capsys.readouterr().out`
  a `str`: an attribute read off a call whose own type no file can name, pytest's private
  `CaptureResult`), and its `tmp_path`, a `Path`, anywhere. And one `@pytest.mark.parametrize` gives
  literals of one type (`"n, s"` with `[(1, "a"), (2, "b")]`): on the function itself, names and
  cases written out, or on its class, for each method directly in it. A fixture's `request.param` is
  typed the same way by its decorator's `params` (`@pytest.fixture(params=[1, 2])`: an `int`), and
  so is the fixture's value where it returns that. A name bound to a call whose type no file can
  name types what's read of it, until it's bound again (`both = capsys.readouterr()`, then
  `both.out`). `def test_copy(float_frame)` types `result = float_frame.copy()`. A guess
  (`fixture`), since a plugin's fixture of the name, or a `conftest.py` out of the checked files,
  may be the one pytest takes; not a parameter the test annotates or binds again, nor any for a test
  file whose name another checked file has (a module's name says nothing of where it is);
- with `--unsafe-fixes`, an empty container (`[]`, `{}`, `set()`, `list()`, `dict()`) the function
  then only adds to, every addition typed alike (`append`, `insert`, `add`, `setdefault`,
  `x[k] = v`; `extend` and `update` with one argument, by its elements, or a `dict`'s keys and
  values): `list[T]`, `set[T]` or `dict[K, V]`. One passed to a checked file's function, by position
  or keyword, is what the parameter there declares, a builtin container of its kind
  (`add(names, "a")`, where `def add(names: list[str], extra: str)`), with what's added to it where
  that agrees. A guess, since something else could add to it; any use that could (passing it to
  another function, a nested function) leaves it alone, as does a local bound to it
  (`alias = names`) unless every use of that local only reads it, but not one that only reads it
  (`x[0]`, `len(x)`, `sep.join(x)`, `x + more`, `[*x]`, `return x, n`). Not where a name added, or
  one in a display added (`rows.append((key, cmd))`), is one the function tests: it's narrowed
  there;
- a value computed from such: `a if c else b` when both sides agree, and `a if c else None` as
  `T | None` (not where `c` tests `a`, which it narrows); `a or b` and `a and b` with operands of
  one type, `or` dropping a `None` before its last operand (`name or "x"` is a `str` for a
  `name: str | None`), and `a or []`, `a if c else {}` by `a`'s `list` or `dict` (`a if a else []`
  is never `None`); arithmetic on builtin scalars (`n + 1`, `n / 2`, `-n`, `~n`, `"x" * n`,
  `3 * "x"`, `"%s" % n`; `n << 2`, `n | 1` and `n & mask` of integers; `**` only where its result
  can't change type, an integer's by a literal, `2 ** 32`, or a `float`'s by an integer), lists
  (`names + names`, `names * 2`), tuples (`pair + (n,)` lists both sides' parts, up to `max-length`;
  `row * 2` is a `tuple[T, ...]`), and a `set`'s `|`, `&`, `-` and `^` or a `dict`'s `|` with
  another of its type, a `dict`'s `.keys()` counting as a `set` of its keys (`allowed & d.keys()`);
  a `pathlib` path's `/` with a `str` or another path (`root / "x"`: `root`'s class); an operator
  between a standard-library class's instance and another's or a builtin's, by the first signature
  of its method (`__add__`, `__sub__`, ...) in typeshed that takes the right operand, as a type
  checker picks it: `when - start`, two `datetime`s, is a `timedelta`, `when - span` a `datetime`,
  `price * 2` a `Decimal` (not where the right operand's class is under the left's, or is a checked
  file's or an installed package's, whose reflected method may answer); a list, set or dict
  comprehension whose elements are known; `sorted` (with `key=` and `reverse=` or not), `list`,
  `set`, `frozenset` or `tuple` of something whose elements are (a generator expression's too:
  `list(str(i) for i in ns)`); and `await` of a call to one of the module's `async def`s, another
  checked file's (the CLI only), or a method's of a class of either (`await self.fetch()`, the
  class's own or its base's), or to a standard-library coroutine with one declared return
  (`line = await reader.readline()` is a `bytes`, on a receiver typed `asyncio.StreamReader`;
  `await asyncio.start_server(...)` an `asyncio.Server`), or one its arguments decide
  (`await asyncio.wait_for(fetch(url), 5)`) or its generic class's receiver does
  (`await queue.get()` on an `asyncio.Queue[Item]`), or of anything typed a future or a task
  (`await asyncio.gather(a(), b())` is a `tuple[A, B]`, as `await task` is what `task` holds). An
  `async def` declaring no return is typed by its `return`s, awaited, as a plain function's call is
  (certain for a function, a guess for a method), in the module or another checked file. A
  coroutine's call passed where a parameter is an awaitable of a type variable binds it to what
  awaiting it gives: `asyncio.create_task(fetch(url))` is an `asyncio.Task[bytes]` where `fetch`
  declares `bytes`, and `asyncio.run(main())` what `main` does; `asyncio.ensure_future(fetch(url))`
  too, and given a task or a future, that one's own type.

A loop's target (LVA002) and an unpacking's names (LVA001) are declared instead, on a line of their
own before the statement: `for k, v in ages.items():` with `ages: dict[str, int]` gets `k: str` and
`v: int` above it. The target's type comes from what's iterated: a `range`, `enumerate` and `zip` of
known things, `map(f, xs)` (what `f` returns: a fixed-return builtin, or a function declaring its
return), `iter(xs)`, a generator expression (not one whose condition may narrow a union), a
mapping's `.keys()`/`.values()`/`.items()` (`dict[K, V]`, `Mapping[K, V]`, `OrderedDict`,
`defaultdict`, `MappingProxyType`, ...), any container whose type is known, a tuple whose parts
agree (`for name in ("a", "b")`), an `Iterable[T]`, `Iterator[T]` or `Generator[T, ...]` (a
generator function's call included), or a standard-library class's instance, by its `__iter__` in
typeshed (its `__next__`, where that returns `Self`): `for line in open(path)` declares `line: str`,
a loop over an `itertools.chain[int]` or a `collections.deque[int]` an `int`, over a
`tarfile.TarFile` a `tarfile.TarInfo`, over `os.walk(top)` a `str` and two `list[str]`s where `top`
is a `str` or a `pathlib` path (`bytes`, where it's a `bytes`); what's built from one too
(`list(file)`, a comprehension). A loop over an `X | None` binds what one over the `X` does (`None`
has no elements), and one over a name holding an `enumerate[T]`, `zip[T]`, `map[T]` or `reversed[T]`
what that yields. `enumerate` and `zip` type each part of the target on its own:
`for i, x in enumerate(xs)` declares `i: int` whatever `xs` is, and a guess about `xs` makes only
`x`'s fix one. Keywords that don't change what they yield are allowed (`enumerate`'s `start=`,
`zip`'s `strict=`, `sorted`'s `key=` and `reverse=`); a starred argument (`zip(*rows)`) isn't.

An unpacking's names are typed one by one. A display of as many values gives each name its own
value's type, as a plain assignment would (`a, b = x, 1` declares `b: int` whatever `x` is), every
value read before any name is bound (`a, b = b, a`). Any other value's type is split: a tuple's part
by part (`a, b = pair`, `pair: tuple[int, str]`), anything else's elements one each
(`a, b = s.split(",")` are `str`s, `q, r = divmod(n, 2)` `int`s, `i, j = range(2)`). A starred name
is a `list` of what's left for it, where that's of one type: `first, *rest = names` declares
`rest: list[str]`. A call whose declared return is a tuple with a vague part
(`tuple[Row, dict[str, Any]]`), which types no call whole, still declares the names whose parts
aren't vague (`row, extra = load()` declares `row: Row`): a function's or a method's, the module's
own or, with the CLI, another checked file's. A value typed as a `NamedTuple` class is split by its
fields, in order (`globalns, localns = resolver.namespaces`): a class defined once, directly under
`NamedTuple` alone, with two fields or more. So is one typed as an alias of a tuple
(`Pair: TypeAlias = tuple[int, str]`, `Pair = tuple[int, str]`, `type Pair = tuple[int, str]`) at
its module's top level, bound once there and generic in nothing. Either in the module or (with the
CLI) another checked file, imported, reached through a module the file imports (`shapes.Pair`), or
named by a type written for it, which it needn't import itself. A part vaguer than `vague` allows
gives its name no fix.

A `:=`'s name can't be annotated where it's bound: it's declared before its statement too, typed as
a plain assignment's name is (`if (m := pattern.match(s)) is not None:` gets
`m: re.Match[str] | None` above it), before the `if` for one in an `elif`. Not one inside a
comprehension, whose value may read the comprehension's names, nor where a line can't go before the
statement: in a definition's decorators or defaults, or a statement that doesn't start its line.

An annotation in quotes, or a quoted part of one, is read as its text: `xs: "list[Node]"` and
`xs: list["Node"]` both type `xs[0]` as a `Node`. Not a `Literal`'s strings or an `Annotated`'s
metadata, which are values. In a module body, where an annotation is evaluated, a fix naming what
the module binds only further down, or imports under an `if` on a flag (`if TYPE_CHECKING:`,
`if MYPY_CHECK_RUNNING:`), is quoted (`first: "Node" = xs[0]`), unless the module has
`from __future__ import annotations`. In any scope of such a module, a fix the project's oldest
Python (`min-python`) doesn't read as a type is quoted too: a union by `|` before 3.10
(`found: "re.Match[str] | None"`), a subscript before 3.9 (`names: "list[str]"`).

A `with` statement's target is declared before it too, as what the context manager's `__enter__`
returns: `with zipfile.ZipFile(path) as z:` gets `z: zipfile.ZipFile` (a standard-library manager
that returns itself gives its own type, type arguments included: a `subprocess.Popen[str]`),
`with tempfile.TemporaryDirectory() as d:` a `str`, a class's of the module's or of an installed
package's what its `__enter__` declares, and a call to one of the module's functions that
`@contextmanager` makes a manager what it declares it yields (`Iterator[T]`'s `T`). A method of the
module's classes that `@contextmanager` makes one types its call the same way, on a receiver whose
type is known (`with self.defs.entry(key) as found:`). One declaring no return gives what its
`yield`s do, each a statement of its own and all of one type (a method's as a guess). Another
checked file's function is entered the same way (the CLI only), by what it declares or, once its
file is checked, yields; and its class's `__enter__` returning `self` gives the class, as a guess. A
target that unpacks is split as an unpacking's value is (`with defs.entry(key) as (ref, schema):`),
a vague part's name left alone. `with open(path, "rb") as f:` declares `f: io.BufferedReader`, by
its mode, as `os.fdopen(fd, "rb")` does; `tokenize.open` gives a `typing.TextIO`, and `gzip.open`,
`bz2.open` and `lzma.open` an `io.TextIOWrapper` in a text mode; and `shelve.open` a
`shelve.Shelf[Any]`, written from `vague` 0 (its keys are `str`s at any level). An `async with`'s
target is typed by a standard-library manager's `__aenter__`
(`async with asyncio.TaskGroup() as group:`), where that has one declared return; no other
manager's, and not split over an unpacking.

A standard-library manager its arguments decide is matched as any such call is: a constructor whose
`__init__` overloads declare the instance (`subprocess.Popen(cmd, text=True)` is a
`subprocess.Popen[str]`, `warnings.catch_warnings(record=True)` gives a
`list[warnings.WarningMessage]`), and a test case's `self.assertRaises(ValueError)`, whose class
argument binds what it catches: `cm: _AssertRaisesContext[ValueError]`, then `cm.exception` a
`ValueError`; `self.assertLogs(...)` binds its `_LoggingWatcher`, whose `output` is a `list[str]`.
Those classes, `_AssertWarnsContext` and `tempfile.NamedTemporaryFile`'s `_TemporaryFileWrapper` are
private in typeshed and at run time, with no public name: they're written as they are (imported from
`unittest.case` or `unittest._log`, where the module doesn't import it), which a checker reporting
private names' use will say. `tarfile.open` gives a `tarfile.TarFile`.

A type the module can't name yet gets an import. One it already has is reused (with `import io`,
`io.BufferedReader`); otherwise `from io import BufferedReader` is added after the module's
docstring and its leading imports (below a shebang or coding line when it has neither), or
`import io` if `BufferedReader` is a name the module binds. A type the module imports under a
top-level `if TYPE_CHECKING:` is named by that import (quoted in a module body, as above). A
standard-library type's import goes under `if TYPE_CHECKING:` only for a module nothing but the
module's functions import (`import decimal` in a function's body): it may not be there to import
when the module is. A class of a module only some platforms have, imported that way (`import pwd`,
`import winreg`), is no fix: a type checker on another platform finds no such class.

An installed package that declares its types (a `py.typed` package, its stubs first; a stub package,
`pkg-stubs`; a lone `mod.pyi`) is read the same way for the calls into it, and never fixed: found on
this Python's path and the active virtual environment's (`VIRTUAL_ENV`), as the import system would
(an untyped copy earlier on the path shadows a typed one later), with the modules it re-exports
from, its private twin's too (`pytest`'s, from `_pytest`). `pydantic_core.to_json(x)` is a `bytes`.
A type it names is written through a public module re-exporting it that the file imports
(`typed.Thing`, after `import typed`), else imported from one (`from typed import Thing`, not
`typed._types`; a module exports what `__all__` lists, or else what it defines and imports as
itself, `from m import x as x`), or not written; and one of its generic classes is never written
bare (`np.ndarray`). A class a module the file imports re-exports has its members there
(`pytest.LogCaptureFixture`'s `text`, `pkg.Row`'s).

A checked file's function defined with `@overload` is matched the same way, in the file defining it
and in those importing it: `load(path, raw=True)` is a `bytes` where `raw: Literal[True]` returns
one. What a parameter takes is read as below. One typed as nothing but checked files' classes
(`frame: DataFrame`), or as an iterable of them (`objs: Iterable[DataFrame]`, beside a mapping or
`None`), takes an argument by its class's bases, through the checked files: `concat([df, df])` is a
`DataFrame`, where another overload takes `Series`; a class under a base that can't be followed
(another package's) decides nothing. An alias, a protocol or a type variable a checked file declares
is read as an installed package's is (`axis: Axis`, by what `Axis` stands for). A class's methods
defined with `@overload` are matched on a receiver typed as the class (`frame.get("k")`), and a
function called through its module however that's imported (`shapes.concat(...)` after
`from pkg import shapes`). Each return is written as another checked file's type is: none of the
function's calls is typed if one of its overloads declares no return, or returns a type variable or
a generic class without its arguments.

An installed package's functions whose arguments decide their type (overloads, or a return naming a
type variable) are matched as the standard library's are: `np.empty(n, dtype=np.float64)` is an
`np.ndarray[tuple[int], np.dtype[np.float64]]` with numpy 2.5's stubs. What each parameter takes is
read from its annotation through the package's aliases, type variables and protocols; a
standard-library class it names (`SupportsIndex`) by the `scalars` table; and a class passed as the
argument binds a `type[T]` parameter's `T`, as does an alias of one (`np.int32`). A builtin
container argument is taken by its elements where the parameter says what they must be
(`tuple[int, ...]`), and binds a bounded type variable its bound takes (numpy's shape: `(n, 2)` is a
`tuple[int, int]`). An installed class's methods are matched the same way, on a receiver whose type
is known: its type arguments bind the class's type parameters, `Self` is the receiver's type, and a
method its class inherits is its base's. A method declaring its `self`
(`def sum(self: NDArray[ScalarT]) -> ScalarT`) is matched against the receiver's type: argument by
argument, a type variable bound to what's there and checked against its bound, and a class by the
installed classes' ancestors (`np.float64` is an `inexact`); a receiver that certainly isn't one
passes the signature over, one that may be leaves it open. A receiver typed through a public alias
of the class (`npt.NDArray[np.float64]`) is matched as what the alias stands for
(`np.ndarray[tuple[Any, ...], np.dtype[np.float64]]`), and has the class's methods: a type variable
bound only to what the alias itself writes is left unbound, and `Self` is the receiver as written. A
private alias in the return is written as what it stands for; a public one by its public path
(`npt.NDArray[np.float64]`).

A type another checked file declares (`get_handle() -> IOHandles[str]`) names what that file imports
or defines; a name the calling file doesn't have is written through the module that defines it, if
the file imports that module to run (`core_schema.CoreSchema`, after
`from pydantic_core import core_schema`; not through a name the file binds as a value somewhere),
else imported where the type's file has it from, under `if TYPE_CHECKING:` (into the module's first
top-level one, or a new one after its imports, with `from typing import TYPE_CHECKING` if it must
be), so the import can't make an import cycle at run time. A name the file already imports, under
any name and even for type checking alone, is reused; a module-level annotation using one imported
for type checking alone is quoted (`top: "IOHandles[str]" = get_handle()`), unless the module has
`from __future__ import annotations`. A generic class another file defines is never written bare.

A chained assignment's names (`i = j = 0`), which can't be annotated where they're bound, are each
declared before it (`i: int`), as an unpacking's are; not as `Final`, which needs its value.

An added import never binds a name the module binds anywhere, or a builtin's; with no name free,
there's no fix. In a notebook, which has no import block, such a fix is reported but not applied.

A fix is never vaguer than `vague` (`--vague LEVEL`) lets an annotation be, which LVA005 reports
past: by default (-1) it has no `Any`, `object` or generic without its parameters in it. At 0 it may
have one, inside a type that says the rest (`dict[str, Any]`, `tuple[Row, Any]`); at a level N from
1, N + 1 of them (`tuple[Any, Any]` at 1), or one alone (`Any`, `Any | None`). Every source answers
to it: a declared return (a function's, a method's, another checked file's), a copy, a loop's
element, `typing.cast`, a callable's call and a type checker's hint. A type vaguer than that is
still its name's, with no fix: what's read of it is typed (`fields = schema.fields()`, declared a
`dict[str, Any]`, stays as it is, and `for name in fields` declares `name: str`), by a declared
return (a property's too), `typing.cast` or a callable's call. To a later binding's fix and to
LVA009 it's a value of no known type. What only a vague type describes is typed from 1, `Any`
imported from `typing` if it must be: `getattr(obj, name)` is an `Any`, with a default of a known
type `T` an `Any | T`; and a standard-library function declared to return `Any` alone (`json.loads`,
`pickle.loads`, `ast.literal_eval`) an `Any`; and `object()` is an `object`.

LVA012 (opt-in) offers `Final`: around the annotation there (`x: int = 1` becomes
`x: Final[int] = 1`), with LVA001's type for an unannotated name (whose own fix it then replaces),
or bare (`x: Final = f()`) when there's none.

A loop whose target is typed only by `# type: T` (LVA003) gets `name: T` declared before it and the
comment dropped (a type checker would see the name declared twice), when its header is on one line.
A name annotated again with the type it already has (LVA007) loses the repeat: `x: int = 2` becomes
`x = 2` (not a bare `x: int`, and never in a class body).

With `--unsafe-fixes`, LVA008 and LVA010 are fixed too, by rewriting the annotation (`total: float`
only ever given `int`s becomes `total: int`): a guess, since a declared type can be wider on
purpose.

## What a type checker sees

A fix is only as certain as a type checker would find it (`tests/corpus/corpus_suite.py --types`
runs the corpus packages' own checkers after `--fix`), so where a checker sees the value otherwise
than the fix says, the fix is changed, made a guess, or not offered:

- a variable in a class's body is held to what a class above it declares: annotated there as another
  type (`limit: int | None`, then `limit = 3` below), or a builtin base's own (`errno` under
  `OSError`), it isn't typed by its value, across the checked files; and one a `unittest` test case
  declares itself is that type where its value is of it, `None` too (`maxDiff = 80` and
  `maxDiff = None` are an `int | None`), under any base no checked file defines but a builtin one;
- a name bound again later must take every value: `x = 1` then `x = None` declares `x: int | None`
  on a line of its own before the first binding (annotated there, mypy wouldn't narrow it to the
  `int` it's bound to), and `total = 0` then `total += 0.5` declares `total: float` (fix kind
  `rebound`); another type that doesn't fit (`x = 1` then `x = "a"`, a class and its base) leaves it
  untyped. A later value whose type isn't known may be anything, which makes the fix a guess, and no
  fix where it's bound in another arm of the first one's `if`, `try` or `match` (`dtype = "None"`,
  `else: dtype = self.categories.dtype`): only one arm runs, and a checker that knows the other's
  type holds it to the first's. A class or alias the file spells two ways is one type (`CoreSchema`
  and `core_schema.CoreSchema`, after importing the name and its module; the CLI only, whose index
  says where each is defined);
- after it's bound again, a name is what it was bound to: certain where that's a member of its
  declared union (`int | None`, then `1`), which every checker narrows it to; a guess otherwise, and
  where it was first bound to a value of no known type (`levels = index.multi()`, then
  `levels = ["a"]`: `for lvl in levels` declares `lvl: str` as a guess); bound again to a value
  whose type is a guess, it's that type from there on, as a guess (`config = config or Config()`,
  then `config.limit`). One of no known type before a branch that binds it to a known one (a
  parameter, in `if flag: x = float(x)`) has none past the branch, where it may hold either; nor has
  one an arm of an `if`, a `try` or a `match` leaves with no known type, whatever another arm binds
  it to (`levels = index.multi()` under an `if`, `levels = ["a"]` under its `else`), unless that arm
  leaves (`return`, `raise`, ...). A union bound to a value of no known type is narrowed to it: the
  name has no type until its branch ends, and is the union again past it, as a guess;
- a guess isn't offered where, once declared, it makes an error of what the function goes on to do
  with the name, by an unannotated function's `return`s, which a checker took for anything: a union
  of which an attribute or an item is taken where no test narrows it (`opt = registered(key)`, then
  `opt.cb`), and a class of the module's by such `return`s of which an attribute it hasn't is taken
  (`cfg.verbose`, of a class whose attributes are set from outside it; only a class whose attributes
  are all in sight: undecorated, under the module's own classes alone, with no `__getattr__` or
  `setattr`); a name whose comparison is used as more than a `bool` (`(when == index).any()`, an
  operand of `&`, `|`, `^` or `~`: its class compares element by element, whatever its stubs say); a
  `bytes` formatted into a string (`f"{raw}"`, `"{}".format(raw)`, `"%s" % raw`, which mypy reports;
  not `f"{raw!r}"`); and a name stored, or an item of it, in an attribute the function stores
  something else in too (`self.proc = buf[0:n]`, then `self.proc = decode(self.proc)`: the attribute
  then has the name's type);
- a union isn't split over several names (`for name, length in parts`, of `[["prefix", 24], ...]`, a
  `list[list[str | int]]`): each is by position as often as not; a tuple of that many says which is
  which, and is;
- an unannotated function's `return` of a class its own body imports or defines types no call: no
  caller can name it;
- an instance attribute a class above also stores (`self.name = name` under a base's
  `self.name = array.name`) is typed there, to a checker, not by the subclass's assignments;
- a value typed the same whatever a guessed name in it is stays certain: `os.path.join(root, "x")`
  is a `str` by its literal, a guessed `root` or not; so does one typed whatever its parts are
  (`x.kind is None`, an f-string);
- a side of `a if c else None`, an operand of `a or b`, or `type(x)`'s argument, read as its
  declared type (`x`, `self.x`, `d[k]`), makes a guess where the function tests it, and no fix where
  its type is a union of two types or more;
- an annotation naming a parameter or a local of its own function, or the name it annotates, would
  mean that variable there: not offered (`text: str = ""` under a parameter `str`);
- a copy, attribute or subscript of a union, or of anything the function tests (`isinstance(x, C)`,
  `x is None`, `is_c(x)`, an `assert`, a `match`), may be narrowed where it's read: a guess; so is a
  comprehension of a union with a condition (`[c for c in cs if isinstance(c, Column)]`), whose
  element, or a `dict`'s key or value, is the class a condition (or an operand of its `and`) checks
  it for, with no fix where it's checked any other way (`not isinstance(c, Column)`, under an `or`)
  or kept in a display (`(name, c)`). One of an `X | None` (or a filtered comprehension over one)
  isn't offered where its function tests or stores what's read, or what that's read of (`self.conn`,
  for `self.conn.pool`), anywhere: code nearly always checks it for `None` first, and a checker then
  takes it for the `X`. Where nothing does, it has the type it's declared, a guess
  (`conn: Connection | None = self.conn`). Nor is a bare `None` offered; nor is a read where a test
  around it narrows it: in an `if`'s or `while`'s branch, a `match` case, or the rest of a block
  after an `assert` or an `if` that always leaves (`return`, `raise`, ...), for a check
  (`isinstance`, a `TypeGuard`, a `match`) whatever its type, and for a truth test or comparison
  when it's a union. A type alias of a union (`Key = Union[int, str]`,
  `Maybe: TypeAlias = int | None`, the module's own or another checked file's, bound once at its top
  level) is narrowed as the union it names, by a test or an assignment, and one of an `X | None`
  isn't offered; a plain read of one stays certain, written as the alias;
- an ALL_CAPS module-level name bound to a literal is a constant to pyright, which keeps its
  `Literal` type: `MODE = "r"`'s `str` would widen it. Passed to a call (where a parameter may take
  only some values), it's declared `MODE: Final = "r"`, which keeps the `Literal`: a guess, as
  something may rebind it, and not offered where the module binds it again;
- `self`, and a method declared to return `Self` called on `self` or `cls`, is `Self`, not its class
  (in a subclass, the class isn't `Self`), as is what `cls()`, `type(self)()` or `cls.__new__(cls)`
  constructs, and a standard-library function's call given `self` that returns its class
  (`copy.copy(self)`), and `type(self)` there a `type[Self]`: written as the module already imports
  `Self` (`typing.Self` is Python 3.11's, so no import is added), and not offered without one; a
  `Self` later bound to anything else isn't offered either;
- a generic class is never written bare (`list[Box]`, as `[self]` in `Box` would be; `Box()` guessed
  to construct one): the module's own, another checked file's, or the standard library's
  (`logging.StreamHandler()`), unless every type parameter it has has a default
  (`io.BufferedReader`);
- a declared return that names a type variable, the module's own, one it imports from another
  checked file (`from ._typing import T`, under `if TYPE_CHECKING:` too) or `typing.AnyStr`, depends
  on the arguments: its calls aren't typed;
- a one-parameter generic written with a trailing comma (`list[int,]`, as a formatter splits a long
  one) has the element it would without;
- an alias its module assigns in two arms of an `if` (`if MYPY: X = A`, `else: X = B`) is a variable
  to a type checker, unless it decides the `if` itself (`sys.version_info`, `TYPE_CHECKING`, a
  constant): a type naming one isn't written in another file.

## A type checker's types (`--infer-with`)

`--infer-with basedpyright` (or `ty`, or `pyrefly`, or several: `basedpyright,ty,pyrefly`) asks that
type checker what it infers, for the bindings `--fix` can't type itself. It starts the checker's
language server (`basedpyright-langserver`, `ty server` or `pyrefly lsp`, on `PATH` or beside the
Python running constricter), asks it for the inlay hints over each file, and turns a variable's hint
into a fix. Every such fix is a guess (fix kind `checker`), applied with `--unsafe-fixes`: a hint is
the type of the value where the name is bound, which a later binding can widen, and the checker can
be wrong about what the code means. Its guesses feed the rest of the scope as `--fix`'s own do (a
copy of a hinted local is typed too, as a guess).

A hint is used only as an annotation the file can hold:

- `Literal[...]` is widened to its values' types (`Literal[1] | None` is `int | None`,
  `Literal[Color.RED]` is `Color`), and `LiteralString` to `str`;
- ty's own spellings are read: a class object (`<class 'Point'>`) is `type[Point]`, a type variable
  printed with its scope (`Model@create_model`) the variable, and an intersection with a truthiness
  (`str & ~AlwaysFalsy`) its other member; any other intersection is dropped. An unpacked tuple
  (`tuple[str, *tuple[str, ...]]`, Python 3.11's syntax) is kept where the project's oldest Python
  parses it: `min-python` (`--min-python`), which defaults to the lower bound of the nearest
  `pyproject.toml`'s `requires-python`. Where it's older, or not known (the plugins), it's written
  with `Unpack` (`tuple[str, Unpack[tuple[str, ...]]]`, a level deeper to LVA006) if the module
  imports it from `typing` or `typing_extensions`, and dropped if it doesn't;
- a type variable of the module's is a fix only where the function's signature, or its class's
  bases, name it: anywhere else it's unbound;
- anything vague (`Any`, `list[Unknown]`), not an annotation (`Module("os")`, a signature), as deep
  as LVA006 reports or as long a tuple as LVA011 does, or a bare `None`, is dropped;
- every name in it must be a builtin, a name the module binds at its top level (before the binding,
  in a module body), a class it imports under `if TYPE_CHECKING:`, a class the checker prints bare
  that `--fix` can import (`collections.abc`'s, `Path`, `deque`, `Decimal`, `UUID`, ...: one is
  added as other fixes add theirs), or a class the hint's own edits import. Otherwise nothing says
  what the name means, and the hint is dropped;
- a generic class without its arguments is dropped (a checker prints one so when it doesn't know
  them), as is a special form alone (`type[Generic]`, `Annotated`);
- a union (`Option | None`, `Series | bool`) is a fix only for a name its function narrows somewhere
  (`if opt is None`, `if opt`, `isinstance`): untested, the code uses it as one member (`opt.cb`),
  which the union declared would make an error; a union inside the hint (`dict[str, int | bytes]`, a
  mixed container's) is dropped anywhere, since no test of the name narrows its elements;
- a `Literal` isn't widened inside a class's own arguments (`Reader[Literal["frame"]]`), which may
  be bound to the literals: the hint is dropped. A builtin's or `collections.abc`'s are;
- a name its function returns has no fix where the function's signature says `Self`: the checker
  hints the class;
- a name bound again later has no fix unless every later value is known to fit the hint: the hint is
  the first value's type alone (`n = values.mean()`, hinted `np.float64`, then `n = len(values)`);
- `TypeAlias`, which a checker hints an alias's assignment as, declares a module body's alias
  written as a subscript or a union (`Json: TypeAlias = dict[str, "Json"] | str`): named as the
  module's imports can (`typing`'s or `typing_extensions`'s), else imported from `typing`. Never a
  bare class's alias (`Alias = Class`), which declared one loses the class's type parameters, nor a
  function's local.

A hint carries the edits an editor applies to accept it: the annotation, and an import for each
class in it the file doesn't have, which basedpyright, ty and pyrefly send as a statement to add
(`from shapes import Shape`) or as a name for a `from` import the file has (`, Shape`). `--fix`
reads them: the class is written through an import the module runs if it has one (`shapes.Shape`,
after `import shapes`), else imported under `if TYPE_CHECKING:` as another checked file's type is, a
module body's annotation quoted. Never by an import that runs: the checker's Python may have a class
the project's oldest doesn't. The first hint to import a name decides what it means in the file: a
later one importing it from elsewhere is dropped. Where what a hint shows names something the file
can't, the annotation as its edit spells it is judged too (`things.Thing[str]`, through
`import things`), unless it writes a generic under another name than the hint shows: ty's edit for a
generic alias (`NDArray[float64]`) is the class it stands for with the alias's arguments
(`np.ndarray[np.float64]`), which aren't the class's. pyrefly's hint for a loop's target or an
unpacking's names has no edits: its label says which file defines each class, and the import is from
the module that file is (an installed package's, a stub pyrefly bundles, or a checked file's).

A hint is text, and a name in it needn't be a type (basedpyright shows a value that is a module by
the module's name): one an edit imports, or the file imports under `if TYPE_CHECKING:`, is taken
only for a class or a type alias a checked file or an installed package that declares its types
defines (in a public module of the package's: not `numpy._core`), or a class the standard-library
tables have in a public module (not `_collections_abc`'s `dict_keys`). A type alias is a name
annotated `TypeAlias`, bound to a subscript or a union at its module's top level (under an `if` or
`try` too), or a `type` statement's; one that takes type arguments is never written bare. A bare
class's alias, or a class of a package that isn't checked, is left out.

With several checkers, each name takes the first checker's hint, in the order they're named, that
passes the checks above: one checker's `Unknown` falls back to the next's type. They're asked at the
same time, each over its own servers. A checker gets up to four servers, as `--jobs` allows, one per
32 files (more only repeat each other's work: SQLAlchemy's hints took 20s with one basedpyright
server, 11s with four, 18s with sixteen). `ty` and pyrefly work in parallel themselves, and are
still quicker shared out: a hinted check of pandas takes 36s with one `ty` server and 21s with four,
132s with one of pyrefly's and 32s with four. Free servers take the files a few at a time, the
biggest first, each always with its next few asked before its last few are answered. A server's
memory is counted by its checker's own measure: each of basedpyright's holds its own copy of the
program it checks (about 1.2 GB for SQLAlchemy, 3.4 GB for pandas), while `ty`'s and pyrefly's each
hold what they're asked about (pandas: 1.2 GB in one `ty` server and 2.5 GB in four, 2.8 GB and 4.2
GB for pyrefly). `--infer-memory GB` (`infer-memory`) caps what a checker's servers use together: by
default 8 GB, or half the memory available if that's less; set, never more than is available. One
server a checker always gets.

Each server runs behind a small guard process, which passes its input and output through and kills
it (and anything it started: a venv's `basedpyright-langserver` starts `node`) once constricter has
gone, however it went (interrupted, terminated, or killed outright): no server outlives the run,
even one stuck waiting on constricter.

`--fix` repeats with `--infer-with`: a file a round changed is sent to the checker again and fixed
again, as its new annotations change what the checker infers, until a round changes nothing (four at
most). `--diff` shows the first round. A checker that isn't installed, fails, or says nothing at all
for two minutes (it reports its progress as it works: pandas' first answer took basedpyright seven
minutes) stops the run with an error; a notebook, standard input and a file that can't be decoded
aren't sent to it. The checker's own configuration (its `[tool.basedpyright]`, `ty.toml` or
`pyrefly.toml`, its environment) decides what it infers: pyrefly types what an unannotated function
returns only where its configuration has it check and infer one (`check-unannotated-defs = true`,
`infer-return-types = "checked"`), which without a configuration it doesn't.

It touches no class body but a plain class's (a dataclass would gain a field), and it leaves what it
can't fix reported. The standard library and third-party packages are out of reach.

`--show-fixes` lists, after the report, each fix and how its value decided it (for `b = s.strip()`:
`str`, from `str.strip`'s fixed return type), marking the guesses `--unsafe-fixes` would add, or
`--likely`; `--format=json` always carries the same as a `fix` object (`annotation`, `reason`,
`unsafe`, `likely`, and `imports`: the import statements the fix adds, those for type checking alone
too) on each result. With `--fix`, `--show-fixes` lists the fixes made too, after what's left:
`fixed 'b'` as text, and in `--format=json` an entry whose `fixed` is true. Each is on the line it
had before any fix, whichever round of `--fix` made it.

The type hierarchy LVA008–LVA010 compare through is the numeric tower (`bool` < `int` < `float` <
`complex`) plus the classes a module defines, under the bases they name.
`[tool.constricter.narrower]` (or the plugins' `narrower` option, as `B=A, int=`) replaces what
those say for each type it names, and vouches for the types it names: an imported type the rules
would never compare otherwise is compared.

## A traced run's types (`--infer-from`)

What a run binds a name to says what the source doesn't: most bindings with no fix are in functions
with no annotations, computed from parameters nothing types. Those are the ones it types.

```bash
python -m constricter.trace -m pytest          # or a script: writes constricter-trace.json
constricter --fix --unsafe-fixes --infer-from constricter-trace.json .
```

`python -m constricter.trace [--output FILE] [--root DIR] (-m MODULE | SCRIPT) [ARG ...]` runs the
module or script as `python` would, and each time a statement of a function defined under DIR
(default: the working directory; nothing installed there) ends, notes the type of each name it binds
(an assignment's, a loop's or a `with`'s targets, a `:=`'s): a builtin scalar, a builtin container
or one of `collections`' by its first 20 elements' types (up to three, two levels deep), a tuple by
its parts' one type or part by part (up to four), a class as `type[C]`, anything else by its class
(`Outer.Inner`, for one defined in another). A generic class's instance has its arguments where it
was made with them (`Box[int]()`), or where the class is a builtin container of its own type
variables (`class Stack(list[T])`), by its elements; bare, it has no fix. A mock, a class defined in
a function, and a container of more types or deeper have no spelling, and leave their name untyped;
an empty container says nothing, nor does a statement an exception ends. A statement that ends 20
times with nothing new is no longer looked at, nor a function that returns 20 times so. Lines are
followed by `sys.monitoring`, or by `sys.settrace` before Python 3.12. A pytest process the run
starts (pytest-xdist's workers, with `-n`) records itself the same way, and the run's trace has
theirs: the run adds `constricter.trace` to `PYTEST_PLUGINS`, so constricter must be importable
where such a process runs. No other child process is recorded.

`--infer-from FILE` (`infer-from` in `[tool.constricter]`, relative to the `pyproject.toml`) takes
those types as a type checker's hints are taken, after the checkers' own where `--infer-with` is
given too: for the bindings `--fix` can't type itself, each a guess (fix kind `traced`), judged as a
hint is (not vague, not too deep, no generic class bare, every name one the file can use). A class
the file doesn't name is imported under `if TYPE_CHECKING:`, where the checked files or an installed
package's public module define it. Up to three types seen for one name are their union, which is a
fix only where the function tests the name, as a checker's union is.

Only a local no annotation types gets one: a name an assignment or a `for` loop binds to a value
taken from a parameter no checker types (`row = rows[0].load()`, `made = make(n)`,
`for row in rows:`): an unannotated one (not `self` or `cls`, which the class types) with no default
but `None`, that its function doesn't bind again, test by a call (`isinstance(rows, list)`) or
match. Or from an attribute of `self` that a class with no base stores nothing else in
(`conn = self.conn`, where every store is a plain `self.conn = conn` of such a parameter and the
class's body doesn't bind it: a checker types the attribute by what's stored). Anything else a type
checker may type wider than the run saw (an `X | None` that was never `None`, a base class, a
`TypedDict` seen as a `dict[str, str]`), and the narrower annotation would be an error: hints for
every local brought 32 new basedpyright errors with 127 fixes on pydantic, and none with none under
this rule. A name bound more than once, or in a loop, has every type its bindings held, where each
is such a binding and the run reached it: one it never reached may hold anything. A file is matched
by its SHA-256: one edited since the run has no types (`--fix`'s own second round, for one), and a
copy of it has them all.

What the run saw can still be narrower than what the code means (a subclass, an `int` where a
`float` may come, a `dict[str, Series]` that later takes another value): a guess, like the rest. And
a name typed at last is checked at last. With each package's tests traced
(`tests/corpus/corpus_suite.py --types --trace`), its own type checkers find, past what
`--fix --unsafe-fixes` alone brings: on SQLAlchemy 6 errors with 179 fixes, on pandas one with 1,443
(an ignore no longer needed), on pydantic none with one; none where a traced name is bound, each at
a later use of it (`index.table`, a `Table | None`, passed where a `FromClause` is declared).
Django, which has no type checker, is traced through `tests/runtests.py --parallel=1`: 462 fixes,
and its tests the same after. On pandas's `tests/frame/methods`, which its checkers pass over,
basedpyright finds 33 with 148 fixes (7% more), the same way (`df.join(other, how="foo")`, in a test
of that error).

## Fix levels

Each fix names the mechanisms that decided it, parts included (`[1, 2]` is a `container` of
`literal`s), by a stable id: `--show-fixes` prints them after the reason (`[container, literal]`),
and `--format=json`'s `fix` object has them as `kinds`.

| Id              | Decided by                                                                                |
| --------------- | ----------------------------------------------------------------------------------------- |
| `literal`       | a literal, an f-string, `not x`, or `x in y` or `x is y`                                  |
| `container`     | a list, set, tuple or dict display whose elements' types agree                            |
| `joined`        | a list, set or dict display whose elements' types differ, as their union (a guess)        |
| `copy`          | a copy of a local whose type is known                                                     |
| `subscript`     | a subscript of a container whose type is known                                            |
| `attribute`     | an attribute of a class the module (or another checked file) defines                      |
| `method`        | a method with a fixed or declared return type, on a value whose type is known             |
| `builtin`       | a builtin with a fixed return type (`len`, `str`), or one its arguments decide (`min`)    |
| `call`          | a function, classmethod or staticmethod that declares its return type                     |
| `constructor`   | a call to a capitalised name, taken to construct one (a guess)                            |
| `conditional`   | both sides of `a if c else b`, or one side and `None`                                     |
| `boolean`       | `a or b` or `a and b`, its operands of one type                                           |
| `compare`       | a comparison of builtin values (`n < 3`), always a `bool`                                 |
| `arithmetic`    | arithmetic on builtin values, a `pathlib` path's `/`, a library class's operator          |
| `comprehension` | a list, set or dict comprehension's elements                                              |
| `builder`       | `sorted`, `list`, `set`, `frozenset` or `tuple` of known elements                         |
| `await`         | `await` of a checked file's `async def`, a function or a method                           |
| `loop`          | what a loop (or `sorted`, `list`, ...) iterates over                                      |
| `unpack`        | an unpacking, each name by its own value, or the value's type split over them             |
| `narrow`        | LVA008's or LVA010's narrower annotation (a guess)                                        |
| `cast`          | `typing.cast(T, x)`: its `T`                                                              |
| `comment`       | LVA003: the loop's own `# type:` comment, as a declaration                                |
| `redundant`     | LVA007: the repeated annotation, dropped                                                  |
| `stdlib`        | the standard library's functions, classes and members, from typeshed (`uuid4`)            |
| `open`          | `open(path, mode)`'s file object, by its literal mode (`io.TextIOWrapper`, ...)           |
| `final`         | LVA012's `Final`: around its annotation, or with LVA001's type (`Final[int]`)             |
| `checker`       | a type checker's inferred type, from its inlay hints (`--infer-with`; a guess)            |
| `traced`        | what a traced run bound the name to (`--infer-from`; a guess)                             |
| `rebound`       | a name later bound to a wider type: the type every value fits (`int`, then `float`)       |
| `optional`      | `x = None`, then only ever a value of one known type `T`: `T \| None`                     |
| `filled`        | an empty container, then only what the function adds to it (a guess)                      |
| `returned`      | an unannotated function's own `return`s, or a generator's `yield`s (a method's: a guess)  |
| `assigned`      | an unannotated instance attribute's every `self.x = value` in its class (a guess)         |
| `member`        | a plain class's variable, by its value in the class's body (a guess)                      |
| `alias`         | a module's type alias, a subscript or a union of types: `TypeAlias`                       |
| `callable`      | a function or a bound method bound to a name, by what its call gives                      |
| `callers`       | an unannotated parameter every call in the checked files passes one type (a guess)        |
| `fixture`       | a test's parameter, by its pytest fixture's value or its `parametrize` literals (a guess) |

The wider types `fix-widen` adds are kinds too: see [below](#wider-types-fix-widen).

A project chooses which apply, in `[tool.constricter]` or on the command line:

- `fix-select` (`--fix-select KINDS`): offer only fixes every one of whose mechanisms is listed
  (default: all);
- `fix-ignore` (`--fix-ignore KINDS`): never offer a fix any listed mechanism decided;
- `unsafe-fix-select` (`--unsafe-fix-select KINDS`): treat guesses from the listed guessing
  mechanisms (`constructor`, `narrow`) as certain, so plain `--fix` applies them, as ruff's
  `extend-safe-fixes` does. A copy of such a guess is trusted with it.

```toml
[tool.constricter]
fix-ignore = ["arithmetic"]          # never annotate from arithmetic
unsafe-fix-select = ["constructor"]  # this codebase's capitalised calls construct what they name
fix-plain-bases = ["rest_framework"]  # its classes read no annotation in a class body
```

None of them changes what's reported: an offence whose fix isn't offered is still reported, without
a fix. The defaults (every mechanism, nothing trusted) are the plain certain/guess split.

## Wider types (`fix-widen`)

Where a value has no type `--fix` can work out, or none it may write, it writes none. `fix-widen`
(`--fix-widen KINDS`) names the wider types it may write instead, each a fix kind of its own, off
unless listed (`all`: every one), and answering to `fix-ignore` and `unsafe-fix-select` as any kind
does:

| Id                   | Writes                                                                         |         |
| -------------------- | ------------------------------------------------------------------------------ | ------- |
| `untyped-parameters` | `Any` for what comes of a parameter no annotation types                        | certain |
| `empty-containers`   | `list[Any]`, `dict[Any, Any]`, `set[Any]` for an empty one nothing fills       | certain |
| `mixed-containers`   | `list[Any]`, `tuple[Any, ...]`, `dict[str, Any]` for a display of mixed things | certain |
| `unions`             | `int \| str` for a name bound to values of two or three types                  | a guess |
| `vague`              | a type vaguer than `vague` allows (`dict[str, Any]`), written anyway           | a guess |
| `untyped-calls`      | `Any` for a call of a checked file's function that declares no return          | certain |
| `unknown-calls`      | `Any` for any other call of no known type                                      | certain |

```toml
[tool.constricter]
fix-widen = ["untyped-parameters", "empty-containers"]
```

- `untyped-parameters`: `x = param` and `y = param.read()`, each on one line, where `param` has no
  annotation and no default, isn't `self`, `cls`, `*args` or `**kwargs`, and is never bound again in
  its function. `Any` there says what every checker takes the value for already; a parameter with a
  default is one a checker types by it, and is left. Whatever the name is bound to later.
- `empty-containers`: `[]`, `{}`, `list()`, `dict()` or `set()` bound to a function's name that
  nothing in sight fills (what its function adds to one types it still, as `filled` does).
- `mixed-containers`: a list, set, tuple or dict display whose elements' types differ or aren't
  known. A dict's keys are `str` where each is a string; a tuple is `tuple[Any, ...]`, whatever its
  length.
- `unions`: a name bound to values of two or three types that fit no one of them (`x = 1`, then
  `x = "a"`), declared their union on a line of its own before its first binding. Only of values
  whose types are certain, and not for a name its function changes in place (`x += more`).
- `vague`: a value whose type is known and vaguer than `vague` allows (a call declared to return a
  `dict[str, Any]`), which `--fix` otherwise never writes.

- `untyped-calls`: `x = helper()` or `x = self.load()`, awaited or not, where `--fix` has no type
  for the call and its function declares no return: a top-level function of the module's, a method
  its class or one of the class's bases in the module defines, called on `self` or `cls`, or a
  function another checked file defines, called by its name or through its module (`u.helper()`).
  `Any` there is what a checker that reads no body (mypy) takes the call for already; one that reads
  its `return`s (pyright) loses what it inferred. Not a function that's decorated (but as a static
  or class method) or defined twice, nor an `async def` called without `await`; another file's
  `async def` is `unknown-calls`'.
- `unknown-calls`: every other call `--fix` has no type for (`x = obj.method()`,
  `x = module.func()`, an imported function's). The widest of the kinds: it hides whatever a checker
  made of the call. Not a call `--fix` types and doesn't write (a `re.Match[str] | None` nothing
  narrows): a checker knows that one.

The containers and `unions` are for a function's names bound once (a union's, of course, more than
once), by a statement of their own; the calls' are for a function's names first bound by one,
whatever they're bound to later. The calls' and `vague` type what a loop, an unpacking or a `with`
binds too, declared on a line of its own before the statement: each name of
`for key, row in obj.rows():`, `a, b = helper()` or `with obj.open() as (f, g):` is `Any`, by the
call's kind (`a, b = 1, helper()` types `b` by its own value), and a loop's target over a
`list[dict[str, Any]]` is `vague`'s. Not a chained assignment's names, nor a `:=`'s.

On SQLAlchemy 2.0.54, with `--unsafe-fixes`: 175 bindings by `untyped-parameters`, 196 by
`empty-containers`, 98 by `mixed-containers`, 184 by `vague` and 9 by `unions`, 662 together (4.5%
of its bindings); one pass leaves a second nothing. basedpyright then reports no error in a file
under a rule it hadn't one for, and 22 errors fewer: an `Any` written hides what a checker had
inferred, most of all in a display (13 of them by `mixed-containers`).

On pydantic 2.13.5, `--fix` with the two kinds of call marks 519 of its 3,956 bindings (13.1%), all
by `unknown-calls`: every function of pydantic's declares its return. 194 of them are a loop's, an
unpacking's or a `with`'s. With `--unsafe-fixes` and every kind, 773 are widened, from 187 without
the calls' (72 of them a loop's or an unpacking's by `vague`): 81.0% of its bindings typed or
widened, from 66.2%. A second pass adds one union, of two values that were guesses until the first
declared what they rest on. basedpyright reports two errors fewer, which the `Any`s hide, and four
more. Two are of one statement and its copy in `pydantic.v1` (`name = name or parts.local_part`,
`name` a `str | None`, `parts` from a package that isn't installed): assigned an explicit `Any`, a
name keeps its declared type, where a value the checker couldn't type at all left it a `str`. Two
are of one loop's target (`for base in reversed(cls.__mro__):`, then
`if not dataclasses.is_dataclass(base): continue`): declared `Any`, it's narrowed to a dataclass or
an instance of one, where the `type` the checker inferred was narrowed to the class.

Every statement a widening writes ends with `# constricter: auto`, after any comment already there
(on its last line, if it has several; a declaration before its statement, on its own):

```python
def load(reader, count):
    text: Any = reader.read()  # constricter: auto
    seen: list[Any] = []  # constricter: auto
```

A marked annotation is `--fix`'s own, not the author's:

- LVA005 passes over it;
- `--coverage` counts it apart: `3/4 typed (75.0%), 1 widened` (`widened` in `--format=json`), and
  `--fail-under` reads the typed share alone;
- it types nothing read of its name: what `--fix` infers from the name is what it was before the
  widening;
- once its value's type is known (the parameter annotated, say), it's reported as LVA005 with that
  type as its fix: `--fix` writes it over the annotation and deletes the mark, a guess where the
  type is one. A declaration on a line of its own, before a loop, an unpacking or a `with`, is
  written over the same way once the statement types its name, if nothing binds the name again; a
  union's is left.

Take the mark off a line to keep its annotation as written.
