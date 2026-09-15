<a id="coordination"></a>

# Specification ownership and remaining coordination

The main draft defines a complete [delegated flow](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-flow) using ID-JAG's actor extension point. It specifies credential validation, governed-actor mapping, sender binding, token requests and responses, errors, metadata, RAS redemption, and API processing.

The optional `instance_attestation` input reuses [Client Instance Identification](https://github.com/mcguinness/draft-mcguinness-oauth-client-instance-assertion/blob/main/draft-mcguinness-oauth-client-instance-id.md). Identification owns the attested instance claims, receiver scoping, continuity, and validation rules. Federation defines the approved instance-to-agent mapping, authenticated client association, and separate delegation decision. The required platform-JWT and own-client attestation paths do not depend on Identification.

## Ownership

| Topic | Home |
|---|---|
| Direct credential to governed actor in ID-JAG | Main draft's [actor construction](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#actor-construction), defined under ID-JAG §9.7 |
| Token exchange, redemption, errors, and metadata | Main draft's [delegated flow](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-flow) |
| Actor-object structure and resource policy | Normatively selected sections of Actor Profile; the main draft does not claim its different Section 6.3 copying algorithm |
| Instance identity and lifecycle | Identification's `client_instance_id`, trust, receiver scoping, and continuity rules |
| Instance-to-agent resolution | Main draft's [instance-to-agent composition](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#instance-agent-resolution); several instances may map to one governed agent |
| Protocol requirements and problem/ask summaries | The main draft |
| Conformance scenarios and closure criteria | [Interoperability cases](interoperability.md), maintained only in this repository |

## Remaining requests

| Problem | Specific ask and proposed home | Status |
|---|---|---|
| Self-acting WAG composition | WAG defines IdP issuance inputs, governed subject namespace, its identifiers, sender constraint, audience/replay policy, authority limits, and continuing access | Deferred; [summary](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-gaps) |
| Reusable governed-actor mapping | Actor Profile considers a general principal-resolution extension point | Consolidation; the delegated flow already defines its mapping and is not blocked |
| X.509-SVID alone supplies actor evidence | A consuming profile defines how connection evidence binds the actor request and output key, coordinated with SPIFFE OAuth | Not defined here; X.509 client authentication with a separate actor JWT is usable |
| Direct WIT-SVID actor presentation | A future revision of this profile can compose the existing SPIFFE/ATTEST proof with actor presentation; it must choose the DPoP key relationship and respect WIT's prohibition on key use after credential expiry | Local scope deferral, not a missing upstream proof primitive; native client authentication remains usable |
| Downstream instance context | This consuming profile must define how Identification's optional context follows the actor through ID-JAG and access-token issuance, with provenance and receiver-scoping rules | Identity resolution is defined; downstream context propagation remains deferred |
| Cross-system disablement | Future provisioning/lifecycle specifications define correlation, freshness, ordering, recovery, and outstanding-token effects | Future work |

WAG §5 already anticipates IdP issuance through exchange. Its gap is the detailed contract, not permission for the IdP to issue. The draft retains WAG's current refresh prohibition for that deferred path and defines no replacement grant.

These remaining requests do not imply upstream acceptance. Changes to another specification's base semantics need agreement there; requirements permitted by existing extension points are defined in the consuming profile.

One instance hosting several governed agents does not supply an unambiguous agent selector. The instance input rejects ambiguous bindings; such a deployment needs a supported credential that distinguishes the selected agent. No additional agent claim is registered speculatively. Instance continuity and an approved mapping do not confer delegation or move an existing grant to a replacement key.

The main draft bounds its optional RAS refresh exception locally: rotation and grant reuse cannot extend the configured continuation deadline without renewed IdP authorization. That bound does not replace the still-needed cross-system status and revocation mechanisms.
