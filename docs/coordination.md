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
| Agent acts as itself | `sub` = governed agent; AFG has no `act` | Instance of the agent subject |
| Agent acts for a user | `sub` = user; `act` = governed agent under the delegation profile | Instance executing as that actor |
| Agent restarts or replaces a replica | Authorization identity stays unchanged | New execution identifier; installation continuity follows Identification's evidence rules |
| Agent delegates to another governed agent | Actor relationship changes under the consuming delegation profile | Context follows the new actor; the previous actor's instance is not relabeled as the new actor's |
| A particular execution is deliberately granted independent authority | Execution may be subject or actor | Defined by the specialized authorization profile |

[RFC 8693 Section 4.1](https://www.rfc-editor.org/rfc/rfc8693.html#section-4.1)
defines `act` as a representation of delegation and the acting party. It does
not require every authenticated runtime to become an actor.

Earlier Federation text defined subject-instance context for its self-acting grant and
actor-instance context for ID-JAG. The current revision removed that wire
behavior with the unpublished INSTANCE dependency. Preserve those associations
as design requirements for a future consuming extension, without restoring a
normative dependency or implying current interoperability.

## Self-acting grant decision

The draft now defines an **Agent Federation Grant (AFG)** independently of
[Workload Authorization Grant](https://datatracker.ietf.org/doc/html/draft-carleton-workload-authz-grant-00).
AFG has IdP issuance, DPoP binding, a single RAS issuer audience, explicit
scope/resource limits, and single-use redemption. Supporting WAG does not
imply support for AFG. WAG is informative, not a normative dependency.

The draft's IANA Considerations contain the complete requests for
`urn:ietf:params:oauth:token-type:afg` and `application/oauth-afg+jwt`.
The requests belong to this specification and are not claims of completed
IANA registration. No registrations are requested on WAG's behalf.

Both AFG and ID-JAG default to no refresh token. A RAS can enable refresh
only with an authorized client, sender binding, and continuing authorization
checks. AFG does not inherit WAG's refresh-token prohibition. The obsolete
WAG `namespace` and `ctx` placeholders have been removed.

## Other coordination items

* **Actor identifiers:** pairwise agent identifiers need an Actor Profile
  extension. This document preserves the actor token's `sub`.
* **Redemption grant type:** the draft follows ID-JAG's normative `jwt-bearer`
  redemption with DPoP. If ID-JAG adopts `jwt-dpop`, align the common redemption
  procedure and both grants' examples with that change.
* **JWT-SVID discovery:** SPIFFE OAuth defines the `jwt-spiffe` assertion type
  but no corresponding discovery method name. Federation agrees support
  through trusted configuration; coordinate an interoperable advertisement
  upstream.
* **SPIFFE and ATTEST:** align `spiffe_wit` metadata with ATTEST's evolving
  proof modes. The current profile requires the WIT authentication proof and
  DPoP to use the same key.
* **Shared-agent ATTEST binding:** the `agent_id` extension and its registration
  remain self-contained here for -00. Coordinate ownership with ATTEST; move
  the claim and validation rules together into ATTEST or a small published
  extension if the working group chooses that home. Do not introduce an
  unpublished normative dependency in the interim.
* **Instance identification:** instance claims and propagation remain out of
  conformance scope. The design boundaries above belong to a future consuming
  profile.

## Direct mapped actor input proposal

Status: deferred from -00; evaluate for -01 with Actor Profile coordination.
The adapter is retained in -00 as an explicit profile choice. Actor Profile's
JWT access-token input requires validation, issuer trust, absence of `act`,
and proof checks before constructing the actor; the adapter's identity role
is to put the governed agent in the credential's `sub`. Direct inputs would
remove that issuance step, but need a defined mapping before actor construction.
Actor Profile's existing direct-input rules use the credential's `sub`, which
may identify a shared client rather than the governed agent. This is a
coordination issue, not a claim that direct credentials are inherently unsafe. For a future direct path, a delegated request could use:

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

1. Treat the attestation, platform JWT, JWT-SVID, or WIT-SVID as direct actor evidence.
   Select its validation rules from trusted configuration, not the generic JWT
   token type. For ATTEST, JWT-SVID, and WIT-SVID, require the exact authentication JWT as
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
