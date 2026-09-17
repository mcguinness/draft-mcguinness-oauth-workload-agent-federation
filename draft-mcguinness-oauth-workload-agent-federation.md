---
title: "OAuth 2.0 Profile for Governed Agent Federation"
abbrev: "Governed Agent Federation"
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
  RFC6749:
  RFC6750:
  RFC6901:
  RFC7517:
  RFC7519:
  RFC7523:
  RFC7662:
  RFC8414:
  RFC8693:
  RFC8705:
  RFC8707:
  RFC8725:
  RFC9068:
  RFC9396:
  RFC9449:
  RFC9700:
informative:
  EMA:
    title: "Enterprise-Managed Authorization"
    target: https://github.com/modelcontextprotocol/ext-auth/blob/main/specification/stable/enterprise-managed-authorization.mdx
    author:
      - org: Model Context Protocol
  AUTHZEN:
    title: "Authorization API 1.0"
    target: https://openid.net/specs/authorization-api-1_0.html
    author:
      - org: OpenID Foundation
  AROP:
    title: "AuthZEN Access Request OAuth Profile - Draft 1"
    target: https://github.com/openid/authzen/blob/main/profiles/authzen-access-request-oauth/authzen-access-request-oauth-profile-1_0.md
    author:
      - name: Karl McGuinness
  AWS-TOKEN-CLAIMS:
    title: "Understanding token claims"
    target: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound_token_claims.html
    author:
      - org: Amazon Web Services
  AWS-AGENT-IDENTITY:
    title: "Separate agent and human user permission"
    target: https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec03-bp02.html
    author:
      - org: Amazon Web Services
  AWS-AGENTCORE-OBO:
    title: "On-behalf-of token exchange with AgentCore Identity"
    target: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/on-behalf-of-token-exchange.html
    author:
      - org: Amazon Web Services
  AWS-WORKLOAD-TOKEN:
    title: "Get workload access token"
    target: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/get-workload-access-token.html
    author:
      - org: Amazon Web Services
  INSTANCE:
    title: "Client Instance Identification for Attestation-Based Client Authentication"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-id/draft-mcguinness-oauth-client-instance-id.html
    author:
      - name: Karl McGuinness
    date: 2026-09-15
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-instance-id
  ATTESTER-ENDORSEMENT:
    title: "OAuth 2.0 Client Attester Endorsement"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-client-attesters/draft-mcguinness-oauth-client-attesters.html
    author:
      - name: Karl McGuinness
    date: 2026-09-15
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-attesters
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

This document defines how an identity provider resolves external
workload identities to stable enterprise-governed agent principals and
authorizes OAuth clients to exercise them. Resource systems consume
the governed identity without interpreting the original workload
credential. The profile uses existing credentials and defines no new
workload credential format.

For user-delegated access, it profiles the Identity Assertion JWT
Authorization Grant (ID-JAG), carrying the user as subject and the
Governed Agent as actor, with SPIFFE JWT-SVID as the common
interoperability input. Two adoption profiles share the governance
requirements; bound governed agent access additionally requires
sender-constrained grants. For self-acting access, it defines identity
and linking requirements intended for composition with the Workload Authorization
Grant (WAG). This revision does not define or claim conformance to a
WAG wire profile.

--- middle

# Introduction

Agent platforms establish workload identities. Enterprises govern
stable authorization principals. Resource systems need to recognize
those principals without understanding every platform's credentials.
This document defines how an identity provider (IdP) resolves external
workload identity to a Governed Agent, separately authorizes OAuth
client use and user delegation, and carries the governed identity into
the resource domain.

Four independent relationships establish that contract:

| Question | Relationship |
|---|---|
| What enterprise agent does this workload represent? | Identity Binding |
| May this OAuth client exercise that agent through this binding? | Client Association |
| May this agent act for this user toward the requested target and authority? | Delegation Authorization |
| What resource-local principal represents the IdP-qualified agent? | Governed Agent Attribution |

Workload credentials are federation inputs; downstream authorization
identifies the IdP-governed principal. The resource authorization server
(RAS) translates the user identity into its local namespace, preserves
the issuer-qualified agent identity, and correlates that agent with a
local authorization record. External credentials, execution environments,
and OAuth clients can change without changing the governed identity.

Existing specifications leave that mapping open. {{RFC8693}} defines
`act`, while {{ID-JAG, Section 9.7}} leaves actor-token validation,
authorization, and representation to extensions. {{ATTEST}} and
{{SPIFFE-OAUTH}} authenticate OAuth clients, not the agents a shared
client serves.

The federation model ({{model}}) is realized here as a complete delegated
ID-JAG profile ({{delegated-flow}}). SPIFFE JWT-SVID provides a common
interoperability input; supported alternatives use the same identity
and authorization model ({{optional-inputs}}). Self-acting access remains an informative
future composition with WAG ({{wag-flow}}).

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth and Token Exchange terms follow {{RFC6749}} and {{RFC8693}}.
Client Attestation terminology follows {{ATTEST}}.

## Roles

Agent Platform (the platform):
: The environment that runs agents. It supplies verifiable workload
  evidence from its own or an approved external credential authority and
  can implement the OAuth client that obtains access for an agent.

Client:
: Software making OAuth requests for an agent. It authenticates as an
  OAuth client and presents the evidence, target, and proofs for the
  selected grant flow. One client registration can serve several agents;
  client authentication does not establish which Governed Agent is
  acting.

Identity Provider (IdP):
: The OAuth authorization server that resolves external evidence to a
  Governed Agent, checks the permitted client and acting relationship,
  and issues a grant naming that agent as subject or actor.

Resource Authorization Server (RAS):
: The OAuth authorization server that validates the grant, resolves its
  identities, applies local policy, and issues an access token for its
  resources.

API:
: The OAuth resource server that accepts the access token and enforces
  the acting relationship and proof binding it carries.

One service can implement several roles.

## Terms {#terms}

Governed Agent:
: A stable, non-human authorization principal in the IdP's namespace
  representing a workload or agent under its governance. Its identity
  is independent of the external credentials, execution environments,
  and OAuth clients used to obtain authorization for it.

Workload:
: An external computational principal identified by accepted workload
  evidence. It can span multiple running instances; its identity does
  not necessarily distinguish executions. An Identity Binding resolves
  that external identity to a Governed Agent.

Identity Binding:
: An approved association from an external credential authority and
  exact external workload identity to one Governed Agent, administered
  in a Governance Tenant. It is the identity-federation relationship.

Client Association:
: An approved permission for an authenticated OAuth client to use a
  Governed Agent through the selected Identity Binding, flow, and actor
  credential class. The permission can cover one binding or an explicitly
  authorized set of bindings under {{identity-binding}}. It is an
  authorization-policy relationship, independent of identity resolution.

Issuer-bound presenter key:
: A key the credential issuer has attested belongs to the workload,
  such as a Client Attestation's confirmation key. It shows that the
  credential authority authorized the key.

Request proof key:
: A key the presenter proves in the request without issuer attestation,
  as with DPoP accompanying bearer evidence. It shows possession alone
  ({{credential-requirements}}).

Grant proof key:
: The DPoP key proven when requesting an ID-JAG and bound into that
  grant for redemption. A bearer JWT-SVID does not authorize this key;
  any association with an issuer-bound presenter key follows the
  selected input profile.

Governance Tenant:
: The IdP tenant within whose governance domain the Governed Agent
  exists and is administered. The Governed Agent identifier remains
  qualified by the IdP issuer ({{canonical-identity}}), not by the
  tenant.

External Tenant:
: The platform tenant, if any, that qualifies the external workload
  identity. It is expressed in the credential's issuer or subject
  namespace and never substitutes for the Governance Tenant.

Target Tenant:
: The tenant at the RAS in which the agent or user is authorized.

Where the meaning is clear, this document says agent for Governed
Agent.

# Federation Model {#model}

The IdP controls Identity Bindings, Client Associations, and delegation
authorization. The RAS controls local principal attribution and
authorization, using trusted provisioning from the IdP or an authorized
directory connector where applicable.

Establishing one relationship MUST NOT be treated as establishing
another. A local principal link identifies the agent; resource policy
still determines whether to accept its delegated access.

~~~
 Platform namespace     IdP namespace        Resource namespace

 workload-7 ----------> agent-42 ----------> service-principal-42
         Identity Binding      Governed Agent Attribution

 OAuth client -- Client Association --> permission to use binding
 agent-42 -- Delegation Authorization --> authority to act for user
~~~

External workload identity, Governed Agent identity, and OAuth client
identity are distinct. Identity Binding establishes the agent identity;
Client Association authorizes client use through the binding, flow,
and credential class. Its coverage is explicit under {{identity-binding}}.

The IdP is the authority for the Governed Agent: the ID-JAG's `act.iss`
equals its `iss`, and `act.sub` comes from the IdP's mapping rather than
forwarding the external subject. The RAS needs no platform-specific
credential validation or workload resolution. An existing service
principal can represent the agent locally without replacing its
IdP-qualified identity ({{agent-correlation}}).

Tokens and grants belong to the authorized user, agent, client, tenant,
resource, and authority context. A shared client or matching scope alone
MUST NOT permit reuse across those contexts ({{client-token-reuse}}).

## Evidence Roles {#inputs}

The IdP MUST validate a credential according to its configured type
before using it for identity resolution; a generic JWT token-type URI,
an unverified header, or a caller-supplied claim MUST NOT select a
weaker validation path or establish an Identity Binding. Unrecognized
request parameters and JWT claims follow {{RFC6749, Section 3.2}} and
{{RFC7519, Section 4}}.

The IdP MUST distinguish three roles of evidence and MUST NOT substitute
one for another:

* **Client authentication:** evidence authenticating the OAuth client.
* **Agent resolution:** resolution of validated external workload
  evidence through an Identity Binding to exactly one Governed Agent.
* **Key possession:** proof that the presenter controls a key, with the
  binding semantics of the proof mechanism.

The distinction between an issuer-bound presenter key and a request
proof key ({{terms}}) determines what a proof establishes.

The same credential can serve client authentication and agent resolution
without making the client and agent the same principal. Successful
client authentication MUST NOT imply successful agent resolution, and
successful agent resolution MUST NOT imply permission for the
authenticated client to exercise that agent.

## Canonical Identity and Tenant Boundaries {#canonical-identity}

The Governed Agent identifier MUST be unique and non-reassignable
within the IdP issuer's namespace. It need not equal an external
subject, OAuth client identifier, SPIFFE ID, display name, or instance
identifier. Restarting an execution, replacing a replica, or rotating
a key does not by itself create a new authorization principal.

A transfer to a different Governance Tenant under a different
administrative authority MUST create a new Governed Agent identifier
and MUST NOT automatically carry forward delegations or RAS principal
links. Renaming a tenant or changing an owner within the same governance
domain does not by itself change the principal. This revision defines
no cross-tenant identity migration protocol.

Multiple Identity Bindings MAY resolve distinct external workload
identities to the same Governed Agent when the IdP approves them as
representing the same logical principal. Those workloads share the
governed authorization identity downstream. Workloads that require
independent authorization or attribution as principals need separate
Governed Agent identities.

The IdP MUST establish an unambiguous Governance Tenant and, before
issuance, the Target Tenant for the requested RAS and resource. The RAS
MUST interpret an agent identifier in its asserted issuer context and
MUST NOT key agent authorization on a bare `sub`.

# Profiles and Conformance {#profile-overview}

## Grant Paths {#paths}

The federation model supports two acting relationships:

| Acting relationship | Grant | Profile status |
|---|---|---|
| Agent acts as itself | Intended WAG composition; Governed Agent is the subject | Informative identity and linking requirements in {{wag-flow}}; wire details pending {{wag-gaps}} |
| Agent acts for a user | ID-JAG; user is the subject and Governed Agent is the actor | Complete flow in {{delegated-flow}} |

A Governed Agent is not intrinsically self-acting or delegated. The
authorization transaction determines whether it is represented as the
subject or as the actor for another subject. Authorization for one
relationship does not imply authorization for the other.

The delegated path has two token requests:

~~~
 Platform       Client            IdP             RAS        API
    |-- evidence ->|               |               |          |
    |              |-- inputs ---->|               |          |
    |              |               | resolve agent |          |
    |              |               | authorize delegation     |
    |              |<-- ID-JAG ----|               |          |
    |              |------ ID-JAG + proof -------->|          |
    |              |<------ access token ----------|          |
    |              |------------- token + proof ------------>|
~~~

The client presents a supported user credential and workload evidence,
and authenticates at each authorization server. Access requires both
the user's authority and permission for the Governed Agent to act for
that user, within the grant's constraints and resource policy
({{actor-authorization}}).

## Scope and Conformance {#scope}

The adoption path preserves existing Enterprise-Managed Authorization
{{EMA}} deployments and adds agent governance before requiring grant
binding. The level numbers below are explanatory labels, not security
assurance ratings or protocol values.

