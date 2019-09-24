import { Injectable } from '@angular/core';
import { tap } from 'rxjs/operators';

const knownBuildHashKey: string = "knownBuildHash";

@Injectable({
  providedIn: 'root'
})
export class VersionCheckerService {
  buildHash: string;
  constructor() {
    if(localStorage.getItem(knownBuildHashKey))
    {
      this.buildHash = localStorage.getItem(knownBuildHashKey);
    }
    else
    {
      this.buildHash = "";
      localStorage.setItem(knownBuildHashKey, this.buildHash);
    }
  }

  reloadIfServerBuildHashChanged (response:any)
  {
    let knownHash = localStorage.getItem(knownBuildHashKey);
    let serverHash = response.headers.get('Build-Hash');
    if (!serverHash)
    {
      return;
    }
    
    if (!knownHash)
    {
      localStorage.setItem(knownBuildHashKey, serverHash);
      return;
    }

    if (serverHash != knownHash)
    {
      localStorage.setItem(knownBuildHashKey, serverHash);
      location.reload();
    }
  }
}
