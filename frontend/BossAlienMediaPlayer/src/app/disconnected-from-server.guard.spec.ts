import { TestBed, async, inject } from '@angular/core/testing';

import { DisconnectedFromServerGuard } from './disconnected-from-server.guard';

describe('DisconnectedFromServerGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DisconnectedFromServerGuard]
    });
  });

  it('should ...', inject([DisconnectedFromServerGuard], (guard: DisconnectedFromServerGuard) => {
    expect(guard).toBeTruthy();
  }));
});
