#!/usr/bin/env node
/**
 * 🚨 WARNING: SCIENTIFIC INTEGRITY REVIEW IN PROGRESS 🚨
 * This test suite (test/gravitational-wave-validation-suite.js) is currently
 * under review for scientific integrity. Its methodologies, particularly
 * those related to "confidence" scores, "validation thresholds", and
 * "mathematical proofs" of resonance or coupling, may rely on circular
 * reasoning or arbitrary parameter choices.
 *
 * Claims of "validation", "detection", or "confidence" based on this script
 * in its current form may NOT be scientifically sound. The script likely
 * tests internal consistency of its models and configurations rather than
 * providing independent validation against empirical data or established
 * physical theories.
 *
 * This file requires significant refactoring to align with proper scientific
 * methodology as outlined in the SCIENTIFIC_INTEGRITY_RESTORATION_PLAN.md.
 * Do not interpret its outputs as scientifically validated conclusions without
 * critical re-evaluation.
 */
/**
 * Gravitational Wave Resonance Detection - Automated Validation Suite
 * Issue #5 Implementation - Autonomous Testing Protocol
 * 
 * This script provides comprehensive automated validation of gravitational wave
 * resonance patterns, musical frequency correlations, and bio-cosmic coupling
 * using headless testing and mathematical proof generation.
 */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

// Check for stress test command-line argument
const STRESS_TEST_ENABLED = process.argv.includes('--stress-test');

// Configuration
const CONFIG = {
    testSuites: {
        musicalHarmonicDetection: true,
        bioCosmicCoupling: true,
        resonancePatternRecognition: true,
        ligoDataAnalysis: true,
        statisticalValidation: true
    },
    
    musicalFrequencies: {
        'C2': 65.41,
        'E2': 82.41,
        'G2': 98.00,
        'C3': 130.81
    },
    
    bioFrequencies: {
        'heartRate': 72, // BPM
        'alpha': 10.5,   // Hz (8-13 Hz range)
        'beta': 21.5,    // Hz (13-30 Hz range)
        'circadian': 1/(24*3600) // Hz (24 hour cycle)
    },
    
    gravitationalWaveParameters: {
        sampleRate: 4096, // Hz (LIGO sampling rate)
        duration: 10, // seconds
        frequencyRange: [10, 1000], // Hz
        snrThreshold: 4.5,
        chirpRateThreshold: 10.0
    },
    
    validationThresholds: {
        musicalHarmonicConfidence: 75,
        bioCosmicCouplingConfidence: 70,
        resonancePatternConfidence: 80,
        ligoAnalysisConfidence: 85,
        overallConfidence: 75
    },
    
    outputDirectory: './test-results',
    reportFormat: 'markdown',
    stressTestParameters: {
        enabled: STRESS_TEST_ENABLED,
        durationMultiplier: 5, 
        sampleRateMultiplier: 1, 
        noiseLevelMultiplier: 2, 
    }
};

// Global test data
let testResults = {
    timestamp: new Date().toISOString(),
    testSuites: {},
    overallResults: {},
    internalCalculationSummaries: [],
    validationStatus: 'RUNNING'
};

/**
 * Main test execution function
 */
async function runGravitationalWaveValidationSuite() {
    console.log('=== GRAVITATIONAL WAVE RESONANCE DETECTION VALIDATION SUITE ===');
    console.log(`Timestamp: ${testResults.timestamp}`);
    console.log('Testing gravitational wave musical frequency and bio-cosmic correlations...\n');
    
    try {
        // Initialize test environment
        await initializeTestEnvironment();
        
        // Run all test suites
        if (CONFIG.testSuites.musicalHarmonicDetection) {
            await runMusicalHarmonicDetectionTests();
        }
        
        if (CONFIG.testSuites.bioCosmicCoupling) {
            await runBioCosmicCouplingTests();
        }
        
        if (CONFIG.testSuites.resonancePatternRecognition) {
            await runResonancePatternRecognitionTests();
        }
        
        if (CONFIG.testSuites.ligoDataAnalysis) {
            await runLIGODataAnalysisTests();
        }
        
        if (CONFIG.testSuites.statisticalValidation) {
            await runStatisticalValidationTests();
        }
        
        // Calculate overall results
        calculateOverallResults();
        
        // Generate mathematical proofs
        generateInternalSummaryPoints();
        
        // Generate final report
        await generateValidationReport();
        
        // Display results
        displayResults();
        
    } catch (error) {
        console.error('❌ Test suite failed:', error.message);
        testResults.validationStatus = 'FAILED';
        testResults.error = error.message;
    }
}

/**
 * Initialize test environment
 */
async function initializeTestEnvironment() {
    console.log('🔧 Initializing gravitational wave test environment...');
    
    // Create output directory
    if (!fs.existsSync(CONFIG.outputDirectory)) {
        fs.mkdirSync(CONFIG.outputDirectory, { recursive: true });
    }
    
    // Generate synthetic gravitational wave data
    generateSyntheticGravitationalWaveData();
    
    console.log('✓ Gravitational wave test environment initialized');
}

/**
 * Generate synthetic gravitational wave data for testing
 */
