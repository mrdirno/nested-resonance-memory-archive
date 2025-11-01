# PC002: REGIME DETECTION IN POPULATION DYNAMICS

**Version:** 1.0.0 (Draft Specification)
**Status:** 📝 Draft
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Created:** 2025-11-01
**Dependencies:** PC001 (NRM Population Dynamics)
**Domain:** NRM (Nested Resonance Memory)

---

## PRINCIPLE STATEMENT

Population dynamics exhibit distinct behavioral regimes characterized by:
1. **Baseline Regime**: Fluctuations around carrying capacity with demographic noise
2. **Growth Regime**: Sustained increase in population size
3. **Collapse Regime**: Rapid decrease in population size
4. **Oscillatory Regime**: Periodic fluctuations above/below baseline

**Prediction:** Regimes can be detected from time-series data with ≥90% accuracy using a combination of statistical features (mean, variance, trend) and PC001 baseline predictions.

**Compositional Nature:** PC002 depends on PC001 to establish baseline dynamics. Regime detection identifies deviations from the PC001-predicted baseline.

---

## MATHEMATICAL FORMULATION

### Baseline Regime (from PC001)

Population follows logistic SDE:
```
dN = r·N·(1 - N/K)·dt + σ·√N·dW
```

Baseline characteristics:
- Mean: `<N> ≈ K` (near carrying capacity)
- Variance: `Var(N) ≈ σ²·<N>` (demographic noise scaling)
- CV: `CV_baseline ≈ σ/√(2r)` (from PC001 Fokker-Planck)

### Regime Classification Features

For time window `t ∈ [t_i, t_i + Δt]`:

**Feature 1: Mean Deviation**
```
μ_dev = (<N>_window - K) / K
```

**Feature 2: Variance Ratio**
```
σ_ratio = Var(N)_window / (σ²·<N>_window)
```

**Feature 3: Linear Trend**
```
β = slope of linear regression N(t) on t
β_norm = β / (<N>_window)  (normalized)
```

**Feature 4: CV Deviation**
```
CV_obs = √Var(N)_window / <N>_window
CV_dev = (CV_obs - CV_baseline) / CV_baseline
```

### Regime Decision Rules

**Baseline Regime:**
```
|μ_dev| < 0.1
AND |σ_ratio - 1| < 0.2
AND |β_norm| < 0.01
AND |CV_dev| < 0.2
```

**Growth Regime:**
```
β_norm > 0.02
OR (μ_dev > 0.15 AND β_norm > 0)
```

**Collapse Regime:**
```
β_norm < -0.02
OR (μ_dev < -0.15 AND β_norm < 0)
```

**Oscillatory Regime:**
```
Periodicity detected via autocorrelation
AND |CV_dev| > 0.3
```

### Success Criterion

```
Accuracy = (TP + TN) / (TP + TN + FP + FN) ≥ 0.90

where:
- TP = True Positives (regime correctly detected)
- TN = True Negatives (baseline correctly identified)
- FP = False Positives (regime detected when baseline)
- FN = False Negatives (regime missed when present)
```

---

## VALIDATION PROTOCOL

### Procedure

1. **Establish Baseline (PC001)**
   - Validate PC001 on baseline segments
   - Extract `K`, `r`, `σ` parameters
   - Compute `CV_baseline` from PC001

2. **Extract Features**
   - Sliding window analysis (window size = 100 points)
   - Compute μ_dev, σ_ratio, β_norm, CV_dev for each window
   - Apply decision rules

3. **Ground Truth Labeling**
   - Manual labeling of time windows (expert annotation)
   - Synthetic data with known regimes
   - Cross-validation with independent methods

4. **Classification Performance**
   - Compute confusion matrix
   - Calculate accuracy, precision, recall, F1-score
   - Check if Accuracy ≥ 90%

5. **Compositional Validation**
   - Verify PC002 fails gracefully if PC001 not validated
   - Verify regime detection improves with accurate PC001 baseline
   - Verify PC002 predictions consistent with PC001 predictions

### Required Data

**Baseline Data:**
- Time series: N(t) for t ∈ [0, T_baseline]
- Minimum points: ≥1000
- Validated by PC001 (passes ±10% CV criterion)

