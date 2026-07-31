if [ ! -d ".venv" ]; then
	echo Setting up virtualenv for first start...
	python -m venv .venv
	echo ...virtualenv created! Entering venv...
	source .venv/bin/activate
	echo ...venv entered! Installing requirements...
	pip install -r requirements.txt
	echo ...requirements installed! Getting token from token.sh...
	source ./token.sh
	echo ...token sourced! Running Flask webapp!
	python localsite.py
else
	echo Entering virtualenv...
	source .venv/bin/activate
	echo ...venv entered! Getting token from token.sh...
	source ./token.sh || echo ...token.sh does not exist! Copy the format from token.sh.example and replace the placeholder token with the user token at https://www.discogs.com/settings/developers .
	echo ...token sourced! Running Flask webapp!
	python localsite.py
fi



