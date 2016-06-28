vlc=None
plugin=None
player_frame=None

import Tkinter as tkint

class List(object):

    def __init__(self, parent):
        self.items = None
        self.parent = parent
        self.frame = tkint.Frame(self.parent, bg="#0f0f0f")
        self.frame.place(x=0,y=height/10,width=width,height=int((height/10.0)*8))
        self.at=0

    def populate(self, items):
        self.items = []
        for i in items:
            self.items.append((tkint.Canvas(self.frame, bg="gray", highlightthickness=0), i))
        self.frame.place(height=int((height/15.0)*len(items)))
        index=-1
        for i in self.items:
            index=index+1
            i[0].place(x=0,y=(index*(height/15.0)), width=width, height=height/15)
            i[0].create_text(0,0,text="Hello",fill="white")

        self.frame.place(y=(height/10)-(height/15))

    def clear(self):
        self.items = None
        

class Tabs(object):

    def __init__(self, parent):
        self.parent = parent

        self.frame = tkint.Frame(self.parent, bg="#1f1f1f")
        self.frame.place(x=0,y=0,width=width,height=int(height/10.0))

        self.channelscanvas = tkint.Canvas(self.frame,bg="#1f1f1f", highlightthickness=0)
        self.channelscanvas.place(x=0,y=0,width=width/2,height=height/10)

        self.channelscanvastext = self.channelscanvas.create_text(width/4, height/20, text="Channels", fill="white", font=("Verdana", 24))

        self.filterscanvas = tkint.Canvas(self.frame,bg="#1f1f1f", highlightthickness=0)
        self.filterscanvas.place(x=width/2,y=0,width=width/2,height=height/10)

        self.filterscanvastext = self.filterscanvas.create_text(width/4,height/20,text="Filters", fill="white", font=("Verdana", 24))

        self.channelscanvas.bind("<Enter>", lambda e: self.activate_channels())
        self.channelscanvas.bind("<Leave>", lambda e: self.deactivate_channels())

        self.filterscanvas.bind("<Enter>", lambda e: self.activate_filters())
        self.filterscanvas.bind("<Leave>", lambda e: self.deactivate_filters())

    def activate_channels(self):
        self.channelscanvas.config(bg="#2f2f2f")
        self.channelscanvas.itemconfig(self.channelscanvastext, fill="#cccccc")

    def deactivate_channels(self):
        self.channelscanvas.config(bg="#1f1f1f")
        self.channelscanvas.itemconfig(self.channelscanvastext, fill="white")

    def activate_filters(self):
        self.filterscanvas.config(bg="#2f2f2f")
        self.filterscanvas.itemconfig(self.filterscanvastext, fill="#cccccc")

    def deactivate_filters(self):
        self.filterscanvas.config(bg="#1f1f1f")
        self.filterscanvas.itemconfig(self.filterscanvastext, fill="white")
        

class Menu(object):

    def __init__(self, parent):
        self.parent = parent
        self.frame = tkint.Frame(self.parent, bg="#0f0f0f")
        self.frame.place(x=0,y=0,width=width,height=int((height/100.0)*90))
        self.list=List(self.frame)
        self.tabs=Tabs(self.frame)
        self.list.populate("a b c d e f g".split(" "))

class Player(object):

    def __init__(self, parent):
        self.parent = parent

        #width=parent.winfo_width() if parent.winfo_width()>1 else 1280
        #height=parent.winfo_height() if parent.winfo_height()>1 else 720
        
        self.playerframe = tkint.Frame(self.parent, bg="#3f3f3f")
        self.playerframe.place(x=0,rely=.9,relwidth=1,relheight=.1)

        self.playbutton = tkint.Canvas(self.playerframe, bg="#3f3f3f", highlightthickness=0)
        self.playbutton.place(x=width/100, y=0, width=.1*height, height=.1*height)

        self.playbuttontriangle = self.playbutton.create_polygon([height/50,height/50,(height/10)-height/50,height/20,height/50,(height/10)-height/50], fill="gray")

        self.playbutton.tag_bind(self.playbuttontriangle, "<Enter>", lambda e: self.playbutton.itemconfig(self.playbuttontriangle, fill="white"))
        self.playbutton.tag_bind(self.playbuttontriangle, "<Leave>", lambda e: self.playbutton.itemconfig(self.playbuttontriangle, fill="gray"))
        self.playbutton.bind("<Enter>", lambda e: self.playbutton.config(background="#4f4f4f"))
        self.playbutton.bind("<Leave>", lambda e: self.playbutton.config(background="#3f3f3f"))

        self.stopbutton = tkint.Canvas(self.playerframe, bg="#3f3f3f", highlightthickness=0)
        self.stopbutton.place(x=(width/50)+(height/10), y=0, width=height/10, height=height/10)

        self.stopbuttonsquare = self.stopbutton.create_polygon([height/50,height/50, (height/10)-(height/50), height/50, (height/10)-(height/50), (height/10)-(height/50), height/50, (height/10)-(height/50)], fill="gray")
            
        self.stopbutton.tag_bind(self.stopbuttonsquare, "<Enter>", lambda e: self.stopbutton.itemconfig(self.stopbuttonsquare, fill="white"))
        self.stopbutton.tag_bind(self.stopbuttonsquare, "<Leave>", lambda e: self.stopbutton.itemconfig(self.stopbuttonsquare, fill="gray"))
        self.stopbutton.bind("<Enter>", lambda e: self.stopbutton.config(background="#4f4f4f"))
        self.stopbutton.bind("<Leave>", lambda e: self.stopbutton.config(background="#3f3f3f"))

        self.playing = tkint.Canvas(self.playerframe, bg="#4f4f4f", highlightthickness=0)
        self.playing.place(x=(width/50)+(height/5)+(width/100), y=height/100, width=.85*width, height=(height/25)-(height/100))

        self.playingtext = self.playing.create_text(height/100, height/100, anchor=tkint.W, text="Lorem ipsum    -    Artists name", fill="white", font=("Verdana", 12))


        self.timebar = tkint.Canvas(self.playerframe, bg="#1f1f1f", highlightthickness=0,bd=0)
        self.timebar.place(x=(width/50)+(height/5)+(width/100), y=(height/100)+(height/25), width=.85*width, height=(height/25)-(height/100))

        self.currentloc = self.timebar.create_polygon([0,0,(.85*width)/2,0,(.85*width)/2, (height/25)-(height/100),0,(height/25)-(height/100)], fill="gray")
    

def init():
    global plugin
    import plugin
    plugin.load_channels()
    plugin.initialize_dict()

def display(parent):

    global width
    width=parent.winfo_width() if parent.winfo_width() > 1 else 1280
    global height
    height=parent.winfo_height() if parent.winfo_height() > 1 else 720
    
    frame = tkint.Frame(parent, bg="black")
    frame.place(x=0,y=0,relwidth=1,relheight=1)

    global player_frame
    player_frame=Player(frame)
    global menu_frame
    menu_frame=Menu(frame)




if __name__=="__main__":
    import sys, os
    sys.path.insert(0, os.path.join("..","..",".."))

    import extensions
    extensions.load_extension("vlc")
    
    #import Tkinter as tkint
    root=tkint.Tk()
    root.geometry("1280x720+0+0")

    init()
    display(root)
    root.mainloop()
