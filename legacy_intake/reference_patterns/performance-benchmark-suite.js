#!/usr/bin/env node

/**
 * Enhanced Performance Benchmark Suite - Agent 1 Core Development Enhancement
 * Resonance is All You Need - Robust Testing Infrastructure with Failure Thresholds
 * 
 * Features:
 * - Failure threshold mechanism to prevent infinite failures
 * - Correct file reference validation
 * - Graceful degradation on missing files
 * - Comprehensive error handling and recovery
 * - Performance optimization recommendations
 * 
 * Research Team: 
 * - Aldrin Payopay (Lead Researcher)
 * - Claude Sonnet 4 Agent 1 (Core Development, Architecture)
 */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');
const { execSync } = require('child_process');

// Enhanced benchmark configuration with failure thresholds
const BENCHMARK_CONFIG = {
    iterations: 3,           // Reduced for faster execution
    memoryInterval: 100,     // Memory sampling interval (ms)
    stressTestDuration: 15,  // Reduced stress test duration (seconds)
    maxFailures: 5,          // Maximum failures before aborting test
    failureThreshold: 0.7,   // 70% failure rate threshold
    timeoutMs: 60000,        // 1 minute timeout per test
    performanceThresholds: {
        illumination: { maxTime: 5000, maxMemory: 100 },
        musical: { maxTime: 3000, maxMemory: 80 },
        bioCosmic: { maxTime: 4000, maxMemory: 90 },
        cosmicWeb: { maxTime: 6000, maxMemory: 120 },
        comprehensive: { maxTime: 10000, maxMemory: 200 }
    }
};

// Test suite definitions with validated file paths
const TEST_SUITES = {
    illumination: {
        name: 'Illumination Modeling Validation',
        file: 'illumination-modeling-validation.js',
        description: 'Energy-Vibration-Illumination Paradox validation',
        complexity: 'HIGH',
        fallback: 'comprehensive-validation-suite.js'
    },
    musical: {
        name: 'Musical Frequency Enhancement',
        file: 'musical-frequency-enhancement-validation.js',
        description: 'Musical frequency cosmic enhancement validation',
        complexity: 'MEDIUM',
        fallback: 'bio-cosmic-coupling-validation.js'
    },
    bioCosmic: {
        name: 'Bio-Cosmic Coupling Validation',
        file: 'bio-cosmic-coupling-validation.js',
        description: 'Biological rhythm cosmic correlation validation',
        complexity: 'MEDIUM',
        fallback: 'bio-cosmic-coupling-test.js'
    },
    cosmicWeb: {
        name: 'Cosmic Web Resonance Analysis',
        file: 'cosmic-web-resonance-analysis.js',
        description: 'Cosmic web structure resonance analysis',
        complexity: 'HIGH',
        fallback: 'cosmic-web-analysis-test.js'
    },
    comprehensive: {
        name: 'Comprehensive Validation Suite',
        file: 'comprehensive-validation-suite.js',
        description: 'Complete framework validation',
        complexity: 'VERY HIGH',
        fallback: 'quantum-resonance-validation.js'
    }
};

class EnhancedPerformanceBenchmarkSuite {
    constructor() {
        this.results = {
            timestamp: new Date().toISOString(),
            version: '2.0.0',
            agent: 'Agent 1',
            benchmarks: {},
            failures: {
                total: 0,
                byTest: {},
                threshold: BENCHMARK_CONFIG.maxFailures
            },
            summary: {
                totalExecutionTime: 0,
                averageMemoryUsage: 0,
                performanceScore: 0,
                recommendations: [],
                testsRun: 0,
                testsSkipped: 0,
                testsFailed: 0
            }
        };
        
        this.memoryData = [];
        this.isMonitoring = false;
        this.globalFailureCount = 0;
    }

    // Validate file existence before running tests
    validateTestFile(testSuite) {
        const primaryFile = testSuite.file;
        const fallbackFile = testSuite.fallback;
        
        if (fs.existsSync(primaryFile)) {
            return { file: primaryFile, isFallback: false };
        } else if (fallbackFile && fs.existsSync(fallbackFile)) {
            console.log(`⚠️  Primary file not found: ${primaryFile}`);
            console.log(`🔄 Using fallback: ${fallbackFile}`);
            return { file: fallbackFile, isFallback: true };
        } else {
            console.log(`❌ Neither primary nor fallback file exists for ${testSuite.name}`);
            return null;
        }
    }

