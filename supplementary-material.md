# Supplementary Material

## Supplementary Material A: Data-quality and credibility foundations

This appendix extends the epistemological grounding from the Introduction (see "Operationalizing knowledge: from JTB to contestable signals") to data-quality and credibility frameworks.

### A.1 Data quality dimensions

Industrial data quality frameworks — notably Wang & Strong (1996) — decompose quality into measurable dimensions. The following table maps key dimensions to protocol mechanisms:

| Quality dimension | Definition (Wang & Strong) | Protocol operationalization |
|---|---|---|
| **Accuracy** | Extent to which data is correct and reliable | Binary verdict via dispute resolution (Flow 3) |
| **Objectivity** | Extent to which data is unbiased and impartial | Separation of accuracy (evidence-based) from relevance (policy-guided); commit-reveal prevents herding |
| **Timeliness** | Extent to which data is current | Confidence score decays implicitly: stale claims become profitable challenge targets (temporal decay) |
| **Completeness** | Extent to which data is not missing | Claim templates enforce required fields; Under-specified verdict rejects incomplete claims |
| **Relevance** | Extent to which data is applicable to the task | Coherence game (Flow 4) produces a relevance score under a pool-specific curation policy |
| **Believability** | Extent to which data is regarded as credible | Confidence score accumulates as a function of bounty and uncontested time |
| **Consistency** | Extent to which data is coherent with other data | Coherence rule penalizes incoherent assessments |
| **Interpretability** | Extent to which data is in appropriate language/units | Claim schema requires explicit scope (time, jurisdiction, units/definitions) |

Not all dimensions are equally covered. **Reputation** (of the source) and **accessibility** (ease of retrieval) are partially addressed by the reputation system and interface layer, respectively, but remain weaker than the directly incentivized dimensions.

### A.2 Credibility checklist

Practical credibility frameworks (e.g., the CRAAP test used in information literacy) include accuracy, authority, objectivity, currency, and coverage/scope. In this design, these map to explicit protocol structures rather than implicit social signals:

- **Accuracy** → dispute resolution verdict
- **Authority** → reputation score, topic-scoped and non-transferable
- **Objectivity** → separation of powers (accuracy vs. relevance), commit-reveal voting
- **Currency** → temporal decay via challenge economics; confidence score rewards recency
- **Coverage** → evidence policy defines admissible sources; claim template requires scope

The key shift from traditional credibility assessment to this protocol is that credibility indicators become **verifiable on-chain** (stakes, verdicts, vote histories) rather than depending on the consumer's judgment of the source's trustworthiness. This does not eliminate the need for judgment — evidence policy design and pool governance still require it — but it makes the judgment auditable.
