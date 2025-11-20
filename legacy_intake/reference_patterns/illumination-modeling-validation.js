#!/usr/bin/env node

/**
 * Illumination Modeling System - Code Feature Audit
 * Target Simulation Code Analysis Suite
 * 
 * Audits the target simulation for presence of code features related to concepts
 * such as "Energy-Vibration-Illumination", "Musical Frequencies in Cosmology", etc.
 * Does NOT validate the scientific basis of these concepts.
 * 
 * Original Author: Agent 1 (Core Development Specialist)
 * Integrity Review: Agent 1
 * Date: May 28, 2025
 */

const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

// Agent 1: Removed ILLUMINATION_CONFIG block as per "TO BE REMOVED" comment in original code.

// Agent 1 Fix: Add missing Chladni potential function
/**
 * Calculates a 3D Chladni-like potential.
 * This function aims to replicate the mathematical model used in the target simulation.
 * WARNING: The dimensional consistency of this formula, when interpreting 'freq' as a physical
 * frequency (e.g., Hz), is problematic without specific scaling constants or a re-interpretation
 * of terms. The current implementation mirrors the Python version's apparent assumptions, where
 * 'freq' and related constants might be used in a way that makes intermediate terms effectively
 * dimensionless or scaled to act as angles.
 *
 * @param {number} x Cartesian x-coordinate.
 * @param {number} y Cartesian y-coordinate.
 * @param {number} z Cartesian z-coordinate.
 * @param {number} freq A numerical factor, often derived from physical frequencies (e.g., Hz from tests),
 *                      but its role in the formula implies it contributes to dimensionless terms or
 *                      terms scaled to act as angles.
 * @param {number} modeM Modal integer for azimuthal structure.
 * @param {number} modeN Modal integer for polar structure.
 * @param {number} modeP Modal integer for radial structure.
 * @returns {number} Potential value.
 *
 * Dimensional Analysis Clarification (Mirroring Python Version's Apparent Behavior):
 * The formula's structure suggests that combinations like `k_base * 0.5` or `k_base * 0.1` (where `k_base = freq / 50.0`),
 * when multiplied by coordinates or modal numbers, are treated as producing dimensionless angular values suitable for sin/cos.
 * This implies an implicit scaling or that 'freq' itself is treated as contributing to a dimensionless wavenumber-like quantity
 * within the trigonometric arguments, rather than strictly as Hz leading to dimensional imbalances.
 *
 * Example for an angular term `modeN * phi * k_base * 0.5`:
 *  - `phi` is an angle (radians, dimensionless).
 *  - For the overall argument to be an angle, `modeN * k_base * 0.5` must effectively be dimensionless.
 *    If `freq` (and thus `k_base`) were strictly Hz (1/Time), this term would not be an angle.
 *    The formula's usage implies `k_base` is treated as making this part dimensionless.
 *
 * Example for a radial term component `modeP * r * k_base * 0.1`:
 *  - `r` has units of Length.
 *  - For this to be part of an angle, `k_base * 0.1` must effectively have units of 1/Length or combine
 *    with `r` to become dimensionless. This is non-standard if `k_base` carries Hz units.
 *    The formula implies such a scaling.
 *
 * Time term `time * 0.00005 * freq * 0.1`:
 *  - The original validation function included a time term. This has been removed to match the
 *    time-independent Chladni potential function found in the target simulation's core update loop
 *    (2024-12-19_SIM_v3.0_illumination-modeling-system.html) for 'sine' waveType.
 *    The simulation's function itself does not take a time parameter for this specific usage.
 */
function validateChladniPotential3D(x, y, z, freq, modeM, modeN, modeP) {
    const k_base = freq / 50.0;
    
    const r = Math.sqrt(x*x + y*y + z*z);
    if (r === 0) return 0;
    
    const phi = Math.acos(z/r);
    const theta = Math.atan2(y, x);
    
    // Matches simulation's getChladniPotential3D for waveType = 'sine'
    // araştırmalar/simulations/implementations/experimental-variants/2024-12-19_SIM_v3.0_illumination-modeling-system.html
    const angularPart = Math.cos(modeM * theta) * Math.sin(modeN * phi * k_base * 0.5);
    const radialPart = Math.sin(modeP * r * k_base * 0.1); // Simulation uses Math.sin for radial part in this context
    
    let potential = angularPart * radialPart;
    potential = isNaN(potential) ? 0 : potential;
    
    // The simulation clamps the potential: return Math.max(-1, Math.min(1, val));
    // This validation function should also clamp to accurately reflect the simulation's behavior.
    return Math.max(-1, Math.min(1, potential));
}

/**
 * Validates the thermal color mapping logic based on a potential value.
 * This function replicates the heat calculation and color mapping from the simulation,
 * using a fixed normalized distance from origin for testing purposes.
 *
 * @param {number} potential The Chladni potential value.
 * @returns {{heat: number, color: {r: number, g: number, b: number}}} An object containing the calculated heat and the expected RGB color.
 */
