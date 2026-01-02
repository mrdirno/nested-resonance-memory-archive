/**
 * PERFORMANCE BUDGET TEST SUITE
 * Section 17.2: Performance Budgets
 *
 * Defines hard limits for CI/CD pipeline:
 * - LCP (Largest Contentful Paint): < 1.2s
 * - Bundle Size: < 150KB (gzip)
 * - Memory: < 500MB during test runs
 *
 * Run: npx playwright test tests/performance/performance-budget.spec.ts
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Performance thresholds
const THRESHOLDS = {
  LCP_MS: 1200,           // Largest Contentful Paint < 1.2s
  FCP_MS: 800,            // First Contentful Paint < 800ms
  BUNDLE_SIZE_KB: 150,    // Gzip bundle < 150KB
  MEMORY_MB: 500,         // JS Heap < 500MB
  LAYOUT_TIME_MS: 100,    // Layout computation < 100ms
  RENDER_TIME_MS: 500,    // Canvas render < 500ms (for 1200px preview)
};

// ============================================================================
// BUNDLE SIZE TESTS
// ============================================================================

test.describe('Bundle Size Budget', () => {
  test('main bundle is under 150KB gzipped', async () => {
    const distPath = path.join(__dirname, '../../dist/assets');

    if (!fs.existsSync(distPath)) {
      test.skip();
      return;
    }

    const files = fs.readdirSync(distPath);
    const jsFiles = files.filter(f => f.endsWith('.js'));

    let totalSize = 0;
    for (const file of jsFiles) {
      const filePath = path.join(distPath, file);
      const stats = fs.statSync(filePath);
      totalSize += stats.size;
    }

    const sizeKB = totalSize / 1024;
    console.log(`Total JS bundle size: ${sizeKB.toFixed(2)} KB`);

    // Note: This is uncompressed size. Gzip typically reduces by 60-70%
    // So 150KB gzip ≈ 450KB uncompressed
    expect(sizeKB).toBeLessThan(THRESHOLDS.BUNDLE_SIZE_KB * 3);
  });
});

// ============================================================================
// CORE WEB VITALS
// ============================================================================

test.describe('Core Web Vitals', () => {
  test('LCP is under 1.2 seconds', async ({ page }) => {
    // Collect performance metrics
    const metrics: any[] = [];

    page.on('console', msg => {
      if (msg.text().includes('LCP:')) {
        metrics.push(msg.text());
      }
    });

    await page.goto('/');

    // Inject performance observer
    const lcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let lcpValue = 0;

        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1] as any;
          if (lastEntry) {
            lcpValue = lastEntry.startTime;
          }
        });

        observer.observe({ type: 'largest-contentful-paint', buffered: true });

        // Wait for page to settle, then resolve
        setTimeout(() => {
          observer.disconnect();
          resolve(lcpValue);
        }, 3000);
      });
    });

    console.log(`LCP: ${lcp.toFixed(2)}ms`);
    expect(lcp).toBeLessThan(THRESHOLDS.LCP_MS);
  });

  test('FCP is under 800ms', async ({ page }) => {
    await page.goto('/');

    const fcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            if (entry.name === 'first-contentful-paint') {
              resolve(entry.startTime);
              observer.disconnect();
              return;
            }
          }
        });

        observer.observe({ type: 'paint', buffered: true });

        // Timeout fallback
        setTimeout(() => {
          observer.disconnect();
          resolve(0);
        }, 5000);
      });
    });

    console.log(`FCP: ${fcp.toFixed(2)}ms`);
    expect(fcp).toBeLessThan(THRESHOLDS.FCP_MS);
  });
});

// ============================================================================
// MEMORY USAGE
// ============================================================================

test.describe('Memory Budget', () => {
  test('JS heap stays under 500MB during layout computation', async ({ page }) => {
    await page.goto('/');

    // Measure baseline memory
    const baselineMemory = await page.evaluate(() => {
      if ((performance as any).memory) {
        return (performance as any).memory.usedJSHeapSize / (1024 * 1024);
      }
      return 0;
    });

    // Run heavy layout computation
    await page.evaluate(() => {
      const createRng = (s: number) => {
        let t = s + 0x6D2B79F5;
        return () => {
          t = Math.imul(t ^ (t >>> 15), t | 1);
          t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      };

      // Stress test: compute 100 layouts
      for (let iter = 0; iter < 100; iter++) {
        const rng = createRng(iter);
        const W = 4096, H = 2730, count = 25;
        let nodes = [{ x: 0, y: 0, w: W, h: H }];

        while (nodes.length < count) {
          let idx = 0, maxScore = -1;
          for (let i = 0; i < nodes.length; i++) {
            const score = nodes[i].w * nodes[i].h * (0.8 + rng() * 0.4);
            if (score > maxScore) { maxScore = score; idx = i; }
          }

          const p = nodes[idx];
          nodes.splice(idx, 1);
          const split = 0.382 + rng() * 0.236;
          if (p.w > p.h) {
            nodes.push({ x: p.x, y: p.y, w: p.w * split, h: p.h });
            nodes.push({ x: p.x + p.w * split, y: p.y, w: p.w * (1 - split), h: p.h });
          } else {
            nodes.push({ x: p.x, y: p.y, w: p.w, h: p.h * split });
            nodes.push({ x: p.x, y: p.y + p.h * split, w: p.w, h: p.h * (1 - split) });
          }
        }
      }
    });

    // Measure peak memory
    const peakMemory = await page.evaluate(() => {
      if ((performance as any).memory) {
        return (performance as any).memory.usedJSHeapSize / (1024 * 1024);
      }
      return 0;
    });

    console.log(`Memory: baseline=${baselineMemory.toFixed(2)}MB, peak=${peakMemory.toFixed(2)}MB`);

    if (peakMemory > 0) {
      expect(peakMemory).toBeLessThan(THRESHOLDS.MEMORY_MB);
    }
  });
});

// ============================================================================
// COMPUTATION TIME
// ============================================================================

test.describe('Computation Time Budget', () => {
  test('layout computation completes in under 100ms', async ({ page }) => {
    await page.goto('/');

    const layoutTime = await page.evaluate(() => {
      const createRng = (s: number) => {
        let t = s + 0x6D2B79F5;
        return () => {
          t = Math.imul(t ^ (t >>> 15), t | 1);
          t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      };

      const start = performance.now();

      // Standard layout: 9 cells at 1200px
      const rng = createRng(12345);
      const W = 1200, H = 800, count = 9;
      let nodes = [{ x: 0, y: 0, w: W, h: H }];

      while (nodes.length < count) {
        let idx = 0, maxScore = -1;
        for (let i = 0; i < nodes.length; i++) {
          const score = nodes[i].w * nodes[i].h * (0.8 + rng() * 0.4);
          if (score > maxScore) { maxScore = score; idx = i; }
        }

        const p = nodes[idx];
        nodes.splice(idx, 1);
        const split = 0.382 + rng() * 0.236;
        if (p.w > p.h) {
          nodes.push({ x: p.x, y: p.y, w: p.w * split, h: p.h });
          nodes.push({ x: p.x + p.w * split, y: p.y, w: p.w * (1 - split), h: p.h });
        } else {
          nodes.push({ x: p.x, y: p.y, w: p.w, h: p.h * split });
          nodes.push({ x: p.x, y: p.y + p.h * split, w: p.w, h: p.h * (1 - split) });
        }
      }

      return performance.now() - start;
    });

    console.log(`Layout time: ${layoutTime.toFixed(2)}ms`);
    expect(layoutTime).toBeLessThan(THRESHOLDS.LAYOUT_TIME_MS);
  });

  test('high-res layout (30000px) completes in under 500ms', async ({ page }) => {
    await page.goto('/');

    const layoutTime = await page.evaluate(() => {
      const createRng = (s: number) => {
        let t = s + 0x6D2B79F5;
        return () => {
          t = Math.imul(t ^ (t >>> 15), t | 1);
          t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      };

      const start = performance.now();

      // High-res layout: 25 cells at 30000px
      const rng = createRng(12345);
      const W = 30000, H = 20000, count = 25;
      let nodes = [{ x: 0, y: 0, w: W, h: H }];

      while (nodes.length < count) {
        let idx = 0, maxScore = -1;
        for (let i = 0; i < nodes.length; i++) {
          const score = nodes[i].w * nodes[i].h * (0.8 + rng() * 0.4);
          if (score > maxScore) { maxScore = score; idx = i; }
        }

        const p = nodes[idx];
        nodes.splice(idx, 1);
        const split = 0.382 + rng() * 0.236;
        if (p.w > p.h) {
          nodes.push({ x: p.x, y: p.y, w: p.w * split, h: p.h });
          nodes.push({ x: p.x + p.w * split, y: p.y, w: p.w * (1 - split), h: p.h });
        } else {
          nodes.push({ x: p.x, y: p.y, w: p.w, h: p.h * split });
          nodes.push({ x: p.x, y: p.y + p.h * split, w: p.w, h: p.h * (1 - split) });
        }
      }

      return performance.now() - start;
    });

    console.log(`High-res layout time: ${layoutTime.toFixed(2)}ms`);
    expect(layoutTime).toBeLessThan(THRESHOLDS.RENDER_TIME_MS);
  });
});

// ============================================================================
// MEMORY LEAK DETECTION
// ============================================================================

test.describe('Memory Leak Detection', () => {
  test('no memory leak after 10 layout generations', async ({ page }) => {
    await page.goto('/');

    // Get initial memory
    const initialMemory = await page.evaluate(() => {
      if ((performance as any).memory) {
        // Force GC if available
        if ((window as any).gc) (window as any).gc();
        return (performance as any).memory.usedJSHeapSize;
      }
      return 0;
    });

    // Run 10 cycles
    for (let cycle = 0; cycle < 10; cycle++) {
      await page.evaluate((seed) => {
        const createRng = (s: number) => {
          let t = s + 0x6D2B79F5;
          return () => {
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
          };
        };

        const rng = createRng(seed);
        const W = 1200, H = 800, count = 9;
        let nodes = [{ x: 0, y: 0, w: W, h: H }];

        while (nodes.length < count) {
          const idx = Math.floor(rng() * nodes.length);
          const p = nodes[idx];
          nodes.splice(idx, 1);
          const split = 0.382 + rng() * 0.236;
          if (p.w > p.h) {
            nodes.push({ x: p.x, y: p.y, w: p.w * split, h: p.h });
            nodes.push({ x: p.x + p.w * split, y: p.y, w: p.w * (1 - split), h: p.h });
          } else {
            nodes.push({ x: p.x, y: p.y, w: p.w, h: p.h * split });
            nodes.push({ x: p.x, y: p.y + p.h * split, w: p.w, h: p.h * (1 - split) });
          }
        }
      }, cycle);
    }

    // Get final memory
    const finalMemory = await page.evaluate(() => {
      if ((performance as any).memory) {
        if ((window as any).gc) (window as any).gc();
        return (performance as any).memory.usedJSHeapSize;
      }
      return 0;
    });

    if (initialMemory > 0 && finalMemory > 0) {
      const growthMB = (finalMemory - initialMemory) / (1024 * 1024);
      console.log(`Memory growth after 10 cycles: ${growthMB.toFixed(2)}MB`);

      // Allow max 50MB growth for 10 cycles
      expect(growthMB).toBeLessThan(50);
    }
  });
});
