from pkgdrill.geometry import area_circle
from pkgdrill.text_tools import slugify

assert slugify("  Hello, World! ") == "hello-world"
assert slugify("Python   is   FUN") == "python-is-fun"
assert area_circle(5) == 78.54
assert area_circle(0) == 0.0
print("PKGDRILL OK")
