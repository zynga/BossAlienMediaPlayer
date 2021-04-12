import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IcecastStreamComponent } from './icecast-stream.component';

describe('IcecastStreamComponent', () => {
  let component: IcecastStreamComponent;
  let fixture: ComponentFixture<IcecastStreamComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IcecastStreamComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IcecastStreamComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
