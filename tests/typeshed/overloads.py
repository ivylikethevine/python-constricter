# SPDX-License-Identifier: MIT
"""Standard-library functions whose return depends on their arguments: each signature, for `--fix` to pick.

`Overloads.entry` reads a function's overloads (or its one signature, when a type variable or a
class inside a builtin generic puts its return beyond the fixed-return tables) as `--fix` matches
them against a call (`constricter.fix.overloads`): each parameter's kind, whether it has a default,
and which argument types it certainly takes or refuses; and the return, as a template.

Argument types are the builtin scalars in `SCALARS`, `LiteralString` standing for a `str` literal.
A parameter every overload declares the same way takes whatever a call passes it (a call matching
none is an error anyway), so only the parameters that tell the overloads apart, or bind a type
variable, are read. A return
template is an annotation with standard-library classes by their dotted paths (`re.Pattern[AnyStr]`)
and type variables by their bare names, which the call's arguments bind.
"""

import ast
import copy
from collections.abc import Iterable, Iterator, Sequence
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.signatures import Accepts, Constant, Parameter
from constricter.fix.stdlib import Signature
from tests.typeshed.reading import (
    ClassRef,
    Defs,
    Reading,
    readable,
    substituted,
)
from tests.typeshed.stubs import (
    Alias,
    Binding,
    Found,
    Function,
    Klass,
    TypeVariable,
    Variable,
    decorator_name,
    private,
)
from tests.typeshed.templates import (
    BUILTINS,
    LITERAL,
    LITERAL_STRING,
    MAX_DEPTH,
    NONE,
    OBJECT,
    OPTIONAL,
    STR,
    TYPING,
    UNIONS,
    Templates,
    literal_values,
    parsed,
    type_name,
)

SCALARS: Final = ("str", "LiteralString", "bytes", "bytearray", "int", "float", "complex", "bool", "None")
YES: Final = "y"
NO: Final = "n"
MAYBE: Final = "?"
POSITIONAL: Final = "p"  # positional only
EITHER: Final = "e"  # positional or keyword
KEYWORD: Final = "k"  # keyword only
STAR: Final = "a"  # `*args`
STARS: Final = "w"  # `**kwargs`
_ANY: Final = frozenset({"Any", "Incomplete"})
_REFUSING: Final = frozenset({"Callable", "Type", "type"})  # no scalar is a callable or a class
_ANNOTATED: Final = "Annotated"
# A builtin scalar a parameter of another builtin type takes all the same (numbers widened).
_PROMOTED: Final = {
    ("int", "float"),
    ("int", "complex"),
    ("float", "complex"),
    ("bool", "float"),
    ("bool", "complex"),
}
# The class an argument of each type is an instance of (`None`'s, `object`, less what it doesn't have).
_CLASSES: Final = {"LiteralString": STR, "None": OBJECT}
# Methods whose calls aren't an instance's plain ones: read as attributes, or on the class.
_NOT_METHODS: Final = frozenset({"property", "cached_property", "classmethod", "staticmethod"})
# What a protocol's body binds that isn't a member its instances need (`typing`'s own protocols'
# `__slots__ = ()`).
_MACHINERY: Final = frozenset({"__slots__", "__init__", "__new__", "__class_getitem__", "__init_subclass__"})
_ATOM_NONE: Final = "none"
_ATOM_LITERAL: Final = "literal"
_ATOM_FOUND: Final = "found"
_ATOM_UNKNOWN: Final = "unknown"
_SELF_TYPE: Final = "Self"
_CALLABLE: Final = "Callable"
_PROPERTIES: Final = frozenset({"property", "cached_property"})
_INIT: Final = "__init__"
_NEW: Final = "__new__"
# The builtin containers whose element an argument of the type binds a parameter's type variable to.
CONTAINERS: Final = ("list", "tuple", "set", "frozenset", "dict")


class Atom(NamedTuple):
    """One member of a parameter's union: `None`, a `Literal`'s values, a name found, or one unread."""

    kind: str
    found: Found | None = None
    subscripted: bool = False  # the name, with type arguments (`PathLike[str]`)
    literals: tuple[Constant, ...] = ()


