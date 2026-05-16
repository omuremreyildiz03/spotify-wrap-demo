import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
from datetime import datetime


#############################################################
# BASE CLASS -> representing a song type:
# 1_ Streamed Song     in  Streaming History
# 2_ Saved Song        in  Playlist
#############################################################
class SongType:

  def __init__(self, title, artist):
    """
    Parameters:
        title (str): The title of the song.
        artist (str): The artist of the song.
    """
    self.title = title
    self.artist = artist

  def getTitle(self):
    return self.title

  def getArtist(self):
    return self.artist



#############################################################
# Inherits from SongType. Represents a streamed song.
#############################################################
class StreamedSong(SongType):

  def __init__(self, title, artist, duration, end_time):
    """
    Parameters:
        title (str): Song title.
        artist (str): Artist name.
        duration (int): Duration played in milliseconds.
        end_time (datetime): Timestamp when the stream ended.
    """
    super().__init__(title, artist)
    self.duration = duration
    self.end_time = end_time


  def __str__(self):
     return f"TITLE: {self.title}, ARTIST: {self.artist}, DURATION: {self.duration}"
  
  def getDuration(self):
     return self.duration
  
  def getEndTime(self):
     return self.end_time




#############################################################
# Inherits from SongType. Represents a saved song in a playlist.
#############################################################
class SavedSong(SongType):

  def __init__(self, title, artist, added_date):
    """
    Parameters:
        title (str): Song title.
        artist (str): Artist name.
        added_date (datetime): Date when song was added to playlist.
    """
    super().__init__(title, artist)
    self.added_date = added_date





#############################################################
# Represents a playlist object with songs and metadata.
#############################################################
class Playlist:

  def __init__(self, name, last_modified, description):
    """
    Parameters:
        name (str): Playlist name.
        last_modified (str): Last modified date as string.
        description (str): Playlist description.
    """
    self.name = name
    self.last_modified = last_modified
    self.description = description
    self.songs = []   # Playlist is a list, so keep them into a list object

  def add_song(self, song):
    self.songs.append(song) 

  def total_songs(self): 
    return len(self.songs)
  
  def getSongs(self):
     return self.songs
  
  def getPlaylistName(self):
     return self.name





#############################################################
# Represents a Spotify user, contains their data.
# All stream history and playlist belong to this user.
#############################################################
class SpotifyUser:

  def __init__(self, user_name):
    """
    Parameters:
        user_name (str): Spotify username.
    """
    self.user_name = user_name
    self.playlists = [] # list for playlists
    self.streamingHistory = [] # list for streamed songs
    
  def add_playlist(self, playlist): # add whole playlist to library
    self.playlists.append(playlist)

  def add_streamed_song(self, streamed_song):
    self.streamingHistory.append(streamed_song)

  def getStreamHist(self):
     return self.streamingHistory
  
  def getPlaylists(self):
     return self.playlists





#############################################################
# Loads JSON data for playlists and streaming history.
#############################################################
class DataLoader:

  def __init__(self, user):
    """
    Parameters:
        user (SpotifyUser): The Spotify user to load data into.
    """
    self.user = user



  def load_streaming_history(self, path):
    """
    Loads streaming history from JSON file.

    Parameters:
        path (str): Path to the streaming history JSON file.
    """
    with open(path, "r", encoding="utf-8") as filename:
        data = json.load(filename)
        if not data:
            print("Warning: playlists.json is empty.")
            return
    
    for event in data:
        title = event["master_metadata_track_name"]
        artist = event["master_metadata_album_artist_name"]
        duration = event["ms_played"]
        endTime = event["ts"]
        end_time = datetime.strptime(endTime, "%Y-%m-%dT%H:%M:%SZ") # end_time is converted datetime obj

        streamed_song = StreamedSong(title, artist, duration, end_time) # creat StreamedSong obj for each song

        self.user.add_streamed_song(streamed_song) # created StreamSong is added streaming history



  def load_playlists(self, path):
    """
    Loads playlist data from JSON file.

    Parameters:
        path (str): Path to the playlist JSON file.
    """
    with open(path, "r", encoding="utf-8") as filename:
        data = json.load(filename)
        if not data:
            print("Warning: playlists.json is empty.")
            return

    for playlist in data["playlists"]:
        name = playlist["name"]
        last_modified = playlist["lastModifiedDate"]
        description = playlist["description"]
        
        modified_pl = Playlist(name,last_modified,description) # create new Playlist obj for each playlist
      
        for item in playlist["items"]: 
            if item["track"] is not None: # choose songs with provided track
                title = item["track"]["trackName"]
                artist = item["track"]["artistName"]
                dateStr = item["addedDate"] # date conversion is needed
                added_date = datetime.strptime(dateStr, "%Y-%m-%d")

                saved_song = SavedSong(title, artist, added_date) # create SavedSong for each song saved in a playlist
                modified_pl.add_song(saved_song) # add SavedSong in playlist 
    
        self.user.add_playlist(modified_pl) # add modified playlist into Playlists list
    