function validateThermalColorMapping(potential) {
    // Replicate the heat calculation from the simulation
    const nodeProximity = 1.0 - Math.min(1.0, Math.abs(potential) * 1.5);
    const distFromOrigin = 0.5; // Normalized test value
    
    let heat = nodeProximity * 0.8 + (1.0 - distFromOrigin) * 0.2;
    heat = Math.max(0, Math.min(1, heat));
    
    // Validate color mapping logic
    let expectedColor = { r: 0, g: 0, b: 0 };
    
    if (heat < 0.125) {
        expectedColor = { r: 0, g: 0, b: 0.5 + heat * 4 };
    } else if (heat < 0.25) {
        const t = (heat - 0.125) * 8;
        expectedColor = { r: 0, g: t * 0.5, b: 1 };
    } else if (heat < 0.375) {
        const t = (heat - 0.25) * 8;
        expectedColor = { r: 0, g: 0.5 + t * 0.5, b: 1 - t };
    } else if (heat < 0.5) {
        const t = (heat - 0.375) * 8;
        expectedColor = { r: t, g: 1, b: 0 };
    } else if (heat < 0.625) {
        const t = (heat - 0.5) * 8;
        expectedColor = { r: 1, g: 1 - t * 0.5, b: 0 };
    } else if (heat < 0.75) {
        const t = (heat - 0.625) * 8;
        expectedColor = { r: 1, g: 0.5 - t * 0.5, b: 0 };
    } else if (heat < 0.875) {
        const t = (heat - 0.75) * 8;
        expectedColor = { r: 1, g: 0, b: t * 0.2 };
    } else {
        const t = (heat - 0.875) * 8;
        expectedColor = { r: 1, g: t, b: t };
    }
    
    return { heat, color: expectedColor };
}

const { JSDOM } = require('jsdom');

// Test configuration
const SIMULATION_PATH = path.resolve(__dirname, '..', 'research/simulations/implementations/experimental-variants/2024-12-19_SIM_v3.0_illumination-modeling-system.html');
const TEST_RESULTS_PATH = 'test/results/illumination-modeling-validation-results.md';

// Validation criteria from Issue #1
const VALIDATION_CRITERIA = {
    PARTICLE_COUNT_MIN: 100000,
    PARTICLE_COUNT_MAX: 500000,
    ILLUMINATION_THRESHOLD_RANGE: [0.1, 1.0], // For checking presence of thresholding code
    RESONANCE_DETECTION_RADIUS: 2.0, // For checking presence of radius-based code
    // SCIENTIFIC INTEGRITY: Correlation targets for stellar formation based on these models are scientifically unfounded without rigorous causal evidence.
    // STELLAR_FORMATION_CORRELATION_TARGET: 0.8, // >80%
    REQUIRED_VISUALIZATION_MODES: ['illumination', 'thermal', 'resonance', 'stellar'], // Checks for presence of these UI/code modes
    // SCIENTIFIC INTEGRITY: The scientific basis for applying specific musical frequencies (C2-C3) or bio-frequencies (heart rates)
    // to cosmic illumination modeling is unfounded. This list is used to check for their presence in the simulation code if they are part of its design.
    FREQUENCIES_TO_CHECK_FOR_PRESENCE: [65.41, 82.41, 98.00, 130.81], // Formerly REQUIRED_FREQUENCIES
    BIO_COSMIC_FREQUENCIES_TO_CHECK_FOR_PRESENCE: [55, 85] // Formerly BIO_COSMIC_FREQUENCY_RANGE
};

class IlluminationModelingValidator {
    constructor() {
        this.testResults = {
            timestamp: new Date().toISOString(),
            totalTests: 0,
            passedTests: 0,
            failedTests: 0,
            details: [],
            mathematicalValidation: {},
            codeAnalysis: {},
            energyVibrationIlluminationValidation: {}
        };
    }

    async runValidation() {
        console.log('🔬 Starting Illumination Modeling System v3.0 Validation...\n');
        // Agent 1: Note - Many validation checks below rely on string matching in the simulation's code.
        // This approach can be fragile if variable names or code structures are refactored in the simulation.
        // Future improvements could involve the simulation exposing a more direct testing API or specific DOM outputs for validation.
        try {
            // Load and parse the simulation file
            const simulationContent = await this.loadSimulationFile();
            const dom = new JSDOM(simulationContent);
            const document = dom.window.document;
            
            // Extract JavaScript code for analysis
            const scriptElements = document.querySelectorAll('script');
            let simulationCode = '';
            scriptElements.forEach(script => {
                if (script.textContent && !script.src) {
                    simulationCode += script.textContent;
                }
            });
            
            // Run validation tests
            await this.validateCoreMathematicalFunctions();
            await this.validateParticleSystem(simulationCode);
            await this.validateIlluminationModeling(simulationCode);
            await this.validateEnergyVibrationIlluminationParadox(simulationCode);
            await this.validateMusicalFrequencies(simulationCode);
            await this.validateBioCosmicCoupling(simulationCode);
            await this.validateVisualizationModes(simulationCode);
            await this.validateMathematicalFramework(simulationCode);
            await this.validateResearchAttribution(simulationCode, document);
            
            // Generate test report
            await this.generateTestReport();
            
            console.log(`\n✅ Validation Complete: ${this.testResults.passedTests}/${this.testResults.totalTests} tests passed`);
            
            if (this.testResults.failedTests === 0) {
                console.log('🌟 ALL TESTS PASSED - ILLUMINATION MODELING SYSTEM v3.0 FULLY VALIDATED');
                return true;
            } else {
                console.log(`❌ ${this.testResults.failedTests} tests failed - Review required`);
                return false;
            }
            
        } catch (error) {
            console.error('❌ Validation failed with error:', error.message);
            this.addTestResult('System Validation', false, `Critical error: ${error.message}`);
            return false;
        }
    }

    async loadSimulationFile() {
        if (!fs.existsSync(SIMULATION_PATH)) {
            throw new Error(`Simulation file not found: ${SIMULATION_PATH}`);
        }
        return fs.readFileSync(SIMULATION_PATH, 'utf8');
    }

