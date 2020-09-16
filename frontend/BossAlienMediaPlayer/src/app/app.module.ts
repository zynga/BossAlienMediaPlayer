import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule }    from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import { RouterModule, Routes } from '@angular/router';
import { VotingComponent } from './voting/voting.component';
import { QueueComponent } from './queue/queue.component';
import { SearchComponent } from './search/search.component';
import { SongDisplayComponent } from './song-display/song-display.component';
import { QueueItemComponent } from './queue-item/queue-item.component';
import { SearchResultItemComponent } from './search-result-item/search-result-item.component';
import { NowplayingComponent } from './nowplaying/nowplaying.component';
import { AlbumartComponent } from './albumart/albumart.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './auth.guard';
import { NavBarComponent } from './nav-bar/nav-bar.component';
import { ArtistsDisplayComponent } from './artists-display/artists-display.component';
import { LocationStrategy, HashLocationStrategy } from '@angular/common';
import { MopidyPlaybackStateIconComponent } from './mopidy-playback-state-icon/mopidy-playback-state-icon.component';
import { AlreadyLoggedInGuard } from './already-logged-in.guard';
import { HistoryComponent } from './history/history.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';
import { UserProfileComponent } from './user-profile/user-profile.component';
import { HistoryItemComponent } from './history-item/history-item.component';
import { ProfileEditorComponent } from './profile-editor/profile-editor.component';
import { Pipe, PipeTransform } from '@angular/core';
import { TrackLengthPipe } from "./tracklength.pipe";
import { SomethingWentWrongComponent } from './something-went-wrong/something-went-wrong.component';
import { DisconnectedFromServerGuard } from './disconnected-from-server.guard';

@Pipe({
  name: 'truncate'
 })
 
 export class TruncatePipe implements PipeTransform {
 
 transform(value: string, args: string[]): string {
     const limit = args.length > 0 ? parseInt(args[0], 10) : 20;
     const trail = args.length > 1 ? args[1] : '...';
     return value.length > limit ? value.substring(0, limit) + trail : value;
    }
 }

const appRoutes: Routes = [
  { path: 'login', component: LoginComponent, canActivate: [AlreadyLoggedInGuard] },
  { path: 'queue', component: QueueComponent, canActivate: [AuthGuard] },
  { path: 'search', component: SearchComponent, canActivate: [AuthGuard] },
  { path: 'search/:type/:query', component: SearchComponent, canActivate: [AuthGuard] },
  { path: 'search/:query', redirectTo: 'search/any/:query', pathMatch: 'full' },
  { path: 'history', component: HistoryComponent, canActivate: [AuthGuard] },
  { path: 'profile/:user_id', component: UserProfileComponent, canActivate: [AuthGuard] },
  { path: '', redirectTo: 'login', pathMatch: 'full'}
]
@NgModule({
  declarations: [
    AppComponent,
    VotingComponent,
    QueueComponent,
    SearchComponent,
    SongDisplayComponent,
    QueueItemComponent,
    SearchResultItemComponent,
    NowplayingComponent,
    AlbumartComponent,
    LoginComponent,
    NavBarComponent,
    ArtistsDisplayComponent,
    MopidyPlaybackStateIconComponent,
    HistoryComponent,
    UserProfileComponent,
    HistoryItemComponent,
    ProfileEditorComponent,
    TruncatePipe,
    TrackLengthPipe,
    SomethingWentWrongComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(appRoutes),
    FormsModule,
    NgbModule,
    BrowserAnimationsModule,
    ToastrModule.forRoot(),
    ReactiveFormsModule
  ],
  providers: [{provide: LocationStrategy, useClass: HashLocationStrategy}],
  bootstrap: [AppComponent]
})
export class AppModule { }
