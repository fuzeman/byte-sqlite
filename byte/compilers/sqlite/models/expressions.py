from byte.core.models import BaseProperty, Expressions, Node
from byte.core.models.expressions.base import (
    And,
    Between,
    Equal,
    GreaterThan,
    GreaterThanOrEqual,
    In,
    Is,
    IsNot,
    LessThan,
    LessThanOrEqual,
    Like,
    NotEqual,
    NotIn,
    Or,
    RegularExpression
)
from byte.core.models.expressions.proxy import BaseProxyExpression
from byte.compilers.sqlite.models.clause import SqliteClause
from byte.compilers.sqlite.models.entity import SqliteEntity
from byte.compilers.sqlite.models.set import SqliteSet

import inspect


# TODO Implement sqlite expressions
# __add__ = _e(OP.ADD)
# __sub__ = _e(OP.SUB)
# __mul__ = _e(OP.MUL)
# __div__ = __truediv__ = _e(OP.DIV)
# __xor__ = _e(OP.XOR)
# __radd__ = _e(OP.ADD, inv=True)
# __rsub__ = _e(OP.SUB, inv=True)
# __rmul__ = _e(OP.MUL, inv=True)
# __rdiv__ = __rtruediv__ = _e(OP.DIV, inv=True)
# __rand__ = _e(OP.AND, inv=True)
# __ror__ = _e(OP.OR, inv=True)
# __rxor__ = _e(OP.XOR, inv=True)
# __lt__ = _e(OP.LT)
# __le__ = _e(OP.LTE)
# __gt__ = _e(OP.GT)
# __ge__ = _e(OP.GTE)
# __lshift__ = _e(OP.IN)
# __rshift__ = _e(OP.IS)
# __mod__ = _e(OP.LIKE)
# __pow__ = _e(OP.ILIKE)
# bin_and = _e(OP.BIN_AND)
# bin_or = _e(OP.BIN_OR)
# __invert__
class SqliteExpressions(Expressions):
    @classmethod
    def match(cls, source):
        if hasattr(source, '__class__'):
            source = source.__class__

        # Find base class
        source_base = None

        for base in inspect.getmro(source):
            if base.__module__.startswith('byte.core.models.expressions.base'):
                source_base = base
                break

        if source_base is None:
            return None, None

        # Find matching expression
        for expression_cls in EXPRESSIONS:
            if issubclass(expression_cls, source_base):
                return source_base, expression_cls

        return source_base, None

    @classmethod
    def parse(cls, compiler, source):
        if not isinstance(source, BaseProxyExpression):
            return source

        # Find matching sqlite expression
        base_cls, expression_cls = cls.match(source)

        if not expression_cls:
            if base_cls:
                raise NotImplementedError('Unsupported expression: %s' % (base_cls.__name__,))

            raise NotImplementedError('Unsupported expression: %s' % (source.__class__.__name__,))

        # Transform `source` expression into `target_cls`
        if issubclass(expression_cls, SqliteManyExpression):
            return expression_cls(compiler, *[
                cls.parse(compiler, value)
                for value in source.values
            ])

        if issubclass(expression_cls, SqliteExpression):
            return expression_cls(compiler, source.lhs, source.rhs)

        raise NotImplementedError('Unsupported expression: %s' % (base_cls.__name__,))

    def and_(self, *values):
        return SqliteAnd(self, *values)

    def or_(self, *values):
        return SqliteOr(self, *values)

    def in_(self, rhs):
        return SqliteIn(self, rhs)

    def not_in(self, rhs):
        return SqliteNotIn(self, rhs)

    def is_null(self, is_null=True):
        if is_null:
            return SqliteIs(self, None)

        return SqliteIsNot(self, None)

    def contains(self, rhs):
        return SqliteLike(self, '%%%s%%' % rhs)

    def startswith(self, rhs):
        return SqliteLike(self, '%s%%' % rhs)

    def endswith(self, rhs):
        return SqliteLike(self, '%%%s' % rhs)

    def between(self, low, high):
        return SqliteBetween(self, SqliteSet(low, SqliteClause('AND'), high))

    def regexp(self, expression):
        return SqliteRegularExpression(self, expression)

    def concat(self, rhs):
        return SqliteStringExpression(self, rhs)

    def __and__(self, rhs):
        return And(self, rhs)

    def __eq__(self, rhs):
        if rhs is None:
            return SqliteIs(self, rhs)

        return SqliteEqual(self, rhs)

    def __ne__(self, rhs):
        if rhs is None:
            return SqliteIsNot(self, rhs)

        return SqliteNotEqual(self, rhs)

    def __or__(self, rhs):
        return SqliteOr(self, rhs)

    def __pos__(self):
        return self.asc()

    def __neg__(self):
        return self.desc()


