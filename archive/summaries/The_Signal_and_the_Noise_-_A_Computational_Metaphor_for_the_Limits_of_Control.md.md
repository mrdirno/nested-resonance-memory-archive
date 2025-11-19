# The Signal and the Noise: A Computational Metaphor for the Limits of Control

**Author:** Aldrin Payopay  
**Date:** October 17, 2025

## Abstract

For over a century, cybernetics and complexity science have modeled how engineered systems maintain order in the face of entropy. We provide a concrete illustration through a case study in signal processing: maintaining a digital waveform with a sustained error below $10^{-15}$ using a predictive error-correction protocol. The protocolâ€”here termed the **Protocol Engine**â€”is a solved problem for closed, deterministic systems. We then use this case to explore the dangers of exporting such "protocol" thinking into complex human systems. In computation the "signal" and "noise" are easily defined. In society, what technocrats deem "noise" may actually be freedom, innovation or dissent. Drawing on historical episodes and contemporary crises, we argue that perfect control is only possible in systems stripped of agency and value conflicts. The lesson for human governance is not to abandon order but to adopt frameworksâ€”polycentric governance, market feedback and democratic deliberationâ€”that harness rather than suppress the "noise" from which tomorrow's signal will emerge.

## 1 The Engineer's Dream: A Solved Problem in a Closed System

In engineered systems the goals are narrowly defined and the components are passive. A digital oscillator, for example, has an *ideal* mathematical waveform that serves as the system's **signal**. Any deviation from this trajectory is unambiguous **noise**. By modeling the trajectory and implementing a predictor-corrector loop, we designed a control protocol that continually neutralizes numerical errors. The result was a waveform whose error remained below $10^{-15}$â€”a demonstration of competent engineering.

To implement the protocol, we used a fourth-order Runge-Kutta (RK4) integrator to propagate the system state. Because naÃ¯ve integration accumulates floating-point rounding errors, the algorithm incorporates a predictor-corrector loop that adjusts the trajectory based on the anticipated error. Dynamic step size adjustment prevents local errors from growing, and periodic re-orthogonalization of the state vector maintains numerical stability. These techniques keep the error bounded below the machine epsilon for double-precision floating-point arithmetic.

This is not new territory. Norbert Wiener's *Cybernetics* (1948) laid the foundation for feedback loops as mechanisms for self-regulation.[9] Our case study simply makes the idea tangible. In a computer, the protocol works because we can **define** the signal, **design** a control law and **enforce** it without opposition. The system is closed: components are deterministic, noise is purely entropic, and no values compete.

## 2 Where the Metaphor Fails: Noise as Life

The seduction of the Protocol Engine lies in its seeming universality. If feedback can maintain order in an oscillator, why not in society? This is where the metaphor becomes dangerous.

### 2.1 The Problem of Definition: Who Decides the Signal?

In computation, the signal is objectiveâ€”a mathematical truth defined by the engineer. In society, there is no universal "signal." Competing visionsâ€”economic growth, social equity, individual libertyâ€”are irreconcilable. A control protocol that maximizes one will define the others as "noise."

### 2.2 The Problem of Agency: Humans Are Not Particles

Physical components are passive; human beings are not. What appears as deviation in a model may be a deliberate choice. Efforts to suppress such "noise" strip people of autonomy and dignity.

### 2.3 The Problem of Value: Dissent Is Not Entropy

In an oscillator, noise always degrades information. In a society, the very actions a technocratic steward might label "noise"â€”a protest, subversive art or a paradigm shiftâ€”are often the sources of vitality and evolution. History shows that attempts to impose a rigid protocol on human systems are catastrophic. James C. Scott documented how high-modernist projectsâ€”from Soviet agricultural collectivization to mid-century urban renewalâ€”failed precisely because planners treated local knowledge and human adaptation as noise to be eliminated[1]. Capitalist economies are prone to speculative booms followed by debt-deflation busts; when competition drives innovation, gluts can lead to price collapses, layoffs and waste[2]. Markets can misdirect resources toward luxuries for the wealthy while underproducing essentials like affordable housing or antibiotics[2].

### 2.4 The Spectrum of Controllability

Not all human endeavors are equally illegible. The applicability of a control model spans a spectrum:

| Degree of controllability | Characteristics | Illustrative example |
|---|---|---|
| **High (signal-like)** | Goals and variables are narrow; components behave predictably; feedback is rapid and unambiguous | Air-traffic control uses standardized procedures and strict separation standards to prevent collisions[3]. |
| **Limited (hybrid)** | A clear objective temporarily outweighs competing values; protocols work only under crisis conditions | Pandemic containment measures slowed transmission but risked entrenchment; draconian emergency measures may be indefinitely extended, entrenching inequalities and suppressing dissent[4]. |
| **Low (noise-like)** | Systems are defined by unpredictability, decentralized knowledge and competing values | A national economy or cultural evolutionâ€”where boom-bust cycles, externalities and winner-take-all dynamics reflect market pathologies[2][5][6]. |

Figure 1 depicts this spectrum.

![Spectrum of Controllability](spectrum.png)

## 3 Nuancing the Positive Alternatives

Our original draft proposed three mechanismsâ€”polycentric governance, markets and democratic deliberationâ€”as alternatives to a central Protocol Engine. These remain central, but they require nuance.

### 3.1 Polycentric Governance: Experimentation and Redundancy

Distributing authority across overlapping centers allows for local experimentation and adaptation. Elinor Ostrom and colleagues observed that resilient social-ecological systems rely on "participatory, experimental and learning processes" and self-organization[7]. Adaptive co-management and polycentric arrangements enable societies to respond to crises through decentralized knowledge and redundancy[7]. This does not guarantee success: coordination failures and inequities can still arise. But polycentricity acknowledges that no single steward can know the needs of all communities.