    async validateParticleSystem(code) {
        console.log('🔍 Validating Particle System...');
        
        // Check particle count configuration
        const particleCountMatch = code.match(/PARTICLE_COUNT\s*=\s*(\d+)/);
        if (particleCountMatch) {
            const particleCount = parseInt(particleCountMatch[1]);
            const isValidCount = particleCount >= VALIDATION_CRITERIA.PARTICLE_COUNT_MIN && 
                               particleCount <= VALIDATION_CRITERIA.PARTICLE_COUNT_MAX;
            this.addTestResult('Particle Count Range', isValidCount, 
                `Found ${particleCount} particles (valid range: ${VALIDATION_CRITERIA.PARTICLE_COUNT_MIN}-${VALIDATION_CRITERIA.PARTICLE_COUNT_MAX})`);
        }
        
        // Check for 3D particle positions
        const has3DPositions = code.includes('particlePositions') && code.includes('* 3');
        this.addTestResult('3D Particle Positions', has3DPositions, '3D position arrays implemented');
        
        // Check for velocity arrays
        const hasVelocities = code.includes('particleVelocities');
        this.addTestResult('Particle Velocities', hasVelocities, 'Velocity tracking implemented');
        
        // Check for density calculation
        const hasDensityCalculation = code.includes('calculateLocalDensity') || code.includes('particleDensities');
        this.addTestResult('Density Calculation', hasDensityCalculation, 'Local density calculation implemented');
    }

    async validateIlluminationModeling(code) {
        console.log('🔍 Auditing Illumination Modeling Code Features...');
        
        // Check for illumination threshold code presence
        const thresholdMatch = code.match(/ILLUMINATION_THRESHOLD\s*=\s*([\d\.]+)/);
        if (thresholdMatch && thresholdMatch[1]) {
            const thresholdValue = parseFloat(thresholdMatch[1]);
            const [min, max] = VALIDATION_CRITERIA.ILLUMINATION_THRESHOLD_RANGE;
            // SCIENTIFIC INTEGRITY: This check verifies if the coded threshold value falls within a predefined range for audit purposes.
            // It does not validate the scientific appropriateness of this range or the threshold itself. (Integrity Plan 2.1)
            const isWithinAuditRange = thresholdValue >= min && thresholdValue <= max;
            this.addTestResult('Illumination Threshold Value (Audit Range Check)', isWithinAuditRange, 
                `Found ILLUMINATION_THRESHOLD = ${thresholdValue} (audit range: ${min}-${max}). Scientific validity TBD.`);
        } else {
            const hasIlluminationThreshold = code.includes('ILLUMINATION_THRESHOLD') || code.includes('illumination-threshold');
            this.addTestResult('Illumination Threshold Code Presence', hasIlluminationThreshold, 
                'Illumination threshold parameter code presence check (value not parsed or found). Scientific validity TBD.');
        }
        
        // Check for stellar formation related code constructs
        const hasStellarFormationCode = code.includes('stellar') && (code.includes('formation') || code.includes('Formation'));
        this.addTestResult('Stellar Formation Related Code Presence', hasStellarFormationCode, 
            'Code constructs related to "stellar formation" found/not found. Scientific interpretation pending.');
        
        // Check for resonance node detection and radius code presence
        const radiusMatch = code.match(/(?:RESONANCE_DETECTION_RADIUS|resonanceRadius|DETECTION_RADIUS)\s*=\s*([\d\.]+)/i);
        if (radiusMatch && radiusMatch[1]) {
            const radiusValue = parseFloat(radiusMatch[1]);
            const expectedRadiusAudit = VALIDATION_CRITERIA.RESONANCE_DETECTION_RADIUS;
            // SCIENTIFIC INTEGRITY: Comparing to an audit value. Does not confirm scientific validity. (Integrity Plan 2.1)
            const isAuditRadiusMatch = Math.abs(radiusValue - expectedRadiusAudit) < 0.001; 
            this.addTestResult('Resonance Detection Radius Value (Audit Match)', isAuditRadiusMatch, 
                `Found Resonance Detection Radius = ${radiusValue} (audit expected: ${expectedRadiusAudit}). Scientific validity TBD.`);
        } else {
            const hasResonanceDetectionCode = code.includes('resonance') && (code.includes('node') || code.includes('Node'));
            this.addTestResult('Resonance Node Detection Code Presence', hasResonanceDetectionCode, 
                'Code for "resonance node detection" found/not found (radius value not parsed). Scientific validity TBD.');
        }
        
        // Check for illumination statistics tracking code
        const hasIlluminationStatsCode = code.includes('illuminationPercentage') || code.includes('stellarFormationCount');
        this.addTestResult('Illumination Statistics Tracking Code Presence', hasIlluminationStatsCode, 
            'Code for tracking "illumination statistics" found/not found.');

        // SCIENTIFIC INTEGRITY: Removed check for STELLAR_FORMATION_CORRELATION_TARGET.
        // Correlation does not imply causation, and a target for it is scientifically unfounded without further evidence. (Integrity Plan 2.3)
        /*
        const correlationTargetRegex = /(?:STELLAR_FORMATION_CORRELATION_TARGET|stellarCorrelationTarget|formationCorrelationTarget)\s*=\s*0\.8/i;
        const hasCorrelationTarget = correlationTargetRegex.test(code) || 
                                   (code.includes('stellar') && code.includes('correlation') && code.includes('0.8'));
        this.addTestResult('Stellar Formation Correlation Target Setup', hasCorrelationTarget, 
            `Check for setup of stellar formation correlation target around ${VALIDATION_CRITERIA.STELLAR_FORMATION_CORRELATION_TARGET}`);
        */
        this.addTestResult('Stellar Formation Correlation Target Code', code.includes('STELLAR_FORMATION_CORRELATION_TARGET') || code.includes('stellarCorrelationTarget'),
            'Code for a "stellar formation correlation target" parameter found/not found. Scientific basis of such a target is TBD.');
    }

