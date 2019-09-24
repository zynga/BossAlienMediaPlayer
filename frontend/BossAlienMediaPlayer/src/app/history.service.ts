import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { Observable, timer } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { HistoryItem } from './history-item';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class HistoryService {
  public history: HistoryItem[];

  private historyUrl: string = "api/history";

  constructor(private authService: AuthService, private http: HttpClient) {
    timer(0, environment.historyPollTime).subscribe(() => this.updateHistory());
  }

  updateHistory(): void {
    if (this.authService.isLoggedIn == false)
    {
      return;
    }
    let obs:Observable<any> = this.http.get<HistoryItem[]>(this.historyUrl);
   
    obs.pipe(
      tap(results => {
        let historyItems : HistoryItem[] = [];

        for(let i in results.historyitems){
          let historyItem = new HistoryItem();

          historyItem.track = results.tracks[i];
          historyItem.track.requestedBy = results.users[results.historyitems[i].user_id];
          historyItem.upvotes = results.historyitems[i].upvotes;
          historyItem.downvotes = results.historyitems[i].downvotes;
          historyItem.epoch = results.historyitems[i].epoch;
          historyItem.was_voted_off = results.historyitems[i].was_voted_off;
          historyItems.push(historyItem);
        }
        this.history = historyItems;
      })
    ).subscribe();
  }
}
