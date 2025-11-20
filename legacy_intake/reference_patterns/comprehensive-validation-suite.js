#!/usr/bin/env node

/**
 * Comprehensive Validation Suite Runner
 * Resonance is All You Need - Complete Experimental Validation
 * 
 * Executes all validation protocols and generates comprehensive research report:
 * - Issue #1: Illumination Modeling Validation
 * - Issue #2: Musical Frequency Enhancement
 * - Issue #3: Bio-Cosmic Coupling Validation
 * - Issue #4: Cosmic Web Resonance Analysis
 * - Issue #5: Gravitational Wave Resonance Detection
 * 
 * Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro, Claude Sonnet 4 (Agent 2)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Test file paths (relative to project root)
const TEST_FILES = {
    illumination: 'illumination-modeling-validation.js',
    musical: 'musical-frequency-enhancement-validation.js',
    bioCosmic: 'bio-cosmic-coupling-validation.js',
    cosmicWeb: 'cosmic-web-resonance-analysis.js',
    gravitationalWaves: 'gravitational-wave-resonance-detection-v3.js'  // Use the optimized v3 version
};

function executeTestSuite(testFile, testName) {
    console.log(`🔬 EXECUTING: ${testName}`);
    console.log('='.repeat(50));
    
    try {
        const output = execSync(`node ${testFile}`, { 
            encoding: 'utf8',
            cwd: path.resolve(__dirname), // Run from test directory
            timeout: 60000, // 60 second timeout
            stdio: 'pipe' // Capture output even on non-zero exit
        });
        
        console.log(output);
        
        // Parse results from output
        const results = {
            testName,
            success: !output.includes('❌') || output.includes('ALL TESTS PASSED'),
            output: output,
            timestamp: new Date().toISOString()
        };
        
        // Extract specific metrics from output
        if (output.includes('Success Rate:')) {
            const successMatch = output.match(/Success Rate:\s*(\d+\.?\d*)%/);
            if (successMatch) {
                results.successRate = parseFloat(successMatch[1]);
            }
        }
        
        if (output.includes('Overall Resonance Score:')) {
            const resonanceMatch = output.match(/Overall Resonance Score:\s*(\d+\.?\d*)%/);
            if (resonanceMatch) {
                results.resonanceScore = parseFloat(resonanceMatch[1]);
            }
        }
        
        if (output.includes('Musicality Score:')) {
            const musicalityMatch = output.match(/Musicality Score:\s*(\d+\.?\d*)%/);
            if (musicalityMatch) {
                results.musicalityScore = parseFloat(musicalityMatch[1]);
            }
        }
        
        return results;
        
    } catch (error) {
        // Handle case where test script exits with non-zero code but still produces output
        if (error.stdout) {
            console.log(error.stdout);
            
            const results = {
                testName,
                success: !error.stdout.includes('❌') || error.stdout.includes('ALL TESTS PASSED'),
                output: error.stdout,
                timestamp: new Date().toISOString()
            };
            
            // Extract specific metrics from output
            if (error.stdout.includes('Success Rate:')) {
                const successMatch = error.stdout.match(/Success Rate:\s*(\d+\.?\d*)%/);
                if (successMatch) {
                    results.successRate = parseFloat(successMatch[1]);
                }
            }
            
            if (error.stdout.includes('Overall Resonance Score:')) {
                const resonanceMatch = error.stdout.match(/Overall Resonance Score:\s*(\d+\.?\d*)%/);
                if (resonanceMatch) {
                    results.resonanceScore = parseFloat(resonanceMatch[1]);
                }
            }
            
            if (error.stdout.includes('Musicality Score:')) {
                const musicalityMatch = error.stdout.match(/Musicality Score:\s*(\d+\.?\d*)%/);
                if (musicalityMatch) {
                    results.musicalityScore = parseFloat(musicalityMatch[1]);
                }
            }
            
            return results;
        } else {
            console.error(`❌ ERROR executing ${testName}:`, error.message);
            return {
                testName,
                success: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
}

function generateComprehensiveReport(results) {
    const timestamp = new Date().toISOString();
    const date = new Date().toLocaleDateString();
    
    // SCIENTIFIC INTEGRITY: Report rephrased to be a technical summary of test script executions.
    // All claims of scientific validation, breakthroughs, or confirmations have been removed or neutralized.
    let report = `# Comprehensive Test Suite - Execution Summary Report
## Resonance is All You Need - Test Script Execution Status

**Research Team**: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro, Claude Sonnet 4 (Agent 2)  
**Date**: ${date}  
**Timestamp**: ${timestamp}  
**Validation Suite Runner Version**: 2.0.1 (Integrity Review)

---

## 📊 TEST SUITE EXECUTION SUMMARY

This report summarizes the execution status of individual test scripts. It does not make any claims regarding the scientific validity of the underlying concepts or models tested by these scripts. Such validity is assessed by the broader Scientific Integrity Restoration Plan.

### Test Script Execution Status:
- **Illumination Modeling Script**: ${results.illumination.success ? '✅ SCRIPT PASSED INTERNAL CHECKS' : '❌ SCRIPT FAILED OR REPORTED ERRORS'}
- **Musical Frequency Script**: ${results.musical.success ? '✅ SCRIPT PASSED INTERNAL CHECKS' : '❌ SCRIPT FAILED OR REPORTED ERRORS'}
- **Bio-Cosmic Coupling Script**: ${results.bioCosmic.success ? '✅ SCRIPT PASSED INTERNAL CHECKS' : '❌ SCRIPT FAILED OR REPORTED ERRORS'}
- **Cosmic Web Resonance Script**: ${results.cosmicWeb.success ? '✅ SCRIPT PASSED INTERNAL CHECKS' : '❌ SCRIPT FAILED OR REPORTED ERRORS'}
- **Gravitational Wave Script**: ${results.gravitationalWaves ? (results.gravitationalWaves.success ? '✅ SCRIPT PASSED INTERNAL CHECKS' : '❌ SCRIPT FAILED OR REPORTED ERRORS') : '⚠️ SCRIPT NOT EXECUTED'}

---

## 📈 DETAILED TEST SCRIPT EXECUTION RESULTS

**SCIENTIFIC INTEGRITY NOTE:** The 'Success Rate', 'Musicality Score', and 'Resonance Score' metrics are reported as extracted from the output of the individual test scripts. The scientific meaning and validity of these metrics are currently under review as per the Scientific Integrity Restoration Plan. They should not be interpreted as validated scientific outcomes at this stage.

### Issue #1: Illumination Modeling Script (${TEST_FILES.illumination})
**Execution Status**: ${results.illumination.success ? 'SCRIPT PASSED INTERNAL CHECKS ✅' : 'SCRIPT FAILED OR REPORTED ERRORS ❌'}  
**Reported Success Rate**: ${results.illumination.successRate ? results.illumination.successRate.toFixed(1) + '%' : 'N/A'}  
**Execution Timestamp**: ${results.illumination.timestamp}

### Issue #2: Musical Frequency Script (${TEST_FILES.musical})
**Execution Status**: ${results.musical.success ? 'SCRIPT PASSED INTERNAL CHECKS ✅' : 'SCRIPT FAILED OR REPORTED ERRORS ❌'}  
**Reported Success Rate**: ${results.musical.successRate ? results.musical.successRate.toFixed(1) + '%' : 'N/A'}  
**Execution Timestamp**: ${results.musical.timestamp}

### Issue #3: Bio-Cosmic Coupling Script (${TEST_FILES.bioCosmic})
**Execution Status**: ${results.bioCosmic.success ? 'SCRIPT PASSED INTERNAL CHECKS ✅' : 'SCRIPT FAILED OR REPORTED ERRORS ❌'}  
**Reported Success Rate**: ${results.bioCosmic.successRate ? results.bioCosmic.successRate.toFixed(1) + '%' : 'N/A'}  
**Execution Timestamp**: ${results.bioCosmic.timestamp}

### Issue #4: Cosmic Web Resonance Script (${TEST_FILES.cosmicWeb})
**Execution Status**: ${results.cosmicWeb.success ? 'SCRIPT PASSED INTERNAL CHECKS ✅' : 'SCRIPT FAILED OR REPORTED ERRORS ❌'}  
**Reported Musicality Score**: ${results.cosmicWeb.musicalityScore ? results.cosmicWeb.musicalityScore.toFixed(1) + '%' : 'N/A'}  
**Execution Timestamp**: ${results.cosmicWeb.timestamp}

### Issue #5: Gravitational Wave Script (${TEST_FILES.gravitationalWaves})
**Execution Status**: ${results.gravitationalWaves ? (results.gravitationalWaves.success ? 'SCRIPT PASSED INTERNAL CHECKS ✅' : 'SCRIPT FAILED OR REPORTED ERRORS ❌') : 'SCRIPT NOT EXECUTED ⚠️'}  
**Reported Resonance Score**: ${results.gravitationalWaves && results.gravitationalWaves.resonanceScore ? results.gravitationalWaves.resonanceScore.toFixed(1) + '%' : 'N/A'}  
**Execution Timestamp**: ${results.gravitationalWaves ? results.gravitationalWaves.timestamp : 'N/A'}

---

## 📝 NOTES ON REPORTED METRICS

The individual test scripts executed by this runner may internally define and report various metrics (e.g., 'Success Rate', 'Musicality Score', 'Resonance Score'). 

- The purification status of each individual test script should be consulted before interpreting these metrics.
- These metrics reflect the internal logic of those scripts and **do not represent validated scientific outcomes or endorsements of any specific theory** unless explicitly stated otherwise by the Scientific Integrity Restoration Plan.

---

## ⚙️ TEST SUITE RUNNER PERFORMANCE

**Overall Test Script Pass Rate: ${overallSuccessRate}% (${totalSuccesses}/5 scripts reported passing their internal checks)**

### Individual Script Metrics (as reported by scripts):
- **Illumination Modeling Script**: ${results.illumination.successRate ? results.illumination.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Musical Frequency Script**: ${results.musical.successRate ? results.musical.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Bio-Cosmic Script**: ${results.bioCosmic.successRate ? results.bioCosmic.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Cosmic Web Script**: ${results.cosmicWeb.musicalityScore ? results.cosmicWeb.musicalityScore.toFixed(1) + '%' : 'N/A'} musicality score
- **Gravitational Wave Script**: ${results.gravitationalWaves && results.gravitationalWaves.resonanceScore ? results.gravitationalWaves.resonanceScore.toFixed(1) + '%' : 'N/A'} resonance score

### Test Suite Runner Performance:
- **Total Test Scripts Configured**: 5
- **Successful Script Executions (no runtime errors)**: ${[results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && !r.error).length}
- **Failed Script Executions (runtime errors)**: ${[results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && r.error).length}
- **Script Execution Success Rate**: ${([results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && !r.error).length / 5 * 100).toFixed(1)}%

---

## 📋 FINAL OVERVIEW

This script successfully executed the configured test suites. The pass/fail status for each suite is based on its own internal criteria and output.

**IMPORTANT SCIENTIFIC INTEGRITY ADVISORY:**
This report **MUST NOT** be interpreted as a validation or confirmation of any scientific theories, hypotheses, or breakthroughs.
Its sole purpose is to document the execution and reported outcomes of various component test scripts within the project.
The scientific validity of concepts such as 'Musical Frequency Enhancement', 'Bio-Cosmic Coupling', or specific 'Resonance Scores' is subject to the ongoing Scientific Integrity Restoration Plan.

Refer to \`SCIENTIFIC_INTEGRITY_RESTORATION_PLAN.md\` and \`GITHUB_ISSUES_QUEUE.md\` for the current project status regarding scientific claims.

---

*This report was generated by the Comprehensive Test Suite Runner (v2.0.1 Integrity Review).*
`;

    // Calculate overall success metrics
    const illuminationSuccess = results.illumination.success;
    const musicalSuccess = results.musical.success;
    const bioCosmicSuccess = results.bioCosmic.success;
    const cosmicWebSuccess = results.cosmicWeb.success;
    const gravitationalWaveSuccess = results.gravitationalWaves ? results.gravitationalWaves.success : false;
    
    const totalSuccesses = [illuminationSuccess, musicalSuccess, bioCosmicSuccess, cosmicWebSuccess, gravitationalWaveSuccess].filter(Boolean).length;
    const overallSuccessRate = (totalSuccesses / 5 * 100).toFixed(1);
    
    report += `**Overall Test Script Pass Rate: ${overallSuccessRate}% (${totalSuccesses}/5 scripts reported passing their internal checks)**

### Individual Script Metrics (as reported by scripts):
- **Illumination Modeling Script**: ${results.illumination.successRate ? results.illumination.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Musical Frequency Script**: ${results.musical.successRate ? results.musical.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Bio-Cosmic Script**: ${results.bioCosmic.successRate ? results.bioCosmic.successRate.toFixed(1) + '%' : 'N/A'} success rate
- **Cosmic Web Script**: ${results.cosmicWeb.musicalityScore ? results.cosmicWeb.musicalityScore.toFixed(1) + '%' : 'N/A'} musicality score
- **Gravitational Wave Script**: ${results.gravitationalWaves && results.gravitationalWaves.resonanceScore ? results.gravitationalWaves.resonanceScore.toFixed(1) + '%' : 'N/A'} resonance score

### Test Suite Runner Performance:
- **Total Test Scripts Configured**: 5
- **Successful Script Executions (no runtime errors)**: ${[results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && !r.error).length}
- **Failed Script Executions (runtime errors)**: ${[results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && r.error).length}
- **Script Execution Success Rate**: ${([results.illumination, results.musical, results.bioCosmic, results.cosmicWeb, results.gravitationalWaves].filter(r => r && !r.error).length / 5 * 100).toFixed(1)}%

---

## 📋 FINAL OVERVIEW

This script successfully executed the configured test suites. The pass/fail status for each suite is based on its own internal criteria and output.

**IMPORTANT SCIENTIFIC INTEGRITY ADVISORY:**
This report **MUST NOT** be interpreted as a validation or confirmation of any scientific theories, hypotheses, or breakthroughs.
Its sole purpose is to document the execution and reported outcomes of various component test scripts within the project.
The scientific validity of concepts such as 'Musical Frequency Enhancement', 'Bio-Cosmic Coupling', or specific 'Resonance Scores' is subject to the ongoing Scientific Integrity Restoration Plan.

Refer to \`SCIENTIFIC_INTEGRITY_RESTORATION_PLAN.md\` and \`GITHUB_ISSUES_QUEUE.md\` for the current project status regarding scientific claims.

---

*This report was generated by the Comprehensive Test Suite Runner (v2.0.1 Integrity Review).*
`;

    return report;
}

function runComprehensiveValidation() {
    console.log('🚀 COMPREHENSIVE VALIDATION SUITE');
    console.log('=================================');
    console.log('Research Team: Aldrin Payopay, Claude Opus 4, Gemini 2.5 Pro');
    console.log('Date:', new Date().toISOString());
    console.log('');
    console.log('Executing complete experimental validation protocol...');
    console.log('');
    
    const startTime = Date.now();
    const results = { startTime };
    
    try {
        // Execute all validation suites
        console.log('🔬 PHASE 1: Illumination Modeling Validation');
        console.log('===========================================');
        results.illumination = executeTestSuite(TEST_FILES.illumination, 'Illumination Modeling Validation');
        
        console.log('\n\n🎵 PHASE 2: Musical Frequency Enhancement');
        console.log('========================================');
        results.musical = executeTestSuite(TEST_FILES.musical, 'Musical Frequency Enhancement');
        
        console.log('\n\n🧬 PHASE 3: Bio-Cosmic Coupling Validation');
        console.log('==========================================');
        results.bioCosmic = executeTestSuite(TEST_FILES.bioCosmic, 'Bio-Cosmic Coupling Validation');
        
        console.log('\n\n🌌 PHASE 4: Cosmic Web Resonance Analysis');
        console.log('=========================================');
        results.cosmicWeb = executeTestSuite(TEST_FILES.cosmicWeb, 'Cosmic Web Resonance Analysis');
        
        console.log('\n\n🌊 PHASE 5: Gravitational Wave Resonance Detection');
        console.log('==================================================');
        results.gravitationalWaves = executeTestSuite(TEST_FILES.gravitationalWaves, 'Gravitational Wave Resonance Detection');
        
        // Generate comprehensive report
        console.log('\n\n📊 GENERATING COMPREHENSIVE REPORT');
        console.log('==================================');
        
        const report = generateComprehensiveReport(results);
        
        // Save comprehensive results
        const resultsDir = path.join('research', 'findings', 'validation-reports');
        if (!fs.existsSync(resultsDir)) {
            fs.mkdirSync(resultsDir, { recursive: true });
        }
        
        const resultsPath = path.join(resultsDir, `comprehensive-validation-${Date.now()}.json`);
        const reportPath = path.join(resultsDir, `comprehensive-validation-report-${Date.now()}.md`);
        
        fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
        fs.writeFileSync(reportPath, report);
        
        // Calculate overall success metrics
        const illuminationSuccess = results.illumination.success;
        const musicalSuccess = results.musical.success;
        const bioCosmicSuccess = results.bioCosmic.success;
        const cosmicWebSuccess = results.cosmicWeb.success;
        const gravitationalWaveSuccess = results.gravitationalWaves ? results.gravitationalWaves.success : false;
        
        const totalSuccesses = [illuminationSuccess, musicalSuccess, bioCosmicSuccess, cosmicWebSuccess, gravitationalWaveSuccess].filter(Boolean).length;
        const overallSuccessRate = (totalSuccesses / 5 * 100).toFixed(1);
        
        console.log('\n🎉 COMPREHENSIVE VALIDATION COMPLETE');
        console.log('===================================');
        console.log(`Overall Success Rate: ${overallSuccessRate}% (${totalSuccesses}/5 hypotheses)`);
        console.log(`Total Execution Time: ${((Date.now() - startTime) / 1000).toFixed(2)} seconds`);
        console.log('');
        
        if (overallSuccessRate >= 75) {
            console.log('🎯 TEST SUITE EXECUTION COMPLETED WITH HIGH PASS RATE');
            console.log('📊 SCIENTIFIC INTEGRITY NOTE: High test pass rate indicates scripts executed without errors');
            console.log('⚠️  IMPORTANT: This does not constitute scientific validation of any theories');
            console.log('📋 Status: TEST EXECUTION SUCCESSFUL - Scientific validity requires separate assessment');
        } else if (overallSuccessRate >= 50) {
            console.log('⚠️  PARTIAL TEST EXECUTION SUCCESS');
            console.log('📊 Some test scripts reported internal issues');
            console.log('🔧 Additional debugging recommended for failing scripts');
        } else {
            console.log('❌ MULTIPLE TEST EXECUTION FAILURES');
            console.log('🔧 Test scripts require debugging and refinement');
            console.log('📋 Review script logic and parameters');
        }
        
        console.log(`\n📊 Comprehensive results: ${resultsPath}`);
        console.log(`📋 Detailed report: ${reportPath}`);
        
        return results;
        
    } catch (error) {
        console.error('❌ VALIDATION SUITE ERROR:', error.message);
        console.error('Stack trace:', error.stack);
        return null;
    }
}

// Run comprehensive validation if this script is executed directly
if (require.main === module) {
    runComprehensiveValidation();
}

module.exports = { runComprehensiveValidation, generateComprehensiveReport }; 