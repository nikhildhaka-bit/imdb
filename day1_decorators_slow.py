def say_hello():
    return "hello!"


# functions are just values -- proof:
x = say_hello          # no parentheses! we're not CALLING it, just storing it
print(x)                # this prints the function object itself, not "hello!"
print(x())              # NOW we call it, via the variable x


print("---")

# a function that TAKES another function as input (the secretary)
def secretary(boss_function):
    print("secretary: phone is ringing, let me announce it...")
    result = boss_function()          # secretary calls the boss for you
    print("secretary: boss said their piece, call is done.")
    return result


print(secretary(say_hello))

print("---")

# now: a secretary that returns a NEW phone number (function),
# instead of handling the call immediately
def make_secretary(boss_function):
    def new_phone_number():                    # this is the "wrapper"
        print("secretary: phone is ringing, let me announce it...")
        result = boss_function()
        print("secretary: boss said their piece, call is done.")
        return result
    return new_phone_number                     # return the FUNCTION, don't call it


upgraded_hello = make_secretary(say_hello)
print(upgraded_hello)          # a function object -- nothing has run yet!
print(upgraded_hello())        # NOW it runs

print("---")

# THE KEY MOVE: what if we reuse the ORIGINAL name instead of a new one?
say_hello = make_secretary(say_hello)
#   ^^^^^^^^   this OVERWRITES "say_hello" to now point at new_phone_number
#              the original say_hello still exists in memory, but only
#              new_phone_number's closure can still reach it

print(say_hello())     # looks like we're calling the original... but we're not!


print("---")

# this exact line -- name = decorator(name) -- is ALL "@decorator" syntax does.
# so this:
@make_secretary
def say_hi():
    return "hi!"

# is 100% equivalent to writing:
#   def say_hi(): return "hi!"
#   say_hi = make_secretary(say_hi)

print(say_hi())