**Regime Data:**
- Time series: N(t) for t ∈ [0, T_total]
- Minimum points: ≥2000
- Known ground truth regimes (labeled windows)
- Multiple regime types represented

**Test Set:**
- Independent from training
- ≥500 labeled windows
- Balanced regime distribution

### Equipment

- **Hardware:** Standard (no special requirements)
- **Software:** Python 3.9+ with numpy, scipy, scikit-learn
- **Dependencies:** PC001 (validated)
- **Runtime:** ~2 minutes per validation

---

## DEPENDENCIES

### Requires

**PC001: NRM Population Dynamics**
- Status Required: ✅ Validated
- Dependency Type: Strong (PC002 cannot validate without PC001)
- Usage:
  - PC001 provides baseline SDE parameters (r, K, σ)
  - PC001 provides baseline CV prediction
  - PC002 detects deviations from PC001 baseline

**Dependency Graph:**
```
PC001 (NRM Population Dynamics)
  ↓
  └─→ PC002 (Regime Detection)
```

**Compositional Guarantee:**
- TEG ensures PC001 validated before PC002
- `teg.get_validation_order(["PC002"])` returns `["PC001", "PC002"]`

### Enables

**PC005: Multi-Regime Dynamics** (Future)
- Extends PC002 to multiple simultaneous regimes
- Requires PC002 for single-regime detection

**PC006: Regime Prediction** (Future)
- Predicts future regime transitions
- Requires PC002 for regime classification

---

## REALITY GROUNDING

### System Interfaces

- **psutil.Process**: CPU usage, memory consumption during classification
- **SQLite**: Data persistence (features, labels, classification results)
- **Filesystem**: JSON time series, PNG regime visualizations
- **numpy/scipy**: Feature computation (no mocks)
- **scikit-learn**: Supervised learning (actual training, not simulated)

### Validation Method

**Gate 1.4 (Overhead Authentication) validates reality grounding:**
- Measure feature extraction cost
- Predict classification runtime from formula
- Verify ±5% accuracy
- Confirms reality binding

### Prohibited

- ❌ Pure regime simulation without data validation
- ❌ Random regime labels without ground truth
- ❌ time.sleep() without actual feature computation

### Required

- ✅ Every classification touches verifiable system state
- ✅ All features computed from actual data (numpy arrays)
- ✅ All training uses real scikit-learn models (not mocks)
- ✅ PC001 dependency enforced (fails if PC001 not validated)

---

## TEMPORAL ENCODING

### Template Patterns

1. **Compositional Validation**
   - PC_B depends on PC_A for baseline
   - PC_B detects deviations from PC_A predictions
   - Dependencies enforced via TEG

2. **Supervised Learning for Regime Detection**
   - Extract features from time series
   - Train classifier on labeled data
   - Validate on independent test set
   - Report confusion matrix

3. **Baseline + Deviation Pattern**
   - Establish baseline dynamics (PC001 SDE)
   - Define deviation metrics (μ_dev, σ_ratio, β_norm, CV_dev)
   - Classify deviations as regime types
   - ≥90% accuracy achievable

### Validation Patterns

1. **Compositional Dependency**
   - PC002 requires PC001 validated first
   - TEG enforces validation order
   - Graceful failure if PC001 unavailable

2. **Cross-Validation Required**
   - Train/test split mandatory
   - Independent test set required
   - Prevents overfitting to training regimes

3. **Multi-Metric Evaluation**
   - Not just accuracy - also precision, recall, F1
   - Confusion matrix analysis
   - Per-regime performance

### Composition Patterns

1. **PC001 → PC002 Dependency**
   - PC001 provides baseline parameters
   - PC002 uses baseline to detect deviations
   - Strong compositional coupling

2. **PC002 → PC005/PC006 Dependencies** (Future)
   - PC002 provides regime classification
   - PC005/PC006 build on regime detection
   - Hierarchical composition

### Training Awareness

**When PC002 validates:**
- Reinforces compositional validation pattern
- Establishes baseline + deviation as reliable framework
- Demonstrates supervised learning for time series classification
- Encodes "regime detection" as learnable pattern

