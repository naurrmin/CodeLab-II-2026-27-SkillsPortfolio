"""Exercise 2 - Alexa tell me a Joke (Tkinter), Dead-Letter Box edition.

Extras on top of the brief: back buttons, a postcard that flips to show the punchline, jokes typed
out letter by letter, a favourites list, no repeats until every joke has been told, and a stamp
collection that fills up as you hear more jokes.
"""
import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

import coquette as cq

HERE = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(HERE, "randomJokes.txt")
SAMPLE_JOKES = [
    ("Why did the chicken cross the road?", "To get to the other side."),
    ("What happens if you boil a clown?", "You get a laughing stock."),
]
FAVOURITES_FILE = os.path.join(HERE, "favourites.json")
STAMPS = [(1, "bow", "First letter"), (5, "teddy", "5 letters"), (10, "heart", "10 letters"), (20, "star", "20 letters")]


def findJokesFile():
    """Look for randomJokes.txt next to this script, in a resources folder, or where Python was started."""
    for folder in (HERE, os.path.join(HERE, "resources"), os.getcwd(), os.path.join(os.getcwd(), "resources")):
        path = os.path.join(folder, "randomJokes.txt")
        if os.path.exists(path):
            return path
    return None


def loadJokes(filename):
    """Read the file and return a list of (setup, punchline) tuples."""
    jokes = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "?" not in line:
                continue
            setup, punchline = line.split("?", 1)
            jokes.append((setup + "?", punchline.strip()))
    return jokes


def loadFavourites():
    try:
        with open(FAVOURITES_FILE, "r", encoding="utf-8") as file:
            return [tuple(joke) for joke in json.load(file)]
    except (OSError, ValueError):
        return []


def saveFavourites(favourites):
    try:
        with open(FAVOURITES_FILE, "w", encoding="utf-8") as file:
            json.dump(favourites, file)
    except OSError:
        pass


