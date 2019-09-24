Contributing
============

Thank you for contributing to BAMP, we are really glad that you are interested in helping us shaping BAMP to be useful, nice and fun to use.

This document is a guide on how you can collaborate, and why you might want to. If you have specific questions, please email the BAMP authors.

## What’s BAMP

- BAMP is an easy to run solution to play music in a shared space, that allows its members to suggest their own music with rules that allow fair distribution of songs for everyone.

## What BAMP is Not

- BAMP is not a replacement for services like Jukestar or Festify, in the sense that BAMP aims to play music in one space only. We will not support BAMP for multiple concurrent parties. Multi-party music is not a problem we are interested in solving.

## Why we want your help

If you are a user of BAMP, we would be delighted that you join the conversation and suggest features that would be useful to this web application, or even suggest other uses for it. BAMP is made by folks who love music and love to share music in a physical space.

Programming is not the only necessary skill to collaborate to open source! Good software is the result of good communication. It requires documentation that can be understood by anyone who wants to use the software, an onboarding process that brings the reader up to speed quickly (we hope this document is part of that) and good coordination between parts that may not be physically close.

## How can you collaborate

First and foremost, you can collaborate with BAMP by using it, spotting bugs and suggesting features. You can also fix bugs and implement these features. You can also contribute to the parent project, mopidy, which in turn benefits BAMP.

Mopidy's website is at [https://www.mopidy.com/](https://www.mopidy.com/)

## What is BAMP (again, this time technically)

BAMP is a web application. The project contains a module for [mopidy](https://www.mopidy.com/). Mopidy is a music server written in Python with the [Tornado](https://www.tornadoweb.org/) web framework. BAMP offers http endpoints through which users authenticate, request songs, vote for songs and get the state of the queue. BAMP also serves a one page application written in Angular that uses these endpoints, completing a browser-based interface.

Authentication is available through LDAP, but you could write another way to authenticate that is more suitable to you. Or an anonymous login mode.

BAMP runs on a Docker container, so its dependencies are mostly self contained. However, this means you need to install Docker and Pulseaudio. Mopidy uses gstreamer to output the audio inside the container. Pulseaudio is then used to stream the audio out of the container into the host machine.

## Setting up a developer workflow

Follow the instructions in the README to get BAMP running. Make changes to code, and run BAMP again. There are specific instructions for backend and frontend below. There are no specific preferences for editors in the project. BAMP has the following file structure:

- `/database` - this directory contains the SQLite database that BAMP generates. You can inspect this database with a SQLite database browser. The database is ignored in the version control. This directory gets mounted as a volume in the bamp image.
- `/docker` - contains most necessary files to build Docker images, including the configuration files. The startup scripts take a copy of the `*-base` files to generate the final configuration file. This allows to isolate secrets from the version control.
- `/docker/scripts` - these scripts are not essential to BAMP, there mostly to diagnose problems.
- `/docker/certbot` - files to create the certbot image
- `/frontend` - contains the Angular source code to generate the frontend. The destination of the frontend build is in `/mopidy_bamp/mopidy_bamp/static`.
- `/letsencrypt` - the subdirectories contained here are mounted as volumes in certbot. This allows to easily renew the [Let's Encrypt](https://letsencrypt.org/) certificates.
- `/media` - this directory is mounted as a volume in bamp for local files. It is currently used for the kicked off songs after downvoting.
- `/mopidy_bamp` - where the mopidy module resides.

## Backend development workflow

Most of the times you will be doing changes in `/mopidy_bamp/mopidy_bamp`. Here are some notes to help you navigate in that directory:

- `__init__.py` is where the module gets initialized. You can also add configuration options here (see relevant section below).
- `queue_request_handlers.py` - where the endpoints for getting the queue, requesting a song and voting songs are.
- `search_request_handler.py` - search endpoints here
- `user_request_handlers.py` - update user nickname here
- `is_logged_in_request_handler.py` - to determine whether the user has logged into BAMP
- `login_request_handler.py` - handles authentication
- `playback_handler.py` - handles getting the currently played song, and enabling/disabling playback.
- `history_request_handlers.py` - get the history of songs played, and the votes they carried.
- `base_request_handler.py` - almost all handlers extend BaseRequestHandler, which allow them to easily access the module configuration, and set headers for all endpoints.
- `dtos.py` - Data transfer objects
- `queue_ordering.py` - contains the function that sorts the queue. If you want to improve the ordering algorithm, this is the place.
- `history_service.py` - thread-safe service that holds the history of songs played.
- `playback_service.py` - service in charge of begin playback once there is a song queued.
- `queue_metadata_service.py` - contains the track URI, time of request, and the upvotes/downvotes accumulated for each track in the queue.
- `event_listener_actor.py` - mopidy's playback events are handled here
- `images.py` - locates and sets the images for the tracks
- `database_*.py` - everything related to the database
- `ext.conf` - Configuration default values

### BAMP database

The BAMP database contains some information about the songs requested, songs played and songs kicked off (evicted). This allows to run some basic stats on the data. As of now, the data that BAMP handles is contained in memory. Restarting BAMP will reset the queue and eliminate the history.

The database gets written to `/database`. You can use a SQLite inspector to run queries on the database.

### Adding a configuration option

1. Add the corresponding value in the `get_config_schema` function in `__init__.py`.
2. Add a default value in `ext.conf`
3. If you request handler descends from `BaseRequestHandler`, you can use `self.config['mopidy_bamp']['your_config_key']` to access such value.

## Deploying BAMP

BAMP runs over Docker, and uses docker-compose to run a number of services depending on whether you want to run the service on HTTPS.

`start_bamp.sh` will deploy a BAMP image only on port 6680. It's preferred for development, but if you want to run BAMP on HTTP you can, and it's on you.
`start_bamp_prod.sh` will deploy a BAMP image, an nginx image that proxies port 80 and 443 yo BAMP, and a certbot image that as of now doesn't renew automatically images. See Let's Encrypt documentation on how to generate and renew certificates if you wish to run BAMP on HTTPS. You could also use your own custom certificate if you don't want to use Let's Encrypt.

Mopidy streams audio through gstreamer. Pulseaudio is used to route the audio out of the container and into the host machine.

## Front end development workflow

Changes to the frontend can be made within frontend/BossAlienMediaPlayer/src. The majority of changes you might need to make will be done within the 'app' folder, which contains angular services, and modular components which make up most of BAMPs frontend. These components are composed of a typescript, sass styling, and html file. 

Interactions with the backend should be done via services, such as queue.service.ts, which maintains the currently playing track, and the queue. 

Environment variables for development and production can be found within 'environments'. This contains values such as the polling and debounce time.

Stylisation changes can be made via SASS files. The root folder contains styles.scss and variables.scss, which are global.  

## Compiling the frontend

Requirements
-node.js

After launching the backend as instructed above, from the BossAlienMediaPlayer folder, first run 'npm install' to install node packages. Following this run:

npm run build:dev
or
npm run build:prod

This will compile the frontend, and poll for further changes (in dev mode), compiling when required.
