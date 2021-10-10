from tkinter import *
from tkinter import ttk
from tkinter import font
from threading import Timer
import math
import random
from Graph import *
from background import Background

random.seed()
TRANSPARENT = "#576890"
DECIMAL_POINTS = "{:.2f}"
inputs = {
    'loan': 10000,
    'down': 10,
    'rate': 4.5,
    'year': 10
}
outputs = {
    'repayment': 0,
    'principle': 0,
    'interest': 0,
    'month': 0
}

LargeFont = ("Times New Roman", 15)

def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(func):
        def debounced(*args, **kwargs):
            def call_it():
                func(*args, **kwargs)
            try:
                debounced._timer.cancel()
            except(AttributeError):
                pass
            debounced._timer = Timer(wait, call_it)
            debounced._timer.start()
        return debounced
    return decorator


def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def mortgage(loan, down, rate, year, format="%"):
    if format == "%":
        # down payment in percentage format
        principle = loan * (100 - down) / 100
    elif format == "RM":
        # down payment in cash format
        principle = loan - down

    month = int(year * 12)
    monthly_rate = rate / 12 / 100
    compound = (1 + monthly_rate) ** month
    repayment = principle / ((compound - 1) / (monthly_rate * compound)) * month
    interest = repayment - principle

    return repayment, principle, interest, month

@debounce(0.3)
def mortgage_list():
    debt = outputs['repayment']
    interest = outputs['interest']
    rate = inputs['rate']
    month = outputs['month']


    # Use treeview or something to display the data in a table like forma
    month_debt = debt/month
    interest /= month

    results = ResultListTopLevel(root)

    for i in range(1, month + 1):
        interest = debt * rate / 100 / 12
        principle = month_debt - interest
        debt = debt - principle - interest
        results.list.insert('', 'end', text=i, values=(DECIMAL_POINTS.format(principle), DECIMAL_POINTS.format(interest), DECIMAL_POINTS.format(debt)))




# Widget function callbacks
@debounce(0.3)
def display_update(repayment, prin, rate, month):
    debt.label.config(text=DECIMAL_POINTS.format(repayment))
    principle.label.config(text=DECIMAL_POINTS.format(prin))
    interest.label.config(text=DECIMAL_POINTS.format(rate))

    outputs.update({
        'repayment': repayment,
        'principle': prin,
        'interest': rate,
        'month': month
    })

    circle_graph.cal([
        {
            "subject": "Principle",
            "value": prin,
            "color": "#90ee90"

        },
        {
            "subject": "Interest",
            "value": rate,
            "color": "#006400"
        }
    ])
    circle_graph.animate()



