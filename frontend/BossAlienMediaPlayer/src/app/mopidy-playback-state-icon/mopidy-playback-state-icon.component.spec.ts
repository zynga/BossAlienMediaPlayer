import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MopidyPlaybackStateIconComponent } from './mopidy-playback-state-icon.component';

describe('MopidyPlaybackStateIconComponent', () => {
  let component: MopidyPlaybackStateIconComponent;
  let fixture: ComponentFixture<MopidyPlaybackStateIconComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MopidyPlaybackStateIconComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MopidyPlaybackStateIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
