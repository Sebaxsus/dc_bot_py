import spotipy, dotenv, sys, pathlib, os

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/authorize"

sys.path.append(str(pathlib.Path(__file__).parent.parent / "Dev2025/modules"))

DOTENV_PATH = pathlib.Path(__file__).parent / '.env'

dotenv.load_dotenv(DOTENV_PATH)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

#enviromentVariables = dotenv_values("bot_dc_py/src/.env")
spClientId='99d13bd2585a46c8acc7b7c9028dbfbe'
spClientSecret='dc04ddb0ad22464c94a65580f5fdd529'
spApi = "https://api.spotify.com/v1/"
spEndPoint = "/track/{track_id}"
spURI = 'http://localhost:3000'
spUricall = 'http://google.com/callback/'
tokenBot = 'MTExOTg0OTk5MTU2NjAwODM0MA.GqbZY1.E9htEvIOG-FKE2BD36nT2RBP6NT4H2YfYL8bXc'

scope = """ugc-image-upload,user-read-playback-state,user-modify-playback-state,user-read-currently-playing,
app-remote-control,streaming,playlist-read-private,playlist-modify-public,playlist-read-collaborative,user-read-email,user-read-private
"""

auth_manager = spotipy.oauth2.SpotifyPKCE(client_id=spClientId,redirect_uri=spUricall,scope=scope)
#auth_manager = spotipy.oauth2.SpotifyClientCredentials(client_id=spClientId, client_secret=spClientSecret)
token = auth_manager.get_access_token()
#token = token_dict['access_token']
#cliente = spotipy.Spotify(auth_manager=auth_manager)

try:
    #print(token)
    cliente = spotipy.Spotify(auth=token)
    user_name = cliente.current_user() 
except:
    print("Fallo token")
else:
    #print(json.dumps(user_name, sort_keys=True, indent=4))
    #print(f'token: {token}')
    print('token correcto')

album_data = cliente.album("https://open.spotify.com/intl-es/album/3CCnGldVQ90c26aFATC1PW")

def recorrer_album():
    for i, item in enumerate(album_data):
        print(f"Album item {i}: {item}")


def recorrer_album_tracks_atrib(album):
    # Recorrre los primero atribs
    for i, item in enumerate(album_data['tracks']):
        # print(f"Album track {i}, tracksAtribs: {item}, \ntrackAtribData: {album_data["tracks"][item]}")
        print(f"Album track {i}, tracksAtribs: {item},")

def recorrer_tracks_album(album):
    for i, item in enumerate(album_data['tracks']['items']):
        # print(f"Track {i}, data: {item}")
        print(f"Track artis {len(item['artists'])}, Track Name: {item['name']}")

playlist_data = cliente.playlist('https://open.spotify.com/playlist/4TpkY9l53Zz7kZmvgn7sbo')

def recorrer_playlist(playlist):

    for i, item in enumerate(playlist):
        print(f"Playlist Atrib {i}, {item} ")
        # if item == "owner":
        #     print(f"{playlist_data.get("name")} - {playlist_data.get("owner").get("display_name")}")

def recorrer_tracks_playlist(playlist):
    for i, item in enumerate(playlist['tracks']['items']):  
        print(f"TrackItem {i}")    
        # for i in item:
        #     print(f"\t{i}: {item[i]}")
        if i == 61:
            print("Depurando posible error Artist:", playlist['tracks']['items'][61])
        else:
            print(f"PlaylisTrack artis {len(item['track']['artists'])}, Track Name: {item['track']['name']}, Track Artist: {item['track']['artists']}")

pl_tracks = cliente.playlist_tracks("https://open.spotify.com/playlist/5dFb8AnJIbi6dUMSiN8gws")
pl_data = cliente.playlist_items("https://open.spotify.com/playlist/5dFb8AnJIbi6dUMSiN8gws")
# for i, item in enumerate(pl_tracks):
#     # print(f"Track {i} {item}: {pl_tracks[item]}")
#     print(f"Track {i}: {item}")

# for i, item in enumerate(pl_data):
#     print(f"Item {i}: {item}")
#     if item == "items":
#         # print(f"name: {pl_data[item][0].get("track").get("name")}")
#         for a, trackAtr in enumerate(pl_data[item]):
#             print(f"Track {a}")
#             for j in pl_data[item][a]:
#                 if j == "track":
#                     for c in pl_data[item][a][j]:
#                         if c == "available_markets":
#                             print("available_markets")
#                         else:
#                             print(f"\t\ttrack atrib: {c}: {pl_data[item][a][j][c]}")
#                 else:
#                     print(f"\t{j}: {pl_data[item][a][j]}")

print(album_data.get("name"))