| Adoption profile | Required addition | Grant protection |
|---|---|---|
| Enterprise access (Level 1) | Existing EMA and base ID-JAG; no separate Governed Agent required | Existing deployment policy |
| Governed agent access (Level 2) | Workload evidence, Identity Binding, Client Association, governed actor, tenant enforcement, and downstream actor gate | Grants without sender constraint permitted only by explicit policy; any binding present is enforced |
| Bound governed agent access (Level 3) | All governed agent requirements plus DPoP at grant issuance and redemption | `cnf.jkt` and same-key continuity required |

Enterprise access is a migration baseline, not conformance to this
document's governed profiles. Existing EMA deployments need no changes
to continue on that path. Adding `act` alone does not establish governed
agent conformance: identity resolution and actor authorization are also
required. These adoption profiles apply to delegated ID-JAG, not WAG.

Unless explicitly limited to bound grants or a named profile, the
requirements below apply to both governed profiles. Conformance claims
MUST identify the supported profile by its URI ({{metadata}}),
implemented role, and supported inputs:

* **ID-JAG:** The IdP, RAS, and client MUST implement their respective
  requirements in {{model}}, {{evidence}}, {{identity}}, {{authorization}},
  {{delegated-flow}}, and {{metadata}}; the API MUST implement {{api-processing}}.
  * The IdP MUST implement ID Token subjects and SPIFFE JWT-SVID actor
    evidence with native client authentication ({{jwt-svid-input}}).
  * A client MUST implement at least one supported subject input and
    one actor input, identify them in its conformance claim, and satisfy
    their requirements.
  * The client and RAS MUST implement `private_key_jwt` for redemption.
    DPoP support and use are REQUIRED for bound governed agent access;
    governed agent access follows {{grant-protection}}.
  * Access tokens are JWTs under {{RFC9068}} or opaque tokens whose
    introspection response carries the same context under
    {{introspection}}.
  * Existing platform JWTs, Client Attestation, SAML subjects, and IdP
    refresh-token subjects are OPTIONAL capabilities at the IdP. A
    deployment selects mutually supported inputs through trusted
    configuration; a client using platform JWTs need not implement SPIFFE.
* **WAG:** {{wag-flow}} is informative and describes identity and linking
  requirements for a future composition. WAG is outside the conformance
  targets of this revision ({{wag-gaps}}).

Implementations MAY support other flows but MUST NOT retry the same
request under another flow, grant type, or credential class after
validation or authorization fails under this profile.

Grant protection, workload-evidence protection, and access-token
protection are separate choices. Even bound governed agent access can
use bearer workload evidence and, under explicit resource policy,
bearer access tokens. {{grant-protection}} and {{discovery}} define
applicability and downgrade prevention; {{access-token-protection}} defines
protection on the API hop.

Not in this revision: continuation composition, provisioning protocols
and account administration, multi-agent delegation chains, instance
identification and propagation, client attester endorsement, and
enrollment or key-replacement protocols ({{upstream-gaps}}).

## Deployment Configuration {#configuration}

The relationships in {{model}} require trusted configuration, not a
particular storage representation or administrative interface:

| Value | Configured by | Consumed by | Discoverable |
|---|---|---|---|
| Credential authority: issuer or trust domain, approved key source, algorithms, credential class, time limits | IdP, under the selected credential specification | IdP | Per credential specification; discovery MUST NOT establish trust |
| Identity Binding: authority, exact workload identity, Governed Agent, Governance Tenant | IdP administrator or approved platform-registry import | IdP | No |
| Client Association: client, permitted binding or binding set, flow, actor credential class | IdP administrator | IdP | No |
| Accepted evidence and proof requirements for each binding and client | IdP policy and client configuration | Client, IdP | No |
| Client registration and authentication keys | Client, at the IdP and at the RAS, or via CIMD | IdP, RAS | Client metadata under {{CIMD}} where supported |
| Target: RAS issuer, resources, Target Tenant, subject namespace, `aud_sub` authority | IdP administrator | IdP | RAS metadata under {{RFC8414}} confirms grant and profile support |
| Delegation authorization: agent, user, client, tenant, RAS, resource, authority | IdP policy or consent | IdP | No |
| Local agent principal and user links | RAS, via provisioning or directory synchronization | RAS, API | No |
| Applicable profile and minimum per client, trust relationship, and resource | Client, IdP, RAS, and resource policy | Client, IdP, RAS, API | Metadata advertises capability, not acceptance policy ({{discovery}}) |
| Access-token protection per resource | RAS and client | RAS, API, client | Trusted configuration under {{access-token-protection}}; `token_type` distinguishes DPoP, but not mutual TLS from bearer |

Existing workload-federation configuration can supply credential trust
and exact identity selectors. The Governed Agent mapping and separate
Client Association are still required, but no new configuration object
types are prescribed. {{identity-example}} illustrates the shared-client
case; {{aws-example}} applies the model to AWS STS and Amazon Bedrock
AgentCore.

Request hints, discovered client metadata, and unverified JWT claims
MUST NOT by themselves establish credential-authority trust or change
an approved Identity Binding or Client Association. Creating and changing bindings
and associations, including imports from platform registries, is an
administrative act outside this profile ({{operational-guidance}}).

## Identity Mapping Example {#identity-example}

This non-normative example uses a shared platform SSO client and a
corresponding RAS client. The IdP associates approved SPIFFE IDs with
the shared client for authentication; tenant trust, Identity Bindings,
and Client Associations remain separate. Replicas obtain evidence for
the same platform agent without per-replica registration.

| Association | Configured value |
|---|---|
| Shared OAuth client at IdP; corresponding client at RAS | `platform-sso`; `platform-api` |
| Approved SPIFFE trust domain and bundle endpoint | `platform.example`; `https://platform.example/spiffe/bundle` |
| Exact external workload identity | `spiffe://platform.example/accounts/acme/agents/workload-7` |
| Client authentication | JWT-SVID associated with `platform-sso` at IdP; `private_key_jwt` for `platform-api` at RAS |
| Governed Agent and Governance Tenant | `agent-42` at `https://idp.example/`; `acme` |
| Target RAS, tenant, and resource | `https://ras.example/`; `acme-data`; `https://api.example/tenants/acme-data/` |
| RAS agent principal | `service-principal-42`, linked to `(https://idp.example/, agent-42)` |
| Delegation | Agent may act for Alice on `files.read` in `acme-data` |

Alice's ID Token has `sub=alice-app` and `aud=platform-sso`.
The IdP translates her subject to `alice-ras` for the RAS, which links
it to local user `user-108`. Alice holds the file permission; the local
agent principal passes the actor gate without an independent file ACL.

The same agent can run in Kubernetes with SPIFFE ID
`spiffe://platform.example/accounts/acme/agents/workload-7-k8s`.
A second Identity Binding resolves it to `agent-42`. The Client
Association permits the shared client to use either approved binding.
Either binding produces the same IdP-qualified actor and RAS principal.
Disabling one leaves the other available, subject to policy.

Under the intended WAG composition, `agent-42` would be the subject
for self-acting work ({{wag-gaps}}). The execution environment changes
neither the governed identity nor its downstream correlation.

The complete messages for this configuration are in {{walkthrough}}.

## Requirements by Implementer {#profile-requirements}

This non-normative index locates requirements by role. The differences
from the underlying protocols are summarized in {{profile-additions}}.

| Implementer | Requirement | Defined in |
|---|---|---|
| Platform | Supply an existing credential accepted by the selected input profile | {{evidence}} |
| Client | Select supported inputs, authenticate, satisfy the selected grant protection, and retain token context | {{scope}}, {{grant-protection}}, {{exchange-request}}, {{redemption}}, {{client-token-reuse}} |
| IdP | Validate evidence, resolve the agent, enforce the Client Association, and authorize delegation | {{inputs}}, {{identity}}, {{authorization}} |
| IdP | Construct the governed actor and issue the governed ID-JAG | {{actor-construction}}, {{grant-issuance}} |
| IdP and RAS | Resolve and link the user in the target namespace | {{subject-resolution}} |
| RAS | Validate and redeem the grant; apply local authorization and token-protection policy | {{redemption}} |
| API | Enforce profile applicability, actor authorization, tenant, and token protection | {{api-processing}} |
| Client, IdP, and RAS | Configure capabilities, advertise support, and process failures | {{metadata}}, {{errors}} |

# Workload Evidence {#evidence}

This profile accepts existing workload credentials under the input
profiles below. Each profile defines credential validation, identity
extraction, its relationship to client authentication, and any proof
requirements. The resulting external identity is resolved through an
Identity Binding; no new workload credential format is defined.

Input support follows {{scope}}; alternatives are in {{optional-inputs}}.
Support does not establish trust in a credential authority or permission
to use a binding.

The platform supplies credentials using its existing issuance and
workload-authentication mechanisms. Those mechanisms MUST authorize
issuance for the workload identity; a caller-supplied subject or agent
identifier alone MUST NOT establish that identity. Evidence acquisition
is outside this profile. The IdP approves credential authorities and
exact external identities through configured Identity Bindings.

## SPIFFE JWT-SVID {#jwt-svid-input}

The client MUST present the identical compact JWT-SVID in `actor_token`
and `client_assertion`, and authenticate under {{SPIFFE-OAUTH, Section
3.1}}. The IdP MUST apply its JWT-SVID validation rules before resolving
the actor, including:

* Require `client_assertion_type` of
  `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` and the IdP
  issuer identifier as the sole audience.
* Validate the signature and expiration using keys authorized for the
  trust domain in the SPIFFE ID, with trust establishment and key
  distribution under {{SPIFFE-OAUTH, Sections 5 and 6}}. An optional
  `iss` MUST NOT select another trust domain or key authority.
* Verify the SPIFFE ID's association with the authenticated client
  under SPIFFE OAuth. This authentication check does not establish an
  Identity Binding or Client Association.

The IdP MUST resolve the exact SPIFFE ID in the validated `sub` and
separately authorize client use under {{identity-binding}}, even when
client authentication permits a prefix match. The evidence-role
separation in {{inputs}} applies to this dual use of the credential.

This input retains JWT-SVID's existing format and bearer semantics; it
requires no new `typ` value or issuer-bound key. When used, DPoP binds
the issued grant to the grant proof key, not the JWT-SVID to its
presenter. A policy requiring issuer-bound presenter proof MUST reject this bearer
input rather than treat DPoP as that proof ({{credential-requirements}}).

# Governed Agent Resolution {#identity}

Resolution turns validated evidence into principals: the Identity
Binding resolves the external workload identity to one Governed Agent,
subject resolution identifies the user for delegated access, and the
RAS correlates both to its local principals.

## Identity Binding {#identity-binding}

| Evidence | Identity used for resolution | Qualification |
|---|---|---|
| SPIFFE JWT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Common input under {{jwt-svid-input}}; native client authentication |
| Existing platform JWT | Approved issuer and exact subject, with configured additional selectors | Optional input under {{imported-jwt-input}} |
| Client Attestation whose attested client maps explicitly to one Governed Agent | Trusted attester and validated Client Attestation `sub` under {{agent-evidence}} | The validated `sub` identifies the OAuth client; client-to-agent mapping is explicit |
| SPIFFE X.509-SVID | Approved trust domain and exact SPIFFE ID in the URI SAN | Client authentication only in this revision; separate actor evidence required |
| SPIFFE WIT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Client authentication only in this revision; separate actor evidence required |

After validating actor evidence, the IdP MUST:

* Resolve the exact workload identity to one active Governed Agent
  through an enabled Identity Binding; reject missing, ambiguous, or
  disabled mappings.
* Apply exact resolution even when client authentication permits a
  prefix match. A client identifier, including a {{CIMD}} URL,
  identifies the client, not the agent.

Similar names, unqualified identifiers, or a shared signing key MUST
NOT establish identity equivalence. The table above defines the
external identity for each input.

The IdP MUST support disabling an individual Identity Binding without
requiring the Governed Agent or its other bindings to be disabled.
Once the change is applied, the disabled binding MUST NOT authorize new
grant issuance. Disabling a binding does not itself revoke outstanding
tokens; their treatment follows {{status-changes}}.

The IdP MUST verify a Client Association that permits the authenticated
client to use the selected Identity Binding in the selected flow with
the selected actor credential class ({{flow-configuration}}). The IdP
MUST NOT substitute the client's identity for the resolved actor.

A Client Association MAY authorize one or more Identity Bindings. The
IdP MUST determine explicitly whether the selected binding is within
that authorization. Authorization of one binding, a credential
authority, a credential class, or the Governed Agent itself MUST NOT
imply authorization of another binding unless the association's policy
explicitly includes it. No association overrides a disabled binding.
Policy representation and evaluation mechanisms are outside this profile.

## Subject Resolution and Linking {#subject-resolution}

