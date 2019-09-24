import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';

class FormInput {
  public alias: string;
}

@Component({
  selector: 'bamp-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {

  protected formInput : FormInput = new FormInput();

  constructor(private authService: AuthService) {
    
  }

  ngOnInit() {
    this.formInput.alias = this.authService.user.alias;
  }

}