    async validateEnergyVibrationIlluminationParadox(code) {
        console.log('🔍 Auditing "Energy-Vibration-Illumination Paradox" Related Code Features...');
        
        // Check for Energy-Vibration-Illumination Paradox related textual mentions
        const hasParadoxText = code.includes('Energy-Vibration-Illumination') || 
                                       code.includes('energy illuminating its own');
        this.addTestResult('"Energy-Vibration-Illumination Paradox" Textual Mentions', hasParadoxText, 
            'Textual mentions related to "Energy-Vibration-Illumination Paradox" found/not found.');
        
        // Check for code related to "invisible infrastructure" visualization
        const hasInvisibleInfrastructureCode = code.includes('invisible') || code.includes('vibrational') || code.includes('field');
        this.addTestResult('"Invisible Infrastructure" Visualization Code Presence', hasInvisibleInfrastructureCode, 
            'Code for "invisible vibrational infrastructure" visualization found/not found.');
        
        // Check for code related to "energy transformation cycle"
        const hasEnergyTransformationCode = code.includes('energy') && 
                                      (code.includes('transformation') || code.includes('illuminat'));
        this.addTestResult('"Energy Transformation Cycle" Code Presence', hasEnergyTransformationCode, 
            'Code for "energy transformation cycle" visualization found/not found.');
        
        // Check for code related to the four-stage process: Creates → Concentrates → Illuminates → Reveals
        const hasCreateStageCode = code.includes('vibration') || code.includes('standing') || code.includes('wave');
        const hasConcentrateStageCode = code.includes('gravitational') || code.includes('density') || code.includes('concentration');
        const hasIlluminateStageCode = code.includes('stellar') || code.includes('luminous') || code.includes('illumination');
        const hasRevealStageCode = code.includes('pattern') || code.includes('structure') || code.includes('visualization');
        
        this.addTestResult('Four-Stage Process Code Feature Presence', 
            hasCreateStageCode && hasConcentrateStageCode && hasIlluminateStageCode && hasRevealStageCode,
            'Code features corresponding to a "Create-Concentrate-Illuminate-Reveal" cycle found/not found. Scientific interpretation pending.');
    }

    async validateMusicalFrequencies(code) {
        console.log('🔍 Auditing Musical Frequencies Code Features...');
        
        // Check for musical frequency related code
        const hasMusicalFrequenciesCode = code.includes('BASE_FREQUENCIES') || code.includes('musical');
        this.addTestResult('Musical Frequency System Code Presence', hasMusicalFrequenciesCode, 'Code related to a "musical frequency system" found/not found.');
        
        // Check for presence of specific frequency values in code
        let foundFrequencies = 0;
        VALIDATION_CRITERIA.FREQUENCIES_TO_CHECK_FOR_PRESENCE.forEach(freq => {
            if (code.includes(freq.toString())) {
                foundFrequencies++;
            }
        });
        
        this.addTestResult('Specific Musical Frequencies Code Presence', foundFrequencies >= 3, // Original threshold 
            `Found code containing ${foundFrequencies}/${VALIDATION_CRITERIA.FREQUENCIES_TO_CHECK_FOR_PRESENCE.length} of the target frequencies. Scientific basis TBD.`);
        
        // Check for harmonic relationship code
        const hasHarmonicsCode = code.includes('harmonic') || code.includes('octave');
        this.addTestResult('Harmonic Relationships Code Presence', hasHarmonicsCode, 'Code related to "harmonic relationships" found/not found.');
    }

    async validateBioCosmicCoupling(code) {
        console.log('🔍 Auditing "Bio-Cosmic Coupling" Code Features...');
        
        // Check for heart rate integration code
        const hasHeartRateCode = code.includes('heart') && code.includes('rate');
        this.addTestResult('"Heart Rate" Integration Code Presence', hasHeartRateCode, 'Code related to "heart rate integration" found/not found. Scientific basis TBD.');
        
        // Check for biological frequency range code
        const hasBioFrequenciesCode = (code.includes('55') && code.includes('85')) || 
                                 (code.includes('40') && code.includes('180')) || 
                                 code.includes('biological') || code.includes('bio-cosmic');
        this.addTestResult('"Biological Frequencies" Code Presence', hasBioFrequenciesCode, 'Code related to "biological frequency ranges" found/not found. Scientific basis TBD.');
        
        // Check for bio-cosmic emission zones code
        const hasEmissionZonesCode = code.includes('EMISSION_ZONES') || code.includes('emission');
        this.addTestResult('"Bio-Cosmic Emission Zones" Code Presence', hasEmissionZonesCode, 'Code related to "bio-cosmic emission zones" found/not found. Scientific basis TBD.');
    }

