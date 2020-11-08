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

  getProgressTime() : number {
    let secs = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.progress_seconds : 0;
    return secs*1000; 
  }

  getTotalTime() : number {
    let progress = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.progress_seconds : 0;
    let duration = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.track_length_seconds : 0
    switch (this.timeDisplayMode)
    {
      case showRemainingTime:
        return -(duration - progress)*1000;
      case showSongDuration:
        return duration*1000;
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

  getTotalQueueLengthMilliseconds() : number {
    if (this.queueService.queueLengthMilliseconds == NaN) return 0;

    let progress = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.progress_seconds : 0;
    let duration = this.queueService.currentPlaybackState ? this.queueService.currentPlaybackState.track_length_seconds : 0;
    return (duration - progress)*1000 + this.queueService.queueLengthMilliseconds;
  }
}
