def mutate_list(lst):
    lst.append(4)
    print("inside mutate_list:", lst)


def reassign_list(lst):
    lst = [100, 200, 300]
    print("inside reassign_list:", lst)


numbers = [1, 2, 3]

mutate_list(numbers)
print("after mutate_list, caller sees:", numbers)

reassign_list(numbers)
print("after reassign_list, caller sees:", numbers)


# --- Now the classic mutable-default-argument bug ---

def add_movie(title, watchlist=None):
    if watchlist is None:
        watchlist = []
    watchlist.append(title)
    return watchlist


print(add_movie("Inception"))
print(add_movie("Interstellar"))
print(add_movie("Tenet"))
