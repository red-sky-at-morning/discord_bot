import spotipy
import random

CLIENT_ID = "0fe3f195a2b640d382f11194e3cc6c92"
CLIENT_SECRET = "7e43a1c559b940929488b6c9f7df73bf"

client_credentials_manager = spotipy.SpotifyClientCredentials(client_id=CLIENT_ID, 
client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def playlist_tracks(playlist_link, mode):
    # Black magic to get the urt from the link
    list_uri = playlist_link.split("/")[-1].split("?")[0]
    # Use spotipy to get the playlist
    results = sp.playlist(list_uri)
    # Get the tracks from that
    tracks = results['tracks']['items']

    track_list = []
    
    # Put all the tracks into a list
    for track in tracks:
        track_list.append(track['track']['name'])
    
    match mode:
        case "RANDOM":
            # Return a random item from the track list
            return ([{"type":"message","message":f"{track_list[random.randint(0,len(track_list)-1)]}"}])
        case "LIST":
            # Return as much of the track list as we can, formatted
            f_tracks = f"{track_list}".strip("[']").replace('\'','').replace('"','').replace(", ", "\n")
            return ([{"type":"message","message":f"{f_tracks}"}])