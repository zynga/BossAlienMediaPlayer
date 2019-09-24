import { Component, OnInit, Input } from '@angular/core';
import { HistoryItem } from '../history-item';
import { SpotifyService } from '../spotify.service';

@Component({
  selector: 'bamp-history-item',
  templateUrl: './history-item.component.html',
  styleUrls: ['./history-item.component.scss']
})
export class HistoryItemComponent implements OnInit {

  @Input() HistoryItem: HistoryItem;
  
  constructor(public spotifyService: SpotifyService) { }

  ngOnInit() {
  }

}