class Param(NamedTuple):
    """One parameter of one signature: its name, kind (`POSITIONAL`...), default, and annotation."""

    name: str
    kind: str
    default: bool
    annotation: ast.expr | None


class Verdicts(NamedTuple):
    """What a parameter takes: a verdict per `SCALARS` type, and more for literals and type variables.

    `values`: for a variable argument; `constants`: for a literal argument not among `literals`
    (the values of its `Literal[...]` members), if they differ; `binds`: the type variable the
    parameter is, and what an argument of each type binds it to. `anything`: the type variable the
    parameter is, if it's unbounded, which any argument binds to its own type; `elements`: for a
    parameter that is a generic class of one type variable (`Iterable[_T]`), that variable, and which
    type argument of each builtin container in `CONTAINERS` taking it binds it (`dict`'s keys: 0);
    `returned`: for a callable returning an unbounded type variable (`Callable[..., _T]`), that
    variable, which a function argument binds to its declared return.
    """

    values: str
    constants: str | None = None
    literals: tuple[Constant, ...] | None = None
    binds: dict[str, tuple[str, str]] | None = None
    anything: str | None = None
    elements: tuple[str, dict[str, int]] | None = None
    returned: str | None = None


def parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Param]:
    """List a signature's parameters in order, a `__name` (the stubs' old spelling) positional only.

    Returns:
      Them.

    """
    args: ast.arguments = node.args
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    defaults: int = len(positional) - len(args.defaults)
    found: list[Param] = []
    index: int
    arg: ast.arg
    for index, arg in enumerate(positional):
        old: bool = arg.arg.startswith("__") and not arg.arg.endswith("__")
        kind: str = POSITIONAL if index < len(args.posonlyargs) or old else EITHER
        found.append(Param(arg.arg, kind, index >= defaults, arg.annotation))
    if args.vararg is not None:
        found.append(Param(args.vararg.arg, STAR, default=True, annotation=args.vararg.annotation))
    default: ast.expr | None
    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        found.append(Param(arg.arg, KEYWORD, default is not None, arg.annotation))
    if args.kwarg is not None:
        found.append(Param(args.kwarg.arg, STARS, default=True, annotation=args.kwarg.annotation))
    return found


# A method's entry (`module.Class.name`) and signatures.
_Method: TypeAlias = tuple[str, list[Signature]]
# A parameter as every signature must have it to be shared: name, kind, default, annotation.
_Key: TypeAlias = tuple[str, str, bool, str]


def _binding(binds: dict[str, tuple[str, str]]) -> str | dict[str, list[str]]:
    """Write what a parameter's type variable binds to: each argument type's own, as a bare name, or each.

    Returns:
      The variable's name if every argument type binds it to itself (a `str` literal to `str`), else
      what each binds it to.

    """
    names: set[str] = {name for name, _ in binds.values()}
    own: bool = len(binds) == len(SCALARS) and all(
        text == (STR if scalar == LITERAL_STRING else scalar) for scalar, (_, text) in binds.items()
    )
    return names.pop() if own and len(names) == 1 else {kind: list(bound) for kind, bound in binds.items()}


