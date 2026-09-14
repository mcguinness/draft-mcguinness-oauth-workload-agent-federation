# Interoperability and upstream closure cases

The first table tests Federation's current identity and authorization requirements. The remaining tables are acceptance criteria for proposed upstream changes. They are not claims that this draft defines those wire behaviors today.

## Current Federation requirements

| Case | Required outcome |
|---|---|
| Valid credential with one active, enabled exact binding | Resolve the configured Registered Agent |
| Missing, ambiguous, inactive, or disabled binding | Do not issue authorization for that agent |
| Unverified issuer URL, request hint, or client metadata proposes another authority | Does not establish credential-authority trust |
| Same `kid` under unrelated issuers or SPIFFE trust domains | Verify only with keys authorized for the selected authority |
| Client registration permits several workload identities | Resolve the exact authenticated workload; do not map the whole prefix to one agent implicitly |
| Valid client authentication without a governed-agent binding | Does not establish agent identity |
| Shared-client ATTEST without standardized, authenticated agent evidence | Does not identify a subordinate Registered Agent |
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
| WIT authentication proof and DPoP both appear | SPIFFE OAuth, WIMSE, ATTEST | Supported modes and key/algorithm consistency without accidental redundant proofs |
| Cached bearer JWT reaches two replicas with independent keys | Credential and consuming profiles | Defined reuse/assurance rules, not a Federation-specific first-use cache |
| Bearer credential is stolen before first use | Credential and consuming profiles | Explicit limitation or independently established holder binding |
| Two agents share an ATTEST client | ATTEST extension | Authenticated agent namespace, attester authority, and key association |
| Client metadata selects an unapproved attester | Trust configuration/profile | Client endorsement cannot expand IdP trust |
| Execution restarts or changes keys | Identification and platform evidence | Evidence-based continuity, enrollment, and replacement semantics |
| Subject becomes an actor, or the actor changes | Consuming instance profile | Whose context is retained, replaced, or omitted |
| Disablement signal is delayed, duplicated, or missed | Provisioning/lifecycle work | Freshness, ordering, recovery, and effect on issued tokens |