function generateSyntheticGravitationalWaveData() {
    const waveData = [];
    const sampleRate = CONFIG.gravitationalWaveParameters.sampleRate;
    const duration = CONFIG.gravitationalWaveParameters.duration;
    const numSamples = sampleRate * duration;
    
    for (let i = 0; i < numSamples; i++) {
        const time = i / sampleRate;
        
        // Base gravitational wave signal (chirp-like)
        const frequency = 50 + 200 * Math.pow(time / duration, 3);
        const amplitude = Math.exp(-time / 2) * (1 + 0.1 * Math.sin(2 * Math.PI * frequency * time));
        
        // Calculate musical component using existing utility
        const musicalComponent = getMusicalProximity(frequency); 
        
        // Combine base signal with noise
        const noise = (Math.random() - 0.5) * 0.02;
        const signal = amplitude + noise; 
        
        waveData.push({
            time: time,
            amplitude: signal,
            frequency: frequency,
            musicalComponent: musicalComponent // Store musical component
        });
    }
    
    // Store test data globally
    global.testGravitationalWaveData = waveData;
    
    console.log(`✓ Generated ${waveData.length} gravitational wave data points`);
}

/**
 * Test Suite 1: Musical Harmonic Detection
 */
async function runMusicalHarmonicDetectionTests() {
    console.log('\n🎵 Running Musical Harmonic Detection Tests (Internal Checks)...');
    console.warn("   ℹ️ This suite calculates internal consistency metrics. It does NOT provide scientific validation of harmonic detection.");
    const startTime = performance.now();
    
    const results = {
        harmonicStrengthAnalysis: await testHarmonicStrengthAnalysis(),
        harmonicCoherenceValidation: await testHarmonicCoherenceValidation(),
        frequencyProximityTesting: await testFrequencyProximityTesting(),
        musicalRatioDetection: await testMusicalRatioDetection()
    };
    
    const internalMetricScore = calculateMusicalHarmonicConfidence(results);
    // results.confidence = confidence; // SIRP: Removed misleading confidence assignment
    results.internal_metric_score = internalMetricScore; // Store for transparency
    results.executionTime = performance.now() - startTime;
    results.status = 'INFO_ONLY'; // SIRP: Status changed from PASSED/FAILED to INFO_ONLY
    
    testResults.testSuites.musicalHarmonicDetection = results;
    
    console.log(`✓ Musical Harmonic Detection Internal Checks Complete. Status: ${results.status} (Internal Metric Score: ${internalMetricScore.toFixed(1)})`);
    console.warn(`   🚨 The 'Internal Metric Score' is NOT a scientific confidence value.`);
}

async function testHarmonicStrengthAnalysis() {
    let totalStrength = 0;
    let count = 0;
    
    for (const dataPoint of global.testGravitationalWaveData) {
        const proximity = getMusicalProximity(dataPoint.frequency);
        if (proximity > 0.5) {
            totalStrength += dataPoint.amplitude * proximity;
            count++;
        }
    }
    
    const averageStrength = count > 0 ? totalStrength / count : 0;
    
    return {
        averageHarmonicStrength: averageStrength,
        harmonicCount: count,
        validation: averageStrength > 0.1
    };
}

async function testHarmonicCoherenceValidation() {
    const coherenceScores = [];
    
    for (const [note, freq] of Object.entries(CONFIG.musicalFrequencies)) {
        let coherenceSum = 0;
        let validCount = 0;
        
        for (const dataPoint of global.testGravitationalWaveData) {
            const freqDiff = Math.abs(dataPoint.frequency - freq);
            if (freqDiff < 10) {
                coherenceSum += Math.max(0, 1 - freqDiff / 10) * dataPoint.amplitude;
                validCount++;
            }
        }
        
        const coherence = validCount > 0 ? coherenceSum / validCount : 0;
        coherenceScores.push(coherence);
    }
    
    const avgCoherence = coherenceScores.length > 0 ? 
        coherenceScores.reduce((sum, val) => sum + val, 0) / coherenceScores.length : 0;
    
    return {
        coherenceByFrequency: coherenceScores,
        averageCoherence: avgCoherence,
        validation: avgCoherence > 0.05
    };
}

async function testFrequencyProximityTesting() {
    let proximitySum = 0;
    let count = 0;
    
    for (const dataPoint of global.testGravitationalWaveData) {
        const musicalProximity = getMusicalProximity(dataPoint.frequency);
        proximitySum += musicalProximity;
        count++;
    }
    
    const averageProximity = count > 0 ? proximitySum / count : 0;
    
    return {
        averageProximity: averageProximity,
        samplesAnalyzed: count,
        validation: averageProximity > 0.2
    };
}

async function testMusicalRatioDetection() {
    // Placeholder for musical ratio detection (e.g., 3:2, 4:3)
    // This would involve more complex spectral analysis and peak finding
    // For now, returning a dummy result
    return {
        detectedRatios: [],
        ratioConfidence: 0, // Placeholder
        validation: false
    };
}

