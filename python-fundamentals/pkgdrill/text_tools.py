def slugify(text: str) -> str:
    res = ""
    for c in text.strip():
        if c.isalnum() or c == " " or c == "-":
            res += c.lower()
        else:
            pass

    return "-".join(res.split())
