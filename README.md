# Qobuz Playlist Script

Get all track urls from a given qobuz playlist (public), also able to download using slavartdl

Only supports play.qobuz.com domain and you must have a qobuz account  
Only supports firefox for now, because thats the browser i use :)

## Usage

- Download and install [python3](https://www.python.org/downloads/) and [firefox](https://www.mozilla.org/en-US/firefox/new/)
- Install packages using `pip install -r requirements.txt`
- (Optional) To be able to download the songs you must download [slavartdl](https://github.com/tywil04/slavartdl)
- Rename config.yml.sample to config.yml and configure it
- Run the script `python main.py`

You can find all the collected tracks urls in the output/tracks.txt file  
Some tracks might fail to download due to geo restrictions or other issues on qobuz/slavart end
