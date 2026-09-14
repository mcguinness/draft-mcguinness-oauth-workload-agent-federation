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
  RFC6749:
  RFC7519:
  RFC8693:
  RFC8725:
  RFC9449:
  RFC9700:
informative:
  IDENTITY-CHAINING: I-D.ietf-oauth-identity-chaining
  RFC9068:
  WAG: I-D.carleton-workload-authz-grant
  SPIFFE-CONCEPTS:
    title: "SPIFFE Concepts"
    target: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
    author:
      - org: SPIFFE
  RFC6755:
  RFC6838:
  ENTITY-PROFILES: I-D.mora-oauth-entity-profiles
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
--- abstract

This document defines how an identity provider resolves external
workload or platform evidence to a governed agent and applies policy
before authorizing downstream access. It distinguishes agent identity,
delegation, and instance context. Workload Authorization Grant is the
intended mechanism for self-acting access; Identity Assertion JWT
Authorization Grant and Actor Profile provide the basis for delegated
access. It defines the additional evidence, trust, and validation
requirements for agent federation using existing credential extension
points, and identifies grant changes that require upstream agreement.

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

## Intended Composition {#paths}

~~~
 Platform       Agent             IdP             RAS        API
    |-- evidence ->|               |               |          |
    |              |-- evidence -->|               |          |
    |              |               |-- resolve agent          |
    |              |               |-- authorize relationship |
    |              |<-- grant -----|               |          |
    |              |-------- grant + proof ------->|          |
    |              |<------- access token ---------|          |
    |              |------------- token + proof ------------>|
~~~

The diagram is an architectural target, not a complete wire protocol
specified by this revision. The intended outputs are:

| Situation | Grant owner | Authorization identity | Dependency status |
|---|---|---|---|
| Agent acts for itself | Workload Authorization Grant (WAG) {{WAG}} | Governed agent as subject; no delegated actor | IdP-issued, sender-constrained composition needs {{wag-gaps}} |
| Agent acts for a user | ID-JAG {{ID-JAG}} and Actor Profile {{ACTOR-PROFILE}} | User as subject; governed agent as actor | Direct mapped-actor composition needs {{actor-gap}} and {{id-jag-gap}} |

Federation owns the association from external evidence to the governed
agent and the policy decision about the requested access. It consumes
the grant formats, actor representation, credential proofs, and
metadata defined by their owning specifications.

## Current Scope and Dependency Status {#scope}

The identity-resolution and authorization requirements in
{{identity}}, {{inputs}}, and {{authorization}} are normative.
They include the Client Attestation profile in {{agent-evidence}}.
They do not define a complete token-endpoint flow for every input and
output. {{upstream-gaps}} is informative and records proposed changes,
their rationale, and observable closure criteria. Those proposals have
not been adopted by the referenced specifications.

This revision does not define:

* A new authorization grant, JWT type, token-type URI, or API token.
* A mandatory intermediate IdP access token for identity normalization.
* A new Client Attestation proof mode or a change to base ATTEST.
* Replacement WAG issuance, audience, refresh, or redemption rules.
* An enrollment, key-replacement, or instance-propagation protocol.

Existing mechanisms remain usable within their defined scope. For
example, SPIFFE OAuth can authenticate a JWT-SVID, and Actor Profile
can consume an eligible credential whose subject already identifies
the intended actor. Supporting either operation does not establish
support for the unresolved governed-agent composition.

A deployment selecting a grant path MUST apply its defining
specification, including its input validation, client authentication,
proof, and metadata requirements. Where a required composition is
undefined, this document supplies no interoperable fallback. In
particular, successful identity mapping does not authorize treating
an arbitrary signed JWT as a grant or actor credential.

## Responsibility Boundaries

| Concern | Owning work |
|---|---|
| External identity to governed agent; issuance policy | Agent Federation |
| Self-acting workload grant and its registrations | WAG |
| Who may act for whom; actor representation and chain processing | Actor Profile and consuming authorization profiles |
| ID-JAG input/output composition and downstream processing | ID-JAG |
| Base workload authentication and credential proofs | SPIFFE OAuth, WIMSE, and ATTEST |
| Agent evidence, attester trust, and credential selection for Federation | This profile, using existing credential extension points |
| Stable installation or execution identity | Identification |
| Agent ownership, groups, provisioning, and disablement signals | Provisioning and lifecycle work, coordinated with Federation |
| Enrollment, clone detection, verified key replacement | Platform evidence mechanisms initially |
| Interoperable model or runtime assurance | Deferred until producers and consumers agree on semantics |

