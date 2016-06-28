vlc=None
plugin=None
player_frame=None

import Tkinter as tkint

class Channels(object):

    def __init__(self, channels):
        self.channels = channels

class Player(object):

    def __init__(self, parent):
        self.parent = parent

        width=parent.winfo_width() if parent.winfo_width()>1 else 1280
        height=parent.winfo_height() if parent.winfo_height()>1 else 720
        
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
    frame = tkint.Frame(parent, bg="black")
    frame.place(x=0,y=0,relwidth=1,relheight=1)

    global player_frame
    player_frame=Player(frame)




if __name__=="__main__":
    import sys, os
    sys.path.insert(0, os.path.join("..","..",".."))

    import extensions
    extensions.load_extension("vlc")
    
    import Tkinter as tkint
    root=tkint.Tk()
    root.geometry("1280x720+0+0")

    init()
    display(root)
    root.mainloop()
