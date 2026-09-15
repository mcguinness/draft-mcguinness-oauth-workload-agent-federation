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
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  RFC6750:
  RFC8705:
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
  INSTANCE:
    title: "Client Instance Identification for Attestation-Based Client Authentication"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-id/draft-mcguinness-oauth-client-instance-id.html
    author:
      - name: Karl McGuinness
    date: 2026-09-15
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-instance-id-latest
  ATTESTER-ENDORSEMENT:
    title: "OAuth 2.0 Client Attester Endorsement"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-client-attesters/draft-mcguinness-oauth-client-attesters.html
    author:
      - name: Karl McGuinness
    date: 2026-09-15
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-attesters-latest
  ICA: I-D.mcguinness-oauth-id-continuation-assertion
  RFC6755:
  WAG: I-D.carleton-workload-authz-grant
  SPIFFE-CONCEPTS:
    title: "SPIFFE Concepts"
    target: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
    author:
      - org: SPIFFE
  ENTITY-PROFILES: I-D.mora-oauth-entity-profiles
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
--- abstract

This document specifies how an agent platform integrates with an
identity provider to obtain downstream authorization for its agents.
It defines workload-evidence requirements, governed-agent resolution,
OAuth client association, and subject linking. The governed agent is
the subject for self-acting Workload Authorization Grant (WAG) access
or the actor for user-delegated Identity Assertion JWT Authorization
Grant (ID-JAG) access.

The document defines a complete ID-JAG flow with proof-bound grants
and resource-specific access-token protection. The WAG wire profile
remains pending the upstream changes identified here.

--- middle

# Introduction

This profile gives agent-platform vendors and IdP implementers a common
integration contract: which workload evidence to provide, how to bind it
to a governed agent and OAuth client, and how to request downstream
authorization. It specifies the protocol behavior and trust decisions
needed for that integration. Platform-specific credential acquisition
and administrative interfaces remain deployment choices.

An agent platform authenticates a workload in its own identity
namespace. An identity provider (IdP) may govern that workload as a
separate agent principal, with its own owner, status, groups, and
assignments. A resource authorization server (RAS) needs to know which
governed principal has been authorized, without implementing every
platform's credential validation and identity mapping.

This document assigns that resolution and policy decision to the IdP.
Its core is the Federation Binding: external evidence identifies a
governed agent, and an approved binding determines which OAuth client
can use that evidence in the selected flow. The grant preserves the
governed agent as subject or actor.

The integration divides responsibility as follows:

* **Platform and client:** Supply verifiable workload evidence,
  authenticate the OAuth client, and present the requested resource,
  authority, and proofs using the selected grant flow.
* **IdP:** Resolve the evidence to a Registered Agent, the principal it
  governs. Check the permitted client and acting relationship, then
  issue a grant identifying that agent as subject or actor.
* **RAS and API:** Resolve the grant's identities, preserve the acting
  relationship and proof binding, and enforce downstream authorization.

Authenticating an OAuth client, resolving an agent, and proving
possession of a key are distinct operations. None alone establishes
permission to act for a user. Optional instance identification adds
runtime continuity evidence; it does not confer independent authority.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth and Token Exchange terms follow {{RFC6749}} and {{RFC8693}}.
Client Attestation and Client Instance follow {{ATTEST}}.

## Roles

Agent Platform:
: The environment that runs agents and supplies workload evidence from
  its own or an approved external credential authority. It can also
  implement the OAuth client that obtains access for an agent.

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
  identity, Source Tenant, and Registered Agent. For flows requiring
  client authentication, it identifies permitted combinations of flow,
  credential class, and OAuth client.

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

Conformance applies to each implemented role and selected grant and
credential profile:

* **ID-JAG:** The IdP, RAS, and client MUST implement their respective
  requirements in {{delegated-flow}} and {{metadata}}. The API MUST
  implement {{api-processing}}.
  * The common integration path requires an ID Token subject, platform
    JWT actor, `private_key_jwt` client authentication, and DPoP at the
    token endpoints. A platform providing evidence for this path MUST implement
    {{platform-evidence-contract}}.
  * IdP refresh-token subjects and the additional inputs in
    {{actor-inputs}} are OPTIONAL.
* **WAG:** {{wag-flow}} defines the federation requirements. Complete
  protocol conformance remains pending the upstream contract in
  {{wag-gaps}}. Support for one grant does not advertise support for the
  other.

Implementations MAY support other flows, but MUST NOT use them as a
fallback after validation or authorization fails for this profile.
Continuation composition, provisioning protocols and account
administration, multi-agent delegation chains, instance propagation, and enrollment or
key-replacement protocols are outside core conformance.
{{continuing-access}} identifies ICA as the continuation mechanism;
{{operational-guidance}} gives deployment guidance.

Instance-based agent resolution and client-endorsement trust are
extension work described in {{instance-agent-resolution}} and
{{attester-endorsement-extension}}. Their editor's copies are informative
references; neither is a conformance dependency of this revision.
{{upstream-gaps}} records the remaining dependencies and coordination.

## Integration Contract and Profile Requirements {#profile-requirements}

Common requirements are in {{identity}} and {{authorization}}; WAG
requirements are in {{wag-flow}}. This non-normative index locates the
additional ID-JAG requirements by implementer. The cited sections define
the rules; selected base specifications also apply.

