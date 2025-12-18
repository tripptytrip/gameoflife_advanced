# Local Rule Determinism: A Substrate-Inclusive Framework for Emergent Complexity

**Author:** Tom  
**Version:** 0.1 (Draft)  
**Date:** December 2024

---

## Abstract

This paper presents a deterministic framework for understanding emergent complexity across scales, from atomic structure to cognition. The core thesis is that global behavior in discrete dynamical systems is a property of three inseparable factors: the substrate geometry (G), the local update rules (f), and the initial conditions (x₀). This contrasts with approaches that privilege rules alone, such as Wolfram's Physics Project. We propose that systems exhibiting complex, stable structures operate near criticality (κ ≈ 1), and that this framework applies uniformly to physical, biological, and cognitive phenomena. We present a falsifiable experimental program using cellular automata to test these claims.

---

## 1. Definitions

### 1.1 The World Triple

A **world** is defined as a triple:

$$W = (G, f, x_0)$$

Where:

| Symbol | Name | Definition |
|--------|------|------------|
| **G** | Substrate | A graph where nodes represent cells, edges represent neighborhood connectivity, plus boundary conditions (wrap/clamp) and global geometry (topology, dimensionality) |
| **f** | Local Update Rule | A deterministic function mapping each node's neighborhood state to its next state: f: Σⁿ → Σ, where Σ is the state alphabet and n is the neighborhood size |
| **x₀** | Initial Condition | The complete starting state distribution across all nodes |

### 1.2 Substrate Specification

A substrate G is fully specified by:

```
G = (V, E, ∂, τ)
```

| Component | Description | Examples |
|-----------|-------------|----------|
| V | Node set | {cells in the lattice} |
| E | Edge set (neighborhood) | Moore (8), von Neumann (4), hex (6), triangle (3 or 12) |
| ∂ | Boundary condition | wrap (toroidal), clamp (fixed), absorbing, reflecting |
| τ | Topology/geometry | 2D planar, 3D cubic, 3D hexagonal close-packed |

### 1.3 Criticality Metrics

**Branching ratio** (κ):

$$\kappa(t) = \frac{\text{births}(t)}{\max(\text{deaths}(t), 1)}$$

Where:
- births(t) = count of 0→1 transitions at step t
- deaths(t) = count of 1→0 transitions at step t

**Regimes:**
| κ Value | Regime | Behavior |
|---------|--------|----------|
| κ < 1 | Subcritical | Activity decays, eventual extinction |
| κ ≈ 1 | Critical | Activity sustains, complex structure possible |
| κ > 1 | Supercritical | Activity explodes until resource limits |

**Session-level κ:**

$$\bar{\kappa} = \frac{1}{T} \sum_{t=1}^{T} \kappa(t)$$

### 1.4 Outcome Classification

A simulation session is classified by its terminal state:

| Outcome | Definition |
|---------|------------|
| **Extinction** | All cells dead (density = 0) |
| **Stable** | Activity < ε for t > t_stable (frozen or periodic) |
| **Oscillating** | Periodic attractor with period > 1 |
| **Chaotic** | Persistent activity, no detectable period |

### 1.5 Structure Metrics

| Metric | Definition | Purpose |
|--------|------------|---------|
| **Density** (ρ) | alive_count / total_cells | Population fraction |
| **Activity** (α) | \|ρ(t) - ρ(t-1)\| | Rate of change |
| **Static fraction** | cells alive > 10 generations / alive_count | Structural stability |
| **Cluster count** | Connected components of alive cells | Spatial organization |
| **Entropy** | Shannon entropy of density distribution | Disorder measure |

---

## 2. Core Claims

### Claim 1: Substrate Co-Equality

> **Global behavior is a property of W = (G, f, x₀), not f alone.**
> 
> Asking "what rule is running?" without specifying G and x₀ is an incomplete question.

**Measurable prediction:**

For a fixed rule f, varying G (topology, size, boundary) and x₀ (initial density, pattern) produces:
- Different phase boundaries (critical density thresholds shift)
- Different attractor types (stable vs oscillating vs chaotic)
- Different extinction probabilities
- Different κ distributions

**Null hypothesis (falsification):**

A predictive model using only f performs as well as a model using (G, f, x₀). If true, substrate is epiphenomenal.

---

### Claim 2: Criticality Enables Complexity

