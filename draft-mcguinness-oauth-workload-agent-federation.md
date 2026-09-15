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
  ICA: I-D.mcguinness-oauth-id-continuation-assertion
  INSTANCE:
    title: "Client Instance Identification for Attestation-Based Client Authentication"
    target: https://github.com/mcguinness/draft-mcguinness-oauth-client-instance-assertion/blob/26abba5fb612381331c670f4d6dfc54737f698af/draft-mcguinness-oauth-client-instance-id.md
    author:
      - name: Karl McGuinness
    date: 2026-09
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-instance-id-latest
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
  RFC6755:
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
An IdP-issued refresh token is an optional subject input under
{{exchange-request}}.
Continuing access is OPTIONAL and uses the Identity Continuation Assertion
(ICA) composition in {{continuing-access}}. The common path does not
require that extension or the optional instance-identification input. Additional
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
| Continuing access, continuation evidence, and chain lifecycle | {{ICA}}, composed under {{continuing-access}} |
| Actor object, current actor, and actor-aware resource policy | Selected rules of {{ACTOR-PROFILE}}, as specified in {{actor-construction}} |
| Base workload authentication and proofs | SPIFFE OAuth, WIMSE, and ATTEST |
| Attested instance identity, continuity, and receiver scoping | {{INSTANCE}}; this profile defines instance-to-agent resolution |
| Self-acting workload grant | WAG; requested changes in {{wag-gaps}} |
| Self-acting subject resolution and agent linking | Proposed composition in {{wag-subject-resolution}}; dependent on the WAG grant contract |
| Downstream instance context | {{INSTANCE}} defines the object; propagation through this flow is outside this revision |
| Agent provisioning and disablement signals | Future provisioning and lifecycle specifications |

This document defines requirements locally where the base protocol
permits extensions. It uses ID-JAG's actor extension point and imports
Actor Profile's representation rules; it does not claim conformance to
Actor Profile's different credential-to-subject copying algorithm.
The optional instance-attestation input uses the editor's copy of
{{INSTANCE}}, pinned by the reference to the reviewed repository revision.
It is a dependency only for that input; the reference
does not imply that the identification draft has been submitted to
the Datatracker. This document defines no additional agent-identity claim.

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
The requirements of each selected base protocol or referenced section
also apply, subject to the explicit narrowings below.

| Area | Addition or narrowing | Defined in |
|---|---|---|
| Trust | Approved credential authority and tenant context | {{identity}} |
| Identity | Exact, unambiguous mapping to an active Registered Agent | {{identity}} |
| Subject resolution | Target-specific user identifier; one local subject; authorized account linking and fail-closed conflict handling | {{subject-resolution}} |
| Evidence | Validate the selected credential; distinguish client, agent, and key evidence | {{inputs}} |
| Instance ATTEST | Validate Identification's instance evidence, then resolve its approved agent binding and client association | {{instance-agent-resolution}} |
| Credential use | Apply the selected proof mode and explicit reuse/key-binding limits | {{credential-requirements}} |
| Authorization | Current binding, status, assignments, target, and scope policy | {{authorization}} |
| Delegation | Explicit authorization for the resolved agent to act for the user | {{delegation-approval}} |
| Attribution | Preserve issuer-qualified agent identity and subject/actor roles | {{agent-correlation}} |
| Root exchange | ID Token or supported IdP refresh-token subject, with a direct JWT actor; both actor parameters REQUIRED | {{exchange-request}} |
| Common capabilities | Platform JWT input, `private_key_jwt`, RS256 signatures, and ES256 DPoP | {{flow-configuration}} |
| Chain scope | One direct user-to-agent relationship; reject pre-existing actor chains on issuance inputs | {{actor-inputs}} |
| Explicit authority | One `resource` and non-empty `scope` REQUIRED in issuance; both claims REQUIRED in the ID-JAG | {{exchange-request}} |
| Actor mapping | Governed `act.sub` and IdP `act.iss`, rather than copying the external credential subject | {{actor-construction}} |
| Proof | DPoP REQUIRED at both token endpoints; same key retained in grant and access token | {{grant-issuance}} and {{redemption}} |
| Root grant lifetime | Finite grant lifetime bounded by input credential expiry; five minutes RECOMMENDED | {{grant-issuance}} |
| Redemption | One matching `resource` REQUIRED; JWT access token with actor and key binding | {{redemption}} |
| Continuing access | Optional ICA composition; same governed actor; no RAS refresh tokens | {{continuing-access}} |
| API | Configured applicability independent of token contents; required actor and proof validation, with resource errors | {{api-processing}} |
| Errors | Credential validation uses `invalid_grant`, rather than RFC 8693's `invalid_request` default; delegation denial uses `actor_unauthorized` | {{errors}} |
| Discovery | ID-JAG grant-profile URI for RAS and client support; configured IdP support and optional inputs | {{metadata}} |

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
| Instance Client Attestation | Validated (`iss`, `client_instance_id`), associated with the authenticated client `sub` | Optional input using {{INSTANCE}} and {{instance-agent-resolution}} |
| SPIFFE JWT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | OAuth client association follows SPIFFE OAuth |
| SPIFFE X.509-SVID | Approved trust domain and exact SPIFFE ID in the URI SAN | Client authentication only in this revision; separate actor evidence required |
| SPIFFE WIT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Client authentication only in this revision; separate actor evidence required |