| Implementer | Requirement | Defined in |
|---|---|---|
| Platform | Verifiable workload JWT and agreed evidence contract | {{platform-evidence-contract}} |
| Client, IdP, and RAS | Platform JWT, `private_key_jwt`, RS256, and ES256 DPoP common capabilities | {{flow-configuration}} |
| Client and IdP | ID Token or supported IdP refresh-token subject; direct JWT actor; one resource and non-empty scope | {{exchange-request}} |
| IdP | Validate evidence; enforce the client, flow, credential class, and Federation Binding as one approved combination | {{identity}} and {{inputs}} |
| IdP | Authorize one user-to-agent relationship; construct governed `act.sub` and IdP `act.iss` | {{authorization}} and {{actor-construction}} |
| IdP and RAS | Resolve the user in the target namespace; authorize links and reject conflicts | {{subject-resolution}} |
| IdP | Bind grant expiry to input expiry and a finite configured limit; five minutes recommended | {{grant-issuance}} |
| Client, IdP, and RAS | DPoP at both token endpoints; access-token protection selected per resource | {{issuance-proof}} and {{access-token-protection}} |
| Client and RAS | `jwt-bearer` redemption; grant confirmation check; matching resource and preserved actor | {{redemption}} |
| API | Configured applicability; actor gate and selected token protection | {{api-processing}} |
| IdP and RAS | `invalid_grant` for invalid credentials; `actor_unauthorized` for delegation denial | {{errors}} |
| Client, IdP, and RAS | Grant-profile URI at RAS and client; configured IdP issuance and optional inputs | {{metadata}} |

Before exchanging tokens, the platform and IdP establish the evidence
contract in {{platform-evidence-contract}} and the client, agent, tenant,
and target associations in {{flow-configuration}}. Configuration supplies
deployment-specific values; it does not replace the specified validation
and authorization behavior.

Base ID-JAG or generic Token Exchange support does not imply support for
these requirements.

# Profile Selection and Identity Binding {#identity}

The IdP MUST configure:

* Credential-authority trust policy, approved keys or key-source
  selection rules, and validation rules for each accepted credential
  class. Attester approval follows {{attester-trust}}.
* Exact external identity selectors and their Source Tenant and
  Registered Agent associations.
* Permitted OAuth clients where the selected flow requires a client.
* Approved RAS issuers, resources, Target Tenants, and applicable
  identity and authorization mappings.

Request hints, discovered client metadata, and unverified JWT claims
MUST NOT by themselves establish credential-authority trust or change an
approved Federation Binding. Configured attester-to-client associations under
{{attester-trust}} do not themselves authorize a governed-agent mapping.

The IdP MUST authorize binding creation and changes, including imports
from platform registries. Administrative mechanisms are outside this
profile ({{operational-guidance}}).

## Selecting the External Identity

| Evidence | Identity used for resolution | Qualification |
|---|---|---|
| Platform JWT | Approved issuer and exact subject, with configured additional selectors | Workload evidence; not automatically OAuth client authentication |
| Client Attestation, agent has its own client | Attester selected under {{attester-trust}}; client `sub` | Client-to-agent mapping is explicit |
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
verify that the authenticated client is authorized for the selected
flow, actor credential class, and Federation Binding as one approved
combination under {{flow-configuration}}. Permission through another
binding for the same Registered Agent MUST NOT satisfy this check. The
IdP MUST NOT substitute the client's identity for the resolved actor.

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

For token exchange, the IdP MUST validate the subject credential under
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

### Resolution at the RAS {#ras-subject-resolution}

After validating the ID-JAG and its client and proof bindings, the RAS
MUST resolve exactly one local user in the authorized Target Tenant
before issuing an access token. Its configured resolution rules MUST:

* **Issuer subject:** Qualify `sub` by the validated IdP issuer and the
  tenant relationship under {{ID-JAG, Section 6}}. IdP and RAS tenant
  identifiers are not interchangeable.
* **Local subject:** Use `aud_sub` only when the trusted IdP is
  authorized to assert local account identifiers for the selected Target
  Tenant. An asserted local identifier MUST NOT override a conflicting
  approved link.
* **Alternate namespace:** Process `sub_id` under ID-JAG's format and
  issuer-association rules ({{ID-JAG, Sections 3.2.2 and 9.5}}).
* **Conflicts:** Reject conflicting identifiers used for resolution or
  multiple local matches. The RAS MUST NOT retry with a weaker selector
  or another tenant after such a conflict.

The access token's `sub` identifies that resolved user in the RAS's
access-token namespace. The RAS resolves `act.iss` and `act.sub`
separately under {{agent-correlation}} and MUST NOT link the agent to
the user's account merely because it acts for that user.

### Account Linking {#subject-linking}

The RAS MUST use an authoritative association to link an external user
to a local account. It MUST NOT establish a link from email, username,
or display-name equality alone. Issuer-qualified SAML NameIDs remain
usable under {{ras-subject-resolution}}, including email-format NameIDs.

Each qualified external identity MUST resolve to at most one local
account per Target Tenant. A link change MUST NOT transfer an outstanding
grant or delegation to another user; further use MUST be rejected if
continuity with the authorized user cannot be established.

The IdP and RAS MUST reject issuance for a disabled user or required
link, or missing, ambiguous, or conflicting resolution ({{errors}}).
Provisioning and link-administration mechanisms are deployment choices;
{{operational-guidance}} provides informative guidance.

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

### Platform Evidence Contract {#platform-evidence-contract}

For the common integration path, the platform MUST supply a signed JWT
containing `iss`, `sub`, `aud`, and `exp` that satisfies the agreed IdP
validation policy below. The platform's credential authority MUST derive
the workload identity from authenticated platform evidence; a caller's
requested subject or agent identifier alone MUST NOT authorize issuance.

Before use, the platform and IdP MUST agree on:

* The credential issuer, verification-key source, and algorithms.
* The exact workload identity selectors and their meaning, including
  any platform tenant or agent selector needed to distinguish workloads.
* The audience authorizing presentation as workload evidence to the IdP.
* Credential classification and time limits, including issuance and
  caching behavior.

For repeatable integrations, platforms SHOULD use the following common
identity conventions:

