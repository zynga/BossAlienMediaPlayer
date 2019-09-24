import { Component, OnInit, Input } from '@angular/core';
import { QueueService } from '../queue.service';
import { HttpService } from '../http.service';

const timeDisplayModeKey: string = "timeDisplayModeKey";
const showRemainingTime: string = "showRemainingTime";
const showSongDuration: string = "showSongDuration";

@Component({
  selector: 'bamp-nowplaying',
  templateUrl: './nowplaying.component.html',
  styleUrls: ['./nowplaying.component.scss']
})
export class NowplayingComponent implements OnInit {

  public timeDisplayMode: string = showSongDuration;
  constructor(public queueService : QueueService, public httpService: HttpService) { }

  ngOnInit() {
    if(localStorage.getItem(timeDisplayModeKey))
    {
      this.timeDisplayMode = localStorage.getItem(timeDisplayModeKey);
    }
  }

  secondsToMS(d) : string {
    d = Number(d);

    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    return ('' + m).slice(-2) + ":" + ('0' + s).slice(-2);
  }

  getProgressTime() : string{
    let secs = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.progress_seconds : 0;
    return this.secondsToMS(secs); 
  }

  getTotalTime() : string{
    let progress = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.progress_seconds : 0;
    let duration = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.track_length_seconds : 0
    switch (this.timeDisplayMode)
    {
      case showSongDuration:
        return "-" + this.secondsToMS(duration - progress);
      case showRemainingTime:
        return this.secondsToMS(duration);
    }
  }

  toggleTimeDisplayMode(): void {
    switch(this.timeDisplayMode)
    {
      case showSongDuration:
        this.timeDisplayMode = showRemainingTime;
        break;
      case showRemainingTime:
        this.timeDisplayMode = showSongDuration;
        break;
      default:
        this.timeDisplayMode = showSongDuration;
        break;
    }
    localStorage.setItem(timeDisplayModeKey, this.timeDisplayMode);
  }

}