After validating the selected actor evidence, the IdP MUST resolve
exactly one active Registered Agent through an enabled binding. Missing,
ambiguous, or disabled mappings MUST prevent issuance for that agent.
Similar names, matching unqualified strings, or a shared signing key MUST NOT
establish identity equivalence.

A client registration or Client ID Metadata Document {{CIMD}} can
identify an OAuth client. It does not by itself distinguish the
agents behind a shared client. Even when the credential specification
permits a client-identifier association or prefix match, the Federation
Binding MUST resolve the exact workload identity selected as actor
evidence to one Registered Agent.

Evidence used only for client authentication identifies the OAuth
client; it does not require a Registered Agent mapping. The IdP MUST
check that the authenticated client is permitted to use the selected
actor evidence and its Federation Binding under {{flow-configuration}}.
It MUST NOT substitute that client's identity for the resolved actor.

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

## Subject Resolution and Linking {#subject-resolution}

Subject resolution determines which user an authenticated identifier
represents. Linking establishes an approved association between that
external identity and a local account. Neither operation authorizes the
agent to act for the user. This section profiles ID-JAG's subject
resolution rules; it defines no new identifier claim or linking protocol.
For self-acting access, the corresponding subject is the governed agent;
{{wag-subject-resolution}} identifies the required WAG composition.

### Resolution at the IdP {#idp-subject-resolution}

After validating the subject credential under {{exchange-request}},
the IdP MUST:

1. Resolve exactly one user from the ID Token's issuer-qualified subject
   and applicable tenant context, or from the validated refresh token's
   authorization context. The actor credential and authenticated client
   MUST NOT substitute for that user identity.
2. Select the subject namespace associated with the target RAS's SSO
   relationship under {{ID-JAG, Section 5}}. A client-specific pairwise
   subject MUST NOT be copied into another relying party's namespace
   without resolving the same user in that namespace.
3. Issue `sub` and any additional subject identifiers for that same
   user under {{ID-JAG, Sections 3.1 and 6}}. The IdP MUST derive
   `aud_sub`, `aud_tenant`, or `sub_id`, when used, from an authoritative
   association for the target; a client-supplied account hint does not
   establish that association.

The resulting ID-JAG `sub` remains in the IdP's namespace for the RAS;
`aud_sub`, when present, identifies the RAS's local user. Equal strings
in different namespaces do not establish a link.

### Resolution at the RAS {#ras-subject-resolution}

After validating the ID-JAG and its client and proof bindings, the RAS
MUST resolve exactly one local user in the authorized Target Tenant
before issuing an access token. Its configured resolution rules MUST:

* Qualify `sub` by the validated IdP issuer and the tenant context
  required by {{ID-JAG, Section 6}}. The RAS MUST NOT assume that an IdP
  tenant identifier is its own local tenant identifier.
* Use `aud_sub` only when the trusted IdP is authorized to assert local
  account identifiers for the selected Target Tenant. An asserted local
  identifier MUST NOT override a conflicting approved link.
* Use `sub_id` only under ID-JAG's format-specific and issuer-association
  rules ({{ID-JAG, Sections 3.2.2 and 9.5}}). A SAML NameID retains its
  issuer, format, and applicable qualifiers; its value alone is not a
  cross-namespace identifier.
* Reject conflicting identifiers used for resolution or multiple local
  matches. The RAS MUST NOT retry with a weaker selector or another
  tenant after such a conflict.

The access token's `sub` identifies that resolved user in the RAS's
access-token namespace. The RAS resolves `act.iss` and `act.sub`
separately under {{agent-correlation}} and MUST NOT link the agent to
the user's account merely because it acts for that user.

### Account Links and Their Lifecycle {#subject-linking}

The RAS MAY use pre-provisioned links, an authorized account-linking
flow, or just-in-time account creation. These are deployment choices,
subject to the following requirements:

* Creating or changing a link to an existing account MUST require an
  authenticated administrative or provisioning authority authorized for
  that account, or a user flow that verifies control of both identities.
  A valid ID-JAG alone does not authorize linking to an arbitrary account.