Federation defines its own requirements where a base specification
already permits profiling or extension. For example, {{ATTEST, Section 13}} permits
profiles; {{agent-evidence}} defines this document's profile using that
facility and additional claims permitted by {{ATTEST, Section 4}}.

Changes to another specification's grant semantics, identifiers, or
actor-construction rules still require coordination. The proposals in
{{upstream-gaps}} explain those changes. Once agreed, this document can
reference the adopted rules and finish the corresponding composition.

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

## Requirements Added by Federation {#profile-requirements}

The following requirements concern the federation decision. Wire
requirements remain with the selected credential and grant profiles.

| Area | Federation requirement | Defined in |
|---|---|---|
| Trust | Approved credential authority and tenant context | {{identity}} |
| Identity | Exact, unambiguous mapping to an active Registered Agent | {{identity}} |
| Evidence | Validate the selected credential; distinguish client, agent, and key evidence | {{inputs}} |
| Shared-client ATTEST | Require signed `iss` and `attested_agent_id`; apply the configured mode, namespace, and failure rules | {{attest-gap}} |
| Attester trust | Intersect approved attester authority with client restrictions | {{trust-gap}} |
| Credential use | Apply the selected proof mode and explicit reuse/key-binding limits | {{credential-requirements}} |
| Authorization | Current binding, status, assignments, target, and scope policy | {{authorization}} |
| Delegation | Explicit authorization for the resolved agent to act for the user | {{delegation-approval}} |
| Attribution | Preserve issuer-qualified agent identity and subject/actor roles | {{agent-correlation}} |

No requirement in this table makes a proposed upstream claim,
identifier, or grant extension a supported wire feature.

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
| Client Attestation, agent has its own client | Validated attester and client identity | Client-to-agent mapping is explicit |
| Shared-client Client Attestation | Approved attester, client `sub`, and signed `attested_agent_id` | Federation extension defined in {{attest-gap}} |
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

The proposed subject-token and actor-token uses of platform evidence
are described in {{wag-gaps}} and {{actor-gap}}. This document does not
create an intermediate token to make those uses appear supported.

## Client Attestation Profile {#agent-evidence}

This section defines Federation requirements on top of {{ATTEST}}.
An IdP supporting this input MUST apply them in addition to ATTEST
validation. Support for each agent mode is OPTIONAL. An implementation
claiming a mode MUST implement its requirements below. These modes use
ATTEST's existing claim and profiling facilities.

### Profile Selection {#attest-selection}

The IdP MUST determine profile applicability from trusted configuration
for the Source Tenant, approved attester, and OAuth client. Before
accepting requests, that configuration MUST identify:

* Whether the client has its own Registered Agent or hosts several
  agents using the shared-client mode in {{attest-gap}}.
* The permitted attesters and the applicable Federation Bindings.
* The accepted ATTEST authentication methods and proof algorithms.

The client MUST be provisioned with the applicable mode and accepted
methods before using this input. An unauthenticated client identifier
can locate configuration, but MUST NOT establish its authority; the
IdP MUST confirm the client identity through ATTEST validation.
Presence or absence of an agent claim MUST NOT switch modes. A failed
shared-client request MUST NOT fall back to an own-client mapping.

This is the out-of-band profile-selection mechanism permitted by
{{ATTEST, Section 13}}. ATTEST metadata advertises its authentication
capabilities; it does not by itself advertise this Federation profile.
No new discovery field is needed for these configured relationships.

### Agent with Its Own Client

The IdP MUST authenticate the client under ATTEST and resolve the
approved attester/client binding to one Registered Agent. The `sub`
continues to identify the OAuth client. An `attested_agent_id` claim,
if present, MUST NOT override the configured own-client binding.

### Agent Behind a Shared Client {#attest-gap}

