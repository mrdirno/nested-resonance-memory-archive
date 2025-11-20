#!/usr/bin/env node

/**
 * Musical Frequency Enhancement Validation Suite
 * Resonance is All You Need - Issue #2 Implementation
 * 
 * Tests musical frequencies vs non-musical controls:
 * - C2 (65.41 Hz) for stable illumination patterns
 * - E2 (82.41 Hz) for stellar formation efficiency optimization
 * - G2 (98.00 Hz) for structure-illumination balance
 * - C3 (130.81 Hz) for rapid, bright structural formation
 * 
 * Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro
 */

const fs = require('fs');
const path = require('path');

// Import validation functions from illumination modeling test
const { validateChladniPotential3D } = require('./illumination-modeling-validation.js');

function calculateStructureClarity(freq, modeM = 2, modeN = 2, modeP = 4, gridSize = 20) {
    const points = [];
    const potentials = [];
    
    // Sample 3D space to measure structure clarity
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            for (let k = 0; k < gridSize; k++) {
                const x = (i - gridSize/2) * 0.3;
                const y = (j - gridSize/2) * 0.3;
                const z = (k - gridSize/2) * 0.3;
                
                const potential = validateChladniPotential3D(x, y, z, freq, modeM, modeN, modeP);
                points.push({ x, y, z });
                potentials.push(potential);
            }
        }
    }
    
    // Calculate structure metrics
    const mean = potentials.reduce((sum, p) => sum + p, 0) / potentials.length;
    const variance = potentials.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / potentials.length;
    const stdDev = Math.sqrt(variance);
    
    // Count distinct nodes (low potential regions)
    const nodeThreshold = 0.2;
    const nodeCount = potentials.filter(p => Math.abs(p) < nodeThreshold).length;
    const nodeRatio = nodeCount / potentials.length;
    
    // Calculate gradient strength (structure definition)
    let gradientSum = 0;
    let gradientCount = 0;
    
    for (let i = 1; i < gridSize - 1; i++) {
        for (let j = 1; j < gridSize - 1; j++) {
            for (let k = 1; k < gridSize - 1; k++) {
                const idx = i * gridSize * gridSize + j * gridSize + k;
                const current = potentials[idx];
                
                // Calculate local gradient magnitude
                const dx = potentials[(i+1) * gridSize * gridSize + j * gridSize + k] - 
                          potentials[(i-1) * gridSize * gridSize + j * gridSize + k];
                const dy = potentials[i * gridSize * gridSize + (j+1) * gridSize + k] - 
                          potentials[i * gridSize * gridSize + (j-1) * gridSize + k];
                const dz = potentials[i * gridSize * gridSize + j * gridSize + (k+1)] - 
                          potentials[i * gridSize * gridSize + j * gridSize + (k-1)];
                
                const gradientMag = Math.sqrt(dx*dx + dy*dy + dz*dz);
                gradientSum += gradientMag;
                gradientCount++;
            }
        }
    }
    
    const avgGradient = gradientSum / gradientCount;
    
    // Structure clarity score (higher = more defined structures)
    const clarityScore = (stdDev * 0.4) + (avgGradient * 0.4) + (nodeRatio * 0.2);
    
    return {
        frequency: freq,
        clarityScore,
        standardDeviation: stdDev,
        averageGradient: avgGradient,
        nodeRatio,
        nodeCount,
        totalPoints: potentials.length
    };
}

function calculateStellarFormationEfficiency(freq, modeM = 2, modeN = 2, modeP = 4) {
    // Simulate stellar formation at resonance nodes
    const gridSize = 15;
    let stellarSites = 0;
    let totalSites = 0;
    
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            for (let k = 0; k < gridSize; k++) {
                const x = (i - gridSize/2) * 0.4;
                const y = (j - gridSize/2) * 0.4;
                const z = (k - gridSize/2) * 0.4;
                
                const potential = validateChladniPotential3D(x, y, z, freq, modeM, modeN, modeP);
                totalSites++;
                
                // Stellar formation occurs at low potential (high concentration) sites
                if (Math.abs(potential) < 0.15) {
                    stellarSites++;
                }
            }
        }
    }
    
    return {
        frequency: freq,
        stellarFormationEfficiency: stellarSites / totalSites,
        stellarSites,
        totalSites
    };
}