* Matching email, username, or display-name attributes alone MUST NOT
  create or change a link. This narrows ID-JAG's flexible claim-based
  resolution. A configured, issuer-qualified SAML NameID remains usable
  under {{ras-subject-resolution}}, including an email-format NameID.
* Just-in-time creation MUST be authorized for the issuer and Target
  Tenant. A collision with an existing account MUST NOT silently merge
  accounts or reactivate a disabled account. Creating a record does not
  itself grant memberships, entitlements, or delegation approval.
* Each qualified external identity MUST resolve to at most one local
  account within a Target Tenant. Multiple external identities MAY link
  to the same account when each link is independently authorized.
* A removed, disabled, or reassigned link MUST NOT let a previously
  issued grant authorize a different account. Link changes MUST NOT
  transfer existing delegation approval or ICA continuation authority
  to another user. Implementations MUST reject further use when they
  cannot establish continuity with the originally authorized user.

If the user or a required link is disabled, or resolution is missing,
ambiguous, or conflicting, token issuance MUST fail under {{errors}}. Operators
SHOULD audit link creation, changes, and removal. This document does
not require a particular mapping database or provisioning protocol.

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

For instance-based agent resolution, including agents sharing an OAuth
client, the IdP and client MUST use {{instance-agent-resolution}}.
The client and IdP MUST select own-client or instance-based resolution
through trusted client configuration before accepting requests. Claims
MUST NOT switch modes, and failed instance validation MUST NOT fall back
to own-client resolution.

Both inputs produce the governed actor under {{actor-construction}}.
The own-client input uses base ATTEST without requiring Identification.

### Instance-to-Agent Resolution {#instance-agent-resolution}

The `instance_attestation` input uses {{INSTANCE}} to identify an
enrolled installation or execution unit. Identification supplies
instance evidence; this profile supplies the approved agent mapping
and the separate authorization decision. The IdP MUST:

1. Act as a Receiver under Identification and apply its Receiver
   validation and instance-policy requirements, using the configured
   attester trust, client association, receiver scope, granularity,
   continuity evidence, and freshness limits.
   Validate the ATTEST proof and the output-key relationship in
   {{actor-inputs}} against the same attestation in the request.
2. Use the validated (`iss`, `client_instance_id`) pair as the external
   instance identity. Match it exactly through an enabled Federation
   Binding to one active Registered Agent, checking the authenticated
   client `sub`, Source Tenant, and configured receiver scope. A shared
   OAuth client or matching proof key MUST NOT establish that binding.
3. Reject a missing or ambiguous agent mapping. Several instances MAY
   map to one agent. An instance hosting several agents is insufficient
   evidence for selecting among them; this input defines no additional
   agent selector. Such a deployment needs another supported input
   that unambiguously identifies the selected agent.
4. Apply {{authorization}} and {{delegation-approval}} to the resolved
   agent. Set `act` from the governed identity under
   {{actor-construction}}, not from the instance identifier.

The attester remains responsible for enrollment and continuity evidence
under Identification; an identifier alone does not prove continuity.
Renewal and verified key changes retain or replace instance identity
only under Identification's lifecycle rules. A new instance identifier
requires an approved binding; the IdP MUST NOT inherit one merely from
an earlier key, shared client, or claimed predecessor. The new binding
MAY resolve to the same governed agent. Neither instance continuity nor
a new binding transfers an existing grant to a replacement key.

Identification claim and instance-policy failures use its
`invalid_client_attestation` error. After successful instance validation,
missing, disabled, or ambiguous agent bindings and denied delegation use
`actor_unauthorized` under {{errors}}. The distinction does not permit
disclosure of instance or agent status in error details.

This input does not define downstream instance-context propagation.
The IdP MUST NOT copy `client_instance_id` into `act.sub` merely because
it was authenticated. {{instance-identification}} records the remaining
context composition work.

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
actor presentation is defined in {{actor-inputs}} and its use is agreed
through trusted configuration under {{metadata}}.

## SPIFFE X.509-SVID {#spiffe-input}

X.509-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.2}}.
The IdP MUST validate the certificate with the configured trust-domain
anchors and associate the authenticated SPIFFE ID with the OAuth client.
Client identity and TLS proof checks remain those of SPIFFE OAuth.

X.509-SVID MAY authenticate the OAuth client in a delegated request
that also supplies a supported JWT actor credential. Using the TLS
identity alone as actor evidence remains outside this revision;
{{x509-gap}} records that separate composition gap.

## SPIFFE WIT-SVID {#wit-input}