This document defines the `attested_agent_id` JWT claim for agent
evidence in a Client Attestation. Its value is a non-empty,
case-sensitive string identifying one agent in the namespace of the
attester and OAuth client. The attester MUST NOT reassign that value
to a different agent within that namespace.

The claim asserts that the Client Instance represented by the
attestation is authorized to authenticate as that agent using the
attestation's confirmation key. It does not assert user delegation,
resource authority, or an independently verified execution identity.
Its value is an external identifier, not necessarily the Registered
Agent identifier assigned by the IdP.

An attester issuing a shared-client attestation for this profile MUST:

* Include `attested_agent_id` and an `iss` identifying the attester in
  the integrity-protected claims set of the Client Attestation JWT.
* Use a non-empty StringOrURI value for `iss` that matches the approved
  attester identifier in the Federation Binding.
* Retain the OAuth client identifier in `sub` and the Client Instance
  Key in `cnf.jwk`, with their ATTEST meanings.

The IdP MUST:

1. Validate the Client Attestation and the selected ATTEST proof before
   using its agent claim. An agent identifier carried only in the
   request or proof is not attester-authenticated agent evidence.
2. Validate `iss` and `attested_agent_id` as required above. The key
   validating the attestation MUST be authorized for that exact `iss`;
   the claim MUST NOT authorize discovery of a new attester.
3. Resolve the exact tuple (`iss`, `sub`, `attested_agent_id`) through
   an enabled Federation Binding to exactly one active Registered
   Agent and Source Tenant. If an attester/client pair serves several
   platform tenants, its agent identifiers MUST distinguish them;
   otherwise the deployment MUST use distinct attester namespaces.
4. Use the confirmation key from that same validated attestation for
   ATTEST proof validation. Claims from separate attestations MUST NOT
   be combined to construct an agent identity or key association.

A missing, empty, or incorrectly typed required claim, an unapproved
attester, or an invalid attestation/proof MUST cause rejection. For a
profile-specific claim validation failure, the IdP MUST return
`invalid_client_attestation`; other ATTEST failures retain ATTEST's
error and challenge processing. A well-formed attestation with no
active authorized binding fails the Federation decision and uses the
consuming grant's applicable error, not a fabricated proof failure.

A base ATTEST implementation can ignore this additional claim. Such an
implementation does not support shared-client Federation resolution.
The claim is required by this selected profile, not by base ATTEST.

### Proofs, Renewal, and Compatibility {#attest-proof}

The configured ATTEST method MUST govern proof processing. In
`attest_jwt_client_auth_dpop` mode, the client and IdP MUST use ATTEST's
combined mode, including its key-matching and nonce rules. In
`attest_jwt_client_auth` mode, they MUST use the ATTEST PoP JWT; any
accompanying DPoP proof retains its separate role under ATTEST.

The IdP MUST NOT treat a separately proven DPoP key as endorsed by the
attester solely because it accompanies a valid attestation. When the
selected grant policy requires an attested output key, the IdP MUST
verify that it matches the attestation's confirmation key. Unsupported
method or key combinations MUST fail; they MUST NOT trigger another
authentication mode or skip a required proof.

For each use of a renewed or reused attestation, the IdP MUST reapply
profile validation and current Federation policy. A replacement key
requires a valid attestation authorizing that key for the named agent.
Neither the previous key nor an unchanged agent identifier alone
establishes that authorization. Attester enrollment and evidence
collection remain deployment mechanisms.

The additions to ATTEST are explicit:

| Item | Federation requirement |
|---|---|
| Applicability | Trusted, provisioned mode selection; no claim-triggered fallback |
| Shared-client claims | `iss` and `attested_agent_id` are REQUIRED in the attestation |
| Agent resolution | Exact attester/client/agent tuple and active Federation Binding |
| Trust | Attester authority and client restrictions in {{trust-gap}} |
| Proof and renewal | Key-role and current-policy checks in this section |

ATTEST's `typ`, client `sub`, proof formats, transport, metadata, and
refresh-token binding remain unchanged. This profile does not require
`iat` in the Client Attestation or introduce a proof method. Grant
issuance and refresh permission remain with the consuming profile.

