import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Track } from '../track.interface';
import { SearchService } from '../search.service';
import { SearchResult } from '../search-result';
import { Router } from '@angular/router';
import { SpotifyService } from '../spotify.service';

@Component({
  selector: 'bamp-search-result-item',
  templateUrl: './search-result-item.component.html',
  styleUrls: ['./search-result-item.component.scss']
})
export class SearchResultItemComponent implements OnInit {
  @Input() SearchResult: SearchResult;
  @Output() selected = new EventEmitter<Track>();

  public queueingAllowed: boolean;
  public noQueueReason: string;

  //private noQueueReasonMap:Map<string, string>;

  constructor(public spotifyService: SpotifyService) { }

  private noQueueReasonMap = {
    on_queue : "On Queue",
    too_soon: "Recently Played",
    voted_off_queue: "Recently Vetoed"
  };

  ngOnInit() {
    this.queueingAllowed = this.SearchResult.Actions.includes("queue");
    if (!this.queueingAllowed)
    {
      this.noQueueReason = this.getNoQueueReason(this.SearchResult.Reasons[0]);
    }
  }

  Select() :void {
    this.queueingAllowed = false;
    this.SearchResult.Actions.splice(this.SearchResult.Actions.indexOf("queue"), 1);
    this.noQueueReason = this.getNoQueueReason("on_queue");
    this.SearchResult.Reasons.push("on_queue");
    this.selected.emit(this.SearchResult.Track);
  }

  getNoQueueReason(reason : string) : string {    
    let mapVal = this.noQueueReasonMap[reason];
    return mapVal;
  }
}
