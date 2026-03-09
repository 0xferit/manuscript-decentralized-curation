# Prelec (2004): A Bayesian Truth Serum for Subjective Data

**Citation**: Prelec, D. (2004). A Bayesian Truth Serum for Subjective Data. *Science*, 306(5695), 462-466. doi:10.1126/science.1102081

## Core thesis

Proposes a mechanism for eliciting truthful reports about subjective quantities (opinions, experiences) without requiring ground truth verification. The mechanism rewards reports that are "surprisingly common": if your report is more common among respondents than you predicted it would be, you score higher. Under certain Bayesian assumptions, truthful reporting is a Nash equilibrium.

## Key concepts

- **Bayesian Truth Serum (BTS)**: respondents provide both (1) their own answer and (2) their prediction of the distribution of others' answers. The scoring rule rewards answers that are "surprisingly common" relative to predicted frequencies.
- **No ground truth required**: unlike our dispute mechanism, BTS does not need an external fact to verify against. It extracts truth from the structure of predictions.
- **Bayesian assumptions**: agents are assumed to be Bayesian reasoners with a common prior, updating on private signals. The equilibrium depends on this assumption holding.

## Connection to our paper

BTS is an alternative approach to truthful elicitation that we considered and implicitly rejected:

- **Why not BTS for accuracy?**: our accuracy dimension has ground truth (or at least an evidence standard). BTS is designed for settings without ground truth. Using BTS for factual claims would be over-engineered: binary dispute resolution is simpler and exploits the existence of evidence.
- **Why not BTS for relevance?**: relevance is subjective (closer to BTS's target domain), but BTS requires respondents to predict the distribution of others' answers. In our coherence game, curators rate policy conformity against a public curation policy. The curation policy serves as the focal point, making BTS's prediction mechanism unnecessary: the policy *is* the coordination device.
- **Theoretical positioning**: BTS, peer prediction (Miller 2005), and our coherence game are all answers to "how do you elicit truthful reports without centralized verification?" Our design choices are driven by the specific structure of our problem (binary accuracy + policy-guided relevance), not by BTS being wrong in general.

## Limitations

- BTS assumes common priors and Bayesian rationality. These are strong assumptions, especially for diverse, pseudonymous populations.
- The mechanism is complex for respondents: they must provide both an answer and a distributional prediction. Our coherence game requires only a single scalar rating.
- Empirical validations of BTS are limited. The mechanism is theoretically elegant but has seen less real-world deployment than simpler Schelling games.
