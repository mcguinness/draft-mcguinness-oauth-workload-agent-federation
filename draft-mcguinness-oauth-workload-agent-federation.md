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
  JWT-DPOP: I-D.parecki-oauth-jwt-dpop-grant
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

This document profiles agent federation using Workload Authorization
Grant (WAG) for self-acting access and Identity Assertion JWT
Authorization Grant (ID-JAG) for user-delegated access. An identity
provider resolves workload evidence to a governed agent; a resource
authorization server preserves that agent as the subject or actor when
issuing an access token. The document defines subject resolution and
linking requirements for both paths and a complete sender-constrained
ID-JAG flow. The WAG wire profile remains pending the upstream changes
identified in this document.

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

* **Agent identity:** which Registered Agent, the principal governed by
  the IdP, does the external evidence identify?
* **Acting relationship:** is that agent acting for itself or for a
  user, and is the requested delegation authorized?
* **Instance context:** which installation or execution is involved, if
  a separate identification profile establishes that context?

Authenticating an OAuth client, resolving an agent, and proving
possession of a key are distinct operations. None alone establishes
permission to act for a user. An instance identifier likewise does not
confer independent authority on a runtime.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth and Token Exchange terms follow {{RFC6749}} and {{RFC8693}}.
Client Attestation and Client Instance follow {{ATTEST}}.

## Roles

Client:
: Software making OAuth requests for an agent. A client registration can
  serve one or more agents; client authentication does not establish
  which governed agent is acting.

Identity Provider (IdP):
: The OAuth authorization server that resolves external evidence to a
  governed agent and issues the downstream grant.

Resource Authorization Server (RAS):
: The OAuth authorization server that validates the grant, applies local
  policy, and issues an access token for its resources.

API:
: The OAuth resource server that accepts the access token.

One service can implement multiple roles.

## Terms

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
: The IdP's current lifecycle state for an agent, including whether new
  authorization is permitted. Only an active agent is eligible.

# Profile Overview and Conformance {#profile-overview}

## Grant Paths {#paths}

Both grant paths are part of this revision:

| Acting relationship | Grant | Profile status |
|---|---|---|
| Agent acts as itself | WAG; governed agent is the subject | Identity and linking requirements in {{wag-flow}}; wire details pending {{wag-gaps}} |
| Agent acts for a user | ID-JAG; user is the subject and governed agent is the actor | Complete flow in {{delegated-flow}} |

The delegated path has two token requests:

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

The agent presents the user's ID Token, or a supported IdP refresh
token, with workload evidence. The client authenticates independently at
the IdP and RAS. {{identity-example}} illustrates the identity mappings.

## Scope and Conformance {#scope}

Conformance applies to the common requirements and each selected grant
and credential profile:

* **ID-JAG:** The IdP, RAS, and client MUST implement their respective
  requirements in {{delegated-flow}} and {{metadata}}. The API MUST
  implement {{api-processing}}.
  * The common path requires an ID Token subject, platform JWT actor,
    `private_key_jwt` client authentication, and DPoP.
  * IdP refresh-token subjects and the additional inputs in
    {{actor-inputs}} are OPTIONAL.
  * Continuing access is OPTIONAL and uses Identity Continuation
    Assertion (ICA) for eligible receiving-service or assigned-task
    deployments under {{continuing-access}}.
* **WAG:** {{wag-flow}} defines the federation requirements. Complete
  protocol conformance remains pending the upstream contract in
  {{wag-gaps}}. Support for one grant does not advertise support for the
  other.

Implementations MAY support other flows, but MUST NOT use them as a
fallback after validation or authorization fails for this profile.
Multi-agent delegation chains, instance propagation, and
enrollment/key-replacement protocols are outside this revision.

The optional instance input depends on the pinned editor's copy of
{{INSTANCE}}, which has not been submitted to the Datatracker.
{{upstream-gaps}} records the remaining dependencies and coordination.

## Requirements Added by This Profile {#profile-requirements}

Common requirements are in {{identity}} and {{authorization}}; WAG
requirements are in {{wag-flow}}. This non-normative index locates the
additional ID-JAG requirements. The cited sections define the rules;
selected base specifications also apply.

| Area | Addition or narrowing | Defined in |
|---|---|---|
| Subject resolution | One target-specific user; authorized links; conflict rejection | {{subject-resolution}} |
| Instance ATTEST | Validated instance evidence and approved agent/client association | {{instance-agent-resolution}} |
| Root exchange | ID Token or supported IdP refresh-token subject; direct JWT actor | {{exchange-request}} |
| Common capabilities | Platform JWT input, `private_key_jwt`, RS256 signatures, and ES256 DPoP | {{flow-configuration}} |
| Platform JWT time checks | Authoritative issuance time for configured age and original-lifetime limits | {{platform-jwt-input}} |
| Chain scope | One user-to-agent relationship; no pre-existing actor chain | {{actor-inputs}} |
| Explicit authority | One resource and non-empty scope in the request and grant | {{exchange-request}} |
| Actor mapping | Governed `act.sub` and IdP `act.iss` | {{actor-construction}} |
| Proof | DPoP at both token endpoints; same key in grant and access token | {{issuance-proof}} and {{redemption}} |
| Root grant lifetime | Bounded by input expiry; five minutes recommended | {{grant-issuance}} |
| Redemption | `jwt-dpop`; matching resource; JWT access token preserving actor and key | {{redemption}} |
| Continuing access | Eligible ICA source; original actor and binding; no RAS refresh tokens | {{continuing-access}} |
| API | Configured applicability independent of token contents; required actor and proof validation, with resource errors | {{api-processing}} |
| Errors | `invalid_grant` for invalid credentials; `actor_unauthorized` for delegation denial | {{errors}} |
| Discovery | Grant-profile URI at RAS and client; configured IdP issuance and optional inputs | {{metadata}} |

Base ID-JAG or generic Token Exchange support does not imply support for
these requirements.

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
approved Federation Binding. Metadata can locate an already approved key
source; it does not authorize that source to assert every agent.

The IdP MUST authorize binding creation and changes, including imports
from platform registries. Operators SHOULD authenticate and audit the
administrative source. Binding changes do not alter the validation rules
of the credential itself.

## Selecting the External Identity

| Evidence | Identity used for resolution | Qualification |
|---|---|---|
| Platform JWT | Approved issuer and exact subject, with configured additional selectors | Workload evidence; not automatically OAuth client authentication |
| Client Attestation, agent has its own client | Attester identified by the trusted verification key; client `sub` | Client-to-agent mapping is explicit |
| Instance Client Attestation | Validated (`iss`, `client_instance_id`), associated with the authenticated client `sub` | Optional input using {{INSTANCE}} and {{instance-agent-resolution}} |
| SPIFFE JWT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | OAuth client association follows SPIFFE OAuth |
| SPIFFE X.509-SVID | Approved trust domain and exact SPIFFE ID in the URI SAN | Client authentication only in this revision; separate actor evidence required |
| SPIFFE WIT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Client authentication only in this revision; separate actor evidence required |

After validating actor evidence, the IdP MUST resolve exactly one active
Registered Agent through an enabled binding. It MUST reject missing,
ambiguous, or disabled mappings. Similar names, unqualified identifiers,
or a shared signing key MUST NOT establish identity equivalence.