function calculateMusicalHarmonicConfidence(results) {
    console.warn("   ⚠️ calculateMusicalHarmonicConfidence: The calculated 'confidence' is an internal composite metric based on arbitrary thresholds and weightings. It is NOT a statistical confidence level nor a measure of scientific validation.");
    // Simplified confidence calculation based on sub-test results
    let totalWeightedScore = 0;
    let totalWeight = 0;

    const strengthWeight = 2;
    const coherenceWeight = 3;
    const proximityWeight = 1;
    const ratioWeight = 1; // Placeholder weight

    if (results.harmonicStrengthAnalysis && results.harmonicStrengthAnalysis.validation) {
        totalWeightedScore += (results.harmonicStrengthAnalysis.averageHarmonicStrength * 100) * strengthWeight; 
    }
    totalWeight += 100 * strengthWeight; // Max possible score for this part if validation is true

    if (results.harmonicCoherenceValidation && results.harmonicCoherenceValidation.averageCoherence) {
        totalWeightedScore += results.harmonicCoherenceValidation.averageCoherence * 100 * coherenceWeight;
    }
    totalWeight += 100 * coherenceWeight;

    if (results.frequencyProximityTesting && results.frequencyProximityTesting.averageProximity) {
        totalWeightedScore += results.frequencyProximityTesting.averageProximity * 100 * proximityWeight;
    }
    totalWeight += 100 * proximityWeight;

    if (results.musicalRatioDetection && results.musicalRatioDetection.ratioConfidence) {
        totalWeightedScore += results.musicalRatioDetection.ratioConfidence * 100 * ratioWeight;
    }
    totalWeight += 100 * ratioWeight;

    const internal_metric_score = totalWeight > 0 ? (totalWeightedScore / totalWeight) * 100 : 0;
    return Math.min(100, Math.max(0, internal_metric_score)); // Cap at 0-100
}

/**
 * Test Suite 2: Bio-Cosmic Coupling
 */
async function runBioCosmicCouplingTests() {
    console.log('\n🧬 Running Bio-Cosmic Coupling Tests (Internal Checks)...');
    console.warn("   ℹ️ This suite calculates internal consistency metrics. It does NOT provide scientific validation of bio-cosmic coupling.");
    const startTime = performance.now();
    
    const results = {
        heartRateCorrelation: await testHeartRateCorrelationAnalysis(),
        brainwaveDetection: await testBrainwaveFrequencyDetection(),
        circadianRhythmCorrelation: await testCircadianRhythmCorrelation(),
        biologicalHarmonicResonance: await testBiologicalHarmonicResonance()
    };
    
    const internalMetricScore = calculateBioCosmicCouplingConfidence(results);
    // results.confidence = confidence; // SIRP: Removed misleading confidence assignment
    results.internal_metric_score = internalMetricScore; // Store for transparency
    results.executionTime = performance.now() - startTime;
    results.status = 'INFO_ONLY'; // SIRP: Status changed from PASSED/FAILED to INFO_ONLY
    
    testResults.testSuites.bioCosmicCoupling = results;
    
    console.log(`✓ Bio-Cosmic Coupling Internal Checks Complete. Status: ${results.status} (Internal Metric Score: ${internalMetricScore.toFixed(1)})`);
    console.warn(`   🚨 The 'Internal Metric Score' is NOT a scientific confidence value.`);
}

async function testHeartRateCorrelationAnalysis() {
    const heartRateFreq = CONFIG.bioFrequencies.heartRate / 60; // Convert BPM to Hz
    let correlationSum = 0;
    let count = 0;
    
    for (const dataPoint of global.testGravitationalWaveData) {
        const bioProximity = getBioProximity(dataPoint.frequency);
        if (bioProximity > 0.3) {
            correlationSum += dataPoint.amplitude * bioProximity;
            count++;
        }
    }
    
    const correlation = count > 0 ? correlationSum / count : 0;
    
    return {
        heartRateCorrelation: correlation,
        correlatedSamples: count,
        validation: Math.abs(correlation) > 0.01
    };
}

async function testBrainwaveFrequencyDetection() {
    const brainwaveFreqs = [CONFIG.bioFrequencies.alpha, CONFIG.bioFrequencies.beta];
    let detectionScore = 0;
    let totalTests = 0;
    
    for (const freq of brainwaveFreqs) {
        let proximitySum = 0;
        let count = 0;
        
        for (const dataPoint of global.testGravitationalWaveData) {
            const freqDiff = Math.abs(dataPoint.frequency - freq);
            if (freqDiff < 5) {
                proximitySum += Math.max(0, 1 - freqDiff / 5);
                count++;
            }
        }
        
        if (count > 0) {
            detectionScore += proximitySum / count;
        }
        totalTests++;
    }
    
    const averageDetection = totalTests > 0 ? detectionScore / totalTests : 0;
    
    return {
        brainwaveDetectionScore: averageDetection,
        frequenciesTested: brainwaveFreqs,
        validation: averageDetection > 0.1
    };
}

async function testCircadianRhythmCorrelation() {
    const circadianFreq = CONFIG.bioFrequencies.circadian;
    let correlationSum = 0;
    let count = 0;
    
    // Since circadian frequency is very low, we look for long-term patterns
    for (let i = 0; i < global.testGravitationalWaveData.length; i += 1000) {
        const dataPoint = global.testGravitationalWaveData[i];
        if (dataPoint) {
            const circadianComponent = Math.sin(2 * Math.PI * circadianFreq * dataPoint.time);
            correlationSum += dataPoint.amplitude * circadianComponent;
            count++;
        }
    }
    
    const correlation = count > 0 ? Math.abs(correlationSum / count) : 0;
    
    return {
        circadianCorrelation: correlation,
        samplesAnalyzed: count,
        validation: correlation > 0.001
    };
}

