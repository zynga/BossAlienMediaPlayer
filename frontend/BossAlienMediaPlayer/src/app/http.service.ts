import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { VersionCheckerService } from './version-checker.service';
import { timer } from 'rxjs';
import { environment } from 'src/environments/environment';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class HttpService {

  public connected: boolean = true;
  public retryDelay:number = 1000;
  public lastRequestTime: number;
  public requestInFlight: boolean;

  constructor(
    private http: HttpClient,
    private versionChecker: VersionCheckerService
  ) { }

  attemptHttpGetRequest<T>(url: string, onSuccess: Function = null, retryDelay = 1000)
  {
    this.requestInFlight = true;
    this.lastRequestTime = Date.now();
    this.retryDelay = retryDelay;
    let http$ = this.http.get<T>(url, {observe: "response"});
    http$.pipe(
      tap(response => this.versionChecker.reloadIfServerBuildHashChanged(response))
    );

    http$.subscribe(
      res => 
      {
        this.requestInFlight = false;
        this.connected = true;
        if (onSuccess)
        {
          onSuccess(res);
        }
      },
      err => 
      {
        this.requestInFlight = false;
        if (err.status == 404) // This prevents the pesky error from /api/queue when not logged in
        {
          return;
        }
        this.connected = false;
        timer(retryDelay).subscribe(() => {
          this.lastRequestTime = Date.now();
          this.attemptHttpGetRequest<T>(url, onSuccess, Math.min(retryDelay * 2, environment.maxRequestRetryDelayTime));
        });
      }
    )
  }

  attemptHttpPostRequest<T>(url: string, body: any, onSuccess: Function = null, retryDelay = 1000)
  {
    this.lastRequestTime = Date.now();
    this.retryDelay = retryDelay;
    let http$ = this.http.post<T>(url, body, {observe: "response"});

    http$.pipe(
      tap(response => this.versionChecker.reloadIfServerBuildHashChanged(response))
    );

    http$.subscribe(
      res => 
      {
        this.requestInFlight = false;
        this.connected = true;
        if (onSuccess)
        {
          onSuccess(res);
        }
      },
      err => 
      {
        this.requestInFlight = false;
        this.connected = false;
        
        timer(retryDelay).subscribe(() => {
          this.lastRequestTime = Date.now();
          this.attemptHttpPostRequest<T>(url, body, onSuccess, Math.min(retryDelay * 2, environment.maxRequestRetryDelayTime));
        });
      }
    )
  }
}
