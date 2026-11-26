# # # class Animal:  # the parent
# # #     def __init__(self, name: str) -> None:
# # #         self.name = name

# # #     def speak(self) -> str:
# # #         return "..."

# # #     def intro(self) -> str:
# # #         return f"{self.name} says {self.speak()}"


# # # class Dog(Animal):  # Dog inherits from Animal (the parent goes in brackets)
# # #     def speak(self) -> str:  # ...and replaces speak()
# # #         return "Woof"


# # # class Cat(Animal):
# # #     def speak(self) -> str:
# # #         return "Meow"


# # # rex = Dog("Rex")
# # # print(rex.name)  # Rex
# # # print(rex.intro())  # Rex says Woof


# class Employee:
#     def __init__(self, name: str, salary: int):
#         self.name = name
#         self.salary = salary

#     def describe(self):
#         return f"name:{self.name!r} earns salary:{self.salary}"


# class Manager(Employee):
#     def __init__(self, name: str, salary: int, reports: list[str] | None = None):
#         super().__init__(name, salary)
#         self.reports = reports

#     def describe(self):
#         return f"super().describe() and manages {len(self.reports) if self.reports is not None else 0} people"


# # k = Manager("kishore", 100000, ["james", "john"])
# # a = Manager("arun", 100000)
# # j = Employee("john", 75000)

# # print(k.describe())
# # print(a.describe())
# # print(j.describe())


# # P5
class Animal:
    def speak(self):
        return "..."

    def intro(self):
        return "I say " + self.speak()


class Dog(Animal):
    def speak(self):
        return "Woof"


# print(Animal().intro(), Dog().intro())


# # P6
# class A:
#     def __init__(self):
#         print("A init")


# class B(A):
#     def __init__(self):
#         print("B init")


# B()


# # P7
# class C(A):
#     def __init__(self):
#         super().__init__()
#         print("C init")


# C()

# # P8
# print(isinstance(Dog(), Animal), isinstance(Animal(), Dog), issubclass(Dog, Animal))


def raises(exc_type, fn, *args, **kwargs) -> bool:
    try:
        fn(*args, **kwargs)
    except exc_type:
        return True
    return False


from dataclasses import dataclass
import math


class Shape:
    def area(self):
        raise NotImplementedError


@dataclass
class Rectangle(Shape):
    width: int
    height: int

    def area(self):
        return self.width * self.height


@dataclass
class Circle(Shape):
    radius: int

    def area(self):
        return self.radius * self.radius * math.pi


def total_area(shapes: list[Shape]) -> float:
    total = 0
    for shape in shapes:
        total += shape.area()

    return total


# ============


class Animal:  # the parent
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."

    def intro(self) -> str:
        return f"{self.name} says {self.speak()}"


class Dog(Animal):  # Dog inherits from Animal (the parent goes in brackets)
    def speak(self) -> str:  # ...and replaces speak()
        return "Woof"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow"


def chorus(animals: list[Animal]) -> list[str]:
    return [f"{a.name}: {a.speak()}" for a in animals]


chorus([Dog("Rex"), Cat("Tom"), Animal("Generic")])
# ['Rex: Woof', 'Tom: Meow', 'Generic: ...']

# ==========


class Employee:
    def __init__(self, name: str, salary: int):
        self.name = name
        self.salary = salary

    def describe(self):
        return f"{self.name} earns {self.salary}"


class Manager(Employee):
    def __init__(self, name: str, salary: int, reports: list[str] | None = None):
        super().__init__(name, salary)
        self.reports = reports if reports is not None else []

    def describe(self):
        return f"{super().describe()} and manages {len(self.reports) if self.reports is not None else 0} people"


pets = [Dog("Rex"), Cat("Tom"), Animal("Generic")]
assert chorus(pets) == ["Rex: Woof", "Tom: Meow", "Generic: ..."]
assert isinstance(pets[0], Animal) and not isinstance(pets[2], Dog)
assert issubclass(Cat, Animal)

assert Rectangle(3, 4).area() == 12
assert math.isclose(Circle(1).area(), math.pi)
assert raises(NotImplementedError, Shape().area)
assert math.isclose(total_area([Rectangle(2, 5), Circle(2)]), 10 + 4 * math.pi)

assert Employee("Ravi", 50).describe() == "Ravi earns 50"
assert (
    Manager("Asha", 90, ["a", "b"]).describe() == "Asha earns 90 and manages 2 people"
)
assert isinstance(Manager("x", 1), Employee)
m1, m2 = Manager("x", 1), Manager("y", 2)
m1.reports.append("z")
assert m2.reports == []
print("D3 P2 OK")
