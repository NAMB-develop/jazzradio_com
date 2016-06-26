vlc=None
plugin=None

def init():
    global plugin
    import plugin

def play():
    global vlc
    i = vlc.get_default_instance()
    print(i)

def display(parent):
    import Tkinter as tkint
    
    width=parent.winfo_width() if parent.winfo_width()>1 else 1280
    height=parent.winfo_height() if parent.winfo_height()>1 else 720
    
    frame = tkint.Frame(parent, bg="black")
    frame.place(x=0,y=0,relwidth=1,relheight=1)

    playerframe = tkint.Frame(frame, bg="#3f3f3f")
    playerframe.place(x=0,rely=.9,relwidth=1,relheight=.1)

    playbutton = tkint.Canvas(playerframe, bg="#3f3f3f", highlightthickness=0)
    playbutton.place(x=width/100, y=0, width=.1*height, height=.1*height)

    playbuttontriangle = playbutton.create_polygon([height/50,height/50,(height/10)-height/50,height/20,height/50,(height/10)-height/50], fill="gray")

    playbutton.tag_bind(playbuttontriangle, "<Enter>", lambda e: playbutton.itemconfig(playbuttontriangle, fill="white"))
    playbutton.tag_bind(playbuttontriangle, "<Leave>", lambda e: playbutton.itemconfig(playbuttontriangle, fill="gray"))
    playbutton.bind("<Enter>", lambda e: playbutton.config(background="#4f4f4f"))
    playbutton.bind("<Leave>", lambda e: playbutton.config(background="#3f3f3f"))

    stopbutton = tkint.Canvas(playerframe, bg="#3f3f3f", highlightthickness=0)
    stopbutton.place(x=(width/50)+(height/10), y=0, width=height/10, height=height/10)

    stopbuttonsquare = stopbutton.create_polygon([height/50,height/50, (height/10)-(height/50), height/50, (height/10)-(height/50), (height/10)-(height/50), height/50, (height/10)-(height/50)], fill="gray")
        
    stopbutton.tag_bind(stopbuttonsquare, "<Enter>", lambda e: stopbutton.itemconfig(stopbuttonsquare, fill="white"))
    stopbutton.tag_bind(stopbuttonsquare, "<Leave>", lambda e: stopbutton.itemconfig(stopbuttonsquare, fill="gray"))
    stopbutton.bind("<Enter>", lambda e: stopbutton.config(background="#4f4f4f"))
    stopbutton.bind("<Leave>", lambda e: stopbutton.config(background="#3f3f3f"))

    playing = tkint.Canvas(playerframe, bg="#4f4f4f", highlightthickness=0)
    playing.place(x=(width/50)+(height/5)+(width/100), y=height/100, width=.85*width, height=(height/25)-(height/100))

    playingtext = playing.create_text(height/100, height/100, anchor=tkint.W, text="Lorem ipsum    -    Artists name", fill="white", font=("Verdana", 12))


    timebar = tkint.Canvas(playerframe, bg="#1f1f1f", highlightthickness=0,bd=0)
    timebar.place(x=(width/50)+(height/5)+(width/100), y=(height/100)+(height/25), width=.85*width, height=(height/25)-(height/100))

    currentloc = timebar.create_polygon([0,0,(.85*width)/2,0,(.85*width)/2, (height/25)-(height/100),0,(height/25)-(height/100)], fill="gray")


if __name__=="__main__":
    import Tkinter as tkint
    root=tkint.Tk()
    root.geometry("1280x720+0+0")
    display(root)
    root.mainloop()