For ID-JAG, subject resolution identifies the user and linking
associates that identity with a local account. The intended self-acting
composition is described informatively in {{wag-flow}}.
Subject identifiers, tenant relationships, and `aud_sub`, `aud_tenant`,
and `sub_id` follow {{ID-JAG, Sections 3.1, 5,
and 6}}; this profile adds the following.

The IdP MUST:

* Resolve exactly one user from the ID Token's issuer-qualified subject
  or the SAML assertion's issuer-qualified NameID and tenant context,
  or from the validated refresh token's authorization context. The actor
  credential and authenticated client MUST NOT substitute for that
  identity.
* Select the subject namespace of the target RAS's SSO relationship. A
  client-specific pairwise subject MUST NOT be copied into another
  relying party's namespace without resolving the same user there.
* Derive `aud_sub`, `aud_tenant`, or `sub_id`, when used, from an
  authoritative association for the target, never from a client-supplied
  account hint.

After validating the ID-JAG and its client and proof bindings, the RAS
MUST:

* Resolve exactly one local user in the authorized Target Tenant,
  qualifying `sub` by the validated IdP issuer and tenant relationship;
  IdP and RAS tenant identifiers are not interchangeable.
* Use `aud_sub` only when the IdP is authorized to assert local account
  identifiers for that Target Tenant, and MUST NOT use it to override
  a conflicting approved link.
* Reject conflicting identifiers or multiple local matches without
  retrying a weaker selector or another tenant.
* Resolve `act.iss` and `act.sub` separately under {{agent-correlation}};
  acting for a user does not link the agent to the user's account.

A link between an external user and a local account MUST rest on an
authoritative association, not on email, username, or display-name
equality alone. Each qualified external identity MUST resolve to at
most one local account per Target Tenant. A link change MUST NOT
transfer an outstanding grant or delegation to another user. The IdP
and RAS MUST reject issuance for a disabled user or missing, ambiguous,
or conflicting resolution ({{errors}}); linking mechanisms are
deployment choices ({{operational-guidance}}).

## Governed Agent Attribution {#agent-correlation}

The Governed Agent identity is the pair of IdP issuer and agent
identifier, carried in ID-JAG as (`act.iss`, `act.sub`).
The RAS MUST:

* Resolve that qualified identity independently of the user's identity;
  a bare subject, display name, or OAuth client identifier MUST NOT
  replace it.
* Deny authorization that depends on a missing provisioned agent record.

User-account and agent-record links are distinct. A changed Identity
Binding or local agent link MUST NOT transfer an existing delegation
to a different agent.

The RAS MUST preserve the complete validated `act` object in the access
token or its introspection context, including `iss`, `sub`, and any
`sub_profile`, under {{ACTOR-PROFILE, Section 3.6.3.2}}. It MUST NOT add,
remove, or rewrite actor members. Preservation applies to JSON members
and values, not to serialization, whitespace, or member order.

In particular, the RAS MUST NOT translate `act.sub` to its local
agent-principal identifier or replace `act.iss` with its own issuer.
The local agent record supports authorization and attribution; it does
not replace the federated actor.
Thus, user identity is translated into the RAS namespace, while agent
identity is preserved and correlated with a local record.

Where the RAS requires a local agent principal, the IdP or its
authorized directory connector SHOULD provision and synchronize that
principal keyed by the same pair and SHOULD propagate activation and
deactivation. Once deactivation is applied, the RAS MUST reject new
issuance and refresh for that agent; outstanding tokens follow
{{status-changes}}. No provisioning protocol is required
({{operational-guidance}}).

# Authorization Relationship {#authorization}

Validated identity does not grant authority. After resolution under
{{inputs}} and {{identity}}, the IdP MUST authorize issuance under
current assignments and policy for the resolved agent, authenticated
client, acting relationship, Governance and Target Tenants, RAS, resource,
and requested authority. The authority asserted in the ID-JAG MUST be
bounded by both:

* The authority the IdP is authorized to assert for the user.
* The authority permitted by the agent's delegation authorization
  ({{delegation-authorization}}).

The IdP authorizes cross-domain delegation within its configured
authority; the RAS and API determine effective resource and operation
authorization, including the actor gate ({{actor-authorization}}).
The IdP need not interpret every tool argument or business
object. An issuance decision that depends on those semantics requires
authoritative resource-domain evaluation, locally or through a trusted
policy service.

The IdP MAY narrow scope, reflecting the result in the grant and
response under {{RFC8693}}. It MUST return `invalid_scope` if no scope
can be granted. It MUST NOT issue by dropping a required actor or
binding, substituting an external identifier for the Governed Agent,
or weakening proof requirements. Denied delegation MUST NOT fall back
to self-acting access.

Governed Agent identity and actor attribution do not establish the
purpose, approval, or lifecycle of a multi-operation task.

## Delegation Authorization {#delegation-authorization}

Before constructing `act`, the IdP MUST authorize the resolved Governed
Agent to act for the user in the requested client, tenant, RAS,
resource, and authority context. The IdP MUST reject missing, revoked,
expired, or insufficient delegation authorization. Valid credentials,
user sign-in, or a shared client MUST NOT imply that authorization or
permit one agent to use another agent's.

The basis for the decision is a deployment choice: user consent,
administrator assignment, organizational policy, or task authorization
are all acceptable. Approval records and their storage are outside this
profile. Pre-existing actor chains are rejected under {{actor-inputs}}.

## Authorization Lifetime {#authorization-lifetime}

Credential validity, the ID-JAG redemption window, and the duration of
downstream authorization are separate limits. Credential or ID-JAG
expiration does not by itself terminate an access token or RAS refresh
authorization already issued.

The RAS MUST limit access-token and refresh-authorization lifetimes
under its local policy ({{ras-refresh}}). The ID-JAG's `exp` limits
redemption, not subsequent access. This profile defines no portable
IdP-imposed deadline on downstream authorization ({{deadline-gap}});
it requires no shared approval record or correlated lifetime lookup.

If IdP approval requires a downstream lifetime condition that the
selected composition cannot enforce, the IdP MUST reject issuance
with `actor_unauthorized`. It MUST NOT discard that condition or treat
a shorter ID-JAG lifetime as enforcing it. Revocation follows
{{status-changes}}.

## Delegated Actor Authorization {#actor-authorization}

The authorization decisions belong to separate policy domains:

| Decision point | Question |
|---|---|
| IdP | May this agent act for this user toward the requested RAS, resource, and authority? |
| RAS | Does this resource domain accept the trusted IdP's delegation for this user, actor, client, and tenant? |
| API | Is this operation permitted by user authority, the actor gate, and the token's resource and authorization constraints? |

For delegated access, the RAS and API MUST enforce both:

* **User authority:** the requested operation is within the user's
  permissions and the grant or token's authorized scope and constraints.
* **Actor gate:** the issuer-qualified agent is permitted to act for
  that user in the selected tenant and resource, within the authorized
  delegation. A valid signature or an `act` claim alone does not open
  the gate; failure to establish it MUST result in denial.

The gate MAY be implemented through an agent registration, tenant
assignment, consent policy, or another explicit rule. Requiring the
agent to also hold independent permissions on each object is local
policy, not a baseline requirement. The API MUST enforce the gate at
request time, directly or through a validated RAS authorization whose
scope and freshness satisfy resource policy.

Issuing an ID-JAG under this profile asserts that the IdP authorized
the specified delegation within the grant's constraints. The RAS MUST
independently decide whether to accept that delegation under its local
user, actor, client, tenant, and resource policy. The grant does not
assert that the RAS's policy has been satisfied or convey the IdP's
underlying approval records.

Audit records SHOULD identify both the user and the issuer-qualified
actor; the client identifier MUST NOT stand in for the actor in
authorization or attribution.

# Delegated ID-JAG Profile {#delegated-flow}

This section profiles ID-JAG issuance and redemption using the actor
extension point in {{ID-JAG, Section 9.7}}. Where it is silent, ID-JAG
applies unchanged; the text states only additions and narrowings.

## Relationship to Base Specifications {#profile-additions}

Token Exchange request and response syntax, the ID-JAG format,
`jwt-bearer` redemption, and DPoP proof processing are inherited from
{{RFC8693}}, {{ID-JAG}}, and {{RFC9449}}. This non-normative table
identifies this profile's additions and deliberate narrowings; the
referenced sections define the requirements.

| Area | Profile requirement | Defined in |
|---|---|---|
| Actor extension | Resolve external evidence through an Identity Binding; authorize client use through a separate Client Association | {{identity-binding}} |
| Actor representation | One actor with the Governed Agent as `act.sub` and the IdP as `act.iss`; replaces Actor Profile's credential-to-actor copying | {{actor-construction}} |
| Request narrowing | Actor evidence, exactly one resource, and non-empty scope required; no incoming actor chain | {{root-request}}, {{actor-inputs}} |
| Identity and client binding | Resolve users and agents separately; derive downstream `client_id` from an authoritative client-registration association | {{subject-resolution}}, {{agent-correlation}}, {{flow-configuration}} |
| Grant narrowing | One resource URI as a string, scope constraints, and expiration bounded by evidence and policy; bound profile additionally requires DPoP and `cnf.jkt` | {{grant-issuance}}, {{grant-protection}} |
| Resource processing | Preserve actor and tenant context; enforce the user authority and actor gate with the selected token protection | {{access-token-response}}, {{api-processing}} |
| Refresh narrowing | Explicit policy, client binding, preservation of proof binding and profile, and a finite absolute authorization expiration | {{ras-refresh}} |
| Error processing | Actor credential or resolution failures use `invalid_grant` rather than RFC 8693's default `invalid_request`; denial for a resolved actor uses `actor_unauthorized` | {{errors}} |
| Profile discovery | Identify supported governed profiles in existing ID-JAG metadata; trusted policy sets the minimum | {{metadata}} |

## Prerequisites and Common Capabilities {#flow-configuration}

Before issuance, the IdP MUST have trusted configuration for:

* The Client Association: authenticated client, selected Identity
  Binding, flow, and actor credential class.
* That client's registration and the user's subject namespace at the
  target RAS ({{subject-resolution}}).
* The Governance Tenant, Target Tenant, RAS issuer, and permitted resource.
* The applicable governed profile and minimum requirements under {{discovery}}.

The IdP MUST derive the ID-JAG `client_id` from an authoritative
association between the authenticated IdP client and that client's
registration at the target RAS. A client-supplied downstream client
identifier MUST NOT select or override that association. This
association is distinct from the Client Association that permits use
of an Identity Binding.

The IdP and RAS MUST enforce the applicable profile for the configured
client and trust relationship, even if `actor_token`, `act`, or
`cnf` is omitted from a request or grant.

Each authorization server establishes authoritative client metadata
through registration or, when supported, {{CIMD}}. Clients selecting
JWT-SVID use native authentication under {{jwt-svid-input}}. The client
and RAS MUST support `private_key_jwt` under {{RFC7523, Section 2.2}},
with the RAS token endpoint URL as the
assertion audience. Other configured methods MAY be used, and client
identifiers and keys MAY differ between servers.

`private_key_jwt` provides a common redemption authentication method
across independent implementations without provisioning a shared
client secret. It is mandatory to implement, not mandatory to use;
governed identity resolution does not depend on that method.

One platform client, including an existing SSO client authorized for
Token Exchange, MAY serve many agents; each actor credential still
selects exactly one Identity Binding, and no per-agent
client or per-replica registration is required. With CIMD and SPIFFE
authentication, client association follows {{SPIFFE-OAUTH, Section
5.1}}, including its `spiffe_id` matching rules. A client-metadata prefix
match does not replace exact Identity Binding resolution.

Each implementing role MUST support the capabilities below for the
artifacts it produces or validates:

| Artifact | Mandatory-to-implement capability |
|---|---|
| ID-JAG | IdP signing and RAS validation: `RS256`, as this profile's common grant algorithm |
| JWT access token | RAS signing and API validation: algorithms required by {{RFC9068, Section 2.1}}; not applicable to opaque-token consumers |
| `private_key_jwt` at redemption | Client signing and RAS validation: `RS256`, as this profile's common client-assertion algorithm |
| JWT-SVID | IdP validation: `RS256` and `ES256`; existing issuers retain their credential format and algorithms |
| DPoP, where supported or required | Client proof generation and server validation: `ES256` |

Other algorithms permitted by the selected specification MAY be used
through trusted configuration and metadata. Client authentication at
the IdP follows the selected method's algorithm requirements.

An ID-JAG containing `cnf.jkt` is bound to the DPoP key proven at issuance
and MUST be redeemed with that key. This revision defines no key
transition for bound grants; a distributed platform MUST route their
issuance and redemption through the same key holder. A broker obtaining
bound grants for workers therefore also redeems those grants.

{{configuration}} summarizes deployment configuration by responsible
party. Deployments also choose a renewal strategy for unattended work
and recovery when fresh user authorization is required
({{continuing-access}}).

## Grant Protection {#grant-protection}

The applicable profile determines whether an ID-JAG without sender
constraint is acceptable. Client authentication and all governance
requirements remain mandatory in either profile.