A client registration or Client ID Metadata Document {{CIMD}} can
identify an OAuth client. It does not by itself distinguish the agents
behind a shared client. Even when the credential specification permits a
client-identifier association or prefix match, the Federation Binding
MUST resolve the exact workload identity selected as actor evidence to
one Registered Agent.

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
issuance, the Target Tenant for the requested RAS and resource. The RAS
MUST interpret an agent identifier in its asserted issuer or namespace
context. It MUST NOT key agent authorization on bare `sub`.

Trusted key lookup MUST retain the issuer or trust-domain association;
`kid` alone or a union of unrelated issuers' keys cannot establish the
asserting authority. Separate signing keys are RECOMMENDED for
independently administered authorities. Shared keys do not remove
issuer-specific authorization checks.

Restarting an execution, replacing a replica, or rotating a key does not
by itself create a new authorization principal. Credential renewal still
follows the credential's own validation and proof rules.

## Subject Resolution and Linking {#subject-resolution}

For ID-JAG, subject resolution identifies the user; linking associates
that external identity with a local account. Neither grants delegation.
WAG subject resolution follows {{wag-subject-resolution}}. No new
identifier claim or linking protocol is defined.

### Resolution at the IdP {#idp-subject-resolution}

For a root exchange, the IdP MUST validate the subject credential under
{{exchange-request}} and:

1. **User identity:** Resolve exactly one user from the ID Token's
   issuer-qualified subject and applicable tenant context, or from the
   validated refresh token's authorization context. The actor credential
   and authenticated client MUST NOT substitute for that user identity.
2. **Target namespace:** Select the subject namespace associated with
   the target RAS's SSO relationship under {{ID-JAG, Section 5}}. A
   client-specific pairwise subject MUST NOT be copied into another
   relying party's namespace without resolving the same user in that
   namespace.
3. **Output identifiers:** Issue `sub` and any additional subject
   identifiers for that same user under {{ID-JAG, Sections 3.1 and 6}}.
   The IdP MUST derive `aud_sub`, `aud_tenant`, or `sub_id`, when used,
   from an authoritative association for the target; a client-supplied
   account hint does not establish that association.

For ICA continuation, the IdP resolves the user from the validated chain
and applies the same target-namespace and output-identifier
requirements.

### Resolution at the RAS {#ras-subject-resolution}

After validating the ID-JAG and its client and proof bindings, the RAS
MUST resolve exactly one local user in the authorized Target Tenant
before issuing an access token. Its configured resolution rules MUST:

* **Issuer subject:** Qualify `sub` by the validated IdP issuer and the
  tenant context required by {{ID-JAG, Section 6}}. The RAS MUST NOT
  assume that an IdP tenant identifier is its own local tenant
  identifier.
* **Local subject:** Use `aud_sub` only when the trusted IdP is
  authorized to assert local account identifiers for the selected Target
  Tenant. An asserted local identifier MUST NOT override a conflicting
  approved link.
* **Alternate namespace:** Use `sub_id` only under ID-JAG's
  format-specific and issuer-association rules ({{ID-JAG, Sections 3.2.2
  and 9.5}}). A SAML NameID retains its issuer, format, and applicable
  qualifiers; its value alone is not a cross-namespace identifier.
* **Conflicts:** Reject conflicting identifiers used for resolution or
  multiple local matches. The RAS MUST NOT retry with a weaker selector
  or another tenant after such a conflict.

The access token's `sub` identifies that resolved user in the RAS's
access-token namespace. The RAS resolves `act.iss` and `act.sub`
separately under {{agent-correlation}} and MUST NOT link the agent to
the user's account merely because it acts for that user.

### Account Links and Their Lifecycle {#subject-linking}

The RAS MAY use provisioned links, account linking, or just-in-time
creation. It MUST enforce the following requirements:

* **Link authority:** Creating or changing a link requires either:
  * An authenticated administrative or provisioning authority authorized
    for the account; or
  * A user flow verifying control of both identities.
* **Attribute matching:** Email, username, or display-name attributes
  alone MUST NOT establish a link. This narrows ID-JAG's claim-based
  resolution; configured, issuer-qualified SAML NameIDs remain usable,
  including email-format NameIDs, under {{ras-subject-resolution}}.
* **Account creation:** Just-in-time creation requires issuer and Target
  Tenant authorization. It MUST NOT silently merge a conflicting account
  or reactivate a disabled one. Memberships, entitlements, and
  delegation require separate authorization.
* **Uniqueness:** Each qualified external identity resolves to at most
  one account per Target Tenant. Multiple identities MAY link to one
  account when each link is independently authorized.
* **Link changes:** Removal, disablement, or reassignment MUST NOT
  transfer an outstanding grant, delegation approval, or ICA authority
  to another user. If continuity with the authorized user cannot be
  established, further use MUST be rejected.

The IdP and RAS MUST reject issuance when the user or a required link is
disabled, or resolution is missing, ambiguous, or conflicting
({{errors}}). Operators SHOULD audit link creation, changes, and
removal.

# Evidence and Client Authentication {#inputs}

The IdP MUST validate a credential according to its selected type and
trusted configuration before using it for identity resolution. A generic
JWT token-type URI or a caller-supplied claim MUST NOT select a weaker
validation path. The credential's role in a token request is determined
by the consuming authorization profile.

The IdP MUST distinguish:

* **Client authentication:** evidence authenticating the OAuth client.
* **Agent resolution:** the approved association from validated external
  evidence to the Registered Agent.
* **Key possession:** proof that the presenter controls a particular
  key, with the binding semantics specified by the proof mechanism.

The IdP MUST NOT substitute one role for another. Credential and proof
validation MUST refer to the same request and applicable principal.
DPoP with bearer evidence does not establish issuer endorsement of the
proof key; {{credential-requirements}} defines the assurance limits.

Unrecognized request parameters and JWT claims follow {{RFC6749, Section
3.2}} and {{RFC7519, Section 4}}. An unconfigured claim MUST NOT select
an identity model or establish a Federation Binding.

## Platform-Issued JWT {#platform-jwt-input}

For an imported workload, the Federation Binding MUST specify an exact
issuer and `sub`. It MAY require additional top-level string claims,
such as tenant or platform agent identifiers. Every configured selector
MUST be present, have the configured type, and match exactly. These
selectors are deployment configuration, not new JWT claims registered by
this document.

The IdP MUST validate the JWT under {{RFC7519}} and {{RFC8725}},
including signature, credential class, accepted audience, and time
claims. Its policy MUST specify:

* The approved issuer, key source, and signature algorithms.
* Audiences authorizing presentation to this IdP for the selected
  workload-evidence purpose.
* Required expiration and any maximum age, issuance-to-expiration
  lifetime, or remaining-validity limits, accounting for the platform's
  issuance and caching behavior.
* Rules distinguishing accepted workload credentials from user,
  management-API, or other tokens issued by the same authority.

Classification can use an explicit type, a dedicated issuer, or an
accepted audience combined with exact workload selectors. Generic
`typ=JWT` alone does not distinguish credential classes.

When policy limits age or issuance-to-expiration lifetime, the IdP MUST:

* Obtain a NumericDate `iat` or another authoritative issuance time
  defined by the configured credential class.