async function testBiologicalHarmonicResonance() {
    const bioFreqs = Object.values(CONFIG.bioFrequencies);
    let resonanceScore = 0;
    let totalTests = 0;
    
    for (const bioFreq of bioFreqs) {
        if (bioFreq > 0.001) { // Skip very low frequencies
            let harmonicSum = 0;
            let count = 0;
            
            for (const dataPoint of global.testGravitationalWaveData) {
                // Check for harmonic relationships (2x, 3x, 0.5x frequencies)
                const harmonics = [bioFreq * 2, bioFreq * 3, bioFreq * 0.5];
                for (const harmonic of harmonics) {
                    const freqDiff = Math.abs(dataPoint.frequency - harmonic);
                    if (freqDiff < 10) {
                        harmonicSum += Math.max(0, 1 - freqDiff / 10) * dataPoint.amplitude;
                        count++;
                    }
                }
            }
            
            if (count > 0) {
                resonanceScore += harmonicSum / count;
            }
            totalTests++;
        }
    }
    
    const averageResonance = totalTests > 0 ? resonanceScore / totalTests : 0;
    
    return {
        biologicalResonanceScore: averageResonance,
        frequenciesTested: bioFreqs.filter(f => f > 0.001),
        validation: averageResonance > 0.05
    };
}

function calculateBioCosmicCouplingConfidence(results) {
    console.warn("   ⚠️ calculateBioCosmicCouplingConfidence: The calculated value is an internal composite metric based on arbitrary thresholds and weightings. It is NOT a statistical confidence level nor a measure of scientific validation.");
    // Example confidence calculation - actual logic would be more complex
    let score = 0;
    if (results.heartRateCorrelation && results.heartRateCorrelation.correlation > 0.1) score += 25;
    if (results.brainwaveDetection && results.brainwaveDetection.brainwaveDetectionScore > 0.15) score += 25;
    if (results.circadianRhythmCorrelation && results.circadianRhythmCorrelation.correlationFactor > 0.05) score += 25;
    if (results.biologicalHarmonicResonance && results.biologicalHarmonicResonance.avgResonance > 0.2) score += 25;
    
    // Apply stress test penalty if enabled and significant degradation
    if (CONFIG.stressTestParameters.enabled && results.heartRateCorrelation && results.heartRateCorrelation.stressTestDegradation > 0.3) {
        score *= 0.8; // Penalize if stress test shows high degradation
    }
    const internal_metric_score = Math.max(0, Math.min(100, score));
    return internal_metric_score;
}

/**
 * Test Suite 3: Resonance Pattern Recognition
 */
async function runResonancePatternRecognitionTests() {
    console.log('\n🌊 Running Resonance Pattern Recognition Tests (Internal Checks)...');
    console.warn("   ℹ️ This suite calculates internal consistency metrics. It does NOT provide scientific validation of resonance patterns.");
    const startTime = performance.now();
    
    const results = {
        standingWaveDetection: await testStandingWaveDetection(),
        resonanceNodeIdentification: await testResonanceNodeIdentification(),
        patternCoherenceAnalysis: await testPatternCoherenceAnalysis(),
        cosmicScaleCorrelation: await testCosmicScaleCorrelation()
    };
    
    const internalMetricScore = calculateResonancePatternConfidence(results);
    // results.confidence = confidence; // SIRP: Removed misleading confidence assignment
    results.internal_metric_score = internalMetricScore; // Store for transparency
    results.executionTime = performance.now() - startTime;
    results.status = 'INFO_ONLY'; // SIRP: Status changed from PASSED/FAILED to INFO_ONLY
    
    testResults.testSuites.resonancePatternRecognition = results;
    
    console.log(`✓ Resonance Pattern Recognition Internal Checks Complete. Status: ${results.status} (Internal Metric Score: ${internalMetricScore.toFixed(1)})`);
    console.warn(`   🚨 The 'Internal Metric Score' is NOT a scientific confidence value.`);
}

async function testStandingWaveDetection() {
    const amplitudes = global.testGravitationalWaveData.map(d => d.amplitude);
    const nodes = findNodes(amplitudes);
    const antinodes = findAntinodes(amplitudes);
    
    const standingWaveIndicator = nodes.length > 0 && antinodes.length > 0 ? 
        (nodes.length + antinodes.length) / amplitudes.length : 0;
    
    return Math.max(0, Math.min(100, standingWaveIndicator)); // Cap at 0-100
}

async function testResonanceNodeIdentification() {
    const frequencies = global.testGravitationalWaveData.map(d => d.frequency);
    const amplitudes = global.testGravitationalWaveData.map(d => d.amplitude);
    
    const coherence = calculatePatternCoherence(amplitudes, frequencies);
    const nodes = findNodes(amplitudes);
    
    return {
        nodeAccuracy: nodes.length / frequencies.length,
        patternCoherence: coherence,
        nodesIdentified: nodes.length,
        validation: coherence > 0.3 && nodes.length > 10
    };
}

async function testPatternCoherenceAnalysis() {
    const frequencies = global.testGravitationalWaveData.map(d => d.frequency);
    const amplitudes = global.testGravitationalWaveData.map(d => d.amplitude);
    
    const coherence = calculatePatternCoherence(amplitudes, frequencies);
    
    return {
        overallCoherence: coherence,
        samplesAnalyzed: frequencies.length,
        validation: coherence > 0.2
    };
}

async function testCosmicScaleCorrelation() {
    // Test correlation with cosmic-scale phenomena
    let correlationSum = 0;
    let count = 0;
    
    for (const dataPoint of global.testGravitationalWaveData) {
        // Simulate cosmic scale correlation
        const cosmicFactor = Math.sin(dataPoint.time * 0.1) * 0.1;
        correlationSum += dataPoint.amplitude * cosmicFactor;
        count++;
    }
    
    const correlation = count > 0 ? Math.abs(correlationSum / count) : 0;
    
    return {
        cosmicCorrelation: correlation,
        samplesAnalyzed: count,
        validation: correlation > 0.005
    };
}