* **Bound governed agent access:** The client MUST supply a DPoP proof
  at issuance. The IdP MUST validate it and bind the grant with `cnf.jkt`.
  The RAS MUST require that binding and a proof from the same key at
  redemption. An issuance request without the required proof MUST fail
  with `invalid_request`; a grant without the required binding MUST fail
  with `invalid_grant`.
* **Governed agent access:** The IdP and RAS MAY issue and accept grants
  without `cnf` only when trusted policy explicitly permits them for
  the client, trust relationship, and requested resource. DPoP support
  is OPTIONAL. If the issuance request includes a DPoP proof, the IdP
  MUST validate it and bind the grant under {{ID-JAG, Section 9.8.1.1}}.

The following rules apply to both profiles:

* A supplied DPoP proof MUST be validated under {{RFC9449}}. An endpoint
  that does not support DPoP MUST reject a request containing such a
  proof with `invalid_request`; it MUST NOT silently ignore the proof.
* A grant containing `cnf` MUST have a valid, supported `jkt` binding.
  The RAS MUST require a fresh DPoP proof whose public-key thumbprint
  matches exactly. Missing proof, missing required binding, unsupported
  confirmation, or key mismatch MUST fail with `invalid_grant`.
* When policy permits a grant without `cnf`, the client MAY present a
  DPoP proof only at redemption to obtain a DPoP-bound access token.
  That proof protects the resulting token; it does not retroactively
  bind the grant. Access-token protection follows {{access-token-protection}}.
* Credential-specific proof requirements still apply. Selecting governed
  agent access MUST NOT disable proof required by the actor input or
  client authentication method.

## Token Exchange {#exchange-request}

### Request {#root-request}

The client sends an HTTPS POST to the IdP token endpoint, using
`application/x-www-form-urlencoded`, authenticates as the configured
client, and supplies any proof required by {{grant-protection}}.
The following parameters are REQUIRED:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `requested_token_type` | `urn:ietf:params:oauth:token-type:id-jag` |
| `subject_token` | User ID Token, SAML 2.0 assertion, or refresh token when supported, issued for the authenticated client |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:id_token`, `urn:ietf:params:oauth:token-type:saml2`, or `urn:ietf:params:oauth:token-type:refresh_token` |
| `actor_token` | Direct credential selected under {{actor-inputs}} |
| `actor_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `audience` | One target RAS issuer identifier |
| `resource` | Exactly one resource URI under {{RFC8707}}, served by the RAS named in `audience` |
| `scope` | Non-empty scope string for the requested resource |

`audience` selects the RAS that will redeem the grant; `resource`
selects protected-resource authority at that RAS. The request MUST
contain exactly one `resource` parameter. A client requiring access to
multiple resources MUST obtain a separate ID-JAG for each resource.
The IdP MUST reject multiple `resource` parameters with `invalid_target`.

This profile narrows ID-JAG by requiring actor evidence, exactly one
resource, and a non-empty scope; `authorization_details` MAY
accompany `scope` and is processed under ID-JAG. Requiring scope gives
this revision a common authorization mechanism through grant issuance,
redemption, refresh, and API enforcement. Resource-specific
authorization details can supplement it; RAR-only authorization is
outside this revision ({{rar-gap}}).

One resource per grant avoids carrying different scope ceilings for
different resources. The IdP MUST constrain all granted scope and
`authorization_details` to that resource. If requested authorization
details cannot be confined to it, the IdP MUST reject the request with
`invalid_authorization_details` under {{RFC9396, Section 6}} rather
than authorize additional resources. Unsupported or invalid requested
authorization details use the same error; an unacceptable `resource`
parameter uses `invalid_target` ({{errors}}).

DPoP processing and the bound profile's additional requirement follow
{{grant-protection}}.

### Subject Token Validation {#subject-token-validation}

The IdP MUST support ID Token subjects, MAY support SAML 2.0 assertion
subjects, and MAY support its own refresh tokens when agreed in client
configuration, validating each under {{ID-JAG, Section 4.3.3}}:

* **ID Token:** the audience MUST identify the authenticated IdP client.
* **SAML 2.0 assertion:** `subject_token_type` is
  `urn:ietf:params:oauth:token-type:saml2`. The IdP MUST map the
  assertion's Audience to the authenticated client under
  {{ID-JAG, Section 4.5}} and resolve the subject under
  {{ID-JAG, Section 3.2}}; agent evidence and actor construction are
  unchanged.
* **Refresh token:** apply `refresh_token` grant validation, including
  client binding, validity, revocation, and proof requirements. The
  requested scope and audience MUST remain within the token's retained
  authorization, and any binding retained with that grant MUST be
  enforced rather than bypassed by selecting another actor input, with
  conflicts rejected as `invalid_grant`.

All subject inputs require current actor evidence and delegation
authorization under {{delegation-authorization}}; the output remains an
ID-JAG. User access tokens are not subject inputs in this revision
({{access-token-subject-gap}}); JWT encoding alone does not make an
access token an ID Token.

### Actor Token Validation {#actor-inputs}

All actor inputs use
`actor_token_type=urn:ietf:params:oauth:token-type:jwt`.

This identifies the format, consistent with {{RFC8693, Section 3}};
it does not select a credential's validation policy. Native inputs
reuse the explicit client authentication method and, for JWT-SVID,
the `client_assertion_type` defined by {{SPIFFE-OAUTH, Section 3.1}}.
The equality check below ensures that actor evidence is the credential
validated under that method. Platform JWTs instead use a configured
credential class. These paths MUST have mutually exclusive validation
rules; the IdP MUST NOT try validators until one accepts the credential.

| Input | Support | Presentation and validation |
|---|---|---|
| JWT-SVID | REQUIRED at the IdP; selectable by the client | Identical compact JWT in `actor_token` and `client_assertion`; native JWT-SVID authentication under {{jwt-svid-input}} |
| Existing platform JWT | OPTIONAL | Existing platform JWT in `actor_token`; validate under {{imported-jwt-input}} and authenticate separately |
| Client Attestation | OPTIONAL | Identical compact JWT in `actor_token` and `OAuth-Client-Attestation`; attested client maps explicitly to one Governed Agent under {{agent-evidence}} |

The IdP MUST classify the `actor_token` using these steps:

1. Select a native credential class when the JWT is
   byte-identical to evidence used by the configured authentication
   method:
   * `client_assertion` used for JWT-SVID authentication selects
     JWT-SVID.
   * `OAuth-Client-Attestation` used for Client Attestation
     authentication selects Client Attestation.
2. Otherwise, an issuer and credential class configured for the
   authenticated client's existing platform JWT input select that
   input. Apply its configured classification rules under
   {{imported-jwt-input}}; a generic `typ=JWT` alone is insufficient.

The IdP MUST reject a credential matching no configured class or more
than one class with `invalid_request`. Classification selects validation
rules; unverified claims do not establish trust. A validation failure
MUST NOT cause retry under another class.

For Client Attestation with `attest_jwt_client_auth`, any grant proof
key MUST match the attestation's confirmation key, narrowing ATTEST's
allowance for a separate DPoP key; with `attest_jwt_client_auth_dpop`
the keys are already one and its DPoP proof serves both roles. ATTEST's
errors apply.

To preserve the single user-to-agent relationship, the IdP MUST reject
an `actor_token` or ID Token containing `act`, and a refresh-token
subject whose retained authorization contains an actor chain.

### Actor Resolution and Construction {#actor-construction}

After credential validation, the IdP MUST resolve the agent under
{{identity}} and authorize issuance under {{authorization}}. The
ID-JAG MUST contain one `act` object with:

* `sub`: the Governed Agent identifier from the Identity Binding.
* `iss`: this IdP's issuer identifier.

These values MUST come from the approved mapping, even when external
and governed identifiers coincide. This replaces the credential-to-actor
copying in {{ACTOR-PROFILE, Section 6.3}}.

The object MUST follow {{ACTOR-PROFILE, Section 3.4}}, including its
`sub_profile` recommendation and unclassified-actor rules. Any
`sub_profile` MUST reflect the IdP's authoritative classification.
{{ENTITY-PROFILES}} defines `service` and `ai_agent`; being a Governed
Agent does not itself establish the `ai_agent` classification.

### Grant Issuance {#grant-issuance}

The ID-JAG MUST use the format and claims of {{ID-JAG, Section 3.1}}
and additionally satisfy:

| Claim | Required result |
|---|---|
| `sub` | Same user as the validated subject credential, expressed in the IdP's subject namespace for the RAS |
| `act` | Governed Agent actor constructed under {{actor-construction}} |
| `cnf.jkt` | Thumbprint of the grant proof key when DPoP is used at issuance; REQUIRED for bound governed agent access ({{grant-protection}}) |
| `resource` | The authorized resource URI as a JSON string; arrays are not permitted in this profile |
| `scope` | Non-empty authorized scope string, no broader than the approved request |
| `client_id` | The client's registration identifier at the RAS, derived under {{flow-configuration}} |

The IdP MUST NOT issue a grant if it cannot determine an unambiguous
user, actor, downstream client, or tenant relationship. The grant
lifetime SHOULD be at most five minutes and MUST NOT exceed the
configured lifetime limit. Its expiration MUST NOT exceed the actor
credential's expiration or the subject credential's expiration,
determined as follows:

* **ID Token:** its `exp` claim.
* **SAML assertion:** the earliest applicable `NotOnOrAfter` in the
  assertion's `Conditions` and the `SubjectConfirmationData` used to
  validate the subject. If neither supplies an expiration bound, the
  IdP MUST reject the subject as `invalid_grant`.
* **Refresh token:** its expiry, if the IdP records one. If no expiry is
  recorded, the actor-credential and configured grant-lifetime limits
  still apply; current refresh-token validity and delegation authorization
  remain required. Absence of a recorded expiry does not authorize an
  unlimited grant lifetime.

### Successful Response {#exchange-response}

The response follows {{ID-JAG, Section 4.3.4}}, with `issued_token_type`
of `urn:ietf:params:oauth:token-type:id-jag` and `token_type` of `N_A`.
For a bound grant, the client MUST retain the DPoP key for redemption
and MAY inspect the grant, for example to confirm `cnf.jkt`.

## ID-JAG Redemption {#redemption}

### Request {#redemption-request}

The client sends an authenticated HTTPS POST to the RAS token endpoint
using `application/x-www-form-urlencoded`, with the proof required by
{{grant-protection}} and the applicable access-token protection. These
parameters are REQUIRED unless marked OPTIONAL:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:jwt-bearer` |
| `assertion` | The ID-JAG |
| `resource` | Exactly one parameter whose value equals the grant's resource URI |
| `scope` | OPTIONAL subset of the grant's scope; if omitted, the grant's scope is the upper bound |

The confirmation checks of {{ID-JAG, Section 9.8.1.2}} apply to this
grant type ({{bound-grant-coordination}}).

The RAS MUST reject multiple `resource` parameters or a requested
resource different from the grant's resource with `invalid_target`
under {{RFC8707, Section 2}}. Resource-indicator processing applies to
all token-endpoint grant types, including this JWT bearer grant and
refresh requests ({{RFC8707, Section 2.2}}).

### Grant Validation {#redemption-validation}

The RAS MUST perform ID-JAG validation and additionally:

1. **Actor:** Require a single `act` object under Actor Profile's rules:
   * Require non-empty `iss` and `sub`, with no nested `act`.
   * Require `act.iss` to equal the ID-JAG issuer and configured trust
     to authorize assertion of that namespace.
2. **Proof and client:** Enforce {{grant-protection}}, including the
   configured minimum profile even when `cnf` is absent. Independently
   authenticate the client identified by `client_id`.
3. **Authority:** Require `resource` to be a single resource URI encoded
   as a JSON string; reject missing or invalid values, including arrays,
   with `invalid_grant`. Require the requested resource to match that
   string exactly. Require a non-empty `scope` string and validate any
   scope reduction. Apply ID-JAG's
   processing for `authorization_details`; reject the grant with
   `invalid_grant` if its authority extends beyond that resource.
4. **Local authorization:** Resolve the user under
   {{subject-resolution}} and the Governed Agent actor under
   {{agent-correlation}}. Apply current RAS policy to the user/actor
   relationship under {{actor-authorization}}, client, tenant, and
   resource. A valid grant sets an authority ceiling; it does not
   require issuance.

### Access Token Issuance and Response {#access-token-response}

After validation and authorization, the RAS MUST issue an access token
with these claims under {{RFC9068}}, or equivalent context through
{{introspection}}:

* **Identity:** RAS as issuer, resolved user as subject, and validated
  `act` unchanged under {{agent-correlation}}. Neither the authenticated
  client nor the local agent-principal identifier replaces the actor.
* **Authority:** Redeemed resource as audience and non-empty authorized
  `scope` (otherwise `invalid_scope`), without broadening authority.
* **Protection:** The binding selected under {{access-token-protection}}.
* **Tenant:** The authorized Target Tenant, represented unambiguously by
  a tenant-specific audience ({{RFC8707, Section 3}}), an existing tenant
  claim, or authoritative token context available to the API. The RAS
  and API MUST agree on that representation; a request parameter alone
  MUST NOT establish the token's authorized tenant.
* **Authorization details:** Effective `authorization_details`, when
  used, in the JWT claim or introspection member under {{RFC9396, Section 9}}.
  Narrowing or translating authorization MUST NOT discard restrictions
  in those details or expand the approved authority.
* **Expiration:** Within RAS-local lifetime policy under
  {{authorization-lifetime}} and any applicable refresh-authorization limit.

The response follows {{ID-JAG, Section 4.4.2}}; the client MUST reject
an output that does not satisfy its configured protection requirement.
Refresh-token issuance follows {{ras-refresh}}. An unexpired ID-JAG
remains reusable under ID-JAG, each redemption requiring validation of
any required proof and current RAS policy.

### Access-Token Protection {#access-token-protection}

The RAS MUST issue a sender-constrained access token unless the resource
is explicitly configured to permit bearer tokens. The permitted
protection is selected through trusted client and resource
configuration before issuance, not by a request flag, and a validation
failure MUST NOT trigger a weaker mode.

| Selected protection | Access token | Token response and API use |
|---|---|---|
| DPoP | `cnf.jkt` identifies the validated redemption proof key, which also matches the grant binding when present | `token_type=DPoP`; RFC 9449 proof and resource processing |
| Mutual TLS | `cnf.x5t#S256` identifies the client certificate validated at redemption | `token_type=Bearer`; certificate binding and presentation under RFC 8705 |
| Bearer | No `cnf` | `token_type=Bearer`; RFC 6750 presentation, explicitly permitted by policy |