* Reject evidence if the limit cannot be evaluated.

Expiration alone establishes remaining validity. An input without `iat`
is usable when policy needs no issuance-time check or defines another
authoritative source for that time.

A platform JWT accepted as workload evidence MUST NOT be treated as
OAuth client authentication unless it independently satisfies a
configured client authentication specification. A flow requiring client
authentication MUST validate that authentication separately and verify
its association with the permitted client.

The JWT is presented as `actor_token` under {{exchange-request}}.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL direct actor input. The client MUST
present the identical compact JWT in `actor_token` and the
`OAuth-Client-Attestation` header and authenticate using the configured
ATTEST method. The IdP MUST validate the attestation and proof before
resolving the agent. {{actor-inputs}} defines the proof/key
relationship.

For an agent with its own client, the attester is the configured
authority associated with the trusted key that verified the attestation.
The IdP MUST select that authority unambiguously and resolve the pair of
its identifier and the validated client `sub`. An `iss`, when present,
MUST match that authority. It is not required in this mode.

For instance-based agent resolution, including agents sharing an OAuth
client, the IdP and client MUST use {{instance-agent-resolution}}. The
client and IdP MUST select own-client or instance-based resolution
through trusted client configuration before accepting requests. Claims
MUST NOT switch modes, and failed instance validation MUST NOT fall back
to own-client resolution.

Both inputs produce the governed actor under {{actor-construction}}. The
own-client input uses base ATTEST without requiring Identification.

### Instance-to-Agent Resolution {#instance-agent-resolution}

The `instance_attestation` input uses {{INSTANCE}} to identify an
enrolled installation or execution unit. Identification supplies
instance evidence; this profile supplies the approved agent mapping
and the separate authorization decision. The IdP MUST:

1. **Validate:** Act as a Receiver under Identification and apply its
   Receiver validation and instance-policy requirements, using the
   configured attester trust, client association, receiver scope,
   granularity, continuity evidence, and freshness limits. Validate the
   ATTEST proof and the output-key relationship in {{actor-inputs}}
   against the same attestation in the request.
2. **Resolve:** Use the validated (`iss`, `client_instance_id`) pair as
   the external instance identity. Match it exactly through an enabled
   Federation Binding to one active Registered Agent, checking the
   authenticated client `sub`, Source Tenant, and configured receiver
   scope. A shared OAuth client or matching proof key MUST NOT establish
   that binding.
3. **Check uniqueness:** Reject a missing or ambiguous agent mapping.
   * Several instances MAY map to one agent.
   * An instance hosting several agents needs another supported input
     that selects one agent unambiguously.
4. **Authorize:** Apply {{authorization}} and {{delegation-approval}} to
   the resolved agent. Set `act` from the governed identity under
   {{actor-construction}}, not from the instance identifier.

Enrollment, continuity evidence, renewal, and key changes follow
Identification. For a new instance identifier, the IdP MUST require an
approved binding; it MUST NOT inherit one from an earlier key, shared
client, or claimed predecessor. The binding MAY identify the same agent
but does not transfer an existing grant to a replacement key.

Identification claim and instance-policy failures use its
`invalid_client_attestation` error. After successful instance
validation, missing, disabled, or ambiguous agent bindings and denied
delegation use `actor_unauthorized` under {{errors}}. The distinction
does not permit disclosure of instance or agent status in error details.

Downstream instance-context propagation remains outside this input
({{instance-identification}}). Actor construction follows
{{actor-construction}}; `client_instance_id` is not the governed actor.

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

Direct actor presentation follows {{actor-inputs}}, selected through
trusted configuration under {{metadata}}. Its bearer-evidence limitation
is specified in {{credential-requirements}}.

## SPIFFE X.509-SVID {#spiffe-input}

X.509-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.2}}.
The IdP MUST validate the certificate with the configured trust-domain
anchors and associate the authenticated SPIFFE ID with the OAuth client.
Client identity and TLS proof checks remain those of SPIFFE OAuth.

X.509-SVID MAY authenticate the OAuth client in a delegated request that
also supplies a supported JWT actor credential. Using the TLS identity
alone as actor evidence remains outside this revision; {{x509-gap}}
records that separate composition gap.

## SPIFFE WIT-SVID {#wit-input}

WIT-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.3}} and
{{WIT}}. The IdP MUST validate the credential and required proof, use
trust anchors authorized for the trust domain in `sub`, and associate
the authenticated identity with the OAuth client.

The WIT's confirmation key and the authentication proof retain their
specified roles. DPoP alone MUST NOT substitute for a required WIT or
attestation proof. WIT-SVID MAY authenticate the OAuth client when the
request also supplies a supported actor credential. Direct WIT-SVID
actor presentation is outside this revision as a scope choice described
in {{credential-gap}}, not because SPIFFE OAuth lacks a proof mechanism.

## Credential Use Requirements {#credential-requirements}

For each accepted credential input, the IdP MUST configure its role,
required proof mechanism, and the assurance required for an output key.
The IdP MUST validate each required proof; support for one proof mode
MUST NOT imply support for another.

For bearer JWT-SVID and platform JWT inputs, the IdP MUST NOT infer
platform authorization of a DPoP key from co-presentation or from a
first-use credential-to-key cache. A deployment requiring issuer-
endorsed key possession MUST use evidence that cryptographically binds
the key. A deployment accepting bearer evidence MUST account for theft
of that evidence in its issuance policy.

A reused credential MUST be validated with the current request's
required proof and current binding policy. Credential reuse MUST NOT
bypass proof replay checks or implicitly enroll a replacement key. The
IdP MUST NOT describe a platform identity shared by replicas as unique
instance evidence. Additional instance assurance requires the evidence
and consuming profile discussed in {{instance-identification}}.

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
2. Resolve an active agent through a current, enabled Federation Binding
   and verify any required client association.
3. Resolve the RAS, resource, and Target Tenant through trusted
   configuration and check the requested acting relationship. For
   delegated access, resolve the user under {{idp-subject-resolution}}.
4. Apply current assignments and scope policy. Issued authority MUST NOT
   exceed the agent's authorized authority and, for delegated access,
   the user's authority and applicable delegation.
5. Supply the resolved principal and approved authority to the selected
   grant mechanism without substituting the external identifier for the
   governed identity.

For requested scopes, the IdP:

* MAY grant an authorized, non-empty subset if policy permits partial
  approval.
* MUST return `invalid_scope` if no scope can be granted, or if policy
  requires full approval and the request exceeds it.
* MUST reflect any reduction in the grant and response. ID-JAG follows
  {{grant-issuance}}; WAG's wire contract remains in {{wag-gaps}}.

Scope reduction does not waive target or delegation checks.

If the selected mechanism cannot represent the required identity or
binding, the IdP MUST NOT issue a misleading token by dropping the
actor, changing the credential class, or silently weakening the proof
requirement. This includes attempts to substitute self-acting access for
a denied delegated request.

ID-JAG authentication and proof failures follow {{errors}}.

## Delegation Approval {#delegation-approval}

Before constructing `act`, the IdP MUST authorize the resolved agent to
act for the user, client, tenant, RAS, resource, and requested
authority. The IdP MUST reject missing, revoked, expired, or
insufficient delegation. Valid credentials, user sign-in, or a shared
client MUST NOT imply approval or permit one agent to reuse another
agent's approval.

