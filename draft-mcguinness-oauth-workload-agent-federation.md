---
title: "OAuth 2.0 Profile for Agent Federation"
abbrev: "Agent Federation"
category: std
docname: draft-mcguinness-oauth-workload-agent-federation-latest
submissiontype: IETF
stand_alone: yes
ipr: trust200902
area: "Security"
workgroup: "Web Authorization Protocol"
keyword:
 - OAuth
 - agent federation
 - workload identity
 - agent registry
 - token exchange
venue:
  group: "Web Authorization Protocol"
  type: "Working Group"
  mail: "oauth@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/oauth/"
  github: "mcguinness/draft-mcguinness-oauth-workload-agent-federation"
  latest: "https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html"
author:
 - fullname: Karl McGuinness
   organization: Independent
   email: public@karlmcguinness.com
normative:
  SPIFFE-OAUTH: I-D.ietf-oauth-spiffe-client-auth
  WIT: I-D.ietf-wimse-workload-creds
  ATTEST: I-D.ietf-oauth-attestation-based-client-auth
  ACTOR-PROFILE: I-D.mcguinness-oauth-actor-profile
  ID-JAG: I-D.ietf-oauth-identity-assertion-authz-grant
  AGENT-ATTEST:
    title: "OAuth 2.0 Attested Agent Identity"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-attested-agent-identity.html
    author:
      - name: Karl McGuinness
    date: 2026-09
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-attested-agent-identity-latest
  RFC7523:
  RFC8414:
  RFC8707:
  RFC9068:
  RFC6749:
  RFC7519:
  RFC8693:
  RFC8725:
  RFC9449:
  RFC9700:
informative:
  WAG: I-D.carleton-workload-authz-grant
  SPIFFE-CONCEPTS:
    title: "SPIFFE Concepts"
    target: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
    author:
      - org: SPIFFE
  ENTITY-PROFILES: I-D.mora-oauth-entity-profiles
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
--- abstract

This document defines a delegated agent-federation profile of the
Identity Assertion JWT Authorization Grant (ID-JAG). An identity
provider validates user and workload credentials, resolves the workload
to a governed agent, and issues a sender-constrained ID-JAG identifying
the user as subject and the governed agent as actor. The resource
authorization server preserves that relationship in an access token.
Self-acting access using Workload Authorization Grant is deferred
pending the grant changes identified in this document.

--- middle

# Introduction

An agent platform authenticates a workload in its own identity
namespace. An identity provider (IdP) may govern that workload as a
separate agent principal, with its own owner, status, groups, and
assignments. A resource authorization server (RAS) needs to know which
governed principal has been authorized, without implementing every
platform's credential validation and identity mapping.

This document assigns that resolution and policy decision to the IdP.
It separates three questions:

* **Agent identity:** which Registered Agent, the principal governed
  by the IdP, does the external evidence identify?
* **Acting relationship:** is that agent acting for itself or for a
  user, and is the requested delegation authorized?
* **Instance context:** which installation or execution is involved,
  if a separate identification profile establishes that context?

Authenticating an OAuth client, resolving an agent, and proving
possession of a key are distinct operations. None alone establishes
permission to act for a user. An instance identifier likewise does not
confer independent authority on a runtime.

## Defined Delegated Flow {#paths}

The delegated flow is specified in {{delegated-flow}}:

~~~
 Platform       Agent             IdP             RAS        API
    |-- evidence ->|               |               |          |
    |              |-- inputs ---->|               |          |
    |              |               | resolve agent |          |
    |              |               | authorize delegation     |
    |              |<-- ID-JAG ----|               |          |
    |              |------ ID-JAG + proof -------->|          |
    |              |<------ access token ----------|          |
    |              |------------- token + proof ------------>|
~~~

The agent first obtains the user's ID Token through the IdP's existing
OpenID Connect flow. The two token requests then resolve an external
workload identity to a Registered Agent, authorize that agent for the
user, and obtain an API access token. The client authenticates
independently at each authorization server.

Self-acting WAG access is not defined by this revision. {{wag-gaps}}
identifies the missing grant contract. Authenticating a workload or
resolving its governed identity alone does not complete that path.

## Scope and Conformance {#scope}

The IdP, RAS, and client roles claiming this profile MUST implement
{{delegated-flow}}. The required common path uses an ID Token subject,
a platform JWT actor, `private_key_jwt` client authentication, and DPoP.
It does not require the companion attested-agent draft. Additional
credential inputs have the status listed in {{actor-inputs}}.

The API MUST support the access-token processing in {{api-processing}}.
Implementations MAY support other flows, but MUST NOT use them as a
fallback after validation or authorization fails for this profile.
Self-acting access, multi-agent delegation chains, instance propagation,
and enrollment/key-replacement protocols are outside this revision.

## Responsibility Boundaries

| Concern | Defined by |
|---|---|
| External identity to governed agent; delegated issuance and redemption | This profile, using the extension point in {{ID-JAG, Section 9.7}} |
| ID-JAG format and base grant processing | {{ID-JAG}} |
| Actor object, current actor, and actor-aware resource policy | Selected rules of {{ACTOR-PROFILE}}, as specified in {{actor-construction}} |
| Base workload authentication and proofs | SPIFFE OAuth, WIMSE, and ATTEST |
| Attested agent identity and trust restrictions | Companion profile {{AGENT-ATTEST}} |
| Self-acting workload grant | WAG; requested changes in {{wag-gaps}} |
| Stable installation or execution identity | A future identification specification and its consuming profiles |
| Agent provisioning and disablement signals | Future provisioning and lifecycle specifications |

