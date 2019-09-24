import { Component, OnInit, Input } from '@angular/core';
import { Track } from '../track.interface';
import { QueuedItemMetadata } from '../queued-item-metadata.interface';
import { QueueService } from '../queue.service';
import { AuthService } from '../auth.service';
import { SpotifyService as SpotifyService } from '../spotify.service';

@Component({
  selector: 'bamp-voting',
  templateUrl: './voting.component.html',
  styleUrls: ['./voting.component.scss']
})
export class VotingComponent implements OnInit {

  @Input() Metadata: QueuedItemMetadata;
  @Input() Track: Track;
  
  public CanShowRemoveTrack : boolean;

  constructor(
    public queueService : QueueService,
    public authService: AuthService,
    public spotifyService: SpotifyService
    ) { }

  ngOnInit() {
    this.CanShowRemoveTrack = this.Track && this.Track.is_downvote_sound == false && this.Metadata && this.Metadata.actions && this.Metadata.actions.includes('remove');
  }

  isMyTrack() : boolean {
    return this.Track ? (this.Track.is_downvote_sound == false && this.Track.requestedBy.user_id == this.authService.user.user_id) : false;
  }


  upVote() {
    if (this.Metadata.userUpvotedTrack)
    {
      this.Metadata.upvotes--;
      this.Metadata.userUpvotedTrack = false;
    }
    else
    {
      this.Metadata.upvotes++;
      if (this.Metadata.userDownvotedTrack)
      {
        this.Metadata.downvotes--;
        this.Metadata.userDownvotedTrack = false;
      }
  
      this.Metadata.userUpvotedTrack = true;
    }

    this.queueService.voteTrack(this.Track, true);
  }

  downVote() {
    if (this.Metadata.userDownvotedTrack)
    {
      this.Metadata.downvotes--;
      this.Metadata.userDownvotedTrack = false;
    }
    else
    {
      this.Metadata.downvotes++;
      if (this.Metadata.userUpvotedTrack)
      {
        this.Metadata.upvotes--;
        this.Metadata.userUpvotedTrack = false;
      }
  
      this.Metadata.userDownvotedTrack = true;
    }
    
    this.queueService.voteTrack(this.Track, false);
  }

  trash(): void {
    this.queueService.removeTrack(this.Track);
  }

  onEnterVotingComponent() : void {
    this.queueService.pauseQueueUpdating();
  }

  onLeaveVotingComponent() : void {
    this.queueService.resumeQueueUpdating();
  }

}
