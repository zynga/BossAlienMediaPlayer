# Installation notes

## MacOS troubleshooting

* If you have no cookie file in `~/.config/pulse/cookie`, check daemon is running with `pulseaudio --check -v`
* If it says that the daemon is not running, run pulseaudio daemon with the following command:
`pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon`
* `pulseaudio --check -v` should now say the daemon is running and its PID
* Further troubleshooting: adding `command: gst-launch-1.0 audiotestsrc ! audioresample ! autoaudiosink`
under the `ports:` item in `bamp:` in `docker-compose-base.yml` and running `start_bamp.sh` should
play a constant sine wave instead of running mopidy. If you can't hear this sound, mopidy won't output
sound either. Remove this line once you're finished. You should get some logs like the following when
running this command: \
`bamp_1  | Setting pipeline to PAUSED ...` \
`bamp_1  | Pipeline is PREROLLING ...` \
`bamp_1  | Redistribute latency...` \
`bamp_1  | Pipeline is PREROLLED ...` \
`bamp_1  | Setting pipeline to PLAYING ...` \
`bamp_1  | New clock: GstPulseSinkClock`

## Secret Handling

* We do not check in sensitive information into our repo (e.g. passwords, API secret keys, etc.),
so secrets are written to the file `docker/mopidy.conf.secrets`. Each line contains a secret,
each line has two columns, a secret name, and a secret value, separated by a space. Copy `docker/mopidy.conf.secrets.example` to `docker/modipy.conf.secrets` to have a starting point for this file.
* In the secrets example you can see a few values that need random strings to work. Use a page like random.org to generate these strings.
* `docker/modipy.conf.secrets` has been gitignored, you should keep out these values out of the version control.
* `docker/mopidy.conf` has been gitignored too, do not check in this file.
* Spotify client ID and secret can be obtained from https://www.mopidy.com/authenticate/#spotify

## "Position query failed"

Sometimes the streaming with mopidy can fail, in such case you might get an error like this:

```
bamp          	| INFO 	2023-11-06 11:20:49,979 [7:HttpServer] mopidy_bamp
bamp          	|   Track spotify:track:1eeRBdZ22KoULKkPmLK5Kc in queue metadata but not mopidy, removing
bamp          	| thread '<unnamed>' panicked at audio/spotify/src/spotifyaudiosrc/imp.rs:250:37:
bamp          	| called `Result::unwrap()` on an `Err` value: RecvError
bamp          	| note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
bamp          	| ERROR	2023-11-06 11:24:52,547 [7:MainThread] mopidy.audio.gst
bamp          	|   GStreamer error: Panicked: called `Result::unwrap()` on an `Err` value: RecvError
bamp          	| DEBUG	2023-11-06 11:24:52,547 [7:MainThread] mopidy.audio.gst
bamp          	|   Got ERROR bus message: error=GLib.Error('Panicked: called `Result::unwrap()` on an `Err` value: RecvError', 'gst-library-error-quark', 1) debug=None
bamp          	| DEBUG	2023-11-06 11:24:52,552 [7:MainThread] mopidy.audio.gst
bamp          	|   Changing state to GST_STATE_NULL: result=GST_STATE_CHANGE_SUCCESS
bamp          	| DEBUG	2023-11-06 11:24:53,224 [7:Audio-3] mopidy.audio.actor
bamp          	|   Position query failed
```

And the position query failed will be spammed in logs constantly, and you will not get more sound.

Due to how BAMP works, there are no API calls that could unblock this situation. For this case, we have enabled `mopidy-mpd` in localhost within the container. This allows you to run an mpd client inside the container and unblock BAMP.

Open a shell inside the bamp container, and run `ncmpcpp`. Then press down and up to select the first song of the playlist, and then press `delete` to delete the first song from the playlist. This will prompt BAMP to play the next song and (maybe) continue as usual (if the problem was transient, the API might just be down at some point). Do not try to re-play the song as BAMP will read the events from the playlist changing and remove the first song from the playlist and become inconsistent with the voting queue.

## Sources

* https://stackoverflow.com/questions/40136606/how-to-expose-audio-from-docker-container-to-a-mac 
* https://github.com/wernight/docker-mopidy
* https://github.com/TheBiggerGuy/docker-pulseaudio-example
* https://certbot.eff.org/docs/using.html#dns-plugins
* https://certbot-dns-route53.readthedocs.io/en/stable/
* https://certbot.eff.org/docs/using.html#re-creating-and-updating-existing-certificates
