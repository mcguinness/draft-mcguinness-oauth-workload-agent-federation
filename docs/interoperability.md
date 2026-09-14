# Interoperability Test Cases

This test inventory is informative; the normative requirements are in the
body. Independent platform, client, IdP, and RAS implementations can
exercise:

## Identity and Input Selection

| Case | Expected result |
|---|---|
| Shared client omits `agent_id` | Reject; no fallback to client-only binding |
| Missing, ambiguous, or disabled binding | Reject issuance |
| Unexpired eligible token with the same client, agent, input method, and key | Reuse subject to current policy; fresh acquisition can be required |
| Direct JWT input contains `act` | `invalid_grant`; no conversion from delegation to self-acting access |
| Same registered agent through direct WAG and the access-token adapter | Same WAG `sub` and issuer namespace |
| Direct WAG with shared-client ATTEST; approved `(iss, sub, agent_id)` and key proof | WAG subject is the Registered Agent, not the shared client |
| Agent with its own client identity supplies `agent_id` | Resolve `(iss, sub)`; the additional claim cannot switch to the shared-client model |
| Access token from any other issuance, even with a matching audience | Not eligible as an IdP access-token input; use direct WAG or acquire an eligible token |

## Platform JWT Evidence

| Case | Expected result |
|---|---|
| Any input lacks a nonce required by the IdP | `use_dpop_nonce`; no grant issued |
| Platform JWT outside the configured credential class or older than the bounded age | Reject input |
| Direct WAG with platform JWT; approved issuer and exact selectors, nonce and DPoP proof; no client authentication required by the binding | WAG for the bound agent without acquisition or `client_id` |
| Platform-issued JWT with an unapproved issuer, wrong audience, or expired | Reject subject evidence with `invalid_grant` |
| Platform JWT with an unbound subject, missing additional selector, or wrong exact claim value | `invalid_grant`; no prefix, wildcard, or partial match |
| Shared platform subject plus exact agent and tenant claims matches one approved binding | Resolve that Registered Agent independently of OAuth `client_id` |
| Platform JWT presented as `client_assertion` without independent client authentication | Does not authenticate the OAuth client |
| Platform acquisition with a valid JWT but no separate client authentication, or an unauthorized client | Reject; workload evidence alone cannot obtain the actor credential |
| Platform acquisition requests an audience, scope, or actor | `invalid_request` |
| Platform-origin actor token used with another authenticated client or DPoP key | `invalid_grant` |
| Platform-origin actor token, same permitted client and key, current binding, valid user and approval; no platform JWT resent | Issue ID-JAG |
| Platform JWT with missing or mistyped `iat`, invalid time ordering, excessive age or lifetime, or future `iat` beyond clock skew | `invalid_grant` |
| Cached platform JWT reused with the same binding and key, all other checks valid | Accept with fresh DPoP proof |
| Previously used platform JWT presented with another key, including a different signature over the same signing input | `invalid_grant`; no new key association |

## SPIFFE and Credential Renewal

| Case | Expected result |
|---|---|
| X.509-SVID client with approved exact ID and DPoP proof | IdP access token without stable instance context |
| Direct WAG with WIT-SVID; approved exact ID, attestation PoP, matching DPoP key; no `iss` | WAG for the configured agent without acquisition |
| WIT-SVID with missing attestation PoP, mismatched key or proof algorithm, or expired credential | Reject authentication or proof |
| WIT-SVID with unapproved trust domain or mismatched `client_id` | Reject; `iss` cannot select another trust anchor |
| Renewed X.509-SVID, same binding and DPoP key | Existing eligible token remains usable |
| Renewed WIT-SVID, same binding and unchanged `cnf.jwk` | Existing eligible token remains usable |
| Renewed WIT-SVID with a new `cnf.jwk` | Reject exchange with the old token; new IdP access token required |
| Direct WAG using a renewed WIT-SVID and proofs from its new key | WAG bound to the new key; no IdP access token required |
| Direct ATTEST or WIT-SVID subject differs from the authentication JWT, even for the same identity | `invalid_grant` |
| X.509-SVID request omits `subject_token` | `invalid_request`; use the access-token adapter |

## Delegation and Instance Context

