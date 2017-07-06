# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests,sys
import youtube_dl
import vlc
import time
import threading

class MediaPlayer():
  def __init__(self):
    self.lyric = ""
    self.search_list = []
    self.play_list = []
    self.play_target = 0
    self.vlc_p = 0
    self.vlc_listen = 0
    self.listenLock = threading.Lock()
    self.playLock = threading.Lock()
    self.downloadLock = threading.Lock()
    self.download_cnt = 0
  def play(self):
      self.listenLock.acquire()
      if self.vlc_listen != 0 and self.vlc_listen.get_state() == vlc.State.Playing:
        self.vlc_listen.pause()
      #while self.play_target != len(self.play_list):
      if self.vlc_p == 0 or self.vlc_p.get_state() == vlc.State.Ended:
        self.vlc_p = vlc.MediaPlayer(self.play_list[self.play_target])
        self.vlc_p.play()
        while self.vlc_p.get_state() == vlc.State.Opening:
          pass
        duration = self.vlc_p.get_length() / 1000
        mm, ss = divmod(duration, 60)
        print "Length:", "%02d:%02d" % (mm,ss)
        # self.play_target += 1
      else:
        self.vlc_p.pause()
      # while self.vlc_p.get_state() != vlc.State.Ended:
      #   pass
      
      #break
      self.listenLock.release()
  def previous_or_next_song(self):
      self.listenLock.acquire()
      if self.vlc_listen != 0 and self.vlc_listen.get_state() == vlc.State.Playing:
        self.vlc_listen.pause()
      self.listenLock.release()
      self.playLock.acquire()
      if self.vlc_p != 0 and self.vlc_p.get_state() != vlc.State.Paused:
        self.vlc_p.pause()
      self.vlc_p = vlc.MediaPlayer(self.play_list[self.play_target])
      self.vlc_p.play()
      while self.vlc_p.get_state() == vlc.State.Opening:
        pass
      duration = self.vlc_p.get_length() / 1000
      mm, ss = divmod(duration, 60)
      print "Length:", "%02d:%02d" % (mm,ss)
      self.playLock.release()
  def load_lyric(self, song_name):
    song_name = song_name.split('/')[-1]
    song_name = song_name.split('.')[0]
    print(song_name)
    res = requests.get("http://www.kkbox.com/tw/tc/search.php?search=mix&word="+song_name)
    soup = BeautifulSoup(res.text)
    try:
        link = soup.select(".song-title")[0]['href']

        res = requests.get("http://www.kkbox.com/"+link)
        soup = BeautifulSoup(res.text)
        self.lyric = soup.select(".lyrics.col-md-12")[0].text.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding).strip()
    except:
      self.lyric = "這首歌目前沒有歌詞"
    

  def search_song(self,search_query):
      self.download_cnt = 0
      self.search_list = []
      print search_query
      res = requests.get("https://www.youtube.com/results?search_query="+search_query)
      soup = BeautifulSoup(res.text)
      query_list = soup.select(".item-section > li")

      for item in query_list:
        try:
          song_dict = {
            'song':item.select('.yt-lockup-title > a')[0]['title'],
            'length':item.select('.yt-thumb-simple')[0].text.strip(),
            # 'poster':item.select('.yt-lockup-byline')[0].text,
            'post_time':item.select('.yt-lockup-meta')[0].text,
            'link':"http://www.youtube.com"+item.select('.yt-lockup-title > a')[0]['href']
          }
          self.search_list.append(song_dict) 
        except:
          pass

  def listen_song(self,addr):
    self.listenLock.acquire()
    if self.vlc_p != 0 and self.vlc_p.get_state() == vlc.State.Playing:
        self.vlc_p.pause()
    if self.vlc_listen != 0 and self.vlc_listen.get_state() == vlc.State.Playing:
        self.vlc_listen.pause()
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    with ydl:
        result = ydl.extract_info(
            addr,
            download=False # We just want to extract the info
        )

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result
    for format in video['formats']:
      if format['ext'] == 'm4a':
        audio_url = format['url']

    self.vlc_listen = vlc.MediaPlayer(audio_url)
    print self.vlc_listen.get_state()
    self.vlc_listen.play()

    time.sleep(1)
    while self.vlc_listen.get_state() == vlc.State.Opening:
        pass
    print self.vlc_listen.get_length()
    duration = self.vlc_listen.get_length() / 2000
    mm, ss = divmod(duration, 60)
    print "Length:", "%02d:%02d" % (mm,ss)
    self.listenLock.release()

    # while self.vlc_listen.get_state() != vlc.State.Ended:
    #     pass
  def download_song(self,song_name,addr):
    self.downloadLock.acquire()
    if self.download_cnt != 0:
      song_name += "_" + str(self.download_cnt)
    ydl_opts = {
        'verbose': True,
          'format': '140/best', # 140 means 'm4a' format
          'outtmpl': song_name + '.%(ext)s', # set output file name
          'noplaylist': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    	ydl.download([addr])
    self.download_cnt += 1
    self.downloadLock.release()
