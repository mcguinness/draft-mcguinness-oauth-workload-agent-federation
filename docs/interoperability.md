# Conformance scenarios and remaining closure criteria

This repository is the sole home for the scenario inventory. The drafts contain normative requirements; these cases exercise them without adding requirements. The signed fixture check covers example integrity, not an implemented IdP/RAS pair.

## Required delegated path

| Case | Expected outcome |
|---|---|
| Valid ID Token, platform JWT, registered clients, DPoP, binding and delegation | ID-JAG identifies user and governed actor; RAS issues a DPoP-bound JWT access token |
| External workload subject differs from governed agent | `act.sub` is the approved governed identifier, not the external subject |
| Client IDs differ across IdP and RAS | Trusted mapping supplies the RAS `client_id`; each hop authenticates its own client |
| User IDs differ across namespaces | Trusted subject mapping preserves the same user; actor namespace remains the IdP's |
| Required subject/actor parameter, resource, or scope missing | `invalid_request`; no fallback to a client-only path |
| Subject token issued by another IdP or for another client | `invalid_grant`; client authentication alone does not fix audience mismatch |
| Actor signature, issuer, audience, expiration, or configured selector invalid | `invalid_grant` |
| Several configured input classes match | `invalid_request`; no weaker validation path |
| Platform credential has an unsupported confirmation binding | Reject; no bearer downgrade |
| Actor token or subject context contains an existing actor chain | `invalid_grant`; no chain dropping or rewriting |
| Binding absent, ambiguous, disabled, or agent inactive | No grant; applicable `actor_unauthorized` outcome |
| Valid identities without user-to-agent delegation | `actor_unauthorized` |
| Scope/resource request exceeds policy | Narrow where allowed or return the defined target/scope error; never expand authority |
| Optional authorization details supplied | Process under ID-JAG while retaining explicit resource/scope requirements |
| Grant expiry would exceed known actor or subject expiry | Bound the grant lifetime; do not extend input validity |
| DPoP absent, malformed, replayed, or stale at issuance | Applicable DPoP error; no unbound ID-JAG |
| Server issues a nonce challenge | Return required header; accept an authorized retry with fresh valid proof |
| Grant lacks actor, confirmation key, resource, or scope | Reject under the configured profile |
| Grant audience differs from RAS issuer or authenticated client differs from grant client | `invalid_grant` |
| Grant's actor namespace differs from its trusted IdP issuer | Reject; no actor trust based solely on `act.iss` |
| Redemption proof absent or its key differs | `invalid_grant` under ID-JAG |
| RAS cannot authorize user/actor relationship | No access token; no actor-free or bearer fallback |
| Successful access-token issuance | Preserve actor object and DPoP key; retain enforceable authority ceilings |
| Same unexpired grant presented with fresh proof | Apply ID-JAG reuse rules and current RAS policy; no implicit single-use rule |
| Refresh token issued as the permitted exception | Preserve user, actor, client, authority and key binding; recheck RAS policy |
| API proof has wrong method, URL, key, hash, nonce, or replayed identifier | Reject under DPoP |
| API token valid for user but agent lacks required authority | Reject under user/actor authorization policy |
| Unknown `agent_id` parameter or claim | Base ignore rules; no identity-model switch |
| Same bare actor identifier under another issuer | Distinct principal |

## Optional credential paths

| Case | Expected outcome |
|---|---|
| Valid native JWT-SVID appears identically as client assertion and actor token | Authenticate using SPIFFE OAuth, resolve exact identity, and produce the same governed actor |
| JWT-SVID missing optional `iss` or `iat` | No rejection solely for absence |
| JWT-SVID actor and client assertion differ | Reject the unsupported combination |
| SPIFFE client association covers several workload IDs | Resolve the exact authenticated SPIFFE ID, not an implicit prefix-to-agent mapping |
| Own-client attestation omits `iss` | Identify attester through its trusted verification key and configured authority |
| Own-client attestation has conflicting `iss` | Reject the attester mismatch |
| Shared-client attestation validated under the companion profile | Resolve its tuple through the approved binding, then construct the governed actor |
| Attestation header differs from `actor_token` | Reject; do not combine claims or keys from different attestations |
| Normal ATTEST mode uses a separately keyed DPoP proof | Base ATTEST can authenticate, but this federation profile rejects the output-key mismatch |
| Combined ATTEST mode uses a valid matching DPoP key | One combined proof suffices |
| X.509-SVID or WIT-SVID used only for client authentication with a supported actor JWT | Apply both mechanisms in their defined roles |
| X.509-SVID or WIT-SVID presented as an unsupported sole actor input | No advertised or inferred support |

## Standalone attested-agent profile

| Case | Expected outcome |
|---|---|
| Own-client mode without `iss` | Return the configured attester/client pair |
| Verification key associated with several authorities without disambiguating configuration | Reject ambiguity |
| Two agent claims under the same attester and client | Return distinct attester/client/agent tuples |
| Shared-client `iss` or `attested_agent_id` absent, empty, or incorrectly typed | `invalid_client_attestation` |
| Agent ID exists only in a request parameter or proof | It is not attester-authenticated evidence |
| Same client and agent strings under another attester | Distinct namespace |
| Same attester/client spans platform tenants | Agent identifiers distinguish tenants or attester namespaces differ |
| Own-client input contains agent claim | No mode switch or override of the pair |
| Shared-client validation fails | No own-client fallback |
| Base ATTEST validator ignores additional claim | It does not establish shared-agent profile support |
| Proof key mismatches attestation key | Reject under ATTEST |
| Client restriction excludes an IdP-approved attester | Reject; trust sets are intersected |
| Client metadata names an unapproved attester | No expansion of verifier trust |
| Attestation renewed with replacement key | Require new valid key authorization and current policy |

## Metadata

| Case | Expected outcome |
|---|---|
| IdP advertises issuance | Includes required platform-JWT input and base exchange/client/DPoP capabilities |
| RAS advertises redemption | Includes required base ID-JAG/JWT bearer/client/DPoP capabilities |
| Missing object, wrong role, or malformed member types | No usable capability advertisement |
| Unknown object member or actor input identifier | Ignore it; do not reinterpret as a known capability |
| Generic JWT actor support without this profile's object | Does not imply governed-actor composition |
| SPIFFE assertion type present | Does not invent an authentication-method metadata value |
| Actor or confirmation claim omitted after profile selection | Still enforce the configured profile; no downgrade |

## Remaining gap closure criteria

| Gap | Evidence required to close it |
|---|---|
| Self-acting WAG issuance | Independent implementations agree on issuance inputs, IdP/governed subject namespace, client roles, and success/errors without a normalization token |
| WAG identifiers and discovery | WAG owns complete registration templates and capability rules; clients can distinguish supported grant/proof combinations |
| Bound WAG redemption | Wrong key/audience fails; nonce retries and concurrent redemption obey an explicit replay policy |
| WAG authority and continuing access | Scope/resource ceilings, missing constraints, renewal, and disablement are testable under WAG's own rules |
| General actor resolution extension point | Other consuming profiles can use the same mapping semantics; this is consolidation, not a blocker to the defined ID-JAG path |
| X.509 connection as sole actor evidence | Independent implementations bind the connection identity to the requested actor and output key without fabricated JWTs |
| Direct WIT-SVID actor input | Credential, native proof, actor request, and DPoP key are unambiguously bound and discoverable |
| Instance context | Trusted evidence establishes continuity; consumers agree whose instance survives or changes at each exchange |
| Lifecycle signals | Receivers handle delay, duplicates, missed events and outstanding tokens within stated freshness/recovery guarantees |