Approval requires an authenticated party authorized to approve and a
means to withdraw approval. Record formats and policy engines are
implementation choices. Pre-existing actor chains are rejected under
{{actor-inputs}}.

## Canonical Agent Attribution {#agent-correlation}

The intended governed identity is the pair of IdP namespace and
Registered Agent identifier. In self-acting access it identifies the
subject; in user-delegated access it identifies the agent actor. The
delegated output mapping is defined in {{actor-construction}}. The
self-acting contract is specified in {{wag-flow}}, with grant
coordination tracked in {{wag-gaps}}.

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
describe. User memberships MUST NOT be interpreted as the agent actor's
memberships, or agent memberships as the user's. Where SCIM `externalId`
{{RFC7643}} is used, its provisioning association MUST retain the issuer
and tenant context.

# Self-Acting WAG Profile {#wag-flow}

WAG carries the governed agent as subject for self-acting access. This
section defines its federation requirements. The complete IdP-issued,
sender-constrained wire profile remains pending {{wag-gaps}}; the WAG
name is retained.

## Subject Resolution and Linking {#wag-subject-resolution}

The IdP and RAS MUST apply {{identity}} and {{agent-correlation}} and
preserve these identity relationships at their respective stages:

| Stage | Required identity relationship |
|---|---|
| Workload evidence to IdP | Validated external identity resolves through an approved Federation Binding to one active Registered Agent |
| IdP-issued WAG | Issuer-qualified `sub` identifies that governed agent; no `act` is needed solely to identify its executing instance |
| WAG to local authorization | The RAS resolves the governed identity to one local agent principal in the authorized Target Tenant |
| Access token to API | The token identifies the same agent in the RAS's subject namespace; authorization uses that agent's authority |

The RAS MUST apply these linking requirements:

* **Identity:** Scope lookup to the trusted grant issuer, its subject
  namespace, and the established tenant relationship. An external
  workload subject, OAuth client identifier, or instance identifier is
  not automatically the governed or local agent identifier.
* **Link authority:** Authorize creation and changes of local agent
  links for that issuer and Target Tenant. Several approved workload
  bindings can identify one governed agent, but a selected binding or
  local link cannot resolve ambiguously to several principals.
* **Consistent resolution:** Resolve the same governed agent to the same
  local agent whether it appears as a self-acting WAG subject or an
  ID-JAG actor. Keep the acting relationship and authorization decision
  separate: a matching agent link does not make self-acting and
  user-delegated authority interchangeable.
* **Creation:** If just-in-time agent creation is supported, require
  explicit issuer and tenant policy authorizing it. A name, owner,
  group, or client match alone MUST NOT merge it with an existing
  principal, reactivate a disabled agent, or attach it to a human
  account. Ownership is not identity equivalence.
* **Failure and lifecycle:** Reject missing, conflicting, ambiguous, or
  disabled resolution when a required link cannot be established.
  Binding or link replacement MUST NOT transfer outstanding grants or
  continuing authority to a different agent. Workload retirement and
  resource ownership transfer remain separate lifecycle decisions.

ID-JAG's user-resolution claims do not automatically become WAG claims.
If the composition needs an additional target-local subject identifier
on the wire, its issuer authority, tenant scope, and consistency with
`sub` need to be specified with WAG. ICA's user-anchored continuation
model likewise does not establish independent self-acting authority.

# Delegated ID-JAG Flow {#delegated-flow}

This section profiles ID-JAG issuance and redemption using the actor
extension point in {{ID-JAG, Section 9.7}}.

Both token endpoints retain {{RFC6749, Section 5.1}}'s JSON response
encoding and cache-control requirements. Error responses follow
{{errors}}.

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
selection even if `actor_token` is omitted. The RAS MUST enforce it even
if `act` or `cnf` is omitted from a presented ID-JAG. Metadata
advertisement alone establishes neither trust nor authorization.

The client MUST be registered at both authorization servers. The client
and servers MUST support `private_key_jwt` under {{RFC7523, Section
2.2}}. Other configured methods MAY be used. Client identifiers and keys
MAY differ between servers.

Client-authentication audiences follow the selected method:

* For `private_key_jwt`, the client MUST use the receiving token
  endpoint URL as the assertion audience. This selects an RFC 7523
  audience option.
* JWT-SVID uses the IdP issuer as its sole audience
  ({{jwt-svid-input}}).
* Client Attestation PoP JWTs use ATTEST's audience rules.

Each role MUST support the algorithms for its operations:

* `RS256` for signing or validating platform JWTs, client assertions,
  ID-JAGs, and JWT access tokens.
* `ES256` for DPoP.

Other mutually supported algorithms MAY be selected through trusted
configuration and metadata; algorithm support does not establish key
trust.

The client and RAS MUST support the DPoP-bound JWT grant {{JWT-DPOP}}
for both root and onward ID-JAG redemption under {{redemption}}.

## Root Token Exchange {#exchange-request}

### Request {#root-request}

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

### Client Authentication and Proof {#issuance-proof}

The IdP MUST authenticate the client under {{flow-configuration}}.
It MUST validate the DPoP proof under {{RFC9449}} and {{ID-JAG, Section
9.8.1.1}} and reject a missing or invalid proof. Nonce challenges and
fresh-proof retries follow DPoP and {{errors}}.

### Subject Token Validation {#subject-token-validation}

The IdP MUST support ID Token subjects and MAY additionally support its
own refresh tokens. Refresh-token support MUST be agreed in client
configuration. The IdP MUST validate the selected subject token under
{{ID-JAG, Section 4.3.3}}:

* **ID Token:** Validate signature, issuer, expiration, audience, and
  applicable client binding. The audience MUST identify the
  authenticated IdP client.
* **Refresh token:** Apply standard `refresh_token` grant validation:
  * Check issuance by this IdP, authenticated-client binding, validity,
    revocation status, and applicable proof requirements.
  * Require requested scopes and audience to remain within the token's
    retained authorization context.

Both inputs require current actor evidence and delegation approval under
{{delegation-approval}}. A refresh token replaces the ID Token input;
the output remains an ID-JAG.

### Actor Token Validation {#actor-inputs}

The labels below identify configured input choices, not wire parameters
or registered identifiers. All use
`actor_token_type=urn:ietf:params:oauth:token-type:jwt`.

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

The IdP MUST apply the selected input's requirements:

* **Platform JWT:** Require `iss`, `sub`, `aud`, and `exp`.
  * Match issuer and subject to the approved binding and audience to
    this IdP's workload-evidence purpose.
  * If `cnf` is present, enforce its defined proof mechanism. Reject an
    unsupported binding; it MUST NOT receive bearer treatment.
* **Client or instance attestation:** Apply ATTEST authentication and
  mode-specific proof checks to the exact JWT in `actor_token`.
  * Require the issuance DPoP key to match the attestation's
    confirmation key. This narrows normal ATTEST mode, which permits a
    separate DPoP key.
  * Combined mode uses its existing DPoP proof. Base ATTEST errors
    remain applicable.
* **JWT-SVID:** Authorize the credential/client/agent association and
  output key under {{authorization}} and {{credential-requirements}}.

