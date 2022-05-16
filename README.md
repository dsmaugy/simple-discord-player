# simple-discord-player
Simple media player bot for Discord.

This was created as an alternative for me and my friends to listen to music together on Discord after the [takedown of multiple YouTube-based Discord bots](https://www.nme.com/news/gaming-news/discord-music-bot-rythm-follows-groovy-into-the-void-after-cease-and-desist-3045407).

The bot plays audio from YouTube, has a queueing system, a permission system, and has volume controls.

Supported commands:
```
# Permission Controls
-ban, -ban | <@user>           
-unban, -ub | <@user>

# Connection Commands
-join, -j
-disconnect, -dc

# Media Controls
-pause
-resume, -r
-stop
-queue, -q
-now_playing, -np
-skip, -s
-play, -p | <query> | <youtube_url> | <soundcloud_url>
-volume, -v | <[0.0, 2.0]>

# Debugging
-status
```