For mutual TLS with a bound grant, the client MUST also prove possession
of the grant's DPoP key in the same redemption request; certificate
possession alone does not redeem the grant. In this mode the grant proof key protects
grant redemption and any DPoP-bound refresh token; the mutual-TLS key
protects subsequent access-token use. A native mutual-TLS-bound grant
is future work ({{mtls-grant-gap}}).

Bearer issuance accommodates resources without sender-constraint
support; the RAS MUST still enforce any grant binding. The RAS MUST NOT
copy the grant's `cnf` into an access token whose binding will not be
enforced, and clients and APIs MUST NOT treat
a constrained token as an unconstrained bearer token or bypass an
unrecognized confirmation method.

### Opaque Access Tokens and Introspection {#introspection}

The RAS MAY issue an opaque access token instead of a JWT when the API
obtains equivalent context through token introspection {{RFC7662}}.
In that case:

* The API MUST authenticate to the introspection endpoint
  ({{RFC7662, Section 2.1}}) and MUST treat any response other than
  `active` equal to `true` as an invalid token.
* The response MUST carry `sub`, `aud`, `scope`, `client_id`, and the
  validated `act` object unchanged, using the `act` introspection
  member registered by {{RFC8693, Section 7.5}}.
* The response MUST preserve the Target Tenant representation and any
  effective `authorization_details` required by {{access-token-response}}.
* For a bound token the response MUST carry `cnf` with `jkt` under
  {{RFC9449, Section 6.2}} or `x5t#S256` under
  {{RFC8705, Section 3.2}}, and the API MUST enforce it as it would
  the JWT claim.
* The API MUST NOT cache a response that lacks `exp`. When present,
  `exp` MUST identify the token's expiration under
  {{RFC7662, Section 2.2}}. The API MUST NOT cache the response beyond
  that expiration or the freshness limit its resource policy requires
  for disablement ({{RFC7662, Section 4}}).

The processing in {{api-processing}} applies to the introspected
context exactly as to JWT claims.

### RAS Refresh Tokens {#ras-refresh}

The RAS SHOULD NOT issue refresh tokens, retaining {{ID-JAG, Section
4.4.3}}, but MAY do so for authorized long-running work under explicit
policy. The RAS MUST bind each refresh token to the authenticated client
and apply the first applicable sender-binding rule below:

| Redemption context | Refresh-token requirement |
|---|---|
| Grant contains `cnf.jkt` | Retain the grant's DPoP key binding, regardless of access-token protection |
| Unbound grant; DPoP proof used at redemption | Bind to the validated redemption proof key |
| No DPoP proof; certificate-bound access token | Bind to the validated mutual-TLS certificate |
| Neither sender binding | Require explicit policy permitting client-bound refresh without sender constraint, and use rotation under {{RFC9700, Section 4.14}} |

A refresh request MAY include one `resource` parameter under
{{RFC8707, Section 2.2}} solely to identify the retained resource.
If omitted, the RAS MUST use that resource. If supplied, its value MUST
match the retained resource exactly. The RAS MUST reject multiple
values or a different resource with `invalid_target`.

On every refresh, the RAS MUST:

* Authenticate the bound client and enforce any sender binding under
  RFC 9449 or RFC 8705. Dropping or replacing a sender binding requires
  a new grant in this revision.
* Preserve the user, qualified actor, Target Tenant, resource, and
  authorization ceiling, including `authorization_details`. Apply
  current local user and actor policy and {{RFC9396, Section 6}}.
* Enforce current minimum-profile policy against the profile under
  which the grant was accepted; reject with `invalid_grant` if it no
  longer qualifies. Adding a proof does not upgrade that authorization.
* Enforce a finite absolute authorization expiration set at issuance
  under local policy and an inactivity limit under {{RFC9700}}.
  Rotation, refresh, or repeated redemption of the same ID-JAG MUST NOT
  reset the absolute expiration.
* Issue access tokens under {{access-token-response}} and
  {{access-token-protection}}, expiring no later than the absolute
  authorization expiration.

This is RAS-local authorization context; no refresh-token format,
storage representation, or cross-domain refresh exchange is defined.

The absolute expiration bounds authorization derived from one ID-JAG,
not the entire delegated session. Continued access beyond that period
requires a new ID-JAG, a new IdP authorization decision, and a new RAS
authorization decision. If permitted, those decisions establish a new
authorization period; they do not extend the previous one.
Repeated issuance using an IdP refresh token therefore relies on
IdP refresh-token and delegation
policy, and any cumulative RAS limits, to bound overall unattended access.

Refresh is not evidence of a fresh IdP decision. IdP-side revocation
reaches the RAS only through a signal or online check ({{status-changes}}).

## Token Endpoint Error Responses {#errors}

Token endpoint errors follow {{RFC6749, Section 5.2}}, {{RFC8693,
Section 2.2.2}} for Token Exchange, {{RFC8707, Section 2}} for resource
parameters, {{RFC9396, Section 6}} for requested authorization details,
and the applicable authentication and proof methods.
Servers MUST validate client authentication, credentials, and proofs
before authorization. This profile specifies the following outcomes:

| Failure | Error |
|---|---|
| Missing required request parameter, unsupported input combination, or ambiguous credential classification | `invalid_request` |
| Unacceptable `resource` parameter at exchange, redemption, or refresh, including multiple values or a target outside the grant or retained authorization | `invalid_target` under RFC 8707 |
| Requested authorization details are unsupported, invalid, exceed permitted authorization, or cannot be confined to the single resource | `invalid_authorization_details` under RFC 9396 |
| Issued ID-JAG has invalid resource or authorization-detail claims, including authority beyond its single resource | `invalid_grant`; the assertion violates this profile |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Absent, disabled, or ambiguous Identity Binding, or no active Governed Agent can be resolved | `invalid_grant` |
| Resolved Governed Agent, but no Client Association permits the selected binding and flow, or delegation is unauthorized | `actor_unauthorized`, as defined by Actor Profile, with HTTP 400 |
| Missing required grant binding or redemption proof, unsupported confirmation, mismatch with grant `cnf.jkt`, or authenticated client differing from the grant's `client_id` | `invalid_grant` under {{grant-protection}} and ID-JAG client processing |

Actor-credential failures use `invalid_grant` instead of the default
`invalid_request` described by RFC 8693; this narrowing is intentional.
When DPoP is used, proof and nonce errors follow {{RFC9449}} at both
endpoints; unsupported DPoP and missing required issuance proof follow
{{grant-protection}}.

Client authentication failures use the authentication method's error,
including when the same JWT supplies actor evidence. Error descriptions
SHOULD NOT reveal user or agent
existence or binding and policy details. Distinguishing `invalid_grant`
from `actor_unauthorized` reveals that an actor was resolved but denied
authorization, including to a holder of stolen bearer evidence who
satisfies the request's other authentication requirements. It does not
distinguish the individual binding-resolution failures.

## Continuing Access {#continuing-access}

Deployments select a renewal model before scheduling unattended work:

| Mechanism | Conditions |
|---|---|
| Redeem an existing ID-JAG | Grant remains valid; any required proof and current RAS policy apply ({{redemption}}) |
| Obtain a new ID-JAG | Valid subject credential, current actor evidence, and a fresh IdP authorization decision ({{exchange-request}}) |
| RAS refresh | Preserves authorization at the same RAS within its lifetime and policy limits ({{ras-refresh}}) |

An IdP refresh token can supply the subject credential for a new
exchange when permitted; otherwise renewal may require user interaction.
The five-minute ID-JAG recommendation bounds redemption, not task
duration. Cross-domain continuity using Identity Continuation Assertion
{{ICA}} is a separate, deferred composition ({{continuation-sources}}).

## Client Token Reuse {#client-token-reuse}

The client MUST associate each cached grant, access token, and refresh
token with its authorized user, Governed Agent, Governance and Target
Tenants, OAuth client registrations, target RAS and resource, authority,
applicable profile, and proof-binding context. It MUST reuse a token or
grant only when that context authorizes the operation. A shared client
identifier or matching scope alone MUST NOT permit reuse across agents,
users, or tenants.

The association can use trusted request and configuration context;
clients need not parse opaque tokens. If the client cannot establish
the required association, it MUST obtain a token or grant for the current
context. A credential change alone need not invalidate cached tokens
when the governed principal and authorization context remain the same.

## Resource Server Processing {#api-processing}

The API MUST determine whether this profile applies from trusted
resource and issuer policy, using validated client identity or
authoritative token-issuance context where a path also accepts ordinary
user tokens. Missing or malformed `act` MUST NOT select non-delegated
processing when that policy requires this profile. If the API cannot
distinguish the permitted token populations, it MUST reject the
ambiguous token rather than bypass actor processing.

Both governed profiles require the same API identity and actor-policy
processing. The RAS enforces their different grant-protection rules;
the API enforces access-token protection independently. An ordinary
`act` claim alone MUST NOT establish that governed issuance occurred.
The RAS and API MUST agree on authoritative applicability context,
whether conveyed by validated JWT claims, authenticated introspection,
or issuer/client policy. This profile defines no new discriminator.

For tokens subject to this profile, the API MUST validate access tokens
under {{RFC9068}}, or obtain the same context under {{introspection}},
and MUST enforce the following requirements:

* **Identity:** Require one `act` object with non-empty `iss` and `sub`
  and no nested `act`. Trust configuration MUST authorize the RAS to
  assert that IdP-qualified agent identity; `act.iss` need not equal the
  access-token issuer.
* **Protection:** Enforce the configured resource mode and all token
  confirmation claims. Validate DPoP under {{RFC9449}}, certificate
  binding under {{RFC8705}}, or permitted bearer use under {{RFC6750}}.
* **Authority:** Require non-empty `scope` with its defined type.
  Enforce user permissions and the actor gate under
  {{actor-authorization}} and {{ACTOR-PROFILE, Section 8}}. Enforce any
  effective `authorization_details` under {{RFC9396}}, using the API's
  defined semantics for their combination with scope. Independent
  agent permissions on each data object are required only by local policy.
* **Tenant:** Resolve the token's authorized Target Tenant under
  {{access-token-response}} and verify that it matches the tenant of
  the requested operation. Missing, ambiguous, or conflicting tenant
  context MUST result in denial.

If the API delegates authorization evaluation to a policy decision
service, it MUST preserve the distinction between the user, the
issuer-qualified Governed Agent, and the OAuth client, and supply the
tenant and token constraints needed to evaluate the requested operation.
{{AUTHZEN}} provides an optional evaluation interface; this profile
defines no AuthZEN message mapping and requires no particular policy
engine. A policy permit does not override the token's constraints.

For example, the RAS can reserve `platform-api` for this profile while
issuing ordinary user tokens to `interactive-web`. The API configures
that distinction for trusted issuer `https://ras.example/` and selects
processing from the validated issuer and `client_id`. A token for
`platform-api` missing `act` is rejected, not treated as an ordinary
user token. If the RAS issues both populations to one client, these
claims are insufficient: the API needs other authoritative issuance
context and rejects ambiguous tokens.

### Error Responses {#resource-errors}