WIT-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.3}}
and {{WIT}}. The IdP MUST validate the credential and required proof,
use trust anchors authorized for the trust domain in `sub`, and
associate the authenticated identity with the OAuth client.

The WIT's confirmation key and the authentication proof retain their
specified roles. DPoP alone MUST NOT substitute for a required WIT
or attestation proof. WIT-SVID MAY authenticate the OAuth client when
the request also supplies a supported actor credential. Direct WIT-SVID
actor presentation is outside this revision as a scope choice described
in {{credential-gap}}, not because SPIFFE OAuth lacks a proof mechanism.

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
   configuration, resolve the user under {{idp-subject-resolution}},
   and check the requested acting relationship.
4. Apply current assignments and scope policy. Issued authority
   MUST NOT exceed the agent's authorized authority and, for delegated
   access, the user's authority and applicable delegation.
5. Supply the resolved principal and approved authority to the
   selected grant mechanism without substituting the external
   identifier for the governed identity.

The IdP MAY grant an authorized, non-empty subset of the requested
scopes when policy permits partial approval. It MUST return
`invalid_scope` if no requested scope can be granted or policy requires
full approval and the request exceeds that approval. The grant and
response MUST reflect any scope reduction under {{grant-issuance}}.
Narrowing scope does not waive the target or delegation checks.

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
to act for that user in the client, tenant, RAS, resource, and scope
context approved for issuance. Missing, revoked, expired, or insufficient
delegation for that authority MUST prevent issuance. Possession of valid
user and agent credentials, user sign-in, or a shared OAuth client MUST NOT imply
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
Its proposed subject-resolution and linking contract is described in
{{wag-subject-resolution}}.

A RAS using provisioned agent records MUST correlate the asserted
issuer-qualified agent identity to the appropriate record. Bare
subjects, display names, or OAuth client identifiers MUST NOT replace
that correlation. A missing record MUST prevent authorization that
depends on that record; it does not prove that the upstream identity
assertion is invalid.

Creating or changing that agent correlation MUST be authorized for the
governed agent and Target Tenant. User-account links and agent-record
links MUST remain distinct. A changed Federation Binding or local agent
link MUST NOT transfer an existing delegation to a different agent.

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
* The user and the subject namespace used for that RAS, following
  {{subject-resolution}}.
* The Source Tenant, Target Tenant, RAS issuer, and permitted resource.

The IdP and RAS MUST configure this profile as required for the
applicable client and trust relationship. The IdP MUST enforce that
selection even if `actor_token` is omitted. The RAS MUST enforce it
even if `act` or `cnf` is omitted from a presented ID-JAG. Metadata
advertisement alone establishes neither trust nor authorization.

The client MUST be registered at both authorization servers. Both
servers MUST support `private_key_jwt` client authentication using
{{RFC7523, Section 2.2}}. For `private_key_jwt`, each client assertion
MUST use the receiving token endpoint URL as its audience. Authentication
keys and client identifiers MAY differ between the servers. Other
registered methods, including the optional native credential methods below, MAY be used
when configured at that server.

Native methods retain their own audience requirements. In particular,
a JWT-SVID client assertion uses the IdP issuer identifier as its sole
audience under {{jwt-svid-input}}, not the token endpoint URL. A Client
Attestation PoP JWT uses the audience required by ATTEST.

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
| `subject_token` | User ID Token, or a refresh token when supported, issued by this IdP for the authenticated client |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:id_token` for an ID Token; `urn:ietf:params:oauth:token-type:refresh_token` for a refresh token |
| `actor_token` | Direct credential selected under {{actor-inputs}} |
| `actor_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `audience` | One target RAS issuer identifier |
| `resource` | One resource URI under {{RFC8707}} |
| `scope` | Non-empty scope string for that resource |

This profile narrows ID-JAG by requiring actor evidence, an explicit
resource and scope, and DPoP. `authorization_details`, when present,
retains ID-JAG's processing rules; it does not replace these required
parameters. No new request parameter is introduced.

The IdP MUST support ID Token subjects and MAY additionally support its
own refresh tokens. Refresh-token support MUST be agreed in client
configuration. The IdP MUST validate the selected subject token under
{{ID-JAG, Section 4.3.3}}:

* For an ID Token, validate its signature, issuer, expiration, audience,
  and applicable client-binding checks. The audience MUST identify the
  authenticated IdP client.
* For a refresh token, apply the validation used for a `refresh_token`
  grant, including issuance by this IdP, binding to the authenticated
  client, validity, revocation status, and applicable proof requirements.
  Requested scopes and audience MUST remain within the refresh token's
  retained authorization context.

