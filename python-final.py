
#!/usr/bin/env python
# -*- coding: big5 -*-
from Tkinter import *
from FileDialog import *
from mediaPlayer import MediaPlayer
import threading
import vlc
from PIL import ImageTk
import tkFileDialog
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
list_num = 0
song_list = {}
song_list["song"] = []
search_list = [{"song":"aaa","length":"0:36"},{"song":"bbb","length":"0:354"}]
num = 0.0
switch = 0
class GUIDemo(Frame):
	global list_num
	global num
	def __init__(self, master=None):
		self.mediaPlayer = MediaPlayer()
		Frame.__init__(self, master)
		self.grid()
		self.createWidgets()
		self.search_name = ""
		self.play = 0

	def createWidgets(self):
		def open_file():
			global num
			global list_num
			file_path = tkFileDialog.askopenfilename()
			audio_format = file_path.split('.')[-1]
			if file_path != "" and (audio_format=="mp3" or audio_format=="m4a"):
				self.mediaPlayer.play_list.append(file_path.encode('utf8'))
				if audio_format == "mp3":
					audio = MP3(file_path)
					mm, ss = divmod(audio.info.length, 60)
				else:
					audio = MP4(file_path)
					mm, ss = divmod(audio.info.length, 60)
				song_length = "%02d:%02d" % (mm,ss)

				line = file_path.split("/")
				file_name = line.pop()
				if file_name != 'None':
					file_name_c = file_name
					song_ii = file_name_c+"         "+song_length
					song_list['song'].append(song_ii)
					self.song_list.delete(0,self.song_list.size())
					for i in song_list['song']:
						list_num+=1
						song_i = i
						self.song_list.insert(list_num,song_i)
					self.song_list.bind("<Double-Button-1>", double_click_playlist)
					self.song_list.selection_clear(0, "end")
					self.song_list.selection_set(self.mediaPlayer.play_target)
		def search():
			if self.search.get() != "" and self.search.get() != None:
				print self.search.get() + "**"
				self.search_name = self.search.get()
				t1 = threading.Thread(target=search_thread)
				t1.start()
		def search_thread():
			global list_num
			self.mediaPlayer.search_song(self.search_name)
			if self.search_list_show.size != 0:
				self.search_list_show.delete(0,self.search_list_show.size())
			for item in self.mediaPlayer.search_list:
				list_num+=1
				info = (item["song"][:12] + '..') if len(item["song"]) > 12 else item["song"]
				search_song_str = info + " "*10 + item["length"]
				self.search_list_show.insert(list_num,search_song_str)
			print self.search.get()

		def click_search(e):
			global list_num
			list_num = 0
			index = self.search_list_show.curselection()[0]
			t1 = threading.Thread(target=self.mediaPlayer.listen_song, args=[self.mediaPlayer.search_list[int(index)]['link']])
			t1.start()

			if self.search_list_show.size != 0:
				self.search_list_show.delete(0,self.search_list_show.size())
			for item in self.mediaPlayer.search_list:
				
				if list_num != index:
					info = (item["song"][:12] + '..') if len(item["song"]) > 12 else item["song"]
				else:
					info = item["song"]
				search_song_str = info + " "*10 + item["length"]
				self.search_list_show.insert(list_num,search_song_str)
				list_num+=1
			self.search_list_show.selection_set(index)

		def play_song():
			if self.mediaPlayer.vlc_p == 0 or self.mediaPlayer.vlc_p.get_state() == vlc.State.Ended:
				t1 = threading.Thread(target=load_lyric, args=[self.mediaPlayer.play_list[self.mediaPlayer.play_target]])
				t1.start()
				
			t2 = threading.Thread(target=self.mediaPlayer.play)
			t2.start()
			if self.play == 0:
				self.photo_play = ImageTk.PhotoImage(file = "pause.jpg")
				self.btn_play["image"] = self.photo_play
				self.play = 1
			else:
				self.photo_play = ImageTk.PhotoImage(file = "play.jpg")
				self.btn_play["image"] = self.photo_play
				self.play = 0
			
		def load_lyric(song_name):
			self.lyrics["state"] = "normal"
			self.mediaPlayer.load_lyric(song_name)
			self.lyrics.delete(1.0,END)
			self.lyrics.insert(1.0,self.mediaPlayer.lyric)
			self.lyrics["state"] = "disabled"

		def download():
			index = self.search_list_show.curselection()[0]
			t1 = threading.Thread(target=self.mediaPlayer.download_song, args=[self.search_name,self.mediaPlayer.search_list[int(index)]['link']])
			t1.start()
		def previous():
			if self.mediaPlayer.play_target - 1 != -1 and self.mediaPlayer.vlc_p != 0:
				self.mediaPlayer.play_target -= 1
				t1 = threading.Thread(target=load_lyric, args=[self.mediaPlayer.play_list[self.mediaPlayer.play_target]])
				t1.start()
				t2 = threading.Thread(target=self.mediaPlayer.previous_or_next_song)
				t2.start()
				self.photo_play = ImageTk.PhotoImage(file = "pause.jpg")
				self.btn_play["image"] = self.photo_play
				self.play = 1
				self.song_list.selection_clear(0, "end")
				self.song_list.selection_set(self.mediaPlayer.play_target)
		def next_song():
			if self.mediaPlayer.play_target + 1 != len(self.mediaPlayer.play_list) and self.mediaPlayer.vlc_p != 0:
				self.mediaPlayer.play_target += 1
				t1 = threading.Thread(target=load_lyric, args=[self.mediaPlayer.play_list[self.mediaPlayer.play_target]])
				t1.start()
				t2 = threading.Thread(target=self.mediaPlayer.previous_or_next_song)
				t2.start()
				self.photo_play = ImageTk.PhotoImage(file = "pause.jpg")
				self.btn_play["image"] = self.photo_play
				self.play = 1
				self.song_list.selection_clear(0, "end")
				self.song_list.selection_set(self.mediaPlayer.play_target)
		def click_now_playing(e):
			pass
		def double_click_playlist(e):
			index = self.song_list.curselection()[0]
			self.mediaPlayer.play_target = index
			t1 = threading.Thread(target=load_lyric, args=[self.mediaPlayer.play_list[self.mediaPlayer.play_target]])
			t1.start()
			t2 = threading.Thread(target=self.mediaPlayer.previous_or_next_song)
			t2.start()
			self.photo_play = ImageTk.PhotoImage(file = "pause.jpg")
			self.btn_play["image"] = self.photo_play
			self.play = 1

		self.search = Entry(self)
		self.search["width"] = "20"
		self.search.grid(row=0, column=5)


		self.btn_search = Button(self)
		self.btn_search["width"] = "10"
		self.btn_search["text"] = "search"
		self.btn_search.grid(row=0, column=6)
		self.btn_search["command"] = search #method

		self.now_playing = Label(self)
		self.now_playing["width"] = "30"
		self.now_playing["text"] = "now_playing:"
		self.now_playing.grid(row = 0,column = 3)

		self.btn_open_file = Button(self)
		self.btn_open_file["width"] = "10"
		self.btn_open_file["text"] = "open_file"
		self.btn_open_file.grid(row=0, column=4)
		self.btn_open_file["command"] = open_file #method


		self.search_list_show = Listbox(self)
		self.search_list_show.grid(row = 1,column = 5,rowspan = 1,columnspan = 2)
		self.search_list_show["width"] = "35"
		self.search_list_show["height"] = "30"		
		self.search_list_show.bind('<<ListboxSelect>>',click_search)
		self.search_list_show["selectmode"] = SINGLE

		self.sr_scroll_x = Scrollbar(self)
		self.sr_scroll_x["orient"] = 'horizontal'
		self.sr_scroll_x["command"] = self.search_list_show.xview
		self.search_list_show['xscrollcommand'] = self.sr_scroll_x.set
		self.sr_scroll_x.grid(row=1, column=5,columnspan = 2, sticky='nsew')




		self.btn_download = Button(self)
		self.btn_download["width"] = "10"
		self.btn_download["text"] = "download"
		self.btn_download.grid(row = 2,column = 5,columnspan = 2)
		self.btn_download["command"] = download

		self.song_list = Listbox(self)
		self.song_list.grid(row = 1,column = 3,rowspan = 2,columnspan = 2)
		self.song_list["width"] = "40"
		self.song_list["height"] = "35"
		self.song_list.bind('<<ListboxSelect>>',click_now_playing)
		self.song_list["selectmode"] = SINGLE

		self.so_scroll_y = Scrollbar(self)
		self.so_scroll_y["orient"] = 'vertical'
		self.so_scroll_y["command"] = self.song_list.yview
		self.song_list['yscrollcommand'] = self.so_scroll_y.set
		self.so_scroll_y.grid(row=1, column=4,rowspan = 2, sticky='nse')


		self.so_scroll_x = Scrollbar(self)
		self.so_scroll_x["orient"] = 'horizontal'
		self.so_scroll_x["command"] = self.song_list.xview
		self.song_list['xscrollcommand'] = self.so_scroll_x.set
		self.so_scroll_x.grid(row=2, column=3,columnspan = 2, sticky='nsew')





		self.lyrics = Text(self)
		self.lyrics.insert(1.0,self.mediaPlayer.lyric)
		self.lyrics["width"] = "50"
		self.lyrics["height"] = "40"
		self.lyrics.grid(row=0, column=0,columnspan=3,rowspan = 2)
		self.lyrics["bg"] = "light blue"
		self.lyrics["state"] = "disabled"
		

		self.ly_scroll = Scrollbar(self)
		self.ly_scroll["orient"] = 'vertical'
		self.ly_scroll["command"] = self.lyrics.yview
		self.lyrics['yscrollcommand'] = self.ly_scroll.set
		self.ly_scroll.grid(row=0, column=2,rowspan = 2, sticky='nse')



		self.btn_pre = Button(self)
		self.btn_pre["width"] = "50"
		self.btn_pre["height"] = "50"
		self.photo_pre = ImageTk.PhotoImage(file = "previous.jpg")
		self.btn_pre["image"] = self.photo_pre
		self.btn_pre.grid(row=2, column=0)
		self.btn_pre["command"] = previous #method

		self.btn_play = Button(self)
		self.btn_play["width"] = "50"
		self.btn_play["height"] = "50"
		self.photo_play = ImageTk.PhotoImage(file = "play.jpg")
		self.btn_play["image"] = self.photo_play
		self.btn_play.grid(row=2, column=1)
		self.btn_play["command"] = play_song #method

		self.btn_next = Button(self)
		self.btn_next["width"] = "50"
		self.btn_next["height"] = "50"
		self.photo_next = ImageTk.PhotoImage(file = "next.jpg")
		self.btn_next["image"] = self.photo_next
		self.btn_next.grid(row=2, column=2)
		self.btn_next["command"] = next_song #method



if __name__ == '__main__':
	window = Tk()
	window.resizable(0,0)
	win = GUIDemo(master=window)
	
	win.mainloop()