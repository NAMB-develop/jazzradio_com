import imem



import sys, os
sys.path.insert(0, os.path.join("..","..",".."))

import extensions
extensions.load_extension("vlc")

global instance
instance=extensions.get_extension("vlc").Instance('-vvv')

mm=imem.Media(instance, "http://icecast.omroep.nl/radio4-bb-mp3")
p=instance.media_player_new()

p.set_media(mm.get_media())
p.play()

#TODO: Wrap everything else around this
