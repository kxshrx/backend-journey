# comprehensions: build a new collection in one readable line
nums = [1, 2, 3, 4, 5, 6]
evens = [n for n in nums if n % 2 == 0]
squares = {n: n * n for n in nums}
lengths = {len(w) for w in ["a", "bb", "cc"]}
flat = [x for row in [[1, 2], [3]] for x in row]

# dicts
user = {"name": "Asha", "age": 30}
user.get("email")
user.get("email", "n/a")
for k, v in user.items():
    ...

# counting and grouping
from collections import Counter, defaultdict

Counter("Mississippi").most_common(2)
groups = defaultdict(list)
groups[3].append("sup")


# sorting with a key function; tuples sort element by element
people = [("zed", 30), ("amy", 20)]
sorted(people, key=lambda p: p[1])
sorted(people, key=lambda p: (-p[1], p[0]))


for i, name in enumerate(["a", "b"], start=1):
    ...
for name, score in [("a", "b"), [10, 20]]:
    ...
any(n > 0 for n in nums)
all(n > 0 for n in nums)

# unpacking
first, *rest = [1, 2, 3]
a, b = 1, 2
a, b = b, a

a = [1, 2]
b = a #same list but two diff variable names
b.append(3)
print(a)

c = a.copy() #seperate lists
c.append(4)
print(a, c)

grid = [[0] * 2] * 2
grid[0][0] = 9

print(grid)


# predict:
# [1,2]
# ([1,2] [1,4])

# output
# [1, 2, 3]
# [1, 2, 3] [1, 2, 3, 4]
# [[9, 0], [9, 0]]