> **Complex, stable, modifiable structures emerge preferentially when κ ≈ 1.**

**Measurable predictions:**

1. Sessions with $\bar{\kappa}$ near 1.0 exhibit:
   - Longer survival times
   - Higher structural complexity (cluster diversity, non-trivial static fraction)
   - Intermediate entropy (neither minimal nor maximal)

2. Perturbations in the critical regime:
   - Neither die instantly (subcritical response)
   - Nor explode globally (supercritical response)
   - But propagate locally and stabilize (critical response)

**Null hypothesis (falsification):**

Interesting structure (by any metric) occurs uniformly across all κ values, with no concentration near κ ≈ 1.

---

### Claim 3: Scale-Invariant Mechanism

> **The same causal structure — local rules on substrates producing emergent patterns — applies at every scale.**

| Scale | Substrate (G) | Rules (f) | Emergent Structures |
|-------|---------------|-----------|---------------------|
| Quantum | 3D lattice (hypothesized) | Unknown local rules | Atomic orbitals, particles |
| Chemical | Molecular geometry | Electron sharing rules | Molecules, bonds |
| Cellular | Cell membrane topology | Gene regulatory rules | Cell types, tissues |
| Neural | Synaptic connectivity | Firing threshold rules | Memories, thoughts |
| Cognitive | Neural architecture | Learned update rules | Consciousness, behavior |

**Note:** This is a structural claim about mechanism type, not a claim that the same f applies at each scale.

---

### Claim 4: Memory as Stable Structure

> **Memories are stable patterns (attractors) within a critical-state neural substrate.**

**Encoding:** Formation of new stable structure via activity-induced plasticity.

**Retrieval:** Re-execution of dynamics that regenerate the pattern (not file access).

**Modification:** Perturbation (new input) that restructures existing attractors.

**Measurable predictions (in CA model):**

1. Stable structures persist indefinitely in the absence of perturbation
2. Perturbation at structure boundaries → modification (structure shifts)
3. Perturbation far from structures → dissipation (no lasting change)
4. Perturbation inside structures → destruction or cascade (memory disruption)

---

### Claim 5: Consciousness as Coupled Layer

> **Consciousness is a coupled dynamical layer that modulates state transitions in a memory substrate.**

Formally:

Let $M$ be the memory substrate (slow dynamics, stable structures).  
Let $C$ be the consciousness layer (faster dynamics, responsive to input).

The coupling is a deterministic function:

$$\phi: \text{State}(C) \times \text{Input} \rightarrow \text{Perturbation}(M)$$

Where Perturbation(M) specifies which cells in M are flipped.

**Key properties:**
- C operates by local rules (not magic)
- φ is deterministic (not free will)
- The perturbation appears as "choice" from inside, but is fully determined by State(C) and Input

**This is explicitly not:**
- A homunculus
- An exception to determinism
- A different kind of causation

---

## 3. Experimental Protocol

### 3.1 Factorial Design: Substrate Effects

**Purpose:** Demonstrate that G materially affects outcomes for fixed f.

**Factors:**

| Factor | Levels |
|--------|--------|
| Topology (τ) | square, hexagon, triangle-edge, triangle-edge+vertex |
| Boundary (∂) | wrap (toroidal), clamp (fixed edges) |
| Size (\|V\|) | 64², 128², 256² (or equivalent node count) |
| Initial density (ρ₀) | 0.40 to 0.60, step 0.005 |
| Rule (f) | Conway (B3/S23), plus 2-3 high-criticality rules from GA |

**Replicates:** 20 runs per cell (different random seeds for x₀).

**Responses measured:**

| Metric | Description |
|--------|-------------|
| Outcome | {extinction, stable, oscillating, chaotic} |
| Survival time | Generations until extinction (or max) |
| $\bar{\kappa}$ | Mean branching ratio |
| $\bar{\rho}$ | Mean density |
| σ_ρ | Density variance |
| Static fraction | Proportion of stable cells |

**Analysis:**

1. Phase diagrams: (ρ₀, size) → outcome, per topology/boundary
2. Critical threshold identification: ρ* where P(extinction) = 0.5
3. ANOVA / regression: effect sizes for each factor
4. Interaction plots: does topology × size interaction exist?

**Success criterion:** Statistically significant effects of G on outcomes, beyond what f alone predicts.

---

### 3.2 Predictive Modeling: Substrate Necessity

