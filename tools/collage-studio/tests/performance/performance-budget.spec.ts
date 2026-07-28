import { test, expect } from '@playwright/test';

test.describe('Performance Budget', () => {
  
  test('LCP should be under 1.2s', async ({ page }) => {
    await page.goto('/');
    
    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      });
    });

    console.log(`LCP: ${lcp}ms`);
    expect(lcp).toBeLessThan(1200);
  });

  test('Memory usage should be stable', async ({ page }) => {
    // Note: implementation requires launching chrome with --enable-precise-memory-info
    await page.goto('/');

    // Simulate usage
    await page.waitForTimeout(1000);

    const memory = await page.evaluate(() => (performance as any).memory?.usedJSHeapSize);

    // SKIP LOUDLY, DO NOT PASS QUIETLY. `performance.memory` is Chromium-only,
    // so on both WebKit projects the old `if (memory) { expect(...) }` asserted
    // NOTHING and still reported green — a budget that cannot fail on the very
    // engine the owner's phone runs. An explicit skip puts the hole in the
    // report where it can be counted.
    test.skip(!memory, 'performance.memory is Chromium-only — no heap budget on this engine');

    const mb = memory / 1024 / 1024;
    console.log(`Heap: ${mb.toFixed(2)} MB`);
    expect(mb).toBeLessThan(50); // Initial load
  });
});