class SqliteExpression(Node, SqliteExpressions):
    operator = None

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def compile(self):
        if not self.operator:
            raise NotImplementedError('%s.operator hasn\'t been defined' % (self.__class__.__name__,))

        parameters = []

        # Parse values
        lhs = self._compile_value(parameters, self.lhs)
        rhs = self._compile_value(parameters, self.rhs)

        # Compile clause
        return SqliteClause('%s %s %s' % (lhs, self.operator, rhs), *parameters).compile()

    def _compile_value(self, parameters, value):
        if isinstance(value, BaseProperty):
            statement, _ = SqliteEntity(self.compiler.table, value.name).compile()
            return statement

        parameters.append(value)
        return '?'


class SqliteManyExpression(Node, SqliteExpressions):
    operator = None

    def __init__(self, *values):
        self.values = values

    def compile(self):
        if not self.operator:
            raise NotImplementedError('%s.operator hasn\'t been defined' % (self.__class__.__name__,))

        return SqliteSet(*self.values, delimiter=' %s ' % (self.operator,)).compile()


class SqliteStringExpression(SqliteExpression):
    def __add__(self, other):
        return self.concat(other)

    def __radd__(self, other):
        return other.concat(self)


class SqliteAnd(And, SqliteManyExpression):
    operator = 'AND'


class SqliteBetween(Between, SqliteExpression):
    operator = 'BETWEEN'


class SqliteEqual(Equal, SqliteExpression):
    operator = '=='


class SqliteGreaterThan(GreaterThan, SqliteExpression):
    operator = '>'


class SqliteGreaterThanOrEqual(GreaterThanOrEqual, SqliteExpression):
    operator = '>='


class SqliteIn(In, SqliteExpression):
    operator = 'IN'


class SqliteIs(Is, SqliteExpression):
    operator = 'IS'


class SqliteIsNot(IsNot, SqliteExpression):
    operator = 'IS NOT'


class SqliteLessThan(LessThan, SqliteExpression):
    operator = '<'


class SqliteLessThanOrEqual(LessThanOrEqual, SqliteExpression):
    operator = '<='


class SqliteLike(Like, SqliteExpression):
    operator = 'LIKE'


class SqliteNotEqual(NotEqual, SqliteExpression):
    operator = '!='


class SqliteNotIn(NotIn, SqliteExpression):
    operator = 'NOT IN'


class SqliteOr(Or, SqliteManyExpression):
    operator = 'OR'


class SqliteRegularExpression(RegularExpression, SqliteExpression):
    operator = 'REGEXP'


EXPRESSIONS = [
    SqliteAnd,
    SqliteBetween,
    SqliteEqual,
    SqliteGreaterThan,
    SqliteGreaterThanOrEqual,
    SqliteIn,
    SqliteIs,
    SqliteIsNot,
    SqliteLessThan,
    SqliteLessThanOrEqual,
    SqliteLike,
    SqliteNotEqual,
    SqliteNotIn,
    SqliteOr,
    SqliteRegularExpression
]