| Element | Convention |
|---|---|
| `iss` and `sub` | Identify one stable platform agent or workload across its replicas; include the platform tenant in the issuer or subject namespace when needed for uniqueness |
| `aud` | The target IdP issuer identifier; an existing credential audience may instead be explicitly approved by IdP policy |
| Key source | One approved issuer-scoped JWK Set URI reusable across customer integrations |
| Additional selectors | Needed only when `iss` and `sub` do not sufficiently distinguish the governed workload |

The IdP MUST support the issuer-and-subject mapping without requiring
vendor-specific agent claims. Existing native JWT formats remain usable
under the validation rules below. No new JWT type or issuer-discovery
document is defined; key locations are configured or obtained through
an independently supported, trusted issuer-discovery mechanism.

The platform MUST provide an authorized workload a way to obtain that
evidence. This document does not standardize that platform interface.
The client presents the JWT as `actor_token` and separately authenticates
under {{exchange-request}}; the JWT need not use the IdP's Registered
Agent identifier or OAuth `client_id` as its subject.

### IdP Validation

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

This document defines no client-authentication method that maps an
arbitrary platform JWT directly to an IdP-assigned `client_id`.

The JWT is presented as `actor_token` under {{exchange-request}}.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL direct actor input. The client MUST
present the identical compact JWT in `actor_token` and the
`OAuth-Client-Attestation` header and authenticate using the configured
ATTEST method. The IdP MUST validate the attestation and proof before
resolving the agent. {{actor-inputs}} defines the proof/key
relationship.

### Attester Trust and Agent Resolution {#attester-trust}

The IdP MUST use configured attester-to-client and key associations.
For an agent with its own client, it MUST identify the attester
unambiguously from the trusted verification key and resolve that
attester and the validated client `sub` through an approved Federation
Binding. An `iss`, when present, MUST match that authority; base ATTEST
does not require it.

This input does not distinguish agents behind a shared client. Those
agents use platform JWTs or another supported credential that resolves
one agent unambiguously. Instance-based resolution and client attester
endorsement remain extension work in {{instance-agent-resolution}} and
{{attester-endorsement-extension}}. ATTEST's additional-signal mode is
not a separate actor input in this revision.

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

X.509-SVID MAY authenticate the client under {{SPIFFE-OAUTH, Section
3.2}}. The request still requires a supported JWT actor credential;
connection evidence alone as actor input is outside this revision
({{x509-gap}}).

## SPIFFE WIT-SVID {#wit-input}

WIT-SVID MAY authenticate the client under {{SPIFFE-OAUTH, Section
3.3}} and {{WIT}}, including their proof and key-use requirements. The
request still requires a supported actor credential. Direct WIT-SVID
actor input remains outside this revision ({{credential-gap}}).

## Credential Use Requirements {#credential-requirements}

Each input retains its credential specification's validation, proof,
replay, and key-use requirements. The IdP MUST apply the selected input's
requirements to every presentation and check the current Federation
Binding and client association. DPoP MUST NOT substitute for another
required credential proof.

For bearer JWT-SVID and platform JWT inputs, co-presentation with DPoP
does not establish issuer endorsement of the proof key. A deployment
requiring that assurance MUST use evidence that cryptographically binds
the key. Bearer-evidence theft remains a threat even when the output is
sender-constrained ({{security}}).

Optional input selection follows {{metadata}}. An assertion-type URI
identifies a credential format; it is not an authentication-method
metadata value. Shared workload identities do not distinguish replicas;
instance assurance needs a separate evidence profile
({{instance-identification}}).

# Authorization Policy {#authorization}

Validated identity does not itself grant authority. After credential
validation and resolution under {{inputs}} and {{identity}}, the IdP
MUST authorize issuance for the resolved agent, authenticated client,
acting relationship, Source and Target Tenants, RAS, resource, and
requested authority under current assignments and policy.

Self-acting authority MUST NOT exceed the agent's authority. Delegated
authority MUST NOT exceed the user's authority and the agent's approved
delegation under {{delegation-approval}}. This delegation is a gate on
acting for the user, not a requirement for independent agent ownership
of each data permission ({{actor-authorization}}).

The IdP MAY grant an authorized non-empty scope subset. It MUST return `invalid_scope` if none can be granted, or if
policy requires full approval and the request exceeds it. Any reduction
MUST be reflected in the grant and response.

The IdP MUST NOT issue a grant by dropping a required actor or binding,
substituting an external identifier for the governed identity, or
weakening proof requirements. Denied delegated access MUST NOT fall back
to self-acting access. ID-JAG errors follow {{errors}}; WAG's wire
contract remains in {{wag-gaps}}.

## Delegation Approval {#delegation-approval}

Before constructing `act`, the IdP MUST authorize the resolved agent to
act for the user, client, tenant, RAS, resource, and requested
authority. The IdP MUST reject missing, revoked, expired, or
insufficient delegation. Valid credentials, user sign-in, or a shared
client MUST NOT imply approval or permit one agent to reuse another
agent's approval.

Approval mechanisms and records are outside this profile. Pre-existing
actor chains are rejected under {{actor-inputs}}.

## Canonical Agent Attribution {#agent-correlation}

The governed identity is the IdP issuer and Registered Agent identifier:
the WAG subject or ID-JAG actor. The RAS MUST resolve that qualified
identity independently of the user's identity.

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

Provisioning, ownership, and membership handling are deployment concerns
described in {{operational-guidance}}.

Where the RAS requires a local agent principal, the IdP or its authorized
directory connector SHOULD provision and synchronize that principal
using the exact pair (IdP issuer, Registered Agent identifier). This is
the WAG (`iss`, `sub`) or ID-JAG (`act.iss`, `act.sub`) pair. The RAS
MUST retain that association independently of its local principal ID.

Directory synchronization SHOULD propagate activation and deactivation.
Once deactivation is applied, the RAS MUST reject new issuance and
refresh for that agent. Provisioning may use existing directory sync,
an administrative API, or SCIM; this profile requires no specific
provisioning protocol. Offline token validation still has the revocation
limits in {{status-changes}}.