### Attester Trust and Client Restrictions {#trust-gap}

The IdP MUST configure which attesters may assert which client and
agent namespaces in each Source Tenant. Signature verification alone
MUST NOT grant an attester authority over every Registered Agent.

A client administrator MAY restrict the acceptable attesters through
the authenticated registration or configuration process. Such a
restriction is the client's endorsement for this profile; it is not a
new ATTEST message. The IdP MUST:

* Authenticate the party configuring the restriction and verify its
  authority over that client registration.
* Accept an attester only within both the IdP's approved trust scope
  and any configured client restriction. An empty intersection MUST
  prevent acceptance; absence of a client restriction leaves the
  IdP's approved set in effect.
* Apply approved changes using the freshness rules in {{status-changes}}.
  Request-supplied metadata MUST NOT expand or replace the approved set.

These rules are sufficient for configured deployments. Interoperable
discovery of client restrictions, if later needed, can be defined as a
separate extension without changing ATTEST or blocking this profile.

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
composition and discovery work is listed in {{credential-gap}}.

## SPIFFE X.509-SVID {#spiffe-input}

X.509-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.2}}.
The IdP MUST validate the certificate with the configured trust-domain
anchors and resolve the authenticated SPIFFE ID through {{identity}}.
Client identity and TLS proof checks remain those of SPIFFE OAuth.

X.509-SVID supplies authenticated connection evidence rather than a
JWT to place in `subject_token` or `actor_token`. An interoperable way
to use that evidence in grant issuance needs {{x509-gap}}. This
profile does not require a newly minted adapter access token to bridge
that representational gap.

## SPIFFE WIT-SVID {#wit-input}

WIT-SVID client authentication follows {{SPIFFE-OAUTH, Section 3.3}}
and {{WIT}}. The IdP MUST validate the credential and required proof,
use trust anchors authorized for the trust domain in `sub`, and
resolve the exact identity through {{identity}}.

The WIT's confirmation key and the authentication proof retain their
specified roles. DPoP alone MUST NOT substitute for a required WIT
or attestation proof. Federation applies the credential-use requirements
in {{credential-requirements}}; any new proof mechanism needs its own
specification and registrations as described in {{credential-gap}}.

## Credential Use Requirements {#credential-requirements}

For each accepted credential input, the IdP MUST configure its role,
required proof mechanism, and the assurance required for an output key.
It MUST validate each proof under the selected mechanism; support for
one proof mode MUST NOT imply support for another. This is a Federation
composition requirement, not a request to change the base credentials.

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
their specified meanings. When metadata does not distinguish the
required composition, support MUST be established through trusted
configuration before use. A client MUST NOT infer an authentication-
method metadata value from a JWT assertion-type URI. Further generic
discovery or proof mechanisms are separate work in {{credential-gap}}.

# Federation Authorization {#authorization}

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
requirement. Completing the upstream composition is necessary for
that path; a successful mapping does not close the gap.

Request and response parameters, scope/resource claims, errors, and
refresh behavior follow the consuming grant specification. This
document defines no alternative OAuth errors and does not override
RFC 8693's default error with a profile-local code. Authentication and
proof failures retain their mechanism-specific errors.

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

Delegation representation and chain processing follow Actor Profile
and the consuming authorization profile. Federation does not add an
actor merely because a runtime was authenticated. Extending an
existing actor chain requires the applicable delegation profile;
agent-to-agent chain construction is outside this revision.

## Canonical Agent Attribution {#agent-correlation}

The intended governed identity is the pair of IdP namespace and
Registered Agent identifier. In self-acting access it identifies the
subject; in user-delegated access it identifies the agent actor.
The output mapping needed to express that identity using WAG or
ID-JAG is addressed in {{wag-gaps}} and {{actor-gap}}.

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

# Upstream Gaps and Proposed Changes {#upstream-gaps}

This section is informative. It is the coordination agenda for this
profile, not an extension registry or a second set of grant rules.
The baseline revisions assessed are WAG-00, ID-JAG-04, Actor Profile-00,
SPIFFE OAuth-02, and ATTEST-11. Federation requirements using existing
extension points are defined in {{inputs}}; they are not awaiting
changes to those base documents. Each request here identifies its owner,
why Federation needs it, and how to determine whether the gap is
closed. Changes require agreement in the owning specification.