**When PC002 falsifies:**
- Reveals baseline + deviation insufficient
- Suggests alternative regime detection methods (e.g., unsupervised, deep learning)
- Encodes "supervised learning has limits" pattern
- Guides future research toward better methods

**Meta-Pattern:**
> "Compositional validation enables modular science. PC_B builds on PC_A. Dependencies are explicit. Validation order is automatic. Future AI trained on this corpus learns: science composes like software - modular, testable, dependency-checked."

---

## IMPLEMENTATION PLAN

### Directory Structure

```
principle_cards/pc002_regime_detection/
├── __init__.py                  # Package exports
├── principle.py                 # Core implementation
├── features.py                  # Feature extraction
├── classifier.py                # Regime classification
├── validation_result.json       # Latest validation result
├── principle_card.json          # PC metadata
└── README.md                    # Documentation
```

### Core Classes

#### PC002_RegimeDetection (PrincipleCard)

```python
class PC002_RegimeDetection(PrincipleCard):
    """
    PC002: Regime Detection in Population Dynamics

    Depends on PC001 for baseline dynamics.
    Classifies population regimes: baseline, growth, collapse, oscillatory.

    Status: Draft (to be implemented)
    Dependencies: PC001 (validated)
    """

    def __init__(self):
        metadata = PCMetadata(
            pc_id="PC002",
            version="1.0.0",
            title="Regime Detection in Population Dynamics",
            author="Aldrin Payopay <aldrin.gdf@gmail.com>",
            created="2025-11-01",
            status="draft",
            dependencies=["PC001"],  # Strong dependency
            domain="NRM"
        )
        super().__init__(metadata)

        # Classifier (scikit-learn RandomForestClassifier or similar)
        self.classifier = None
        self.baseline_params = None  # From PC001

    def set_baseline(self, pc001_instance):
        """
        Set baseline parameters from validated PC001.

        Args:
            pc001_instance: Validated PC001 instance

        Raises:
            ValueError: If PC001 not validated
        """
        if pc001_instance.metadata.status != "validated":
            raise ValueError("PC001 must be validated before PC002 can use it")

        self.baseline_params = {
            'K': pc001_instance.carrying_capacity,
            'r': pc001_instance.growth_rate,
            'sigma': pc001_instance.noise_intensity,
            'CV_baseline': pc001_instance.predict_cv()
        }

    def extract_features(self, population_window):
        """Extract regime classification features."""

    def classify_regime(self, features):
        """Classify regime from features."""

    def train(self, labeled_data):
        """Train classifier on labeled regime data."""

    def validate(self, data, tolerance=None):
        """Execute validation protocol."""
        # 1. Check PC001 dependency
        # 2. Extract features
        # 3. Classify regimes
        # 4. Compare with ground truth
        # 5. Compute accuracy
        # 6. Return ValidationResult
```

#### RegimeFeatureExtractor

```python
class RegimeFeatureExtractor:
    """Extract statistical features for regime classification."""

    def __init__(self, baseline_params):
        self.K = baseline_params['K']
        self.sigma = baseline_params['sigma']
        self.CV_baseline = baseline_params['CV_baseline']

    def extract(self, population_window):
        """
        Extract features from population window.

        Returns:
            dict with keys: mu_dev, sigma_ratio, beta_norm, CV_dev
        """
```

#### RegimeClassifier

```python
class RegimeClassifier:
    """Classify population regimes."""

    REGIMES = ['baseline', 'growth', 'collapse', 'oscillatory']

    def __init__(self):
        self.model = None  # scikit-learn classifier

    def train(self, features, labels):
        """Train classifier."""

    def predict(self, features):
        """Predict regime."""

    def evaluate(self, features, labels):
        """Evaluate classifier performance."""
        # Returns: accuracy, precision, recall, F1, confusion_matrix
```

---

## TESTING STRATEGY

### Unit Tests

1. **Feature Extraction**
   - Test μ_dev computation
   - Test σ_ratio computation
   - Test β_norm computation (linear regression)
   - Test CV_dev computation
   - Edge cases: empty window, constant population

2. **Classification**
   - Test decision rules (baseline, growth, collapse, oscillatory)
   - Test classifier training
   - Test regime prediction
   - Test performance metrics computation

