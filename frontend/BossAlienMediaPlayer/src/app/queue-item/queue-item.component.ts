import { Component, OnInit, Input } from '@angular/core';

import { QueuedItem } from '../queued-item';

@Component({
  selector: 'bamp-queue-item',
  templateUrl: './queue-item.component.html',
  styleUrls: ['./queue-item.component.scss']
})
export class QueueItemComponent implements OnInit {

  @Input() QueuedItem: QueuedItem;
  constructor() { }

  ngOnInit() {
  }

}
