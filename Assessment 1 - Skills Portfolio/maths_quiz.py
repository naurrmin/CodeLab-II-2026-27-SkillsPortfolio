"""Exercise 1 - Maths Quiz (Tkinter), coquette edition.

Extras on top of the brief: back buttons, a Galentine Passport (stamps, stickers, rank titles,
saved between plays), a Catch the Falling Bows bonus round and a VIP ticket with a secret letter.
"""
import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

import coquette as cq

QUESTIONS_PER_GAME = 10
POINTS_FIRST_TRY = 10
POINTS_SECOND_TRY = 5
FEEDBACK_DELAY_MS = 1200
STAMP_SCORE = 70  # score needed to earn a level stamp
LEVEL_NAMES = {1: "Easy", 2: "Moderate", 3: "Advanced"}
DISPATCH = {1: "Local Delivery", 2: "Airmail", 3: "Transatlantic Telegraph"}
POSTAL_TITLES = {"A+": "Certified Chief Postmistress", "A": "Head Courier", "B": "Senior Clerk",
                 "C": "Sorting Clerk", "D": "Apprentice Stamper", "F": "Mail Room Trainee"}
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passport.json")


# ---------- Required quiz functions ----------

def randomInt(level):
    """Return a random number with 1, 2 or 4 digits depending on the level."""
    if level == 1:
        return random.randint(1, 9)
    if level == 2:
        return random.randint(10, 99)
    return random.randint(1000, 9999)


def decideOperation():
    """Randomly return '+' or '-'."""
    return random.choice(["+", "-"])


def getRank(score):
    """Convert a score out of 100 into a letter rank."""
    if score > 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


# ---------- Passport (saved progress) ----------

def loadPassport():
    passport = {"best": {"1": 0, "2": 0, "3": 0}, "played": 0, "bows": 0, "torn": False}
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            passport.update(json.load(file))
    except (OSError, ValueError):
        pass
    return passport


def savePassport(passport):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(passport, file)
    except OSError:
        pass


def passportPoints(passport):
    """0-100 points: the average of the best score on each level."""
    return sum(passport["best"].get(str(level), 0) for level in LEVEL_NAMES) / len(LEVEL_NAMES)


def stickersFor(passport):
    """Return (emoji, name, unlocked) for each collectible sticker."""
    best = passport["best"]
    return [  # (picture, name, unlocked)
        ("bow", "First Quiz", passport["played"] >= 1),
        ("star", "Perfect 100", max(best.values()) >= 100),
        ("teddy", "Triple Stamp", all(best.get(str(l), 0) >= STAMP_SCORE for l in LEVEL_NAMES)),
        ("heart", "Bow Catcher", passport["bows"] >= 15),
        ("envelope", "Secret Letter", passport["torn"]),
    ]


# ---------- Bonus round: Catch the Falling Bows ----------