This document defines requirements locally where the base protocol
permits extensions. It uses ID-JAG's actor extension point and imports
Actor Profile's representation rules; it does not claim conformance to
Actor Profile's different credential-to-subject copying algorithm.
The attested-agent profile is maintained as a separate, self-contained
Standards Track draft. Its editor's copy is included in this repository;
it is a dependency only for the optional shared-client input.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth and Token Exchange terms follow {{RFC6749}} and {{RFC8693}}.
Client Attestation and Client Instance follow {{ATTEST}}. A harness is
the software executing the agent and making OAuth requests. The IdP
acts as an OAuth authorization server; the RAS issues access tokens
for its resources. These roles can be implemented by one service.

Registered Agent:
: A non-human principal governed by the IdP, with a stable identifier,
  status, and approved external identity bindings.

Federation Binding:
: An approved association between an external credential authority,
  identity, Source Tenant, and Registered Agent. It also identifies
  permitted OAuth clients when the selected flow requires them.

Source Tenant:
: The IdP tenant that governs the Registered Agent.

Target Tenant:
: The tenant at the RAS in which the agent or user is authorized.

Agent Status:
: The IdP's current lifecycle state for an agent, including whether
  new authorization is permitted. Only an active agent is eligible.

## Requirements Added by This Profile {#profile-requirements}

The following table identifies this profile's additions and narrowings.
All other requirements of the referenced base protocols still apply.

| Area | Addition or narrowing | Defined in |
|---|---|---|
| Trust | Approved credential authority and tenant context | {{identity}} |
| Identity | Exact, unambiguous mapping to an active Registered Agent | {{identity}} |
| Evidence | Validate the selected credential; distinguish client, agent, and key evidence | {{inputs}} |
| Shared-client ATTEST | Apply the companion claim and trust profile only when that optional input is selected | {{agent-evidence}} |
| Credential use | Apply the selected proof mode and explicit reuse/key-binding limits | {{credential-requirements}} |
| Authorization | Current binding, status, assignments, target, and scope policy | {{authorization}} |
| Delegation | Explicit authorization for the resolved agent to act for the user | {{delegation-approval}} |
| Attribution | Preserve issuer-qualified agent identity and subject/actor roles | {{agent-correlation}} |
| Exchange | ID Token subject and direct JWT actor; both actor parameters REQUIRED | {{exchange-request}} |
| Common capabilities | Platform JWT input, `private_key_jwt`, RS256 signatures, and ES256 DPoP | {{flow-configuration}} |
| Chain scope | One direct user-to-agent relationship; reject pre-existing actor chains on issuance inputs | {{actor-inputs}} |
| Explicit authority | One `resource` and non-empty `scope` REQUIRED in issuance; both claims REQUIRED in the ID-JAG | {{exchange-request}} |
| Actor mapping | Governed `act.sub` and IdP `act.iss`, rather than copying the external credential subject | {{actor-construction}} |
| Proof | DPoP REQUIRED at both token endpoints; same key retained in grant and access token | {{grant-issuance}} and {{redemption}} |
| Lifetime | Finite grant lifetime bounded by input credential expiry; five minutes RECOMMENDED | {{grant-issuance}} |
| Redemption | One matching `resource` REQUIRED; JWT access token with actor and key binding | {{redemption}} |
| Errors | Credential validation uses `invalid_grant`, rather than RFC 8693's `invalid_request` default; delegation denial uses `actor_unauthorized` | {{errors}} |
| Discovery | Role-specific `agent_federation` metadata and configured applicability | {{metadata}} |

These narrowings apply only to this profile. Base ID-JAG or generic
Token Exchange support alone does not imply support for them.

# Profile Selection and Identity Binding {#identity}

The IdP MUST configure:

* Approved credential authorities, their keys or trusted key sources,
  and the validation rules for each accepted credential class.
* Exact external identity selectors and their Source Tenant and
  Registered Agent associations.
* Permitted OAuth clients where the selected flow requires a client.
* Approved RAS issuers, resources, Target Tenants, and applicable
  identity and authorization mappings.

Unsigned request hints, discovered client metadata, and unverified JWT
claims MUST NOT establish credential-authority trust or change an
approved Federation Binding. Metadata can locate an already approved
key source; it does not authorize that source to assert every agent.

The IdP MUST authorize binding creation and changes, including imports
from platform registries. Operators SHOULD authenticate and audit the
administrative source. Binding changes do not alter the validation
rules of the credential itself.

## Selecting the External Identity

| Evidence | Identity used for resolution | Qualification |
|---|---|---|
| Platform JWT | Approved issuer and exact subject, with configured additional selectors | Workload evidence; not automatically OAuth client authentication |
| Client Attestation, agent has its own client | Attester identified by the trusted verification key; client `sub` | Client-to-agent mapping is explicit |
| Shared-client Client Attestation | Approved attester, client `sub`, and signed `attested_agent_id` | Optional input using {{AGENT-ATTEST}} |
| SPIFFE JWT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | OAuth client association follows SPIFFE OAuth |
| SPIFFE X.509-SVID | Approved trust domain and exact SPIFFE ID in the URI SAN | OAuth client authentication follows SPIFFE OAuth |
| SPIFFE WIT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Credential and proof validation follow SPIFFE OAuth and WIMSE |

After validating the evidence, the IdP MUST resolve exactly one active
Registered Agent through an enabled binding. Missing, ambiguous, or
disabled mappings MUST prevent issuance for that agent. Similar names,
matching unqualified strings, or a shared signing key MUST NOT
establish identity equivalence.

A client registration or Client ID Metadata Document {{CIMD}} can
identify an OAuth client. It does not by itself distinguish the
agents behind a shared client. Even when the credential specification
permits a client-identifier association or prefix match, the Federation
Binding MUST resolve the exact authenticated workload identity to one
Registered Agent.

## Canonical Identity and Tenant Boundaries

The Registered Agent identifier MUST be unique and non-reassignable
within the IdP issuer's namespace. It need not equal an external
subject, OAuth client identifier, SPIFFE ID, display name, or instance
identifier. Multiple approved bindings MAY identify the same agent.