| Gap | Proposed owner | Consequence until closed |
|---|---|---|
| IdP-issued WAG through exchange | WAG; Federation supplies identity resolution | No complete governed-agent self-acting exchange profile |
| WAG typing, token type, and discovery | WAG and identity chaining | No locally assigned WAG identifiers or advertised extension |
| Sender-constrained WAG and redemption | WAG, coordinated with DPoP and ID-JAG | No claim that base WAG enforces the desired key binding |
| Authority bounds and continuing access | WAG and ID-JAG | Existing claim and refresh rules remain unchanged |
| Direct credential to governed actor | Actor Profile, consumed by ID-JAG and Federation | No mandatory normalization access token |
| X.509-SVID as issuance evidence | SPIFFE OAuth and consuming authorization profiles | No JWT fabricated to stand in for connection evidence |
| Additional proof mechanisms and generic discovery | Separate credential extensions, coordinated with their consumers | Current modes and Federation requirements remain usable |
| Instance context | Identification and a consuming profile | No instance claims or propagation rules here |
| Provisioning and disablement signals | Provisioning and lifecycle specifications | No guarantee of immediate cross-system revocation |

## WAG: IdP Issuance and Grant Semantics {#wag-gaps}

WAG is the intended self-acting grant. Its current deployment model
centers on a platform issuer, but {{WAG, Section 5}} already anticipates
an enterprise IdP issuing the grant through Token Exchange. That
observation is not a complete issuance profile. The requests below
make that composition explicit without creating a different grant.

### IdP Issuance and Identity Ownership {#wag-issuance-gap}

**Problem.** A platform identifies `support-bot-7`; the IdP governs
that workload as `agent-42`. The RAS trusts the IdP, not every platform
that can supply evidence. Issuer placement determines who is
accountable for the subject and attributes, and which namespace the
RAS uses for policy.

**Proposed change in WAG.** Define the IdP as a grant issuer distinct
from the evidence issuer. Specify the issuance contract with Token
Exchange: accepted subject evidence categories, client-authentication
requirements, requested output identification, and success/error
processing. Leave external-to-governed identity resolution to
Federation. Make clear that the resulting subject is asserted in the
grant issuer's namespace; platform identifiers are evidence for that
decision, not automatically downstream subject identifiers.

**Closure criteria.** Two independent implementations can issue and
redeem the same WAG for a configured governed agent using different
external evidence sources. They agree on the issuer, subject, tenant
context, client role, and authoritative source of agent properties.
No extra identity-normalization access token is required solely to
express the mapped subject.

### Identifiers and Capability Discovery {#wag-identifiers-gap}

**Problem.** WAG-00 does not define the token-type URI and explicit JWT
typing needed to select this composition. A generic signed JWT cannot
signal its validation contract. Earlier local identifier proposals
would make Federation the de facto owner of another draft's format.

**Proposed change in WAG.** Choose and register the WAG token-type URI
under {{RFC6755}} and an explicit JWT media type under {{RFC6838}}, if
those are the agreed discriminators. Define their use in exchange,
JWT validation, and redemption. Coordinate output advertisement with
{{IDENTITY-CHAINING}} and distinguish support for any optional bound
grant variant from mere acceptance of an issuer.

**Closure criteria.** WAG contains the complete registration requests
and associated processing rules. Clients can discover the supported
issuance/redemption composition without Federation assigning a URI,
a JWT type, or an authentication-method name on WAG's behalf.

### Sender Constraint, Audience, and Replay {#wag-binding-gap}

**Problem.** WAG-00's bearer model does not provide the bound-grant
contract needed when a harness key is intended to control redemption.
Its audience guidance permits forms that need a common selection for
IdP-to-RAS federation. Proof freshness and grant replay are different
checks.

**Proposed change in WAG, coordinated with ID-JAG and DPoP.** Define:

* How issuance validates the presenter's key and records its binding
  in the grant, including the relationship to any credential-bound key.
