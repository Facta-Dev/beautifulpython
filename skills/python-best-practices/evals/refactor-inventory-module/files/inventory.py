import json


_REGISTRY = {}


class InventoryError(Exception):
    pass


class Item:
    def __init__(self, name, qty, price_cents, is_perishable):
        self.name = name
        self.qty = qty
        self.price_cents = price_cents
        self.is_perishable = is_perishable


def get_registry():
    return _REGISTRY


def add_item(name, qty=0, price_cents=0, is_perishable=False, verbose=False, items=_REGISTRY):
    if qty < 0 or price_cents < 0:
        raise InventoryError("invalid numbers for " + name)
    items[name] = Item(name, qty, price_cents, is_perishable)


def get_item(name):
    global _REGISTRY
    if name in _REGISTRY:
        return _REGISTRY[name]
    else:
        return None


def total_value(names):
    total = 0
    for n in names:
        item = _REGISTRY[n]
        total = total + item.qty * item.price_cents
    return total


def restock(name, amount):
    item = _REGISTRY[name]
    item.qty += amount
    _REGISTRY[name] = item
    return item.qty


def parse_line(line):
    parts = line.split(",")
    if len(parts) != 4:
        raise InventoryError("bad line: " + line)
    qty = int(parts[1])
    price = int(parts[2])
    if parts[3].strip() == "true":
        perishable = True
    else:
        perishable = False
    return Item(parts[0].strip(), qty, price, perishable)


def load(path):
    f = open(path)
    try:
        text = f.read()
    except Exception:
        pass
    for line in text.splitlines():
        if not line.strip():
            continue
        item = parse_line(line)
        _REGISTRY[item.name] = item


def report(verbose=False):
    s = ""
    for k in _REGISTRY:
        v = _REGISTRY[k]
        s = s + k + ": " + str(v.qty) + "\n"
        if verbose == True:
            s = s + "  price=" + str(v.price_cents) + " perishable=" + str(v.is_perishable) + "\n"
    return s


def to_json(items=None):
    """Serialize item names to JSON."""
    return json.dumps([i.name for i in items])