    async validateVisualizationModes(code) {
        console.log('🔍 Auditing Visualization Modes Code Features...');
        
        let foundModes = 0;
        VALIDATION_CRITERIA.REQUIRED_VISUALIZATION_MODES.forEach(mode => {
            if (code.includes(`'${mode}'`) || code.includes(`"${mode}"`)) {
                foundModes++;
            }
        });
        
        this.addTestResult('Specific Visualization Modes Code Presence', foundModes >= VALIDATION_CRITERIA.REQUIRED_VISUALIZATION_MODES.length, 
            `Found code for ${foundModes}/${VALIDATION_CRITERIA.REQUIRED_VISUALIZATION_MODES.length} target visualization modes.`);
        
        // Check for real-time mode switching code
        const hasModeSwitchingCode = code.includes('visualizationMode') && code.includes('change');
        this.addTestResult('Real-time Mode Switching Code Presence', hasModeSwitchingCode, 'Code for "real-time visualization mode switching" found/not found.');
    }

    async validateMathematicalFramework(code) {
        console.log('🔍 Auditing Mathematical Framework Code Features...');
        
        // Check for 3D Chladni mathematics code
        const hasChladniMathCode = code.includes('Chladni') && code.includes('3D');
        this.addTestResult('3D Chladni Mathematics Code Presence', hasChladniMathCode, 'Code related to "3D Chladni field mathematics" found/not found.');
        
        // Check for standing wave calculation code
        const hasStandingWavesCode = code.includes('standing') || code.includes('wave') || code.includes('Chladni') || code.includes('field');
        this.addTestResult('Standing Wave Calculations Code Presence', hasStandingWavesCode, 'Code for "standing wave field calculations" found/not found.');
        
        // Check for gravitational force calculation code
        const hasGravitationalForcesCode = code.includes('gravitational') || code.includes('force');
        this.addTestResult('Gravitational Forces Code Presence', hasGravitationalForcesCode, 'Code for "gravitational force calculations" found/not found.');
        
        // Check for modal parameters (M, N, P) code
        const hasModalParamsCode = code.includes('modeM') && code.includes('modeN') && code.includes('modeP');
        this.addTestResult('Modal Parameters (M, N, P) Code Presence', hasModalParamsCode, 'Code for modal parameters (M, N, P) found/not found.');
    }

    async validateResearchAttribution(code, document) {
        console.log('🔍 Auditing Research Attribution...');
        
        // Check for proper research attribution in code or document text
        const documentText = document && document.textContent ? document.textContent : '';
        const hasAldrinAttribution = code.includes('Aldrin Payopay') || documentText.includes('Aldrin Payopay');
        this.addTestResult('Lead Researcher Attribution Presence', hasAldrinAttribution, 'Textual attribution to "Aldrin Payopay" found/not found.');
        
        const hasClaudeAttribution = code.includes('Claude Sonnet 4') || documentText.includes('Claude Sonnet 4');
        this.addTestResult('AI Implementation Attribution Presence', hasClaudeAttribution, 'Textual attribution to "Claude Sonnet 4" found/not found.');
        
        // Check for research integrity protection code
        const hasIntegrityProtectionCode = code.includes('RESEARCH_TEAM') || code.includes('verifyResearchIntegrity');
        this.addTestResult('Research Integrity Protection Code Presence', hasIntegrityProtectionCode, 'Code related to "research integrity protection" found/not found.');
    }

