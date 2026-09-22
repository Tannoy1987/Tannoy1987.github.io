import xbmc, xbmcgui, json

monitor = xbmc.Monitor()
player = xbmc.Player()
home = xbmcgui.Window(10000)

def get_discart():
    tag = player.getMusicInfoTag()
    if not tag:
        return ""
    album = tag.getAlbum()
    artist = tag.getAlbumArtist() or tag.getArtist()
    if not album:
        return ""
    query = {
        "jsonrpc": "2.0",
        "method": "AudioLibrary.GetAlbums",
        "params": {
            "filter": {"and": [
                {"field": "album", "operator": "is", "value": album},
                {"field": "albumartist", "operator": "contains", "value": artist}
            ]},
            "properties": ["art"]
        },
        "id": 1
    }
    result = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    albums = result.get("result", {}).get("albums", [])
    if not albums:
        return ""
    return albums[0].get("art", {}).get("discart", "")

while not monitor.abortRequested():
    if player.isPlayingAudio():
        discart = get_discart()
        xbmc.log("DISCart discart: [{}]".format(discart), xbmc.LOGINFO)
        if discart:
            home.setProperty('discart', discart)
        else:
            home.clearProperty('discart')
    else:
        home.clearProperty('discart')
    monitor.waitForAbort(1)