Neither subject input supplies approval for the actor. The actor
credential, client authentication, DPoP proof, and current delegation
checks under {{delegation-approval}} remain required on every request.
Using a refresh token avoids obtaining a new ID Token solely for this
exchange; the request still uses the Token Exchange grant type and
requests an ID-JAG. It does not request a RAS refresh token.

## Direct Actor Inputs {#actor-inputs}

The following labels identify the input choices in this document and
trusted configuration. They are not wire parameters, OAuth token-type
URIs, or authentication-method names. Every root actor in this revision is
carried with `actor_token_type=urn:ietf:params:oauth:token-type:jwt`.

| Input | Support | Presentation and validation |
|---|---|---|
| `platform_jwt` | REQUIRED at the IdP | JWT in `actor_token`; validate under {{platform-jwt-input}} and authenticate the client separately |
| `spiffe_jwt_svid` | OPTIONAL | Identical compact JWT in `actor_token` and `client_assertion`; native JWT-SVID authentication under {{jwt-svid-input}} |
| `client_attestation` | OPTIONAL | Identical compact JWT in `actor_token` and `OAuth-Client-Attestation`; own-client processing under {{agent-evidence}} |
| `instance_attestation` | OPTIONAL | Same presentation as Client Attestation; validate Identification and the instance-to-agent binding under {{instance-agent-resolution}} |

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
to the user, authenticated client, target, and approved authority.
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
claims and any subject translation MUST follow {{subject-resolution}};
the agent identifier remains unique within `act.iss`.
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
4. Resolve the user under {{ras-subject-resolution}} and the governed
   actor under {{agent-correlation}}. Apply current RAS policy to the
   user/actor relationship, client, tenant, and resource.
   A valid grant sets an authority ceiling; it does not require issuance.
5. Issue a JWT access token under {{RFC9068}} with the RAS as issuer,
   the same user in its local subject namespace, and the resource as
   audience. Copy the validated `act` object unchanged and set top-level
   `cnf.jkt` to the same DPoP key. Include the non-empty authorized scope
   string in `scope`; if no scope can be granted, return `invalid_scope`.
   Preserve all applicable authorization constraints in the token or
   its enforceable resource policy.

The RAS MUST NOT issue broader authority, substitute its authenticated
client for the actor, or return a bearer token. The response uses
`token_type=DPoP` and otherwise follows ID-JAG's access-token response
and RFC 6749. The client MUST NOT use a response that reports a different
token type as completion of this flow.

This profile retains ID-JAG's unexpired-grant reuse; it does not impose
single-use redemption. Each use requires fresh proof validation and
current RAS policy. Continuing access follows {{continuing-access}};
grant expiry alone does not revoke an issued token.

### Continuing Access {#continuing-access}

Deployments offering continuing access under this profile MUST use
{{ICA}}. A trusted Continuation Assertion Issuer (CAI) attests to an
accepted, active authorization; the agent exchanges that assertion at
the IdP for a new ID-JAG. This keeps continuation subject to IdP
authorization. The RAS MUST NOT issue refresh tokens on root or onward
ID-JAG redemption, narrowing ID-JAG's SHOULD NOT. An IdP refresh token
remains an optional root subject credential under {{exchange-request}}.

#### Establishing Continuation

The root exchange retains this profile's direct actor evidence and
delegation checks. To establish continuation, the IdP MUST also:

* Apply ICA's chain-establishment and lifecycle-anchor requirements.
  An eligible user session or, where supported, the IdP refresh token's
  OAuth grant anchors the chain; credential expiry alone does not
  define the chain lifetime.
* Require the authenticated client's configured canonical actor identity
  under {{ICA, Section 5.5.2}} to equal the governed `(iss, sub)` pair
  resolved under {{actor-construction}}. A shared client with no
  unambiguous mapping to that agent cannot establish this composition.

If continuation cannot be established, an otherwise valid root exchange
can issue an ordinary ID-JAG without a continuation handle, following
{{ICA, Section 5.1}}. The client MUST NOT infer continuation authority
from successful root issuance. A continuation-aware RAS MUST implement
ICA's acceptance and handle-binding requirements.

#### Continuing as the Governed Agent

The client, CAI, IdP, and RAS MUST implement their applicable ICA roles,
including assertion issuance, validation, replay handling, trust,
errors, and recovery. In particular:

* The continuation request uses ICA as `subject_token` and carries no
  `actor_token` or `actor_token_type`. ICA's client authentication and
  assertion matching replace this profile's root actor-input processing.
* For this composition, the current actor MUST remain the root's
  Registered Agent. The IdP MUST recheck current agent, binding, and
  delegation policy as well as ICA's chain authorization. Continuation
  involving a different actor is outside this profile.