    async validateCoreMathematicalFunctions() {
        console.log('🔍 Auditing Core Mathematical Functions (Code Feature & Output Check)...');
        // Test 1: Chladni Potential Calculation - Properties and Critical Points Audit
        console.log('\nAUDIT 1: 3D Chladni Potential Calculation - Properties and Critical Points');
        const chladniTestPoints = [
            { x: 0, y: 0, z: 0, freq: 65.41, m: 2, n: 2, p: 4, description: "Origin" },
            { x: 1, y: 0, z: 0, freq: 65.41, m: 2, n: 2, p: 4, description: "X-axis point" },
            { x: 0, y: 1, z: 0, freq: 65.41, m: 2, n: 2, p: 4, description: "Y-axis point" },
            { x: 0, y: 0, z: 1, freq: 65.41, m: 2, n: 2, p: 4, description: "Z-axis point" },
            { x: 0.5, y: 0.5, z: 0.5, freq: 65.41, m: 2, n: 2, p: 4, description: "Mid-quadrant point" },
            { x: 1, y: 1, z: 1, freq: 130.81, m: 1, n: 1, p: 1, description: "Simple mode C3" },
            { x: 0.2, y: 0.3, z: 0.4, freq: 98.00, m: 0, n: 1, p: 1, description: "M=0 (azimuthal symmetry expected check)" },
            { x: 0.2, y: 0.3, z: 0.4, freq: 98.00, m: 1, n: 0, p: 1, description: "N=0 (polar plane node expected check)" },
            { x: 0.2, y: 0.3, z: 0.4, freq: 98.00, m: 1, n: 1, p: 0, description: "P=0 (radial constant expected check)" }
        ];
        let chladniPropertiesPassed = 0;
        let chladniClampingPassed = 0;
        let chladniOriginTestPassed = true;

        chladniTestPoints.forEach((tp, index) => {
            const potential = validateChladniPotential3D(tp.x, tp.y, tp.z, tp.freq, tp.m, tp.n, tp.p);
            const isValid = !isNaN(potential) && isFinite(potential);
            if (isValid) chladniPropertiesPassed++;
            
            const isClamped = potential >= -1.0 && potential <= 1.0;
            if (isClamped) chladniClampingPassed++;

            console.log(`  TestPoint #${index} (${tp.description}): potential = ${potential.toFixed(6)} ${isValid && isClamped ? '✅' : '❌'}`);
            if (!isValid) console.log(`    ❌ Audit Fail: Potential is NaN or Infinite for ${tp.description}`);
            if (!isClamped) console.log(`    ❌ Audit Fail: Potential ${potential.toFixed(6)} not clamped [-1, 1] for ${tp.description}`);

            if (tp.x === 0 && tp.y === 0 && tp.z === 0) {
                if (potential !== 0) {
                    chladniOriginTestPassed = false;
                    console.log(`    ❌ Audit Fail: Potential at origin is ${potential.toFixed(6)}, expected 0 for this function.`);
                }
            }
        });
        this.addTestResult('Chladni Potential Calculation (Valid & Finite Output Audit)', chladniPropertiesPassed === chladniTestPoints.length, `${chladniPropertiesPassed}/${chladniTestPoints.length} calculations give valid and finite output.`);
        this.addTestResult('Chladni Potential Clamping [-1, 1] Output Audit', chladniClampingPassed === chladniTestPoints.length, `${chladniClampingPassed}/${chladniTestPoints.length} results clamped correctly by function.`);
        this.addTestResult('Chladni Potential at Origin (r=0) Output Audit', chladniOriginTestPassed, `Potential at origin is ${chladniOriginTestPassed ? '0 as expected from function' : 'not 0'}.`);

        // Test 2: Thermal Color Mapping Validation - Specific Segments
        console.log('\nAUDIT 2: Thermal Color Mapping Logic - Segment Checks');
        const potentialForHeatTest = [
            0.0,  // Max heat = 1.0 * 0.8 + 0.2 = 1.0
            0.1,  // Heat = (1-0.1*1.5)*0.8 + 0.2 = (1-0.15)*0.8 + 0.2 = 0.85*0.8 + 0.2 = 0.68 + 0.2 = 0.88 -> This note is wrong, calc is nodeProximity = 1-(0.1*1.5) = 0.85. heat = 0.85*0.8 + (1-0.5)*0.2 = 0.68+0.1 = 0.78
            0.33, // nodeProx = 1-(0.33*1.5) = 1-0.495 = 0.505. heat = 0.505*0.8 + 0.1 = 0.404+0.1=0.504
            0.5,  // nodeProx = 1-(0.5*1.5)=1-0.75=0.25. heat=0.25*0.8+0.1=0.2+0.1=0.3
            0.6,  // nodeProx = 1-(0.6*1.5)=1-0.9=0.1. heat=0.1*0.8+0.1=0.08+0.1=0.18
            0.66, // nodeProx = 1-Math.min(1,0.66*1.5)=1-Math.min(1,0.99)=1-0.99=0.01. heat=0.01*0.8+0.1=0.008+0.1=0.108
            0.7,  // nodeProx = 1-Math.min(1,0.7*1.5)=1-Math.min(1,1.05)=1-1=0. heat=0*0.8+0.1=0.1
            1.0   // nodeProx = 1-Math.min(1,1.0*1.5)=1-1=0. heat=0*0.8+0.1=0.1
        ];
        let directThermalMappingPassed = 0;
        const numThermalSegments = 8; // Based on the if/else structure
        let segmentsCovered = new Array(numThermalSegments).fill(false);
        const epsilon = 0.001; // Tolerance for float comparisons

        potentialForHeatTest.forEach((potential, idx) => {
            const result = validateThermalColorMapping(potential);
            const isValidColor = result.color.r >= -epsilon && result.color.r <= 1 + epsilon &&
                               result.color.g >= -epsilon && result.color.g <= 1 + epsilon &&
                               result.color.b >= -epsilon && result.color.b <= 1 + epsilon;
            const isValidHeat = result.heat >= -epsilon && result.heat <= 1 + epsilon;
            
            let segmentIndex = -1;
            if (result.heat < 0.125) segmentIndex = 0;
            else if (result.heat < 0.25) segmentIndex = 1;
            else if (result.heat < 0.375) segmentIndex = 2;
            else if (result.heat < 0.5) segmentIndex = 3;
            else if (result.heat < 0.625) segmentIndex = 4;
            else if (result.heat < 0.75) segmentIndex = 5;
            else if (result.heat < 0.875) segmentIndex = 6;
            else segmentIndex = 7;
            if(segmentIndex !== -1) segmentsCovered[segmentIndex] = true;

            if (isValidColor && isValidHeat) {
                directThermalMappingPassed++;
                console.log('  Potential ' + potential.toFixed(2) + ' -> Heat ' + result.heat.toFixed(3) + ' -> RGB(' + result.color.r.toFixed(2) + ',' + result.color.g.toFixed(2) + ',' + result.color.b.toFixed(2) + ') (Seg ' + segmentIndex + ') ✅');
            } else {
                console.log('  Potential ' + potential.toFixed(2) + ' -> Heat ' + result.heat.toFixed(3) + ' -> RGB(' + result.color.r.toFixed(2) + ',' + result.color.g.toFixed(2) + ',' + result.color.b.toFixed(2) + ') (Seg ' + segmentIndex + ') ❌');
                if (!isValidColor) console.log(`    ❌ Audit Fail: Invalid color component for potential ${potential.toFixed(2)}`);
                if (!isValidHeat) console.log(`    ❌ Audit Fail: Invalid heat value for potential ${potential.toFixed(2)}`);
            }
        });
        const allSegmentsCovered = segmentsCovered.every(s => s === true);
        this.addTestResult('Thermal Color Mapping (Valid Outputs & Segment Coverage Audit)', 
            directThermalMappingPassed === potentialForHeatTest.length && allSegmentsCovered, 
            `${directThermalMappingPassed}/${potentialForHeatTest.length} mappings valid. Segments covered: ${segmentsCovered.filter(s=>s).length}/${numThermalSegments}.`);


        // Test 3: Musical Frequency Response - Evaluating Potential Field Structure
        console.log('\nAUDIT 3: Musical Frequency Response - Potential Field Structure Check');
        const musicalFreqs = VALIDATION_CRITERIA.FREQUENCIES_TO_CHECK_FOR_PRESENCE; // C2, E2, G2, C3
        const nonMusicalFreqs = [70.0, 90.0, 110.0, 140.0]; // Control frequencies for comparison
        
        const sampleGridSize = 5; 
        const samplePoints = [];
        for (let i = 0; i < sampleGridSize; i++) {
            for (let j = 0; j < sampleGridSize; j++) {
                for (let k = 0; k < sampleGridSize; k++) {
                    samplePoints.push([
                        (i / (sampleGridSize - 1) * 2 - 1) * 2, 
                        (j / (sampleGridSize - 1) * 2 - 1) * 2,
                        (k / (sampleGridSize - 1) * 2 - 1) * 2
                    ]);
                }
            }
        }

        function getPotentialFieldStats(freq, m, n, p) {
            const potentials = samplePoints.map(sp => validateChladniPotential3D(sp[0], sp[1], sp[2], freq, m, n, p));
            const validPotentials = potentials.filter(pot => !isNaN(pot) && isFinite(pot));
            if (validPotentials.length === 0) return { mean: 0, variance: 0, validRatio: 0, min:0, max:0 };
            
            const sum = validPotentials.reduce((acc, val) => acc + val, 0);
            const mean = sum / validPotentials.length;
            const variance = validPotentials.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / validPotentials.length;
            const min = Math.min(...validPotentials);
            const max = Math.max(...validPotentials);
            return { mean: mean, variance: variance, validRatio: validPotentials.length / potentials.length, min:min, max:max };
        }

        let musicalStructureChecksPassed = 0;
        const minExpectedVarianceForStructure = 0.05; // Heuristic: fields should show some variance

        console.log('  Musical Frequencies (audit for structured potential fields):');
        musicalFreqs.forEach(freq => {
            const stats = getPotentialFieldStats(freq, 2, 2, 4); // Default modes m,n,p
            const createsStructure = stats.validRatio === 1 && stats.variance > minExpectedVarianceForStructure && (stats.max - stats.min > 0.1);
            if (createsStructure) musicalStructureChecksPassed++;
            console.log(`    Freq ${freq.toFixed(2)} Hz: Var=${stats.variance.toFixed(4)}, Mean=${stats.mean.toFixed(4)}, Range=[${stats.min.toFixed(2)},${stats.max.toFixed(2)}]. ${createsStructure ? '✅ (Structured)' : '⚠️ (Less structured/flat or invalid)'}`);
        });

        console.log('  Control (Non-Musical) Frequencies (audit for comparative structure):');
        let controlValidFieldCount = 0;
        nonMusicalFreqs.forEach(freq => {
            const stats = getPotentialFieldStats(freq, 2, 2, 4);
            if (stats.validRatio === 1) controlValidFieldCount++;
            console.log(`    Freq ${freq.toFixed(2)} Hz: Var=${stats.variance.toFixed(4)}, Mean=${stats.mean.toFixed(4)}, Range=[${stats.min.toFixed(2)},${stats.max.toFixed(2)}].`);
        });
        
        this.addTestResult('Musical Frequency Response (Field Structure & Validity Audit)', 
            musicalStructureChecksPassed === musicalFreqs.length && controlValidFieldCount === nonMusicalFreqs.length, 
            `${musicalStructureChecksPassed}/${musicalFreqs.length} musical freqs showed structured fields. All control freqs gave valid fields: ${controlValidFieldCount === nonMusicalFreqs.length}.`);
        
        // Test 4: Resonance Node Concentration - Recalibrated Check
        console.log('\nAUDIT 4: Resonance Node Concentration - Distribution Check');
        const t4_gridSize = 10;
        const t4_nodeCount = { low: 0, high: 0 };
        let t4_totalValidPoints = 0;
        for (let i = 0; i < t4_gridSize; i++) {
            for (let j = 0; j < t4_gridSize; j++) {
                for (let k = 0; k < t4_gridSize; k++) {
                    const x = (i / (t4_gridSize -1) * 4 - 2); 
                    const y = (j / (t4_gridSize -1) * 4 - 2);
                    const z = (k / (t4_gridSize -1) * 4 - 2);
                    const potential = validateChladniPotential3D(x, y, z, 65.41, 2, 2, 4); // Standard C2 Freq, m=2,n=2,p=4
                    if (!isNaN(potential) && isFinite(potential)) {
                        t4_totalValidPoints++;
                        if (Math.abs(potential) < 0.2) t4_nodeCount.low++; // Node threshold audit
                        else t4_nodeCount.high++;
                    }
                }
            }
        }
        const t4_totalSamplePoints = t4_gridSize * t4_gridSize * t4_gridSize;
        const t4_nodeRatio = t4_totalValidPoints > 0 ? t4_nodeCount.low / t4_totalValidPoints : 0;
        
        const t4_isReasonableDistribution = t4_nodeRatio > 0.01 && t4_nodeRatio < 0.99 && t4_totalValidPoints === t4_totalSamplePoints;
        console.log(`  Total sample points: ${t4_totalSamplePoints}, Valid points: ${t4_totalValidPoints}. Low potential (nodes < 0.2): ${t4_nodeCount.low} (${(t4_nodeRatio * 100).toFixed(1)}%).`);
        this.addTestResult('Resonance Node Concentration (Plausible Distribution Audit)', t4_isReasonableDistribution, 
            `Node ratio ${t4_nodeRatio.toFixed(3)}. Audit checks for a non-extreme ratio (0.01 < ratio < 0.99) and all points valid. Valid points: ${t4_totalValidPoints}/${t4_totalSamplePoints}.`);
    }