To preserve the single user-to-agent relationship, the IdP MUST reject:

* An `actor_token` or ID Token subject containing `act`.
* A refresh-token subject whose retained authorization context contains
  an actor chain.

### Actor Resolution and Construction {#actor-construction}

After credential validation, the IdP MUST resolve exactly one active
Registered Agent through {{identity}} and authorize its relationship to
the user, authenticated client, target, and approved authority.
The issued ID-JAG MUST contain a single `act` object with:

* `sub`: the Registered Agent identifier resolved by the binding.
* `iss`: this IdP's issuer identifier, which is the namespace of that
  Registered Agent identifier.

The IdP MUST derive these values from an approved mapping, including
when the external and governed identifiers have the same value.

The object MUST conform to {{ACTOR-PROFILE, Section 3.4}}, including its
`sub_profile` recommendation and unclassified-actor rules. Entity
Profiles {{ENTITY-PROFILES}} remains a transitive dependency.

This profile imports Actor Profile's actor-object and resource rules.
The mapping above replaces its Section 6.3 credential-to-actor copying
algorithm. Other Actor Profile paths require independent support.

### Grant Issuance {#grant-issuance}

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
the agent identifier remains unique within `act.iss`. The IdP MUST NOT
issue a grant if it cannot determine an unambiguous user, actor,
downstream client, or tenant relationship.

The root grant lifetime SHOULD be no more than five minutes. Its
expiration MUST NOT exceed any of:

* The expiration computed from the IdP's finite configured lifetime
  limit and the grant's issuance time.
* The actor credential's expiration.
* The subject credential's expiration, when known.

These limits apply to the grant, not the input credential or downstream
access token.

### Successful Response {#exchange-response}

The response follows {{ID-JAG, Section 4.3.4}} and {{RFC8693}}:

* `access_token` carries the ID-JAG.
* `issued_token_type` is `urn:ietf:params:oauth:token-type:id-jag`.
* `token_type` is `N_A`.
* `expires_in` and `scope` retain their base-protocol requirements.

The client MUST retain the DPoP key for redemption. Grant inspection
retains ID-JAG's optional or recommended status.

## ID-JAG Redemption {#redemption}

### Request {#redemption-request}

The client sends an authenticated, form-encoded HTTPS POST to the
RAS token endpoint with:

* `grant_type=urn:ietf:params:oauth:grant-type:jwt-dpop`.
* `assertion` containing the ID-JAG.
* One `resource` equal to the resource authorized by the grant.
* A fresh DPoP proof made with the same key used at issuance.

Root and ICA onward grants use {{JWT-DPOP}} and {{ID-JAG, Section
9.8.1.2}}. The RAS MUST reject a profile ID-JAG presented using
`jwt-bearer`; the client MUST NOT retry with that grant type after a
failure.

A redemption `scope` MAY request a subset. If omitted, the grant's
scopes are the requested upper bound.

### Grant Validation {#redemption-validation}

The RAS MUST perform ID-JAG validation and additionally:

1. **Actor:** Require a single `act` object under Actor Profile's rules:
   * Require non-empty `iss` and `sub`, with no nested `act`.
   * Require `act.iss` to equal the ID-JAG issuer and configured trust
     to authorize assertion of that namespace.
2. **Proof and client:** Require `cnf.jkt` and a valid DPoP proof
   matching that key. Independently authenticate the client identified
   by `client_id`.
3. **Authority:** Require the grant's resource and scope constraints.
   Validate the requested resource and any scope reduction, and apply
   ID-JAG's processing for any `authorization_details` present.
4. **Local authorization:** Resolve the user under
   {{ras-subject-resolution}} and the governed actor under
   {{agent-correlation}}. Apply current RAS policy to the user/actor
   relationship, client, tenant, and resource. A valid grant sets an
   authority ceiling; it does not require issuance.

### Access Token Issuance and Response {#access-token-response}

After successful validation and authorization, the RAS MUST issue a JWT
access token under {{RFC9068}} with:

* The RAS as issuer, the resolved user as subject, and the resource as
  audience.
* The validated `act` unchanged and top-level `cnf.jkt` bound to the
  same DPoP key.
* A non-empty authorized `scope`; otherwise, return `invalid_scope`.
* All applicable constraints preserved in the token or enforced resource
  policy.

The RAS MUST NOT broaden authority, substitute its authenticated client
for the actor, or return a bearer token. Its successful response MUST
use `token_type=DPoP` and follow {{ID-JAG, Section 4.4.2}} and RFC 6749.
The client MUST reject a response reporting a different token type.

An unexpired ID-JAG remains reusable under ID-JAG. Each redemption
requires fresh proof validation and current RAS policy. Grant expiry
alone does not revoke an issued token; {{continuing-access}} defines
subsequent exchanges.

## Token Endpoint Error Responses {#errors}

Token endpoint errors MUST follow {{RFC6749, Section 5.2}}, including
its HTTP status and authentication-challenge rules, with the codes
below. Servers MUST validate client authentication, credentials, and
proofs before authorization. Error details SHOULD NOT reveal user or
agent existence.

| Failure | Error |
|---|---|
| Unsupported `grant_type` | `unsupported_grant_type` |
| Authenticated client not permitted to use the grant type | `unauthorized_client` |
| Missing required parameter, unsupported token type/combination, ambiguous input classification, or malformed request | `invalid_request` |
| Invalid client authentication | Its configured method's error, normally `invalid_client` |
| Instance-identification claim or instance-policy failure | `invalid_client_attestation` under Identification |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Valid identity evidence but absent, disabled, or ambiguous agent binding, or unauthorized delegation | `actor_unauthorized`, as defined by Actor Profile |
| Unsupported or unauthorized target | `invalid_target` under RFC 8693 and the applicable resource rules |
| Invalid scope | `invalid_scope` |
| Missing or invalid DPoP proof at root issuance | `invalid_dpop_proof` under RFC 9449 |
| Missing or invalid redemption proof, mismatch with grant `cnf.jkt`, or profile ID-JAG presented using `jwt-bearer` | `invalid_grant` under the selected bound-grant processing |
| Otherwise valid proof requiring a nonce challenge | `use_dpop_nonce` and the required RFC 9449 response headers |

Actor-credential failures use `invalid_grant` instead of the default
`invalid_request` described by RFC 8693; this narrowing is intentional.
When the same JWT also performs client authentication, its shared
validation failure uses the authentication method's error. ATTEST
retains its claim, proof, freshness, and challenge errors. No failure
permits issuance after dropping the actor or its proof binding.

At redemption, the nonce challenge above takes precedence over
{{JWT-DPOP}}'s generic `invalid_grant` validation error when the proof
otherwise validates. This profile explicitly selects RFC 9449 nonce
recovery. Continuation exchanges and CAI assertion issuance retain ICA's
error and precedence rules. {{bound-grant-coordination}} records the
upstream alignment needed.

## Identity Mapping Example {#identity-example}

This non-normative example shows selected claims, not complete tokens.
The IdP at `https://idp.example/` validates:

* A platform JWT from `https://platform.example/` with
  `sub=workload-7`. An approved Federation Binding resolves it to
  Registered Agent `agent-42`.