Challenges and scope errors use the selected protection mechanism:
`DPoP` under {{RFC9449, Section 7.1}}, or `Bearer` under {{RFC6750}} for
bearer and mutual-TLS tokens. Missing or invalid required actor claims,
unauthorized namespace assertions, or missing, ambiguous, or conflicting
token tenant context use HTTP 401 with `invalid_token`.
Denial for a valid actor identity uses
HTTP 403 with `actor_unauthorized` under {{ACTOR-PROFILE, Section 8.2}}.
Actor denial MUST NOT use `insufficient_scope`. The API MUST NOT expose
actor-specific rejection details outside the trust domain.

# Optional Evidence Inputs {#optional-inputs}

The inputs in this section are OPTIONAL. Existing platform JWTs and
Client Attestations can supply actor evidence instead of JWT-SVIDs.
X.509-SVIDs and WIT-SVIDs can authenticate the client but do not yet
supply actor evidence in this profile. Each supported composition is
selected through trusted configuration ({{flow-configuration}}).

## Existing Platform JWT {#imported-jwt-input}

This input accepts existing signed platform JWTs without requiring a
new media type or reissuance in a federation-specific format. The
client presents the JWT as `actor_token` and authenticates separately
with a configured method. The IdP MUST explicitly configure the
accepted issuer, credential class, and authenticated client; this input
MUST NOT be used as fallback for failed native credential validation.

The Identity Binding MUST specify an exact issuer and `sub` and MAY
require additional string values from the JWT Claims Set, including
nested claims. Additional selectors MUST use the JSON Pointer string
representation in {{RFC6901, Section 5}}, evaluated from the Claims Set
root under {{RFC6901, Section 4}}:

* Every selector MUST resolve unambiguously to a string equal to its
  configured value, without type conversion, case folding, or Unicode
  normalization. Missing paths, evaluation errors, non-string values,
  or unequal values MUST prevent that binding from matching.
* Selectors MUST NOT use wildcard, prefix, or pattern matching, and
  MUST NOT replace the exact issuer and `sub` checks.
* A caller-controlled claim MUST NOT distinguish agents unless trusted
  issuance policy constrains its values to identities the caller is
  authorized to assert. A signature alone does not establish that
  authority for request tags or other caller-supplied attributes.

These selectors constrain identity resolution, not the administrative
configuration format. Configuration MUST also specify:

| Item | Requirement |
|---|---|
| Key source and algorithms | Approved keys or an approved HTTPS JWK Set URI under {{RFC7517}}, retrieved with server authentication, and permitted asymmetric algorithms for the issuer |
| Audiences | Values that authorize presentation to this IdP as workload evidence |
| Time limits | Lifetime, rejection of a future `iat`, and any maximum age; an age limit requires `iat` or another configured issuance time, and evidence whose limit cannot be evaluated MUST be rejected |
| Credential class | The rule distinguishing workload credentials from user, management-API, or other tokens of the same issuer: an explicit `typ`, a dedicated issuer, or an accepted audience combined with exact selectors |

The IdP MUST validate the JWT under {{RFC7519}} and {{RFC8725}} and the
configured credential profile. Keys or URLs in the JWT MUST NOT
override the approved key source. An accepted JWT MUST NOT be treated
as OAuth client authentication unless it independently satisfies a
configured client authentication method.
If `cnf` is present, the IdP MUST enforce its proof mechanism and MUST
NOT give the credential bearer treatment when the binding is
unsupported.

This profile defines no new proof mechanism for platform JWTs. A
deployment accepting key-bound JWTs MUST configure their proof
validation and any required relationship to the grant proof key. If
the JWT is bearer evidence, {{credential-requirements}} applies;
exchange DPoP does not add an issuer-bound presenter key.

An AWS STS and Amazon Bedrock AgentCore example appears in {{aws-example}}.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL direct actor input where the attested
OAuth client identity maps explicitly to one Governed Agent. The client
MUST present the identical compact JWT in `actor_token` and the
`OAuth-Client-Attestation` header and authenticate with the configured
ATTEST method; the IdP MUST validate
the attestation and proof under {{ATTEST}} before resolving the agent
({{actor-inputs}}).

The IdP MUST identify the attester unambiguously from the trusted
verification key and configured attester-to-client associations, and
resolve the trusted attester and validated Client Attestation `sub`
through an approved Identity Binding. An `iss`, when present, MUST match that
authority; base ATTEST does not require it.

This input does not distinguish agents behind a shared client; those
agents need distinct workload evidence, such as a JWT-SVID or an
accepted platform JWT. Instance-based resolution
and attester endorsement are deferred ({{instance-agent-resolution}},
{{attester-endorsement-extension}}).

## SPIFFE X.509-SVID and WIT-SVID {#spiffe-input}

X.509-SVID MAY authenticate the client under {{SPIFFE-OAUTH, Section
3.2}}, and WIT-SVID under {{SPIFFE-OAUTH, Section 3.3}} and {{WIT}},
including their proof and key-use requirements. Either request still
requires a supported JWT actor credential; connection evidence or a
WIT-SVID alone as actor input is outside this revision ({{x509-gap}},
{{credential-gap}}).

## Bearer Evidence Limits {#credential-requirements}

Where issuer endorsement of the proof key is required, the deployment
MUST use a supported input that cryptographically binds the key, such
as Client Attestation under {{agent-evidence}}; DPoP co-presented with
bearer JWT-SVID or unbound platform JWT evidence establishes possession only.
DPoP MUST NOT substitute for a credential proof that the selected input
requires. Bearer-evidence theft remains a threat even when the output
is sender-constrained ({{security}}), and shared workload identities do
not distinguish replicas ({{instance-identification}}).

Bearer evidence establishes the credential authority's assertion of
the workload identity, not a cryptographic binding of the current
presenter to that workload. An attacker holding it can impersonate the
workload while the evidence remains acceptable if the attacker also
satisfies client authentication, Client Association, user-credential,
and delegation checks. The attacker can then choose its own grant
proof key. In the JWT-SVID path, the same bearer credential also
satisfies client authentication; that check is not an independent
possession factor.

Short evidence lifetimes limit this exposure; output binding does not
prevent it.

# Authorization Server and Client Metadata {#metadata}

The governed profiles have distinct identifiers:

* **Governed agent access:**
  `urn:ietf:params:oauth:grant-profile:id-jag-governed-agent`
* **Bound governed agent access:**
  `urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`

The existing agent-federation URI retains its mandatory grant-binding
requirements. Enterprise access uses the base
`urn:ietf:params:oauth:grant-profile:id-jag` identifier under ID-JAG;
that identifier alone makes no governed-agent conformance claim.

These URIs identify RAS and client processing. IdP issuance and optional
inputs follow {{discovery}}. No URI claims continuation support, a
particular workload-evidence protection, or access-token protection.
This document defines no numeric level parameter or token claim.

## Authorization Server Metadata {#server-metadata}

Servers MUST publish {{RFC8414}} metadata as follows:

* **RAS:** Include each supported governed profile URI and the base
  `urn:ietf:params:oauth:grant-profile:id-jag` in
  `authorization_grant_profiles_supported`.
  * Include `urn:ietf:params:oauth:grant-type:jwt-bearer` in
    `grant_types_supported` for this profile.
* **IdP:** Advertise Token Exchange in `grant_types_supported` and
  ID-JAG in `identity_chaining_requested_token_types_supported` under
  {{ID-JAG, Section 7.1}}.
  * Include `spiffe_jwt` in `token_endpoint_auth_methods_supported`
    under {{SPIFFE-OAUTH, Section 4}}. The generic JWT actor token type
    alone does not advertise JWT-SVID client authentication.
* **Both:** Advertise supported client authentication methods and, when
  DPoP is supported, DPoP algorithms, including {{flow-configuration}}'s
  common capabilities.
  Where supported, publish the existing CIMD and mutual-TLS capability
  metadata defined by {{CIMD}} and {{RFC8705}}.

## Client Metadata {#client-metadata}

A client SHOULD advertise each supported governed profile URI in
`authorization_grant_profiles_supported` in its authoritative client
metadata under {{ID-JAG, Section 8}}, including when supplied through
CIMD. Its `grant_types` MUST permit:

* `urn:ietf:params:oauth:grant-type:token-exchange` at the IdP.
* `urn:ietf:params:oauth:grant-type:jwt-bearer` at the RAS.

## Discovery and Profile Applicability {#discovery}

RAS support is advertised in metadata. IdP issuance requires bilateral
configuration of trust, Identity Bindings, and Client Associations.
Profile applicability follows these rules:

1. Before exchange, trusted configuration MUST establish the applicable
   governed profile and minimum requirements for the client, issuer
   trust relationship, and target resource. The client, IdP, and RAS
   MUST use that configuration. Client identity, issuer context, and
   target resource identify the applicable policy; this document defines
   no transaction-level profile negotiation.
2. Each server MUST enforce its configured minimum regardless of absent
   `actor_token`, `act`, DPoP, or `cnf`. Their presence or absence MUST
   NOT select a different profile. Metadata advertises capabilities;
   it MUST NOT authorize a lower profile or override resource policy.
3. Implementations MUST NOT retry a failed governed request as ordinary
   EMA or drop proof to retry as governed agent access. A lower profile
   requires a separately authorized configuration, not an error-driven
   fallback.
4. The RAS and API MUST agree on the minimum profile for their resource.
   The API relies on the RAS to enforce grant protection; an access
   token's `cnf` describes its own protection and does not establish
   which grant profile was used. Where multiple paths share a resource,
   applicability follows {{api-processing}}.

An implementation MAY serve existing EMA and either governed profile
concurrently under these rules. Supporting the bound profile does not
require accepting grants without sender constraint or advertising the
intermediate profile. Migration changes the configured profile after
the participating roles implement its requirements; it does not relabel
previously issued grants or refresh tokens.

Conformance follows {{scope}}; other deployment choices are summarized below.

| Common capability | Configured alternatives |
|---|---|
| ID Token subject | SAML 2.0 assertion or IdP refresh-token subject |
| JWT-SVID as actor and IdP client authentication | Existing platform JWT with separate client authentication, or Client Attestation actor |
| `spiffe_jwt` at the IdP; `private_key_jwt` at the RAS | Other methods where supported by the selected input |
| DPoP-protected access token, or bearer where the resource explicitly permits it | Mutual-TLS-bound access token |
| JWT access token under {{RFC9068}} | Opaque access token with introspection under {{introspection}} |
| No RAS refresh token; renewal by new exchange | RAS refresh tokens under {{ras-refresh}} |

Before using the delegated path, the client and IdP MUST agree through
trusted configuration on issuance support and any options; generic JWT
or authentication-method support is insufficient. The client MUST
verify the RAS's profile advertisement, JWT bearer grant support, and
compatible access-token protection. If no supported profile satisfies
the configured minimum, the client MUST NOT initiate that path. If the
`actor_profile_token_exchange`
parameter of {{ACTOR-PROFILE, Section 16.2}} is published, it MUST
describe only the paths actually supported and agree with the ID-JAG
advertisement.

# Identity Requirements for a Future WAG Composition {#wag-flow}

This informative section describes identity and linking requirements
for a future WAG composition carrying the Governed Agent as subject
for self-acting access. An interoperable IdP-issued, sender-constrained
WAG remains pending {{wag-gaps}}; this revision defines no WAG wire
profile or implementation conformance target.

A future composition will need to preserve the identity invariants in
{{identity}}, particularly {{agent-correlation}}, at these stages:

| Stage | Intended identity relationship |
|---|---|
| Workload evidence to IdP | Validated external identity resolves through an approved Identity Binding to one active Governed Agent |
| IdP-issued WAG | Issuer-qualified `sub` identifies that Governed Agent; no `act` is needed solely to identify its executing instance |
| WAG to local authorization | The RAS resolves the Governed Agent identity to one local agent principal in the authorized Target Tenant |
| Access token to API | The token identifies the same agent in the RAS's subject namespace; authorization uses that agent's authority |

The intended composition resolves the same Governed Agent to the same
local principal whether it appears as a WAG subject or an ID-JAG actor.
Self-acting authority is limited to the agent's own authority; delegated
authority remains limited by the user's authority and approved delegation.
A shared agent link does not make those authorities interchangeable.

# Security Considerations {#security}

The security requirements of the selected credential and grant
specifications, {{RFC9700}}, and {{RFC8725}} apply.

## Adoption Tradeoffs {#baseline-costs}

The profile's security controls carry these deployment costs:

