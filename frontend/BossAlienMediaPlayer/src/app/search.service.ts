import { Injectable, SimpleChanges, Output } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

import { Observable } from 'rxjs';
import { Track } from './track.interface';
import { map, tap } from 'rxjs/operators';
import { SearchResult } from './search-result';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  public searchResults: SearchResult[];
  public searchTerm: string;

  private searchUrl = 'api/search';

  constructor(private http: HttpClient) { }

  Search(query: string, type: string): Observable<SearchResult[]>
  {
    this.searchResults = [];
    this.searchTerm = query;
    return this.http.post<any>(this.searchUrl, {"search_text": query, "search_option": type}).pipe(
      tap(results => 
        {
          let searchResults : SearchResult[] = [];
          for(let i in results.tracks){
            let searchResult = new SearchResult();

            searchResult.Track = results.tracks[i];
            searchResult.Actions = results.actions[i].actions;
            searchResult.Reasons = results.actions[i].reasons;
            searchResults.push(searchResult);
          }
          this.searchResults = searchResults;
      })
    );
  }

  Clear(): void
  {
    this.searchResults = [];
  }

  

}