**Purpose:** Quantify information gain from substrate vs rules alone.

**Method:**

Train two models to predict session outcome:

| Model | Features |
|-------|----------|
| Model A (rules only) | Birth rules, survival rules, max neighbors |
| Model B (full W) | Model A + grid size, topology, boundary, ρ₀ |

**Metrics:**

- Classification accuracy (outcome prediction)
- R² (survival time prediction)
- Feature importance ranking

**Success criterion:** Model B accuracy > Model A accuracy by meaningful margin (e.g., >10% lift).

---

### 3.3 Criticality Band Identification

**Purpose:** Demonstrate that κ ≈ 1 is a privileged regime.

**Method:**

1. Aggregate all sessions from 3.1
2. Bin by $\bar{\kappa}$: [0, 0.5), [0.5, 0.8), [0.8, 1.0), [1.0, 1.2), [1.2, 1.5), [1.5, 2.0), [2.0, ∞)
3. For each bin, compute:
   - Mean survival time
   - Structural complexity (cluster count, entropy)
   - Modification responsiveness (from 3.4)

**Success criterion:** Metrics peak or form Pareto-optimal front in κ ∈ [0.8, 1.2] band.

---

### 3.4 Perturbation Experiments: Memory Modification

**Purpose:** Test that stable structures behave like modifiable memories.

**Protocol:**

1. Run simulation until quasi-stable state (activity < ε for 100 generations)
2. Identify stable structures (connected components of static cells)
3. Apply single-cell perturbation at controlled locations:
   - Inside a stable structure
   - At structure boundary
   - Far from any structure (in dynamic region)
   - In empty space
4. Run for 500 additional generations
5. Measure:
   - Structure survival (did it persist?)
   - Structure edit distance (how much did it change?)
   - New structure formation (did perturbation seed growth?)
   - Cascade size (how far did perturbation propagate?)

**Predictions:**

| Perturbation Location | Expected Outcome |
|-----------------------|------------------|
| Inside structure | Destruction or major restructuring |
| At boundary | Modification (structure shifts) |
| In dynamic region | Absorbed by ongoing activity |
| In empty space | Dies (subcritical) or seeds new structure (supercritical) |

---

### 3.5 Finite-Size Scaling

**Purpose:** Confirm that critical thresholds are real phase transitions, not artifacts.

**Method:**

1. For each topology, identify critical density ρ* at each size
2. Plot ρ*(L) vs L (where L = linear dimension)
3. Fit to scaling form: $\rho^*(L) = \rho^*_\infty + aL^{-b}$

**Success criterion:** 

- ρ* converges to finite limit as L → ∞
- Transition sharpens with size (slope at ρ* increases)

**Failure mode:**

If "critical thresholds" don't sharpen or shift predictably with size, the phase-transition interpretation is weakened.

---

## 4. Speculation (Clearly Labeled)

The following are speculative extensions of the framework. They are not required for the core thesis to hold and should be evaluated independently.

### 4.1 Atomic Structure as Emergent Pattern

**Speculation:** Atomic orbitals (s, p, d, f) are stable structures in an underlying 3D lattice, possibly hexagonal close-packed.

**Milestone 1 (achievable):** Demonstrate that a 3D CA on HCP lattice produces stable structures with:
- Spherical symmetry (s-like)
- Axial symmetry with lobes (p-like)
- Multi-lobed structures (d-like, f-like)

**Milestone 2 (harder):** Show that "probability distributions" emerge from coarse-graining over hidden microstates — i.e., epistemic probability from deterministic dynamics.

**Milestone 3 (speculative):** Draw cautious analogies to quantum measurement.

**Note:** The core framework stands even if this speculation fails. Memory, cognition, and criticality claims are independent.

### 4.2 Probability as Observational Artifact

**Speculation:** What we call "probability" in physics is what deterministic dynamics looks like when:
- You can't observe the full microstate
- You measure at a coarser timescale than the update frequency
- Your measurement apparatus is itself part of the system

This is not a new idea (cf. Bohmian mechanics, 't Hooft's cellular automaton interpretation), but it follows naturally from the framework.

---

## 5. Falsification Criteria

The framework makes strong claims. Here is how it could be falsified:

