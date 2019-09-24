import { Component } from '@angular/core';
import { HttpService } from './http.service';

@Component({
  selector: 'bamp-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(public httpService: HttpService) {}
  title = 'BossAlienMediaPlayer';
}
