from urllib.parse import unquote


def parse_qs(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace'):
    params = {}
    for p in qs.split('&'):
        if '=' not in p:
            if strict_parsing:
                raise ValueError('bad query field: %s' % p)
            if keep_blank_values:
                params[p] = ''
            continue
        k, v = p.split('=')
        if v or keep_blank_values:
            params[k] = unquote(v, encoding=encoding, errors=errors)
    return params