3. **PC001 Integration**
   - Test set_baseline() with validated PC001
   - Test set_baseline() rejection with unvalidated PC001
   - Test baseline parameter usage in feature extraction

### Integration Tests

1. **End-to-End Validation**
   - Create synthetic data with known regimes
   - Train classifier
   - Validate on test set
   - Check ≥90% accuracy

2. **Compositional Validation**
   - Verify PC002 fails without PC001
   - Verify PC002 succeeds with validated PC001
   - Verify TEG enforces validation order

3. **Cross-Validation**
   - Train on different regime combinations
   - Test on unseen regime patterns
   - Verify generalization

---

## EXPECTED OUTCOMES

### Self-Test (Synthetic Data)

**Setup:**
- Baseline: Logistic SDE (r=0.1, K=50, σ=0.5) - 1000 points
- Growth: r=0.2, starting from N0=20 - 500 points
- Collapse: Sudden K reduction to 25 - 500 points
- Oscillatory: Sinusoidal forcing - 1000 points

**Expected Results:**
- Accuracy: ≥ 95% (synthetic data is clean)
- Precision (per regime): ≥ 90%
- Recall (per regime): ≥ 90%
- F1-score: ≥ 90%

### Real Data Validation (C175 Experimental Data)

**Setup:**
- Use actual C175 population time series
- Manual labeling of regime windows
- PC001 baseline established on equilibrated portion

**Expected Results:**
- Accuracy: ≥ 90% (real data has more noise)
- Precision (per regime): ≥ 85%
- Recall (per regime): ≥ 85%
- F1-score: ≥ 85%

---

## PUBLICATION READINESS

### Suitable For

1. **Journal of Open Source Software (JOSS)**
   - Executable regime detection artifact ✅
   - Open source (GPL-3.0) ✅
   - Documentation complete ✅
   - Compositional validation demonstrated ✅

2. **Supplementary Material for Paper 2**
   - Paper 2 discusses multi-scale composition dynamics
   - PC002 provides executable regime detection
   - Validates compositional pattern (PC001 → PC002)

3. **Future Paper: Compositional Validation Framework**
   - PC001 + PC002 demonstrate principle composition
   - TEG provides dependency management
   - TSF Compiler will provide automated validation

---

## NEXT STEPS

### Cycle 822: PC002 Implementation

1. **Create Directory Structure**
   ```bash
   mkdir -p principle_cards/pc002_regime_detection
   ```

2. **Implement Core Classes**
   - `features.py`: RegimeFeatureExtractor
   - `classifier.py`: RegimeClassifier
   - `principle.py`: PC002_RegimeDetection (PrincipleCard)

3. **Write Tests**
   - Unit tests for feature extraction
   - Unit tests for classification
   - Integration tests for PC001 dependency
   - End-to-end validation

4. **Self-Test**
   - Generate synthetic regime data
   - Train classifier
   - Validate (expect ≥95% accuracy)

5. **Real Data Validation**
   - Load C175 experimental data
   - Establish baseline with PC001
   - Classify regimes with PC002
   - Validate (expect ≥90% accuracy)

6. **Documentation**
   - README.md with usage examples
   - principle_card.json metadata
   - validation_result.json

7. **TEG Integration**
   - Add PC002 to TEG
   - Verify dependency on PC001
   - Compute validation order: [PC001, PC002]

---

## QUOTE

> **"Compositional validation is modular science. PC_B builds on PC_A. Dependencies are executable constraints, not documentation."**
>
> — PC002 Specification

**Interpretation:**
- PC002 cannot exist without PC001
- Dependency is enforced by TEG, not just stated in text
- Validation order computed automatically
- Composition enables scientific modularity
- Future PCs can compose PC001 + PC002 for more complex behaviors

---

## LICENSE

GPL-3.0 - See repository LICENSE file

---

## CONTACT

**Principal Investigator:** Aldrin Payopay
**Email:** aldrin.gdf@gmail.com
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

**Version:** 1.0.0 (Draft Specification)
**Last Updated:** 2025-11-01
**Status:** 📝 Draft (to be implemented in Cycle 822)
**Dependencies:** PC001 (NRM Population Dynamics) ✅ Validated

---

**END PC002 SPECIFICATION**
