def raises(exc_type: type[BaseException], fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False


def greet(name: str, excited: bool = False) -> str:
    return f"Hello {name} {'!' if excited else '.'}"


def total(*numbers: float) -> float:
    print(type(numbers), numbers)
    return sum(numbers)


def show(**options) -> None:
    print(type(options), options)


def bad_add(x, bucket=[]) -> list:
    bucket.append(x)
    return bucket


# print(greet("Asha"))
# print(greet("Asha", excited=True))
# total(1, 2, 3)
# show(debug=True, port=8000)
# settings = {"debug": False, "port": 8000}
# show(**settings)
# print(bad_add(1), bad_add(2))


# answer predictions
# Hello Asha .
# Hello Asha !
# list [1,2,3]                              WRONG: <class 'tuple'> (1, 2, 3)
# dict {"debug":True, "port":8000}
# dict {"debug":False, "port":8000}
# [1,2]                                     WRONG: [1, 2] [1, 2]

# ===================================================================================================================


def clamp(value: int, low: int = 0, high: int = 100) -> int:
    if value < low:
        return low
    elif value > high:
        return high
    else:
        return value


def full_name(first: str, last: str, *, middle: str | None = None) -> str:
    # print(f"{first} {middle + ' ' if middl\e else ''}{last}")
    return f"{first} {middle + ' ' if middle else ''}{last}"


def add_item(item: str, bucket: list[str] | None = None) -> list[str]:
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


def build_url(base: str, **params) -> str:
    if params:
        base += "?"
        for i in params:
            base += f"{i}={params.get(i)}&"
        return base[:-1]
    return base


def describe(*numbers: float) -> dict:
    return {
        "count": len(numbers),
        "total": sum(numbers),
        "max": max(numbers) if len(numbers) > 0 else None,
    }



# tests (claude generated)

assert clamp(150) == 100
assert clamp(-5) == 0
assert clamp(7, low=10, high=20) == 10
assert clamp(15, 10, 20) == 15

assert full_name("Ada", "Lovelace") == "Ada Lovelace"
assert full_name("Ada", "Lovelace", middle="Byron") == "Ada Byron Lovelace"
assert raises(TypeError, full_name, "Ada", "Lovelace", "Byron")

assert add_item("a") == ["a"]
assert add_item("b") == ["b"]
shared = ["x"]
assert add_item("y", shared) == ["x", "y"] and shared == ["x", "y"]

assert build_url("https://x.io/search") == "https://x.io/search"
assert build_url("https://x.io/search", q="py", page=2) == "https://x.io/search?q=py&page=2"

assert describe(3, 1, 2) == {"count": 3, "total": 6, "max": 3}
assert describe() == {"count": 0, "total": 0, "max": None}
print("D1 B1 OK")
