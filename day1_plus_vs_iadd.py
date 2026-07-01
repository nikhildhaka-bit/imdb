def reassign_with_plus(lst):
    print("id before:", id(lst))
    lst = lst + [4]          # creates a NEW list, rebinds local name
    print("id after: ", id(lst))
    print("inside function:", lst)


def mutate_with_iadd(lst):
    print("id before:", id(lst))
    lst += [4]                # mutates in place (list.__iadd__)
    print("id after: ", id(lst))
    print("inside function:", lst)


numbers = [1, 2, 3]
print("--- using lst = lst + [4] ---")
reassign_with_plus(numbers)
print("caller sees:", numbers)

print()

numbers = [1, 2, 3]
print("--- using lst += [4] ---")
mutate_with_iadd(numbers)
print("caller sees:", numbers)
