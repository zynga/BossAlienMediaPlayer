import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SongDisplayComponent } from './song-display.component';

describe('SongDisplayComponent', () => {
  let component: SongDisplayComponent;
  let fixture: ComponentFixture<SongDisplayComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SongDisplayComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SongDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
