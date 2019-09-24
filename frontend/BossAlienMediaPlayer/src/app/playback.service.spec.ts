import { TestBed } from '@angular/core/testing';

import { PlaybackService } from './playback.service';

describe('PlaybackService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: PlaybackService = TestBed.get(PlaybackService);
    expect(service).toBeTruthy();
  });
});