class JokeApp(tk.Tk):
    def __init__(self, jokes):
        super().__init__()
        self.title("Alexa tell me a Joke")
        self.geometry("580x680")
        self.resizable(False, False)
        cq.applyTheme(self)
        self.body = cq.makePaper(self, "Alexa tell me a Joke", "The Dead-Letter Comedy Box")

        self.jokes = jokes
        self.deck = []              # jokes not told yet
        self.currentJoke = None
        self.heard = 0
        self.favourites = loadFavourites()
        self.jobs = []              # running after() jobs (typing, flipping)

        self.home()

    # --- helpers ---

    def newScreen(self):
        for job in self.jobs:
            self.after_cancel(job)
        self.jobs = []
        cq.clear(self.body)
        return self.body

    def points(self):
        return min(100, self.heard * 5)

    def later(self, ms, func):
        self.jobs.append(self.after(ms, func))

    # --- home: the postbox ---

    def home(self):
        frame = self.newScreen()
        c = tk.Canvas(frame, width=480, height=235, bg=cq.PAPER, highlightthickness=0)
        c.pack(pady=(4, 0))
        cq.bunting(c, 8, 472, 6)
        c.create_line(20, 226, 460, 226, fill=cq.INK, width=2)
        cq.drawSprite(c, "teddy", 85, 175, 1.6)
        cq.drawSprite(c, "envelope", 135, 205, .9)
        cq.drawPostbox(c, 245, 226, 1.0)
        cq.drawSprite(c, "bow", 375, 170, 1.4)
        cq.drawSprite(c, "heart", 425, 100, 1.0)
        cq.drawSprite(c, "envelope", 345, 90, .9)

        ttk.Label(frame, text="Draw a letter from the postbox", style="Sub.TLabel").pack(pady=(2, 2))
        ttk.Label(frame, text=f"{cq.rankFor(self.points())}  ·  letters opened: {self.heard}").pack(pady=(0, 12))
        ttk.Button(frame, text="✉  Alexa tell me a Joke", width=30, command=self.tellJoke).pack(pady=5)
        ttk.Button(frame, text="My Favourites ♥", width=30, command=self.showFavourites).pack(pady=5)
        ttk.Button(frame, text="My Stamp Collection ✦", width=30, command=self.showStamps).pack(pady=5)
        ttk.Button(frame, text="Quit", width=30, command=self.destroy).pack(pady=5)

    # --- the joke screen ---

    def tellJoke(self):
        """Pick a random joke, show the setup and hide the punchline."""
        if not self.deck:
            self.deck = list(self.jokes)
        self.currentJoke = random.choice(self.deck)
        self.deck.remove(self.currentJoke)
        self.heard += 1
        self.showJokeScreen()
        for needed, kind, name in STAMPS:
            if self.heard == needed:
                cq.toast(self, f"Stamp unlocked: {name}")

    def showJokeScreen(self):
        frame = self.newScreen()
        ttk.Button(frame, text="← Back", style="Back.TButton", command=self.home).pack(anchor="w")
        ttk.Label(frame, text=f"Letter #{self.heard}  ·  {cq.rankFor(self.points())}", style="Sub.TLabel").pack()

        self.card = tk.Canvas(frame, width=480, height=200, bg=cq.PAPER, highlightthickness=0)
        self.card.pack(pady=10)
        self.drawCard(1.0, "front", "")

        self.punchlineButton = ttk.Button(frame, text="Show Punchline", width=22, state="disabled",
                                          command=self.flipCard)
        self.punchlineButton.pack(pady=4)
        ttk.Button(frame, text="Next Joke", width=22, command=self.tellJoke).pack(pady=4)
        ttk.Button(frame, text="♥ Love it", width=22, command=self.favourite).pack(pady=4)
        ttk.Button(frame, text="Quit", width=22, command=self.destroy).pack(pady=4)

        self.typeSetup(0)

    def drawCard(self, frac, side, typed):
        """Draw the postcard. frac < 1 squeezes it, which is how the flip is animated."""
        c = self.card
        c.delete("all")
        cx, hw = 240, 230 * max(frac, 0.02)
        c.create_rectangle(cx - hw, 10, cx + hw, 190, fill=cq.PARCH, outline=cq.INK, width=2)
        if frac < 0.4:
            return
        cq.paste(c, "parch", int(cx - hw) + 1, 11, int(2 * hw) - 2, 178, "tex", lower=False)
        c.create_rectangle(cx - hw, 10, cx + hw, 190, outline=cq.INK, width=2)
        c.create_rectangle(cx - hw + 8, 18, cx + hw - 8, 182, outline=cq.ROSE, dash=(4, 3))
        if side == "front":
            c.create_text(32, 34, text="POSTCARD", anchor="w", font=(cq.BODY, 9, "bold"), fill=cq.ROSE)
            c.create_rectangle(404, 26, 452, 72, fill=cq.PINK, outline=cq.INK, width=2)
            cq.drawSprite(c, "bow", 428, 47, .6)
            cq.postmark(c, 372, 60, 20, "1887")
            c.create_text(215, 120, text=typed, width=340, justify="center", font=(cq.HEAD, 15), fill=cq.INK)
        else:
            c.create_text(32, 32, text=self.currentJoke[0], anchor="nw", width=390,
                          font=(cq.HEAD, 10, "italic"), fill=cq.INK)
            c.create_line(32, 78, 448, 78, fill=cq.ROSE)
            c.create_text(240, 128, text=self.currentJoke[1], width=380, justify="center",
                          font=(cq.HEAD, 17, "italic"), fill=cq.ROSE)
            c.create_rectangle(412, 144, 448, 178, outline=cq.INK, fill=cq.PINK)
            c.create_text(430, 161, text="✉", font=(cq.BODY, 14), fill=cq.INK)

    def typeSetup(self, index):
        """Type the setup onto the postcard one letter at a time."""
        text = self.currentJoke[0]
        try:
            self.drawCard(1.0, "front", text[:index])
            if index < len(text):
                self.later(25, lambda: self.typeSetup(index + 1))
            else:
                self.punchlineButton.config(state="normal")
        except tk.TclError:
            pass

    def flipCard(self):
        """Flip the postcard over to reveal the punchline below the setup."""
        self.punchlineButton.config(state="disabled")
        steps = [1.0, 0.8, 0.6, 0.4, 0.2, 0.05]
        frames = [(f, "front") for f in steps] + [(f, "back") for f in reversed(steps[:-1])] + [(1.0, "back")]
        for i, (frac, side) in enumerate(frames):
            self.later(i * 40, lambda f=frac, s=side: self.drawCard(f, s, self.currentJoke[0]))

    def favourite(self):
        if self.currentJoke in self.favourites:
            cq.toast(self, "Already pinned to your favourites ♥")
            return
        self.favourites.append(self.currentJoke)
        saveFavourites(self.favourites)
        cq.toast(self, "Pinned to favourites ♥")

    # --- favourites and stamps ---

    def showFavourites(self):
        frame = self.newScreen()
        ttk.Button(frame, text="← Back", style="Back.TButton", command=self.home).pack(anchor="w")
        ttk.Label(frame, text="My Favourites", style="Head.TLabel").pack()
        if not self.favourites:
            ttk.Label(frame, text="Nothing here yet. Tap the ♥ Love it button on a joke you like.",
                      style="Sub.TLabel").pack(pady=30)
            return
        listbox = tk.Listbox(frame, height=9, font=(cq.BODY, 10), bg=cq.PARCH, fg=cq.INK,
                             selectbackground=cq.ROSE, selectforeground="white", activestyle="none",
                             highlightthickness=1, highlightbackground=cq.INK)
        listbox.pack(fill="x", pady=8)
        for setup, _ in self.favourites:
            listbox.insert("end", setup)
        shown = tk.Label(frame, text="Pick a joke to see its punchline.", font=(cq.HEAD, 13, "italic"),
                         wraplength=470, height=3, bg=cq.PAPER, fg=cq.ROSE)
        shown.pack(fill="x")

        def onSelect(event):
            if listbox.curselection():
                shown.config(text=self.favourites[listbox.curselection()[0]][1])

        def remove():
            if not listbox.curselection():
                return
            index = listbox.curselection()[0]
            if messagebox.askyesno("Remove", "Remove this joke from your favourites?"):
                del self.favourites[index]
                saveFavourites(self.favourites)
                self.showFavourites()

        listbox.bind("<<ListboxSelect>>", onSelect)
        ttk.Button(frame, text="Remove selected", command=remove).pack(pady=4)

    def showStamps(self):
        frame = self.newScreen()
        ttk.Button(frame, text="← Back", style="Back.TButton", command=self.home).pack(anchor="w")
        ttk.Label(frame, text="Stamp Collection", style="Head.TLabel").pack()
        ttk.Label(frame, text=cq.rankFor(self.points()), font=(cq.HEAD, 15, "italic"),
                  foreground=cq.ROSE).pack()
        ttk.Label(frame, text=f"Letters opened this session: {self.heard}").pack(pady=(0, 12))
        grid = ttk.Frame(frame)
        grid.pack()
        for col, (needed, kind, name) in enumerate(STAMPS):
            cq.stampTile(grid, kind, name, self.heard >= needed, f"{needed}c").grid(row=0, column=col, padx=6)
        ttk.Label(frame, text=f"Favourite jokes saved: {len(self.favourites)}").pack(pady=10)
        cq.footerScene(frame, height=150).pack(side="bottom")


if __name__ == "__main__":
    path = findJokesFile()
    allJokes = loadJokes(path) if path else []
    usingSamples = not allJokes
    if usingSamples:
        allJokes = SAMPLE_JOKES  # keeps the app running if the file is missing
    app = JokeApp(allJokes)
    if usingSamples:
        app.after(600, lambda: cq.toast(app, "randomJokes.txt not found, using 2 sample jokes", 6000))
    app.mainloop()