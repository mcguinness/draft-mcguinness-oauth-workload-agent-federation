# Interoperability and upstream closure cases

The first two tables test Federation's identity, authorization, and Client Attestation profile requirements. The remaining tables are acceptance criteria for proposed upstream changes. They are not claims that this draft defines those wire behaviors today.

## Current Federation requirements

| Case | Required outcome |
|---|---|
| Valid credential with one active, enabled exact binding | Resolve the configured Registered Agent |
| Missing, ambiguous, inactive, or disabled binding | Do not issue authorization for that agent |
| Unverified issuer URL, request hint, or client metadata proposes another authority | Does not establish credential-authority trust |
| Same `kid` under unrelated issuers or SPIFFE trust domains | Verify only with keys authorized for the selected authority |
| Client registration permits several workload identities | Resolve the exact authenticated workload; do not map the whole prefix to one agent implicitly |
| Valid client authentication without a governed-agent binding | Does not establish agent identity |
| Shared-client ATTEST without the required signed `iss` or `attested_agent_id` | Reject under the Federation profile; no fallback to own-client mapping |
| Unknown `agent_id` claim or request parameter | Follow base ignore rules; do not switch models or select an agent |
| Valid JWT-SVID without `iss` or `iat` | No rejection solely for their absence; validate under SPIFFE OAuth |
| SPIFFE credential renewal with unchanged workload identity | Revalidate credential and proofs; do not infer a new authorization principal |
| Bearer workload JWT with a valid DPoP proof | Do not treat the DPoP key as platform-endorsed |
| Valid user and agent credentials without delegation approval | Do not issue delegated authorization |
| Approval applies to another agent behind the same client | Does not authorize this agent |
| Requested authority exceeds assignments, user authority, or delegation | Do not authorize excess authority |
| Grant mechanism cannot represent the required governed actor | Do not drop or relabel the actor to obtain a token |
| Same bare subject from a different issuer | Do not correlate records solely on the bare identifier |
| User and agent properties coexist | Preserve their principal associations |
| Agent disabled or binding withdrawn after cached authorization | Apply current status and configured freshness limits before new issuance |

## Client Attestation profile requirements

These checks apply to the profile defined here; they do not await ATTEST changes.

| Case | Required outcome |
|---|---|
| Two signed agent identifiers under one attester/client | Resolve each exact tuple to its own approved agent |
| `attested_agent_id` absent, empty, non-string, or present only in the proof/request | `invalid_client_attestation` for missing or invalid attested agent evidence |
| `iss` absent, empty, incorrectly typed, or not authorized for the signing key | Reject; no new attester trust from the claim |
| Same client and agent strings under another attester | Distinct namespace; no reuse of the first attester's binding |
| Attester/client pair serves several platform tenants | Agent identifiers distinguish tenants, or distinct attester namespaces are used |
| Configured shared-client request fails profile validation | No downgrade to own-client mapping or weaker proof mode |
| Own-client attestation contains `attested_agent_id` | Does not switch mode or override its configured client-to-agent binding |
| Base ATTEST validator ignores the claim | Client authentication alone does not establish shared-client Federation support |
| Combined DPoP mode uses a different key from `cnf.jwk` | Reject under ATTEST's key-matching rules |
| Normal ATTEST PoP plus a separately keyed DPoP proof | Validate each role; do not claim attester endorsement of the DPoP key |
| Separate key used where grant policy requires an attested output key | Reject the unsupported key binding |
| Profile claim missing while base timestamp claims are valid | Reject for the profile claim; missing optional attestation `iat` alone is not the cause |
| Attestation becomes stale or a proof needs a challenge | ATTEST's freshness/challenge error and response behavior applies |
| Well-formed agent attestation has no active authorized binding | Fail the Federation decision using the consuming profile's applicable error |
| Renewed attestation authorizes a replacement key | Revalidate attestation, proof, and current policy; identifier continuity alone is insufficient |
| Client restriction and IdP-approved attesters have no overlap | Reject; client configuration cannot expand IdP trust |
| Unsupported discovery composition | Require trusted configuration before use; do not invent a metadata value |

## WAG closure cases

Pending [WAG proposals](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wag-gaps):

| Case | Evidence that the upstream gap is closed |
|---|---|
| Platform and IdP issuance of the same grant family | WAG defines each issuer's role and the subject/property namespace |
| External workload maps to a different governed identifier | WAG issuance accepts Federation's resolution without an extra normalization token |
| Independent client selects a WAG output | Uses identifiers and discovery specified and registered by WAG |
| Grant stolen without the binding key | Bound WAG cannot be redeemed |
| Issuance credential key differs from output proof key | Agreed proof relationship determines acceptance; no implicit rebinding |
| Wrong RAS audience or cross-issuer key substitution | Rejected under the WAG validation contract |
| Concurrent redemption and nonce retry | Agreed single-use/retry behavior is enforced atomically where applicable |
| Requested resource/scope exceeds the grant | RAS does not expand the authorized ceiling |
| Required constraint is absent or unsupported | Defined error; no silent broadening |
| Continuing workload access | WAG defines whether fresh issuance or refresh is allowed and what must be rechecked |
| Current WAG refresh prohibition is unchanged | Federation supplies no local exception |

## Actor Profile and ID-JAG closure cases

Pending [direct mapped-actor processing](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#actor-gap) and [ID-JAG composition](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#id-jag-gap):

| Case | Evidence that the upstream gap is closed |
|---|---|
| Own-client agent, imported workload, and shared-client agent | All construct the intended canonical actor through defined evidence and mapping rules |
| Credential subject differs from governed actor identifier | Actor Profile explicitly defines how the mapping composes with subject-copying rules |
| One JWT is used for authentication and actor evidence | The consuming profile specifies allowed dual use, exact-token matching, and proof checks |
| Existing canonical actor credential | Existing valid input remains usable without acquiring a new token class |
| Missing or ambiguous mapping | Defined rejection, with no fallback to client identity |
| Input carries an existing actor chain | No silent actor rewriting or chain replacement |
| Coarse JWT actor support advertised | Does not imply every credential class, mapped identity, or proof mode |
| Actor Profile and identity-chaining metadata overlap | Their relationship identifies the supported ID-JAG composition consistently |
| Unsupported user/actor/output combination | Defined error instead of a hidden adapter-acquisition path |

## Credential and lifecycle closure cases

| Case | Proposed owner | Required upstream decision |
|---|---|---|
| X.509-SVID connection supplies agent evidence | SPIFFE OAuth and consuming profiles | Explicit subject/actor request binding without fabricated JWT evidence |
| X.509-SVID TLS key differs from DPoP key | SPIFFE OAuth and grant profile | Proof relationship and permitted output binding |
| Additional WIT/ATTEST proof integration is proposed | Credential extensions and consuming profiles | Define any new composition using existing extension facilities; no ATTEST revision prerequisite |
| Cached bearer JWT reaches two replicas with independent keys | Credential and consuming profiles | Defined reuse/assurance rules, not a Federation-specific first-use cache |
| Bearer credential is stolen before first use | Credential and consuming profiles | Explicit limitation or independently established holder binding |
| Execution restarts or changes keys | Identification and platform evidence | Evidence-based continuity, enrollment, and replacement semantics |
| Subject becomes an actor, or the actor changes | Consuming instance profile | Whose context is retained, replaced, or omitted |
| Disablement signal is delayed, duplicated, or missed | Provisioning/lifecycle work | Freshness, ordering, recovery, and effect on issued tokens |