## Delegated Actor Authorization {#actor-authorization}

For delegated access, the RAS and API MUST enforce both:

* **User authority:** The requested operation is within the user's
  permissions and the grant or token's authorized scope and constraints.
* **Actor gate:** The issuer-qualified agent is permitted to act for
  that user in the selected tenant and resource, within the approved
  delegation. A valid signature or an `act` claim alone does not open
  this gate. Failure to establish it MUST result in denial.

The gate MAY be implemented through an agent registration, tenant
assignment, consent policy, or another explicit authorization rule.
Deployments MAY additionally require the agent to hold independent
permissions on each underlying object; that intersection is local
policy, not a baseline requirement. The API MUST enforce the gate at
request time, directly or through a validated RAS authorization whose
scope and freshness satisfy configured resource policy.

The RAS and API SHOULD record the user, qualified actor, OAuth client,
tenant, resource, operation, and decision in audit events. An existing
acting-principal field can carry the resolved `act` identity, retaining
its issuer association. The client identifier MUST NOT replace the
governed actor in authorization or attribution.

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
  namespace, and the established tenant relationship.
* **Link authority:** Authorize creation and changes of local agent
  links for that issuer and Target Tenant. Names, owners, groups, and
  client identifiers alone MUST NOT establish an agent link or merge
  it with a human account.
* **Consistent resolution:** Resolve the same governed agent to the same
  local agent whether it appears as a self-acting WAG subject or an
  ID-JAG actor. The acting relationship still determines authorization;
  a shared agent link does not make those authorities interchangeable.
* **Failure and lifecycle:** Reject missing, conflicting, ambiguous, or
  disabled resolution when a required link cannot be established.
  Binding or link replacement MUST NOT transfer outstanding grants or
  delegated authority to a different agent.

ID-JAG's user-resolution claims do not automatically become WAG claims.
If the composition needs an additional target-local subject identifier
on the wire, its authority, tenant scope, and consistency with `sub`
need to be specified with WAG. Provisioning and lifecycle mechanisms
remain outside this profile.

# Delegated ID-JAG Flow {#delegated-flow}

This section profiles ID-JAG issuance and redemption using the actor
extension point in {{ID-JAG, Section 9.7}}.

Both token endpoints retain {{RFC6749, Section 5.1}}'s JSON response
encoding and cache-control requirements. Error responses follow
{{errors}}.

## Configuration and Common Capabilities {#flow-configuration}

Before issuance, the IdP MUST have a trusted association between:

* Its authenticated OAuth client and the approved combination of flow,
  actor credential class, and Federation Binding.
* That client and its client registration at the target RAS.
* The user and the subject namespace used for that RAS, following
  {{subject-resolution}}.
* The Source Tenant, Target Tenant, RAS issuer, and permitted resource.

The IdP and RAS MUST configure this profile as required for the
applicable client and trust relationship. The IdP MUST enforce that
selection even if `actor_token` is omitted. The RAS MUST enforce it even
if `act` or `cnf` is omitted from a presented ID-JAG. Metadata
advertisement alone establishes neither trust nor authorization.

Each authorization server MUST establish authoritative client metadata
through registration or, when supported, {{CIMD}}. CIMD resolution and
client authentication do not establish trust in workload evidence or
permission to use a Federation Binding. The client and servers MUST
support `private_key_jwt` under {{RFC7523, Section
2.2}}. Other configured methods MAY be used. Client identifiers and keys
MAY differ between servers.

One platform client MAY serve multiple agents, including the client's
existing SSO integration when authorized for Token Exchange. Each actor
credential still selects exactly one approved Federation Binding. No
per-agent OAuth client or per-replica registration is required.

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

The client and RAS MUST support RFC 7523 JWT bearer grant redemption
with the confirmation checks in {{redemption}}. DPoP support is required
at the token endpoints; resource APIs implement the access-token
protection selected under {{access-token-protection}}.

## Token Exchange {#exchange-request}

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
  * Enforce all bindings retained with the subject grant. Selecting
    another actor input MUST NOT bypass required evidence; reject an
    unsupported or conflicting grant binding with `invalid_grant`.

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
* **Client attestation:** Apply ATTEST authentication and proof checks
  to the exact JWT in `actor_token`.
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

The grant lifetime SHOULD be no more than five minutes. Its
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

* `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`.
* `assertion` containing the ID-JAG.
* One `resource` equal to the resource authorized by the grant.
* A fresh DPoP proof made with the same key used at issuance.

This profile uses {{RFC7523}} and applies the confirmation checks of
{{ID-JAG, Section 9.8.1.2}} to that grant type. The `jwt-bearer` name does
not permit ignoring the assertion's `cnf`. This explicitly selects
ID-JAG's Section 4.4 grant type instead of the `jwt-dpop` value in its
bound-grant example ({{bound-grant-coordination}}).

A redemption `scope` MAY request a subset. If omitted, the grant's
scopes are the requested upper bound.

### Grant Validation {#redemption-validation}

The RAS MUST perform ID-JAG validation and additionally:

1. **Actor:** Require a single `act` object under Actor Profile's rules:
   * Require non-empty `iss` and `sub`, with no nested `act`.
   * Require `act.iss` to equal the ID-JAG issuer and configured trust
     to authorize assertion of that namespace.
2. **Proof and client:** Require `cnf.jkt`. Validate the DPoP proof under
   RFC 9449 and require its public key thumbprint to match `cnf.jkt`
   exactly. A missing proof or key mismatch MUST fail with
   `invalid_grant`. Independently authenticate the client identified
   by `client_id`.
3. **Authority:** Require the grant's resource and scope constraints.
   Validate the requested resource and any scope reduction, and apply
   ID-JAG's processing for any `authorization_details` present.
