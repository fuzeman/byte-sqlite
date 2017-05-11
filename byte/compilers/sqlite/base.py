from byte.compilers.core.base import Compiler
from byte.expressions import (
    And, CompoundExpression, MultiExpression, Equal, GreaterThan, GreaterThanOrEqual,
    LessThan, LessThanOrEqual, NotEqual, Or
)
from byte.property import Property, PropertyExpression

from six import string_types


class BaseSqliteCompiler(Compiler):
    def __init__(self, executor):
        super(BaseSqliteCompiler, self).__init__(executor)

        self.table = self.collection.parameters.get('table')

    def encode_expressions(self, expressions):
        for expression in expressions:
            yield self.encode_expression(expression)

    def encode_expression(self, expression):
        if isinstance(expression, CompoundExpression):
            return self.encode_expression_compound(expression)

        if isinstance(expression, MultiExpression):
            return self.encode_expression_multi(expression)

        raise NotImplementedError

    def encode_expression_compound(self, expression):
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
        delimiter = self.get_delimiter(expression)

        clauses = [
            self.encode_expression(ex)
            for ex in expression.values
        ]

        return self.join(delimiter, clauses)

    def encode_property(self, value):
        if isinstance(value, Property):
            value = value.name

        return '"%s"."%s"' % (self.table, value)

    def get_delimiter(self, expression):
        if isinstance(expression, And):
            return 'AND'

        if isinstance(expression, Or):
            return 'OR'

        raise NotImplementedError

    def get_operator(self, expression):
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
    def __init__(self, statement, *parameters):
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
