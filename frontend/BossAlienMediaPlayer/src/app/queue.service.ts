import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { timer } from 'rxjs'

import { environment } from '../environments/environment';
import { Track } from './track.interface';
import { PlaybackState } from './playback.interface';
import { QueuedItem } from './queued-item';
import { QueuedItemMetadata } from './queued-item-metadata.interface';
import { AuthService } from './auth.service';
import { VersionCheckerService } from './version-checker.service';
import { Router } from '@angular/router';
import { HttpService } from './http.service';

@Injectable({
  providedIn: 'root'
})
export class QueueService {
  private lastVoteTime : number = Date.now();
  private shouldUpdate : boolean = true;
  
  private queueUrl = 'api/queue';
  private removeUrl = 'api/remove';
  private nowPlayingUrl = 'api/nowplaying'; 
  private voteUrl = 'api/vote'
    
  public currentTrack : Track;
  public currentPlaybackState : PlaybackState;
  public currentQueuedItemMetadata : QueuedItemMetadata;
  
  public queue: QueuedItem[];

  constructor(
    private http: HttpClient,
    private authService:AuthService,
    private versionChecker: VersionCheckerService,
    private router: Router,
    private httpService: HttpService
  ) {    
    timer(0, environment.nowPlayingPollTime).subscribe(() => this.updateNowPlaying());
    timer(0, environment.queuePollTime).subscribe(() => this.updateQueue());
  }

  updateQueue(): void {
    if (this.authService.isLoggedIn == false )
    {
      return;
    }

    if (this.httpService.connected == false)
    {
      return;
    }

    this.httpService.attemptHttpGetRequest<QueuedItem>(this.queueUrl, (response: any) =>
    {
      if (this.shouldUpdate == false)
      {
        if (Date.now() - this.lastVoteTime > environment.queueUpdatePauseDuration)
        {
          this.shouldUpdate = true;
        }
        else
        {
          return;
        }
      }
      let queueChanged: boolean = false;
      
      let tracks = response.body.tracks;
      
      if (this.queue && tracks.length != this.queue.length)
      {
        queueChanged = true;
      }
      
      let queuedItems : QueuedItem[] = [];
      
      for(let i in tracks){
        let queuedItem = new QueuedItem();
        
        let track : Track = tracks[i];
        let metadata : QueuedItemMetadata = response.body.queueitems[i];
        
        queuedItem.track = track;
        queuedItem.track.requestedBy = response.body.users[metadata.user_id];
        queuedItem.metadata = metadata;
        queuedItem.metadata.actions = response.body.actions[i].actions;
        queuedItem.metadata.reasons = response.body.actions[i].reasons;
        queuedItem.metadata.userUpvotedTrack = response.body.actions[i].reasons.includes('voted_up');
        queuedItem.metadata.userDownvotedTrack = response.body.actions[i].reasons.includes('voted_down');
        
        if (this.queue && queueChanged == false)
        {
          if(this.queue.length > (+i) && this.queuedItemsAreEqual(this.queue[i], queuedItem) == false)
          {
            queueChanged = true;
          }
        }
        
        queuedItems.push(queuedItem);
      }
      if (queueChanged || this.queue == undefined)
      {
        this.queue = queuedItems;
      }
    });
  }

  updateNowPlaying(): void {
    if (this.httpService.connected == false)
    {
      return;
    }

    this.httpService.attemptHttpGetRequest<Track>(this.nowPlayingUrl, (response: any) =>
    {
      this.currentQueuedItemMetadata = response.body.queueitem;
      this.currentPlaybackState = response.body.playbackstate;
      
      let track = response.body.track;
      if (track)
      {
        track.requestedBy = response.body.user;
      }

      if(response.body.actions)
      {
      this.currentQueuedItemMetadata.userUpvotedTrack = response.body.actions.reasons.includes('voted_up');
      this.currentQueuedItemMetadata.userDownvotedTrack = response.body.actions.reasons.includes('voted_down');
      }

      if (!this.currentTrack || (this.currentTrack && track && this.tracksAreEqual(this.currentTrack, track) == false))
      {
        this.currentTrack = track;
      }        

      if(this.currentTrack && this.currentTrack.is_downvote_sound == false)
        this.currentTrack.requestedBy = response.body.user;
      if (!track)
        this.currentTrack = null;
    })
  }

  queueTrack(track: Track): void {
    this.httpService.attemptHttpPostRequest<string>(this.queueUrl, {"track_uri": track.uri}, (result: any) => {
      console.log(result);
      // if (result.success) {
      //   this.toastr.success(track.name + " added to queue", "Added to queue");
      // }
    });
  } 

  voteTrack(track : Track, upVote : boolean) :void {
    this.shouldUpdate = false;
    this.lastVoteTime = Date.now();
    this.http.post<string>(this.voteUrl, {"track_uri": track.uri, "vote_type" : upVote ? "up" : "down"}).subscribe();
  }

  removeTrack(track: Track) : void{
    this.httpService.attemptHttpPostRequest(this.removeUrl, {"track_uri": track.uri});
    this.http.post(this.removeUrl, {"track_uri": track.uri}).subscribe();
    let indexToRemove = -1;
    for (let i = 0; i < this.queue.length; i++) {
      const queuedItem: QueuedItem = this.queue[i];
      if (queuedItem.track.uri == track.uri)
      {
        indexToRemove = i;
        break;
      }
    }
    if (indexToRemove > -1)
    {
      this.queue.splice(indexToRemove, 1);
    }
  }

  getIsInQueueOrNowPlaying(track: Track): boolean {
    for (let i = 0; i < this.queue.length; i++) {
      const queuedItem: QueuedItem = this.queue[i];
      if (queuedItem.track.uri == track.uri)
      {
        return true;
      }
    }
    return this.currentTrack.uri == track.uri;
  }

  queuedItemsAreEqual(item1: QueuedItem, item2: QueuedItem)
  {
    return this.tracksAreEqual(item1.track, item2.track)
      && item1.metadata.upvotes == item2.metadata.upvotes
      && item1.metadata.downvotes == item2.metadata.downvotes;
  }

  tracksAreEqual(track1: Track, track2: Track)
  {
    if(track1.is_downvote_sound || track2.is_downvote_sound)
      return false;

    return track1.uri == track2.uri
      && track1.requestedBy.alias == track2.requestedBy.alias;
  }

  pauseQueueUpdating()
  {
    this.shouldUpdate = false;
  }

  resumeQueueUpdating()
  {
    this.shouldUpdate = true;
  }
}