The IdP MUST establish an unambiguous Source Tenant and, before
issuance, the Target Tenant for the requested RAS and resource. The
RAS MUST interpret an agent identifier in its asserted issuer or
namespace context. It MUST NOT key agent authorization on bare `sub`.

Trusted key lookup MUST retain the issuer or trust-domain association.
Neither `kid` alone nor a union of unrelated issuers' keys can establish
which authority made an assertion. Separate signing keys are
RECOMMENDED for independently administered signing authorities;
shared keys do not remove issuer-specific authorization checks.

Restarting an execution, replacing a replica, or rotating a key does
not by itself create a new authorization principal. Credential renewal
still follows the credential's own validation and proof rules.

# Evidence and Client Authentication {#inputs}

The IdP MUST validate a credential according to its selected type and
trusted configuration before using it for identity resolution.
A generic JWT token-type URI or a caller-supplied claim MUST NOT select
a weaker validation path. The credential's role in a token request is
determined by the consuming authorization profile.

The IdP MUST distinguish:

* **Client authentication:** evidence authenticating the OAuth client.
* **Agent resolution:** the approved association from validated
  external evidence to the Registered Agent.
* **Key possession:** proof that the presenter controls a particular
  key, with the binding semantics specified by the proof mechanism.

The IdP MUST NOT substitute one role for another. In particular, a
DPoP proof {{RFC9449}} accompanying a bearer credential does not prove
that the credential issuer authorized that proof key. Credential and
proof validation MUST refer to the same request and applicable
principal before the IdP relies on their combination.

Unrecognized request parameters and JWT claims follow {{RFC6749,
Section 3.2}} and {{RFC7519, Section 4}}. This profile defines no
`agent_id` request parameter or claim. An additional claim cannot
switch the identity model or establish a Federation Binding merely
because its name resembles an agent identifier.

## Platform-Issued JWT {#platform-jwt-input}

For an imported workload, the Federation Binding MUST specify an exact
issuer and `sub`. It MAY require additional top-level string claims,
such as tenant or platform agent identifiers. Every configured
selector MUST be present, have the configured type, and match exactly.
These selectors are deployment configuration, not new JWT claims
registered by this document.

The IdP MUST validate the JWT under {{RFC7519}} and {{RFC8725}},
including signature, credential class, accepted audience, and time
claims. Its policy MUST specify:

* The approved issuer, key source, and signature algorithms.
* Audiences authorizing presentation to this IdP for the selected
  workload-evidence purpose.
* A finite credential lifetime and any maximum age, accounting for
  the platform's issuance and caching behavior.
* Rules distinguishing accepted workload credentials from user,
  management-API, or other tokens issued by the same authority.

Classification can use an explicit type, a dedicated issuer, or an
accepted audience combined with exact workload selectors. Generic
`typ=JWT` alone does not distinguish credential classes.

A platform JWT accepted as workload evidence MUST NOT be treated as
OAuth client authentication unless it independently satisfies a
configured client authentication specification. A flow requiring
client authentication MUST validate that authentication separately
and verify its association with the permitted client.

The JWT is presented directly as `actor_token` in {{exchange-request}}.
The IdP resolves its validated identity before constructing the actor.
No identity-normalization access token is needed.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL direct actor input. The client MUST
present the identical compact JWT in `actor_token` and the
`OAuth-Client-Attestation` header and authenticate using the configured
ATTEST method. The IdP MUST validate the attestation and proof before
resolving the agent. {{actor-inputs}} defines the proof/key relationship.

For an agent with its own client, the attester is the configured
authority associated with the trusted key that verified the attestation.
The IdP MUST select that authority unambiguously and resolve the pair
of its identifier and the validated client `sub`. An `iss`, when
present, MUST match that authority. It is not required in this mode.

For a shared client, the IdP and client MUST implement {{AGENT-ATTEST}}
and use its authenticated (`iss`, `sub`, `attested_agent_id`) tuple.
That companion draft owns the claim, attester restrictions, profile
selection, and registration. The IdP MUST resolve the resulting tuple
through a Federation Binding. The configured mode MUST NOT change
based on the presence or absence of a claim.

Both modes produce the governed actor specified in {{actor-construction}},
even when its identifier differs from the attestation's client `sub`.
The own-client path uses base ATTEST and does not depend on the companion
claim registration.

## SPIFFE JWT-SVID {#jwt-svid-input}

JWT-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.1}},
including `client_assertion_type` equal to
`urn:ietf:params:oauth:client-assertion-type:jwt-spiffe`. The assertion
is a JWT-SVID; its sole audience identifies the IdP issuer.

The IdP MUST use signing keys authorized for the trust domain in the
SPIFFE ID and resolve that exact identity through {{identity}}. An
optional `iss` MUST NOT establish a different trust domain or key
authority. Missing `iss` or `iat` alone is not a rejection condition
under this profile. Client-identifier associations follow SPIFFE OAuth;
this document adds no equality requirement beyond that specification.

JWT-SVID remains bearer evidence. Adding DPoP can constrain an issued
token under a consuming profile; it does not convert the JWT-SVID into
a platform-endorsed proof-of-possession credential. The remaining
actor presentation is defined in {{actor-inputs}} and its capability
is advertised under {{metadata}}.

## SPIFFE X.509-SVID {#spiffe-input}

X.509-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.2}}.
The IdP MUST validate the certificate with the configured trust-domain
anchors and resolve the authenticated SPIFFE ID through {{identity}}.
Client identity and TLS proof checks remain those of SPIFFE OAuth.

X.509-SVID MAY authenticate the OAuth client in a delegated request
that also supplies a supported JWT actor credential. Using the TLS
identity alone as actor evidence remains outside this revision;
{{x509-gap}} records that separate composition gap.