* Whether the bound variant uses `cnf.jkt`, and how a RAS verifies the
  corresponding DPoP proof and issues a sender-constrained access token.
* An agreed audience form. Federation proposes one RAS issuer
  identifier, matching the ID-JAG composition, rather than multiple
  issuer and token-endpoint audiences.
* The redemption grant type, client-authentication requirements,
  nonce challenges, proof errors, and grant-error behavior.
* Whether redemption is single use. If so, define atomic consumption,
  replay-cache scope, retention through expiry plus clock skew, and
  retry behavior after a nonce challenge.

**Closure criteria.** A stolen grant cannot be redeemed without its
binding key; wrong-audience and cross-issuer key substitutions fail;
concurrent redemptions obey the agreed replay rule; nonce retries do
not accidentally consume a grant. These checks are defined in WAG,
not inherited merely because Federation recommends DPoP.

### Authority Bounds and Refresh {#wag-lifecycle-gap}

**Problem.** The IdP and RAS need to agree what authority the grant
conveys and what remains a local RAS decision. WAG's current refresh
prohibition also affects continuing self-acting workloads; Federation
cannot change it while claiming WAG compatibility.

**Proposed change in WAG, coordinated with ID-JAG.** Decide how resource
and scope limits are represented and enforced, including absent
claims, narrowed scopes, and additional authorization details. Define
whether a consuming profile can require explicit `scope` and `resource`
without changing their meanings. Keep RAS authorization independent:
validated grant claims set a ceiling, not an obligation to issue.

Review the refresh prohibition upstream. If retained, explain why a
fresh WAG is needed for continuing access. If changed, define the
client and sender bindings, current-status/delegation checks, and
revocation behavior before enabling refresh. Compare the two-request
direct issuance/redemption path with any additional credential renewal;
separate grant lifetime from downstream access-token lifetime.

**Closure criteria.** Issuer and RAS tests cover authority reduction,
missing/unsupported constraints, continuing access, and disablement.
Until WAG changes its rule, its prohibition remains in effect; this
document supplies no alternate refresh permission.

## Actor Profile: Direct Mapped Actors {#actor-gap}

{{ACTOR-PROFILE, Section 6.3}} defines direct client,
workload, and JWT access-token inputs. Its processing uses the
credential's subject as the actor. A shared-client attestation may
instead identify the hosting client, and an external workload subject
may differ from the governed agent identifier.

**Problem.** For a user request, the intended result is the user as
`sub` and `(IdP namespace, agent-42)` as the actor. Copying an external
`sub` can identify the wrong principal. Requiring a special IdP access
token merely to carry `agent-42` hides the missing mapping rule and
adds an issuance step to every uncached delegated flow.

**Proposed change in Actor Profile.** Define a consuming-profile
extension point that accepts validated external evidence and an
authorized canonical-principal resolution before actor construction:

1. Validate the actual credential and its proof under its own type;
   a generic JWT token type does not identify an evidence class.
2. Resolve exactly one governed actor using an approved mapping.
   Preserve the distinction between external credential authority,
   OAuth client identity, and the actor's output namespace.
3. Define how the resolved identifier supplies `act.sub` and how
   `act.iss` identifies that identifier's namespace. Specify precisely
   how this composes with the existing subject-copying rules.
4. Reject inconsistent evidence or a mapping that changes an already
   established actor without the required authorization. Do not use
   this extension to rewrite preserved actor chains silently.
5. Specify errors and capability signaling so a client can distinguish
   mapped evidence support from generic JWT actor-token support.

Federation would supply the approved mapping and delegation decision;
Actor Profile would own the representation and construction contract.
This does not make client authentication alone an actor credential.

**Closure criteria.** Tests cover an own-client agent, an imported
workload, a shared-client agent, and an already canonical actor
credential. Each produces the same issuer-qualified governed actor
when authorized, without forcing an intermediate token. Missing
shared-agent evidence and ambiguous mappings fail. An existing
eligible JWT access token under {{RFC9068}} remains usable where the
consuming profile already supports it; Federation does not mandate
issuing a new token class.

## ID-JAG: Consuming the Mapped Actor {#id-jag-gap}