4. **Local authorization:** Resolve the user under
   {{ras-subject-resolution}} and the governed actor under
   {{agent-correlation}}. Apply current RAS policy to the user/actor
   relationship under {{actor-authorization}}, client, tenant, and
   resource. A valid grant sets an authority ceiling; it does not
   require issuance.

### Access Token Issuance and Response {#access-token-response}

After successful validation and authorization, the RAS MUST issue a JWT
access token under {{RFC9068}} with:

* The RAS as issuer, the resolved user as subject, and the resource as
  audience.
* The validated `act` unchanged and the access-token protection selected
  under {{access-token-protection}}.
* A non-empty authorized `scope`; otherwise, return `invalid_scope`.
* All applicable constraints preserved in the token or enforced resource
  policy.

The RAS MUST NOT broaden authority or substitute its authenticated client
for the actor. The response MUST follow {{ID-JAG, Section 4.4.2}} and
RFC 6749 and report the selected token type. The client MUST reject an
output that does not satisfy its configured protection requirement.

Refresh-token issuance follows {{ras-refresh}}. An IdP refresh token
remains an optional subject credential for a new exchange under
{{exchange-request}}.

An unexpired ID-JAG remains reusable under ID-JAG. Each redemption
requires fresh proof validation and current RAS policy. Grant expiry
alone does not revoke an issued token; {{continuing-access}} defines
subsequent exchanges.

### Access-Token Protection {#access-token-protection}

Sender-constrained access tokens are RECOMMENDED. The client and RAS
MUST select permitted protection through trusted client and resource
configuration before issuance; this profile introduces no request flag.
The choice MUST satisfy IdP-imposed constraints and client and resource
policy. A validation failure MUST NOT trigger a weaker mode.

| Selected protection | Access token | Token response and API use |
|---|---|---|
| DPoP | `cnf.jkt` equals the redeemed grant's key thumbprint | `token_type=DPoP`; RFC 9449 proof and resource processing |
| Mutual TLS | `cnf.x5t#S256` identifies the client certificate validated at redemption | `token_type=Bearer`; certificate binding and presentation under RFC 8705 |
| Bearer | No `cnf` | `token_type=Bearer`; RFC 6750 presentation, explicitly permitted by policy |

For mutual TLS, the client MUST also prove possession of the grant's
DPoP key in the same authenticated redemption request. The RAS MUST
authorize binding the output to the presented certificate under
{{RFC8705}}; certificate possession alone does not redeem the grant.

Bearer issuance MAY support resources without sender-constraint support.
It protects neither a stolen access token nor its subsequent API use;
grant proof validation remains mandatory. The RAS MUST NOT copy the
grant's `cnf` into an access token whose binding will not be enforced.
Clients and APIs MUST NOT treat a constrained token as an unconstrained
bearer token or bypass an unrecognized confirmation method.

### RAS Refresh Tokens {#ras-refresh}

The RAS SHOULD NOT issue refresh tokens, retaining {{ID-JAG, Section
4.4.3}}. It MAY do so for authorized long-running work under explicit
policy. When issuing refresh tokens, the RAS MUST:

* Bind the refresh token to the authenticated client and the redeemed
  grant's DPoP key, including for confidential clients. Validate both
  bindings on every refresh under {{RFC9449}} and {{RFC6749}}.
* Preserve the original user, qualified actor, tenant, resource, and
  delegation ceiling. Apply current local user and actor authorization;
  reject refresh after the relevant principal or authorization is disabled.
* Apply finite configured lifetime and inactivity limits and any known
  delegation deadline, with refresh-token protection under {{RFC9700}}.
  Rotation MUST NOT extend an authorization deadline.

A refresh token renews access within the existing RAS authorization;
it does not authorize a new resource or broader delegation. Revocation
at the IdP needs a signal or online check to affect the RAS promptly;
local refresh is not evidence of a fresh IdP decision. Deployments MUST
configure the acceptable delay and resulting authorization lifetime.

Refresh responses MUST satisfy {{access-token-response}} and
{{access-token-protection}}, including actor preservation and the
configured output protection.

## Token Endpoint Error Responses {#errors}

Token endpoint errors follow {{RFC6749, Section 5.2}}, {{RFC8693,
Section 2.2.2}}, and the selected authentication and proof methods.
Servers MUST validate client authentication, credentials, and proofs
before authorization. This profile specifies the following outcomes:

| Failure | Error |
|---|---|
| Unsupported input combination or ambiguous credential classification | `invalid_request` |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Valid identity evidence but absent, disabled, or ambiguous agent binding, or unauthorized delegation | `actor_unauthorized`, as defined by Actor Profile |
| Missing or invalid DPoP proof at IdP issuance | `invalid_dpop_proof` under RFC 9449 |
| Missing redemption proof or mismatch with grant `cnf.jkt` | `invalid_grant` under ID-JAG confirmation processing |
| Invalid DPoP proof at redemption | `invalid_dpop_proof` under RFC 9449 |
| Otherwise valid proof requiring a nonce challenge | `use_dpop_nonce` and the required RFC 9449 response headers |

Actor-credential failures use `invalid_grant` instead of the default
`invalid_request` described by RFC 8693; this narrowing is intentional.

When the same JWT also authenticates the client, shared validation
failures use that method's error. ATTEST retains its validation and
challenge errors;
a subject grant-binding conflict uses `invalid_grant` under
{{subject-token-validation}}. No failure permits dropping the actor
or its proof binding; error details SHOULD NOT reveal user or agent
existence.

At redemption, an otherwise valid proof requiring a nonce uses RFC 9449
nonce recovery. The client MUST NOT retry without proof or discard the
grant's confirmation requirement after an error.

## Shared-Client Wire Example {#identity-example}

This non-normative example uses one platform SSO client for many agents.
Both servers accept its CIMD URL as `client_id`; a registered client can
use the same topology. Tenant trust, client permissions, and Federation
Bindings remain separately approved. Multiple serving replicas obtain
evidence for the same platform agent; the IdP registers no replicas.