## SPIFFE WIT-SVID {#wit-input}

WIT-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.3}}
and {{WIT}}. The IdP MUST validate the credential and required proof,
use trust anchors authorized for the trust domain in `sub`, and
resolve the exact identity through {{identity}}.

The WIT's confirmation key and the authentication proof retain their
specified roles. DPoP alone MUST NOT substitute for a required WIT
or attestation proof. WIT-SVID MAY authenticate the OAuth client when
the request also supplies a supported actor credential. Direct WIT-SVID
actor presentation is outside this revision; the required proof/request
binding is described in {{credential-gap}}.

## Credential Use Requirements {#credential-requirements}

For each accepted credential input, the IdP MUST configure its role,
required proof mechanism, and the assurance required for an output key.
It MUST validate each proof under the selected mechanism; support for
one proof mode MUST NOT imply support for another. This profile adds
that composition requirement using the base credentials.

For bearer JWT-SVID and platform JWT inputs, the IdP MUST NOT infer
platform authorization of a DPoP key from co-presentation or from a
first-use credential-to-key cache. A deployment requiring issuer-
endorsed key possession MUST use evidence that cryptographically binds
the key. A deployment accepting bearer evidence MUST account for theft
of that evidence in its issuance policy.

A reused credential MUST be validated with the current request's
required proof and current binding policy. Credential reuse MUST NOT
bypass proof replay checks or implicitly enroll a replacement key.
The IdP MUST NOT describe a platform identity shared by replicas as
unique instance evidence. Additional instance assurance requires the
evidence and consuming profile discussed in {{instance-identification}}.

Existing credential discovery and authentication-method values retain
their specified meanings. In particular, SPIFFE OAuth's `jwt-spiffe`
assertion-type URI identifies an assertion format, not a registered
`token_endpoint_auth_methods_supported` value. Clients MUST use
{{metadata}} and trusted client configuration to select that optional
input, rather than invent an authentication-method name from the URI.

# Authorization Policy {#authorization}

Identity resolution establishes which agent made the request. It does
not establish an assignment, delegation, or entitlement to a token.
Before authorizing issuance, the IdP MUST:

1. Validate the selected input and all authentication and proofs
   required by the consuming profile.
2. Resolve an active agent through a current, enabled Federation
   Binding and verify any required client association.
3. Resolve the RAS, resource, and Target Tenant through trusted
   configuration and check the requested acting relationship.
4. Apply current assignments and scope policy. Requested authority
   MUST NOT exceed the agent's authorized authority and, for delegated
   access, the user's authority and applicable delegation.
5. Supply the resolved principal and approved authority to the
   selected grant mechanism without substituting the external
   identifier for the governed identity.

If the selected mechanism cannot represent the required identity or
binding, the IdP MUST NOT issue a misleading token by dropping the
actor, changing the credential class, or silently weakening the proof
requirement. This includes attempts to substitute self-acting access
for a denied delegated request.

The delegated wire requirements and their explicit base-protocol
narrowings are specified in {{delegated-flow}}. Authentication and
proof failures retain their mechanism-specific errors as detailed in
{{errors}}.

## Delegation Approval {#delegation-approval}

For user-delegated access, the IdP MUST authorize the resolved agent
to act for that user in the requested client, tenant, RAS, resource,
and scope context. Missing, revoked, expired, or insufficient
delegation MUST prevent issuance. Possession of valid user and agent
credentials, user sign-in, or a shared OAuth client MUST NOT imply
that approval.

Approval records and policy engines are implementation choices.
The decision needs an authenticated approving party, authority to
approve, and a means to withdraw approval. A shared client cannot
reuse one agent's approval for another agent.

The actor is constructed under {{actor-construction}} after delegation
approval. Authenticating a runtime alone does not introduce an actor.
This revision supports a single agent acting directly for a user and
rejects pre-existing actor chains on issuance inputs.

## Canonical Agent Attribution {#agent-correlation}

The intended governed identity is the pair of IdP namespace and
Registered Agent identifier. In self-acting access it identifies the
subject; in user-delegated access it identifies the agent actor.
The delegated output mapping is defined in {{actor-construction}}.
Self-acting WAG access remains deferred under {{wag-gaps}}.

A RAS using provisioned agent records MUST correlate the asserted
issuer-qualified agent identity to the appropriate record. Bare
subjects, display names, or OAuth client identifiers MUST NOT replace
that correlation. A missing record MUST prevent authorization that
depends on that record; it does not prove that the upstream identity
assertion is invalid.

Ownership, groups, and assignments belong to the principal they
describe. User memberships MUST NOT be interpreted as the agent
actor's memberships, or agent memberships as the user's. Where SCIM
`externalId` {{RFC7643}} is used, its provisioning association MUST
retain the issuer and tenant context.

# Delegated ID-JAG Flow {#delegated-flow}

This section defines the actor extension permitted by {{ID-JAG,
Section 9.7}}. It is normative and complete for the common path in
{{scope}}. {{ID-JAG}} supplies the base issuance and redemption
protocol; the requirements below specify this profile's actor inputs,
mapping, authorization, proof binding, and access-token result.

## Configuration and Common Capabilities {#flow-configuration}

Before issuance, the IdP MUST have a trusted association between:

* Its authenticated OAuth client and the client's permitted actor
  evidence classes and Federation Bindings.
* That client and its client registration at the target RAS.
* The user and the subject namespace used for that RAS.
* The Source Tenant, Target Tenant, RAS issuer, and permitted resource.

The IdP and RAS MUST configure this profile as required for the
applicable client and trust relationship. The IdP MUST enforce that
selection even if `actor_token` is omitted. The RAS MUST enforce it
even if `act` or `cnf` is omitted from a presented ID-JAG. Metadata
advertisement alone establishes neither trust nor authorization.