* The IdP MUST resolve the chain's original user for each target under
  {{subject-resolution}}. A continuation handle or prior target's local
  account identifier MUST NOT substitute for the new target's subject
  resolution or authorize a new account link.
* The request MUST identify one resource and a non-empty scope. The
  onward grant follows {{ICA, Section 5.5.5}} and retains this profile's
  governed actor, resource, scope, and downstream client requirements.
  Its lifetime and key binding follow ICA rather than the root input
  credential limits in {{grant-issuance}}.
* Redemption uses ICA's DPoP-bound JWT grant,
  `urn:ietf:params:oauth:grant-type:jwt-dpop`, instead of the root flow's
  JWT bearer grant. The additional RAS checks and access-token requirements
  in {{redemption}}, and API processing in {{api-processing}}, still apply.

ICA governs chain lifetime and termination; this document defines no
separate continuation deadline or renewal protocol. Ending a chain
prevents further continuation but does not itself revoke outstanding
grants or access tokens; {{status-changes}} still applies.

## API Processing {#api-processing}

The API MUST determine which request paths require this profile from
trusted resource configuration, independently of the presented token's
claims. An absent or malformed `act` MUST NOT select non-delegated
processing on those paths. Other configured resource paths can accept
other token profiles.

The client presents the access token using the DPoP authorization scheme
and a fresh resource-request proof under {{RFC9449}}, including the
access-token hash. On a path requiring this profile, the API MUST:

1. Validate the JWT under {{RFC9068}} and require non-empty `scope` and
   `cnf.jkt` claims with their defined types.
2. Require a single `act` object with non-empty `iss` and `sub`, no
   nested `act`, and the structure in {{ACTOR-PROFILE, Section 3.4}}.
   Trusted configuration MUST authorize the RAS to assert that actor
   namespace. The RAS is the access-token issuer; `act.iss` remains the
   IdP namespace and need not equal the access token's `iss`.
3. Validate the DPoP proof and key binding, and enforce resource, scope,
   and any additional authorization constraints.
4. Apply {{ACTOR-PROFILE, Section 8.1}} to the user and issuer-qualified
   actor. The API MUST NOT treat the request as non-delegated. It MUST
   reject the request if required actor authorization cannot be
   established, including when policy information is unavailable.

Resource errors use the `DPoP` `WWW-Authenticate` challenge under
{{RFC9449, Section 7.1}}, with the following outcomes:

| Failure | HTTP status and error |
|---|---|
| Invalid token, missing required claim, malformed actor, nested actor, or unauthorized actor namespace assertion | 401, `invalid_token` |
| Valid token but required user/actor relationship is not authorized or cannot be established | 403, `actor_unauthorized`, following {{ACTOR-PROFILE, Section 8.2}} |
| Insufficient token scope for the operation | 403, `insufficient_scope` |
| Missing or invalid proof, key mismatch, or required nonce | RFC 9449 resource error processing, including its nonce header and challenge rules |

Actor authorization failures MUST NOT use `insufficient_scope`.
The API MUST NOT expose actor-specific rejection details outside the
trust domain. Token endpoint errors in {{errors}} do not replace these
resource error responses.

## Errors {#errors}

The following outcomes apply to this selected profile. Where a request
has several failures, client authentication and credential/proof
validation precede authorization; error details SHOULD avoid revealing
whether a particular user or agent exists.

| Failure | Error |
|---|---|
| Missing required parameter, unsupported type/combination, ambiguous input classification, or malformed request | `invalid_request` |
| Invalid client authentication | Its configured method's error, normally `invalid_client` |
| Instance-identification claim or instance-policy failure | `invalid_client_attestation` under Identification |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Valid identity evidence but absent, disabled, or ambiguous agent binding, or unauthorized delegation | `actor_unauthorized`, as defined by Actor Profile |
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

This profile is identified by:

`urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`

The RAS MUST include that URI in `authorization_grant_profiles_supported`
in its {{RFC8414}} metadata, using {{ID-JAG, Section 7.2}}. It indicates
support for this profile's redemption and access-token requirements.
A client SHOULD include the same URI in its client metadata under
{{ID-JAG, Section 8}} to advertise its corresponding client role.
These advertisements establish capability, not trust or authorization.

The IdP MUST advertise Token Exchange in `grant_types_supported` and
ID-JAG in `identity_chaining_requested_token_types_supported` under
{{ID-JAG, Section 7.1}}. The RAS MUST advertise
JWT bearer grants and `urn:ietf:params:oauth:grant-profile:id-jag` in
`authorization_grant_profiles_supported` under {{ID-JAG, Section 7.2}}.
Both MUST advertise the supported client authentication methods and
DPoP algorithms, including the common capabilities in
{{flow-configuration}}.