{{ID-JAG, Section 9.7}} leaves actor-token processing to extensions.
The composition with {{actor-gap}} therefore belongs in ID-JAG and its
Actor Profile integration, not in a Federation-specific adapter flow.

**Proposed change.** Specify the user-subject and direct actor-evidence
combinations, required client authentication, delegation checks, proof
binding, and actor preservation at redemption. Decide whether one JWT
can serve as both client authentication and actor evidence, and how
exact-token matching is enforced for each applicable input. Keep the
ID-JAG audience rule authoritative; the token-endpoint audience in
Actor Profile examples does not override it.

Also settle capability composition:

* `actor_profile_token_exchange` describes role-specific input/output
  token types using its `subject_token_types_supported`,
  `actor_token_types_supported`, and `requested_token_types_supported`
  members.
* `identity_chaining_requested_token_types_supported` advertises grant
  outputs. Define how the two signals agree for delegated ID-JAG,
  without requiring unrelated output arrays to be identical.
* Generic `jwt` actor support alone does not advertise governed-agent
  mapping, a shared-client extension, or every workload proof mode.

**Closure criteria.** An implementation can determine support for the
actual user-input/actor-input/output combination and produces ID-JAG
with the intended user, governed actor, client, and presenter key.
Unsupported combinations fail explicitly rather than triggering a
hidden acquisition round trip or omitting the actor.

Actor Profile recommends `act.sub_profile`. Federation does not turn
that recommendation into a mandatory classification claim. Its
unclassified-actor rules still apply when omitted. Entity Profiles
{{ENTITY-PROFILES}} remains a transitive normative dependency of
Actor Profile; bibliography placement here does not remove it.

## X.509-SVID: Connection Evidence in Grant Issuance {#x509-gap}

**Problem.** Mutual TLS proves the identity and key represented by an
X.509-SVID, but the certificate is not a JWT actor token. An OAuth
client identifier alone does not state which governed actor a
Token Exchange request intends to introduce. A separate DPoP key can
also differ from the TLS authentication key.

**Proposed change in SPIFFE OAuth and consuming authorization profiles.**
Define how authenticated connection evidence participates in
self-acting and delegated issuance. Choose an explicit presentation
or request-binding mechanism for the acting principal and specify its
relationship to any `subject_token`, `actor_token`, or sender key.
Preserve the distinction between authenticating a client and
introducing a delegated actor.

**Closure criteria.** Two implementations can process the X.509-SVID
path without fabricating a JWT from the certificate or requiring a
Federation-specific access token. Tests include a changed TLS
credential, a different DPoP key, wrong workload identity, and absent
actor evidence. If an upstream specification ultimately selects an
intermediate credential, it owns that credential's semantics and
lifecycle; Federation consumes that result.

## Additional Credential Mechanisms and Discovery {#credential-gap}

{{agent-evidence}} defines the shared-client attestation extension,
proof selection, and attester restrictions in this document.
{{credential-requirements}} defines how Federation uses bearer and
key-bound evidence using the existing credential mechanisms.

**Remaining problem.** Existing metadata may not identify every
credential/grant combination. A deployment may also require stronger
holder evidence than a bearer JWT-SVID or platform JWT supplies. A
first-use cache cannot authenticate the first claimant and can reject
replicas that receive identical cached credentials.

**Possible separate work.** If interoperable discovery beyond trusted
configuration is needed, define the relevant capability and registration
in a credential extension or consuming profile. If a new proof mechanism
is needed, define its evidence, key-binding assurance, replay protection,
renewal behavior, and registrations through the base specification's
extension facilities.

For WIT-SVID, any additional ATTEST integration needs an explicit
credential/proof contract. Existing WIT-SVID authentication under SPIFFE
OAuth and WIMSE remains usable; an ATTEST method name alone does not
advertise every such composition.

**Closure criteria.** Independent clients can identify the added
capability and its assurance. Tests cover unsupported combinations,
credential theft, key mismatch, and reuse across replicas. Changes to
base credential semantics require agreement with their owners; new
consumer requirements belong in the consuming profile.

## Identification and Context Propagation {#instance-identification}

