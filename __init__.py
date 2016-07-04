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
        self.parent.master.master.bind("<Up>", lambda e: self.shift(1))
        self.parent.master.master.bind("<Down>", lambda e: self.shift(-1))
        self.parent.master.master.bind("<Return>", lambda e: self.select())

    def receive(self, event):
        import namb.keys
        import namb.ui_processor
        if event==namb.keys.UP:
            self.shift(1)
        elif event==namb.keys.DOWN:
            self.shift(-1)
        elif event==namb.keys.ENTER:
            self.select()
        elif event==namb.keys.BACK:
            namb.ui_processor.set_receiver(self.parent.tabs)

    def currently_playing_loop():
        d=plugin.get_channel_history(self.playing[1]['id'])
        start=d['started']
        duration=d['length']
        import time
        def loop():
            current=time.time.now()-start
            self.playing[0].delete("timer")
            self.playing[0].create_text(100, 100, anchor=("timer",), text=str(current))
            self.playing[0].after(1000, loop)
        self.playing[0].after(1000, loop)
        
        

    def select(self):
        key=self.items[self.at][1]['key']
        self.playing=self.items[self.at]
        if plugin.play(key)==0:
            self.frame.after(1000, self.currently_playing_loop)

    def populate(self, items):
        self.items = []
        for i in items:
            self.items.append((tkint.Canvas(self.frame, bg="#5f5f5f", highlightthickness=0), i))
        self.frame.place(height=int((height/15)*(len(items)+1)))
        index=-1
        offset=height/30
        for i in self.items:
            index=index+1
            i[0].config(bg="#5f5f5f" if index%2==0 else "#4f4f4f")
            i[0].place(x=0,y=offset+(index*(height/15)), width=width, height=height/15)
            i[0].create_text(width/30,height/30,anchor=tkint.W, text=i[1]["name"],fill="white", font=("Verdana", 18))
            #i[0].create_text(width/2,height/30,text=i[1]["name"],fill="white", font=("Verdana", 18))

        self.update(0)

    def update(self, posneg):
        prev=self.at
        cur=self.at+posneg
        self.items[prev][0].config(bg="#5f5f5f" if prev%2==0 else "#4f4f4f")
        self.items[cur][0].config(bg="#9f9f9f")
        self.at=self.at+posneg
        print(self.at)

    def clear(self):
        self.items = None

    def shift(self, posneg):
        p=posneg*-1
        if p+self.at<0 or p+self.at==len(self.items):
            return

        if self.items[p+self.at][0].winfo_y()+self.frame.winfo_y()>(height/10.0)*8 or self.items[p+self.at][0].winfo_y()+self.frame.winfo_y()<height/10:
            offset=posneg*(height/15)
            self.frame.place(y=self.frame.winfo_y()+offset)

        self.update(p)
        
        

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
        self.list.populate(plugin.CHANNELS)

class Player(object):

    def __init__(self, parent):
        self.parent = parent

        #width=parent.winfo_width() if parent.winfo_width()>1 else 1280
        #height=parent.winfo_height() if parent.winfo_height()>1 else 720
        
        self.playerframe = tkint.Frame(self.parent, bg="#2f2f2f")
        self.playerframe.place(x=0,rely=.9,relwidth=1,relheight=.1)

        self.playbutton = tkint.Canvas(self.playerframe, bg="#2f2f2f", highlightthickness=0)
        self.playbutton.place(x=width/100, y=0, width=.1*height, height=.1*height)

        self.playbuttontriangle = self.playbutton.create_polygon([height/50,height/50,(height/10)-height/50,height/20,height/50,(height/10)-height/50], fill="gray")

        self.playbutton.tag_bind(self.playbuttontriangle, "<Enter>", lambda e: self.playbutton.itemconfig(self.playbuttontriangle, fill="white"))
        self.playbutton.tag_bind(self.playbuttontriangle, "<Leave>", lambda e: self.playbutton.itemconfig(self.playbuttontriangle, fill="gray"))
        self.playbutton.bind("<Enter>", lambda e: self.playbutton.config(background="#4f4f4f"))
        self.playbutton.bind("<Leave>", lambda e: self.playbutton.config(background="#2f2f2f"))

        self.stopbutton = tkint.Canvas(self.playerframe, bg="#2f2f2f", highlightthickness=0)
        self.stopbutton.place(x=(width/50)+(height/10), y=0, width=height/10, height=height/10)

        self.stopbuttonsquare = self.stopbutton.create_polygon([height/50,height/50, (height/10)-(height/50), height/50, (height/10)-(height/50), (height/10)-(height/50), height/50, (height/10)-(height/50)], fill="gray")
            
        self.stopbutton.tag_bind(self.stopbuttonsquare, "<Enter>", lambda e: self.stopbutton.itemconfig(self.stopbuttonsquare, fill="white"))
        self.stopbutton.tag_bind(self.stopbuttonsquare, "<Leave>", lambda e: self.stopbutton.itemconfig(self.stopbuttonsquare, fill="gray"))
        self.stopbutton.bind("<Enter>", lambda e: self.stopbutton.config(background="#4f4f4f"))
        self.stopbutton.bind("<Leave>", lambda e: self.stopbutton.config(background="#2f2f2f"))

        self.playing = tkint.Canvas(self.playerframe, bg="#4f4f4f", highlightthickness=0)
        self.playing.place(x=(width/50)+(height/5)+(width/100), y=height/100, width=.85*width, height=(height/25)-(height/100))

        self.playingtext = self.playing.create_text(height/100, height/100, anchor=tkint.W, text="Lorem ipsum    -    Artists name", fill="white", font=("Verdana", 12))


        self.timebar = tkint.Canvas(self.playerframe, bg="#1f1f1f", highlightthickness=0,bd=0)
        self.timebar.place(x=(width/50)+(height/5)+(width/100), y=(height/100)+(height/25), width=.85*width, height=(height/25)-(height/100))

        self.currentloctext=self.timebar.create_text(.85*width,((height/25)-(height/100))/2, anchor=tkint.E, text="0:00", fill="white")

        self.currentloc = self.timebar.create_polygon([0,0,(.85*width)/2,0,(.85*width)/2, (height/25)-(height/100),0,(height/25)-(height/100)], fill="gray")
    

def init():
    global plugin
    import plugin
    plugin.load_channels()
    plugin.initialize_dict()

def display(parent, geom=(1280,720)):

    global width
    width=parent.winfo_width() if parent.winfo_width() > 1 else geom[0]
    global height
    height=parent.winfo_height() if parent.winfo_height() > 1 else geom[1]
    
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

    global root
    
    #import Tkinter as tkint
    root=tkint.Tk()
    #root.geometry("1280x720+0+0")
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", lambda e: root.destroy())
    root.focus_set()

    init()
    display(root, (root.winfo_screenwidth(), root.winfo_screenheight()))
    root.mainloop()