| Requirement | Benefit | Cost |
|---|---|---|
| Native JWT-SVID as the common input | Reuses SPIFFE issuance, client authentication, and trust-domain validation | JWT-SVID is bearer evidence; deployments requiring issuer-bound presenter proof must select another supported input |
| Bound profile: DPoP at both token endpoints; grant bound to the grant proof key | A stolen ID-JAG cannot be redeemed without the key | Every client holds and proves a key. Grant binding does not make bearer evidence proof of an issuer-authorized presenter ({{credential-requirements}}) |
| Bound grants: same key for issuance and redemption | No key-transition protocol to secure | A broker that obtains bound grants must also redeem them ({{flow-configuration}}) |
| Access-token context as JWT claims or introspection | The API reads `act`, `scope`, and `cnf` from the token or from an authenticated introspection response ({{introspection}}) | Opaque-token deployments add an introspection round trip and a freshness policy |
| Actor-aware API processing | The actor gate is enforced where access happens | APIs parse `act` and consult the gate on delegated paths |
| Sender-constrained access tokens by default | Token theft is contained | Resources without DPoP or mutual TLS must be explicitly configured for bearer |

Governed agent access without grant binding adds agent authorization
to existing enterprise access but leaves stolen grants redeemable by
an attacker able to authenticate as their designated client. This is
particularly relevant to shared clients. Binding only the resulting
access token does not prevent that redemption. Explicit acceptance
policy, short grant lifetimes, credential confidentiality, and the
no-fallback rules in {{discovery}} limit this exposure; they do not
provide proof of possession of an issuer-authorized grant key.

## Credential and Token Confusion

Validators MUST use mutually exclusive validation rules for the
credential classes they accept under {{RFC8725, Section 3.12}}. A
trusted signature or a matching audience alone MUST NOT convert a client
assertion, platform credential, access token, or grant into another
credential class.

## Time, Replay, and Key Changes {#time-validation}

Validators MUST enforce:

* **Time claims:** Apply the selected credential's expiration and other
  time rules; reject `iat` later than the current time plus permitted
  clock skew. Under {{RFC7519}}, `iat` has no not-before semantics.
* **Clock skew:** Use a configured tolerance that MUST NOT extend a
  configured maximum age or lifetime. It SHOULD remain within the few
  minutes contemplated by {{RFC7519}}.
* **Replay protection:** Apply each credential, proof, and grant
  mechanism independently. Replay state retained through expiration
  MUST cover the maximum allowed skew.

A fresh proof does not renew an expired credential; an unchanged
identifier does not authorize a new proof key.

## Credential Authority and Key Isolation

A compromised credential authority can assert identities within its
trusted scope. Exact bindings, tenant boundaries, and issuer-scoped
key lookup limit that scope. Key lookup MUST retain the issuer or
trust-domain association ({{RFC8725, Section 3.8}}); `kid` alone or a
union of unrelated issuers' keys does not establish the assertion's source.

A holder of a shared private key can present any credential issued for
that key. Agent isolation therefore depends on issuance controls and
key custody as well as identity mapping. Sharing the grant proof key
across components widens its exposure ({{flow-configuration}}).

## Authorization Changes and Revocation {#status-changes}

Before issuance, the IdP MUST apply current binding and authorization
policy and reject an inactive agent or withdrawn binding once the change
has been applied; cached policy data MUST have configured freshness
limits. Cross-system disablement and revocation need the mechanisms in
{{lifecycle-gap}}; without a signal or online check, issued tokens
remain usable until expiration.

The following table summarizes the effect after a change is applied at
the enforcing server; it defines no new propagation mechanism:

| Administrative action | Effect on new authorization | Previously issued authority |
|---|---|---|
| Disable one Identity Binding or its Client Association at the IdP | No new ID-JAG through that relationship; other approved bindings remain available | Existing grants and RAS tokens need separate revocation or expiry |
| Disable the Governed Agent at the IdP | No new ID-JAG for that agent | RAS issuance and refresh stop when the change reaches and is applied by the RAS |
| Withdraw the user's delegation at the IdP | No new ID-JAG for that delegation | Existing RAS authorization can continue until revocation is applied or its absolute expiration |
| Disable the local agent or user at the RAS | No new access tokens or refresh for that principal | API access stops when its actor/user policy observes the change, introspection reports inactivity, or the token expires |

Deployments SHOULD document their maximum disablement delay, including
propagation and cache freshness. Without a bound on propagation, the
remaining lifetime of existing grants, refresh authorizations, and
access tokens determines the possible continuation window; the
five-minute ID-JAG recommendation is not a global stopping guarantee.

Account-linking errors can grant access to another user's account.
{{subject-resolution}} requires issuer, namespace, tenant, and
link-change checks before authorization; proof of key possession does
not establish account ownership, and link removal does not revoke
outstanding tokens.

## External Approval {#external-approval}

External approval MUST NOT replace credential validation, identity
resolution, Client Association, or delegation authorization. A
resource-local approval can satisfy an additional policy condition
within the presented token's authority; it MUST NOT expand that
authority or override token validity or tenant restrictions. Access
beyond that authority requires new authorization through an applicable
protocol. Asynchronous approval composition is deferred under
{{approval-composition}}.

# Privacy Considerations {#privacy}

A stable agent identifier can correlate activity across resources,
users, and instances. Issuers SHOULD disclose only the agent attributes
needed for the authorized purpose, and user and agent context remain
separate when the agent acts for a user. The mapping in
{{actor-construction}} keeps external workload identifiers out of the
ID-JAG; this profile does not define pairwise actor translation. Any
future instance context needs purpose limits, retention guidance, and
clear rules about whose activity it describes.

# IANA Considerations {#iana}

## ID-JAG Grant Profile URIs

This document requests registration in the "OAuth URI" registry
established by {{RFC6755}}:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`
* Common Name: ID-JAG Agent Federation grant profile
* Change Controller: IETF
* Specification Document: {{metadata}} of this document.

This document also requests:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-governed-agent`
* Common Name: ID-JAG Governed Agent grant profile
* Change Controller: IETF
* Specification Document: {{metadata}} of this document.

The URIs are used with ID-JAG's existing authorization server and client
metadata parameters.

--- back

# Dependencies and Deferred Work {#upstream-gaps}

This informative appendix records dependencies and deferred work.
Assessed revisions: WAG-00, ID-JAG-04, ICA-02, Actor
Profile-00, SPIFFE OAuth-02, ATTEST-11, WIT-02, CIMD-02, and the
editor's copies of Identification and Client Attester Endorsement dated
15 September 2026.

## Upstream Dependencies

| Specification | What this profile needs | Consequence until resolved |
|---|---|---|
| WAG | IdP issuance through Token Exchange, WAG-owned identifiers and discovery, sender-constraint and replay rules, authority ceilings, and a decision on refresh ({{wag-gaps}}) | No WAG conformance is claimed |
| ID-JAG | Bound-grant example aligned with the normative `jwt-bearer` grant type, and grant-confirmation errors separated from RFC 9449 proof errors ({{bound-grant-coordination}}) | Confirmation checks are applied to `jwt-bearer` here |
| Actor Profile | A reusable principal-resolution extension point separating credential validation, identity mapping, and actor construction | The mapping is defined locally in {{actor-construction}} |
| ICA | Eligibility rules for a calling agent that holds a token for a third-party API | Continuation beyond RAS refresh is not composed here |

### WAG {#wag-gaps}

{{WAG, Section 5}} anticipates IdP issuance through Token Exchange
without specifying it. Coordination is needed on:

* **Issuance:** External workload evidence as input; the resolved
  Governed Agent in the IdP's namespace as the issued WAG's subject.
* **Identifiers:** WAG-owned token-type and JWT-type registrations
  and discovery.
* **Protection:** Proof-key, audience, nonce, and replay rules at
  issuance and redemption. This document proposes DPoP and a RAS-issuer
  audience.
* **Authority and renewal:** Resource and scope ceilings, WAG's refresh
  prohibition, and IdP refresh tokens for continuing self-acting access.
* **Linking:** WAG Section 7 requires acceptance of previously unseen
  agent identifiers under trusted issuers. Acceptance must remain
  distinct from local principal linking and authorization ({{wag-flow}}).

### ID-JAG Bound Grants {#bound-grant-coordination}

ID-JAG Section 4.4 requires `jwt-bearer` while its bound-grant example
uses `jwt-dpop`. This profile follows the normative grant type with
explicit confirmation processing ({{redemption}}) and takes no
dependency on JWT DPoP Grant.

## Deferred Compositions

### Portable Authorization Deadlines {#deadline-gap}

A portable IdP-imposed deadline on downstream access needs an
authenticated claim or reference, its association with the delegation,
and enforcement rules for access tokens and refresh authorization.
That composition is outside this revision. ID-JAG `exp` remains the
redemption limit; it cannot communicate when subsequent access must end
({{authorization-lifetime}}).

### Asynchronous Approval {#approval-composition}

{{AROP}} composes access-request approval with OAuth token issuance and
discusses deferral at either issuer in an ID-JAG chain. This profile
does not yet define that composition. It needs rules for:

* Credential and grant expiration while approval is pending, including
  whether completion requires fresh evidence or a new ID-JAG.
* Retaining the user, qualified actor, client, tenant, requested
  authority, and proof-key bindings through completion, with current
  authorization checks.
* Completion as an ID-JAG at the IdP or an access token at the RAS,
  including transport discovery, response types, and error precedence.
* Preserving the authorization ceiling and any approval-imposed lifetime
  conditions, including the deadline composition in {{deadline-gap}};
  approval does not permit refresh to broaden existing authority.

Approval transports and policy-service mappings belong in that
composition; the requirements in {{external-approval}} apply regardless
of the mechanism used.

### User Access Tokens as Subjects {#access-token-subject-gap}

Deployed OBO flows, including {{AWS-AGENTCORE-OBO}}, exchange a user
access token for downstream access. {{ID-JAG, Section 4.3}} defines
ID Token, SAML assertion, and refresh-token subject inputs; this
revision does not add an access-token subject composition. A follow-on
profile needs to define:

* Which issuers and token classes are eligible, how the token's audience
  authorizes its use by the authenticated exchange client, and how the
  IdP validates JWT or opaque tokens without accepting arbitrary API
  tokens as identity assertions.
* How the original user, tenant, authorized client, and any existing
  actor relationship are resolved; how sender constraints are enforced
  when the exchange client differs from the original token holder.
* Which retained authorization permits a new downstream audience and
  authority, and how expiry and revocation constrain grant issuance.

This work should be coordinated with ID-JAG's subject-token processing.
Changing only `subject_token_type` to a generic JWT type does not
resolve the audience and authorization differences.

### Continuation with ICA {#continuation-sources}

A federation composition with {{ICA}} would need to specify how ICA's
authenticated-client identity maps to the Governed Agent resolved at the
root, how the agent qualifies as an eligible continuation source, which
Identity Binding and Client Association constrain the chain, and how
each target resolves the original user without expanding delegation. It
would select ICA's discovery, proof, replay, and error rules rather than
redefine them.

### X.509-SVID as Actor Evidence {#x509-gap}

Mutual TLS proves the identity and key of an X.509-SVID but supplies no
JWT for `actor_token`. Binding connection evidence to the requested
actor needs a mechanism defined with SPIFFE OAuth; X.509-SVID client
authentication remains usable with a supported actor JWT.

### WIT-SVID as Actor Evidence {#credential-gap}

Direct WIT-SVID actor input needs actor/header matching, capability
signaling, and an explicit output-key rule. {{WIT, Section 9.4}}
forbids using the workload key after credential expiration, so reusing
it for DPoP would require downstream lifetime limits, and a separate
DPoP key would require an explicit authorization rule.

### Instance-Based Agent Resolution {#instance-agent-resolution}

A composition with {{INSTANCE}} would map the validated (`iss`,
`client_instance_id`) to a Governed Agent with client, receiver-scope,
continuity, and migration checks. It suits managed installations with
durable enrollment; elastic replicas use platform workload evidence and
need no per-replica registration.

### Client Attester Endorsement {#attester-endorsement-extension}

{{ATTESTER-ENDORSEMENT}} defines client endorsements constrained by AS
policy. A composition would use them for attester trust while keeping
this profile's Identity Binding, Client Association, and delegation
checks independent. This revision uses configured attester trust.

### Mutual-TLS-Bound Grants {#mtls-grant-gap}

A native mutual-TLS composition would bind the ID-JAG to the client
certificate (`cnf.x5t#S256`). It needs issuer and redeemer agreement on
presenter binding, recipient binding, and replay handling. Until then,
bound grants require DPoP for redemption even when the access token is
certificate-bound ({{access-token-protection}}). Governed agent access
can instead use an unbound grant under explicit policy; that does not
make the grant certificate-bound.

### RAR-Only Authorization {#rar-gap}

The scope requirement gives every stage a common authorization
vocabulary. {{RFC9396}} permits authorization details without scope,
so an API whose authority lives entirely in `authorization_details`
would today have to supply a placeholder scope. A follow-on composition
must define RAR-only issuance, resource selection, carriage in the
access token or introspection response, API enforcement, refresh, and
errors end to end; placeholder scopes are not an acceptable interim.

### Instance Context {#instance-identification}

