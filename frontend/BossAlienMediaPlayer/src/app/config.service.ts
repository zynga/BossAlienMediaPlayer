import { Injectable } from '@angular/core';
import { ConfigValue } from './config-value';
import { Observable, timer } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
// Will query and cache config values from BAMP for other components
export class ConfigService {
  
  private configUrl : string = "api/config";

  private configValues : string[] = [ "icecast_url" ];

  private config : { [configName: string] : string; } = {}

  constructor(private http: HttpClient) {
    for (let i in this.configValues) {
        let obs:Observable<any> = this.http.get<ConfigValue>(this.configUrl + "/" + this.configValues[i]);

        obs.pipe(
            tap(result => {
                this.config[result.name] = result.value;
            })
        ).subscribe();
    }
  }

  getValue(name:string) : string {
    return this.config[name];
  }
  
}