* Alice's ID Token with `sub=alice-app` and `aud=agent-app`. The IdP
  resolves Alice's subject for the target RAS to `alice-ras` and maps
  client `agent-app` to that RAS's client `ras-agent-app`.

After delegation approval, the IdP issues the ID-JAG below. The RAS
resolves `(https://idp.example/, alice-ras)` to local user `user-108`
and independently authorizes the governed agent. Successful redemption
produces the access-token claims shown. `JKT_K` denotes the thumbprint
of the client's DPoP key K; tenant associations are preconfigured.

| Claim | ID-JAG | Access token |
|---|---|---|
| `iss` | `https://idp.example/` | `https://ras.example/` |
| `sub` | `alice-ras` | `user-108` |
| `act.iss` | `https://idp.example/` | `https://idp.example/` |
| `act.sub` | `agent-42` | `agent-42` |
| `client_id` | `ras-agent-app` | `ras-agent-app` |
| `aud` | `https://ras.example/` | `https://api.example/` |
| `resource` | `https://api.example/` | Represented by `aud` |
| `scope` | `files.read` | `files.read` |
| `cnf.jkt` | `JKT_K` | `JKT_K` |

Agent resolution replaces the external identifier with the governed
IdP identifier. Alice's subject changes namespace at redemption; the
governed actor and DPoP key remain unchanged.

## Continuing Access {#continuing-access}

This document distinguishes three operations:

* **Redemption:** Presenting an unexpired ID-JAG again under
  {{redemption}} obtains another access token within that grant's
  authority.
* **New root exchange:** Presenting a valid ID Token or supported IdP
  refresh token with current actor evidence under {{exchange-request}}
  obtains a new root grant and repeats all root authorization checks.
* **Continuation:** Using an established RAS authorization without
  presenting the root subject credential MUST use {{ICA}}. A trusted
  Continuation Assertion Issuer (CAI) attests to that authorization;
  the agent exchanges the assertion at the IdP for an onward ID-JAG.

The RAS MUST NOT issue refresh tokens on root or onward redemption,
narrowing ID-JAG's SHOULD NOT. IdP refresh tokens remain optional root
subject credentials under {{exchange-request}}.

### Eligible Continuation Sources {#continuation-sources}

This composition requires the root Registered Agent to have an eligible
role in the accepting RAS's domain. Before issuing an assertion, the
CAI MUST associate the authenticated agent with that authorization under
{{ICA, Sections 5.3 and 5.4}} through either:

* A received request or forwarded context assigned to the agent. For
  ICA's access-token input, the token MUST be valid for a protected
  resource the authenticated agent operates.
* An active, durable RAS task authorization designating that agent.
  Each authenticated run MUST derive its context from that task state,
  not from a requester-supplied continuation handle.

Task setup and delivery of task or forwarded context remain
deployment-specific under ICA. Deployments MUST configure that mechanism
and the CAI's authoritative association with the same governed agent
before enabling this composition. Client registration alone or a token
obtained to call another service does not establish eligibility.
General calling-agent continuation remains an upstream gap in
{{continuation-gap}}.

### Establishing Continuation

The root exchange retains this profile's direct actor evidence and
delegation checks. To establish continuation, the IdP MUST also:

* Apply ICA's chain-establishment and lifecycle-anchor requirements. An
  eligible user session or, where supported, the IdP refresh token's
  OAuth grant anchors the chain; credential expiry alone does not define
  the chain lifetime.
* Require the authenticated client's configured canonical actor identity
  under {{ICA, Section 5.5.2}} to equal the governed `(iss, sub)` pair
  resolved under {{actor-construction}}. A shared client with no
  unambiguous mapping to that agent cannot establish this composition.
* Bind the chain authorization to the Federation Binding used at the
  root, including its external identity, authority, Source Tenant, and
  permitted client association. This association MUST remain fixed for
  the chain's lifetime; its representation is implementation-specific.

If continuation cannot be established, an otherwise valid root exchange
can issue an ordinary ID-JAG without a continuation handle, following
{{ICA, Section 5.1}}. The client MUST NOT infer continuation authority
from successful root issuance. A continuation-aware RAS MUST implement
ICA's acceptance and handle-binding requirements.

### Continuing as the Governed Agent

The client, CAI, IdP, and RAS MUST implement their applicable ICA roles,
including assertion issuance, validation, replay handling, trust,
errors, and recovery. In particular:

* **Request:** The client MUST use ICA as `subject_token` and omit
  `actor_token` and `actor_token_type`. ICA's client authentication and
  assertion matching replace this profile's root actor-input processing.
* **Actor:** The IdP MUST require the root's Registered Agent as current
  actor and recheck agent, delegation, and ICA chain authorization.
* **Binding:** The IdP MUST check the chain's original Federation
  Binding, including its client association:
  * It MUST still be enabled and resolve the recorded external identity
    to the root's Registered Agent in the same Source Tenant.
  * Removal, disablement, or reassignment MUST end the chain once the
    change is applied under {{status-changes}}.
  * Another binding for the same agent MUST NOT sustain or revive that
    chain. Using another binding requires a new root exchange.
* **Subject:** The IdP MUST resolve the chain's original user for each
  target under {{subject-resolution}}. A continuation handle or prior
  target's local account identifier MUST NOT substitute for the new
  target's subject resolution or authorize a new account link.
* **Authority:** The request MUST identify one resource and a non-empty
  scope. The IdP MUST construct the onward grant under {{ICA, Section
  5.5.5}}:
  * Retain this profile's actor, resource, scope, and downstream client
    rules.
  * Apply ICA's lifetime and key-binding rules, not the root credential
    limits in {{grant-issuance}}.
* **Redemption:** The client and RAS MUST apply {{redemption}}, using
  the same DPoP-bound JWT grant as at the root. The API MUST apply
  {{api-processing}}.

ICA governs chain lifetime and termination; this document defines no
separate continuation deadline or renewal protocol. Ending a chain
prevents further continuation but does not itself revoke outstanding
grants or access tokens; {{status-changes}} still applies.

# Resource Server Processing {#api-processing}

The API MUST determine which request paths require the delegated ID-JAG
profile from trusted resource configuration, independently of the
presented token's claims. An absent or malformed `act` MUST NOT select
non-delegated processing on those paths. Other configured resource paths
can accept other token profiles.

The client presents the access token using the DPoP authorization scheme
and a fresh resource-request proof under {{RFC9449}}, including the
access-token hash. On a path requiring the delegated ID-JAG profile,
the API MUST:

1. **Token:** Validate the JWT under {{RFC9068}} and require non-empty
   `scope` and `cnf.jkt` claims with their defined types.
2. **Actor:** Require the structure in {{ACTOR-PROFILE, Section 3.4}}:
   * A single `act` object with non-empty `iss` and `sub`, and no nested
     `act`.
   * Configured trust authorizing the RAS to assert that actor
     namespace. Here `act.iss` is the IdP namespace and need not equal
     the token's `iss`.
3. **Proof and authority:** Validate the DPoP proof and key binding, and
   enforce resource, scope, and any additional authorization
   constraints.
4. **Decision:** Apply {{ACTOR-PROFILE, Section 8.1}} to the user and
   issuer-qualified actor. Reject if actor authorization cannot be
   established, including when policy information is unavailable.

## Error Responses {#resource-errors}