The client MUST be registered at both authorization servers. Both
servers MUST support `private_key_jwt` client authentication using
{{RFC7523, Section 2.2}}; each client assertion MUST use the receiving
token endpoint URL as its audience. Authentication keys and client
identifiers MAY differ between the servers. Other registered methods,
including the optional native credential methods below, MAY be used
when configured at that server.

For a common algorithm set, each role MUST support `RS256` for the
signing or validation operations it performs on platform JWTs, client
assertions, ID-JAGs, and JWT access tokens, and `ES256` for its DPoP
operations. Deployments MAY select other mutually
supported algorithms through trusted configuration and the applicable
metadata. Algorithm support does not imply trust in a signing key.

## Token Exchange Request {#exchange-request}

The client sends an HTTPS POST to the IdP token endpoint, using
`application/x-www-form-urlencoded`, authenticates as the configured
client, and supplies a DPoP proof for that endpoint. The following
parameters are REQUIRED:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `requested_token_type` | `urn:ietf:params:oauth:token-type:id-jag` |
| `subject_token` | User ID Token issued by this IdP for the authenticated client |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:id_token` |
| `actor_token` | Direct credential selected under {{actor-inputs}} |
| `actor_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `audience` | One target RAS issuer identifier |
| `resource` | One resource URI under {{RFC8707}} |
| `scope` | Non-empty scope string for that resource |

This profile narrows ID-JAG by requiring actor evidence, an explicit
resource and scope, and DPoP. `authorization_details`, when present,
retains ID-JAG's processing rules; it does not replace these required
parameters. No new request parameter is introduced.

The IdP MUST validate the ID Token according to {{ID-JAG, Section 4.3.3}},
including its signature, issuer, expiration, audience, and applicable
client-binding checks. The audience MUST identify the authenticated
IdP client. Validation of the user's ID Token does not supply approval
for the actor. The IdP MUST separately apply {{delegation-approval}}.

An IdP MAY additionally accept its own refresh token as `subject_token`
with `subject_token_type=urn:ietf:params:oauth:token-type:refresh_token`,
using ID-JAG's refresh-token subject rules. This support MUST be agreed
in client configuration. The actor credential, client authentication,
DPoP proof, and current delegation checks remain required on every
request. It is not an intermediate actor-normalization token.

## Direct Actor Inputs {#actor-inputs}

The following identifiers are used only in the `actor_inputs_supported`
metadata member defined in {{metadata}}. They are not OAuth token-type
URIs or authentication-method names. Every actor in this revision is
carried with `actor_token_type=urn:ietf:params:oauth:token-type:jwt`.

| Input identifier | Support | Presentation and validation |
|---|---|---|
| `platform_jwt` | REQUIRED at the IdP | JWT in `actor_token`; validate under {{platform-jwt-input}} and authenticate the client separately |
| `spiffe_jwt_svid` | OPTIONAL | Identical compact JWT in `actor_token` and `client_assertion`; native JWT-SVID authentication under {{jwt-svid-input}} |
| `client_attestation` | OPTIONAL | Identical compact JWT in `actor_token` and `OAuth-Client-Attestation`; own-client processing under {{agent-evidence}} |
| `shared_client_attestation` | OPTIONAL | Same presentation as Client Attestation; shared-client processing under {{AGENT-ATTEST}} and {{agent-evidence}} |

The client and IdP MUST select the input using the authenticated
client's configured credential classes and trusted issuer or attester
associations. The IdP MUST reject ambiguous classification. The generic
JWT token-type URI, a token's unverified header, or an agent-like claim
MUST NOT select a weaker validation rule.

For the platform JWT input, `iss`, `sub`, `aud`, and `exp` are REQUIRED.
The issuer and subject MUST match the approved binding; the audience
MUST authorize presentation to this IdP as workload evidence. If the
credential contains `cnf`, the IdP MUST enforce that binding using its
defined proof mechanism. An unsupported binding MUST cause rejection;
it MUST NOT be ignored to obtain bearer treatment.

For either attestation input, the IdP MUST apply ATTEST authentication
and its mode-specific proof checks to the exact JWT in `actor_token`.
The issuance DPoP key MUST match the attestation's confirmation key.
This is an additional key relationship required by this profile even
when normal ATTEST mode permits a separate DPoP key. Combined mode
needs only its existing DPoP proof. Base ATTEST errors remain applicable.

For JWT-SVID, the client uses the `jwt-spiffe` assertion type defined
in SPIFFE OAuth. DPoP binds the output; it does not make the bearer
JWT-SVID a platform-endorsed holder credential. The IdP MUST authorize
the credential/client/agent association and resulting output key under
{{authorization}} and {{credential-requirements}}.

The IdP MUST reject an `actor_token` containing `act`. An ID Token
subject containing `act`, or a refresh-token subject whose retained
authorization context contains an actor chain, is also outside this
revision and MUST be rejected. This profile creates one direct
user-to-agent relationship; it does not discard or rewrite an existing
chain to fit that relationship.

## Actor Resolution and Construction {#actor-construction}

After credential validation, the IdP MUST resolve exactly one active
Registered Agent through {{identity}} and authorize its relationship
to the user, authenticated client, target, and requested authority.
The issued ID-JAG MUST contain a single `act` object with:

* `sub`: the Registered Agent identifier resolved by the binding.
* `iss`: this IdP's issuer identifier, which is the namespace of that
  Registered Agent identifier.

These values MUST be set by the IdP from the approved mapping. Neither
the external credential's `sub` nor an OAuth client identifier is
copied merely because it is authenticated. An identity mapping whose
input and output identifiers happen to coincide is valid only when
that exact association is approved.

