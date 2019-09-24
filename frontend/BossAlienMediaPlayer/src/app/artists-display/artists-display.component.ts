import { Component, OnInit, Input } from '@angular/core';
import { Artist } from '../artist';

@Component({
  selector: 'bamp-artists-display',
  templateUrl: './artists-display.component.html',
  styleUrls: ['./artists-display.component.scss']
})
export class ArtistsDisplayComponent implements OnInit {

  @Input() Artists: Artist[];
  @Input() MaxArtists: number;

  constructor() { }

  ngOnInit() {
  }

}