Resource errors use the `DPoP` `WWW-Authenticate` challenge under
{{RFC9449, Section 7.1}}, with the following outcomes:

| Failure | HTTP status and error |
|---|---|
| Invalid token, missing required claim, malformed actor, nested actor, or unauthorized actor namespace assertion | 401, `invalid_token` |
| Valid token but required user/actor relationship is not authorized or cannot be established | 403, `actor_unauthorized`, following {{ACTOR-PROFILE, Section 8.2}} |
| Insufficient token scope for the operation | 403, `insufficient_scope` |
| Missing or invalid proof, key mismatch, or required nonce | RFC 9449 resource error processing, including its nonce header and challenge rules |

Actor authorization failures MUST NOT use `insufficient_scope`. The API
MUST NOT expose actor-specific rejection details outside the trust
domain. Token endpoint errors in {{errors}} do not replace these
resource error responses.

# Authorization Server and Client Metadata {#metadata}

The delegated profile identifier is:

`urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`

It identifies RAS and client processing. IdP issuance support, optional
inputs, and ICA eligibility follow {{discovery}}.

## Authorization Server Metadata {#server-metadata}

Servers MUST publish {{RFC8414}} metadata as follows:

* **RAS:** Include both this URI and the base
  `urn:ietf:params:oauth:grant-profile:id-jag` in
  `authorization_grant_profiles_supported`.
  * Include `urn:ietf:params:oauth:grant-type:jwt-dpop` in
    `grant_types_supported` for this profile.
  * Retain the JWT bearer advertisement required for base ID-JAG under
    {{ID-JAG, Section 7.2}}.
* **IdP:** Advertise Token Exchange in `grant_types_supported` and
  ID-JAG in `identity_chaining_requested_token_types_supported` under
  {{ID-JAG, Section 7.1}}.
* **Both:** Advertise supported client authentication methods and DPoP
  algorithms, including {{flow-configuration}}'s common capabilities.

## Client Metadata {#client-metadata}

A client SHOULD advertise this profile URI in its client metadata under
{{ID-JAG, Section 8}}. Its registered `grant_types` MUST permit:

* `urn:ietf:params:oauth:grant-type:token-exchange` at the IdP.
* `urn:ietf:params:oauth:grant-type:jwt-dpop` at the RAS.

A client advertising the base ID-JAG profile also follows its JWT bearer
registration requirement. That support does not permit JWT bearer
redemption of this profile's grants.

## Discovery and Profile Selection {#discovery}

Before using the delegated path:

* The client and IdP MUST agree through trusted configuration on
  issuance support and any optional actor or refresh-token subject
  inputs. Generic JWT or authentication-method support is insufficient.
* The client and IdP MUST verify the RAS's profile advertisement. The
  client MUST also verify its `jwt-dpop` grant support, the configured
  IdP support, and the selected input.
* For continuing access, participants MUST use {{ICA, Section 7}}'s
  metadata and trust rules:
  * The IdP MUST advertise `identity_continuation_supported=true`.
  * A continuation-aware RAS MUST advertise ICA's continuation profile
    and required grant types.
  * Participants MUST configure an eligible source and assertion
    acquisition mechanism under {{continuation-sources}}. Metadata
    alone does not establish the agent's eligibility.

Advertisements establish neither trust nor authorization; selection is
enforced under {{flow-configuration}}. Actor Profile metadata MAY
advertise independently supported paths. Servers MUST NOT advertise its
full Token Exchange algorithm solely for implementing this profile.
If published, `actor_profile_token_exchange` MUST describe those paths
and agree with shared ID-JAG capabilities.

# Security Considerations {#security}

The security requirements of the selected credential and grant
specifications, {{RFC9700}}, and {{RFC8725}} apply.

## Credential and Token Confusion

Validators MUST use mutually exclusive validation rules for the
credential classes they accept under {{RFC8725, Section 3.12}}. A
trusted signature or a matching audience alone MUST NOT convert a client
assertion, platform credential, API access token, or grant into another
credential class.

Credentials and proofs MUST use the transport protection required by
their protocols. DPoP does not replace HTTPS or client authentication.

## Time, Replay, and Key Changes {#time-validation}

Validators MUST enforce the selected credential's expiration and other
applicable time claims. Clock skew is a configured deployment parameter
and SHOULD remain small, normally within the few minutes contemplated by
{{RFC7519}}. A skew allowance MUST NOT increase a configured maximum
credential age or permitted lifetime.

Replay protection follows the credential, proof, and grant mechanisms
independently. Where a mechanism requires replay state through
expiration, that state MUST cover the maximum allowed clock skew. A
fresh proof does not make an expired credential valid; an unchanged
identifier does not authorize a new proof key.

## Credential Authority and Key Isolation

A compromised credential authority can assert identities within its
trusted scope. Exact bindings, tenant boundaries, issuer-scoped key
lookup, and limits on attester authority constrain that scope; a new JWT
type does not repair excessive trust.

The optional instance-attestation input inherits Identification's
attester trust, receiver scoping, continuity, and privacy requirements.
A holder of a shared private key can present attestations issued for
that key. Agent isolation therefore requires separate key control and
attester policy; instance mapping alone does not provide it.

## Authorization Changes and Revocation {#status-changes}

Before issuance, the IdP MUST apply current binding and authorization
policy and reject an inactive agent or withdrawn binding once the change
has been applied. Cached policy data MUST have configured freshness
limits; stale data MUST NOT authorize issuance.

Cross-system disablement and revocation require the mechanisms in
{{lifecycle-gap}}. Without a signal or online check, issued tokens can
remain usable until expiration. ICA continuation rechecks IdP
authorization, chain state, and its anchor; chain termination does not
notify resources or revoke their outstanding tokens.

Account-linking errors can authorize access to another user's account.
{{subject-resolution}} requires issuer, namespace, tenant, and
link-change checks before authorization. Proof of key possession does
not establish account ownership. Link removal prevents further issuance
through that link but does not revoke outstanding access tokens.

# Privacy Considerations {#privacy}

A stable agent identifier can correlate activity across resources,
users, or execution instances. Issuers SHOULD disclose only the agent
attributes needed for the authorized purpose. User and agent context
remain separate when the agent acts for a user.

The mapping in {{actor-construction}} keeps external workload
identifiers out of the ID-JAG. The RAS preserves the governed actor
identifier; this profile does not define pairwise actor translation.

Instance context can increase correlation further. Any consuming profile
introducing it needs purpose limits, retention guidance, and clear rules
about whose activity it describes.

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

# Remaining Gaps and Coordination {#upstream-gaps}

This informative appendix records unresolved contracts and coordination
requests. It adds no conformance requirements. The assessed revisions
are WAG-00, ID-JAG-04, ICA-02, Actor Profile-00, SPIFFE OAuth-02,
ATTEST-11, WIT-02, and JWT DPoP Grant-01.

## Responsibility Boundaries {#responsibility-boundaries}