The object MUST conform to {{ACTOR-PROFILE, Section 3.4}}, including
its recommendation for `sub_profile` when the actor can be classified.
Omitting classification does not omit actor identity; Actor Profile's
unclassified-actor rules apply. Entity Profiles {{ENTITY-PROFILES}}
remains a transitive dependency of Actor Profile.

This document uses Actor Profile's actor-object and resource-processing
rules, not its Section 6.3 input-to-`act.sub` copying algorithm. The
mapped actor is defined here using ID-JAG's extension point. The meanings
of user `sub`, actor (`iss`, `sub`), and current-presenter `cnf` remain
unchanged; claiming this profile does not imply support for all Actor
Profile grant or Token Exchange processing paths.

## Grant Issuance and Response {#grant-issuance}

The IdP MUST validate the issuance DPoP proof under {{RFC9449}} and
{{ID-JAG, Section 9.8.1.1}} before issuing a grant. Missing or invalid
proofs MUST NOT produce an unbound grant. Nonce processing follows
DPoP, including its challenge errors and fresh-proof retries.

The ID-JAG MUST use the format and claims of {{ID-JAG, Section 3.1}}.
In addition to its base required claims, this profile requires:

| Claim | Required result |
|---|---|
| `sub` | Same user as the validated subject credential, expressed in the IdP's subject namespace for the RAS |
| `act` | Governed actor constructed under {{actor-construction}} |
| `cnf.jkt` | Thumbprint of the validated issuance DPoP key |
| `resource` | The one authorized resource URI, as a string or single-element array |
| `scope` | Non-empty authorized scope string, no broader than the approved request |
| `client_id` | Client identifier at the RAS selected by the trusted client mapping |

The `aud` retains ID-JAG's RAS-issuer semantics. User and target tenant
claims and any subject translation MUST follow ID-JAG's tenant and
subject rules; the agent identifier remains unique within `act.iss`.
The IdP MUST NOT issue a grant if it cannot determine an unambiguous
user, actor, downstream client, or tenant relationship.

The grant lifetime SHOULD be no more than five minutes. The IdP MUST
apply a finite configured limit and MUST NOT extend the grant beyond
the actor credential's expiration or the subject credential's known
expiration. These are this profile's lifetime constraints, not limits
on the lifetime of a platform credential or downstream access token.

The response follows {{ID-JAG, Section 4.3.4}} and {{RFC8693}}:
`access_token` carries the ID-JAG, `issued_token_type` is
`urn:ietf:params:oauth:token-type:id-jag`, and `token_type` is `N_A`.
`expires_in` and response `scope` retain their base-protocol requirements.
The client handles the grant as opaque except for the optional or
recommended inspections already specified by ID-JAG; it MUST retain
the DPoP key for redemption.

## Redemption and Access-Token Issuance {#redemption}

The client sends an authenticated, form-encoded HTTPS POST to the
RAS token endpoint with:

* `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`.
* `assertion` containing the ID-JAG.
* One `resource` equal to the resource authorized by the grant.
* A fresh DPoP proof made with the same key used at issuance.

This profile selects ID-JAG's JWT bearer redemption protocol and
applies its bound-grant processing in {{ID-JAG, Section 9.8.1.2}}.
It defines no separate DPoP grant type. A redemption `scope` MAY request
a subset; if omitted, the grant's scopes are the requested upper bound.

The RAS MUST perform ID-JAG validation and additionally:

1. Require a single `act` object with non-empty `iss` and `sub`, no
   nested `act`, and `act.iss` equal to the ID-JAG issuer. Validate the
   object under Actor Profile's actor-object rules. The configured IdP
   trust relationship MUST authorize assertion of that agent namespace.
2. Require `cnf.jkt`, validate the DPoP proof, and verify the exact key
   match. Client authentication is checked independently against the
   grant's `client_id`; possession of a DPoP key does not replace it.
3. Require the grant's resource and scope constraints. Validate the
   requested resource and any scope reduction, and apply ID-JAG's
   processing for any `authorization_details` present.
4. Resolve the user and governed actor separately. Apply current RAS
   policy to the user/actor relationship, client, tenant, and resource.
   A valid grant sets an authority ceiling; it does not require issuance.
5. Issue a JWT access token under {{RFC9068}} with the RAS as issuer,
   the same user in its local subject namespace, and the resource as
   audience. Copy the validated `act` object unchanged and set top-level
   `cnf.jkt` to the same DPoP key. Preserve all applicable authorization
   constraints in the token or its enforceable resource policy.

The RAS MUST NOT issue broader authority, substitute its authenticated
client for the actor, or return a bearer token. The response uses
`token_type=DPoP` and otherwise follows ID-JAG's access-token response
and RFC 6749. The client MUST NOT use a response that reports a different
token type as completion of this flow.

This profile retains ID-JAG's unexpired-grant reuse and refresh rules;
it does not impose single-use redemption. Each use requires fresh proof
validation and current RAS policy. A RAS SHOULD NOT issue a refresh
token. If it does, it MUST retain the user, governed actor, client,
authority ceiling, and DPoP key binding, and recheck applicable RAS
policy on refresh. Cross-system revocation remains subject to
{{status-changes}}; grant expiry alone does not revoke an issued token.

## API Processing {#api-processing}

The client presents the access token using the DPoP authorization scheme
and a fresh resource-request proof under {{RFC9449}}, including the
access-token hash. The API MUST validate the JWT under {{RFC9068}},
validate the DPoP proof and key binding, and enforce resource and scope
constraints before granting access.

The API MUST apply the user-and-actor authorization rules of
{{ACTOR-PROFILE, Section 8.1}}. It MUST interpret the governed actor in
its `act.iss` namespace and MUST NOT authorize the request solely on
the user's authority when policy also requires agent authorization.
The access-token issuer is the RAS; it does not replace `act.iss`.

## Errors {#errors}

