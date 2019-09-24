import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'bamp-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  id: string;
  password: string;

  loginError: boolean;
  
  constructor(private authService: AuthService, private router: Router) { }

  ngOnInit() {
  }

  login(id: string, password: string)
  {
    this.authService.login(id, password).subscribe(success => {
      this.loginError = !success;
      if (success) {
        this.router.navigate(['/queue']);
      }
    });
  }

}
