<a id="coordination"></a>

# Upstream coordination index

The draft's [Upstream Gaps and Proposed Changes](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#upstream-gaps) is the authoritative proposal set for discussion. Each item contains the problem, owning specification, proposed change, and observable closure criteria. This index adds no protocol requirements.

All items below are proposals awaiting upstream agreement. Inclusion here does not mean an upstream issue, pull request, or specification change has been accepted.

| Item | Owner | Draft proposal |
|---|---|---|
| WAG issuance by an IdP with a governed subject | WAG; Federation supplies the mapping | [Issuance and identity ownership](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-issuance-gap) |
| WAG token type, JWT typing, and discovery | WAG and identity chaining | [Identifiers](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-identifiers-gap) |
| Bound WAG, audience, errors, and replay | WAG with ID-JAG and DPoP | [Sender constraint](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-binding-gap) |
| Scope/resource ceilings and continuing access | WAG and ID-JAG | [Authority and refresh](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-lifecycle-gap) |
| Direct external evidence to governed actor | Actor Profile | [Mapped actor construction](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#actor-gap) |
| User subject with mapped actor evidence | ID-JAG and Actor Profile | [ID-JAG composition](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#id-jag-gap) |
| X.509-SVID connection evidence in issuance | SPIFFE OAuth and consuming profiles | [X.509-SVID](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#x509-gap) |
| Agent evidence behind a shared client | ATTEST or a focused ATTEST extension | [Shared-agent evidence](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#attest-gap) |
| Proof modes, bearer reuse, and discovery | SPIFFE OAuth, WIMSE, ATTEST | [Credential composition](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#credential-gap) |
| Client restrictions on approved attesters | Federation configuration; ATTEST trust work if discovery is needed | [Trust relationship](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#trust-gap) |
| Continuity and context propagation | Identification and consuming profiles | [Instance context](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#instance-identification) |
| Properties, provisioning, and disablement | Provisioning/lifecycle work | [Lifecycle](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#lifecycle-gap) |

## Coordination order

1. Agree the ownership and semantics of WAG issuance and direct actor mapping. These determine the grant paths Federation can actually compose.
2. Settle the corresponding identifiers, proof relationships, and capability signals in those owning specifications.
3. Use the draft's closure criteria and the [interoperability cases](interoperability.md) to check independent implementations.
4. Replace each resolved proposal with a reference to the adopted upstream rule. Only then add complete wire examples and conformance requirements for that composition.

The earlier replacement grant, mandatory adapter access token, shared-agent claim registration, and first-use key-association protocol have been removed. Their implementation details are not alternate ways to satisfy the open proposals.
