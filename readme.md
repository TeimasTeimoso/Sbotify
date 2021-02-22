# Sbotify
Simple voice-controlled bot for Spotify.

## Installation
### System Dependencies
+ python3
+ python3-dev
+ mpg123
+ swig
+ libpulse-dev
+ poetry

### Configuring Environment
To configure the _poetry_ virtual env just run _poetry install --no-root_

## Voice Commands
Action | Voice Command 
:----- | :----: 
Next track   | next 
Previous track  | previous
Resume song | continue
Pause song | stop
Play song | play {song}
Play song by artist | play {song} by {artist}
Get song name | currently playing
Inactivate | sleep
Activate | wake up
Play artist top songs | artist {artist}