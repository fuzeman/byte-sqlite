"""byte-sqlite - compiler base module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.core.base import Compiler
from byte.expressions import (
    And, CompoundExpression, MultiExpression, Equal, GreaterThan, GreaterThanOrEqual,
    LessThan, LessThanOrEqual, NotEqual, Or
)
from byte.property import Property, PropertyExpression

from six import string_types


class BaseSqliteCompiler(Compiler):
    """Base SQLite compiler class."""

    def __init__(self, executor):
        """Create base SQLite compiler.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor
        """
        super(BaseSqliteCompiler, self).__init__(executor)

        self.table = self.collection.parameters.get('table')

    def encode_expressions(self, expressions):
        """Encode expressions into SQLite clause.

        :param expressions: Expressions
        :type expressions: list of byte.base.BaseExpression
        """
        for expression in expressions:
            yield self.encode_expression(expression)

    def encode_expression(self, expression):
        """Encode expression into SQLite expression.

        :param expression: Expression
        :type expression: byte.base.BaseExpression
        """
        if isinstance(expression, CompoundExpression):
            return self.encode_expression_compound(expression)

        if isinstance(expression, MultiExpression):
            return self.encode_expression_multi(expression)

        raise NotImplementedError

    def encode_expression_compound(self, expression):
        """Encode compound-expression into SQLite expression.

        :param expression: Compound-expression
        :type expression: byte.expressions.CompoundExpression
        """
        operator = self.get_operator(expression)

        if isinstance(expression.left, Property) and isinstance(expression.right, Property):
            return Clause('%s %s %s' % (
                self.encode_property(expression.left),
                operator,
                self.encode_property(expression.right)
            ))
        elif isinstance(expression.left, Property):
            return Clause(
                '%s %s ?' % (
                    self.encode_property(expression.left),
                    operator
                ),
                expression.right
            )
        elif isinstance(expression.right, Property):
            return Clause(
                '? %s %s' % (
                    operator,
                    self.encode_property(expression.right)
                ),
                expression.left
            )

        return Clause(
            '? %s ?' % operator,
            expression.left,
            expression.right
        )

    def encode_expression_multi(self, expression):
        """Encode multi-expression into SQLite expression.

        :param expression: Multi-expression
        :type expression: byte.expressions.MultiExpression
        """
        delimiter = self.get_delimiter(expression)

        clauses = [
            self.encode_expression(ex)
            for ex in expression.values
        ]

        return self.join(delimiter, clauses)

    def encode_property(self, value):
        """Encode property into SQLite table name."""
        if isinstance(value, Property):
            value = value.name

        return '"%s"."%s"' % (self.table, value)

    def get_delimiter(self, expression):
        """Retrieve delimiter for expression.

        :param expression: Expression
        :type expression: byte.base.BaseExpression
        """
        if isinstance(expression, And):
            return 'AND'

        if isinstance(expression, Or):
            return 'OR'

        raise NotImplementedError

    def get_operator(self, expression):
        """Retrieve operator for expression.

        :param expression: Expression
        :type expression: byte.base.BaseExpression
        """
        if isinstance(expression, Equal):
            return '='

        if isinstance(expression, GreaterThan):
            return '>'

        if isinstance(expression, GreaterThanOrEqual):
            return '>='

        if isinstance(expression, LessThan):
            return '<'

        if isinstance(expression, LessThanOrEqual):
            return '<='

        if isinstance(expression, NotEqual):
            return '!='

        raise NotImplementedError

    def add_properties(self, clauses, properties):
        """Add properties to :code:`clauses` list.

        :param clauses: Clauses
        :type clauses: list

        :param properties: Properties
        :type properties: list of byte.base.BaseProperty
        """
        if not properties:
            clauses.append('*')
            return

        for i, column in enumerate(properties):
            if isinstance(column, Property):
                column = column.name
            elif isinstance(column, PropertyExpression):
                column = column.value.name
            elif not isinstance(column, string_types):
                raise ValueError(
                    'Invalid value provided for property (expected Property, PropertyExpression or string)'
                )

            # Add property
            clauses.append('"%s"."%s"%s' % (
                self.table,
                column,
                ',' if i < len(properties) - 1 else ''
            ))

    def join(self, delimiter, clauses):
        """Join :code:`clauses` with :code:`delimiter`.

        :param delimiter: Delimiter
        :type delimiter: str

        :param clauses: Clauses
        :type clauses: list of Clause
        """
        statements = []
        parameters = []

        for clause in clauses:
            if isinstance(clause, Clause):
                statements.append(clause.statement)
                parameters.extend(clause.parameters)
            else:
                statements.append(clause)

        return Clause((' %s ' % (delimiter,)).join(statements), *parameters)

    def merge(self, clauses):
        """Merge :code:`clauses` into SQLite statement.

        :param clauses: Clauses
        :type clauses: list of Clause
        """
        statements = []
        parameters = []

        for clause in clauses:
            if isinstance(clause, Clause):
                statements.append(clause.statement)
                parameters.extend(clause.parameters)
            else:
                statements.append(clause)

        return ' '.join(statements) + ';', tuple(parameters)


class Clause(object):
    """SQlite Clause class."""

    def __init__(self, statement, *parameters):
        """Create SQLite clause.

        :param statement: Statement
        :type statement: str

        :param parameters Parameters
        :type parameters: tuple
        """
        self.statement = statement
        self.parameters = parameters

    def __repr__(self):
        if not self.parameters:
            return 'Clause(%r)' % (self.statement,)

        return 'Clause(%r, %s)' % (
            self.statement,
            ', '.join([
                repr(value) for value in self.parameters
            ])
        )
