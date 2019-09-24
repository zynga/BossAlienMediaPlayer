import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SomethingWentWrongComponent } from './something-went-wrong.component';

describe('SomethingWentWrongComponent', () => {
  let component: SomethingWentWrongComponent;
  let fixture: ComponentFixture<SomethingWentWrongComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SomethingWentWrongComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SomethingWentWrongComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
