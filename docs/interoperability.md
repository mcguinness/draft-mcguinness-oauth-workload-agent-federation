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
| Requested scopes partially authorized and partial approval permitted | Issue only the non-empty approved subset; grant and response report the reduction |
| No requested scope authorized, or full approval required and unavailable | `invalid_scope`; no token |
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
| Refresh-token rotation or repeated redemption of the same ID-JAG | Original continuation deadline remains anchored to that ID-JAG's `iat` |
| Refresh would issue a token expiring after the continuation deadline | Cap expiry at the deadline; reject refresh after the deadline with `invalid_grant` |
| RAS authorization withdrawn or authenticated upstream disablement notification applied | No further refresh issuance; `invalid_grant` |
| No upstream status signal is available | Continuation is limited by the configured deadline; no claim of immediate upstream revocation |
| New ID-JAG used to establish a new continuation period | Reapply profile issuance and redemption checks; local refresh alone cannot renew IdP authority |
| API proof has wrong method, URL, key, hash, nonce, or replayed identifier | Reject under DPoP |
| API path requires the profile but access token lacks `act` | HTTP 401 `invalid_token`; no non-delegated fallback |
| API actor malformed, nested, or in a namespace the RAS is not trusted to assert | HTTP 401 `invalid_token` |
| API token lacks required scope or confirmation binding | HTTP 401 `invalid_token` |
| API token valid for user but required actor authorization fails or is unavailable | HTTP 403 `actor_unauthorized`, not `insufficient_scope` |
| API token has insufficient scope for the operation | HTTP 403 `insufficient_scope` |
| API token issuer is the trusted RAS and actor issuer is its approved IdP namespace | Accept that namespace relationship; do not require the two issuers to be equal |
| Unknown `agent_id` parameter or claim | Base ignore rules; no identity-model switch |
| Same bare actor identifier under another issuer | Distinct principal |

## Optional credential paths

| Case | Expected outcome |
|---|---|
| Valid native JWT-SVID appears identically as client assertion and actor token | Authenticate using SPIFFE OAuth, resolve exact identity, and produce the same governed actor |
| JWT-SVID sole audience is the IdP issuer while token endpoint URL differs | Apply native audience rules; do not apply the `private_key_jwt` endpoint audience rule |
| `private_key_jwt` assertion uses only the issuer instead of the distinct token endpoint | Reject client authentication under this profile's explicit audience narrowing |
| JWT-SVID missing optional `iss` or `iat` | No rejection solely for absence |
| JWT-SVID actor and client assertion differ | Reject the unsupported combination |
| SPIFFE client association covers several workload IDs | Resolve the exact authenticated SPIFFE ID, not an implicit prefix-to-agent mapping |
| Own-client attestation omits `iss` | Identify attester through its trusted verification key and configured authority |
| Own-client attestation has conflicting `iss` | Reject the attester mismatch |
| Instance attestation validated under Identification | Resolve the issuer-qualified instance through its approved binding and client association, then construct the governed actor |
| Attestation header differs from `actor_token` | Reject; do not combine claims or keys from different attestations |
| Normal ATTEST mode uses a separately keyed DPoP proof | Base ATTEST can authenticate, but this federation profile rejects the output-key mismatch |
| Combined ATTEST mode uses a valid matching DPoP key | One combined proof suffices |
| X.509-SVID or WIT-SVID used only for client authentication with a supported actor JWT | Apply both mechanisms in their defined roles; no agent mapping required for the client-only evidence |
| Hosting client's credential has no Registered Agent record but its separate actor JWT has an approved binding | Issue when the authenticated client is permitted to use that actor binding and delegation is approved |
| Authenticated hosting client is not permitted to use the selected actor binding | Reject; client authentication cannot authorize an arbitrary agent |
| X.509-SVID or WIT-SVID presented as an unsupported sole actor input | No advertised or inferred support |

## Instance-to-agent composition

These scenarios exercise Federation's use of Identification. They do not redefine Identification's enrollment or lifecycle requirements.

| Case | Expected outcome |
|---|---|
| Valid (`iss`, `client_instance_id`), authenticated client and enabled binding | Resolve one active governed agent, then apply separate delegation policy |
| Several validated instances map to the same agent | Preserve the same governed `act.iss` and `act.sub`; instance IDs remain distinct |
| One instance has ambiguous mappings to several agents | `actor_unauthorized`; no inferred selector or arbitrary choice |
| Missing, disabled or unapproved agent binding after successful instance validation | `actor_unauthorized` |
| Required instance claim absent, empty, incorrectly typed or beyond Identification's limit | `invalid_client_attestation` |
| Instance policy rejects a suspended or retired instance | Identification's `invalid_client_attestation`, without status disclosure |
| Base ATTEST implementation ignores the instance claim | Does not satisfy configured `instance_attestation` support |
| Same instance string under another attester | Distinct identity; no shared binding or continuity inferred |
| Instance attestation presented under an unauthorized client or receiver scope | Reject under the applicable Identification trust or client validation rule |
| Valid instance and agent binding without delegation | `actor_unauthorized`; instance identity supplies no delegation |
| Configured own-client input contains an instance claim | No mode switch or replacement of the configured own-client identity |
| Instance validation fails | No own-client fallback |
| Renewal or verified key change preserves instance identity under Identification | Revalidate current binding, instance policy and proof; no automatic transfer of existing grants |
| New enrollment, replacement instance or changed identifier | Require an approved new binding; that binding may resolve to the same agent |
| Prior key, shared client or claimed predecessor used to infer a replacement binding | Reject that inference; it does not approve a binding |
| Instance identifier appears only in the request or proof | Does not supply the attested instance identity required by this input |
| Successful output | Governed actor in `act`; no instance-context propagation defined by this input |

## Metadata

| Case | Expected outcome |
|---|---|
| IdP advertises issuance | Includes required platform-JWT input and base exchange/client/DPoP capabilities |
| RAS advertises redemption | Includes required base ID-JAG/JWT bearer/client/DPoP capabilities |
| Missing object, wrong role, or malformed member types | No usable capability advertisement |
| Unknown object member or actor input identifier | Ignore it; do not reinterpret as a known capability |
| Instance input advertised | `actor_inputs_supported` includes `instance_attestation`; base ATTEST support alone does not advertise that composition |
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
| Direct WIT-SVID actor input (local scope deferral) | Compose existing credential and attestation proof with exact actor presentation and discovery; define output-key authorization and lifetimes respecting WIT's prohibition on post-expiry key use |
| Downstream instance context | Compose Identification’s context with the governed actor and define provenance, receiver scoping and retain/replace/omit rules across both exchanges |
| Lifecycle signals | Receivers handle delay, duplicates, missed events and outstanding tokens within stated freshness/recovery guarantees |
