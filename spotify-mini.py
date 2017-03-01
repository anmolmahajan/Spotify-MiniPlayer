#!/usr/bin/env python2
import sys, os
import urllib,subprocess
import dbus,sys
import threading
import Tkinter as tk
from PIL import ImageTk, Image


osd = False
if(len(sys.argv) > 1):
	osd = True


img = Image.new('RGB', (50, 50))
img.save('/tmp/File.jpg')
root = tk.Tk()
img = ImageTk.PhotoImage(Image.open('/tmp/File.jpg'))
panel = tk.Label(root, image = img)
panel.pack(side = "bottom", fill = "both", expand = "yes")


def imgchange():
	img2 = ImageTk.PhotoImage(Image.open('/tmp/File.jpg'))
	panel.configure(image = img2)
	panel.image = img2


def getart(image_url):
	try:
		urllib.urlretrieve(image_url,"/tmp/File.jpg")
	except Exception,e:
		print('Sorry, no dice.')
	imgchange()

song = ""
msg = ""
pid = ""
prev_url = ""

def check():
	threading.Timer(1.0, check).start()
	session_bus = dbus.SessionBus()
	spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
									 "/org/mpris/MediaPlayer2")
	spotify_properties = dbus.Interface(spotify_bus,
									"org.freedesktop.DBus.Properties")
	metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
	title =  str(metadata['xesam:title'])
	length = metadata['mpris:length']
	length = length / 1000
	artist = str(metadata['xesam:artist'][0])
	album = metadata['xesam:album']
	img_url = metadata['mpris:artUrl']
	global song
	if(str(title) != str(song)):
		song = str(title)
		time = "-t " + str(length)
		global msg
		msg = str(artist) + ' - ' + str(album)
		global prev_url
		if(str(prev_url) != str(img_url)):
			getart(img_url)
			prev_url = str(img_url)
		if(osd == True): 
			if(pid != ""):
					pid = subprocess.Popen(["notify-send", "-p","-r", str(int(pid)),"-t" ,str(length),title, msg], stdout=subprocess.PIPE).communicate()[0]
			else:
					pid = subprocess.Popen(["notify-send", "-p","-t" ,str(length),title, msg], stdout=subprocess.PIPE).communicate()[0]
		

def callback_exit(e):
	cm = "pkill python2"
	subprocess.Popen(cm.split(), stdout=subprocess.PIPE)

def callback_click(e):
	subprocess.Popen(['notify-send','-t','1000', str(song), str(msg)], stdout=subprocess.PIPE)

def callback_back(e):
	cm = "playerctl previous"
	subprocess.Popen(cm.split())

def callback_next(e):
	cm = "playerctl next"
	subprocess.Popen(cm.split())

def callback_toggle(e):
	cm = "playerctl play-pause"
	subprocess.Popen(cm.split())
	callback_click(root)

FNULL = open(os.devnull, 'w')
def callback_up(e):
	cm = "amixer set Master 3%+"
	subprocess.Popen(cm.split(), stdout=FNULL)

def callback_down(e):
	cm = "amixer set Master 3%-"
	subprocess.Popen(cm.split(), stdout=FNULL)


root.bind("<Escape>", callback_exit)
root.bind("<Button-1>",callback_toggle)
root.bind("<Button-3>",callback_click)
root.bind("<space>",callback_toggle)
root.bind("<Up>", callback_up)
root.bind("<Down>", callback_down)
root.bind("<Button-4>",callback_up)
root.bind("<Button-5>",callback_down)
root.bind("<Left>", callback_back)
root.bind("<Right>", callback_next)
root.after(0, check)
root.mainloop()