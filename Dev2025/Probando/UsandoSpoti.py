import spotipy

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/authorize"

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

album_data = cliente.album("3CCnGldVQ90c26aFATC1PW")

## Recorrre los primero atribs
# for i, item in enumerate(album_data['tracks']):
#     print(f"Album track {i}, tracksAtribs: {item}, \ntrackAtribData: {album_data["tracks"][item]}")

# for i, item in enumerate(album_data['tracks']['items']):
#     # print(f"Track {i}, data: {item}")
#     print(f"Track artis {len(item['artists'])}, Track Name: {item['name']}")

playlist_data = cliente.playlist('https://open.spotify.com/playlist/4TpkY9l53Zz7kZmvgn7sbo')

for i, item in enumerate(playlist_data['tracks']['items']):
    print(f"TrackItem {i}")
    # for i in item:
    #     print(f"\t{i}: {item[i]}")
    if i == 61:
        print("Depurando posible error Artist:", playlist_data['tracks']['items'][61])
    else:
        print(f"PlaylisTrack artis {len(item['track']['artists'])}, Track Name: {item['track']['name']}, Track Artist: {item['track']['artists']}")