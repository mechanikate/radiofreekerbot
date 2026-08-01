function addEnterCallback(qs, callbackFn) { // runs callbackFn if enter is pressed in element(s) in query selector qs
	[...document.querySelectorAll(qs)].forEach(ele => ele.addEventListener("keypress", evt => evt.key === "Enter" && (evt.preventDefault(), callbackFn())));
}
const clickCallbackGenerator = qs => (() => { document.querySelector(qs).click(); });

window.onload = () => {
	addEnterCallback("#queueAddFromString", clickCallbackGenerator("#queueAddFromStringButton"));
	addEnterCallback("#queueSearch", clickCallbackGenerator("#queueSearchButton"));
	updateQueue();
};

function addAlbumToQueue(strAlbum) {
	handleQueueUpdate(fetch("./addSongToQueue", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({string: strAlbum})
	}));
}

const nextAlbum = () => handleQueueUpdate(fetch("./next"));
const previousAlbum = () => handleQueueUpdate(fetch("./previous"));
const saveQueue = () => fetch("./saveQueue");
const loadQueue = () => handleQueueUpdate(fetch("./loadQueue"));
const handleQueueUpdate = (fetchCallback, alreadyJSON = false) => {
	if(alreadyJSON) return fetchCallback.then(r => r.error ? (document.getElementById("errorLog").innerHTML = r.error) : updateQueue()).catch(err => document.getElementById("errorLog").innerHTML = err.message);
	return fetchCallback.then(r => r.json()).then(r => r.error ? (document.getElementById("errorLog").innerHTML = r.error) : updateQueue()).catch(err => document.getElementById("errorLog").innerHTML = err.message);
};

function updateSearchResults(query) {
	handleQueueUpdate(fetch("./searchAlbum", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({query: query})
	}).then(r => r.json()).then(results => { 
		[...document.querySelectorAll(".results-removable-member")].forEach(e => e.remove());
		results.forEach(result => {
			let listEle = document.createElement("li");

			listEle.classList.add("results-removable-member");

			listEle.innerHTML = result;
			
			let addEle = document.createElement("button");

			addEle.innerHTML = "+";
			addEle.style.float = "right";
			addEle.addEventListener("click", () => addAlbumToQueue(result));

			listEle.appendChild(addEle);
			document.getElementById("searchResultContainer").appendChild(listEle);
		});
	}));
}
function updateQueue() {
	fetch("./getQueue").then(e => e.json()).then(dict => {
		let j = dict.queue;
		let nowPlayingIdx = dict.index;
		
		
		if(j.length > 0) document.getElementById("nowPlayingAlbum").innerHTML = j[nowPlayingIdx].now_playing_formatted;
		else document.getElementById("nowPlayingAlbum").innerHTML = "Nothing"; 
		[...document.querySelectorAll(".queue-removable-member")].forEach(e => e.remove());
	
		j.forEach((album, index) => {
			let listEle = document.createElement("li");

			if(index == nowPlayingIdx) listEle.id = "queueNowPlaying";
			listEle.classList.add("queue-removable-member");
				
			listEle.innerHTML = `${album.now_playing_artist || ""}${album.now_playing_artist ? " - " : ""}${album.now_playing_album}`;
			listEle.setAttribute("title", `${album.now_playing_label || ""}${album.now_playing_label ? ", " : ""}${album.now_playing_year || ""}`);

			let removeIndexEle = document.createElement("button");

			removeIndexEle.innerHTML = "x";
			removeIndexEle.style.float = "right";
			removeIndexEle.addEventListener("click", () => {
				fetch("./removeIndex", {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify({index: index-1})
				}).then(r => r.json()).then(r => r.error ? (document.getElementById("errorLog").innerHTML = r.error) : updateQueue()); 
			});

			listEle.appendChild(removeIndexEle);
			document.getElementById("queueDisplayList").appendChild(listEle);

			index++;
		});
	}).catch(err => document.getElementById("errorLog").innerHTML = err.message);
}
