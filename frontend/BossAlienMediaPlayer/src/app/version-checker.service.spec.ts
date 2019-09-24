import { TestBed } from '@angular/core/testing';

import { VersionCheckerService } from './version-checker.service';

describe('VersionCheckerService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: VersionCheckerService = TestBed.get(VersionCheckerService);
    expect(service).toBeTruthy();
  });
});