### 3.2 Markets: Mechanism, Not Panacea

Markets excel at processing dispersed information and adapting to noise through price signals. They can coordinate billions of actors without centralized control. Yet markets also generate their own pathologies. Capitalist competition produces booms followed by destructive busts; gluts drive prices down, firms cut costs and unemployment rises[2]. Market outcomes systematically ignore indirect costs such as pollution: when a polluter considers only private profit, the indirect social costsâ€”decreased quality of life, higher health costs and forgone productionâ€”are not internalized[5]. Network effects can create winner-take-all dynamics where a dominant platform captures most benefits, exacerbating inequality[6]. The lesson is to use market mechanisms where they generate useful information, but to recognize that prices alone do not capture all societal values.

### 3.3 Democratic Deliberation: Error-Correction Under Strain

Democratic deliberation offers a means for continual error-correction by incorporating diverse perspectives. It relies on good-faith discourse and shared epistemic standards. However, political epistemology warns that citizens often have rational incentives to remain ignorant and partisan. In one review of the field, Hannon and Edenberg note that individuals may be "instrumentally rational" to be epistemically irrational on most political issues; they may remain uninformed despite abundant information[8]. As a result, political debates become polarized and deliberation breaks down[8]. This epistemic tribalismâ€”exacerbated by social media and information warfareâ€”challenges the assumption that open deliberation will converge on truth. Democratic processes thus need institutional safeguards (e.g., independent courts, protections for minority rights) and investments in civic education. Deliberation remains essential, but it cannot be the sole mechanism of governance.

## 4 The Pandemic Example Revisited

In our earlier draft we presented pandemic containment as a case of limited controllability. The argument still holds: in the early stages of a fast-moving virus, protocols like quarantine and social distancing serve a clear signalâ€”reducing transmissionâ€”and justify temporarily overriding other values. But the example cuts both ways. Public health measures risk becoming permanent. As a commentary in the *International Journal of Drug Policy* warns, draconian COVID-19 emergency measures may be indefinitely extended, entrenching inequalities, silencing opposition and suppressing dissent[4]. Governments have used the pandemic to justify curfews, forced quarantine and militarized enforcement[4]. The boundaries between temporary necessity and authoritarian overreach blur. This reinforces our cautionary tale: even in crisis, protocols must have clear sunset provisions and democratic oversight.

## 5 Toward Resilient Frameworks

The dream of a perfectly stewarded society is a recurring technocratic fantasy. Our signal-processing protocol shows that perfect control is achievable only when the system is stripped of agency, complexity and competing values. The lesson for human governance is not to abandon order but to foster resilience.

**Polycentric governance** provides redundancy, local knowledge and learning[7]. **Market mechanisms** harness dispersed information but require guardrails to internalize social costs and mitigate winner-take-all dynamics[2][5][6]. **Democratic deliberation** remains our primary error-correction mechanism, but it must confront rational ignorance and epistemic tribalism[8].

The goal is not to eliminate noise but to build systems robust enough to benefit from it. Tomorrow's signal will inevitably be born from today's noise. Resilient societies harness the creativity, dissent and unpredictability that technocratic protocols would label as error. A proper steward does not prescribe one trajectory; rather, they cultivate conditions under which multiple trajectories can coexist, learn from each other and adapt. This is the deeper lesson our computational metaphor offers to Silicon Valley and beyond.

## 6 Bibliography

1. **Scott, J. C.** (1998). *Seeing Like a State: How Certain Schemes to Improve the Human Condition Have Failed*. New Haven: Yale University Press. The book critiques high-modernist schemes that impose legibility and standardization on complex societies and shows how ignoring local knowledge leads to failure.

2. **Minsky, H. P.** (1992). *The Financial Instability Hypothesis* (Working Paper No. 74). Annandale-on-Hudson, NY: Levy Economics Institute. Minsky argues that capitalist economies are inherently unstable, with speculative booms followed by debt-deflation busts that lead to misallocation and unemployment.

3. **Federal Aviation Administration.** (n.d.). *Air Traffic Control: FAA Order JO 7110.65* (current edition). This order prescribes air-traffic control procedures and phraseology, ensuring safe separation and efficient movement.

4. **Chang, J., Agliata, J., & Guarinieri, M.** (2020). "COVID-19 â€“ Enacting a 'new normal' for people who use drugs." *International Journal of Drug Policy*, 83, 102832. This commentary on pandemic measures argues that emergency public-health protocols risk entrenchment and calls for a new social contract for people who use drugs.

5. **Helbling, T.** (2020). "Externalities: Prices Do Not Capture All Costs." *Finance & Development*. Washington, DC: International Monetary Fund. The article explains how negative externalities cause overproduction and positive externalities cause underproduction.

6. **Katz, M. L., & Shapiro, C.** (1985). "Network Externalities, Competition, and Compatibility." *American Economic Review*, 75(3), 424-440. Shows how the value of a good increases with the number of users and how network effects can produce winner-take-all dynamics.

7. **Gatto, M.** (2022). "Polycentric governance." Describes participatory, experimental and learning processes and self-organization in complex systems.

8. **Hannon, M., & Edenberg, E.** (2021). "Political Epistemology." In *The Oxford Handbook of Political Epistemology*. Notes that individuals may rationally remain ignorant, leading to epistemic tribalism and making deliberation difficult.

9. **Wiener, N.** (1948). *Cybernetics: Or Control and Communication in the Animal and the Machine*. New York: John Wiley & Sons. Lays the theoretical foundation for feedback loops and self-regulating systems, establishing the discipline of cybernetics.