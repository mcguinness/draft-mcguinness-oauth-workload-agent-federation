<a id="coordination"></a>

# Coordination with Related Work

This repository note tracks unresolved design and dependency decisions. It is not part of the normative draft.

## Scope and ownership

Keep the external-identity-to-governed-agent binding and downstream grant
issuance in Agent Federation. Related gaps have different owners:

| Gap | Recommended home |
|---|---|
| External workload or platform identity → governed agent → downstream grant | Agent Federation |
| Who may act for whom; actor representation and chain processing | Actor Profile and its consuming authorization profiles |
| Stable installation or execution identity | Identification |
| Client endorsement of an attester, constrained by IdP trust policy | Federation configuration initially; a small CLIENT-ATTEST trust profile only if implementations need interoperable discovery |
| Agent ownership, groups, provisioning, and disablement signals | Provisioning and lifecycle work, coordinated with Federation |
| Enrollment, clone detection, and verified key replacement | Platform-specific evidence mechanisms initially |
| Interoperable model or runtime assurance | Defer a dedicated profile until concrete producers and consumers agree on semantics |

Client endorsement can restrict the attesters accepted for a client within
the IdP's configured trust policy. It cannot make an otherwise untrusted
attester authoritative. A future discovery mechanism needs to preserve that
boundary; no additional discovery protocol is required by this revision.

### Identification boundaries

Two gaps need to remain explicit in Identification:

1. **Continuity depends on evidence.** An identifier labels the continuity
   asserted under trusted evidence rules; it does not establish that continuity.
   Identification does not supply an enrollment or key-replacement protocol.
   Evidence for enrollment, replica distinction, clone detection, and verified
   key replacement initially remains platform-specific.
2. **Context propagation needs a consuming profile.** That profile needs to
   identify whose instance is described and define what happens during exchange:
   * Which evidence establishes the instance association.
   * Whether the context is retained, replaced, or omitted in each output.
   * How a change of actor affects the association.

Native workload credentials do not automatically provide replica identity.
SPIFFE permits a workload to span multiple running instances; distinguishing
those replicas requires additional evidence. See
[SPIFFE Concepts](https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/).

### Authorization principal and optional instance context

Treat an instance as a distinct identification subject when its continuity
matters. Treat it as an authorization principal only when the deployment
deliberately grants authority to that instance.

The following table records the intended architecture. Instance context is
not implemented by this revision. Agent-to-agent delegation and independently
authorized executions also require other authorization profiles.

| Situation | Authorization representation | Optional instance context under a future consuming profile |
|---|---|---|
| Agent acts as itself | `sub` = governed agent; WAG has no `act` | Instance of the agent subject |
| Agent acts for a user | `sub` = user; `act` = governed agent under the delegation profile | Instance executing as that actor |
| Agent restarts or replaces a replica | Authorization identity stays unchanged | New execution identifier; installation continuity follows Identification's evidence rules |
| Agent delegates to another governed agent | Actor relationship changes under the consuming delegation profile | Context follows the new actor; the previous actor's instance is not relabeled as the new actor's |
| A particular execution is deliberately granted independent authority | Execution may be subject or actor | Defined by the specialized authorization profile |