Identification owns stable installation and execution identifiers.
Continuity is asserted under trusted evidence rules; an identifier does
not establish continuity or provide enrollment and key replacement.
SPIFFE permits a workload to span multiple running instances
{{SPIFFE-CONCEPTS}}, so native workload identity does not automatically
distinguish replicas.

A consuming profile needs to identify whose instance is described and
what happens during exchange. The intended associations are:

| Situation | Authorization representation | Optional future context |
|---|---|---|
| Agent acts for itself | Governed agent subject | Instance of that subject |
| Agent acts for a user | User subject; governed agent actor | Instance executing as that actor |
| Restart or replica replacement | Authorization identity unchanged | New execution identity under evidence rules |
| Agent delegates to another agent | Actor relationship changes under a delegation profile | Context follows the new actor |
| Execution receives independent authority | Execution may be subject or actor under a specialized profile | Defined by that profile |

The required upstream work is to specify accepted instance evidence,
continuity and replacement rules, claim placement, and whether context
is retained, replaced, or omitted at each exchange. This document does
not define `client_instance_id`, `client_instance`, or an instance-proof
protocol. {{RFC8693, Section 4.1}} expresses delegation through `act`;
it does not require every authenticated runtime to become an actor.

## Provisioning, Properties, and Disablement {#lifecycle-gap}

**Owners:** provisioning and lifecycle specifications, coordinated with
Federation and grant consumers. SCIM Agent resources {{SCIM-AGENT}}
and {{RFC7644}} are possible building blocks, not a complete status
propagation contract.

**Problem.** A new or disabled governed agent must be correlated across
IdP and RAS records. Group and ownership changes affect authorization;
issuing a short-lived grant does not revoke an already issued access
or refresh token.

**Proposed change.** Define issuer/tenant-qualified record correlation,
authoritative property ownership, update ordering, freshness, and
validated disablement or assignment-withdrawal signals. Decide what
receivers do with outstanding tokens and how missed events recover.
Enrollment, clone detection, and verified key replacement initially
remain platform evidence mechanisms. Model/runtime assurance needs
separate work only after producers and consumers agree on semantics.

**Closure criteria.** Tests demonstrate how an applied disablement
blocks new issuance and refresh, how receivers handle stale or missed
updates, and which outstanding tokens can remain valid. The profile
can state a measurable propagation guarantee rather than promise
immediate revocation from an unspecified event channel.

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

The shared-client profile relies on the attester to verify the agent
affiliation and key authorization asserted by `attested_agent_id`.
Its signature protects that assertion; it does not independently prove
the underlying platform evidence. If several agents share a private
key, its holder can present any valid attestation issued for that key.
Deployments requiring isolation between those agents need separate key
control and attester policy that enforces it.

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

Mapping can keep platform-local identifiers out of downstream grants,
but that privacy benefit depends on the agreed output namespace rules.
Federation does not silently rewrite Actor Profile identifiers to
create pairwise identities. Such a transformation needs coordination
with the relevant authorization profile.

Instance context can increase correlation further. Any consuming
profile introducing it needs purpose limits, retention guidance, and
clear rules about whose activity it describes.

# IANA Considerations {#iana}

## JSON Web Token Claim Registration

This document requests registration of the following claim in the
"JSON Web Token Claims" registry established by {{RFC7519, Section 10.1}}:

* Claim Name: `attested_agent_id`
* Claim Description: Identifier of an agent that the attested Client
  Instance is authorized to authenticate as, scoped to the attester
  and OAuth client.
* Change Controller: IETF
* Specification Document(s): {{attest-gap}} of this document.

This is a Federation extension claim carried in a Client Attestation;
it does not modify ATTEST's registry entries or base validation rules.
WAG identifiers and any new generic proof or discovery registrations
remain with their defining specifications. This document requests no
new grant type, authentication method, or proof method.

--- back

# Supporting Material {#supporting-material}

The upstream proposals and closure criteria are contained in this
document. The repository provides informative
[deployment scenarios](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md),
[interoperability cases](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/interoperability.md), and
[a coordination index](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/coordination.md).
They do not complete unresolved wire protocols or add conformance rules.

RFC Editor: Remove this appendix and repository links before RFC
publication, or replace them with stable informative references.

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
