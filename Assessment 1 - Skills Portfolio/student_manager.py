"""Exercise 3 - Student Manager (Tkinter), Academy Dispatch Ledger edition.

Menu items 1-8 from the brief (including the extension), plus back buttons on every screen,
parchment dossier cards, live search, a grade chart (9) and a CSV export (10).
"""
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import coquette as cq

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "studentMarks.txt")
MAX_MARKS = 160  # 3 x 20 coursework + 100 exam
GRADES = ["A", "B", "C", "D", "F"]


# ---------- Data handling ----------

def findDataFile():
    """Look for studentMarks.txt next to this script, in a resources folder, or where Python was started."""
    for folder in (HERE, os.path.join(HERE, "resources"), os.getcwd(), os.path.join(os.getcwd(), "resources")):
        path = os.path.join(folder, "studentMarks.txt")
        if os.path.exists(path):
            return path
    return DATA_FILE


def loadStudents(filename):
    """Read the file and return a list of student dictionaries."""
    students = []
    with open(filename, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
    for line in lines[1:]:  # first line is the student count
        parts = [p.strip() for p in line.split(",")]
        try:
            students.append({
                "code": int(parts[0]),
                "name": parts[1],
                "coursework": [int(m) for m in parts[2:5]],
                "exam": int(parts[5]),
            })
        except (ValueError, IndexError):
            continue  # skip any badly formatted line
    return students


def saveStudents(filename, students):
    """Write the student list back to the file in the original format."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{len(students)}\n")
        for s in students:
            marks = ",".join(str(m) for m in s["coursework"])
            file.write(f"{s['code']},{s['name']},{marks},{s['exam']}\n")


# ---------- Calculations ----------

def courseworkTotal(student):
    return sum(student["coursework"])


def totalMark(student):
    return courseworkTotal(student) + student["exam"]


def percentage(student):
    return totalMark(student) / MAX_MARKS * 100


def gradeFor(percent):
    if percent >= 70:
        return "A"
    if percent >= 60:
        return "B"
    if percent >= 50:
        return "C"
    if percent >= 40:
        return "D"
    return "F"


def validateStudent(codeText, name, markTexts, otherCodes):
    """Return (student, None) if the form is valid, otherwise (None, error message)."""
    try:
        code = int(codeText)
        marks = [int(m) for m in markTexts]
    except ValueError:
        return None, "Student number and marks must be whole numbers."
    name = name.strip()
    if not 1000 <= code <= 9999:
        return None, "Student number must be between 1000 and 9999."
    if code in otherCodes:
        return None, "That student number is already in use."
    if not name or "," in name:
        return None, "Enter a name (commas aren't allowed)."
    if not all(0 <= m <= 20 for m in marks[:3]):
        return None, "Coursework marks must be between 0 and 20."
    if not 0 <= marks[3] <= 100:
        return None, "Exam mark must be between 0 and 100."
    return {"code": code, "name": name, "coursework": marks[:3], "exam": marks[3]}, None


# ---------- App ----------

class StudentManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Manager")
        self.geometry("800x720")
        cq.applyTheme(self)
        self.body = cq.makePaper(self, "Student Manager", "The Academy Dispatch Ledger")
        self.students = []
        self.loadData()
        self.home()

    def loadData(self):
        global DATA_FILE
        DATA_FILE = findDataFile()
        try:
            self.students = loadStudents(DATA_FILE)
        except FileNotFoundError:
            messagebox.showerror("File not found", f"Could not find:\n{DATA_FILE}\n\nStarting with no records.")

    def save(self):
        saveStudents(DATA_FILE, self.students)

    # --- screen helpers ---

    def newScreen(self, title=None, back=True):
        """Clear the page; add a Back button and heading row. Returns the body."""
        cq.clear(self.body)
        if title:
            top = ttk.Frame(self.body)
            top.pack(fill="x")
            if back:
                ttk.Button(top, text="← Back to menu", style="Back.TButton", command=self.home).pack(side="left")
            ttk.Label(top, text=title, style="Head.TLabel").pack(side="left", padx=14)
        return self.body

    def buildTable(self, parent, height=11):
        columns = ("name", "number", "coursework", "exam", "percent", "grade")
        headings = ("Name", "Number", "Coursework (/60)", "Exam (/100)", "Overall %", "Grade")
        widths = (170, 70, 130, 100, 90, 60)
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col, head, width in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=width, anchor="w" if col == "name" else "center")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, pady=6)
        return tree

    def fillTable(self, tree, students):
        tree.delete(*tree.get_children())
        tree.rows = {}
        for i, s in enumerate(students):
            pct = percentage(s)
            iid = f"r{i}"
            tree.rows[iid] = s
            tree.insert("", "end", iid=iid, values=(
                s["name"], s["code"], courseworkTotal(s), s["exam"], f"{pct:.1f}%", gradeFor(pct)))

    def classSummary(self):
        if not self.students:
            return "Students in class: 0"
        average = sum(percentage(s) for s in self.students) / len(self.students)
        return f"Students in class: {len(self.students)}   |   Average percentage: {average:.1f}%"

    # --- home: the oak sorting desk ---

    def home(self):
        frame = self.newScreen()
        ttk.Label(frame, text="MENU", style="Head.TLabel").pack(pady=(4, 0))
        ttk.Label(frame, text=self.classSummary(), style="Sub.TLabel").pack(pady=(0, 8))
        options = [
            ("LEDGER", "1. View all student records", self.viewAll),
            ("DOSSIERS", "2. View individual student record", self.viewIndividual),
            ("STAR SHELF", "3. Show student with highest total score", self.showHighest),
            ("LOW SHELF", "4. Show student with lowest total score", self.showLowest),
            ("SORTING TRAY", "5. Sort student records", self.sortRecords),
            ("NEW ENTRY", "6. Add a student record", self.addRecord),
            ("WASTE BASKET", "7. Delete a student record", self.deleteRecord),
            ("CORRECTIONS", "8. Update a students record", self.updateRecord),
            ("GRADE CHART", "9. Grade chart", self.gradeChart),
            ("OUTBOX", "10. Export report (CSV)", self.exportReport),
        ]
        rows = (len(options) + 1) // 2
        desk = tk.Canvas(frame, width=700, height=rows * 76 + 10, highlightthickness=3,
                         highlightbackground=cq.OAK_DARK, bg=cq.OAK_DARK)
        desk.pack(pady=4)
        cq.paste(desk, "oak", 0, 0, 700, rows * 76 + 10)
        for i, (plate, text, command) in enumerate(options):
            cubby = tk.Frame(desk, bg=cq.OAK_DARK, padx=3, pady=3)
            inner = tk.Frame(cubby, bg=cq.PARCH, padx=6, pady=4)
            inner.pack()
            tk.Label(inner, text=f" {plate} ", bg=cq.GOLD, fg=cq.INK, font=(cq.BODY, 8, "bold")).pack(anchor="w")
            ttk.Button(inner, text=text, width=40, style="Cubby.TButton", command=command).pack(pady=(3, 0))
            desk.create_window(8 + (i % 2) * 346, 8 + (i // 2) * 76, anchor="nw", window=cubby)
        ttk.Button(frame, text="Quit", width=20, command=self.destroy).pack(pady=12)

    # --- reusable screens ---

    def dossierCard(self, parent, s, star=False):
        """One student file: ribbon-tied grade, coursework stamps, exam mark and percentage."""
        pct = percentage(s)
        card = tk.Frame(parent, bg=cq.PARCH, highlightthickness=2, highlightbackground=cq.INK, padx=10, pady=6)
        card.pack(fill="x", padx=6, pady=5)
        badge = tk.Canvas(card, width=64, height=88, bg=cq.PARCH, highlightthickness=0)
        badge.pack(side="left")
        badge.create_polygon(20, 50, 14, 84, 26, 76, 32, 50, fill=cq.ROSE, outline=cq.INK)
        badge.create_polygon(44, 50, 50, 84, 38, 76, 32, 50, fill=cq.ROSE, outline=cq.INK)
        badge.create_oval(8, 6, 56, 54, fill=cq.PINK, outline=cq.INK, width=2)
        badge.create_text(32, 30, text=gradeFor(pct), font=(cq.HEAD, 20, "bold"), fill=cq.INK)

        info = tk.Frame(card, bg=cq.PARCH)
        info.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(info, text=s["name"], font=(cq.HEAD, 14, "bold"), bg=cq.PARCH, fg=cq.INK).pack(anchor="w")
        a, b, c = s["coursework"]
        lines = [f"File No. {s['code']}",
                 f"Coursework stamps: {a} · {b} · {c}   (total {courseworkTotal(s)}/60)",
                 f"Exam mark: {s['exam']}/100     Overall: {pct:.1f}%"]
        for line in lines:
            tk.Label(info, text=line, font=(cq.BODY, 9), bg=cq.PARCH, fg=cq.INK).pack(anchor="w")
        if star:
            tag = tk.Canvas(card, width=74, height=80, bg=cq.PARCH, highlightthickness=0)
            tag.pack(side="right")
            cq.drawSprite(tag, "star", 37, 32, 1.4)
            tag.create_text(37, 68, text="top scholar", font=(cq.BODY, 8, "bold"), fill=cq.INK)

    def showStudents(self, title, students, summary=False, searchable=False, star=False):
        frame = self.newScreen(title)
        if searchable:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=(6, 0))
            ttk.Label(row, text="Search name or number:").pack(side="left")
            query = tk.StringVar()
            ttk.Entry(row, textvariable=query, width=24).pack(side="left", padx=8)
        ttk.Label(frame, text=self.classSummary() if summary else "",
                  font=(cq.BODY, 10, "bold")).pack(side="bottom", anchor="w", pady=4)
        holder, inner = cq.scrollable(frame, height=360)
        holder.pack(fill="both", expand=True, pady=6)

        def render(shown):
            cq.clear(inner)
            for s in shown:
                self.dossierCard(inner, s, star)
            if not shown:
                ttk.Label(inner, text="No files match.", style="Sub.TLabel").pack(pady=20)

        render(students)
        if searchable:
            def refresh(*args):
                q = query.get().strip().lower()
                render([s for s in students if q in s["name"].lower() or q in str(s["code"])])
            query.trace_add("write", refresh)

    def selectScreen(self, title, actionText, onPick):
        """Pick one student by searching a name or number, then call onPick(student)."""
        frame = self.newScreen(title)
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text="Search name or number:").pack(side="left")
        query = tk.StringVar()
        ttk.Entry(row, textvariable=query, width=24).pack(side="left", padx=8)

        footer = ttk.Frame(frame)
        footer.pack(side="bottom", fill="x", pady=6)
        tree = self.buildTable(frame, height=10)
        self.fillTable(tree, self.students)

        def refresh(*args):
            q = query.get().strip().lower()
            self.fillTable(tree, [s for s in self.students if q in s["name"].lower() or q in str(s["code"])])

        def choose():
            selected = tree.selection()
            if not selected:
                cq.toast(self, "Pick a student from the list first")
                return
            onPick(tree.rows[selected[0]])

        query.trace_add("write", refresh)
        tree.bind("<Double-1>", lambda event: choose())
        ttk.Button(footer, text=actionText, command=choose).pack()

    def formScreen(self, title, student, otherCodes, onSave):
        frame = self.newScreen(title)
        labels = ["Student number (1000-9999)", "Name", "Coursework 1 (out of 20)",
                  "Coursework 2 (out of 20)", "Coursework 3 (out of 20)", "Exam (out of 100)"]
        values = ["", "", "", "", "", ""]
        if student:
            values = [student["code"], student["name"], *student["coursework"], student["exam"]]
        form = ttk.Frame(frame)
        form.pack(pady=14)
        entries = []
        for row, (label, value) in enumerate(zip(labels, values)):
            ttk.Label(form, text=label).grid(row=row, column=0, padx=10, pady=6, sticky="w")
            entry = ttk.Entry(form, width=28)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=6)
            entries.append(entry)
        error = ttk.Label(frame, text="", foreground=cq.BAD, font=(cq.BODY, 10, "bold"))
        error.pack()

        def submit():
            result, problem = validateStudent(entries[0].get(), entries[1].get(),
                                              [e.get() for e in entries[2:]], otherCodes)
            if problem:
                error.config(text=problem)
                return
            onSave(result)

        ttk.Button(frame, text="Save ♥", command=submit).pack(pady=8)

    # --- menu items 1-4 ---

    def viewAll(self):
        self.showStudents("All student records", self.students, summary=True, searchable=True)

    def viewIndividual(self):
        self.selectScreen("View individual student record", "View record",
                          lambda s: self.showStudents("Student record", [s]))

    def showHighest(self):
        if not self.students:
            return cq.toast(self, "No student records yet")
        best = max(totalMark(s) for s in self.students)
        self.showStudents("Highest total score", [s for s in self.students if totalMark(s) == best], star=True)

    def showLowest(self):
        if not self.students:
            return cq.toast(self, "No student records yet")
        worst = min(totalMark(s) for s in self.students)
        self.showStudents("Lowest total score", [s for s in self.students if totalMark(s) == worst])

    # --- extension menu items 5-8 ---

    def sortRecords(self):
        frame = self.newScreen("Sort student records")
        field = tk.StringVar(value="Name")
        order = tk.StringVar(value="asc")
        box = ttk.Frame(frame)
        box.pack(pady=30)
        ttk.Label(box, text="Sort by:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ttk.Combobox(box, textvariable=field, state="readonly", width=24,
                     values=["Name", "Student number", "Overall percentage"]).grid(row=0, column=1)
        ttk.Radiobutton(box, text="Ascending", variable=order, value="asc").grid(row=1, column=0, padx=10, pady=6)
        ttk.Radiobutton(box, text="Descending", variable=order, value="desc").grid(row=1, column=1, pady=6)

        def apply():
            keys = {"Name": lambda s: s["name"].lower(),
                    "Student number": lambda s: s["code"],
                    "Overall percentage": percentage}
            descending = order.get() == "desc"
            result = sorted(self.students, key=keys[field.get()], reverse=descending)
            direction = "descending" if descending else "ascending"
            self.showStudents(f"Sorted by {field.get().lower()} ({direction})", result, summary=True)

        ttk.Button(frame, text="Sort", command=apply).pack()

    def addRecord(self):
        codes = {s["code"] for s in self.students}

        def save(student):
            self.students.append(student)
            self.save()
            self.viewAll()
            cq.toast(self, f"{student['name']} stamped into the ledger ♥")

        self.formScreen("Add a student record", None, codes, save)

    def deleteRecord(self):
        def delete(student):
            if messagebox.askyesno("Confirm delete", f"Delete {student['name']} ({student['code']})?"):
                self.students.remove(student)
                self.save()
                self.viewAll()
                cq.toast(self, "Record struck from the ledger")

        self.selectScreen("Delete a student record", "Delete selected", delete)

    def updateRecord(self):
        def edit(student):
            codes = {s["code"] for s in self.students if s is not student}

            def save(updated):
                student.update(updated)
                self.save()
                self.viewAll()
                cq.toast(self, "Ledger entry corrected ♥")

            self.formScreen("Update a students record", student, codes, save)

        self.selectScreen("Update a students record", "Edit selected", edit)

    # --- extras ---

    def gradeChart(self):
        frame = self.newScreen("Grade chart")
        counts = {g: 0 for g in GRADES}
        for s in self.students:
            counts[gradeFor(percentage(s))] += 1
        top = max(counts.values()) or 1

        canvas = tk.Canvas(frame, width=560, height=270, bg=cq.PAPER, highlightthickness=0)
        canvas.pack(pady=10)
        for i, grade in enumerate(GRADES):
            x = 50 + i * 100
            height = counts[grade] / top * 190
            canvas.create_rectangle(x, 220 - height, x + 60, 220, fill=cq.PINK if i % 2 == 0 else cq.ROSE,
                                    outline=cq.INK, width=2)
            canvas.create_text(x + 30, 205 - height, text=str(counts[grade]), font=(cq.BODY, 11, "bold"),
                               fill=cq.INK)
            canvas.create_text(x + 30, 240, text=f"Grade {grade}", font=(cq.HEAD, 12, "bold"), fill=cq.INK)
        canvas.create_line(30, 220, 540, 220, fill=cq.INK, width=2)

        ttk.Label(frame, text=self.classSummary(), font=(cq.BODY, 10, "bold")).pack()
        if self.students:
            star = max(self.students, key=totalMark)
            ttk.Label(frame, text=f"★ Top of the class: {star['name']} ({percentage(star):.1f}%)",
                      style="Sub.TLabel").pack(pady=6)

    def exportReport(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="student_report.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Number", "Coursework total", "Exam", "Overall %", "Grade"])
            for s in self.students:
                pct = percentage(s)
                writer.writerow([s["name"], s["code"], courseworkTotal(s), s["exam"], f"{pct:.1f}", gradeFor(pct)])
        cq.toast(self, "Report saved ♥")


if __name__ == "__main__":
    StudentManager().mainloop()