"""Re-break mongosh output lines to fit the screen without changing a single character.

* If every line already fits and compact is off, the text is returned exactly as mongosh printed it.
* Otherwise it is re-broken the way mongosh breaks long values (one property per line, short value
  lists filled across), at a narrower width. compact=True packs all-value objects across lines.
* check() proves the result equals the original once whitespace is ignored; the build fails if not.
"""
import re
import textwrap

TOK = re.compile(r"""(?P<str>'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|(?P<call>[A-Za-z_]\w*\([^()]*\))|(?P<p>[{}\[\],:])|(?P<atom>[^\s{}\[\],:'"]+)""")


def _tokens(s):
    out, pos, s = [], 0, s.strip()
    while pos < len(s):
        if s[pos].isspace():
            pos += 1
            continue
        m = TOK.match(s, pos)
        if not m:
            raise ValueError("cannot tokenize")
        out.append(m.group(m.lastgroup))
        pos = m.end()
    return out


def _parse(tokens):
    i = 0

    def val():
        nonlocal i
        t = tokens[i]
        if t in ("{", "["):
            close = "}" if t == "{" else "]"
            kind = "obj" if t == "{" else "arr"
            i += 1
            items = []
            if tokens[i] == close:
                i += 1
                return (kind, items)
            while True:
                if kind == "obj":
                    key = tokens[i]
                    i += 1
                    if tokens[i] != ":":
                        raise ValueError("expected ':'")
                    i += 1
                    items.append((key, val()))
                else:
                    items.append(val())
                if tokens[i] == ",":
                    i += 1
                    continue
                if tokens[i] != close:
                    raise ValueError("expected " + close)
                i += 1
                return (kind, items)
        if t in ("}", "]", ",", ":"):
            raise ValueError("unexpected " + t)
        i += 1
        return ("atom", t)

    v = val()
    if i != len(tokens):
        raise ValueError("trailing tokens")
    return v


def _inline(v):
    kind, body = v
    if kind == "atom":
        return body
    if kind == "obj":
        return "{}" if not body else "{ " + ", ".join(f"{k}: {_inline(x)}" for k, x in body) + " }"
    return "[]" if not body else "[ " + ", ".join(_inline(x) for x in body) + " ]"


def _flat(v):
    kind, body = v
    if kind == "atom":
        return True
    vals = [x for _, x in body] if kind == "obj" else body
    return all(x[0] == "atom" for x in vals)


def _fill(pieces, first, pad, width):
    lines, cur = [], first
    for piece in pieces:
        if cur.strip() and cur != first and len(cur) + 1 + len(piece) > width:
            lines.append(cur.rstrip())
            cur = pad + piece
        elif cur == first:
            cur = cur + piece
        else:
            cur = cur + " " + piece
    lines.append(cur.rstrip())
    return lines


def _render(v, ind, width, compact, pre="", suf=""):
    pad = " " * ind
    one = pad + pre + _inline(v) + suf
    kind, body = v
    if len(one) <= width or kind == "atom":
        return [one]
    if compact and _flat(v) and body:
        raw = [f"{k}: {x[1]}" for k, x in body] if kind == "obj" else [x[1] for x in body]
        opener, closer = ("{ ", " }") if kind == "obj" else ("[ ", " ]")
        pieces = [p + "," for p in raw[:-1]] + [raw[-1] + closer + suf]
        packed = _fill(pieces, pad + pre + opener, pad + "  ", width)
        if max(len(x) for x in packed) <= width:
            return packed
    lines = [pad + pre + ("{" if kind == "obj" else "[")]
    if kind == "arr" and _flat(v):
        pieces = [x[1] + "," for x in body[:-1]] + [body[-1][1]]
        lines += _fill(pieces, pad + "  ", pad + "  ", width)
    else:
        for j, x in enumerate(body):
            s2 = "," if j < len(body) - 1 else ""
            if kind == "obj":
                lines += _render(x[1], ind + 2, width, compact, x[0] + ": ", s2)
            else:
                lines += _render(x, ind + 2, width, compact, "", s2)
    lines.append(pad + ("}" if kind == "obj" else "]") + suf)
    return lines


def squash(s):
    return re.sub(r"\s", "", s)


def check(original, shown):
    if squash(original) != squash(shown):
        raise AssertionError("reflow changed characters:\n" + original + "\n---\n" + shown)
    return shown


def reflow(text, width, compact=False):
    if not text:
        return text
    lines = text.split("\n")
    if max(len(x) for x in lines) <= width and not compact:
        return text
    try:
        v = _parse(_tokens(text))
    except (ValueError, IndexError):
        out = "\n".join(w for line in lines for w in (textwrap.wrap(line, width, break_long_words=True) or [""]))
        return check(text, out)
    out = _render(v, 0, width, compact)
    if compact and len(out) >= len(lines) and max(len(x) for x in lines) <= width:
        return text
    return check(text, "\n".join(out))
