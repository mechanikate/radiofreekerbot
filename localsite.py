import discogs_client, json, os, sys
from parse import * # inverse of format/fstrings for parsing old format

from flask import Flask, jsonify, render_template, request # local webapp stuff
app = Flask(__name__)

discogs = discogs_client.Client("RFKBot/0.1", user_token=os.environ["DISCOGS_USERTOKEN"])


class Album:
    def __init__(self, artist, album, label, year):
        self.artist = artist
        self.album = album
        self.label = label
        self.year = str(year)
    
    def __str__(self): # str(album: Album) returns formatted string (that works with Album.from_string by the way)
        if None in [self.artist, self.label, self.year]:
            return self.album if self.album else ""
        return f"{self.artist} - {self.album} [{self.label}, {self.year}]"
    def as_full_str(self):
        return str(self)
    def as_brief_str(self):
        if not self.artist:
            return self.album
        return f"{self.artist} - {self.album}"
    def as_only_attributes_str(self):
        if not self.label and not self.year:
            return ""
        return f"{self.label}, {self.year}"
    def as_context(self):
        return {
            "now_playing_artist": self.artist,
            "now_playing_album": self.album,
            "now_playing_label": self.label,
            "now_playing_year": self.year,
            "now_playing_formatted": str(self),
            "now_playing_formatted_brief": self.as_brief_str(),
            "now_playing_formatted_attributes": self.as_only_attributes_str()
        }
    @staticmethod
    def from_string(formatted_string):
        try:
            parts_dict = search("{artist} - {album} [{label}, {year}]", formatted_string).named # get dict in format of curly brace'd placeholders mapped to matching strs
        except:
            return Album.from_raw_string(formatted_string)
        return Album(parts_dict["artist"], parts_dict["album"], parts_dict["label"], parts_dict["year"])
    @staticmethod
    def from_raw_string(raw_string):
        return Album(None, raw_string, None, None)

now_playing_album = None
current_album_ptr = 0
queue = []

@app.route("/")
def main_site():
    return render_template("index.html", queue=queue, current=current_album_ptr, **(now_playing_album.as_context() if now_playing_album else {}))

@app.route("/addSongToQueue", methods=["POST"])
def add_song_endpoint():
    if not request.is_json:
        return jsonify({"error": "expected json with formatted 'string' key or separate keys for artist, album, label, and year"}), 415 # 415 = unsupported media type
    data = request.get_json()
    as_string = data.get("string")
    if as_string:
        queue.append(Album.from_string(as_string))
        return jsonify({"result": f"added song successfully at position {len(queue)}"}), 201
    return jsonify({"error": "something has gone terribly wrong"}), 400

@app.route("/getQueue", methods=["GET"])
def get_queue_endpoint():
    return jsonify({
        "queue": [album.as_context() for album in queue],
        "index": current_album_ptr
    })

@app.route("/next", methods=["GET","POST"])
def next_album_endpoint():
    global current_album_ptr
    if(current_album_ptr+1 >= len(queue)):
        return jsonify({"error": "out of queued albums"})
    current_album_ptr += 1
    return jsonify({"result": f"success, onto queue #{current_album_ptr+1}"})
    
@app.route("/previous", methods=["GET","POST"])
def previous_album_endpoint():
    global current_album_ptr
    if(current_album_ptr <= 0):
        return jsonify({"error": "already at first queued album"})
    current_album_ptr -= 1
    return jsonify({"result": f"success, onto queue #{current_album_ptr+1}"})

@app.route("/currentIndex", methods=["GET"])
def current_index_endpoint():
    return jsonify({"index": current_album_ptr})

@app.route("/playing", methods=["GET"])
def current_playing_endpoint():
    if len(queue) <= 0:
        return jsonify("Nothing"), 400
    return jsonify(str(queue[current_album_ptr]))

@app.route("/removeIndex", methods=["POST"])
def remove_index_endpoint():
    if not request.is_json:
        return jsonify({"error": "expected json with 'index' key"}), 415 # 415 = unsupported media type
    data = request.get_json()
    got_index = data.get("index")
    if isinstance(got_index,int) and got_index >= 0 and got_index < len(queue):
        del queue[got_index]
        return jsonify({"result": f"success, new length of {len(queue)}"})
    return jsonify({"error": "something has gone terribly wrong"}), 400

def save_queue():
    with open("queue.json", "w+") as f:
        json.dump({
            "queue": [str(album) for album in queue],
            "index": current_album_ptr
        }, f)
def load_queue():
    global queue, current_album_ptr
    with open("queue.json", "r") as f:
        data_dict = json.load(f)
        current_album_ptr = data_dict["index"]
        queue = [Album.from_string(album) for album in data_dict["queue"]]
@app.route("/saveQueue", methods=["GET"])
def save_queue_endpoint():
    save_queue()
    return jsonify({"result": "successfully saved queue"})

@app.route("/loadQueue", methods=["GET"])
def load_queue_endpoint():
    load_queue()
    return jsonify({"result": f"success, new queue length is {len(queue)}"})

@app.route("/searchAlbum", methods=["POST"])
def search_album_endpoint():
    if not request.is_json:
        return jsonify({"error": "expected json with 'query' key"}), 415 # 415 = unsupported media type
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "query is blank"}), 4000
    for _ in range(3):
        try:
            return search_album(query)
        except json.JSONDecodeError: 
            continue
        except:
            return jsonify({"error": "discogs or the api wrapper is having issues right now"}), 400
    return jsonify({"error": "discogs or the api wrapper is having issues right now"}), 400
def search_album(query):
    results = discogs.search(query, type="master,release")
    results.per_page = 5
    results_data = []
    for result in results.page(0):
        if hasattr(result, "main_release") and hasattr(result.main_release, "title") and hasattr(result.main_release, "labels") and hasattr(result.main_release, "year") and result.main_release.year != 0:
            results_data.append(str(Album(result.main_release.artists[0].name, result.main_release.title, result.main_release.labels[0].name, result.main_release.year)))
        elif hasattr(result, "title") and hasattr(result, "artists") and hasattr(result, "labels") and hasattr(result, "year"):
            results_data.append(str(Album(result.artists[0].name, result.title, result.labels[0].name, result.year)))
    return jsonify(list(dict.fromkeys(results_data))), 200 
load_queue()
app.run(port=8080)