function calculateResonancePatternConfidence(results) {
    console.warn("   ⚠️ calculateResonancePatternConfidence: The calculated value is an internal composite metric based on arbitrary thresholds and sub-test validations. It is NOT a statistical confidence level nor a measure of scientific validation.");
    let internal_metric_score = 0;
    
    if (results.standingWaveDetection.validation) internal_metric_score += 25;
    if (results.resonanceNodeIdentification.validation) internal_metric_score += 25;
    if (results.patternCoherenceAnalysis.validation) internal_metric_score += 25;
    if (results.cosmicScaleCorrelation.validation) internal_metric_score += 25;
    
    return internal_metric_score; 
}

/**
 * Test Suite 4: LIGO Data Analysis
 */
async function runLIGODataAnalysisTests() {
    console.log('\n🛰️ Running LIGO Data Analysis (Internal Checks)...');
    console.warn("   ℹ️ This suite calculates internal consistency metrics. It does NOT provide scientific validation of LIGO data interpretations.");
    const startTime = performance.now();

    const results = {
        snrAnalysis: await testSignalToNoiseRatioAnalysis(),
        chirpRateDetection: await testChirpRateDetection(),
        mergerProbability: await testMergerProbabilityCalculation(),
        sourceDistanceEstimation: await testSourceDistanceEstimation()
    };

    const internalMetricScore = calculateLIGOAnalysisConfidence(results);
    // results.confidence = confidence; // SIRP: Removed misleading confidence assignment
    results.internal_metric_score = internalMetricScore; // Store for transparency
    results.executionTime = performance.now() - startTime;
    results.status = 'INFO_ONLY'; // SIRP: Status changed from PASSED/FAILED to INFO_ONLY

    testResults.testSuites.ligoDataAnalysis = results;

    console.log(`✓ LIGO Data Analysis Internal Checks Complete. Status: ${results.status} (Internal Metric Score: ${internalMetricScore.toFixed(1)})`);
    console.warn(`   🚨 The 'Internal Metric Score' is NOT a scientific confidence value.`);
}

async function testSignalToNoiseRatioAnalysis() {
    let signalSum = 0;
    let noiseSum = 0;
    let count = 0;
    
    for (const dataPoint of global.testGravitationalWaveData) {
        signalSum += Math.abs(dataPoint.amplitude);
        noiseSum += 0.02; // Noise level from generation
        count++;
    }
    
    const avgSignal = count > 0 ? signalSum / count : 0;
    const avgNoise = count > 0 ? noiseSum / count : 0.02;
    const snr = avgNoise > 0 ? avgSignal / avgNoise : 0;
    
    return {
        snr: snr,
        averageSignal: avgSignal,
        averageNoise: avgNoise,
        maxAmplitude: Math.max(...global.testGravitationalWaveData.map(d => Math.abs(d.amplitude))),
        validation: snr >= CONFIG.gravitationalWaveParameters.snrThreshold
    };
}

async function testChirpRateDetection() {
    let totalChirpRate = 0;
    let count = 0;
    
    for (let i = 1; i < global.testGravitationalWaveData.length; i++) {
        const data = global.testGravitationalWaveData[i];
        const prevData = global.testGravitationalWaveData[i - 1];
        
        const freqChange = data.frequency - prevData.frequency;
        const timeChange = data.time - prevData.time;
        
        if (timeChange > 0) {
            totalChirpRate += freqChange / timeChange;
            count++;
        }
    }
    
    const averageChirpRate = count > 0 ? totalChirpRate / count : 0;
    
    return {
        averageChirpRate: Math.abs(averageChirpRate),
        chirpRateThreshold: CONFIG.gravitationalWaveParameters.chirpRateThreshold,
        validation: Math.abs(averageChirpRate) >= CONFIG.gravitationalWaveParameters.chirpRateThreshold
    };
}

async function testMergerProbabilityCalculation() {
    const snrResult = await testSignalToNoiseRatioAnalysis();
    const chirpResult = await testChirpRateDetection();
    
    let mergerProbability = 0;
    
    if (chirpResult.averageChirpRate > CONFIG.gravitationalWaveParameters.chirpRateThreshold && 
        snrResult.snr > CONFIG.gravitationalWaveParameters.snrThreshold) {
        mergerProbability = Math.min(100, 
            (chirpResult.averageChirpRate / 50 + snrResult.snr / 20) * 50);
    }
    
    return {
        mergerProbability: mergerProbability,
        basedOnChirpRate: chirpResult.averageChirpRate,
        basedOnSNR: snrResult.snr,
        validation: mergerProbability > 10 // Original validation condition kept
    };
}

async function testSourceDistanceEstimation() {
    const snrResult = await testSignalToNoiseRatioAnalysis();
    const sourceDistance = snrResult.maxAmplitude > 0 ? 100 / snrResult.maxAmplitude : 200; 
    
    const estimatedDistanceClamped = Math.min(500, Math.max(50, sourceDistance));

    return {
        estimatedDistance: estimatedDistanceClamped, 
        basedOnAmplitude: snrResult.maxAmplitude,
        distanceUnit: 'Mpc',
        validation: estimatedDistanceClamped >= 10 && estimatedDistanceClamped <= 1000 
    };
}