| Case | Expected result |
|---|---|
| Direct WAG with ATTEST agent as client; approved binding and proof | WAG for the Registered Agent, without acquisition |
| Valid client and user credentials, with absent, revoked, or expired approval | Same non-enumerating `actor_unauthorized` response |
| Valid user and agent credentials without delegation | `actor_unauthorized` |
| Direct external credential supplied as ID-JAG `actor_token` | Reject; this delegated path requires the IdP-issued actor token |
| Same agent in a second execution | Same agent subject; no stable instance context defined here |
| Unrelated client, agent, or key at exchange | Reject inconsistent evidence |
| Agent acting for itself | WAG subject is the agent; no `act` |
| Agent acting for a user | User subject; Registered Agent `act` |

## Grant Validation and Redemption

| Case | Expected result |
|---|---|
| Grant with tenant B `iss` signed by a key authorized only for tenant A, including colliding `kid` | Reject; key lookup is scoped to exact issuer |
| Grant redemption with missing proof or mismatched key | `invalid_grant` |
| JWT with a future `nbf` outside allowed skew | Reject as not yet valid |
| Redemption without `resource`, or with `resource` not matching the grant | `invalid_target` |
| Replayed grant with a valid DPoP proof | `invalid_grant`; grants are single use |
| ID-JAG redemption with DPoP but no required client authentication | Reject; DPoP is not the registered client credential |
| Valid grant for one RAS also lists another audience | Reject; exactly one RAS issuer is allowed |
| Replayed grant during allowed expiration skew | Reject; consumed identifiers remain recorded through `exp` plus skew |
| Unsupported requested output | `invalid_request`; no fallback |
| Presented redemption proof has an invalid signature, wrong endpoint/method, or stale timestamp | `invalid_dpop_proof` |
| Redemption proof lacks a required RAS nonce | `use_dpop_nonce` with `DPoP-Nonce`; grant remains unconsumed |
| Concurrent redemption of one grant at two RAS replicas | At most one access token issued |
| Repeated `audience`, `resource`, or other request parameter | `invalid_request` |

## Status and Record Correlation

| Case | Expected result |
|---|---|
| WAG subject and ID-JAG actor name the same IdP agent | Resolve the same provisioned record |
| Platform-origin actor token used after its recorded binding is disabled | Reject even though the token is unexpired |
| WAG with a previously unseen `sub` under an allowlisted `iss` | Accept subject; issue only if RAS policy authorizes access; record-dependent authorization requires correlation |
| Authenticated disabled-agent status reaches the RAS | Block subsequent issuance and refresh; revoke or deactivate affected tokens as supported |
| Canonical agent identifier in the IdP access token | Same value in WAG `sub` and ID-JAG `act.sub`; no recipient-specific substitution |
| Same bare agent identifier from another issuer | No match to the original issuer's record |

Only cases for the implemented input and output are applicable.
Existing client-based deployments are compatibility context, not an additional
conformance path for this specification.

## Review regression cases

| Case | Expected result |
|---|---|
| Unknown `agent_id` request parameter | Ignored; does not change the authenticated binding |
| Unconfigured extra JWT claim named `agent_id` | Ignored unless the selected credential profile uses it |
| Management-API token with matching issuer and agent-shaped subject | Reject as an adapter token; dedicated exchange audience is required |
| Federation adapter token presented as API authorization | Reject; the token is usable only as federation exchange input |
| Unexpired adapter token after policy requires fresh acquisition | Require reacquisition; expiration is not a promise of continued eligibility |
| Adapter token older than 300 seconds within an explicitly configured longer lifetime | Reusable only if all current binding and authorization checks pass |
| Generic `typ=JWT` workload credential with approved issuer, audience, exact selectors, and distinguishing validation policy | Eligible even without a dedicated JWT type or issuer |
| Credential older than 300 seconds within the platform's configured age limit | Eligible subject to all other checks |
| `sub_profile` and instance claims absent | No failure solely because those extensions are absent |
| Tenant issuers share a key expressly authorized for both | Key sharing alone does not cause rejection; exact issuer authorization remains required |
| Required `iat` missing from a Client Attestation | Reject under this profile's explicit ATTEST narrowing |
| Nonce required for a non-platform input | Challenge under the same nonce policy used for platform evidence |
