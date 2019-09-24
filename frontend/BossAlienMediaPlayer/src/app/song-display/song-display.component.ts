import { Component, OnInit, Input } from '@angular/core';
import { Track } from '../track.interface';

@Component({
  selector: 'bamp-song-display',
  templateUrl: './song-display.component.html',
  styleUrls: ['./song-display.component.scss']
})
export class SongDisplayComponent implements OnInit {

  @Input() Track: Track;

  constructor() { }

  ngOnInit() {
  }

}
