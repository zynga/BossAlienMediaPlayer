import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { User } from './user';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  public PreviousLocation: string;

  public user: User

  public isLoggedIn: boolean;

  constructor(private http: HttpClient) { }

  private loginUrl: string = "api/login";
  private logoutUrl: string = "api/logout";
  private loggedInQueryUrl: string = "api/isloggedin";
  private updateUserUrl: string = "api/updateuser";

  private loggedInThisSession: boolean;
  private loggedOutThisSession: boolean;


  login(id: string, password: string): Observable<boolean> {
    return this.http.post(this.loginUrl, {user_id: id, password: password}).pipe(
      map((x: any) => 
      {
        this.user = x.user;
        this.isLoggedIn = this.loggedInThisSession = true;
        this.loggedOutThisSession = false;
        return true;
      }),
      catchError(error => {
        console.error(error);
        return of(false);
      })
    );
  }

  logout() : Observable<Object> {
    this.user = null;
    this.isLoggedIn = this.loggedInThisSession = false;
    this.loggedOutThisSession = true;
    return this.http.get(this.logoutUrl);
  }

  getIsLoggedIn(): Observable<boolean>
  {
    if (this.loggedInThisSession)
    {
      this.isLoggedIn = true;
      return of(true);
    }
    else if (this.loggedOutThisSession)
    {
      this.isLoggedIn = false;
      return of(false);
    }

    return this.http.get(this.loggedInQueryUrl).pipe(
      map((x: any) => 
      {
        this.isLoggedIn = this.loggedInThisSession = x.logged_in;
        if (x.logged_in)
        {
          this.user = x.user;
        }
        return x.logged_in;
      })
    );
  }

  setAlias(user : User, newAlias : string) : void{
    user.alias = newAlias;
    this.http.post(this.updateUserUrl, {user_id: user.user_id, alias: newAlias}).subscribe();
  }
}
