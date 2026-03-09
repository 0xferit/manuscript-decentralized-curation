# Wang & Strong (1996): Beyond Accuracy

**Citation**: Wang, R. Y., & Strong, D. M. (1996). Beyond Accuracy: What Data Quality Means to Data Consumers. *Journal of Management Information Systems*, 12(4), 5-33.

## Core thesis

Data quality is not a single dimension. Through empirical research (surveys of data consumers), Wang and Strong identify that data quality decomposes into multiple dimensions grouped into four categories: intrinsic (accuracy, objectivity, believability, reputation), contextual (relevance, timeliness, completeness, value-added, amount), representational (interpretability, ease of understanding, conciseness, consistency), and accessibility (accessibility, security).

## Key concepts

- **Multi-dimensional quality**: the central contribution. "Quality" is not one thing; it is many things, and different consumers weight them differently.
- **Intrinsic vs. contextual**: accuracy is intrinsic (independent of the use context); relevance is contextual (depends on who uses it, when, and for what). This distinction is structural, not a matter of preference.
- **Consumer-centric definition**: quality is defined by what matters to the consumer, not by abstract properties of the data itself.

## Connection to our paper

Wang and Strong provide the methodological precedent for our quality identification step (Step 3 of the framework):

- **Accuracy vs. relevance decomposition**: our decomposition of news quality into accuracy (global, binary) and relevance (local, non-binary) maps directly to Wang and Strong's intrinsic vs. contextual categories. Accuracy is intrinsic: a claim is valid or invalid regardless of who reads it. Relevance is contextual: importance depends on the reader, the pool's curation policy, and the moment.
- **"Collapsing into a single metric is the design flaw"**: Wang and Strong's empirical finding that quality is multi-dimensional supports our argument that collapsing accuracy and relevance into a single engagement metric (as platforms do) is a design flaw, not an implementation detail. It is not that platforms failed to optimize a single metric well; it is that a single metric cannot capture multi-dimensional quality.
- **Domain-agnostic methodology**: Wang and Strong's approach (survey consumers, identify dimensions, categorize) is domain-agnostic. Our framework's quality identification step is a version of this: decompose quality for the specific domain, then design mechanisms for each dimension.

## Limitations relevant to us

- Wang and Strong's dimensions are empirically derived from surveys, not from mechanism design constraints. Some of their dimensions (e.g., "believability," "reputation") are not directly operationalizable in a decentralized protocol.
- Their taxonomy is descriptive, not prescriptive. It tells you what dimensions exist but not which ones to prioritize or how to enforce them. Our framework adds the prescriptive step: once you identify dimensions, design distinct mechanisms for each.
- The 1996 context (enterprise data management) is very different from 2026 information curation. The dimensions may differ, but the methodology (decompose quality, do not treat it as one-dimensional) is durable.