# widgets
class ValidatedEntry(Entry):
    def __init__(self, master, name, default, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.name = name
        self.default = default
        self.upperbound = None

        self.insert(0, self.default)
        vcmd = (root.register(self._validation), "%P")
        self.configure(validate="key", validatecommand=vcmd)

    def _validation(self, value):
        tmp = None
        try:
            if value == "":
                value = float(self.default)
            elif is_float(value):
                value = float(value)
                if self.upperbound:
                    if self.upperbound <= value:
                        raise ValueError("Sorry, no numbers {} and above".format(self.upperbound))
            else:
                raise TypeError("Entry only allows floats input")

            tmp, inputs[self.name] = inputs[self.name], value
            output = mortgage(**inputs)
            display_update(*output)
            return True

        except Exception as ex:
            if tmp:
                inputs[self.name] = tmp
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return False

    def set_range(self, upperbound=None):
        self.upperbound=upperbound

class EntryFrame(LabelFrame):
    def __init__(self, master, name, default, *args, **kwargs):
        super().__init__(master, bg=TRANSPARENT, *args, **kwargs)
        self.ent = ValidatedEntry(self, name, default, font=LargeFont)
        self.ent.grid()

class ResultFrame(LabelFrame):
    def __init__(self, master, *args, value="", **kwargs):
        super().__init__(master, *args, **kwargs)
        self.label = Label(self, bg=TRANSPARENT)
        self.label.grid()

class ResultListTopLevel(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("600x600+700+50")

        headings = 'Principle', 'Interest', 'Debt'
        self.list = ttk.Treeview(self, columns=headings, selectmode='browse')
        self.sb = Scrollbar(self, orient=VERTICAL)
        self.sb.pack(side=RIGHT, fill=Y)

        self.list.config(yscrollcommand=self.sb.set)
        self.sb.config(command=self.list.yview)

        self.list.heading("#0", text="Month")
        self.list.column("#0", minwidth=0, width=100, anchor="center")
        for heading in headings:
            self.list.heading(heading, text=heading)
            self.list.column(heading, minwidth=0, width=100, anchor="center")
        self.list.pack(fill=BOTH,expand=1)
        self.list.bind('<Button-1>', self.handle_click)

    def handle_click(self, event):
        if self.list.identify_region(event.x, event.y) == "separator":
            return "break"

root = Tk()
root.title("Home Loan Calculator")
root.wm_attributes("-transparentcolor", TRANSPARENT)
root.resizable(False, False)
root.wm_attributes("-topmost", True)
root.geometry("600x600+50+50")
root.configure(bg=TRANSPARENT)
root.bind_all("<1>", lambda event:event.widget.focus_set())

bg_root = Toplevel(root)
bg_root.geometry("600x600+50+50")

bg = Background(bg_root)

topframe = Frame(root, bg=TRANSPARENT)
topframe.place(relx=0.5, rely=0.5, anchor=CENTER)

loan = EntryFrame(topframe, 'loan', inputs['loan'], font=LargeFont)
down = EntryFrame(topframe, 'down', inputs['down'], font=LargeFont)
rate = EntryFrame(topframe, 'rate', inputs['rate'], font=LargeFont)
year = EntryFrame(topframe, 'year', inputs['year'], font=LargeFont)

loan.config(text="Loan:")
down.config(text="Down Payment:")
rate.config(text="Interest Rate:")
year.config(text="Year:")

down.ent.set_range(upperbound=100)
rate.ent.set_range(upperbound=100)

loan.grid()
down.grid()
rate.grid()
year.grid()

debt = ResultFrame(topframe, text="Debt:", bg=TRANSPARENT, font=LargeFont)
principle = ResultFrame(topframe, text="Principle:", bg=TRANSPARENT, font=LargeFont)
interest = ResultFrame(topframe, text="Interest:", bg=TRANSPARENT, font=LargeFont)

debt.label.config(justify="center", font=LargeFont)
principle.label.config(justify="center", font=LargeFont)
interest.label.config(justify="center", font=LargeFont)

debt.grid(sticky="EW")
principle.grid(sticky="EW")
interest.grid(sticky="EW")


graph_frame = Frame(topframe, bg=TRANSPARENT)
graph_frame.grid(column=1, row=0, rowspan=7)

circle_graph = GraphCanvas(graph_frame, width=250, height=250, bg=TRANSPARENT, highlightthickness=0)
graph_title = Label(graph_frame, text="Payment Breakdown", bg=TRANSPARENT, font=LargeFont)


graph_frame_label = Frame(graph_frame, width=100, bg=TRANSPARENT)
graph_label1 = GraphLabel(graph_frame_label, text="Principle", color="#90ee90")
graph_label2 = GraphLabel(graph_frame_label, text="Interest", color="#006400")
graph_label1.text.config(bg=TRANSPARENT, font=LargeFont)
graph_label2.text.config(bg=TRANSPARENT, font=LargeFont)

graph_label1.grid(sticky="W")
graph_label2.grid(sticky="W")

graph_title.grid()
circle_graph.grid()
graph_frame_label.grid()

btn_print = Button(root, text="Print List", command=mortgage_list)
btn_print.place(relx=0.9, rely=0.9)

loan.ent._validation("")

bg.setup()
bg.animation()
root.mainloop()