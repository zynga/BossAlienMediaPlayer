import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NowplayingComponent } from './nowplaying.component';

describe('NowplayingComponent', () => {
  let component: NowplayingComponent;
  let fixture: ComponentFixture<NowplayingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NowplayingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NowplayingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