A workload identity can span several replicas {{SPIFFE-CONCEPTS}}, and
an identifier alone establishes neither continuity nor authority. Any
downstream `client_instance` composition needs to define whose instance
the context describes, its association with the WAG subject or ID-JAG
actor, and mapping, preservation, and key-change rules under Sections
7.1 through 7.5 of {{INSTANCE}}.

## Operational Dependencies {#operational-guidance}

Provisioning, account linking, and lifecycle propagation are deployment
choices. Useful controls include:

* Authenticate the authority creating or changing a link, or verify
  control of both accounts in a user-linking flow.
* Authorize just-in-time creation by issuer and tenant; avoid silent
  merges and reactivation of disabled accounts.
* Retain ownership, groups, and entitlements with their principal;
  audit link and binding changes.
* Preserve issuer and tenant context when using SCIM `externalId`
  {{RFC7643}}.

SCIM {{RFC7644}} and Agent resources {{SCIM-AGENT}} provide building
blocks, not a lifecycle propagation contract.

### Provisioning and Disablement {#lifecycle-gap}

Consistent record correlation and disablement across IdP and RAS need a
lifecycle specification defining issuer-qualified correlation,
authoritative properties, update ordering, freshness bounds,
missed-event recovery, and the effect on outstanding tokens. Until then,
{{agent-correlation}} and {{status-changes}} state what this profile
guarantees.

# Walkthrough: Shared Platform Client {#walkthrough}

This non-normative walkthrough completes {{identity-example}} using
bound governed agent access and DPoP-protected access to the
API. Key coordinates, thumbprints, token hashes, and compact JWTs are
labeled placeholders, not cryptographic test vectors.

## SPIFFE Workload Evidence

The workload obtains a JWT-SVID with the IdP issuer as its audience.
The decoded header and payload below use the existing SPIFFE format;
`iss` and `iat` are omitted. The IdP selects trusted signing keys from
its configured bundle for the `platform.example` trust domain and
validates the credential under {{jwt-svid-input}}. The expiration is
an illustrative NumericDate value.

~~~ json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "spiffe-key-1"
}
~~~

~~~ json
{
  "sub": "spiffe://platform.example/accounts/acme/agents/workload-7",
  "aud": ["https://idp.example/"],
  "exp": 1789488600
}
~~~

## Exchange Request and Response

The HTTP examples show all application parameters and relevant headers.
Bodies are line-wrapped for display; concatenate their lines before
sending. Uppercase token placeholders stand for complete signed compact
JWTs. HTTP framing headers are omitted.

`JWT_SVID` is the identical credential in `client_assertion` and
`actor_token`. It authenticates `platform-sso` through the configured
SPIFFE ID association and resolves separately to `agent-42` through
its Identity Binding. The JWT-SVID is bearer evidence and does not
bind the grant proof key K to the workload.

`IDP_DPOP_PROOF` uses K and contains `htm=POST`,
`htu=https://idp.example/token`, a current `iat`, and a unique `jti`.
A server nonce is included if challenged. The client proves possession
of K at both token endpoints; `JKT_K` denotes its public key thumbprint.

~~~ http-message
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: IDP_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&requested_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid-jag
&client_id=platform-sso
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth
%3Aclient-assertion-type%3Ajwt-spiffe
&client_assertion=JWT_SVID
&subject_token=ALICE_ID_TOKEN
&subject_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid_token
&actor_token=JWT_SVID
&actor_token_type=urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fras.example%2F
&resource=https%3A%2F%2Fapi.example%2Ftenants%2Facme-data%2F
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
  "client_id": "platform-api",
  "resource": "https://api.example/tenants/acme-data/",
  "scope": "files.read",
  "act": {"iss":"https://idp.example/", "sub":"agent-42"},
  "cnf": {"jkt":"JKT_K"}
}
~~~

`JKT_K` denotes K's JWK thumbprint. This example uses Actor Profile's
unclassified-actor processing; it omits the recommended `sub_profile`.
The configured issuer and client relationships resolve the Governance
Tenant; the tenant-specific resource identifies Target Tenant
`acme-data`.

## Redemption Request and Response

`RAS_CLIENT_ASSERTION` authenticates the corresponding RAS client with
`iss=sub=platform-api`, `aud=https://ras.example/token`, a short
expiration, and its own `jti`. It uses that registration's signing key.
`RAS_DPOP_PROOF` is a fresh proof using K, `htm=POST`, and
`htu=https://ras.example/token`.
The RAS validates the grant binding regardless of the API's token mode.

~~~ http-message
POST /token HTTP/1.1
Host: ras.example
Content-Type: application/x-www-form-urlencoded
DPoP: RAS_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&client_id=platform-api
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth
%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=RAS_CLIENT_ASSERTION
&assertion=ID_JAG
&resource=https%3A%2F%2Fapi.example%2Ftenants%2Facme-data%2F
~~~

For the configured DPoP-protected resource, the response is:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: no-store
Pragma: no-cache

{
  "access_token": "API_ACCESS_TOKEN",
  "token_type": "DPoP",
  "expires_in": 600,
  "scope": "files.read",
  "resource": "https://api.example/tenants/acme-data/"
}
~~~

The access token uses `typ=at+jwt` and the following decoded payload:

~~~ json
{
  "iss": "https://ras.example/",
  "sub": "user-108",
  "aud": "https://api.example/tenants/acme-data/",
  "iat": 1789488000,
  "exp": 1789488600,
  "jti": "access-1",
  "client_id": "platform-api",
  "scope": "files.read",
  "act": {"iss":"https://idp.example/", "sub":"agent-42"},
  "cnf": {"jkt":"JKT_K"}
}
~~~

The RAS translates Alice's subject while preserving the Governed Agent
actor. The shared OAuth client never becomes that actor, and the access
token is bound to the same key K used at both token endpoints.

## Protected Resource Request

The client presents the access token and a new proof signed with K:

~~~ http-message
GET /tenants/acme-data/files/report-7 HTTP/1.1
Host: api.example
Authorization: DPoP API_ACCESS_TOKEN
DPoP: API_DPOP_PROOF
~~~

The decoded proof header and payload are:

~~~ json
{
  "typ": "dpop+jwt",
  "alg": "ES256",
  "jwk": {
    "kty": "EC",
    "crv": "P-256",
    "x": "K_X",
    "y": "K_Y"
  }
}
~~~

~~~ json
{
  "jti": "api-proof-1",
  "htm": "GET",
  "htu": "https://api.example/tenants/acme-data/files/report-7",
  "iat": 1789488005,
  "ath": "ATH_ACCESS_TOKEN"
}
~~~

`K_X` and `K_Y` represent K's base64url-encoded public coordinates.
The public JWK's thumbprint is `JKT_K`. `ATH_ACCESS_TOKEN` represents
the base64url-encoded SHA-256 hash of the ASCII access-token value,
computed without padding under {{RFC9449, Section 4.2}}. The proof has
a new `jti` and current `iat`; if the API requires a nonce, the client
also includes the API-provided `nonce`.

The API validates the token and proof, including `htm`, `htu`, `ath`,
and the match between the proof key and `cnf.jkt`. It then enforces
the user permissions, actor gate, and tenant constraints.

The API verifies the tenant-specific audience for `acme-data`; a call
for another tenant is rejected even if Alice and the agent also have
permissions there. The platform caches this token for Alice and
`agent-42` in `acme-data`, not for all agents using `platform-api`.

For explicitly configured bearer access, the response instead uses
`token_type=Bearer`, the access token has no `cnf`, and the API request
uses `Authorization: Bearer API_ACCESS_TOKEN` without a DPoP proof.
DPoP at grant issuance and redemption remains required in this bound
profile, including when the API accepts bearer tokens.

## Intermediate Adoption Variant

To adopt governed agent access, the parties instead configure
`urn:ietf:params:oauth:grant-profile:id-jag-governed-agent` and explicitly
permit grants without sender constraint. With bearer access also
permitted for this resource, the preceding messages change only as follows:

| Message | Change |
|---|---|
| Exchange request and ID-JAG | Omit the DPoP header; the issued grant has no `cnf` |
| Redemption request | Omit the DPoP header; retain client authentication and all request parameters |
| Access-token response and API request | Use the bearer variant above |

The JWT-SVID, Identity Binding, Client Association, user and actor
identities, scope, tenant checks, and actor gate are unchanged. An
unbound grant may instead obtain a DPoP-bound access token by presenting
a valid proof at redemption; this does not establish bound governed
agent access.
Refresh, if enabled, follows the applicable binding rules in {{ras-refresh}}.

## Renewal and Rejection Examples

The response contains no refresh token. After access-token expiration,
the client obtains a new ID-JAG using valid subject and actor inputs.
If policy instead permits RAS refresh, the RAS sets an absolute refresh
authorization expiration at initial issuance. For example, a four-hour
authorization with a thirty-minute inactivity limit permits renewal
only while both limits hold. Rotation and refresh do not restart the
four-hour period. Each access token expires no later than its end.
Continued access beyond that period requires a new ID-JAG, a new IdP
authorization decision, and a new RAS authorization decision. These
establish a new period under {{ras-refresh}}; the previous period's
expiration remains unchanged.

Each rejection below changes one condition in the walkthrough; all
other credentials, proofs, and policy checks succeed. Token endpoint
errors follow {{errors}}; API errors follow {{resource-errors}}.

| Changed condition | Rejecting party | Result |
|---|---|---|
| Exchange contains a second `resource` parameter | IdP | HTTP 400, `invalid_target`; obtain separate grants for the resources |
| Exchange requests authorization details that cannot be confined to its resource | IdP | HTTP 400, `invalid_authorization_details`; no ID-JAG |
| Redemption requests a resource different from the grant's resource | RAS | HTTP 400, `invalid_target`; no access token |
| ID-JAG `resource` is an array, even with one URI | RAS | HTTP 400, `invalid_grant`; this profile requires a JSON string |
| JWT-SVID remains valid, but its Identity Binding is disabled | IdP | HTTP 400, `invalid_grant`; no actor can be resolved through this binding |
| JWT-SVID and Identity Binding remain valid, but the Client Association for `platform-sso` is disabled | IdP | HTTP 400, `actor_unauthorized`; no ID-JAG |
| Redemption carries a valid DPoP proof signed with another key, while the ID-JAG contains `cnf.jkt=JKT_K` | RAS | HTTP 400, `invalid_grant`; no access token |
| Bound governed agent access is required, but the grant has no `cnf` | RAS | HTTP 400, `invalid_grant`; no fallback to governed agent access |
| Governed agent access permits unbound grants, but this grant has `cnf.jkt` and redemption omits the proof | RAS | HTTP 400, `invalid_grant`; the existing binding is enforced |
| The client presents the access token for an operation in another tenant, with a fresh valid proof for that request URI | API | HTTP 401, `invalid_token`; no operation performed |

# Example: AWS STS and Amazon Bedrock AgentCore {#aws-example}

This non-normative example uses the AWS STS `GetWebIdentityToken`
credential documented in {{AWS-TOKEN-CLAIMS}}. It fits the existing
platform-JWT input ({{imported-jwt-input}}) without a new credential format:

| Item | Example configuration |
|---|---|
| Credential authority | The AWS account's configured STS issuer and approved verification keys |
| Exact `sub` | `arn:aws:iam::123456789012:role/AgentRuntime` |
| Accepted audience | `https://idp.example/token` |
| Additional selector | `/https:~1~1sts.amazonaws.com~1/aws_account` equals `123456789012` |
| Identity Binding result | Governed Agent `agent-42` in Governance Tenant `acme` |
| Client Association | `platform-sso` may use this binding for delegated ID-JAG with platform-JWT actor evidence |

The selector addresses the string `aws_account` within the
`https://sts.amazonaws.com/` object; `~1` escapes each slash in that
member name. The client presents the STS JWT as `actor_token`,
authenticates separately, and supplies a supported user credential and
any proof required by the applicable profile under {{root-request}}.
The resulting actor is
`{"iss":"https://idp.example/","sub":"agent-42"}`.

The execution role and AgentCore Workload Identity are distinct
{{AWS-AGENT-IDENTITY}}. If several agents share this role, issuer and
`sub` alone identify the shared IAM principal, not an individual agent.
Mapping them to distinct Governed Agents requires distinct credential
identities or additional trusted selectors. An agent name supplied by
the caller does not provide that distinction.

AgentCore's documented `AWS_IAM_ID_TOKEN_JWT` actor mode obtains an STS
JWT with the credential provider's token endpoint as audience
{{AWS-AGENTCORE-OBO}}. This establishes an applicable actor-evidence
path, not complete conformance: its documented OBO flow uses an inbound
user access token and returns a downstream access token. An integration
with this profile needs a supported subject input, ID-JAG issuance and
redemption, and the applicable profile's proof processing; managed OBO
support alone does not establish these capabilities ({{access-token-subject-gap}}).

AgentCore's opaque workload access token is for first-party AgentCore
services {{AWS-WORKLOAD-TOKEN}}. It is not the STS JWT in this example
and is not external actor evidence under this profile.

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