### Configuration and Identity Mapping

| Association | Configured value |
|---|---|
| Shared OAuth client at both servers | `https://platform.example/oauth-client.json` |
| Approved platform issuer and verification keys | `https://platform.example/`; `https://platform.example/workload-jwks.json` |
| External workload subject | `accounts/acme/agents/workload-7` |
| Governed agent and Source Tenant | `agent-42` at `https://idp.example/`; `acme` |
| Target RAS, tenant, and resource | `https://ras.example/`; `acme-data`; `https://api.example/` |
| RAS agent principal | `service-principal-42`, linked to `(https://idp.example/, agent-42)` |
| Delegation | Agent may act for Alice on `files.read` in `acme-data` |

Alice's ID Token has `sub=alice-app` and the shared client URL as `aud`.
The IdP translates her subject to `alice-ras` for the RAS, which links
it to local user `user-108`. Alice holds the file permission; the local
agent principal passes the actor gate without an independent file ACL.

### Platform Evidence

The platform supplies a signed JWT with the following decoded header
and payload. This example's credential class is selected by approved
issuer, audience, and exact workload subject; `typ=JWT` alone does not
select it. Times are illustrative NumericDate values.

~~~ json
{"alg":"RS256","typ":"JWT","kid":"workload-key-1"}
~~~

~~~ json
{
  "iss": "https://platform.example/",
  "sub": "accounts/acme/agents/workload-7",
  "aud": "https://idp.example/",
  "iat": 1789488000,
  "exp": 1789488600
}
~~~

### Exchange Request and Response

The HTTP examples show all application parameters and relevant headers.
Bodies are line-wrapped for display; concatenate their lines before
sending. Uppercase token placeholders stand for complete signed compact
JWTs. HTTP framing headers are omitted. The client-authentication key,
platform signing key, and runtime DPoP key K have distinct roles.

`IDP_CLIENT_ASSERTION` uses the shared client URL as both `iss` and
`sub`, `aud=https://idp.example/token`, a short expiration, and a unique
`jti`. `IDP_DPOP_PROOF` uses K and contains `htm=POST`,
`htu=https://idp.example/token`, a current `iat`, and a unique `jti`.
A server nonce is included if challenged.

~~~ http-message
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: IDP_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&requested_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid-jag
&client_id=https%3A%2F%2Fplatform.example%2Foauth-client.json
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth
%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=IDP_CLIENT_ASSERTION
&subject_token=ALICE_ID_TOKEN
&subject_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid_token
&actor_token=PLATFORM_JWT
&actor_token_type=urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fras.example%2F
&resource=https%3A%2F%2Fapi.example%2F
&scope=files.read
~~~

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store
Pragma: no-cache

{
  "access_token": "ID_JAG",
  "issued_token_type": "urn:ietf:params:oauth:token-type:id-jag",
  "token_type": "N_A",
  "expires_in": 300,
  "scope": "files.read"
}
~~~

The decoded grant header uses `alg=RS256`, `typ=oauth-id-jag+jwt`, and
an IdP signing-key identifier. Its payload includes:

~~~ json
{
  "iss": "https://idp.example/",
  "sub": "alice-ras",
  "aud": "https://ras.example/",
  "iat": 1789488000,
  "exp": 1789488300,
  "jti": "grant-1",
  "client_id": "https://platform.example/oauth-client.json",
  "resource": "https://api.example/",
  "scope": "files.read",
  "act": {"iss":"https://idp.example/", "sub":"agent-42"},
  "cnf": {"jkt":"JKT_K"}
}
~~~

`JKT_K` denotes K's JWK thumbprint. This example uses Actor Profile's
unclassified-actor processing; it omits the recommended `sub_profile`.
The configured issuer and client relationships resolve the tenants.

### Redemption Request and Response

`RAS_CLIENT_ASSERTION` authenticates the same shared client with
`aud=https://ras.example/token` and its own `jti`. `RAS_DPOP_PROOF` is a
fresh proof using K, `htm=POST`, and `htu=https://ras.example/token`.
The RAS validates the grant binding regardless of the API's token mode.

~~~ http-message
POST /token HTTP/1.1
Host: ras.example
Content-Type: application/x-www-form-urlencoded
DPoP: RAS_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&client_id=https%3A%2F%2Fplatform.example%2Foauth-client.json
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth
%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=RAS_CLIENT_ASSERTION
&assertion=ID_JAG
&resource=https%3A%2F%2Fapi.example%2F
~~~

For a resource with explicitly permitted bearer access, the response is:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store
Pragma: no-cache

{
  "access_token": "API_ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 600,
  "scope": "files.read"
}
~~~

The access token uses `typ=at+jwt` and the following decoded payload:

~~~ json
{
  "iss": "https://ras.example/",
  "sub": "user-108",
  "aud": "https://api.example/",
  "iat": 1789488000,
  "exp": 1789488600,
  "jti": "access-1",
  "client_id": "https://platform.example/oauth-client.json",
  "scope": "files.read",
  "act": {"iss":"https://idp.example/", "sub":"agent-42"}
}
~~~

For a DPoP-protected resource, the response instead reports
`token_type=DPoP` and the access token includes `cnf.jkt=JKT_K`. The
client presents it with a fresh API proof including `ath` under RFC 9449.
In either mode, the RAS translates Alice's subject while preserving the
governed actor; the shared OAuth client never becomes that actor.

## Continuing Access {#continuing-access}

An unexpired ID-JAG can be redeemed again under {{redemption}}. A new
exchange under {{exchange-request}} requires a valid subject credential,
current actor evidence, and a fresh authorization decision.

Continuation from an established RAS authorization uses Identity
Continuation Assertion {{ICA}} when extending access beyond local RAS
renewal under {{ras-refresh}}, and requires a separate composition with
this profile. This document defines no ICA exchange, task-authorization
protocol, or continuation lifecycle. {{continuation-sources}} identifies
the federation requirements that such an extension would need to address.
Support for this profile does not imply support for that extension.

