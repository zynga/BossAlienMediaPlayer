import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {

  constructor() { }

  openTrack(trackUri: string) : void {
    let trackId = trackUri.split(":")[2];
    window.open("http://open.spotify.com/track/" + trackId, "_blank");
  }
  
  reroute(url: string) : void {
    window.location.href = url;
  }
}
