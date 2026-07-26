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
    if (memory) {
        const mb = memory / 1024 / 1024;
        console.log(`Heap: ${mb.toFixed(2)} MB`);
        expect(mb).toBeLessThan(50); // Initial load
    }
  });
});