function calculateTemporalStability(freq, modeM = 2, modeN = 2, modeP = 4, timeSteps = 10) {
    const testPoint = { x: 1, y: 0.5, z: 0.5 };
    const potentials = [];
    
    for (let t = 0; t < timeSteps; t++) {
        const time = t * 1000; // Time steps
        const potential = validateChladniPotential3D(
            testPoint.x, testPoint.y, testPoint.z, 
            freq, modeM, modeN, modeP, time
        );
        potentials.push(potential);
    }
    
    // Calculate temporal variance (lower = more stable)
    const mean = potentials.reduce((sum, p) => sum + p, 0) / potentials.length;
    const variance = potentials.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / potentials.length;
    
    return {
        frequency: freq,
        temporalStability: 1 / (1 + variance), // Higher score = more stable
        variance,
        potentials
    };
}

function runMusicalFrequencyTests() {
    console.log('🎵 MUSICAL FREQUENCY ENHANCEMENT VALIDATION');
    console.log('===========================================');
    console.log('Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro');
    console.log('Date:', new Date().toISOString());
    console.log('');
    
    // Test frequencies
    const musicalFrequencies = [
        { freq: 65.41, note: 'C2', purpose: 'Stable illumination patterns' },
        { freq: 82.41, note: 'E2', purpose: 'Stellar formation efficiency' },
        { freq: 98.00, note: 'G2', purpose: 'Structure-illumination balance' },
        { freq: 130.81, note: 'C3', purpose: 'Rapid, bright structural formation' }
    ];
    
    const controlFrequencies = [
        { freq: 70.0, note: 'Control-1', purpose: 'Non-musical baseline' },
        { freq: 90.0, note: 'Control-2', purpose: 'Non-musical baseline' },
        { freq: 110.0, note: 'Control-3', purpose: 'Non-musical baseline' },
        { freq: 140.0, note: 'Control-4', purpose: 'Non-musical baseline' }
    ];
    
    const results = {
        timestamp: new Date().toISOString(),
        musicalResults: [],
        controlResults: [],
        comparison: {},
        summary: {}
    };
    
    console.log('TESTING MUSICAL FREQUENCIES');
    console.log('===========================');
    
    // Test musical frequencies
    musicalFrequencies.forEach(({ freq, note, purpose }) => {
        console.log(`\nTesting ${note} (${freq} Hz) - ${purpose}`);
        console.log('-'.repeat(50));
        
        const clarity = calculateStructureClarity(freq);
        const efficiency = calculateStellarFormationEfficiency(freq);
        const stability = calculateTemporalStability(freq);
        
        const result = {
            frequency: freq,
            note,
            purpose,
            clarity: clarity.clarityScore,
            stellarEfficiency: efficiency.stellarFormationEfficiency,
            temporalStability: stability.temporalStability,
            details: { clarity, efficiency, stability }
        };
        
        results.musicalResults.push(result);
        
        console.log(`  Structure Clarity: ${clarity.clarityScore.toFixed(4)}`);
        console.log(`  Stellar Formation Efficiency: ${(efficiency.stellarFormationEfficiency * 100).toFixed(1)}%`);
        console.log(`  Temporal Stability: ${stability.temporalStability.toFixed(4)}`);
        console.log(`  Node Ratio: ${(clarity.nodeRatio * 100).toFixed(1)}%`);
    });
    
    console.log('\n\nTESTING CONTROL FREQUENCIES');
    console.log('============================');
    
    // Test control frequencies
    controlFrequencies.forEach(({ freq, note, purpose }) => {
        console.log(`\nTesting ${note} (${freq} Hz) - ${purpose}`);
        console.log('-'.repeat(50));
        
        const clarity = calculateStructureClarity(freq);
        const efficiency = calculateStellarFormationEfficiency(freq);
        const stability = calculateTemporalStability(freq);
        
        const result = {
            frequency: freq,
            note,
            purpose,
            clarity: clarity.clarityScore,
            stellarEfficiency: efficiency.stellarFormationEfficiency,
            temporalStability: stability.temporalStability,
            details: { clarity, efficiency, stability }
        };
        
        results.controlResults.push(result);
        
        console.log(`  Structure Clarity: ${clarity.clarityScore.toFixed(4)}`);
        console.log(`  Stellar Formation Efficiency: ${(efficiency.stellarFormationEfficiency * 100).toFixed(1)}%`);
        console.log(`  Temporal Stability: ${stability.temporalStability.toFixed(4)}`);
        console.log(`  Node Ratio: ${(clarity.nodeRatio * 100).toFixed(1)}%`);
    });
    
    // Calculate comparative analysis
    console.log('\n\nCOMPARATIVE ANALYSIS');
    console.log('====================');
    
    const musicalAvg = {
        clarity: results.musicalResults.reduce((sum, r) => sum + r.clarity, 0) / results.musicalResults.length,
        efficiency: results.musicalResults.reduce((sum, r) => sum + r.stellarEfficiency, 0) / results.musicalResults.length,
        stability: results.musicalResults.reduce((sum, r) => sum + r.temporalStability, 0) / results.musicalResults.length
    };
    
    const controlAvg = {
        clarity: results.controlResults.reduce((sum, r) => sum + r.clarity, 0) / results.controlResults.length,
        efficiency: results.controlResults.reduce((sum, r) => sum + r.stellarEfficiency, 0) / results.controlResults.length,
        stability: results.controlResults.reduce((sum, r) => sum + r.temporalStability, 0) / results.controlResults.length
    };
    
    const improvement = {
        clarity: ((musicalAvg.clarity - controlAvg.clarity) / controlAvg.clarity * 100),
        efficiency: ((musicalAvg.efficiency - controlAvg.efficiency) / controlAvg.efficiency * 100),
        stability: ((musicalAvg.stability - controlAvg.stability) / controlAvg.stability * 100)
    };
    
    results.comparison = { musicalAvg, controlAvg, improvement };
    
    console.log('Musical Frequencies Average:');
    console.log(`  Structure Clarity: ${musicalAvg.clarity.toFixed(4)}`);
    console.log(`  Stellar Formation Efficiency: ${(musicalAvg.efficiency * 100).toFixed(1)}%`);
    console.log(`  Temporal Stability: ${musicalAvg.stability.toFixed(4)}`);
    
    console.log('\nControl Frequencies Average:');
    console.log(`  Structure Clarity: ${controlAvg.clarity.toFixed(4)}`);
    console.log(`  Stellar Formation Efficiency: ${(controlAvg.efficiency * 100).toFixed(1)}%`);
    console.log(`  Temporal Stability: ${controlAvg.stability.toFixed(4)}`);
    
    console.log('\nMusical Enhancement:');
    console.log(`  Structure Clarity: ${improvement.clarity > 0 ? '+' : ''}${improvement.clarity.toFixed(1)}%`);
    console.log(`  Stellar Formation Efficiency: ${improvement.efficiency > 0 ? '+' : ''}${improvement.efficiency.toFixed(1)}%`);
    console.log(`  Temporal Stability: ${improvement.stability > 0 ? '+' : ''}${improvement.stability.toFixed(1)}%`);
    
    // Determine success
    const clarityImprovement = improvement.clarity > 50; // Target: >50% improvement
    const efficiencyImprovement = improvement.efficiency > 25; // Target: >25% improvement
    const stabilityImprovement = improvement.stability > 10; // Target: >10% improvement
    
    const overallSuccess = clarityImprovement || efficiencyImprovement || stabilityImprovement;
    
    results.summary = {
        clarityImprovement,
        efficiencyImprovement,
        stabilityImprovement,
        overallSuccess,
        targetMet: improvement.clarity > 50 // Primary success criterion
    };
    
    console.log('\n\nVALIDATION RESULTS');
    console.log('==================');
    
    if (results.summary.targetMet) {
        console.log('🎉 MUSICAL FREQUENCY ENHANCEMENT VALIDATED');
        console.log('✅ Musical frequencies show >50% improvement in structure clarity');
        console.log('✅ Enhanced cosmic structure formation confirmed');
        console.log('✅ Harmonic resonance effects demonstrated');
    } else if (results.summary.overallSuccess) {
        console.log('✅ PARTIAL MUSICAL ENHANCEMENT DETECTED');
        console.log('⚠️  Some improvements detected but below target threshold');
        console.log('📊 Further optimization may be needed');
    } else {
        console.log('❌ MUSICAL ENHANCEMENT NOT DETECTED');
        console.log('⚠️  No significant improvement over control frequencies');
        console.log('🔬 Review frequency selection and parameters');
    }
    
    // Identify best performing frequencies
    const bestMusical = results.musicalResults.reduce((best, current) => 
        current.clarity > best.clarity ? current : best
    );
    
    const bestControl = results.controlResults.reduce((best, current) => 
        current.clarity > best.clarity ? current : best
    );
    
    console.log(`\nBest Musical Frequency: ${bestMusical.note} (${bestMusical.frequency} Hz)`);
    console.log(`  Clarity Score: ${bestMusical.clarity.toFixed(4)}`);
    console.log(`Best Control Frequency: ${bestControl.note} (${bestControl.frequency} Hz)`);
    console.log(`  Clarity Score: ${bestControl.clarity.toFixed(4)}`);
    
    // Save results
    const reportPath = path.join('research', 'findings', 'parameter-sweeps', 
                                `musical-frequency-enhancement-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    
    console.log(`\n📊 Detailed results saved to: ${reportPath}`);
    
    return results;
}

// Run the test if this script is executed directly
if (require.main === module) {
    runMusicalFrequencyTests();
}

module.exports = { runMusicalFrequencyTests, calculateStructureClarity, calculateStellarFormationEfficiency }; 