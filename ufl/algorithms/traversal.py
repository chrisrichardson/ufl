"""This module contains algorithms for traversing expression trees, mostly using
generators and a kind of functional programming.

(Organizing algorithms by implementation technique is a temporary strategy
only to be used during the current experimental implementation phase)."""

from __future__ import absolute_import

__authors__ = "Martin Sandve Alnes"
__date__ = "2008-03-14 -- 2008-09-29"

# Modified by Anders Logg, 2008

from ..output import ufl_assert
from ..base import UFLObject, Terminal
from ..integral import Integral
from ..form import Form

#--- Traversal utilities ---

def iter_expressions(a):
    """Utility function to handle Form, Integral and any UFLObject
    the same way when inspecting expressions.
    Returns an iterable over UFLObject instances:
    - a is an UFLObject: (a,)
    - a is an Integral:  the integrand expression of a
    - a is a  Form:      all integrand expressions of all integrals
    """
    if isinstance(a, Form):
        return (itg._integrand for itg in a._integrals)
    elif isinstance(a, Integral):
        return (a._integrand,)
    else:
        return (a,)

def pre_traversal(expression, stack=[]):
    "Yields (o, stack) for each tree node o in expression, parent before child."
    ufl_assert(isinstance(expression, UFLObject), "Expecting UFLObject.")
    yield (expression, stack)
    is_operator = not isinstance(expression, Terminal)
    if is_operator: stack.append(expression)
    for o in expression.operands():
        for (i, dummy) in pre_traversal(o, stack):
            yield (i, stack)
    if is_operator: stack.pop()

def post_traversal(expression, stack=[]):
    "Yields (o, stack) for each tree node o in expression, parent after child."
    ufl_assert(isinstance(expression, UFLObject), "Expecting UFLObject.")
    is_operator = not isinstance(expression, Terminal)
    if is_operator: stack.append(expression)
    for o in expression.operands():
        for (i, dummy) in post_traversal(o, stack):
            yield (i, stack)
    if is_operator: stack.pop()
    yield (expression, stack)

def traversal(expression, stack=[]):
    "Yields (o, stack) for each tree node o in expression."
    return pre_traversal(expression, stack)

def pre_walk(a, func):
    """Call func on each expression tree node in a, parent before child.
    The argument a can be a Form, Integral or UFLObject."""
    for e in iter_expressions(a):
        for (o, stack) in pre_traversal(e):
            func(o)

def post_walk(a, func):
    """Call func on each expression tree node in a, parent after child.
    The argument a can be a Form, Integral or UFLObject."""
    for e in iter_expressions(a):
        for (o, stack) in post_traversal(e):
            func(o)

def walk(a, func):
    """Call func on each expression tree node in a.
    The argument a can be a Form, Integral or UFLObject."""
    pre_walk(a, func)