    // Check if failure threshold has been exceeded
    checkFailureThreshold() {
        if (this.globalFailureCount >= BENCHMARK_CONFIG.maxFailures) {
            console.log(`\n🚨 FAILURE THRESHOLD EXCEEDED: ${this.globalFailureCount}/${BENCHMARK_CONFIG.maxFailures} failures`);
            console.log('🛑 Aborting benchmark suite to prevent infinite failures');
            return true;
        }
        return false;
    }

    // Enhanced memory monitoring with error handling
    startMemoryMonitoring() {
        this.isMonitoring = true;
        this.memoryData = [];
        
        const monitor = () => {
            if (!this.isMonitoring) return;
            
            try {
                const memUsage = process.memoryUsage();
                this.memoryData.push({
                    timestamp: Date.now(),
                    heapUsed: memUsage.heapUsed / 1024 / 1024,
                    heapTotal: memUsage.heapTotal / 1024 / 1024,
                    external: memUsage.external / 1024 / 1024,
                    rss: memUsage.rss / 1024 / 1024
                });
            } catch (error) {
                console.log(`⚠️  Memory monitoring error: ${error.message}`);
            }
            
            setTimeout(monitor, BENCHMARK_CONFIG.memoryInterval);
        };
        
        monitor();
    }

    stopMemoryMonitoring() {
        this.isMonitoring = false;
        
        if (this.memoryData.length === 0) return { avg: 0, max: 0, min: 0, samples: 0 };
        
        const heapUsages = this.memoryData.map(d => d.heapUsed);
        return {
            avg: heapUsages.reduce((sum, val) => sum + val, 0) / heapUsages.length,
            max: Math.max(...heapUsages),
            min: Math.min(...heapUsages),
            samples: heapUsages.length
        };
    }

