vlc=None
plugin=None
player_frame=None


import Tkinter as tkint
import Queue

def ui_loop():
    import namb.userinput
    namb.userinput.process_next()
    root.after(10, ui_loop)

class List(object):

    def __init__(self, parent):
        self.temp_started=0
        self.parentclass =parent
        self.stop=[True]
        self.items = None
        self.parent = parent.frame
        self.pframe=tkint.Frame(self.parent, bg="#0f0f0f")
        self.pframe.place(x=0,y=height/10,width=width,height=int(((height/10.0)*9))-(height/30))
        self.frame = tkint.Frame(self.pframe, bg="#0f0f0f")
        self.frame.place(x=0,y=0,width=width,height=int(((height/10.0)*9)))
        self.at=0

    def shiftshift(self):
        import time
        now = int(time.time())
        diff=now-self.temp_started
        print("Time diff set to: %s"  % diff)
        plugin.TIME_DIFF=diff

    def focus_receive(self):
        self.activate(self.at)

    def receive(self, event):
        import namb.userinput.keys
        import namb.userinput
        if event==namb.userinput.keys.UP:
            self.shift(-1)
        elif event==namb.userinput.keys.DOWN:
            self.shift(1)
        elif event==namb.userinput.keys.ENTER:
            self.select()
        elif event==namb.userinput.keys.BACK:
            self.deactivate(self.at)
            namb.userinput.set_receiver(self.parentclass.tabs)
            self.parentclass.tabs.focus_receive()
        elif event=="test":
            self.shiftshift()

#TODO: Implement playlist for a channel. Deduce when a song it to end based on start and duration. Keep local clock of when it started etc. Gather information about next song without affecting the current timer.
    def currently_playing_loop(self, songchanges):
        st=self.stop
        c=self.playing
        import threading
        _stop = threading.Event()
        queue=songchanges

        def format_time(seconds):
            m=str(seconds/60)
            s=str(seconds%60)
            return m if len(m)>1 else "0"+m, s if len(s)>1 else "0"+s
        
        def display_current(artist, title):
            c[0].delete("current")
            c[0].create_text((c[0].winfo_width()/4), (c[0].winfo_height()/3), anchor=tkint.W, tags="current", text="%s - %s" % (artist, title),fill="white")

        def display_timing(current, duration):
            if duration==0:
                duration=duration+0.00000000000000001
            if current <= duration:
                div=current/float(duration)
                rem=duration-current
                c[0].delete("timer")
                c[0].create_rectangle(c[0].winfo_width()/4,(c[0].winfo_height()/8)*5,(c[0].winfo_width()/4)+(((c[0].winfo_width()/8)*5)*1),((c[0].winfo_height()/8)*7), fill="#2f2f2f", tags="timer", width=0)
                c[0].create_rectangle(c[0].winfo_width()/4,(c[0].winfo_height()/8)*5,(c[0].winfo_width()/4)+(((c[0].winfo_width()/8)*5)*div),((c[0].winfo_height()/8)*7), fill="#7f7f7f", tags="timer", width=0)
                c[0].create_text(c[0].winfo_width()/4, (c[0].winfo_height()/8)*6, anchor=tkint.W, tags="timer", text=" %s:%s"%format_time(current),fill="white")
                c[0].create_text((c[0].winfo_width()/8)*7, (c[0].winfo_height()/8)*6, anchor=tkint.E, tags="timer", text="-%s:%s "%format_time(rem),fill="white")

        
        start, duration, artist, title = plugin.get_playing_position(c[1]['key'])
        display_current(artist, title)
        #self.temp_started=start
        #display_current(artist, title)
        import time,datetime
        def loop(start, duration, ev, f):
            now=(plugin.get_msec_epoch()/1000)
            current=int(now-start)
            if not ev:
                if not queue.empty():
                    ev=queue.get()
                else:
                    pass
            if ev:
                if ev[0]<time.time():
                    start, duration, a, t = plugin.get_playing_position(c[1]['key'])
                    if f == 1: #Reset time diff to be more accurate
                        start=start-plugin.TIME_DIFF
                        plugin.TIME_DIFF=now-start
                        start=start+plugin.TIME_DIFF
                    print(ev)
                    sev=ev[1].split(" - ")
                    artist=sev[0]
                    if len(sev)>1:
                        title=sev[1]
                    else:
                        title="No title"
                    display_current(a, t)
                    ev=None
                    f=f+1
            display_timing(current, duration)
            if st[0]:
                c[0].after(1000, lambda: loop(start, duration, ev, f))
            else:
                c[0].delete("timer")
                c[0].delete("current")
                _stop.set()
        
        c[0].after(1, lambda: loop(start, duration, None, 0))
        
        

    def select(self):
        key=self.items[self.at][1]['key']
        def d():
            self.stop[0]=False
            self.stop=[True]
            self.playing=self.items[self.at]
            plugin.create_player()
            media=plugin.generate_media(key)
            plugin.set_media(media.get_media())
            if plugin.play()==0:
                self.frame.after(1, lambda: self.currently_playing_loop(media.songchanges))
                #self.frame.after(1000, lambda: print(plugin.PLAYER.))
        self.frame.after(1, d)



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

    def activate(self, item):
        self.items[item][0].config(bg="#9f9f9f")

    def deactivate(self, item):
        self.items[item][0].config(bg="#5f5f5f" if item%2==0 else "#4f4f4f")

    def update(self, posneg):
        prev=self.at
        cur=self.at+posneg
        self.deactivate(prev)
        self.activate(cur)
        self.at=self.at+posneg

    def clear(self):
        self.items = None

    def shift(self, posneg):
        p=posneg #*-1
        if p+self.at<0 or p+self.at==len(self.items):
            return

        if self.items[p+self.at][0].winfo_y()+self.frame.winfo_y()>(height/10.0)*8 or self.items[p+self.at][0].winfo_y()+self.frame.winfo_y()<height/30:
            offset=posneg*(height/15)*-1
            self.frame.place(y=self.frame.winfo_y()+offset)

        self.update(p)
        
        