def _self(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.expr | None:
    """Find a method's `self` annotation.

    Returns:
      It, or `None`.

    """
    positional: list[ast.arg] = [*node.args.posonlyargs, *node.args.args]
    return positional[0].annotation if positional else None


def _unbound(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Copy a method's definition without its first parameter (`self`).

    Returns:
      The copy.

    """
    args: ast.arguments = copy.copy(node.args)
    if args.posonlyargs:
        args.posonlyargs = args.posonlyargs[1:]
    else:
        args.args = args.args[1:]
    unbound: ast.FunctionDef | ast.AsyncFunctionDef = copy.copy(node)
    unbound.args = args
    return unbound


def _shared(parameter: Param) -> str:
    """Write a parameter every signature has alike, which takes whatever a call passes it, compactly.

    Returns:
      Its name and kind, and `=` if it has a default: `bufsize e=`.

    """
    return f"{parameter.name} {parameter.kind}{'=' if parameter.default else ''}"


def _key(parameter: Param) -> _Key:
    annotation: str = "" if parameter.annotation is None else ast.dump(parameter.annotation)
    return parameter.name, parameter.kind, parameter.default, annotation


class Overloads(Templates):
    """Signatures read for `--fix` to pick among, as one configuration sees the stubs."""

    def __init__(self, reading: Reading, canonical: dict[ClassRef, str]) -> None:
        """Read with `reading`; `canonical`: every public class's path, generic ones too."""
        super().__init__(reading, canonical)
        self._names: dict[str, frozenset[str] | None] = {}

    def entry(
        self,
        defs: Defs,
        module: str,
        selves: Sequence[ast.expr | None] = (),
        constructed: str | None = None,
    ) -> list[Signature] | None:
        """Read a function's signatures, in order, as the `overloads` table holds them.

        `selves`: a method's (read without `self`) each signature's `self` annotation, if any;
        `constructed`: for a class's `__new__` or `__init__`, the template its instance is, which a
        signature returning `Self` (or `__init__`'s) returns.

        Returns:
          Each one's parameters (`[name, kind, default, accepts]`, or `"name kind="` where every
          signature has the parameter alike: see `_shared`) and return template (null if it can't
          be written);
          or `None` if a signature can't be read, or none's return can be written.

        """
        if any(not readable(node) for node in defs):
            return None
        each: list[list[Param]] = [parameters(node) for node in defs]
        keys: list[set[_Key]] = [{_key(p) for p in one} for one in each]
        shared: set[_Key] = keys[0].intersection(*keys[1:])
        found: list[Signature] = []
        node: ast.FunctionDef | ast.AsyncFunctionDef
        one: list[Param]
        index: int
        for index, (node, one) in enumerate(zip(defs, each, strict=True)):
            params: list[Parameter | str] = [
                _shared(p)
                if _key(p) in shared and not self._variable_in(p.annotation, module)
                else (p.name, p.kind, p.default, self._accepted(p, module))
                for p in one
            ]
            signature: Signature = Signature(
                params=params,
                returns=constructed
                if constructed is not None and (node.name == _INIT or self._is_self(node.returns, module))
                else self.template(node.returns, module),
            )
            instance: list[str] | None
            if index < len(selves) and (instance := self._instance(selves[index], module)) is not None:
                signature["self"] = instance
            found.append(signature)
        return found if any(signature["returns"] is not None for signature in found) else None

    def constructor(self, klass: ClassRef) -> list[Signature] | None:
        """Read a generic class's constructor as a function returning its instance, typed by its arguments.

        Its `__new__`'s signatures, or its `__init__`'s, whichever its method resolution order has
        (not both: which decides would be a type checker's call), each returning the class with its
        type parameters as the arguments bind them (`deque(names)`: `collections.deque[str]`), or the
        instance a `__new__` overload declares (`array("i")`: `array.array[int]`).

        Returns:
          The signatures (see `entry`), or `None` for a protocol, a class whose order can't be worked
          out, one with neither or both, or an `__init__` declaring `self`'s type.

        """
        node: ast.ClassDef | None = self.reading.class_node(klass)
        params: list[str] | None = self.type_parameters(klass)
        classes: list[ClassRef]
        whole: bool
        classes, whole = self.reading.trusted(klass)
        if (
            node is None
            or klass not in self.canonical  # a builtin (`memoryview`), typed apart
            or not params
            or not whole
            or self.reading.is_protocol(node, klass.module)
        ):
            return None
        found: dict[str, tuple[Function, ClassRef]] = {}
        owner: ClassRef
        for owner in classes:
            name: str
            binding: Binding
            for name, binding in self.reading.body(owner).items():
                if name in {_NEW, _INIT} and isinstance(binding, Function):
                    _ = found.setdefault(name, (binding, owner))
        if len(found) != 1:
            return None
        function: Function
        name, (function, owner) = next(iter(found.items()))
        if name == _INIT and any(_self(node) is not None for node in function.defs):
            return None
        template: str = f"{self.canonical[klass]}[{', '.join(param.rstrip('=') for param in params)}]"
        return self.entry(tuple(_unbound(node) for node in function.defs), owner.module, (), template)

    def _variable_in(self, annotation: ast.expr | None, module: str) -> bool:
        """Check whether a parameter's annotation names a type variable, which its argument may bind.

        Returns:
          Whether it does.

        """
        return annotation is not None and bool(self._variables(annotation, module))

    def attributes(self, klass: ClassRef) -> dict[str, str]:
        """Read a generic class's own attributes and properties, as templates its type arguments bind.

        `re.Match`'s `string` is its `AnyStr`, `pos` an `int`. Only its own body's: a generic base's
        members name that base's type parameters.

        Returns:
          Each one's template, by name (one that can't be written left out).

        """
        found: dict[str, str] = {}
        name: str
        binding: Binding
        annotation: ast.expr
        defs: Defs
        for name, binding in self.reading.body(klass).items():
            written: ast.expr | None = None
            match binding:
                case Variable(annotation=annotation) if not private(name):
                    written = annotation
                case Function(defs=defs) if (
                    not private(name)
                    and len(defs) == 1
                    and _PROPERTIES & {decorator_name(d) for d in defs[0].decorator_list}
                ):
                    written = defs[0].returns
                case _:
                    pass
            template: str | None
            if (template := None if written is None else self.template(written, klass.module)) is not None:
                found[name] = template
        return found

    def _is_self(self, annotation: ast.expr | None, module: str) -> bool:
        found: Found | None = None if annotation is None else self.reading.ref(annotation, module)
        return found is not None and found.module in TYPING and found.name == _SELF_TYPE

    def methods(
        self,
        klass: ClassRef,
        fixed: Iterable[str],
        *,
        inherited: bool = True,
    ) -> dict[str, "_Method"]:
        """Read a class's plain methods whose arguments decide their return: not `fixed` (typed alike always).

        A method's signatures are read without its `self`, as a call on an instance passes it; with
        `inherited` false, only the class's own (a generic base's type variables aren't its own).

        Returns:
          Each one's defining class and method (`module.Class.name`: one entry for all the classes
          inheriting it) and signatures (see `entry`), by name.

        """
        found: dict[str, _Method] = {}
        known: frozenset[str] = frozenset(fixed)
        name: str
        function: Function
        owner: ClassRef
        for name, (function, owner) in self.reading.functions(klass).items():
            decorators: set[str] = {decorator_name(d) for d in function.defs[0].decorator_list}
            signatures: list[Signature] | None
            if name in known or decorators & _NOT_METHODS or (not inherited and owner != klass):
                continue
            if (
                signatures := self.entry(
                    tuple(_unbound(node) for node in function.defs),
                    owner.module,
                    [_self(node) for node in function.defs],
                )
            ) is not None:
                found[name] = (f"{owner.module}.{owner.name}.{name}", signatures)
        return found

    def _instance(self, annotation: ast.expr | None, module: str) -> list[str] | None:
        """Read the type arguments a method's `self` annotation gives its class (`Pattern[str]`'s `str`).

        Returns:
          Them, or `None` if it gives none, or one names a type variable or can't be written.

        """
        if not isinstance(annotation, ast.Subscript):
            return None
        index: ast.expr = annotation.slice
        args: list[ast.expr] = list(index.elts) if isinstance(index, ast.Tuple) else [index]
        texts: list[str | None] = [self.template(arg, module) for arg in args]
        if None in texts or self._variables(annotation.slice, module):
            return None
        return [text for text in texts if text is not None]

    def _accepted(self, parameter: Param, module: str) -> Accepts:
        """Write what a parameter takes as the tables hold it.

        Returns:
          Its verdicts.

        """
        verdicts: Verdicts = (
            Verdicts(MAYBE * len(SCALARS))
            if parameter.annotation is None
            else self.accepts(parameter.annotation, module)
        )
        found: Accepts = Accepts(v=verdicts.values)
        if verdicts.constants is not None:
            found["c"] = verdicts.constants
        if verdicts.literals is not None:
            found["lit"] = list(verdicts.literals)
        if verdicts.binds:
            found["var"] = _binding(verdicts.binds)
        if verdicts.anything is not None:
            found["t"] = verdicts.anything
        if verdicts.elements is not None:
            found["e"], found["of"] = verdicts.elements
        if verdicts.returned is not None:
            found["r"] = verdicts.returned
        return found

    def accepts(self, annotation: ast.expr, module: str) -> Verdicts:
        """Work out which `SCALARS` types a parameter's annotation takes.

        Returns:
          Its verdicts (see `Verdicts`).

        """
        atoms: list[Atom] = list(self._atoms(annotation, module, 0))
        literals: list[Constant] = [value for atom in atoms for value in atom.literals]
        values: str = "".join(self._verdict(atoms, scalar, constant=False) for scalar in SCALARS)
        constants: str = "".join(self._verdict(atoms, scalar, constant=True) for scalar in SCALARS)
        binds: dict[str, tuple[str, str]] = {}
        scalar: str
        for scalar in SCALARS:
            bound: tuple[str, str] | None
            if (bound := self._binds(atoms, scalar)) is not None:
                binds[scalar] = bound
        # A scalar that is one (`str`, an `Iterable[str]`; `float`, a `_SupportsFloor[int]`) binds it.
        of: tuple[ClassRef, str] | None
        if (of := self._of_one(annotation, module)) is not None:
            taken: list[bool] = []
            for scalar in SCALARS:
                element: str | None = self._scalar_element(scalar, of[0])
                taken.append(element is not None)
                if element is not None:
                    binds[scalar] = (of[1], element)
            values = "".join(YES if yes else verdict for yes, verdict in zip(taken, values, strict=True))
            constants = "".join(
                YES if yes else verdict for yes, verdict in zip(taken, constants, strict=True)
            )
        return Verdicts(
            values,
            constants if literals and constants != values else None,
            tuple(literals) if literals else None,
            binds or None,
            _unbounded(atoms),
            None if of is None else self._container_elements(*of),
            self._callable_return(annotation, module),
        )

    def _callable_return(self, annotation: ast.expr, module: str) -> str | None:
        """Name the unbounded type variable a callable parameter returns (`Callable[..., _T]`'s `_T`).

        Returns:
          Its name, or `None` for any other parameter.

        """
        callee: ast.expr
        returned: ast.expr
        match annotation:
            case ast.Subscript(value=callee, slice=ast.Tuple(elts=[_, returned])):
                pass
            case _:
                return None
        found: Found | None = self.reading.ref(callee, module)
        if found is None or found.name != _CALLABLE:
            return None
        return _unbounded(list(self._atoms(returned, module, 1)))

    def _of_one(self, annotation: ast.expr, module: str) -> tuple[ClassRef, str] | None:
        """Read a parameter that is a generic class of one unbounded type variable (`Iterable[_T]`).

        Returns:
          The class, and the variable's name; or `None`.

        """
        if not isinstance(annotation, ast.Subscript) or isinstance(annotation.slice, ast.Tuple):
            return None
        found: Found | None = self.reading.ref(annotation.value, module)
        inner: list[Atom] = list(self._atoms(annotation.slice, module, 1))
        name: str | None = _unbounded(inner)
        if found is None or not isinstance(found.binding, Klass) or name is None:
            return None
        return ClassRef(found.module, found.name), name

    def _scalar_element(self, scalar: str, generic: ClassRef) -> str | None:
        """Find what a builtin scalar that is a `generic` (`str`, an `Iterable[str]`) binds its variable to.

        Returns:
          That type, if it's a builtin scalar (`bytes`' `int`); or `None`.

        """
        builtin: ClassRef = ClassRef(BUILTINS, _CLASSES.get(scalar, scalar))
        found: list[str] | None = self.base_arguments(builtin, generic)
        protocol: str | None = None if found is not None else self._protocol_element(scalar, generic)
        found = found if protocol is None else [protocol]
        return found[0] if found is not None and len(found) == 1 and found[0] in SCALARS else None

    def _protocol_element(self, scalar: str, protocol: ClassRef) -> str | None:
        """Find what a scalar that has a generic protocol's members binds its one type parameter to.

        By the methods returning it (`_SupportsFloor[_T]`'s `__floor__`), as the scalar's class
        declares them (`float.__floor__` returns an `int`).

        Returns:
          That type, if every such method returns the same; or `None`.

        """
        node: ast.ClassDef | None = self.reading.class_node(protocol)
        params: list[str] = [param.rstrip("=") for param in self.type_parameters(protocol) or []]
        if (
            node is None
            or len(params) != 1
            or not self.reading.is_protocol(node, protocol.module)
            or self._structural(protocol, scalar) != YES
        ):
            return None
        owners: list[ClassRef] = self.reading.trusted(ClassRef(BUILTINS, _CLASSES.get(scalar, scalar)))[0]
        found: set[str | None] = set()
        name: str
        binding: Binding
        for name, binding in self.reading.body(protocol).items():
            returns: ast.expr | None = binding.defs[0].returns if isinstance(binding, Function) else None
            if returns is None or self._spelled(returns, protocol.module, 0) != params[0]:
                continue
            method: Binding | None = next(
                (body[name] for body in (self.reading.body(owner) for owner in owners) if name in body),
                None,
            )
            found.update(
                {self.template(d.returns, BUILTINS) for d in method.defs}
                if isinstance(method, Function)
                else {None},
            )
        return found.pop() if len(found) == 1 else None

    def _container_elements(self, generic: ClassRef, variable: str) -> tuple[str, dict[str, int]] | None:
        """Find which type argument of each builtin container that is a `generic` binds its variable.

        Returns:
          The variable, and each such container's index (`list`'s 0, `dict`'s keys' 0); or `None` if
          none is.

        """
        found: dict[str, int] = {}
        container: str
        for container in CONTAINERS:
            klass: ClassRef = ClassRef(BUILTINS, container)
            params: list[str] = [param.rstrip("=") for param in self.type_parameters(klass) or []]
            arguments: list[str] | None = self.base_arguments(klass, generic)
            if arguments is not None and len(arguments) == 1 and arguments[0] in params:
                found[container] = params.index(arguments[0])
        return (variable, found) if found else None

    def base_arguments(self, klass: ClassRef, base: ClassRef, hops: int = 0) -> list[str] | None:
        """Spell the type arguments `klass` gives an ancestor (`list` gives `Iterable` its own `_T`).

        Through its bases' arguments, each class's type parameters replaced by what its subclass
        passes them.

        Returns:
          Them, in terms of `klass`'s own type parameters; or `None` if it isn't an ancestor, or an
          argument can't be spelled.

        """
        node: ast.ClassDef | None = self.reading.class_node(klass)
        if node is None or hops > MAX_DEPTH:
            return None
        written: ast.expr
        for written in node.bases:
            value: ast.expr = written.value if isinstance(written, ast.Subscript) else written
            found: Found | None = self.reading.ref(value, klass.module)
            if found is None or not isinstance(found.binding, Klass):
                continue
            parent: ClassRef = ClassRef(found.module, found.name)
            args: list[ast.expr] = []
            if isinstance(written, ast.Subscript):
                index: ast.expr = written.slice
                args = list(index.elts) if isinstance(index, ast.Tuple) else [index]
            texts: list[str | None] = [self._spelled(arg, klass.module, 0) for arg in args]
            if None in texts:
                continue
            spelled: list[str] = [text for text in texts if text is not None]
            if parent == base:
                return spelled
            above: list[str] | None
            if (above := self.base_arguments(parent, base, hops + 1)) is not None:
                params: list[str] = [param.rstrip("=") for param in self.type_parameters(parent) or []]
                return [substituted(text, dict(zip(params, spelled, strict=False))) for text in above]
        return None

    def _atoms(self, expr: ast.expr, module: str, hops: int) -> Iterator[Atom]:
        """Split an annotation into its union's members, through aliases, `Optional`, `Union`, strings.

        Yields:
          Each member: `None`, a `Literal`'s values, a name found (and its subscript, if any), or
          one that can't be read.

        """
        left: ast.expr
        right: ast.expr
        text: str
        if hops > MAX_DEPTH:
            yield Atom(_ATOM_UNKNOWN)
            return
        match expr:
            case ast.Constant(value=None):
                yield Atom(_ATOM_NONE)
            case ast.Constant(value=str() as text):
                yield from self._atoms(parsed(text), module, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                yield from self._atoms(left, module, hops + 1)
                yield from self._atoms(right, module, hops + 1)
            case ast.Subscript():
                yield from self._subscript_atoms(expr, module, hops)
            case ast.Name() | ast.Attribute():
                found: Found | None = self.reading.ref(expr, module)
                if found is not None and isinstance(found.binding, Alias):
                    yield from self._atoms(found.binding.value, found.module, hops + 1)
                else:
                    yield Atom(_ATOM_UNKNOWN) if found is None else Atom(_ATOM_FOUND, found)
            case _:
                yield Atom(_ATOM_UNKNOWN)

    def _subscript_atoms(self, expr: ast.Subscript, module: str, hops: int) -> Iterator[Atom]:
        found: Found | None = self.reading.ref(expr.value, module)
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        if found is None:
            yield Atom(_ATOM_UNKNOWN)
        elif found.module in TYPING and found.name in UNIONS:
            members: list[ast.expr] = [*args, *([ast.Constant(None)] if found.name == OPTIONAL else [])]
            yield from (atom for member in members for atom in self._atoms(member, module, hops + 1))
        elif found.module in TYPING and found.name == LITERAL:
            constants: list[Constant] = literal_values(args)
            yield Atom(_ATOM_LITERAL, literals=tuple(constants))
        elif found.module in TYPING and found.name == _ANNOTATED:
            yield from self._atoms(args[0], module, hops + 1)
        elif isinstance(found.binding, Alias):  # a generic alias: taken whole, its parameters unread
            yield from (
                inner._replace(subscripted=True)
                for inner in self._atoms(found.binding.value, found.module, hops + 1)
            )
        else:
            yield Atom(_ATOM_FOUND, found, subscripted=True)

    def _verdict(self, atoms: Sequence[Atom], scalar: str, *, constant: bool) -> str:
        """Decide whether a parameter takes an argument of type `scalar` (a literal one if `constant`).

        Returns:
          `YES` if a member certainly does, `NO` if every member certainly doesn't, else `MAYBE`.

        """
        verdicts: set[str] = {self._atom(atom, scalar, constant=constant) for atom in atoms}
        if YES in verdicts:
            return YES
        return NO if verdicts == {NO} else MAYBE

    def _atom(self, atom: Atom, scalar: str, *, constant: bool) -> str:
        if atom.kind == _ATOM_NONE:
            return YES if scalar == NONE else NO
        if atom.kind == _ATOM_LITERAL:
            types: set[str] = {type_name(value) for value in atom.literals}
            matches: bool = scalar in types or (scalar == LITERAL_STRING and STR in types)
            return NO if constant or not matches else MAYBE  # a literal among them is matched apart
        if atom.found is not None:
            return self._found(atom.found, scalar, subscripted=atom.subscripted)
        return MAYBE

    def _found(self, found: Found, scalar: str, *, subscripted: bool) -> str:
        """Decide whether a name a parameter's annotation uses takes an argument of type `scalar`.

        Returns:
          The verdict.

        """
        if found.module in TYPING and found.name in _ANY:
            return YES
        if found.module in TYPING and found.name == LITERAL_STRING:
            return YES if scalar == LITERAL_STRING else NO
        if found.module in TYPING and found.name in _REFUSING:
            return NO
        if isinstance(found.binding, TypeVariable):
            return self._type_variable(found.binding, found.module, scalar)
        return (
            self._klass(found, scalar, subscripted=subscripted) if isinstance(found.binding, Klass) else MAYBE
        )

    def _klass(self, found: Found, scalar: str, *, subscripted: bool = False) -> str:
        """Decide whether a class a parameter's annotation names takes an argument of type `scalar`.

        By inheritance, or for a protocol by its members' names; a builtin number takes a narrower
        one (`int` for `float`).

        Returns:
          The verdict.

        """
        klass: ClassRef = ClassRef(found.module, found.name)
        node: ast.ClassDef | None = self.reading.class_node(klass)
        if klass == ClassRef(BUILTINS, OBJECT) or (
            klass.module == BUILTINS and (scalar, klass.name) in _PROMOTED
        ):
            return YES
        verdict: str = (
            self._structural(klass, scalar)
            if node is not None and self.reading.is_protocol(node, klass.module)
            else self._nominal(klass, scalar)
        )
        # A generic class's parameters aren't read: the class taking it isn't enough.
        return MAYBE if verdict == YES and (subscripted or self.reading.generic(klass)) else verdict

    def _type_variable(self, variable: TypeVariable, module: str, scalar: str) -> str:
        if variable.constraints:
            return self._verdict(
                [atom for constraint in variable.constraints for atom in self._atoms(constraint, module, 1)],
                scalar,
                constant=False,
            )
        if variable.bound is not None:
            return self._verdict(list(self._atoms(variable.bound, module, 1)), scalar, constant=False)
        return YES

    def _binds(self, atoms: Sequence[Atom], scalar: str) -> tuple[str, str] | None:
        """Find the type variable an argument of type `scalar` binds, if one member alone takes it.

        Returns:
          Its name, and what it's bound to: a constraint's type, or the argument's own (a literal's
          widened to `str`); or `None`.

        """
        taking: list[Atom] = [atom for atom in atoms if self._atom(atom, scalar, constant=False) != NO]
        found: Found | None
        if len(taking) != 1 or (found := taking[0].found) is None:
            return None
        variable: Binding = found.binding
        if not isinstance(variable, TypeVariable) or self._atom(taking[0], scalar, constant=False) != YES:
            return None
        widened: str = STR if scalar == LITERAL_STRING else scalar
        if not variable.constraints:
            return found.name, widened
        texts: set[str | None] = {
            self.template(constraint, found.module)
            for constraint in variable.constraints
            if self._verdict(list(self._atoms(constraint, found.module, 1)), scalar, constant=False) == YES
        }
        text: str | None = texts.pop() if len(texts) == 1 else None
        return None if text is None else (found.name, text)

    def _nominal(self, klass: ClassRef, scalar: str) -> str:
        """Decide by inheritance whether an argument of type `scalar` is an instance of `klass`.

        Returns:
          The verdict (`MAYBE` if the scalar's class's order can't be worked out).

        """
        if scalar == NONE:
            return NO
        order: list[ClassRef] | None
        if (order := self.reading.mro(ClassRef(BUILTINS, _CLASSES.get(scalar, scalar)))) is None:
            return MAYBE
        return YES if klass in order else NO

    def _structural(self, protocol: ClassRef, scalar: str) -> str:
        """Decide by its members' names whether an argument of type `scalar` has a protocol's members.

        Returns:
          `YES` if it has them all, `NO` if it lacks one, `MAYBE` if either can't be told.

        """
        needed: frozenset[str] | None = self._protocol_names(protocol)
        has: frozenset[str] | None = self._class_names(_CLASSES.get(scalar, scalar))
        if needed is None or has is None:
            return MAYBE
        return YES if needed <= has else NO

    def _protocol_names(self, protocol: ClassRef) -> frozenset[str] | None:
        classes: list[ClassRef]
        whole: bool
        classes, whole = self.reading.trusted(protocol)
        if not whole:
            return None
        return (
            frozenset(
                name for owner in classes if self._is_protocol(owner) for name in self.reading.body(owner)
            )
            - _MACHINERY
        )

    def _is_protocol(self, klass: ClassRef) -> bool:
        node: ast.ClassDef | None = self.reading.class_node(klass)
        return node is not None and self.reading.is_protocol(node, klass.module)

    def scalar_members(self, scalar: str) -> frozenset[str] | None:
        """Name what an argument of type `scalar` has (`None`'s: `object`'s), for protocols to be checked by.

        Returns:
          Them, or `None` if its class's bases can't all be followed.

        """
        return self._class_names(_CLASSES.get(scalar, scalar))

    def _class_names(self, name: str) -> frozenset[str] | None:
        """Name what a builtin class's instances have: its members, its bases', `object`'s.

        Returns:
          Them, or `None` if its bases can't all be followed.

        """
        if name not in self._names:
            classes: list[ClassRef]
            whole: bool
            classes, whole = self.reading.trusted(ClassRef(BUILTINS, name))
            self._names[name] = (
                frozenset(
                    member
                    for owner in (*classes, ClassRef(BUILTINS, OBJECT))
                    for member in self.reading.body(owner)
                )
                if whole
                else None
            )
        return self._names[name]


def _unbounded(atoms: Sequence[Atom]) -> str | None:
    """Name the type variable a parameter is, if it's all it is and nothing bounds it (`x: _T`).

    Returns:
      Its name, or `None`.

    """
    found: Found | None = atoms[0].found if len(atoms) == 1 else None
    variable: Binding | None = None if found is None else found.binding
    if not isinstance(variable, TypeVariable) or variable.constraints or variable.bound is not None:
        return None
    return variable.name