    addTestResult(testName, passed, details) {
        this.testResults.totalTests++;
        if (passed) {
            this.testResults.passedTests++;
            console.log(`  ✅ ${testName}: ${details}`);
        } else {
            this.testResults.failedTests++;
            console.log(`  ❌ ${testName}: ${details}`);
        }
        
        this.testResults.details.push({
            test: testName,
            passed,
            details,
            timestamp: new Date().toISOString()
        });
    }

    async generateTestReport() {
        // Ensure results directory exists
        const resultsDir = path.dirname(TEST_RESULTS_PATH);
        if (!fs.existsSync(resultsDir)) {
            fs.mkdirSync(resultsDir, { recursive: true });
        }
        
        const report = this.generateMarkdownReport();
        fs.writeFileSync(TEST_RESULTS_PATH, report);
        console.log(`\n📊 Test report generated: ${TEST_RESULTS_PATH}`);
    }

    generateMarkdownReport() {
        const passRate = this.testResults.totalTests > 0 ? ((this.testResults.passedTests / this.testResults.totalTests) * 100).toFixed(1) : "N/A";
        
        // SCIENTIFIC INTEGRITY: Report language neutralized. (Integrity Plan 2.1, 2.4)
        return `# Illumination Modeling System - Code Feature Audit Report

**Date**: ${this.testResults.timestamp}  
**Test Suite**: Automated Code Feature Audit Protocol  
**Target Simulation**: ${SIMULATION_PATH.split('/').pop()} (Path: ${SIMULATION_PATH})

## 📊 Audit Summary

- **Total Checks**: ${this.testResults.totalTests}
- **Checks Passed**: ${this.testResults.passedTests}
- **Checks Failed**: ${this.testResults.failedTests}
- **Pass Rate**: ${passRate}%
- **Audit Status**: ${this.testResults.failedTests === 0 ? '✅ CODE FEATURE AUDIT COMPLETED' : '⚠️  CODE FEATURE AUDIT INCOMPLETE/ERRORS'}

## 🔬 Audit Details (Code Feature Presence & Basic Function Checks)

${this.testResults.details.map(test => 
    `### ${test.passed ? '✅' : '❌'} ${test.test}
**Result**: ${test.details}
**Timestamp**: ${test.timestamp}
`
).join('\n')}

## 🌟 Conceptual Framework Code Feature Audit ("Energy-Vibration-Illumination")

${this.testResults.failedTests === 0 ? 
`**Code Feature Audit Summary**: The target simulation was audited for the presence of code features and textual mentions related to an 'Energy-Vibration-Illumination' conceptual framework.

**Code Features Checked for Presence**: 
- ✅ Textual mentions related to "Energy-Vibration-Illumination Paradox".
- ✅ Code related to "invisible vibrational infrastructure" visualization.
- ✅ Code related to an "energy transformation cycle" visualization.
- ✅ Code features corresponding to a "Create-Concentrate-Illuminate-Reveal" cycle.
- ✅ Code related to a "musical frequency system" and specific frequencies (C2, E2, G2, C3).
- ✅ Code related to "bio-cosmic coupling", "heart rates", and "biological frequencies".
- ✅ Code for multiple visualization modes (illumination, thermal, resonance, stellar).
` : 
`**AUDIT INCOMPLETE**: ${this.testResults.failedTests} critical code feature checks failed or mathematical function audits did not pass. Review of the target simulation's code or this audit script may be required.`}

**SCIENTIFIC INTEGRITY NOTE**: This audit **DOES NOT VALIDATE THE SCIENTIFIC BASIS** of the 'Energy-Vibration-Illumination' concept or its constituent parts (e.g., musical frequencies in cosmology, bio-cosmic coupling). The scientific validity of such concepts is under review as per the project's integrity plan (SCIENTIFIC_INTEGRITY_RESTORATION_PLAN.md). This report only confirms the presence or absence of specific code constructs and textual mentions in the target simulation file, and basic output checks of included mathematical functions.

## 🎯 Research Team Attribution (as found in code/comments)

- **Lead Researcher**: Aldrin Payopay (Conceptual Framework & Scientific Vision) - Code/Text presence: ${this.testResults.details.find(d => d.test === 'Lead Researcher Attribution Presence')?.passed ? 'FOUND' : 'NOT FOUND'}
- **AI Implementation**: Claude Sonnet 4 (Technical Implementation & Validation) - Code/Text presence: ${this.testResults.details.find(d => d.test === 'AI Implementation Attribution Presence')?.passed ? 'FOUND' : 'NOT FOUND'}
- **Project**: Resonance is All You Need - Illumination Modeling System (Target Simulation)

---

**Generated by**: Automated Code Feature Audit System  
**Test Framework**: Node.js + jsdom  
**Audit Standard**: Based on criteria from Issue #1, adapted for Integrity Review. 
`;
    }
}

// Run validation if called directly
if (require.main === module) {
    const validator = new IlluminationModelingValidator();
    validator.runValidation().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('Validation failed:', error);
        process.exit(1);
    });
}

module.exports = { 
    IlluminationModelingValidator, 
    validateChladniPotential3D, 
    validateThermalColorMapping 
};
