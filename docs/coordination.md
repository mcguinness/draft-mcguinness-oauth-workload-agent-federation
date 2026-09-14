<a id="coordination"></a>

# Specification ownership and coordination

The draft's [Upstream Gaps and Proposed Changes](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#upstream-gaps) is the authoritative proposal set for discussion. Each item contains the problem, owning specification, proposed change, and observable closure criteria. This index adds no protocol requirements.

Federation owns the additional requirements it can define through existing extension points. ATTEST is consumed as written, including its profiling provisions; changing a specification in Last Call is not a prerequisite for implementing Federation. Only the upstream proposal table below awaits agreement. Inclusion here does not mean an issue, pull request, or specification change has been accepted.

## Requirements defined in Federation

| Requirement | Local definition | Base contract |
|---|---|---|
| Mode selection and shared-client agent evidence | [Client Attestation profile](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#agent-evidence) | ATTEST additional claims and profile selection; original client `sub`, `typ`, and proofs |
| `attested_agent_id` semantics and registration | [Shared-client processing](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#attest-gap) | Claim carried in the validated Client Attestation; registration requested by Federation |
| Proof selection, current-policy checks, and renewal | [Proof requirements](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#attest-proof) | Existing ATTEST authentication methods and error handling |
| Client restrictions on approved attesters | [Attester trust](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#trust-gap) | Authenticated configuration; no new ATTEST discovery requirement |
| Bearer assurance, key roles, reuse, and configured capability selection | [Credential use](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#credential-requirements) | Existing SPIFFE, WIMSE, ATTEST, and DPoP mechanisms |

## Upstream proposals

| Item | Owner | Draft proposal |
|---|---|---|
| WAG issuance by an IdP with a governed subject | WAG; Federation supplies the mapping | [Issuance and identity ownership](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-issuance-gap) |
| WAG token type, JWT typing, and discovery | WAG and identity chaining | [Identifiers](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-identifiers-gap) |
| Bound WAG, audience, errors, and replay | WAG with ID-JAG and DPoP | [Sender constraint](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-binding-gap) |
| Scope/resource ceilings and continuing access | WAG and ID-JAG | [Authority and refresh](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-lifecycle-gap) |
| Direct external evidence to governed actor | Actor Profile | [Mapped actor construction](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#actor-gap) |
| User subject with mapped actor evidence | ID-JAG and Actor Profile | [ID-JAG composition](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#id-jag-gap) |
| X.509-SVID connection evidence in issuance | SPIFFE OAuth and consuming profiles | [X.509-SVID](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#x509-gap) |
| Additional proof mechanisms and generic discovery | Separate extensions and consuming profiles | [Additional capabilities](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#credential-gap) |
| Continuity and context propagation | Identification and consuming profiles | [Instance context](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#instance-identification) |
| Properties, provisioning, and disablement | Provisioning/lifecycle work | [Lifecycle](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#lifecycle-gap) |

## Coordination order

1. Agree the ownership and semantics of WAG issuance and direct actor mapping. These determine the grant paths Federation can actually compose.
2. Settle the corresponding identifiers, proof relationships, and capability signals in those owning specifications.
3. Use the draft's closure criteria and the [interoperability cases](interoperability.md) to check independent implementations.
4. Replace each resolved upstream proposal with a reference to the adopted rule. Add complete grant-flow examples when that composition is defined. Federation-owned credential requirements and examples can be implemented independently.

Federation defines its own narrowly scoped attested-agent claim and requests its registration. It does not introduce a replacement grant, mandatory adapter token, or first-use key-enrollment protocol to resolve the separate grant-composition proposals.
