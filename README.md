# Prerequisites
* Any Linux distro that supports the rest of the prerequisites
* Python 3.14 with virtualenv support
* A Discogs personal access token, obtainable [here](https://www.discogs.com/settings/developers)
# Installation
Clone and enter directory:
```sh
git clone git@github.com:mechanikate/radiofreekerbot.git
cd radiofreekerbot
```
Copy `token.sh.example` over to `token.sh`:
```sh 
cp token.sh.example token.sh 
```
Edit `token.sh` and replace with your Discogs perosnal access token:
```sh
export DISCOGS_USETOKEN=yourTokenHere
```
Run the `start.sh` script (`chmod` if needed too). It will automatically install dependencies via `pip` in a virtualenv:
```sh
chmod +x start.sh 
./start.sh
```
Finally, browse to [localhost:8080](http://localhost:8080/).

# Usage
## User interface
WIP
## Connecting to Streamer.bot 
You can use Fetch URL to set the "Currently Playing" as a variable via `http://localhost:8080/playing`, with reading as JSON enabled.

