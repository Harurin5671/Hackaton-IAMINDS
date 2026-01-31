import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TabContainer } from './tab-container';

describe('TabContainer', () => {
  let component: TabContainer;
  let fixture: ComponentFixture<TabContainer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TabContainer]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TabContainer);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
