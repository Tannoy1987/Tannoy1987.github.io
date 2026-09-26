import xbmc, xbmcgui, json

home = xbmcgui.Window(10000)
monitor = xbmc.Monitor()

# Patch #5: clear any leftover discart from a previous (possibly crashed) session
home.clearProperty("discart")


def rpc(method, params):
    query = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    try:
        result = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        if "error" in result:
            xbmc.log("DISCart RPC error: {}".format(result["error"]), xbmc.LOGWARNING)
            return {}
        return result.get("result", {})
    except Exception as e:
        xbmc.log("DISCart RPC exception: {}".format(e), xbmc.LOGERROR)
        return {}


def normalize_artist(a):
    if isinstance(a, (list, tuple)):
        return a[0] if a else ""
    return a or ""


def get_discart(player):
    tag = player.getMusicInfoTag()
    if not tag:
        return ""

    songid = tag.getDbId()
    if songid and songid > 0:
        song = rpc("AudioLibrary.GetSongDetails",
                   {"songid": songid, "properties": ["albumid"]})
        albumid = song.get("songdetails", {}).get("albumid")
        if albumid:
            alb = rpc("AudioLibrary.GetAlbumDetails",
                      {"albumid": albumid, "properties": ["art"]})
            discart = alb.get("albumdetails", {}).get("art", {}).get("discart", "")
            if discart:
                return discart

    album = tag.getAlbum()
    artist = normalize_artist(tag.getAlbumArtist() or tag.getArtist())
    if not album or not artist:
        return ""

    res = rpc("AudioLibrary.GetAlbums", {
        "filter": {"and": [
            {"field": "album", "operator": "is", "value": album},
            {"field": "albumartist", "operator": "contains", "value": artist}
        ]},
        "properties": ["art"]
    })
    albums = res.get("albums", [])
    return albums[0].get("art", {}).get("discart", "") if albums else ""


class DiscArtPlayer(xbmc.Player):
    def onAVStarted(self):
        if self.isPlayingAudio():
            discart = get_discart(self)
            xbmc.log("DISCart discart: [{}]".format(discart), xbmc.LOGDEBUG)
            if discart:
                home.setProperty("discart", discart)
            else:
                home.clearProperty("discart")

    def onPlayBackStopped(self):
        home.clearProperty("discart")

    def onPlayBackEnded(self):
        home.clearProperty("discart")


player = DiscArtPlayer()
monitor.waitForAbort()

# Optional: clear on service shutdown for a tidy exit
home.clearProperty("discart")