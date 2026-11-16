from collections import defaultdict, Counter


def unique_sorted(words: list[str]) -> list[str]:
    unique = []
    for w in words:
        if w.lower() in unique:
            continue
        unique.append(w.lower())
    return sorted(unique)


def group_by_length(words: list[str]) -> dict[int, list[str]]:
    lengths = defaultdict(list)
    for w in words:
        lengths[len(w)].append(w)
    print(lengths)
    return lengths


def word_freq(text: str) -> dict[str, int]:
    return Counter([t.strip(".,!?").lower() for t in text.split(" ")])


def invert(d: dict[str, int]) -> dict[int, str]:
    temp = {}
    for k, v in d.items():
        temp[v] = k
    return temp


def top_n(scores: dict[str, int], n: int) -> list[str]:
    topn = []
    for person, marks in scores.items():
        topn.append([person, marks])
    sorted_topn = sorted(topn, key=lambda p: (-p[1], p[0]))
    res = [person for person, marks in sorted_topn[:n]]
    return res


def flatten(nested: list[list[int]]) -> list[int]:
    return [x for row in nested for x in row]




# claude tests
assert unique_sorted(["b", "A", "a", "c", "B"]) == ["a", "b", "c"]
assert group_by_length(["hi", "yo", "sup", "hey"]) == {
    2: ["hi", "yo"],
    3: ["sup", "hey"],
}
assert word_freq("The cat. The dog!") == {"the": 2, "cat": 1, "dog": 1}
assert invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}
scores = {"zed": 5, "amy": 9, "bob": 9, "cy": 1}
assert top_n(scores, 3) == ["amy", "bob", "zed"]
assert top_n(scores, 1) == ["amy"]
assert flatten([[1, 2], [3], []]) == [1, 2, 3]
print("D1 B2 OK")
