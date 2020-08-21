# BAMP, BossAlien Media Player

A mopidy-based server that allows to play music from a public playlist. Democracy for music.

Requires Docker, PulseAudio and a Premium Spotify subscription.

BAMP has only been tested on MacOS, but there is no reason to think that it won’t work on other *NIX platforms, or Windows.

## Goals

BAMP is an easy to run solution to play music in a shared space, that allows its members to suggest their own music with rules that allow fair distribution of songs for everyone.

BAMP assumes that you have a server to which you can plug in speakers, how you set up your speakers is outside the scope of the project. It also streams to an Icecast server, which you can use to listen to BAMP at your place. BAMP runs on Docker, so the only dependency with the host machine is Docker and Pulseaudio.

## Install

Installation instructions follow, see INSTALL.md for troubleshooting and further information.

### MacOS

* Requires [Homebrew](https://brew.sh/) installed
* Install docker \
`brew cask install docker` \
`brew install docker-compose`
* Install pulseaudio `brew install pulseaudio`
* Edit `/usr/local/Cellar/pulseaudio/12.2/etc/pulse/default.pa`, uncomment the following lines: \
`load-module module-esound-protocol-tcp` \
`load-module module-native-protocol-tcp`
* If you can't find the previous file, check pulseaudio version (12.2), and change accordingly
* Restart pulseaudio server `brew services restart pulseaudio`
* Make sure you have a file in `~/.config/pulse/cookie`, this will be mounted into the container
* Copy docker/mopidy.conf.secrets.example to docker/mopidy.conf.secrets, and replace all the relevant lines
with real data. Check out the Secret Handling section below to see how to handle secrets

## Usage

### MacOS

* Development: Run `start_bamp.sh`. The script will use your computer IP, but if there is more than one, it will return and tell you to pass the IP you want as a command line argument. We suggest you use the first one it appears. This version runs on `http://localhost:6680`.
* Production: Run `start_bamp_prod.sh`. The script will use your computer IP, but if there is more than one, it will return and tell you to pass the IP you want as a command line argument. We suggest you use the first one it appears. Check in this script that `SERVER_NAME` is set to the correct domain the production server will have. This version runs on `https://yourdomain`, and should be accessible there. You need to set up ssl certificates.
* Read Backing up data section to know what to back up regularly
* Read SSL Certificates to know where the certificates come from

## Backing up data

Things you should back up in case everything goes down, from the project directory:

* `/database` - contains sqlite database of users and their nicks
* `/letsencrypt` - contains ssl certificates from Let's Encrypt - this and mopidy.conf.secrets should be *securely* backed up. It's important information which should not be checked in to source control.
* `/docker/mopidy.conf.secrets` - keep it safe somewhere in case of data loss

## SSL Certificates

We use SSL certificates from Let's Encrypt, using certbot to automate domain ownership proof. Certificates and
all related to certbot is kept in /letsencrypt/etc and /letsencrypt/varlib.

## Original BAMP Authors

* Alistair Cormack
* Andy Kerridge
* Chris Carr
* Ciro Duran
* Gavin Jones
* Kev Adsett
* Ralph Tittensor
* Robert Lancaster
