#coding=utf8

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import Query
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.orm.util import _entity_descriptor
from sqlalchemy.util import to_list
from sqlalchemy.sql import operators, extract

# MySQL using SQLAlchemy

class DjangoQuery(Query):
    """
    DjangoQuery From
    https://github.com/mitsuhiko/sqlalchemy-django-query

    Can be mixed into any Query class of SQLAlchemy and extends it to
    implements more Django like behavior:

    -   `filter_by` supports implicit joining and subitem accessing with
        double underscores.
    -   `exclude_by` works like `filter_by` just that every expression is
        automatically negated.
    -   `order_by` supports ordering by field name with an optional `-`
        in front.
    """
    _underscore_operators = {
        'gt':           operators.gt,
        'lte':          operators.lt,
        'gte':          operators.ge,
        'le':           operators.le,
        'contains':     operators.contains_op,
        'in':           operators.in_op,
        'exact':        operators.eq,
        'iexact':       operators.ilike_op,
        'startswith':   operators.startswith_op,
        'istartswith':  lambda c, x: c.ilike(x.replace('%', '%%') + '%'),
        'iendswith':    lambda c, x: c.ilike('%' + x.replace('%', '%%')),
        'endswith':     operators.endswith_op,
        'isnull':       lambda c, x: x and c != None or c == None,
        'range':        operators.between_op,
        'year':         lambda c, x: extract('year', c) == x,
        'month':        lambda c, x: extract('month', c) == x,
        'day':          lambda c, x: extract('day', c) == x
    }

    def filter_by(self, **kwargs):
        return self._filter_or_exclude(False, kwargs)

    def exclude_by(self, **kwargs):
        return self._filter_or_exclude(True, kwargs)

    def select_related(self, *columns, **options):
        depth = options.pop('depth', None)
        if options:
            raise TypeError('Unexpected argument %r' % iter(options).next())
        if depth not in (None, 1):
            raise TypeError('Depth can only be 1 or None currently')
        need_all = depth is None
        columns = list(columns)
        for idx, column in enumerate(columns):
            column = column.replace('__', '.')
            if '.' in column:
                need_all = True
            columns[idx] = column
        func = (need_all and joinedload_all or joinedload)
        return self.options(func(*columns))

    def order_by(self, *args):
        args = list(args)
        joins_needed = []
        for idx, arg in enumerate(args):
            q = self
            if not isinstance(arg, basestring):
                continue
            if arg[0] in '+-':
                desc = arg[0] == '-'
                arg = arg[1:]
            else:
                desc = False
            q = self
            column = None
            for token in arg.split('__'):
                column = _entity_descriptor(q._joinpoint_zero(), token)
                if column.impl.uses_objects:
                    q = q.join(column)
                    joins_needed.append(column)
                    column = None
            if column is None:
                raise ValueError('Tried to order by table, column expected')
            if desc:
                column = column.desc()
            args[idx] = column

        q = super(DjangoQuery, self).order_by(*args)
        for join in joins_needed:
            q = q.join(join)
        return q

    def _filter_or_exclude(self, negate, kwargs):
        q = self
        negate_if = lambda expr: expr if not negate else ~expr
        column = None

        for arg, value in kwargs.iteritems():
            for token in arg.split('__'):
                if column is None:
                    column = _entity_descriptor(q._joinpoint_zero(), token)
                    if column.impl.uses_objects:
                        q = q.join(column)
                        column = None
                elif token in self._underscore_operators:
                    op = self._underscore_operators[token]
                    q = q.filter(negate_if(op(column, *to_list(value))))
                    column = None
                else:
                    raise ValueError('No idea what to do with %r' % token)
            if column is not None:
                q = q.filter(negate_if(column == value))
                column = None
            q = q.reset_joinpoint()
        return q

class Model(object):
    id = Column(Integer, primary_key=True) #primary key

    query = None

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def save(self, **kwargs):
        """
        提供直接保存的方法
        用法:
            1. 根据参数保存
            >>> user.save(name="bigman", email="b@ig.man")

            2. 直接保存
            >>> user.name = "bigman"
            >>> user.save()
        """
        if kwargs:
            for k, v in kwargs.iteritems():
                setattr(self, k, v)
        self.db.add(self)
        self.db.commit()

class SQLAlchemy(object):
    """
    Example::
        db = SQLAlchemy("sqlite:///bitch.sqlite", True)
        from sqlalchemy import Column, String
        class User(db.Model):
            username = Column(String(16), unique=True, nullable=False, index=True)
            password = Column(String(30), nullable=False)
        >>> db.create_db()
        >>> User.query.filter_by(username='yourname')
    """

    def __init__(self, db_config, **kwargs):
        db_url = '%(dialect)s+%(driver)s://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s' % db_config
        self.engine = create_engine(db_url, convert_unicode=True, echo=db_config['debug'])
        self.session = self.create_session()
        self.Model = self.create_model()

    def create_session(self):
        session = sessionmaker(bind=self.engine, query_cls=DjangoQuery)
        return scoped_session(session)

    def create_model(self):
        base = declarative_base(cls=Model, name='Model')
        base.query = self.session.query_property()
        base._resource = True
        base.db = self.session
        return base

    def create_db(self, admin=False):
        """init table from model ?"""
        if admin:
            self.Model.metadata.drop_all(self.engine)
            self.Model.metadata.create_all(self.engine)