#############################################################
# FOUR MAIN FUNCTIONS TO ANALYZE
#
# Contains analysis functions on user's data (functions in menu):
# 1. Print the total listening time for an artist with the top 5 songs
# 2. Print the top listened N artists by total listening time
# 3. Print the top listened N tracks by play count between the given dates
# 4. Print playlists containing the given artist
# 0. Exit (no function)
#############################################################
class SpotifyAnalyzer:

  def __init__(self, user): # user is SpotifyUser object
    """
    Parameters:
        user (SpotifyUser): The Spotify user to analyze.
    """
    self.user = user




  #############################################################
  # 1. Print the total listening time for an artist with the top 5 songs
  #############################################################
  def print_listening_time_for_artist(self, artist_name):
    """
    Parameters:
        artist_name (str): Name of artist to analyze.
    """
    total_duration = 0
    d = {}
    found = False
    streamLst = self.user.getStreamHist()
    for elm in streamLst:
      title = elm.getTitle()
      artist = elm.getArtist()
      if title is None or artist is None:
        continue

      if (artist.title() == artist_name.title()):
        found = True
        total_duration += elm.getDuration()
        
        if title in d:
           d[title] += 1
        else:
           d[title] = 1
        

 
    hour = total_duration // 3600000 # conversion from ms into hour min and sec
    minute = (total_duration % 3600000) // 60000
    sec = (total_duration // 1000) - hour*3600 - minute*60

    print(f"{artist_name} : {hour} hours {minute} minutes {sec} seconds")

    # sort artists in descending order of duration and in alphabetical order of song name
    sorted_song = sorted(d.items(), key=lambda item: (-item[1], item[0]), reverse=False)

    count = len(sorted_song)
    if count > 5:
       count = 5 # maximum 5 songs - first 5 songs

    for song_name, count_play in sorted_song[:count]:
      print(f"{song_name} : {count_play} plays")

    if not found:
       print(f"No listening history found for {artist_name}")


    # Barplot visualization of data
    if count > 0:
        df = pd.DataFrame(sorted_song[:count], columns=["Song", "Play Count"])
        sns.barplot(data=df, x="Song", y="Play Count", palette="viridis")
        plt.title(f"Top {count} Songs by {artist_name}")
        plt.xlabel("Play Count")
        plt.ylabel("Song Name")
        plt.tight_layout()
        plt.show()







  #############################################################
  # 2. Print the top listened N artists by total listening time
  #############################################################
  def print_top_n_artists_by_time(self, n):
    """
    Parameters:
        n (int): Number of top artists to display.
    """
    artist_dict = {}
    streamLst = self.user.getStreamHist() # Get streaming history of SpotifyUser
    for elm in streamLst:
      artist = elm.getArtist()
      duration = elm.getDuration()

      if artist is None or duration is None:
         continue # if no provided artist or duration, pass that item

      artist = artist.title() # to write down with specific format
      if artist in artist_dict:
          artist_dict[artist] += duration
      else:
          artist_dict[artist] = duration
        
    # sort artists in descending order of duration and in alphabetical order of artist name
    sorted_artists = sorted(artist_dict.items(), key=lambda item: (-item[1], item[0]), reverse=False)

    for artist_name, total_time in sorted_artists[:n]: # print N artist and their durations
      minutes = total_time / 60000
      print(f"{artist_name} : {minutes:.2f} mins")
    

    # Barplot visualization of data
    top_artists = sorted_artists[:n]
    df = pd.DataFrame(top_artists, columns=["Artist", "Duration(ms)"])
    df["Duration(min)"] = df["Duration(ms)"] / 60000
    sns.barplot(data=df, x="Duration(min)", y="Artist", palette="Set1")
    plt.title(f"Top {n} Artists by Listening Time")
    plt.xlabel("Listening Time (minutes)")
    plt.ylabel("Artist")
    plt.tight_layout()
    plt.show()








  #############################################################
  # 3. Print the top listened N tracks by play count between the given dates
  #############################################################
  def print_top_n_songs_by_count_between_dates(self, n, start_date, end_date):
    """
    Parameters:
        n (int): Number of top songs to display.
        start_date (datetime): Start of date range.
        end_date (datetime): End of date range.
    """
    song_dict = {}
    streamLst = self.user.getStreamHist()
    check = False # no song in provided interval
    for elm in streamLst:
      title = elm.getTitle()
      end_time = elm.getEndTime()
      
      if title is None or end_time is None:
         continue
      
      title = title.title() # print out with specific format

      if (start_date <= end_time <= end_date): # if end_time is in interval of given times
        check = True # if at least one song in inteval
        if title in song_dict:
            song_dict[title] += 1
        else:
            song_dict[title] = 1
        
    # sort artists in descending order of playing count and in alphabetical order of song name
    sorted_songs = sorted(song_dict.items(), key=lambda item: (-item[1], item[0]), reverse=False)

    if n > len(sorted_songs): # if there is less song then n
       n = len(sorted_songs)

    for title, count in sorted_songs[:n]:
      print(f"{title} : {count} plays")

    if not check: # if there is no song
       print("No songs found in that range.")


    # pie chart visualization of data
    if check:
      top_songs = sorted_songs[:n]
      df = pd.DataFrame(top_songs, columns=["Song", "Plays"])

      # Create the pie chart
      plt.figure(figsize=(7, 7))
      plt.pie(
          df["Plays"],
          labels=df["Song"],
          autopct=lambda p: f'{p:.1f}%\n({int(p*df["Plays"].sum()/100)} plays)',
          startangle=140,
          colors=sns.color_palette("Set3")
      )
      plt.title(f"Top {n} Songs\n{start_date.date()} to {end_date.date()}", fontsize=12)
      plt.axis("equal")  # Keep it a circle
      plt.tight_layout()
      plt.show()




     


     

  #############################################################
  # 4. Print playlists containing the given artist
  #############################################################
  def print_playlists_containing_artist(self, artist_name):
    generalFound = False
    playlists = self.user.getPlaylists()
    for elm in playlists:
      found = False
      playlistName = elm.getPlaylistName()
      songLst = elm.getSongs()
      for song in songLst:
        songArtist = song.getArtist().title()
        if songArtist == artist_name.title():
          found = True
          generalFound = True
          break
      if found:
        print(playlistName)

    if not generalFound:
      print(f"None of the playlists contains songs from {artist_name}.")
  
  # no visualization for that function
       




#############################################################
# main function
#############################################################
def main():
  user_name = input("Enter your Spotify user name: ")
  user = SpotifyUser(user_name)

  loader = DataLoader(user)
  loader.load_playlists("playlists.json")
  loader.load_streaming_history("Streaming_History_Audio_2021-2023_0.json")
  loader.load_streaming_history("Streaming_History_Audio_2023-2024_1.json")
  loader.load_streaming_history("Streaming_History_Audio_2024-2025_2.json")
  loader.load_streaming_history("Streaming_History_Audio_2025_3.json")
  loader.load_streaming_history("Streaming_History_Video_2024-2025.json")


  analyzer = SpotifyAnalyzer(user)


  menu = """
  1. Print the total listening time for an artist with the top 5 songs
  2. Print the top listened N artists by total listening time
  3. Print the top listened N tracks by play count between the given dates
  4. Print playlists containing the given artist
  0. Exit
  """


  while True:
    print()
    print(user_name.capitalize(), "welcome to the Spotify Analyzer: ")
    print(menu)
    choice = input("Your choice: ").strip()

    if choice == "0":
      print("Goodbye!")
      break

    elif choice == "1":
      artist = input("Artist name: ").title()
      analyzer.print_listening_time_for_artist(artist)

    elif choice == "2":
      n = int(input("N: "))
      analyzer.print_top_n_artists_by_time(n)

    elif choice == "3":
      n = int(input("N: "))
      start_str = input("Start date (DD.MM.YYYY): ").strip()
      start = datetime.strptime(start_str, "%d.%m.%Y")
      end_str   = input("End   date (DD.MM.YYYY): ").strip()
      end   = datetime.strptime(end_str, "%d.%m.%Y")

      analyzer.print_top_n_songs_by_count_between_dates(n, start, end)

    elif choice == "4":
      artist = input("Artist name: ").title()
      analyzer.print_playlists_containing_artist(artist)

    else:
      print("Invalid choice!")

if __name__ == "__main__":
    main()