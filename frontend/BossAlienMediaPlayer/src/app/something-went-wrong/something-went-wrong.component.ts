import { Component, OnInit } from '@angular/core';
import { timer } from 'rxjs';
import { HttpService } from '../http.service';

@Component({
  selector: 'bamp-something-went-wrong',
  templateUrl: './something-went-wrong.component.html',
  styleUrls: ['./something-went-wrong.component.scss']
})
export class SomethingWentWrongComponent implements OnInit {

  public now: number;
  public timeToRetry: number;
  constructor(public httpService: HttpService) { }

  ngOnInit() {
    timer(0, 1000).subscribe(() => 
    {
      this.now = Date.now();
      this.timeToRetry = Math.abs(Math.ceil(((this.httpService.lastRequestTime + this.httpService.retryDelay) - this.now) / 1000)) * 1000;
    });
  }

}