    // Enhanced benchmark test with failure handling
    async benchmarkTest(testSuite, testName) {
        console.log(`\n🔬 BENCHMARKING: ${testSuite.name}`);
        console.log('='.repeat(60));
        
        // Check failure threshold before starting
        if (this.checkFailureThreshold()) {
            this.results.summary.testsSkipped++;
            return null;
        }

        // Validate test file
        const fileInfo = this.validateTestFile(testSuite);
        if (!fileInfo) {
            console.log(`❌ Skipping ${testSuite.name} - no valid test file found`);
            this.results.summary.testsSkipped++;
            return null;
        }

        const iterations = BENCHMARK_CONFIG.iterations;
        const execTimes = [];
        const memoryStats = [];
        const errors = [];
        let successfulRuns = 0;

        for (let i = 0; i < iterations; i++) {
            console.log(`  Iteration ${i + 1}/${iterations}...`);
            
            // Check failure threshold before each iteration
            if (this.checkFailureThreshold()) {
                break;
            }
            
            try {
                this.startMemoryMonitoring();
                const startTime = performance.now();
                
                // Execute with timeout and proper error handling
                const output = execSync(`node "${fileInfo.file}"`, {
                    encoding: 'utf8',
                    timeout: BENCHMARK_CONFIG.timeoutMs,
                    cwd: process.cwd(),
                    stdio: ['pipe', 'pipe', 'pipe']
                });
                
                const endTime = performance.now();
                const execTime = endTime - startTime;
                const memoryStats_iteration = this.stopMemoryMonitoring();
                
                execTimes.push(execTime);
                memoryStats.push(memoryStats_iteration);
                successfulRuns++;
                
                console.log(`    ✅ Execution Time: ${execTime.toFixed(2)}ms`);
                console.log(`    💾 Peak Memory: ${memoryStats_iteration.max.toFixed(2)}MB`);
                
            } catch (error) {
                this.stopMemoryMonitoring();
                this.globalFailureCount++;
                
                const errorMsg = error.message.substring(0, 100) + (error.message.length > 100 ? '...' : '');
                console.log(`    ❌ Error: ${errorMsg}`);
                errors.push(errorMsg);
                
                // Initialize failure count for this test
                if (!this.results.failures.byTest[testName]) {
                    this.results.failures.byTest[testName] = 0;
                }
                this.results.failures.byTest[testName]++;
                
                // Check if this specific test has too many failures
                const testFailureRate = this.results.failures.byTest[testName] / (i + 1);
                if (testFailureRate >= BENCHMARK_CONFIG.failureThreshold) {
                    console.log(`    🚨 Test failure rate (${(testFailureRate * 100).toFixed(1)}%) exceeds threshold`);
                    console.log(`    🛑 Aborting remaining iterations for ${testSuite.name}`);
                    break;
                }
            }
        }

        // Calculate statistics only if we have successful runs
        if (successfulRuns === 0) {
            console.log(`    ❌ No successful runs for ${testSuite.name}`);
            this.results.summary.testsFailed++;
            return null;
        }

        const avgExecTime = execTimes.reduce((sum, time) => sum + time, 0) / execTimes.length;
        const minExecTime = Math.min(...execTimes);
        const maxExecTime = Math.max(...execTimes);
        const stdDevExecTime = Math.sqrt(execTimes.reduce((sum, time) => 
            sum + Math.pow(time - avgExecTime, 2), 0) / execTimes.length);
        
        const avgMemory = memoryStats.reduce((sum, mem) => sum + mem.avg, 0) / memoryStats.length;
        const maxMemory = Math.max(...memoryStats.map(mem => mem.max));
        
        // Performance assessment
        const threshold = BENCHMARK_CONFIG.performanceThresholds[testName] || 
                         { maxTime: 10000, maxMemory: 200 };
        const timeScore = Math.max(0, (threshold.maxTime - avgExecTime) / threshold.maxTime * 100);
        const memoryScore = Math.max(0, (threshold.maxMemory - maxMemory) / threshold.maxMemory * 100);
        const overallScore = (timeScore + memoryScore) / 2;
        
        const benchmark = {
            testSuite: testSuite.name,
            file: fileInfo.file,
            isFallback: fileInfo.isFallback,
            execution: {
                iterations: successfulRuns,
                avgTime: avgExecTime,
                minTime: minExecTime,
                maxTime: maxExecTime,
                stdDev: stdDevExecTime,
                variancePercent: (stdDevExecTime / avgExecTime) * 100
            },
            memory: {
                avgUsage: avgMemory,
                maxUsage: maxMemory,
                samples: memoryStats.reduce((sum, mem) => sum + mem.samples, 0)
            },
            performance: {
                timeScore: timeScore,
                memoryScore: memoryScore,
                overallScore: overallScore,
                meetsThresholds: timeScore > 50 && memoryScore > 50
            },
            errors: errors,
            successRate: (successfulRuns / iterations) * 100
        };

        this.results.summary.testsRun++;
        console.log(`\n📊 BENCHMARK RESULTS:`);
        console.log(`    ⏱️  Average Time: ${avgExecTime.toFixed(2)}ms`);
        console.log(`    💾 Peak Memory: ${maxMemory.toFixed(2)}MB`);
        console.log(`    📈 Performance Score: ${overallScore.toFixed(1)}%`);
        console.log(`    ✅ Success Rate: ${benchmark.successRate.toFixed(1)}%`);

        return benchmark;
    }

    // Run comprehensive benchmarks with failure handling
    async runComprehensiveBenchmarks() {
        console.log('\n🚀 ENHANCED PERFORMANCE BENCHMARK SUITE');
        console.log('=' .repeat(80));
        console.log(`Agent: ${this.results.agent}`);
        console.log(`Timestamp: ${this.results.timestamp}`);
        console.log(`Max Failures: ${BENCHMARK_CONFIG.maxFailures}`);
        console.log(`Failure Threshold: ${(BENCHMARK_CONFIG.failureThreshold * 100).toFixed(1)}%`);
        console.log('=' .repeat(80));

        const startTime = performance.now();
        
        for (const [testName, testSuite] of Object.entries(TEST_SUITES)) {
            // Check global failure threshold
            if (this.checkFailureThreshold()) {
                console.log('\n🛑 BENCHMARK SUITE ABORTED DUE TO EXCESSIVE FAILURES');
                break;
            }
            
            const benchmark = await this.benchmarkTest(testSuite, testName);
            if (benchmark) {
                this.results.benchmarks[testName] = benchmark;
            }
        }

        const totalTime = performance.now() - startTime;
        this.results.summary.totalExecutionTime = totalTime;

        // Calculate summary statistics
        const benchmarks = Object.values(this.results.benchmarks);
        if (benchmarks.length > 0) {
            this.results.summary.averageMemoryUsage = 
                benchmarks.reduce((sum, b) => sum + b.memory.maxUsage, 0) / benchmarks.length;
            this.results.summary.performanceScore = 
                benchmarks.reduce((sum, b) => sum + b.performance.overallScore, 0) / benchmarks.length;
        }

        this.results.failures.total = this.globalFailureCount;
        this.results.summary.recommendations = this.generateOptimizationRecommendations(this.results.benchmarks);

        // Generate final report
        this.generateFinalReport();
        
        return this.results;
    }

