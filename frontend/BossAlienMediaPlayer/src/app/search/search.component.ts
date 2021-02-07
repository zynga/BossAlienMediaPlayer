import { Component, OnInit } from '@angular/core';
import { SearchService } from '../search.service';
import { Track } from '../track.interface';
import { Observable, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, tap, skip } from 'rxjs/operators';
import { QueueService } from '../queue.service';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { SearchResult } from '../search-result';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'bamp-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {
  tracks$: Observable<SearchResult[]>
  searchType = new Subject<string>();
  searchTerms = new Subject<string>();

  searchTypes: string[] = 
  [
    "any",
    "track_name",
    "album",
    "artist",
    "uri",
  ];

  public typeMap = {
    "any": "Any",
    "track_name": "Track",
    "album": "Album",
    "artist": "Artist",
    "uri": "URI",
  }

  searching: boolean = false;

  currentSearchTerm: string;

  currentSearchType: string;

  constructor(
    public searchService: SearchService,
    private queueService: QueueService,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  search(): void {
    if (this.currentSearchTerm)
    {
      this.searchTerms.next(this.currentSearchTerm);
      this.searching = true;
    }
    else
    {
      this.searchService.Clear();
      this.location.go('/search/');
    }
  }

  ngOnInit() {
    this.currentSearchTerm = this.searchService.searchTerm;
    this.setCurrentSearchType(this.route.snapshot.params.type);

    this.tracks$ = this.searchTerms.pipe(
      debounceTime(environment.searchDebounceTime),
      tap(() => this.location.go('/search/' + this.currentSearchType + "/" + this.currentSearchTerm)),
      switchMap((term: string) => this.searchService.Search(term, this.currentSearchType))
    );

    this.tracks$.subscribe(result => 
      {
        this.searching = false;
      });

    this.route.paramMap.subscribe((result: any) => {
      if (result.params.query)
      {
        this.currentSearchTerm = result.params.query;
      }
      this.setCurrentSearchType(result.params.type);
      
      if (this.currentSearchTerm)
      {
        this.search();
      }
    });
  }

  onTrackSelected(track: Track): void {
    this.queueService.queueTrack(track);
  }

  onSearchTypeSelected(type: string): void
  {
    this.currentSearchType = type;
    this.search();
  }

  setCurrentSearchType(type: string): void
  {
    this.currentSearchType = (type ? type : this.searchTypes[0]);
    if (this.searchTypes.includes(this.currentSearchType) == false)
    {
      this.currentSearchType = this.searchTypes[0];
    }
  }
}
