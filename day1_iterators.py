class MoviePlaylist:
    def __init__(self, titles):
        self.titles = titles
        self.position = 0          # bookmark: "which page am I on?"

    def __iter__(self):
        return self                # "I know how to be iterated -- it's me"

    def __next__(self):
        if self.position >= len(self.titles):
            raise StopIteration     # "I'm done, nothing left"
        title = self.titles[self.position]
        self.position += 1          # move the bookmark forward
        return title


playlist = MoviePlaylist(["Inception", "Tenet", "Interstellar"])

print(playlist.__next__())
print(playlist.__next__())
print(playlist.__next__())

print("---")

# a fresh playlist -- the old one's bookmark already reached the end
playlist2 = MoviePlaylist(["Inception", "Tenet", "Interstellar"])

for movie in playlist2:
    print("watching:", movie)

print("loop finished cleanly -- no crash, no visible StopIteration")