function calculateLIGOAnalysisConfidence(results) {
    console.warn("   ⚠️ calculateLIGOAnalysisConfidence: The calculated value is an internal composite metric based on arbitrary thresholds and sub-test validations. It is NOT a statistical confidence level nor a measure of scientific validation.");
    let internal_metric_score = 0;
    if (results.signalToNoiseRatioAnalysis.validation) internal_metric_score += 25;
    if (results.chirpRateDetection.validation) internal_metric_score += 25;
    if (results.mergerProbabilityCalculation.mergerProbability > 50) internal_metric_score += 25; // Pass if probability > 50%
    if (results.sourceDistanceEstimation.validation) internal_metric_score += 25;
    
    return internal_metric_score; 
}

/**
 * Test Suite 5: Statistical Validation
 */
async function runStatisticalValidationTests() {
    console.log('\n📊 Running Statistical Validation Tests (Internal Checks)...');
    console.warn("   ℹ️ This suite calculates internal consistency metrics. It does NOT provide scientific validation.");
    const startTime = performance.now();

    const results = {
        correlationAnalysis: await performCorrelationAnalysis(),
        frequencyDistribution: await performFrequencyDistributionAnalysis(),
        amplitudeStatistics: await performAmplitudeStatistics(),
        temporalPatternAnalysis: await performTemporalPatternAnalysis()
    };
    
    const internalMetricScore = calculateStatisticalConfidence(results);
    // results.confidence = confidence; // SIRP: Removed misleading confidence assignment
    results.internal_metric_score = internalMetricScore; // Store for transparency
    results.executionTime = performance.now() - startTime;
    results.status = 'INFO_ONLY'; // SIRP: Status changed from PASSED/FAILED to INFO_ONLY
    
    testResults.testSuites.statisticalValidation = results;
    
    console.log(`✓ Statistical Validation Internal Checks Complete. Status: ${results.status} (Internal Metric Score: ${internalMetricScore.toFixed(1)})`);
    console.warn(`   🚨 The 'Internal Metric Score' is NOT a scientific confidence value.`);
}

function calculateStatisticalConfidence(results) {
    console.warn("   ⚠️ calculateStatisticalConfidence: The calculated value is an internal composite metric based on arbitrary thresholds and sub-test validations. It is NOT a statistical confidence level nor a measure of scientific validation.");
    let internal_metric_score = 0;
    if (results.correlationAnalysis.validation) internal_metric_score += 25;
    if (results.frequencyDistribution.validation) internal_metric_score += 25;
    if (results.amplitudeStatistics.validation) internal_metric_score += 25;
    if (results.temporalPatternAnalysis.validation) internal_metric_score += 25;

    return internal_metric_score;
}

function calculateStandardDeviation(values) {
    if (values.length === 0) return 0;
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + (val - mean) ** 2, 0) / values.length;
    return Math.sqrt(variance);
}

function getMusicalProximity(frequency) {
    let minDistance = Infinity;
    for (const freq of Object.values(CONFIG.musicalFrequencies)) {
        const distance = Math.abs(frequency - freq);
        minDistance = Math.min(minDistance, distance);
    }
    return Math.max(0, 1 - minDistance / 50); // Normalize proximity
}

function getBioProximity(frequency) {
    let minDistance = Infinity;
    for (const freq of Object.values(CONFIG.bioFrequencies)) {
        if (freq > 0.001) { // Skip very low frequencies
            const distance = Math.abs(frequency - freq);
            minDistance = Math.min(minDistance, distance);
        }
    }
    return Math.max(0, 1 - minDistance / 20); // Normalize proximity
}

function calculatePatternCoherence(amplitudes, frequencies) {
    if (amplitudes.length === 0) return 0;
    
    const ampStd = calculateStandardDeviation(amplitudes);
    const freqStd = calculateStandardDeviation(frequencies);
    const ampMean = amplitudes.reduce((sum, val) => sum + val, 0) / amplitudes.length;
    const freqMean = frequencies.reduce((sum, val) => sum + val, 0) / frequencies.length;
    
    // Coherence based on stability of patterns
    const ampCoherence = ampMean > 0 ? 1 - (ampStd / ampMean) : 0;
    const freqCoherence = freqMean > 0 ? 1 - (freqStd / freqMean) : 0;
    
    return Math.max(0, (ampCoherence + freqCoherence) / 2);
}

function findNodes(amplitudes) {
    const nodes = [];
    const threshold = 0.1; // Minimum amplitude for node detection
    
    for (let i = 1; i < amplitudes.length - 1; i++) {
        if (Math.abs(amplitudes[i]) < threshold &&
            Math.abs(amplitudes[i]) < Math.abs(amplitudes[i-1]) &&
            Math.abs(amplitudes[i]) < Math.abs(amplitudes[i+1])) {
            nodes.push(i);
        }
    }
    
    return nodes;
}

function findAntinodes(amplitudes) {
    const antinodes = [];
    const threshold = 0.5; // Minimum amplitude for antinode detection
    
    for (let i = 1; i < amplitudes.length - 1; i++) {
        if (Math.abs(amplitudes[i]) > threshold &&
            Math.abs(amplitudes[i]) > Math.abs(amplitudes[i-1]) &&
            Math.abs(amplitudes[i]) > Math.abs(amplitudes[i+1])) {
            antinodes.push(i);
        }
    }
    
    return antinodes;
}

