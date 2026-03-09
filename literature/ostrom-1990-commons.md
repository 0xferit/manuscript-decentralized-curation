# Ostrom (1990): Governing the Commons

**Citation**: Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for Collective Action*. Cambridge University Press. doi:10.1017/CBO9780511807763

## Core thesis

Neither privatization nor state regulation is necessary to manage common-pool resources. Communities can and do self-govern shared resources through institutional arrangements that emerge from local context. The key is institutional design: rules about access, use, monitoring, and sanctions that are crafted by the participants themselves.

## Key concepts

- **Common-pool resources (CPRs)**: resources where exclusion is difficult and one person's use diminishes availability for others (e.g., fisheries, irrigation systems, forests).
- **Design principles for long-enduring CPR institutions**: Ostrom identifies 8 principles, including clearly defined boundaries, congruence between rules and local conditions, collective-choice arrangements, monitoring, graduated sanctions, conflict-resolution mechanisms, and nested enterprises.
- **Polycentric governance**: multiple, overlapping centers of decision-making rather than a single authority. Each center has limited scope and participants can move between centers.
- **Rejection of the "tragedy of the commons" as inevitable**: Hardin's tragedy assumes no institutional design is possible. Ostrom shows this is empirically false.

## Connection to our paper

Ostrom provides the governance backdrop for our system design:

- **Pools as self-governing institutions**: our curation pools parallel Ostrom's CPR institutions. Each pool has defined boundaries (topic scope), rules (curation policy, evidence policy), monitoring (validators), graduated sanctions (slashing), and conflict resolution (DDR).
- **Polycentric structure**: multiple pools with independent policies is a polycentric design. No single pool controls the knowledge layer; competition between pools provides a check.
- **Graduated sanctions**: Ostrom emphasizes that first-time violators should face mild sanctions, with escalation for repeat offenders. Our reputation mechanism does something similar: initial stake is financial, but accumulated reputation (non-transferable, topic-scoped) creates graduated consequences.
- **Collective-choice arrangements**: pool governance (parameter updates, policy changes) maps to Ostrom's principle that those affected by rules should participate in modifying them.

## Key passages worth keeping

> "What one can observe in the world ... is that neither the state nor the market is uniformly successful in enabling individuals to sustain long-term, productive use of natural resource systems." (p. 1)

Maps to our argument: neither centralized curation (state-like) nor pure market mechanisms (engagement optimization) have solved information quality.

## Limitations relevant to us

- Ostrom's cases involve small-to-medium communities with face-to-face interaction. Decentralized curation at internet scale does not have this property. Whether Ostrom's design principles transfer to pseudonymous, global communities is an open question.
- Ostrom's monitoring relies on community members who can observe each other's behavior. Our monitoring is mechanical (on-chain stakes, commit-reveal). The social dynamics are different.
- The "graduated sanctions" parallel is imperfect: Ostrom's sanctions are social (shaming, exclusion), ours are economic (slashing). Economic sanctions may not create the same normative compliance.
