import { Component, OnInit } from '@angular/core';
import { QueueService } from '../queue.service';

@Component({
  selector: 'bamp-queue',
  templateUrl: './queue.component.html',
  styleUrls: ['./queue.component.scss']
})
export class QueueComponent implements OnInit {

  constructor(public queueService : QueueService) { }

  ngOnInit() {
  }

}