The following outcomes apply to this selected profile. Where a request
has several failures, client authentication and credential/proof
validation precede authorization; error details SHOULD avoid revealing
whether a particular user or agent exists.

| Failure | Error |
|---|---|
| Missing required parameter, unsupported type/combination, ambiguous input classification, or malformed request | `invalid_request` |
| Invalid client authentication | Its configured method's error, normally `invalid_client` |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| Valid identity evidence but absent/disabled agent binding or unauthorized delegation | `actor_unauthorized`, as defined by Actor Profile |
| Unsupported or unauthorized target | `invalid_target` under RFC 8693 and the applicable resource rules |
| Invalid scope | `invalid_scope` |
| Invalid DPoP proof or required nonce | RFC 9449's `invalid_dpop_proof` or `use_dpop_nonce` and required response headers |
| Missing redemption proof or mismatch with grant `cnf.jkt` | `invalid_grant` under ID-JAG |

Actor-credential failures use `invalid_grant` instead of the default
`invalid_request` described by RFC 8693; this narrowing is intentional.
When the same JWT also performs client authentication, its shared
validation failure uses the authentication method's error. ATTEST
retains its claim, proof, freshness, and challenge errors. No failure
permits issuance after dropping the actor or its proof binding.

## Metadata {#metadata}

An authorization server implementing this profile MUST publish an
`agent_federation` object in its {{RFC8414}} metadata. The members are:

| Member | Type and meaning |
|---|---|
| `issuance` | Boolean; `true` advertises the IdP role in this section; omitted means `false` |
| `redemption` | Boolean; `true` advertises the RAS role in this section; omitted means `false` |
| `actor_inputs_supported` | Array of distinct input identifiers from {{actor-inputs}}; REQUIRED when `issuance` is `true`, including `platform_jwt` |

At least one role MUST be `true`. A server supporting both roles MUST
implement both. A client MUST treat incorrectly typed defined members or an
absent object as no usable advertisement for this profile. Unknown
members and unknown actor input identifiers
MUST be ignored by clients; they MUST NOT be interpreted as support
for another known input. This profile defines the listed input values;
future extensions may define additional values and their processing.

The IdP MUST advertise Token Exchange in `grant_types_supported` and
ID-JAG in `identity_chaining_requested_token_types_supported` under
{{ID-JAG, Section 7.1}}. The RAS MUST advertise
JWT bearer grants and `urn:ietf:params:oauth:grant-profile:id-jag` in
`authorization_grant_profiles_supported` under {{ID-JAG, Section 7.2}}.
Both MUST advertise the supported client authentication methods and
DPoP algorithms, including the common capabilities in
{{flow-configuration}}.

The `agent_federation` object, not generic JWT actor support, identifies
this mapped-actor composition. Actor Profile metadata MAY describe
other implemented paths; this profile alone MUST NOT cause a server to
advertise conformance to Actor Profile's entire Token Exchange
algorithm. If `actor_profile_token_exchange` is also published, its
arrays describe those paths independently and MUST NOT contradict
shared ID-JAG capabilities.

Clients MUST verify the relevant role and chosen actor input before
using this flow. The IdP MUST verify the RAS's redemption support as
part of establishing the trusted relationship. The configured profile
requirement remains in force if a parameter or claim is omitted;
advertisement is not a downgrade switch.

# Remaining Gaps and Coordination {#upstream-gaps}

This section is informative. It records problems and specific requests
that remain outside the complete delegated path. The assessed revisions
are WAG-00, ID-JAG-04, Actor Profile-00, SPIFFE OAuth-02, ATTEST-11,
and WIT-02. Interoperability and closure criteria are maintained in the
repository's interoperability cases, not repeated here.

## Self-Acting WAG {#wag-gaps}

**Problem.** WAG's bearer model does not define the complete governed-
agent, sender-constrained composition required here. {{WAG, Section 5}}
already anticipates an IdP issuing a WAG through Token Exchange. That
observation leaves issuance inputs, bound-grant behavior, and capability
selection unspecified. Self-acting access is therefore deferred.

**Request to WAG.** Complete these contracts in WAG, leaving external
identity resolution to this profile:

* IdP issuance from validated workload evidence, with the resulting
  subject in the IdP's governed-agent namespace.
* WAG-owned token-type and JWT-type identifiers and their registrations,
  plus issuance/redemption capability discovery.
* Sender constraint at issuance and redemption, key relationships,
  audience selection, errors, nonce handling, and any replay policy.
* Resource and scope ceilings, including absent or unsupported limits.
  Review continuing access and explain or revise the current refresh
  prohibition in WAG itself.

This document proposes a RAS-issuer audience and DPoP binding to align
with the delegated path. These are requests, not WAG requirements
introduced here. It defines no replacement grant or local refresh
exception.

## Reusable Actor Mapping {#actor-coordination}

**Problem.** Actor Profile's generic credential processing copies an
external subject into the actor; this profile instead resolves a
governed identity under {{actor-construction}}. Repeating that mapping
contract in other consumers could produce inconsistent namespaces.

**Request to Actor Profile.** Consider a reusable principal-resolution
extension point separating credential validation, authorized identity
mapping, and actor construction. This is consolidation work: the
ID-JAG extension defined here does not depend on its adoption. ID-JAG
itself needs no change to permit this actor processing.

## X.509-SVID as the Sole Actor Evidence {#x509-gap}

**Problem.** X.509-SVID authenticates a TLS connection but supplies no
JWT for the `actor_token` field defined in this revision. Client
authentication alone does not select the governed actor.

**Request to consuming profiles, coordinated with SPIFFE OAuth.** Define
an explicit way to bind connection evidence to the requested actor and
any output key. Existing X.509-SVID client authentication remains usable
with a supported actor JWT. No adapter access token is required here.

## Additional Credential Compositions {#credential-gap}

