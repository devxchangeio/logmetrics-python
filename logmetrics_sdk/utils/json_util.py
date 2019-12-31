
from datetime import date
from decimal import Decimal
from json import JSONEncoder, dumps, loads


class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, date):
            return o.isoformat()
        if hasattr(o, '__dict__'):
            return o.__dict__
        return super(DecimalEncoder, self).default(o)


def to_json(o, pretty=False) -> str:
    dumps_kwargs = {'cls': DecimalEncoder}
    pretty and dumps_kwargs.update({
        'sort_keys': True,
        'indent': 2
    })
    return dumps(to_object(o), **dumps_kwargs)


def to_object(o):
    return loads(o) if isinstance(o, str) else o