class CatchGame(ttk.Frame):
    DURATION = 15
    KINDS = ["bow", "teddy", "envelope", "heart"]

    def __init__(self, parent, onFinish):
        super().__init__(parent)
        self.onFinish = onFinish
        self.running = False
        self.caught = 0
        self.items = []
        self.count = 0

        self.info = ttk.Label(self, text="Catch as many as you can in 15 seconds!", style="Sub.TLabel")
        self.info.pack()
        self.canvas = tk.Canvas(self, width=420, height=260, bg=cq.SOFT, highlightthickness=2,
                                highlightbackground=cq.INK)
        self.canvas.pack(pady=6)
        cq.paste(self.canvas, "wall", 0, 0, 420, 260)
        self.startButton = ttk.Button(self, text="Start ♥", command=self.start)
        self.startButton.pack()

    def start(self):
        self.running = True
        self.caught = 0
        self.timeLeft = self.DURATION
        self.items = []
        self.clearItems()
        self.startButton.config(state="disabled")
        self.updateInfo()
        self.after(1000, self.tick)
        self.spawn()
        self.move()

    def clearItems(self):
        for entry in self.items:
            self.canvas.delete(entry[0])
        self.items = []
        self.canvas.delete("msg")

    def updateInfo(self):
        self.info.config(text=f"Time: {self.timeLeft}s     Caught: {self.caught}")

    def spawn(self):
        if not self.running:
            return
        self.count += 1
        tag = f"it{self.count}"
        cq.drawSprite(self.canvas, random.choice(self.KINDS), random.randint(30, 390), -20, 1.0, tag)
        self.canvas.tag_bind(tag, "<Button-1>", lambda event, t=tag: self.catch(t))
        self.items.append([tag, random.randint(3, 6)])
        self.after(450, self.spawn)

    def move(self):
        if not self.running:
            return
        for entry in list(self.items):
            self.canvas.move(entry[0], 0, entry[1])
            if self.canvas.bbox(entry[0])[1] > 270:
                self.canvas.delete(entry[0])
                self.items.remove(entry)
        self.after(40, self.move)

    def catch(self, item):
        if not self.running:
            return
        box = self.canvas.bbox(item)
        self.canvas.delete(item)
        if box:
            pop = self.canvas.create_text((box[0] + box[2]) // 2, box[1], text="+1 ♥", fill=cq.BAD,
                                          font=(cq.BODY, 11, "bold"))
            self.after(400, lambda: self.canvas.delete(pop))
        self.items = [e for e in self.items if e[0] != item]
        self.caught += 1
        self.updateInfo()

    def tick(self):
        if not self.running:
            return
        self.timeLeft -= 1
        self.updateInfo()
        if self.timeLeft <= 0:
            self.running = False
            self.clearItems()
            self.canvas.create_rectangle(100, 85, 320, 175, fill=cq.PAPER, outline=cq.INK, width=2, tags="msg")
            self.canvas.create_text(210, 130, tags="msg", text=f"Time’s up!\nYou caught {self.caught} ♥",
                                    font=(cq.HEAD, 20, "bold"), fill=cq.INK, justify="center")
            self.onFinish(self.caught)
        else:
            self.after(1000, self.tick)

    def destroy(self):
        self.running = False
        super().destroy()


# ---------- VIP ticket ----------

class VipTicket(ttk.Frame):
    def __init__(self, parent, letter, onTear):
        super().__init__(parent)
        self.letter = letter
        self.onTear = onTear
        c = self.canvas = tk.Canvas(self, width=440, height=130, bg=cq.PAPER, highlightthickness=0)
        c.pack()
        cq.paste(c, "parch", 10, 15, 290, 100, "main")
        c.create_rectangle(10, 15, 300, 115, outline=cq.INK, width=2)
        c.create_rectangle(18, 23, 292, 107, outline=cq.ROSE, width=2, dash=(4, 3))
        c.create_text(165, 52, text="VIP TICKET", font=(cq.HEAD, 17, "bold"), fill=cq.INK)
        c.create_text(165, 84, text="Valentine’s Day Party\nGirls only ♥", font=(cq.BODY, 9),
                      fill=cq.INK, justify="center")
        cq.drawSprite(c, "bow", 44, 66, .65)
        cq.drawSprite(c, "heart", 268, 66, .65)
        c.create_rectangle(300, 15, 400, 115, fill=cq.ROSE, outline=cq.INK, width=2, tags="stub")
        c.create_text(350, 48, text="ADMIT\nONE", font=(cq.HEAD, 14, "bold"), fill=cq.INK,
                      justify="center", tags="stub")
        cq.drawSprite(c, "star", 350, 88, .6, "stub")
        c.create_line(300, 15, 300, 115, dash=(4, 3), fill=cq.INK)
        self.button = ttk.Button(self, text="Tear Ticket ✂", command=self.tear)
        self.button.pack(pady=4)
        self.letterLabel = tk.Label(self, text="", font=(cq.BODY, 10), bg=cq.SOFT, fg=cq.INK,
                                    wraplength=400, justify="left", padx=12, pady=10,
                                    highlightthickness=1, highlightbackground=cq.INK)

    def tear(self):
        self.button.config(state="disabled")
        self.fly(0)

    def fly(self, step):
        try:
            if step < 25:
                self.canvas.move("stub", 3, 2)
                self.after(20, lambda: self.fly(step + 1))
            else:
                self.canvas.delete("stub")
                self.letterLabel.config(text=self.letter)
                self.letterLabel.pack(pady=8)
                self.onTear()
        except tk.TclError:
            pass


