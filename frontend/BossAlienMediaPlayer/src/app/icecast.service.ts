import { Injectable } from '@angular/core';
import { Observable, timer } from 'rxjs';
import { ConfigService } from './config.service';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { environment } from '../environments/environment';
import { IcecastSource } from './icecast-source';

@Injectable({
  providedIn: 'root'
})

export class IcecastService {
  
  public currentListeners : number = -1;

  constructor(private http : HttpClient, private config: ConfigService) {
    timer(0, environment.icecastListenersPollTime).subscribe(() => this.updateListeners());
  }

  updateListeners() : void {
    var icecast_url = this.config.getValue('icecast_url');

    if (icecast_url === undefined) {
      return;
    }
  
    let obs:Observable<any> = this.http.get<IcecastSource>(this.config.getValue('icecast_url') + "/status-json.xsl");
   
    obs.pipe(
      tap(results => {
            if (results.icestats.source === undefined) {
              this.currentListeners = 0;
            } else {
              this.currentListeners = results.icestats.source.listeners;
            }
          },
          error => {
            this.currentListeners = -1;
          })
    ).subscribe();
  }
}
