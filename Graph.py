from tkinter import *
from BezierEasing import bezier

"""
    tkinter circle graph
    with animation
"""

class GraphCanvas(Canvas):
    OFFSET = 90
    def __init__(self, master, *args, animation={'duration': 1000}, **kwargs):
        # ValueErrors
        # if not len(data):
        #   raise ValueError("CircleGraph.__init__  \'data\' argument cannot be empty")

        self.series = {}
        self.acceleration = 0.01
        self.b = bezier(0,0,0.3,1)
        super().__init__(master, *args, **kwargs)

        # instance attribute with a starting _ are supposed to be hidden for internally uses only

        self._sum = 0 # total value from data
        self._extent = [] # list of end angles for every arc
        self._arcs = []

        # animation dependant attributes
        self._step = 0
        self._end = 0 # the current angle that is rendered
        self._ind = 0  # acts as a pointer for _arcs

    
    # cal must be called everytime an attribute is changed except animation dependant attributes
    def cal(self, data):
        self.update()
        height = self.winfo_height() - 5
        width = self.winfo_width() - 5
        self.series = data
        # clear previous values
        self._extent = []
        for i in range(len(self._arcs)-1, -1, -1):
            self.delete(self._arcs.pop(i))

        self._sum = 0

        # This loop must come immediately after initialization of variables
        # otherwise, self._angle() would failed as it's dependant on this._sum
        length = len(self.series) # shorten code
        for i in range(length):
            self._sum += self.series[i]["value"]

        tmp = 0 # 
        for i in range(length):
            tmp += self.series[i]["value"]
            if i == length-1: 
                self._extent.append(360)
            self._extent.append(self._angle(tmp))

        tmp = 0 # reset variable's value
        for i in range(length):
            try:
                color = self.series[i]["color"]
            except:
                color = "blue"

            self._arcs.append(self.create_arc(5, 5, width, height, start=tmp+self.__class__.OFFSET, extent=0, fill=color, outline=""))
            tmp = self._extent[i]

    def animate(self):
        # reset
        self._step = 0
        self._end = 0
        self._ind = 0

        for i in self._arcs:
            self.delete(self.itemconfigure(i, extent=0))

        self._animation()


    # functions that are called internally by instance
    def _angle(self, n):
        return 360 * n / self._sum

    def _animation(self):
        if self._end > 360:
            self._end = 360

        if self._extent[self._ind] < self._end:
            cur = float(self.itemcget(self._arcs[self._ind], "start"))
            nx = float(self.itemcget(self._arcs[self._ind + 1], "start"))
            
            # nx is smaller than cur when nx cross the 360 degrees cap
            # cause nx is modulus by 360, thus 360 is re-added to compensate
            self.itemconfigure(self._arcs[self._ind], extent=nx-cur if nx>cur else nx+360-cur)
            self._ind += 1

        start = float(self.itemcget(self._arcs[self._ind], "start")) - self.__class__.OFFSET  # offset is subtracted to recalibrate start's value
        self.itemconfigure(self._arcs[self._ind], extent=self._end-start) 

        if self._end >= 360:
            return

        self._step += self.acceleration
        self._end = self.b(self._step) * 360
        self.after(10, self._animation)

class GraphLabel(Frame):
	def __init__(self, master, color="red", text=""):
		super().__init__(master, bg="#576890")
		self.icon = Frame(self, bg=color, width=10, height=10)
		self.text = Label(self, text=text)
		self.icon.pack(side=LEFT)
		self.text.pack(side=RIGHT)