class Tabs(object):

    def __init__(self, parent):
        self.parentclass=parent
        self.parent = parent.frame

        self.frame = tkint.Frame(self.parent, bg="#1f1f1f")
        self.frame.place(x=0,y=0,width=width,height=int(height/10.0))

        self.channelscanvas = tkint.Canvas(self.frame,bg="#1f1f1f", highlightthickness=0)
        self.channelscanvas.place(x=0,y=0,width=width/2,height=height/10)

        self.channelscanvastext = self.channelscanvas.create_text(width/4, height/20, text="Channels", fill="white", font=("Verdana", 18))

        self.filterscanvas = tkint.Canvas(self.frame,bg="#1f1f1f", highlightthickness=0)
        self.filterscanvas.place(x=width/2,y=0,width=width/2,height=height/10)

        self.filterscanvastext = self.filterscanvas.create_text(width/4,height/20,text="Filters", fill="white", font=("Verdana", 18))

        self.channelscanvas.bind("<Enter>", lambda e: self.activate_channels())
        self.channelscanvas.bind("<Leave>", lambda e: self.deactivate_channels())

        self.filterscanvas.bind("<Enter>", lambda e: self.activate_filters())
        self.filterscanvas.bind("<Leave>", lambda e: self.deactivate_filters())

        self.activate_channels()
        self.deactivate_filters()

    def focus_receive(self):
        pass
        
    def receive(self, key):
        import namb.userinput
        import namb.userinput.keys
        if key==namb.userinput.keys.LEFT:
            self.deactivate_filters()
            self.activate_channels()
        elif key==namb.userinput.keys.RIGHT:
            self.deactivate_channels()
            self.activate_filters()
        elif key==namb.userinput.keys.BACK:
            pass
        elif key==namb.userinput.keys.ENTER:
            namb.userinput.set_receiver(self.parentclass.list)
            self.parentclass.list.focus_receive()

    def activate_channels(self):
        self.channelscanvas.config(bg="#2f2f2f")
        self.channelscanvas.itemconfig(self.channelscanvastext, fill="white")

    def deactivate_channels(self):
        self.channelscanvas.config(bg="#1f1f1f")
        self.channelscanvas.itemconfig(self.channelscanvastext, fill="#cccccc")

    def activate_filters(self):
        self.filterscanvas.config(bg="#2f2f2f")
        self.filterscanvas.itemconfig(self.filterscanvastext, fill="white")

    def deactivate_filters(self):
        self.filterscanvas.config(bg="#1f1f1f")
        self.filterscanvas.itemconfig(self.filterscanvastext, fill="#cccccc")
        

class Menu(object):

    def __init__(self, parent):
        self.parent = parent
        self.frame = tkint.Frame(self.parent, bg="#0f0f0f")
        self.frame.place(x=0,y=0,width=width,height=int((height)))
        self.list=List(self)
        self.tabs=Tabs(self)
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
    #player_frame=Player(frame)
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

    import namb.userinput.keyboard
    namb.userinput.keyboard.setup()
    namb.userinput.keyboard.bind(root)

    import namb.userinput.ui_server
    namb.userinput.ui_server.run()

    init()
    display(root, (root.winfo_screenwidth(), root.winfo_screenheight()))
    import namb.userinput
    namb.userinput.set_receiver(menu_frame.list)
    ui_loop()
    root.mainloop()
