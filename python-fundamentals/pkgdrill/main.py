from .geometry import area_circle
from .text_tools import slugify


if __name__ == "__main__":
    print(f"slug={slugify('  Hello, World! ')} area={area_circle(5)}")