async function performCorrelationAnalysis() {
    const amplitudes = global.testGravitationalWaveData.map(d => d.amplitude);
    const musicalComponents = global.testGravitationalWaveData.map(d => d.musicalComponent);
    
    let correlation = 0;
    if (amplitudes.length === musicalComponents.length && amplitudes.length > 0) {
        const ampMean = amplitudes.reduce((sum, val) => sum + val, 0) / amplitudes.length;
        const musMean = musicalComponents.reduce((sum, val) => sum + val, 0) / musicalComponents.length;
        
        let numerator = 0;
        let ampDenominator = 0;
        let musDenominator = 0;
        
        for (let i = 0; i < amplitudes.length; i++) {
            const ampDiff = amplitudes[i] - ampMean;
            const musDiff = musicalComponents[i] - musMean;
            numerator += ampDiff * musDiff;
            ampDenominator += ampDiff * ampDiff;
            musDenominator += musDiff * musDiff;
        }
        
        if (ampDenominator > 0 && musDenominator > 0) {
            correlation = numerator / Math.sqrt(ampDenominator * musDenominator);
        }
    }
    
    return {
        correlation: Math.abs(correlation),
        validation: Math.abs(correlation) > 0.1
    };
}

async function performFrequencyDistributionAnalysis() {
    const frequencies = global.testGravitationalWaveData.map(d => d.frequency);
    const mean = frequencies.reduce((sum, val) => sum + val, 0) / frequencies.length;
    const std = calculateStandardDeviation(frequencies);
    
    return {
        mean: mean,
        standardDeviation: std,
        distribution: 'normal',
        validation: std > 0 && mean > 0
    };
}

async function performAmplitudeStatistics() {
    const amplitudes = global.testGravitationalWaveData.map(d => Math.abs(d.amplitude));
    const mean = amplitudes.reduce((sum, val) => sum + val, 0) / amplitudes.length;
    const max = Math.max(...amplitudes);
    const min = Math.min(...amplitudes);
    const std = calculateStandardDeviation(amplitudes);
    
    return {
        mean: mean,
        maximum: max,
        minimum: min,
        standardDeviation: std,
        validation: mean > 0 && max > min
    };
}

async function performTemporalPatternAnalysis() {
    // Placeholder for temporal pattern analysis
    return { patternsFound: 0, patternMatchScore: 0, validation: false };
}

function calculateOverallResults() {
    console.warn("\n   ⚠️ Calculating Overall Results: The 'overall confidence' and 'validation status' are based on aggregated internal metrics and arbitrary thresholds. They DO NOT represent scientific validation.");
    let totalConfidence = 0;
    let numSuites = 0;
    let allSuitesInfoOnly = true;

    for (const suiteName in testResults.testSuites) {
        const suite = testResults.testSuites[suiteName];
        if (suite && typeof suite.internal_metric_score === 'number') { // Check for internal_metric_score
            totalConfidence += suite.internal_metric_score;
            numSuites++;
            if (suite.status !== 'INFO_ONLY') {
                allSuitesInfoOnly = false; // Should not happen if all are set to INFO_ONLY
            }
        } else if (suite && typeof suite.confidence === 'number') {
            // Fallback for any suites missed in refactor, though this path should ideally not be taken
            console.warn(`   🚨 Suite ${suiteName} still using legacy 'confidence' field. This should be updated to 'internal_metric_score'.`);
            totalConfidence += suite.confidence;
            numSuites++;
            if (suite.status !== 'INFO_ONLY') allSuitesInfoOnly = false;
        }
    }

    const overall_internal_metric_score = numSuites > 0 ? totalConfidence / numSuites : 0;
    // testResults.overallResults.confidence = overallConfidence; // SIRP: Removed
    testResults.overallResults.internal_metric_score = overall_internal_metric_score;
    
    // SIRP: Overall status is now based on processing, not arbitrary pass/fail of metrics.
    // If any individual suite failed to process (e.g. error state, not INFO_ONLY), then overall is affected.
    // For now, if all suites are INFO_ONLY, overall status is INFO_ONLY_PROCESSED.
    if (allSuitesInfoOnly && numSuites > 0) {
        testResults.validationStatus = 'INFO_ONLY_PROCESSED';
    } else if (numSuites === 0) {
        testResults.validationStatus = 'NO_TESTS_PROCESSED';
    } else {
        // This case implies some suites had a status other than INFO_ONLY, which means refactor is incomplete
        // or a suite truly failed to execute properly (not a metric failure, but an error).
        // The top-level try/catch in runGravitationalWaveValidationSuite handles actual errors.
        testResults.validationStatus = 'PROCESSING_INCONSISTENCIES_DETECTED'; 
        console.error("   🚨 PROCESSING_INCONSISTENCIES_DETECTED: Not all test suites have expected 'INFO_ONLY' status or 'internal_metric_score'. Review script.");
    }

    console.log(`\n📈 Overall Internal Metric Score: ${overall_internal_metric_score.toFixed(1)}`);
    console.log(`⚙️ Overall Processing Status: ${testResults.validationStatus}`);
    console.warn(`   🚨 The 'Overall Internal Metric Score' is an average of internal metrics and NOT a scientific confidence value.`);
}

function generateInternalSummaryPoints() {
    console.warn("   ⚠️ generateInternalSummaryPoints: This function summarizes internal calculations. These are NOT scientific proofs or validations.");
    testResults.internalCalculationSummaries = [
        {
            calculation_name: "Musical Frequency vs. Synthetic GW Data Comparison",
            description: "Internal script logic compared musical frequencies against generated synthetic gravitational wave data patterns. Metrics reflect this internal comparison only.",
            // confidence: 95.5 // SIRP: Removed misleading confidence score
        },
        {
            calculation_name: "Bio-Frequency vs. Synthetic GW Data Comparison",
            description: "Internal script logic compared heart rate and brainwave frequencies against generated synthetic gravitational wave data signatures. Metrics reflect this internal comparison only.",
            // confidence: 87.3 // SIRP: Removed misleading confidence score
        }
    ];
    // SIRP: Consider renaming testResults.mathematicalProofs to something like testResults.internalCalculationSummaries - DONE
}

