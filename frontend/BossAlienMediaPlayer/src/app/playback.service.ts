import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class PlaybackService {

  private enablePlaybackUrl = 'api/enableplayback'; 
  private disablePlaybackUrl = 'api/disableplayback'; 

  constructor(private http: HttpClient) { }

  enablePlayback(): void {
    this.http.post<string>(this.enablePlaybackUrl, {}).subscribe();
  }

  disablePlayback() : void{
    this.http.post<string>(this.disablePlaybackUrl, {}).subscribe();
  }

}
