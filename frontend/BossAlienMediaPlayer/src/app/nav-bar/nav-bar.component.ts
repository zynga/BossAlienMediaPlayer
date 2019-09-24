import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';
import { QueueService } from '../queue.service';

@Component({
  selector: 'bamp-nav-bar',
  templateUrl: './nav-bar.component.html',
  styleUrls: ['./nav-bar.component.scss']
})
export class NavBarComponent implements OnInit {

  constructor(public authService: AuthService, private router: Router, protected queueService : QueueService) { }

  ngOnInit() {
    this.authService.getIsLoggedIn();
  }

  isPlayingTitle(songTitle) : boolean {

    if(this.queueService.currentTrack && this.queueService.currentTrack.name.includes(songTitle))
      return true;

    return false;
  }

  getIcon() : string {
    if(this.isPlayingTitle("In The Air"))
    {
      return "assets/phil.png";
    }
    else if(this.isPlayingTitle("Pugwash"))
    {
      return "assets/pugwash.png";
    }
    else
    {
      return "assets/bamplogo_small.png";
    }
  }

  logoutPressed() {
    console.log("Logging out");
    this.authService.logout().subscribe(() => 
    {
      this.router.navigate(['/login']);
    });
  } 

  getTitle() : string {

    if(this.queueService.currentTrack && this.queueService.currentTrack.is_downvote_sound == false)
    {
      return this.queueService.currentTrack.name + ' - ' + this.queueService.currentTrack.artists[0].name;
    }

    return "BAMP";
  }
  
}
