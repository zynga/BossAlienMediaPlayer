import { TestBed, async, inject } from '@angular/core/testing';

import { AlreadyLoggedInGuard } from './already-logged-in.guard';

describe('AlreadyLoggedInGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AlreadyLoggedInGuard]
    });
  });

  it('should ...', inject([AlreadyLoggedInGuard], (guard: AlreadyLoggedInGuard) => {
    expect(guard).toBeTruthy();
  }));
});
