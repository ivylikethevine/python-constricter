# SPDX-License-Identifier: MIT
"""Standard-library functions whose return depends on their arguments: each signature, for `--fix` to pick.

`Overloads.entry` reads a function's overloads (or its one signature, when a type variable or a
class inside a builtin generic puts its return beyond the fixed-return tables) as `--fix` matches
them against a call (`constricter.fix.libraries.overloads`): each parameter's kind, whether it has a default,
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

from constricter.fix.core.signatures import (
    AWAIT,
    CLASS_BINDS,
    CLASS_VERDICT,
    Accepts,
    Signature,
)
from stdlib_tables.accepting import (
    MAYBE,
    SCALARS,
    YES,
    Accepting,
    Verdicts,
)
from stdlib_tables.forms import ClassRef, Defs
from stdlib_tables.reading import OPERATORS, readable
from stdlib_tables.stubs import (
    Binding,
    Found,
    Function,
    Variable,
    decorator_name,
    private,
)
from stdlib_tables.templates import (
    LITERAL_STRING,
    STR,
    TYPING,
)

POSITIONAL: Final = "p"  # positional only
EITHER: Final = "e"  # positional or keyword
KEYWORD: Final = "k"  # keyword only
STAR: Final = "a"  # `*args`
STARS: Final = "w"  # `**kwargs`
# Methods whose calls aren't an instance's plain ones: read as attributes, or on the class.
_NOT_METHODS: Final = frozenset({"property", "cached_property", "classmethod", "staticmethod"})
_SELF_TYPE: Final = "Self"
_PROPERTIES: Final = frozenset({"property", "cached_property"})
_INIT: Final = "__init__"
_TYPE: Final = "type"
_NEW: Final = "__new__"
_ENTER: Final = "__enter__"


class Param(NamedTuple):
    """One parameter of one signature: its name, kind (`POSITIONAL`...), default, and annotation."""

    name: str
    kind: str
    default: bool
    annotation: ast.expr | None


def _classes(annotation: ast.expr) -> Iterator[ast.expr]:
    """Find what a parameter's annotation takes a class of: `_E` in `type[_E] | tuple[type[_E], ...]`.

    Yields:
      Each `type[...]` member of its union's argument.

    """
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        yield from _classes(annotation.left)
        yield from _classes(annotation.right)
    elif (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == _TYPE
    ):
        yield annotation.slice


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


class Overloads(Accepting):
    """Signatures read for `--fix` to pick among, as one configuration sees the stubs."""

    def entry(
        self,
        defs: Defs,
        module: str,
        selves: Sequence[ast.expr | None] = (),
        constructed: str | None = None,
        *,
        awaited: bool = False,
    ) -> list[Signature] | None:
        """Read a function's signatures, in order, as the `overloads` table holds them.

        `selves`: a method's (read without `self`) each signature's `self` annotation, if any;
        `constructed`: for a class's `__new__` or `__init__`, the template its instance is, which a
        signature returning `Self` (or `__init__`'s) returns. `awaited`: an `async def`'s, each
        return what awaiting its call gives.

        Returns:
          Each one's parameters (`[name, kind, default, accepts]`, or `"name kind="` where every
          signature has the parameter alike: see `_shared`) and return template (null if it can't
          be written);
          or `None` if a signature can't be read, or none's return can be written.

        """
        if any(not readable(node, awaited=awaited) for node in defs):
            return None
        each: list[list[Param]] = [parameters(node) for node in defs]
        keys: list[set[_Key]] = [{_key(p) for p in one} for one in each]
        shared: set[_Key] = keys[0].intersection(*keys[1:])
        found: list[Signature] = []
        node: ast.FunctionDef | ast.AsyncFunctionDef
        one: list[Param]
        index: int
        for index, (node, one) in enumerate(zip(defs, each, strict=True)):
            signature: Signature = Signature(
                params=self._params(one, shared, module, alone=len(defs) == 1),
                returns=constructed
                if constructed is not None and (node.name == _INIT or self._is_self(node.returns, module))
                else self.template(node.returns, module),
            )
            instance: list[str] | None
            if index < len(selves) and (instance := self._instance(selves[index], module)) is not None:
                signature["self"] = instance
            found.append(signature)
        return found if any(signature["returns"] is not None for signature in found) else None

    def _params(
        self,
        one: Sequence[Param],
        shared: set[_Key],
        module: str,
        *,
        alone: bool,
    ) -> list[str | tuple[str, str, bool, Accepts | None]]:
        """Lay one signature's parameters out: `"name kind="` where every signature has it alike (`shared`).

        Returns:
          Each one's.

        """
        return [
            _shared(p)
            if _key(p) in shared and not self._variable_in(p.annotation, module)
            else (p.name, p.kind, p.default, self._accepted(p, module, alone=alone))
            for p in one
        ]

    def constructor(self, klass: ClassRef) -> list[Signature] | None:
        """Read a generic class's constructor as a function returning its instance, typed by its arguments.

        Its `__new__`'s signatures, or its `__init__`'s, whichever its method resolution order has
        (not both: which decides would be a type checker's call), each returning the class with its
        type parameters as the arguments bind them (`deque(names)`: `collections.deque[str]`), or the
        instance a `__new__` overload declares (`array("i")`: `array.array[int]`) or an `__init__`
        overload's `self` (`tempfile.TemporaryDirectory()`: a `tempfile.TemporaryDirectory[str]`).

        Returns:
          The signatures (see `entry`), or `None` for a protocol, a class whose order can't be worked
          out, or one with neither or both.

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
        template: str = f"{self.canonical[klass]}[{', '.join(param.rstrip('=') for param in params)}]"
        signatures: list[Signature] | None = self.entry(
            tuple(_unbound(node) for node in function.defs),
            owner.module,
            (),
            template,
        )
        signature: Signature
        declared: ast.FunctionDef | ast.AsyncFunctionDef
        for signature, declared in zip(signatures or [], function.defs if signatures else (), strict=True):
            if name == _INIT and _self(declared) is not None:
                signature["returns"] = self.template(_self(declared), owner.module)
        return signatures

    def _variable_in(self, annotation: ast.expr | None, module: str) -> bool:
        """Check whether a parameter's annotation names a type variable, which its argument may bind.

        Returns:
          Whether it does.

        """
        return annotation is not None and bool(self._variables(annotation, module))

    def attributes(self, klass: ClassRef) -> dict[str, str]:
        """Read a class's own attributes and properties, as templates its type arguments (if any) bind.

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

    def enters_itself(self, klass: ClassRef) -> bool:
        """Check whether a class's `__enter__` (its own, or the one it inherits) returns `Self`.

        `with` then gives the instance as it's typed, a generic class's type arguments included.

        Returns:
          Whether every signature of it does.

        """
        found: tuple[Function, ClassRef] | None = self.reading.functions(klass).get(_ENTER)
        return found is not None and all(
            readable(node) and self._is_self(node.returns, found[1].module) for node in found[0].defs
        )

    def methods(
        self,
        klass: ClassRef,
        fixed: Iterable[str],
        *,
        inherited: bool = True,
    ) -> dict[str, "_Method"]:
        """Read a class's plain methods whose arguments decide their return: not `fixed` (typed alike always).

        A method's signatures are read without its `self`, as a call on an instance passes it; with
        `inherited` false, only the class's own (a generic base's type variables aren't its own). An
        `async def`'s are what awaiting its call gives, under its name after `AWAIT`.

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
            awaited: bool = isinstance(function.defs[0], ast.AsyncFunctionDef)
            selves: list[ast.expr | None] = [_self(node) for node in function.defs]
            unbound: Defs = tuple(_unbound(node) for node in function.defs)
            if (signatures := self.entry(unbound, owner.module, selves, awaited=awaited)) is not None:
                if name in OPERATORS:
                    self._operands(signatures, function.defs, owner.module)
                found[AWAIT + name if awaited else name] = (f"{owner.module}.{owner.name}.{name}", signatures)
        return found

    def _operands(self, signatures: list[Signature], defs: Defs, module: str) -> None:
        """Note what each of an operator's signatures takes as its operand (`Signature`'s `takes`)."""
        signature: Signature
        node: ast.FunctionDef | ast.AsyncFunctionDef
        for signature, node in zip(signatures, defs, strict=True):
            operands: list[Param] = parameters(_unbound(node))
            signature["takes"] = self.template(operands[0].annotation, module) if len(operands) == 1 else None

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

    def _accepted(self, parameter: Param, module: str, *, alone: bool = False) -> Accepts:
        """Write what a parameter takes as the tables hold it; `alone`: with no other signature.

        Returns:
          Its verdicts.

        """
        verdicts: Verdicts = (
            Verdicts(MAYBE * len(SCALARS))
            if parameter.annotation is None
            else self.accepts(parameter.annotation, module)
        )
        held: bool = self.reading.future_bound(parameter.annotation, module)  # by a future: no coroutine
        found: Accepts = (
            Accepts(v=verdicts.values, f=verdicts.bounded or "") if held else Accepts(v=verdicts.values)
        )
        if verdicts.constants is not None:
            found["c"] = verdicts.constants
        if verdicts.literals is not None:
            found["lit"] = list(verdicts.literals)
        if verdicts.binds:
            found["var"] = _binding(verdicts.binds)
        anything: str | None
        if (anything := verdicts.anything or (verdicts.bounded if alone else None)) is not None:
            found["t"] = anything
        if verdicts.elements is not None:
            found["e"], found["of"] = verdicts.elements
        if verdicts.returned is not None:
            found["r"] = verdicts.returned
        if verdicts.awaited is not None:
            found["w"] = verdicts.awaited
        inner: ast.expr
        for inner in () if parameter.annotation is None else _classes(parameter.annotation):
            found[CLASS_VERDICT] = YES
            if isinstance(inner, ast.Name) and inner.id in self._variables(inner, module):
                found[CLASS_BINDS] = inner.id
        return found