ID-JAG defines `authorization_grant_profiles_supported` for the RAS
and client roles; its presence does not advertise IdP issuance support.
The client and IdP MUST agree on this profile's issuance support through
the trusted configuration in {{flow-configuration}}. That agreement MUST
also identify any optional actor inputs and refresh-token subject support
used by the client. Support for the required platform-JWT input follows
from IdP conformance. Generic JWT input or client-authentication metadata
alone does not advertise an optional actor composition.

Continuing access additionally uses the metadata and trust configuration
in {{ICA, Section 7}}. For this composition, the IdP MUST advertise
`identity_continuation_supported` as `true`; a continuation-aware RAS
MUST advertise ICA's continuation grant profile and required grant types.
This profile's URI alone does not advertise ICA support or
authorize establishment of a continuation chain.

Actor Profile metadata MAY describe other implemented paths; this
profile alone MUST NOT cause a server to
advertise conformance to Actor Profile's entire Token Exchange
algorithm. If `actor_profile_token_exchange` is also published, its
arrays describe those paths independently and MUST NOT contradict
shared ID-JAG capabilities.

Clients MUST verify the RAS's profile advertisement and the configured
IdP support and chosen input before using this flow. The IdP MUST verify
the RAS's profile advertisement as part of establishing the trusted
relationship. The configured profile requirement remains in force if
a parameter or claim is omitted;
advertisement is not a downgrade switch.

# Remaining Gaps and Coordination {#upstream-gaps}

This section is informative. It records problems and specific requests
that remain outside the complete delegated path. The assessed revisions
are WAG-00, ID-JAG-04, ICA-02, Actor Profile-00, SPIFFE OAuth-02,
ATTEST-11, and WIT-02.

## Self-Acting WAG {#wag-gaps}

**Problem.** WAG's bearer model does not define the complete governed-
agent, sender-constrained composition required here. {{WAG, Section 5}}
already anticipates an IdP issuing a WAG through Token Exchange. That
observation leaves issuance inputs, bound-grant behavior, and capability
selection unspecified. Self-acting access is therefore deferred.

**Request to WAG.** Complete these contracts in WAG, leaving external
identity resolution and governed-agent linking to this profile:

* IdP issuance from validated workload evidence, with the resulting
  subject in the IdP's governed-agent namespace.
* IdP issuance using its own refresh token as `subject_token`, where
  retained authorization permits continuing self-acting workload access.
  Define how that authorization is established, how the governed subject
  and client are bound, which current workload evidence and proofs are
  required, and how revocation and authority limits are enforced. A
  user's refresh token alone does not establish independent agent authority.
* WAG-owned token-type and JWT-type identifiers and their registrations,
  plus issuance/redemption capability discovery. A self-acting grant
  profile can use `authorization_grant_profiles_supported`; the
  ID-JAG agent-federation URI does not advertise WAG support.
* Sender constraint at issuance and redemption, key relationships,
  audience selection, errors, nonce handling, and any replay policy.
* Resource and scope ceilings, including absent or unsupported limits.
  Review continuing access and explain or revise the current refresh
  prohibition at WAG redemption. That output prohibition is distinct
  from accepting an existing IdP refresh token as an issuance input;
  WAG does not currently specify the latter composition.

This document proposes a RAS-issuer audience and DPoP binding to align
with the delegated path. These are requests, not WAG requirements
introduced here. It defines no replacement grant or local refresh
exception.

### Self-Acting Subject Resolution and Linking {#wag-subject-resolution}

The WAG composition needs an explicit subject-resolution contract,
parallel to {{subject-resolution}}. The subject is the governed agent,
not a user on whose behalf it acts. The following are proposed profile
requirements, not a claim that this revision defines a complete WAG flow:

| Stage | Required identity relationship |
|---|---|
| Workload evidence to IdP | Validated external identity resolves through an approved Federation Binding to one active Registered Agent |
| IdP-issued WAG | Issuer-qualified `sub` identifies that governed agent; no `act` is needed solely to identify its executing instance |
| WAG to local authorization | The RAS resolves the governed identity to one local agent principal in the authorized Target Tenant |
| Access token to API | The token identifies the same agent in the RAS's subject namespace; authorization uses that agent's authority |

The consuming profile needs to apply these linking rules:

* Scope identity lookup to the trusted grant issuer, its subject namespace,
  and the established tenant relationship. An external workload subject,
  OAuth client identifier, or instance identifier is not automatically
  the governed or local agent identifier.
* Authorize creation and changes of local agent links for that issuer and
  Target Tenant. Several approved workload bindings can identify one
  governed agent, but a selected binding or local link cannot resolve
  ambiguously to several principals.
