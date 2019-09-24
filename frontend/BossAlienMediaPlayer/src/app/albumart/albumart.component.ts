import { Component, OnInit, Input } from '@angular/core';
import { Track } from '../track.interface';

@Component({
  selector: 'bamp-albumart',
  templateUrl: './albumart.component.html',
  styleUrls: ['./albumart.component.scss']
})
export class AlbumartComponent implements OnInit {

  @Input() Track: Track;

  constructor() { }

  ngOnInit() {
  }

}