[RFC 8693 Section 4.1](https://www.rfc-editor.org/rfc/rfc8693.html#section-4.1)
defines `act` as a representation of delegation and the acting party. It does
not require every authenticated runtime to become an actor.

Earlier Federation text defined subject-instance context for WAG and
actor-instance context for ID-JAG. The current revision removed that wire
behavior with the unpublished INSTANCE dependency. Preserve those associations
as design requirements for a future consuming extension, without restoring a
normative dependency or implying current interoperability.

<a id="wag-gaps"></a>

## WAG Gaps Filled by This Document

This note is informative. WAG-00 leaves IdP issuance through
exchange open. The definitions below allow this profile to be
implemented while related drafts are coordinated. Once WAG adopts
an item, this document can reference that definition.

| Item | Definition in this profile | Coordination needed |
|---|---|---|
| Token type | `urn:ietf:params:oauth:token-type:wag` | Common identifier for RFC 8693 request and response; proposed registration belongs in WAG |
| JWT type | `oauth-wag+jwt` | Proposed media type registration belongs in WAG |
| Sender constraint | `cnf.jkt`, DPoP proof, and key match at redemption | Resolve WAG's open possession requirement using ID-JAG's bound-grant procedure |
| Authorization claims | Required `scope` and `resource`, using ID-JAG definitions | Add claims to WAG so the RAS can enforce the grant's authorization ceiling |
| Redemption errors | [Redemption Errors](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#redemption-errors) | Align grant, proof, nonce, resource, and scope failures across both outputs |
| Replay prevention | Atomic single use of `(iss, jti)` through expiration plus skew | Define consistent grant consumption regardless of issuer |
| Acting relationship | WAG excludes `act` | Reserve WAG for self-acting access |
| IdP issuance | Tenant-specific IdP issuer and canonical Registered Agent `sub` | Acknowledge IdP placement in WAG; retain identity-resolution mechanics here |

Further agreement is needed on:

* The single issuer-identifier audience, already accepted by WAG.
* Agent Properties registrations, including the RFC 9068 and OpenID
  Connect definitions for `groups`, `roles`, and `name`.
* WAG's Informational status as a normative dependency of this
  standards-track profile.
* Advertising WAG through
  `identity_chaining_requested_token_types_supported`.

## Other Coordination Items

The following items remain open:

* **Actor identifiers:** pairwise agent identifiers need an Actor
  Profile extension. This document preserves the actor token's `sub`.
* **Grant audience:** ID-JAG's RAS issuer audience takes precedence
  over Actor Profile's generic token-endpoint guidance; that precedence
  needs agreement in Actor Profile.
* **Redemption grant type:** ID-JAG and WAG's normative text uses
  `jwt-bearer`, while ID-JAG's bound-grant example and [JWT-DPOP](https://datatracker.ietf.org/doc/html/draft-parecki-oauth-jwt-dpop-grant-01)
  use `jwt-dpop`. This document follows the normative `jwt-bearer`
  text with DPoP and will follow ID-JAG if it adopts `jwt-dpop`.
* **SPIFFE and ATTEST:** `spiffe_wit` currently uses a separate Client
  Attestation PoP JWT plus DPoP with the same key. Its metadata needs
  alignment with ATTEST's evolving proof modes. General WIT actor
  inputs need separate mapping and trust-domain rules when `iss` is
  absent.
* **Instance identification:** the unpublished INSTANCE dependency has been
  removed. Instance identifiers, mapped context, and lifecycle granularity are
  outside this version's conformance requirements.

## Direct mapped actor input proposal

Status: design alternative, not implemented by the current wire profile.
The existing adapter is a choice of this draft, not a universal restriction
in Actor Profile. For a future direct path, a delegated request could use:

```http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...agent-attestation...
DPoP: eyJ...proof-K...

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&client_id=https%3A%2F%2Fplatform.example%2Foauth-client
&requested_token_type=urn:ietf:params:oauth:token-type:id-jag
&subject_token=eyJ...user-id-token...
&subject_token_type=urn:ietf:params:oauth:token-type:id_token
&actor_token=eyJ...agent-attestation...
&actor_token_type=urn:ietf:params:oauth:token-type:jwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
```

The proposal needs an explicit rule for each of these points before adoption:

1. Treat the attestation, platform JWT, or WIT-SVID as direct actor evidence.
   Select its validation rules from trusted configuration, not the generic JWT
   token type. For ATTEST and WIT-SVID, require the exact authentication JWT as
   the actor token and validate all corresponding proofs.
2. Resolve that external evidence through the Federation Binding to the
   canonical Registered Agent. Construct `act.iss` from the IdP and `act.sub`
   from the resolved agent. Coordinate this mapping rule with Actor Profile:
   copying the external credential's issuer and subject would have different
   attribution semantics.
3. Require independent OAuth client authentication for platform evidence and
   match the user credential to that client. A bearer actor credential cannot
   substitute for the OAuth client credential.
4. Check delegation authorization for the resolved agent, user, client, tenant,
   resource, and scope. Preserve the distinction between authentication and
   permission to act for the user.
5. Apply the input's key checks and cached-credential association. The direct
   path changes the number of exchanges, not the bearer JWT theft model.
6. Define capability negotiation and error behavior, and update Actor Profile
   metadata consistently. Retain the adapter for X.509-SVID, which supplies no
   JWT actor token.

If adopted, JWT-based delegated access would need two token-endpoint calls
(exchange and redemption), plus any user-credential renewal. An X.509-SVID
flow would still need acquisition when no eligible adapter token is held.

## WAG registration proposals

Status: proposed upstream text; the current draft does not request these
registrations. Agreement with WAG or selection of a distinct grant name is
still required. The illustrative values in the draft are not assignments
already made by IANA.

### Token type URI

* URN: `urn:ietf:params:oauth:token-type:wag`
* Common Name: Token type URI for a Workload Authorization Grant
* Change Controller: IETF
* Specification Document: WAG, if adopted by that document

### Media type

* Type name: application
* Subtype name: oauth-wag+jwt
* Required parameters: none
* Optional parameters: none
* Encoding considerations: binary; base64url-encoded JWT components
* Security considerations: JWT validation, grant audience restriction,
  possession binding, and replay prevention in the defining specification
* Interoperability considerations: agreement on WAG's required claims and
  bound-grant processing
* Published specification: WAG, if adopted by that document
* Applications: authorization servers and clients processing WAG
* Fragment identifier considerations: none
* Additional information: no magic number, filename extension, or Macintosh
  file type code
* Contact: Karl McGuinness, public@karlmcguinness.com
* Intended usage: COMMON
* Restrictions on usage: none
* Author: Karl McGuinness
* Change controller: IETF
* Provisional registration: no