* Resolve the same governed agent to the same local agent whether it
  appears as a self-acting WAG subject or an ID-JAG actor. Keep the acting
  relationship and authorization decision separate: a matching agent link
  does not make self-acting and user-delegated authority interchangeable.
* Permit just-in-time agent creation under explicit issuer and tenant
  policy. A name, owner, group, or client match alone cannot merge it with
  an existing principal, reactivate a disabled agent, or attach it to a
  human account. Ownership is not identity equivalence.
* Reject missing, conflicting, ambiguous, or disabled resolution when a
  required link cannot be established. Binding or link replacement cannot
  transfer outstanding grants or continuing authority to a different
  agent. Workload retirement and resource ownership transfer remain
  separate lifecycle decisions.

{{WAG, Section 7}} requires acceptance of previously unseen agent
identifiers under trusted issuers and permits just-in-time projection
into an IdP. WAG should distinguish accepting a new asserted identity
from linking it to an existing governed or local principal and granting
that principal authority. This profile can define the governed mapping
and linking checks once WAG defines the IdP-issued grant composition.

ID-JAG's user-resolution claims do not automatically become WAG claims.
If the composition needs an additional target-local subject identifier
on the wire, its issuer authority, tenant scope, and consistency with
`sub` need to be specified with WAG. ICA's user-anchored continuation
model likewise does not establish independent self-acting authority.

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

**Scope choice.** This revision defers direct WIT-SVID actor input.
SPIFFE OAuth already supplies WIT-SVID presentation and a Client
Attestation PoP JWT; no new upstream proof primitive is needed. A
future revision can define the actor composition locally using those
mechanisms, including exact actor/header matching and capability
signaling.

That composition must choose the output-key relationship explicitly.
{{WIT, Section 9.4}} prohibits using the workload key after credential
expiration. Reusing it for DPoP therefore requires downstream lifetime
limits; a separate DPoP key requires an explicit authorization rule
and must not be described as issuer-endorsed merely by co-presentation.
This revision defines neither alternative for direct WIT-SVID actors.
WIT-SVID remains usable for client authentication with separate actor
evidence, subject to its own key-use restrictions.

**Remaining assurance limitation.** Bearer JWT-SVID and platform JWT
inputs cannot establish an issuer-endorsed holder key by accompanying
a DPoP proof. Deployments needing that assurance must select suitable
bound evidence and its consuming profile. This is not a request to
reopen ATTEST or to add a new proof protocol here.

## Instance Context {#instance-identification}

**Problem.** A workload identity can span several replicas
{{SPIFFE-CONCEPTS}}. An identifier alone establishes neither continuity
nor enrollment or key replacement. Runtime identification does not by
itself make that runtime an authorization principal.

{{INSTANCE}} defines instance identity and continuity requirements;
{{instance-agent-resolution}} consumes that evidence for agent resolution.
Enrollment and key-replacement protocols remain outside both profiles.

**Remaining work for this consuming profile.** Define propagation of
Identification's optional `client_instance` context through the ID-JAG
and access token, including its relationship to the actor, provenance,
receiver scoping, and retain, replace, or omit rules during exchange.
Self-acting context would describe the subject's instance; delegated
context would describe the actor's instance. This revision defines no
downstream instance-context composition.

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

The optional instance-attestation input inherits Identification's
attester trust, receiver scoping, continuity, and privacy requirements.
Its mapping does not establish independent runtime isolation: a holder
of a shared private key can present attestations issued for that key.
Deployments requiring isolation between agents need separate key control
and attester policy. A valid attestation and approved mapping still
require the separate delegation decision in {{delegation-approval}}.

Cross-system disablement and token revocation require the mechanisms
in {{lifecycle-gap}}. Without an applicable signal or online check, an
already issued token can remain usable until expiration. Continuing
access under {{continuing-access}} requires fresh IdP authorization
under ICA's active chain and anchor checks. Chain termination does not
make upstream status immediately visible to a resource or revoke tokens
already issued by a RAS.

Account-linking errors can turn valid identity evidence into access to
another user's account. The issuer, namespace, tenant, and link-change
checks in {{subject-resolution}} apply before authorization; proof of
key possession does not establish account ownership. Removing a link
prevents further issuance through that link but does not itself revoke
an outstanding access token.

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

This document requests registration in the "OAuth URI" registry
established by {{RFC6755}}:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`
* Common Name: ID-JAG Agent Federation grant profile
* Change Controller: IETF
* Specification Document: {{metadata}} of this document.

The profile URI uses ID-JAG's existing authorization server and client
metadata parameter. This document requests no new metadata parameter,
JWT claim, grant type, JWT type, or OAuth token-type URI registration.
Instance claim registrations belong to {{INSTANCE}}.

--- back

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
