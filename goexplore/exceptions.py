def ensure_type(obj, obj_type, name, desc):
    if not isinstance(obj, obj_type):
        expected_type_name = obj_type.__name__
        type_name = type(obj).__name__
        raise TypeError('%s `%s` expected %s, but found %s' % (desc, name, expected_type_name, type_name))

def ensure_range(obj, obj_type, name, desc, minn=None, maxx=None):
    if maxx is None:
        expected_range = f'>= {minn}'
        if obj >= minn:
            return
    elif minn is None:
        expected_range = f'<= {maxx}'
        if obj <= maxx:
            return
    else:
        expected_range = f'in the range {minn}-{maxx}'
        if obj >= minn and obj <= maxx:
            return

    expected_type_name = obj_type.__name__
    raise ValueError(f'%s `%s` expected %s %s, but found {obj}' % (desc, name, expected_type_name, expected_range))

def ensure_from(obj, valid, name, desc, delimeter='/'):
    if not obj in valid:
        raise ValueError(f'Expected {desc} `{name}` to be one of {delimeter.join(valid)}, but found \'{obj}\'')