| Concern | Defined by |
|---|---|
| External identity to governed agent; delegated issuance and redemption | This profile, using the extension point in {{ID-JAG, Section 9.7}} |
| ID-JAG format and base grant processing | {{ID-JAG}} |
| Continuing access, continuation evidence, and chain lifecycle | {{ICA}}, composed under {{continuing-access}} |
| Actor object, current actor, and actor-aware resource policy | Selected rules of {{ACTOR-PROFILE}}, as specified in {{actor-construction}} |
| Base workload authentication and proofs | SPIFFE OAuth, WIMSE, and ATTEST |
| Attested instance identity, continuity, and receiver scoping | {{INSTANCE}}; this profile defines instance-to-agent resolution |
| Self-acting workload grant | WAG composition in {{wag-flow}}; upstream grant changes in {{wag-gaps}} |
| Self-acting subject resolution and agent linking | This profile, {{wag-subject-resolution}} |
| Downstream instance context | {{INSTANCE}} defines the object; propagation through this flow is outside this revision |
| Agent provisioning and disablement signals | Future provisioning and lifecycle specifications |

## WAG Grant Contract {#wag-gaps}

**Problem.** {{WAG, Section 5}} anticipates IdP issuance through Token
Exchange but leaves the issuance, sender-constraint, and discovery
contracts incomplete. These are dependencies of {{wag-flow}}.

{{WAG, Section 7}} requires acceptance of previously unseen agent
identifiers under trusted issuers and permits just-in-time projection
into an IdP. WAG should distinguish accepting a new asserted identity
from linking it to an existing governed or local principal and granting
that principal authority. {{wag-subject-resolution}} defines this
composition's mapping and linking requirements.

**Request to WAG.** Complete these contracts in WAG, leaving external
identity resolution and governed-agent linking to this profile:

* **Issuance:** Define workload-evidence inputs, with the resulting
  subject in the IdP's governed-agent namespace.
* **Refresh-token input:** A user's refresh token alone does not
  establish agent authority. Define whether an IdP refresh token can
  carry continuing self-acting authority, including:
  * Establishment, subject/client binding, and current workload
    evidence.
  * Required proofs, revocation, and authority limits.
* **Identifiers and discovery:** Define WAG-owned token-type and
  JWT-type registrations, plus issuance and redemption discovery. RAS
  discovery can use `authorization_grant_profiles_supported`; the ID-JAG
  URI does not advertise WAG support.
* **Sender constraint:** Define proof-key relationships, audience rules,
  errors, nonces, and replay processing at issuance and redemption. This
  document proposes DPoP and a RAS-issuer audience.
* **Authority and continuation:** Define resource and scope ceilings and
  handling of absent or unsupported limits. Explain or revise WAG's
  prohibition on issuing refresh tokens at redemption, separately from
  accepting an IdP refresh token as an issuance input.

These are coordination requests; this document defines no replacement
grant, WAG-owned identifier registration, or local refresh exception.

## Bound ID-JAG Redemption {#bound-grant-coordination}

**Problem.** ID-JAG's general redemption and metadata rules use JWT
bearer grants, while its bound-grant example uses `jwt-dpop`. ICA uses
the latter for bound grants. JWT DPoP Grant's generic validation error
also needs explicit precedence relative to DPoP nonce challenges.

**Request to ID-JAG and JWT DPoP Grant, coordinated with ICA.** Align
normative grant selection, client and server metadata, and proof-error
and nonce recovery. This profile selects `jwt-dpop` for every ID-JAG it
issues under {{redemption}}, with the explicit nonce rule in {{errors}};
its clients do not infer grant selection from examples or retry with a
bearer grant.

## Calling-Agent Continuation {#continuation-gap}

**Problem.** ICA's access-token exchange serves the workload receiving a
call; its task mechanism depends on durable RAS task authorization. A
calling agent holding a token for a third-party API does not thereby
qualify for either source. Requiring the same governed actor does not
supply the missing authorization context.

**Request to ICA.** If general calling-agent continuation is supported,
define how the CAI establishes that caller's eligibility and binds it to
an accepted RAS authorization, including assertion acquisition and
revocation. This profile can then consume that contract. Until then,
{{continuation-sources}} limits its composition to ICA's existing
receiver and assigned-task cases; root exchanges remain available under
{{exchange-request}}.

## Reusable Actor Mapping {#actor-coordination}

**Problem.** Actor Profile's generic credential processing copies an
external subject into the actor; this profile instead resolves a
governed identity under {{actor-construction}}. Repeating that mapping
contract in other consumers could produce inconsistent namespaces.

**Request to Actor Profile.** Consider a reusable principal-resolution
extension point separating credential validation, authorized identity
mapping, and actor construction. This is consolidation work: the ID-JAG
extension defined here does not depend on its adoption. ID-JAG itself
needs no change to permit this actor processing.

## X.509-SVID as the Sole Actor Evidence {#x509-gap}

**Problem.** X.509-SVID authenticates a TLS connection but supplies no
JWT for the `actor_token` field defined in this revision. Client
authentication alone does not select the governed actor.

**Request to consuming profiles, coordinated with SPIFFE OAuth.** Define
an explicit way to bind connection evidence to the requested actor and
any output key. Existing X.509-SVID client authentication remains usable
with a supported actor JWT. No adapter access token is required here.

## Additional Credential Compositions {#credential-gap}

**Scope choice.** Direct WIT-SVID actor input is deferred. SPIFFE OAuth
supplies presentation and proof mechanisms; a consuming profile still
needs actor/header matching, capability signaling, and an output-key
rule.

That composition must choose the output-key relationship explicitly.
{{WIT, Section 9.4}} prohibits using the workload key after credential
expiration. Reusing it for DPoP therefore requires downstream lifetime
limits; a separate DPoP key requires an explicit authorization rule and
must not be described as issuer-endorsed merely by co-presentation. This
revision defines neither alternative for direct WIT-SVID actors.
WIT-SVID remains usable for client authentication with separate actor
evidence, subject to its own key-use restrictions.

Bearer-input assurance limits and key requirements are specified in
{{credential-requirements}}; they require no change to ATTEST.

## Instance Context {#instance-identification}

**Problem.** A workload identity can span several replicas
{{SPIFFE-CONCEPTS}}. An identifier alone establishes neither continuity
nor enrollment or key replacement. Runtime identification does not by
itself make that runtime an authorization principal.

{{INSTANCE}} defines instance identity and continuity requirements;
{{instance-agent-resolution}} consumes that evidence for agent
resolution. Enrollment and key-replacement protocols remain outside both
profiles.

**Remaining work for this consuming profile.** Define propagation of
Identification's optional `client_instance` context through the ID-JAG
and access token, including its relationship to the actor, provenance,
receiver scoping, and retain, replace, or omit rules during exchange.
Self-acting context would describe the subject's instance; delegated
context would describe the actor's instance. This revision defines no
downstream instance-context composition.

## Provisioning and Disablement {#lifecycle-gap}

**Problem.** Ownership, group membership, and disablement need
consistent record correlation and freshness across IdP and RAS.
Short-lived grants do not revoke outstanding tokens. SCIM Agent
resources {{SCIM-AGENT}} and {{RFC7644}} are building blocks, not a
complete propagation contract.

**Request to future provisioning and lifecycle specifications.** Define
issuer/tenant-qualified correlation, authoritative properties, update
ordering, freshness bounds, missed-event recovery, and the effect on
outstanding tokens. Enrollment and clone detection initially remain
platform-specific. Model/runtime assurance needs a separate profile only
when producers and consumers agree on its semantics.

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