Without RAS refresh, long-running work needs fresh IdP subject credentials
and actor evidence whenever a new ID-JAG is needed. An IdP refresh token
can supply the subject credential when permitted; otherwise renewal may
require user interaction. The five-minute recommendation limits grant
redemption, not access-token or approved task duration. Deployments need
to choose their renewal model before scheduling unattended work.

# Resource Server Processing {#api-processing}

The API MUST validate access tokens under {{RFC9068}}, the selected
protection under {{access-token-protection}}, and actor authorization
under {{actor-authorization}} and {{ACTOR-PROFILE, Section 8}}.
In addition, the API MUST:

* **Applicability:** Determine which paths require this profile from
  trusted resource configuration. Missing or malformed `act` MUST
  NOT select non-delegated processing on those paths.
* **Identity:** Require one `act` object with non-empty `iss` and `sub`
  and no nested `act`. Trust configuration MUST authorize the RAS to
  assert that IdP-qualified agent identity; `act.iss` need not equal the
  access-token issuer.
* **Protection:** Enforce the configured resource mode and all token
  confirmation claims. Validate DPoP under {{RFC9449}}, certificate
  binding under {{RFC8705}}, or permitted bearer use under {{RFC6750}}.
* **Authority:** Require non-empty `scope` with its defined type.
  Enforce user permissions and the actor gate; independent agent
  permissions on each data object are required only by local policy.

## Error Responses {#resource-errors}

Challenges and scope errors use the selected protection mechanism:
`DPoP` under {{RFC9449, Section 7.1}}, or `Bearer` under {{RFC6750}} for
bearer and mutual-TLS tokens. Missing or invalid required actor claims, or
unauthorized namespace assertions, use HTTP 401 with `invalid_token`.
Denial for a valid actor identity uses
HTTP 403 with `actor_unauthorized` under {{ACTOR-PROFILE, Section 8.2}}.
Actor denial MUST NOT use `insufficient_scope`. The API MUST NOT expose
actor-specific rejection details outside the trust domain.

# Authorization Server and Client Metadata {#metadata}

The delegated profile identifier is:

`urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`

It identifies RAS and client processing. IdP issuance and optional inputs
follow {{discovery}}; the URI makes no continuation capability claim.

## Authorization Server Metadata {#server-metadata}

Servers MUST publish {{RFC8414}} metadata as follows:

* **RAS:** Include both this URI and the base
  `urn:ietf:params:oauth:grant-profile:id-jag` in
  `authorization_grant_profiles_supported`.
  * Include `urn:ietf:params:oauth:grant-type:jwt-bearer` in
    `grant_types_supported` for this profile.
* **IdP:** Advertise Token Exchange in `grant_types_supported` and
  ID-JAG in `identity_chaining_requested_token_types_supported` under
  {{ID-JAG, Section 7.1}}.
* **Both:** Advertise supported client authentication methods and DPoP
  algorithms, including {{flow-configuration}}'s common capabilities.
  Where supported, publish the existing CIMD and mutual-TLS capability
  metadata defined by {{CIMD}} and {{RFC8705}}.

## Client Metadata {#client-metadata}

A client SHOULD advertise this profile URI in its authoritative client
metadata under {{ID-JAG, Section 8}}, including when supplied through
CIMD. Its `grant_types` MUST permit:

* `urn:ietf:params:oauth:grant-type:token-exchange` at the IdP.
* `urn:ietf:params:oauth:grant-type:jwt-bearer` at the RAS.

Advertising JWT bearer grant support does not waive this profile's
confirmation checks or its independently configured output protection.

## Discovery and Profile Selection {#discovery}

Before using the delegated path:

* The client and IdP MUST agree through trusted configuration on
  issuance support and any optional actor or refresh-token subject
  inputs. Generic JWT or authentication-method support is insufficient.
* The client and IdP MUST verify the RAS's profile advertisement. The
  client MUST also verify its JWT bearer grant support, the configured
  IdP support, the selected input, and compatible access-token protection.

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

A holder of a shared private key can present credentials issued for that
key. Agent isolation therefore requires platform issuance controls and
key-custody policy; an identity mapping alone does not provide it.

## Authorization Changes and Revocation {#status-changes}

Before issuance, the IdP MUST apply current binding and authorization
policy and reject an inactive agent or withdrawn binding once the change
has been applied. Cached policy data MUST have configured freshness
limits; stale data MUST NOT authorize issuance.

Cross-system disablement and revocation require the mechanisms in
{{lifecycle-gap}}. Without a signal or online check, issued tokens can
remain usable until expiration. This profile does not define propagation
of binding changes or revocation to downstream servers.

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
Instance and endorsement registrations remain with their separate drafts.

--- back

# Remaining Gaps and Coordination {#upstream-gaps}

This informative appendix records unresolved contracts and coordination
requests. It adds no conformance requirements. The assessed revisions
are WAG-00, ID-JAG-04, ICA-02, Actor Profile-00, SPIFFE OAuth-02,
ATTEST-11, WIT-02, and CIMD-02. Identification and Client
Attester Endorsement were assessed against their editor's copies dated
15 September 2026.

## Responsibility Boundaries {#responsibility-boundaries}