    generateOptimizationRecommendations(benchmarks) {
        const recommendations = [];
        
        // Global failure analysis
        if (this.globalFailureCount > 0) {
            recommendations.push({
                category: 'System Stability',
                priority: 'CRITICAL',
                description: `${this.globalFailureCount} test failures detected`,
                action: 'Review error logs, fix missing dependencies, validate file paths',
                impact: 'HIGH'
            });
        }

        // Performance analysis
        const slowTests = Object.entries(benchmarks).filter(([name, benchmark]) => 
            !benchmark.performance.meetsThresholds);
        
        if (slowTests.length > 0) {
            recommendations.push({
                category: 'Performance Optimization',
                priority: 'HIGH',
                description: `${slowTests.length} test suites exceed performance thresholds`,
                action: 'Optimize algorithms, implement caching, reduce computational complexity',
                affected: slowTests.map(([name]) => name)
            });
        }

        // Memory optimization
        const memoryIntensiveTests = Object.entries(benchmarks).filter(([name, benchmark]) => 
            benchmark.memory.maxUsage > 100);
        
        if (memoryIntensiveTests.length > 0) {
            recommendations.push({
                category: 'Memory Optimization',
                priority: 'MEDIUM',
                description: `${memoryIntensiveTests.length} test suites use >100MB memory`,
                action: 'Implement memory pooling, reduce data structures, optimize garbage collection',
                affected: memoryIntensiveTests.map(([name]) => name)
            });
        }

        return recommendations;
    }

    generateFinalReport() {
        console.log('\n📋 FINAL BENCHMARK REPORT');
        console.log('=' .repeat(80));
        console.log(`Total Execution Time: ${(this.results.summary.totalExecutionTime / 1000).toFixed(2)}s`);
        console.log(`Tests Run: ${this.results.summary.testsRun}`);
        console.log(`Tests Skipped: ${this.results.summary.testsSkipped}`);
        console.log(`Tests Failed: ${this.results.summary.testsFailed}`);
        console.log(`Global Failures: ${this.results.failures.total}/${this.results.failures.threshold}`);
        console.log(`Average Performance Score: ${this.results.summary.performanceScore.toFixed(1)}%`);
        console.log(`Average Memory Usage: ${this.results.summary.averageMemoryUsage.toFixed(1)}MB`);
        
        if (this.results.summary.recommendations.length > 0) {
            console.log('\n🔧 OPTIMIZATION RECOMMENDATIONS:');
            this.results.summary.recommendations.forEach((rec, i) => {
                console.log(`${i + 1}. [${rec.priority}] ${rec.category}: ${rec.description}`);
                console.log(`   Action: ${rec.action}`);
            });
        }

        // Save results to file
        const resultsPath = `test/results/enhanced-benchmark-results-${Date.now()}.json`;
        const resultsDir = path.dirname(resultsPath);
        if (!fs.existsSync(resultsDir)) {
            fs.mkdirSync(resultsDir, { recursive: true });
        }
        
        fs.writeFileSync(resultsPath, JSON.stringify(this.results, null, 2));
        console.log(`\n💾 Results saved to: ${resultsPath}`);
        
        // Determine overall success
        const successRate = (this.results.summary.testsRun / Object.keys(TEST_SUITES).length) * 100;
        if (successRate >= 80 && this.results.failures.total < BENCHMARK_CONFIG.maxFailures) {
            console.log('\n✅ BENCHMARK SUITE COMPLETED SUCCESSFULLY');
        } else {
            console.log('\n⚠️  BENCHMARK SUITE COMPLETED WITH ISSUES');
        }
    }
}

// Main execution
async function main() {
    const suite = new EnhancedPerformanceBenchmarkSuite();
    
    try {
        await suite.runComprehensiveBenchmarks();
        process.exit(0);
    } catch (error) {
        console.error('\n❌ BENCHMARK SUITE FATAL ERROR:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { EnhancedPerformanceBenchmarkSuite, BENCHMARK_CONFIG, TEST_SUITES }; 