# ---------- Main app ----------

class MathsQuiz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maths Quiz")
        self.geometry("580x700")
        self.resizable(False, False)
        cq.applyTheme(self)
        self.body = cq.makePaper(self, "Maths Quiz", "Courier’s Dispatch Office")

        self.passport = loadPassport()
        self.level = 1
        self.score = 0
        self.questionNum = 0
        self.attempt = 1
        self.answer = 0
        self.lastScore = 0
        self.pending = None
        self.results = []

        self.displayMenu()

    # --- helpers ---

    def newFrame(self):
        """Clear the page and return the body to build the next screen in."""
        if self.pending:
            self.after_cancel(self.pending)
            self.pending = None
        cq.clear(self.body)
        return self.body

    def backButton(self, parent, text, command):
        ttk.Button(parent, text=text, style="Back.TButton", command=command).pack(anchor="w")

    # --- screens ---

    def displayMenu(self):
        """Show the difficulty level menu as a postal tariff board."""
        frame = self.newFrame()
        ttk.Label(frame, text="DIFFICULTY LEVEL", style="Head.TLabel").pack(pady=(8, 0))
        ttk.Label(frame, text="✉  Postal Tariff Board  ✉", style="Sub.TLabel").pack()
        board = tk.Frame(frame, bg=cq.PARCH, highlightthickness=2, highlightbackground=cq.INK, padx=12, pady=10)
        board.pack(pady=10)
        for row, (level, name) in enumerate(LEVEL_NAMES.items()):
            ttk.Button(board, text=f"{level}. {name}", width=16,
                       command=lambda lvl=level: self.startQuiz(lvl)).grid(row=row, column=0, padx=6, pady=6)
            best = self.passport["best"].get(str(level), 0)
            stamp = "✿ stamped" if best >= STAMP_SCORE else "no stamp yet"
            tk.Label(board, text=f"{DISPATCH[level]}\nbest {best} · {stamp}", font=(cq.BODY, 9), bg=cq.PARCH,
                     fg=cq.INK, justify="left", width=30, anchor="w").grid(row=row, column=1, padx=6)
        ttk.Button(frame, text="My Passport ✦", width=18,
                   command=lambda: self.showPassport(self.displayMenu)).pack(pady=(10, 4))
        ttk.Button(frame, text="Quit", width=18, command=self.destroy).pack(pady=4)
        cq.footerScene(frame).pack(side="bottom", pady=(8, 0))

    def startQuiz(self, level):
        self.level = level
        self.score = 0
        self.questionNum = 0
        self.results = []
        self.nextQuestion()

    def leaveQuiz(self):
        if messagebox.askyesno("Leave quiz?", "Go back to the menu? Your progress in this quiz will be lost."):
            self.displayMenu()

    def nextQuestion(self):
        self.pending = None
        if self.questionNum >= QUESTIONS_PER_GAME:
            self.displayResults()
            return
        self.questionNum += 1
        self.attempt = 1
        num1 = randomInt(self.level)
        num2 = randomInt(self.level)
        op = decideOperation()
        self.answer = num1 + num2 if op == "+" else num1 - num2
        self.displayProblem(num1, op, num2)

    def displayProblem(self, num1, op, num2):
        """Show the question and an Entry for the user's answer."""
        frame = self.newFrame()
        self.backButton(frame, "← Back to menu", self.leaveQuiz)
        ttk.Label(frame, text=f"Question {self.questionNum} of {QUESTIONS_PER_GAME}").pack()
        tk.Label(frame, text=f"Score: {self.score}", font=(cq.BODY, 10, "bold"), bg=cq.PINK, fg=cq.INK,
                 padx=12, pady=2).pack(pady=4)
        self.drawSlip(frame, num1, op, num2)

        self.entry = ttk.Entry(frame, font=(cq.BODY, 16), width=10, justify="center")
        self.entry.pack()
        self.entry.focus()
        self.entry.bind("<Return>", lambda event: self.submitAnswer())

        self.submitButton = ttk.Button(frame, text="Submit", command=self.submitAnswer)
        self.submitButton.pack(pady=10)
        self.feedback = ttk.Label(frame, text="", font=(cq.BODY, 11, "bold"))
        self.feedback.pack()
        self.drawManifest(frame)

    def drawSlip(self, parent, num1, op, num2):
        """The question as an unsealed telegram slip."""
        c = self.slip = tk.Canvas(parent, width=440, height=130, bg=cq.PAPER, highlightthickness=0)
        c.pack(pady=8)
        points = []
        for i, x in enumerate(range(10, 431, 10)):
            points += [x, 8 if i % 2 == 0 else 14]
        for i, x in enumerate(range(430, 9, -10)):
            points += [x, 122 if i % 2 == 0 else 116]
        c.create_polygon(points, fill=cq.PARCH, outline=cq.INK, width=2)
        cq.paste(c, "parch", 11, 15, 418, 100, "tex", lower=False)
        c.create_polygon(points, fill="", outline=cq.INK, width=2)
        c.create_text(30, 30, text="TELEGRAM", anchor="w", font=(cq.BODY, 9, "bold"), fill=cq.ROSE)
        c.create_text(410, 30, text=f"No. {self.questionNum}", anchor="e", font=(cq.BODY, 9), fill=cq.INK)
        c.create_text(150, 70, text=f"{num1} {op} {num2} = ?", font=(cq.HEAD, 28, "bold"), fill=cq.INK)
        c.create_text(220, 104, text="— STOP —", font=(cq.BODY, 8), fill=cq.INK)

    def drawManifest(self, parent):
        """Ten slots showing how each telegram was stamped."""
        row = ttk.Frame(parent)
        row.pack(pady=(12, 0))
        ttk.Label(row, text="Manifest:").pack(side="left", padx=(0, 6))
        self.manifestLabels = []
        for _ in range(QUESTIONS_PER_GAME):
            label = tk.Label(row, width=3, font=(cq.BODY, 10, "bold"), bg=cq.PARCH, fg=cq.INK,
                             highlightthickness=1, highlightbackground=cq.INK)
            label.pack(side="left", padx=1)
            self.manifestLabels.append(label)
        self.markManifest()

    def markManifest(self):
        for i, label in enumerate(self.manifestLabels):
            if i < len(self.results):
                label.config(text=self.results[i], fg=cq.BAD if self.results[i] == "✗" else cq.GOOD)
            else:
                label.config(text="•" if i == len(self.results) else "·", fg=cq.INK)

    def submitAnswer(self):
        if str(self.submitButton["state"]) == "disabled":
            return
        try:
            userAnswer = int(self.entry.get().strip())
        except ValueError:
            self.feedback.config(text="Please enter a whole number.", foreground=cq.BAD)
            return

        if self.isCorrect(userAnswer, self.answer):
            self.score += POINTS_FIRST_TRY if self.attempt == 1 else POINTS_SECOND_TRY
            self.results.append("✓" if self.attempt == 1 else "½")
            self.markManifest()
            self.finishQuestion()
        elif self.attempt == 1:
            self.attempt = 2
            self.entry.delete(0, tk.END)
        else:
            self.results.append("✗")
            self.markManifest()
            self.finishQuestion()

    def isCorrect(self, userAnswer, correctAnswer):
        """Check the answer, show an appropriate message and return True/False."""
        if userAnswer == correctAnswer:
            points = POINTS_FIRST_TRY if self.attempt == 1 else POINTS_SECOND_TRY
            self.feedback.config(text=f"Correct! +{points} points ♥", foreground=cq.GOOD)
            cq.inkStamp(self.slip, 350, 72, "✦ PAID ✦\nAPPROVED", cq.STAMP_BLUE, 12, 16)
            return True
        if self.attempt == 1:
            self.feedback.config(text="Wrong, have one more go!", foreground=cq.BAD)
            cq.inkStamp(self.slip, 350, 72, "TRY\nAGAIN", cq.BAD, -10, 16)
        else:
            self.feedback.config(text=f"Wrong. The answer was {correctAnswer}.", foreground=cq.BAD)
            cq.inkStamp(self.slip, 350, 72, "RETURN TO\nSENDER", cq.BAD, -10, 15)
        return False

    def finishQuestion(self):
        """Lock the input briefly so the feedback can be read, then move on."""
        self.submitButton.config(state="disabled")
        self.entry.config(state="disabled")
        self.pending = self.after(FEEDBACK_DELAY_MS, self.nextQuestion)

    def displayResults(self, record=True):
        """Show the final score and rank, update the passport and ask about playing again."""
        if record:
            self.lastScore = self.score
            self.recordResult()
        frame = self.newFrame()
        rank = getRank(self.lastScore)

        banner = tk.Canvas(frame, width=480, height=100, bg=cq.PAPER, highlightthickness=0)
        banner.pack()
        if self.lastScore > 90:
            cq.waxSeal(banner, 240, 50, 38, "♥")
            cq.drawSprite(banner, "bow", 340, 52, 1.0)
            cq.drawSprite(banner, "bow", 140, 52, 1.0)
        else:
            cq.postmark(banner, 200, 50, 36, "DELIVERED")
        ttk.Label(frame, text="Quiz Complete!", style="Head.TLabel").pack()
        ttk.Label(frame, text=f"Your score: {self.lastScore} / 100", font=(cq.HEAD, 16)).pack(pady=2)
        ttk.Label(frame, text=f"Rank: {rank}", font=(cq.HEAD, 16, "bold")).pack()
        ttk.Label(frame, text=POSTAL_TITLES[rank], style="Sub.TLabel").pack()
        ttk.Label(frame, text="Would you like to play again?").pack(pady=(14, 4))
        row = ttk.Frame(frame)
        row.pack()
        ttk.Button(row, text="Play Again", width=14, command=self.displayMenu).pack(side="left", padx=4)
        ttk.Button(row, text="Quit", width=14, command=self.destroy).pack(side="left", padx=4)

        ttk.Label(frame, text="Extras", style="Sub.TLabel").pack(pady=(16, 4))
        extras = ttk.Frame(frame)
        extras.pack()
        ttk.Button(extras, text="Catch the Bows ♥", command=self.showBonus).grid(row=0, column=0, padx=4, pady=3)
        ttk.Button(extras, text="VIP Ticket ✉", command=self.showTicket).grid(row=0, column=1, padx=4, pady=3)
        ttk.Button(extras, text="My Passport", command=lambda: self.showPassport(
            lambda: self.displayResults(record=False))).grid(row=0, column=2, padx=4, pady=3)

        cq.footerScene(frame, height=110).pack(side="bottom")
        if self.lastScore >= 80:
            self.after(200, lambda: cq.confetti(banner))

    def recordResult(self):
        """Save the score, then announce any new stamp or sticker."""
        before = {name for _, name, got in stickersFor(self.passport) if got}
        key = str(self.level)
        hadStamp = self.passport["best"].get(key, 0) >= STAMP_SCORE
        self.passport["played"] += 1
        self.passport["best"][key] = max(self.passport["best"].get(key, 0), self.score)
        savePassport(self.passport)
        if not hadStamp and self.score >= STAMP_SCORE:
            cq.toast(self, f"New stamp: {LEVEL_NAMES[self.level]} ✿")
        else:
            for _, name, got in stickersFor(self.passport):
                if got and name not in before:
                    cq.toast(self, f"Sticker unlocked: {name} ♥")
                    break

    def showBonus(self):
        frame = self.newFrame()
        self.backButton(frame, "← Back to results", lambda: self.displayResults(record=False))
        ttk.Label(frame, text="Bonus Round", style="Head.TLabel").pack(pady=(4, 0))
        ttk.Label(frame, text="Catch the Falling Bows & Hearts", style="Sub.TLabel").pack()
        CatchGame(frame, self.bonusDone).pack(pady=6)

    def bonusDone(self, caught):
        newBest = caught > self.passport["bows"]
        before = self.passport["bows"] >= 15
        self.passport["bows"] = max(self.passport["bows"], caught)
        savePassport(self.passport)
        if self.passport["bows"] >= 15 and not before:
            cq.toast(self, "Sticker unlocked: Bow Catcher")
        elif newBest:
            cq.toast(self, f"New bow record: {caught} ♥")

    def showTicket(self):
        frame = self.newFrame()
        self.backButton(frame, "← Back to results", lambda: self.displayResults(record=False))
        ttk.Label(frame, text="Your VIP Ticket", style="Head.TLabel").pack(pady=(4, 0))
        ttk.Label(frame, text="Tear it to read your secret letter", style="Sub.TLabel").pack(pady=(0, 8))
        letter = (f"Dear bestie,\n\nYou scored {self.lastScore}/100 and earned a rank of "
                  f"{getRank(self.lastScore)}. Your table is waiting for you on February 14th.\n\n"
                  "Wear your heart on your cheek ♥")
        cq.footerScene(frame, height=130).pack(side="bottom")
        VipTicket(frame, letter, self.ticketTorn).pack()

    def ticketTorn(self):
        if not self.passport["torn"]:
            self.passport["torn"] = True
            savePassport(self.passport)
            cq.toast(self, "Sticker unlocked: Secret Letter")

    def showPassport(self, backCommand):
        frame = self.newFrame()
        self.backButton(frame, "← Back", backCommand)
        points = passportPoints(self.passport)
        ttk.Label(frame, text="Galentine Passport", style="Head.TLabel").pack()
        ttk.Label(frame, text=cq.rankFor(points), font=(cq.HEAD, 15, "italic"), foreground=cq.ROSE).pack()
        ttk.Label(frame, text=f"{points:.0f} / 100 points").pack(pady=(0, 10))

        ttk.Label(frame, text="Level stamps", style="Sub.TLabel").pack()
        stamps = ttk.Frame(frame)
        stamps.pack(pady=4)
        for col, (level, name) in enumerate(LEVEL_NAMES.items()):
            best = self.passport["best"].get(str(level), 0)
            kind = {1: "bow", 2: "heart", 3: "star"}[level]
            cq.stampTile(stamps, kind, name, best >= STAMP_SCORE, str(best), alwaysLabel=True).grid(row=0, column=col, padx=6)

        ttk.Label(frame, text="Stickers", style="Sub.TLabel").pack(pady=(10, 0))
        grid = ttk.Frame(frame)
        grid.pack(pady=4)
        for col, (kind, name, got) in enumerate(stickersFor(self.passport)):
            cq.stampTile(grid, kind, name, got, "★").grid(row=0, column=col, padx=1)
        ttk.Label(frame, text=f"Quizzes played: {self.passport['played']}     "
                              f"Best bow catch: {self.passport['bows']}").pack(pady=6)


if __name__ == "__main__":
    MathsQuiz().mainloop()