**Problem.** Direct WIT-SVID actor evidence needs a defined relationship
between its native proof, the request carrying `actor_token`, and the
DPoP key. A bearer JWT-SVID or platform JWT also cannot supply an
issuer-endorsed holder key merely by accompanying a DPoP proof.

**Request to consuming credential extensions.** Define any additional
proof/request binding using the existing SPIFFE OAuth, WIMSE, or ATTEST
extension facilities, including capability signaling. ATTEST need not
be reopened. The optional native authentication modes and the direct
JWT actor inputs already defined here remain usable.

## Instance Context {#instance-identification}

**Problem.** A workload identity can span several replicas
{{SPIFFE-CONCEPTS}}. An identifier alone establishes neither continuity
nor enrollment or key replacement. Runtime identification does not by
itself make that runtime an authorization principal.

**Request to a future identification specification and its consumers.**
Define trusted continuity evidence and which instance is described at
each exchange. Self-acting context would describe the subject's
instance; delegated context would describe the actor's instance.
Consumers need explicit retain, replace, or omit rules when the actor
changes. No instance claim or instance-proof protocol is defined here.

## Provisioning and Disablement {#lifecycle-gap}

**Problem.** Ownership, group membership, and disablement need consistent
record correlation and freshness across IdP and RAS. Short-lived grants
do not revoke outstanding tokens. SCIM Agent resources {{SCIM-AGENT}}
and {{RFC7644}} are building blocks, not a complete propagation contract.

**Request to future provisioning and lifecycle specifications.** Define
issuer/tenant-qualified correlation, authoritative properties, update
ordering, freshness bounds, missed-event recovery, and the effect on
outstanding tokens. Enrollment and clone detection initially remain
platform-specific. Model/runtime assurance needs a separate profile
only when producers and consumers agree on its semantics.

# Security Considerations {#security}

The security requirements of the selected credential and grant
specifications, {{RFC9700}}, and {{RFC8725}} apply. The upstream gaps
are material security dependencies; proposed processing is not proof
that a deployment implements those protections.

## Credential and Token Confusion

Validators MUST use mutually exclusive validation rules for the
credential classes they accept under {{RFC8725, Section 3.12}}.
A trusted signature or a matching audience alone MUST NOT convert a
client assertion, platform credential, API access token, or grant
into another credential class.

Credentials and proofs MUST use transport protection required by
their defining protocols. DPoP does not replace HTTPS or client
authentication. Required proofs, nonce handling, and errors follow
the selected mechanism; no input receives a local special-case nonce
or key-enrollment protocol here.

## Time, Replay, and Key Changes {#time-validation}

Validators MUST enforce the selected credential's expiration and
other applicable time claims. Clock skew is a configured deployment
parameter and SHOULD remain small, normally within the few minutes
contemplated by {{RFC7519}}. A skew allowance MUST NOT increase a
configured maximum credential age or permitted lifetime.

Replay protection follows the credential, proof, and grant mechanisms
independently. Where a mechanism requires replay state through
expiration, that state MUST cover the maximum allowed clock skew.
A fresh proof does not make an expired credential valid; an unchanged
identifier does not authorize a new proof key.

The bearer-theft limitation in {{credential-gap}} remains even if the
issued grant or API token is sender-constrained. Deployments requiring
platform-endorsed key possession need evidence that supplies it.

## Trust Isolation and Current Authorization {#status-changes}

The IdP MUST apply current binding and authorization policy before
issuance and reject an inactive agent or withdrawn binding once that
change has been applied. Cached policy data MUST have configured
freshness limits; stale data MUST NOT authorize issuance.

A compromised credential authority can assert identities within its
trusted scope. Exact bindings, tenant boundaries, issuer-scoped key
lookup, and limits on attester authority constrain that scope; a new
JWT type does not repair excessive trust.

The optional shared-client input inherits the attester trust and key
isolation considerations of {{AGENT-ATTEST}}. A valid attestation still
requires the separate delegation decision in {{delegation-approval}}.

Cross-system disablement and token revocation require the mechanisms
in {{lifecycle-gap}}. Without an applicable signal or online check, an
already issued token can remain usable until expiration. Refresh
semantics remain those of WAG, ID-JAG, and the RAS's applicable profile;
this document does not grant new refresh authority.

# Privacy Considerations {#privacy}

A stable agent identifier can correlate activity across resources,
users, or execution instances. Issuers SHOULD disclose only the agent
attributes needed for the authorized purpose. User and agent context
remain separate when the agent acts for a user.

The mapping in {{actor-construction}} keeps external workload
identifiers out of the ID-JAG. The RAS preserves the governed actor
identifier; this profile does not define pairwise actor translation.

Instance context can increase correlation further. Any consuming
profile introducing it needs purpose limits, retention guidance, and
clear rules about whose activity it describes.

# IANA Considerations {#iana}

This document requests registration in the "OAuth Authorization Server
Metadata" registry established by {{RFC8414, Section 7.1}}:

* Metadata Name: `agent_federation`
* Metadata Description: Object identifying delegated agent-federation
  issuance and redemption capabilities, including supported actor inputs.
* Change Controller: IETF
* Specification Document(s): {{metadata}} of this document.

The member names and values of this object are defined in {{metadata}};
no new registry is created. The attested-agent claim registration is
requested by {{AGENT-ATTEST}}. This document requests no grant type,
JWT type, or OAuth token-type URI registration.

--- back

# Supporting Material {#supporting-material}

Protocol requirements and the remaining gap summaries are in this
document. The repository holds informative examples and test criteria:
[deployment scenarios](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md),
[interoperability cases](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/interoperability.md), and
[a coordination index](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/coordination.md).
The criteria have one home in the repository; they add no normative
requirements. The complete delegated protocol is specified above.

RFC Editor: Remove this appendix and repository links before RFC
publication, or replace them with stable informative references.

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