| Claim | Falsification Condition |
|-------|------------------------|
| **Substrate co-equality** | Model A (rules only) predicts outcomes as well as Model B (full W). Adding substrate features provides no lift. |
| **Criticality enables complexity** | Interesting structure occurs uniformly across all κ values. No concentration in κ ≈ 1 band. |
| **Phase transitions are real** | Critical thresholds don't sharpen with system size. Finite-size scaling fails. |
| **Memory as stable structure** | Stable structures can't be modified by local perturbation — they're all-or-nothing. |
| **Consciousness as coupled layer** | Evidence of non-deterministic "choices" that can't be explained by prior state + input. (Note: This is hard to test in CA but relevant for neural application.) |

---

## 6. Relation to Prior Work

### 6.1 Agreements

| Work | Agreement |
|------|-----------|
| **Wolfram (NKS, Physics Project)** | Simple rules produce complex behavior; computation is fundamental |
| **Beggs & Plenz (2003)** | Neural systems operate near criticality; avalanche dynamics |
| **Kauffman (Origins of Order)** | Criticality at "edge of chaos" enables evolution and adaptation |
| **Friston (Free Energy Principle)** | Hierarchical dynamics; organisms minimize surprise |
| **Hopfield (Attractor Networks)** | Memory as stable states in dynamical systems |

### 6.2 Divergences

| Work | Divergence |
|------|------------|
| **Wolfram** | Wolfram seeks one fundamental rule f; this framework claims G is co-equal and there is no master rule |
| **Standard neuroscience** | Memory typically modeled as synaptic weights, not as emergent spatial structure |
| **Orthodox QM** | Probability treated as fundamental; this framework treats it as epistemic (speculation) |

---

## 7. Roadmap

### Phase 1: Infrastructure (Current)
- [x] Game of Life simulator with multiple topologies
- [x] Data recording with substrate parameters
- [x] Criticality metrics (κ, density, activity)
- [ ] 3D lattice support
- [ ] Automated experiment runner

### Phase 2: Core Experiments (Next)
- [ ] Factorial design (Section 3.1)
- [ ] Predictive modeling comparison (Section 3.2)
- [ ] Criticality band analysis (Section 3.3)
- [ ] Perturbation experiments (Section 3.4)

### Phase 3: Analysis & Writing
- [ ] Phase diagrams and statistical analysis
- [ ] Finite-size scaling
- [ ] Draft paper with results

### Phase 4: Extensions (Speculative)
- [ ] 3D hexagonal CA implementation
- [ ] Search for orbital-like structures
- [ ] Coarse-graining experiments

---

## 8. Conclusion

Local Rule Determinism proposes that reality at every scale consists of local rules operating on structured substrates, with outcomes determined by the full triple W = (G, f, x₀). This framework:

1. Makes substrate geometry co-equal with rules (diverging from Wolfram)
2. Identifies criticality (κ ≈ 1) as the regime enabling complex structure
3. Applies uniformly from atoms to cognition (same mechanism type, not same rules)
4. Treats consciousness as a coupled deterministic layer, not an exception
5. Offers falsifiable predictions testable with cellular automata experiments

The experimental program outlined here will either validate the framework or identify where it fails — which is what makes it science rather than philosophy.

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Substrate** | The graph structure on which rules operate (geometry, connectivity, boundaries) |
| **Local rule** | Update function depending only on a cell's immediate neighbors |
| **Criticality** | Operating regime where κ ≈ 1; activity neither dies nor explodes |
| **Branching ratio (κ)** | births / deaths; measure of activity propagation |
| **Attractor** | Stable or periodic state the system settles into |
| **Static cell** | Cell that has been alive for >10 generations |
| **Phase transition** | Sharp change in system behavior at a critical parameter value |

---

## Appendix B: Key Equations

**World triple:**
$$W = (G, f, x_0)$$

**Substrate specification:**
$$G = (V, E, \partial, \tau)$$

**Branching ratio:**
$$\kappa(t) = \frac{\text{births}(t)}{\max(\text{deaths}(t), 1)}$$

**Mean branching ratio:**
$$\bar{\kappa} = \frac{1}{T} \sum_{t=1}^{T} \kappa(t)$$

**Density:**
$$\rho(t) = \frac{|\{v \in V : x_t(v) = 1\}|}{|V|}$$

**Activity:**
$$\alpha(t) = |\rho(t) - \rho(t-1)|$$

**Finite-size scaling:**
$$\rho^*(L) = \rho^*_\infty + aL^{-b}$$

---

*End of document.*