| Concern | Defined by |
|---|---|
| External identity to governed agent; delegated issuance and redemption | This profile, using the extension point in {{ID-JAG, Section 9.7}} |
| ID-JAG format and base grant processing | {{ID-JAG}} |
| Continuing access, continuation evidence, and chain lifecycle | {{ICA}}; federation composition remains separate work under {{continuation-sources}} |
| Actor object, current actor, and actor-aware resource policy | Selected rules of {{ACTOR-PROFILE}}, as specified in {{actor-construction}} |
| Base workload authentication and proofs | SPIFFE OAuth, WIMSE, and ATTEST |
| Client endorsement of attesters and AS acceptance | Future composition with {{ATTESTER-ENDORSEMENT}}; outside core conformance |
| Attested instance identity, continuity, and receiver scoping | {{INSTANCE}}; agent-resolution composition is future work |
| Self-acting workload grant | WAG composition in {{wag-flow}}; upstream grant changes in {{wag-gaps}} |
| Self-acting subject resolution and agent linking | This profile, {{wag-subject-resolution}} |
| Downstream instance context | {{INSTANCE}} defines the object; propagation through this flow is outside this revision |
| Agent provisioning and disablement signals | Future provisioning and lifecycle specifications |

## Operational Guidance {#operational-guidance}

Provisioning interfaces and administrative workflows are outside
conformance to this profile. Deployments can use provisioned links, a user linking flow, or
just-in-time account creation, subject to the identity-safety rules in
{{subject-linking}} and {{wag-subject-resolution}}.

Useful operational controls include:

* Authenticate the administrator or provisioning authority that changes
  a link; a user linking flow can instead verify control of both accounts.
* Authorize just-in-time creation by issuer and tenant. Avoid silent
  account merges or reactivation of disabled accounts.
* Keep ownership, group membership, and entitlements associated with the
  principal they describe. Agent ownership does not confer delegation.
* Audit link and binding changes. When using SCIM `externalId`
  {{RFC7643}}, retain its issuer and tenant context in the provisioning
  association. SCIM {{RFC7644}} and Agent resources {{SCIM-AGENT}} do not
  themselves define cross-system revocation.

## ICA Composition Requirements {#continuation-sources}

This is an extension agenda, not an implemented ICA composition.
{{ICA}} defines continuation evidence and lifecycle; a separate
federation composition would need to specify:

* **Actor mapping:** How ICA's authenticated-client identity corresponds
  to the Registered Agent resolved at the root. A shared client alone
  does not establish that equivalence.
* **Eligible source:** How the agent qualifies as the receiving workload
  or designated task actor. Holding a token for another service does not
  make the caller an eligible receiver ({{continuation-gap}}).
* **Binding continuity:** Which root Federation Binding and client
  association constrain the chain, and how withdrawal prevents another
  binding from sustaining or reviving it.
* **Subject and authority:** How each target resolves the original user
  and applies the chain authorization without transferring account links
  or expanding delegation.

That extension would select ICA's discovery, assertion acquisition,
proof, replay, and error rules rather than redefine them here.

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
grant, WAG-owned identifier registration, or WAG refresh exception.

## Bound ID-JAG Redemption {#bound-grant-coordination}

**Problem.** ID-JAG's Section 4.4 requires `jwt-bearer`, while its
bound-grant example uses `jwt-dpop`. The prose requires validation of
`cnf.jkt` and leaves access-token sender constraint to resource policy.

**Request to ID-JAG, coordinated with ICA.** Align the bound-grant example
with the normative grant type and distinguish grant-confirmation errors
from RFC 9449 proof and nonce errors. This profile uses RFC 7523 with
explicit confirmation processing under {{redemption}}; it introduces no
new grant type or dependency on JWT DPoP Grant.

## Calling-Agent Continuation {#continuation-gap}

**Problem.** ICA's access-token exchange serves the workload receiving a
call; its task mechanism depends on durable RAS task authorization. A
calling agent holding a token for a third-party API does not thereby
qualify for either source. Requiring the same governed actor does not
supply the missing authorization context.

**Request to ICA.** If general calling-agent continuation is supported,
define how the CAI establishes that caller's eligibility and binds it to
an accepted RAS authorization, including assertion acquisition and
revocation. {{continuation-sources}} records the separate federation
composition work. New exchanges remain available under
{{exchange-request}} without that extension.

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

## Attestation Extension Boundaries

### Instance-to-Agent Resolution {#instance-agent-resolution}

Instance-based agent resolution is outside core conformance. A future
composition with {{INSTANCE}} would need an approved mapping from the
validated (`iss`, `client_instance_id`) to a governed agent, with client,
receiver scope, grant continuity, and migration checks.

Such mappings can suit managed installations with durable enrollment.
Elastic serving replicas use platform JWTs identifying their governed
workload through {{platform-evidence-contract}}; no per-replica IdP
registration is required. Replicas sharing that identity remain the same
authorization principal.

### Client Attester Endorsement {#attester-endorsement-extension}

{{ATTESTER-ENDORSEMENT}} defines client endorsements constrained by AS
policy, including key selection, freshness, and withdrawal. A future
composition would use those rules for attester trust while preserving
this profile's independent Federation Binding and delegation checks.
Publishing `client_attesters` alone selects neither agent mapping nor
instance identification. This revision uses configured attester trust.

## Instance Context {#instance-identification}

**Problem.** A workload identity can span several replicas
{{SPIFFE-CONCEPTS}}. An identifier alone establishes neither continuity
nor enrollment or key replacement. Runtime identification does not by
itself make that runtime an authorization principal.

{{INSTANCE}} defines instance identity and continuity requirements.
Enrollment and key-replacement protocols remain outside both profiles.

**Remaining work for this consuming profile.** Any downstream
`client_instance` composition needs to define:

* Whether context describes the authenticated presenting instance or a
  represented upstream instance, and its validated association with the
  WAG subject or ID-JAG actor.
* Mapping, correlation scope, and replacement or preservation under
  Sections 7.1 through 7.3 of {{INSTANCE}}. Preserving already-forwarded
  context needs authenticated provenance and a finite hop limit.
* Authorized presenter or key changes, sender-constrained access tokens,
  and context-consumer validation and errors under
  Sections 7.2 through 7.5 of {{INSTANCE}}.

An output proof authenticates its presenter, not necessarily the instance
named in preserved context. This revision defines no downstream
instance-context composition.

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