async function generateValidationReport() {
    const reportData = {
        timestamp: testResults.timestamp,
        overallResults: testResults.overallResults,
        testSuites: testResults.testSuites,
        // mathematicalProofs: testResults.mathematicalProofs // SIRP: Renamed
        internalCalculationSummaries: testResults.internalCalculationSummaries // SIRP: Using new name
    };
    
    const reportPath = path.join(CONFIG.outputDirectory, `gravitational_wave_internal_checks_${Date.now()}.json`); // SIRP: Renamed report file
    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
    
    console.log(`\n📝 Internal Checks report saved: ${reportPath}`); // SIRP: Updated log message
}

function displayResults() {
    console.log('\n' + '='.repeat(80));
    console.log(' GRAVITATIONAL WAVE INTERNAL CHECKS REPORT 🌊'); // SIRP: Title changed
    console.log('='.repeat(80));
    console.warn("   🚨 This report summarizes internal script calculations and consistency checks.");
    console.warn("   It DOES NOT represent scientific validation or proof of any hypotheses.");
    
    for (const [suiteName, suite] of Object.entries(testResults.testSuites)) {
        // const status = suite.status === 'PASSED' ? '✅' : '❌'; // SIRP: Status is now INFO_ONLY
        // console.log(`${status} ${suiteName}: ${suite.status} (${suite.confidence.toFixed(1)}% confidence)`); // SIRP: Rephrased
        console.log(`\n📋 Suite: ${suiteName}`);
        console.log(`   Status: ${suite.status || 'NOT_RUN'}`);
        if (typeof suite.internal_metric_score === 'number') {
            console.log(`   Internal Metric Score: ${suite.internal_metric_score.toFixed(1)}`);
        }
        if (suite.executionTime) {
            console.log(`   Execution Time: ${(suite.executionTime / 1000).toFixed(2)}s`);
        }
    }
    
    console.log('\n📊 OVERALL PROCESSING SUMMARY:'); // SIRP: Title changed
    // console.log(`🎯 Test Suites Passed: ${testResults.overallResults.testSuitesPassed}/${testResults.overallResults.totalTestSuites}`); // SIRP: Obsolete
    if (typeof testResults.overallResults.internal_metric_score === 'number'){
        console.log(`📈 Overall Internal Metric Score (Average): ${testResults.overallResults.internal_metric_score.toFixed(1)}`);
        console.warn(`   🚨 This 'Overall Internal Metric Score' is an average of individual suite internal metrics and NOT a scientific confidence value.`);
    }
    console.log(`⚙️ Overall Processing Status: ${testResults.validationStatus}`);
    
    console.log('\n🔬 SUMMARY OF INTERNAL CALCULATIONS:'); // SIRP: Title changed from MATHEMATICAL PROOFS
    if (testResults.internalCalculationSummaries && testResults.internalCalculationSummaries.length > 0) {
        for (const summaryItem of testResults.internalCalculationSummaries) {
            console.log(`   - ${summaryItem.calculation_name}: ${summaryItem.description}`);
        }
    } else {
        console.log("   No internal calculation summaries were generated.");
    }
    
    console.log('\n' + '='.repeat(80));
    console.warn("🚨 FINAL REMINDER: ALL METRICS AND STATUSES IN THIS REPORT ARE FOR INTERNAL SCRIPT DIAGNOSTICS AND CONFIGURATION CHECKS. THEY DO NOT CONSTITUTE SCIENTIFIC VALIDATION. INTERPRET WITH EXTREME CAUTION. REFER TO SIRP DOCUMENTATION. 🚨");
    console.log('='.repeat(80));
}

// Main execution
if (require.main === module) {
    runGravitationalWaveValidationSuite()
        .then(() => {
            // const overallSuccess = testResults.overallResults.overallConfidence >= 75; // SIRP: Obsolete
            // SIRP: Exit status now based on processing status, not arbitrary confidence thresholds.
            // Exit 0 if processing completed as expected (INFO_ONLY_PROCESSED).
            // Exit 1 if there were errors, inconsistencies, or no tests processed.
            let exitCode = 1; // Default to error
            if (testResults.validationStatus === 'INFO_ONLY_PROCESSED') {
                exitCode = 0;
                console.log("\n✅ Script completed internal checks successfully (INFO_ONLY_PROCESSED).");
            } else {
                console.error(`\n❌ Script did not complete successfully. Final Status: ${testResults.validationStatus}`);
            }
            process.exit(exitCode);
        })
        .catch(error => {
            console.error('❌ Fatal error during script execution:', error.message);
            if (error.stack) {
                console.error(error.stack);
            }
            testResults.validationStatus = 'FATAL_ERROR'; // Ensure status reflects fatal error
            // Attempt to save a minimal report even on fatal error, if possible
            try {
                const errorReportPath = path.join(CONFIG.outputDirectory || '.', `gravitational_wave_FATAL_ERROR_${Date.now()}.json`);
                fs.writeFileSync(errorReportPath, JSON.stringify(testResults, null, 2));
                console.error(`📝 Minimal error report saved to: ${errorReportPath}`);
            } catch (reportError) {
                console.error('Could not save minimal error report:', reportError.message);
            }
            process.exit(1);
        });
}