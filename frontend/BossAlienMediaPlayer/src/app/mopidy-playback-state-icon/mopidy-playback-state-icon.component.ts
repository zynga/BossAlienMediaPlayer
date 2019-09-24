import { Component, OnInit } from '@angular/core';
import { QueueService } from '../queue.service';

@Component({
  selector: 'bamp-mopidy-playback-state-icon',
  templateUrl: './mopidy-playback-state-icon.component.html',
  styleUrls: ['./mopidy-playback-state-icon.component.scss']
})
export class MopidyPlaybackStateIconComponent implements OnInit {

  constructor(public queueService : QueueService) { }

  ngOnInit() {
  }

}
