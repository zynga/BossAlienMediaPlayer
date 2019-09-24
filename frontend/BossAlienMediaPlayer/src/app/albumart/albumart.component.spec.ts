import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AlbumartComponent } from './albumart.component';

describe('AlbumartComponent', () => {
  let component: AlbumartComponent;
  let fixture: ComponentFixture<AlbumartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AlbumartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AlbumartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
