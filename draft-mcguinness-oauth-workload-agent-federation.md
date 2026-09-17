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
workload credentials to stable Governed Agent principals and authorizes
OAuth clients to act for them. It uses existing credentials, with
SPIFFE JWT-SVID as the common interoperability input.

For user-delegated access, it profiles the Identity Assertion JWT
Authorization Grant (ID-JAG), carrying the user as subject and the
Governed Agent as actor in a sender-constrained grant. For self-acting
access, it states federation requirements for the Workload Authorization
Grant (WAG); the WAG wire profile remains pending upstream changes.

--- middle

# Introduction

An agent platform authenticates workloads in its own namespace. An
identity provider (IdP) governs them as principals with owners,
lifecycle state, and assignments. A resource authorization server
(RAS) needs to identify the authorized principal without implementing
every platform's credential validation.

Existing specifications leave that mapping open. {{RFC8693}} defines
`act`, while {{ID-JAG, Section 9.7}} leaves actor-token validation,
authorization, and representation to extensions. {{ATTEST}} and
{{SPIFFE-OAUTH}} authenticate OAuth clients, not the agents a shared
client serves.

This profile composes existing workload federation and OAuth mechanisms
into an integration contract: the IdP resolves external evidence to a
Governed Agent, authorizes a separate OAuth client to exercise that
identity, and issues an ID-JAG whose actor the RAS preserves and
authorizes. Existing service principals can represent the agent. The
contribution is the end-to-end identity and authorization contract,
not a new principal type or credential format ({{model}}).

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth and Token Exchange terms follow {{RFC6749}} and {{RFC8693}}.
Client Attestation and Client Instance follow {{ATTEST}}.

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
: An externally authenticated computational principal identified by
  accepted workload evidence. A workload is not a Governed Agent until
  an Identity Binding resolves it to one.

Identity Binding:
: An approved association from an external credential authority and
  exact external workload identity to one Governed Agent, administered
  in a Governance Tenant. It is the identity-federation relationship.

Client Association:
: An approved permission for an authenticated OAuth client to use a
  specific Identity Binding in a specific flow with a specific actor
  credential class. It is an authorization-policy relationship and can
  change without changing the Identity Binding.

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

# Overview and Conformance {#profile-overview}

## Grant Paths {#paths}

The federation model supports two acting relationships:

| Acting relationship | Grant | Profile status |
|---|---|---|
| Agent acts as itself | WAG; Governed Agent is the subject | Identity and linking requirements in {{wag-flow}}; wire details pending {{wag-gaps}} |
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

Conformance applies per implemented role and selected grant:

* **ID-JAG:** The IdP, RAS, and client MUST implement their respective
  requirements in {{model}} through {{authorization}}, {{delegated-flow}},
  and {{metadata}}; the API MUST implement {{api-processing}}.
  * The IdP MUST implement ID Token subjects and SPIFFE JWT-SVID actor
    evidence with native client authentication ({{jwt-svid-input}}).
  * A client MUST implement at least one supported subject input and
    one actor input, identify them in its conformance claim, and satisfy
    their requirements.
  * The client and RAS MUST implement `private_key_jwt` for redemption.
    DPoP is required at both token endpoints ({{flow-configuration}}).
  * Access tokens are JWTs under {{RFC9068}} or opaque tokens whose
    introspection response carries the same context under
    {{introspection}}.
  * Existing platform JWTs, Client Attestation, SAML subjects, and IdP
    refresh-token subjects are OPTIONAL capabilities at the IdP. A
    deployment selects mutually supported inputs through trusted
    configuration; a client using platform JWTs need not implement SPIFFE.
* **WAG:** {{wag-flow}} states the federation requirements applicable to
  WAG. This revision claims no WAG protocol conformance ({{wag-gaps}}).

Implementations MAY support other flows but MUST NOT retry the same
request under another flow, grant type, or credential class after
validation or authorization fails under this profile.

Not in this revision: continuation composition, provisioning protocols
and account administration, multi-agent delegation chains, instance
identification and propagation, client attester endorsement, and
enrollment or key-replacement protocols ({{upstream-gaps}}).

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
A second Identity Binding resolves it to `agent-42`; a separate Client
Association permits use by the shared client. Either binding produces
the same IdP-qualified actor and RAS principal. Disabling one leaves
the other available, subject to policy.

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
| Client | Select supported inputs, authenticate, prove the grant key, and retain token context | {{scope}}, {{flow-configuration}}, {{exchange-request}}, {{redemption}}, {{client-token-reuse}} |
| IdP | Validate evidence, resolve the agent, enforce the Client Association, and authorize delegation | {{inputs}}, {{identity}}, {{authorization}} |
| IdP | Construct the governed actor and issue the bounded grant | {{actor-construction}}, {{grant-issuance}} |
| IdP and RAS | Resolve and link the user in the target namespace | {{subject-resolution}} |
| RAS | Validate and redeem the grant; apply local authorization and token-protection policy | {{redemption}} |
| API | Enforce profile applicability, actor authorization, tenant, and token protection | {{api-processing}} |
| Client, IdP, and RAS | Configure capabilities, advertise support, and process failures | {{metadata}}, {{errors}} |

# Federation Model {#model}

The IdP controls Identity Bindings, Client Associations, and delegation
authorization. The RAS controls local principal attribution and
authorization, using trusted provisioning from the IdP or an authorized
directory connector where applicable.

~~~
 External Workload
        |
        |  Identity Binding ---- Client Association ---- OAuth Client
        v
  Governed Agent
        |---- Delegation Authorization ---------------- User
        '---- Attribution ---------------------- RAS Local Principal
~~~

External workload identity, Governed Agent identity, and OAuth client
identity are distinct. An Identity Binding resolves the workload to
the agent. A Client Association permits an authenticated client to use
that binding for the selected flow and credential class; it establishes
permission, not identity. Permission for one binding does not cover
another binding to the same agent.

Downstream grants identify the Governed Agent in the IdP's namespace.
The RAS resolves that qualified identity to its local principal without
needing to validate the external workload credential or resolve the
platform's workload identifier. An implementation can represent a
Governed Agent using an existing service-principal object; this profile
does not require a new directory object type.

The profile requires no storage representation or administrative
interface for these relationships. Configuration includes:

| Value | Configured by | Consumed by | Discoverable |
|---|---|---|---|
| Credential authority: issuer or trust domain, approved key source, algorithms, credential class, time limits | IdP, under the selected credential specification | IdP | Per credential specification; discovery MUST NOT establish trust |
| Identity Binding: authority, exact workload identity, Governed Agent, Governance Tenant | IdP administrator or approved platform-registry import | IdP | No |
| Client Association: client, Identity Binding, flow, actor credential class | IdP administrator | IdP | No |
| Accepted evidence and proof requirements for each binding and client | IdP policy and client configuration | Client, IdP | No |
| Client registration and authentication keys | Client, at the IdP and at the RAS, or via CIMD | IdP, RAS | Client metadata under {{CIMD}} where supported |
| Target: RAS issuer, resources, Target Tenant, subject namespace, `aud_sub` authority | IdP administrator | IdP | RAS metadata under {{RFC8414}} confirms grant and profile support |
| Delegation authorization: agent, user, client, tenant, RAS, resource, authority | IdP policy or consent | IdP | No |
| Local agent principal and user links | RAS, via provisioning or directory synchronization | RAS, API | No |
| Access-token protection per resource | RAS and client | RAS, API, client | Trusted configuration under {{access-token-protection}}; `token_type` distinguishes DPoP, but not mutual TLS from bearer |

Existing workload-identity-federation configuration can supply the
credential-validation and identity-selection inputs. Non-normative
examples include:

* Microsoft Entra federated identity credentials use `issuer`,
  `subject`, and `audiences`, matched case-sensitively.
* Google Cloud workload identity pool providers use `issuer-uri`,
  `allowed-audiences`, `attribute-mapping`, and `attribute-condition`.
  A `principal://` IAM binding identifies a federated workload
  principal for authorization; it does not identify a separate OAuth
  client permitted to present that workload's credential.
* JWT-SVID validation uses a trusted trust-domain bundle and an exact
  SPIFFE ID for identity resolution.
* AWS STS outbound identity tokens provide an account-specific issuer
  and an IAM principal ARN as `sub`; {{aws-example}} illustrates the
  binding and its use with Amazon Bedrock AgentCore.

Reusing this configuration still requires the Governed Agent mapping
and separate Client Association, but no new configuration object types.

Request hints, discovered client metadata, and unverified JWT claims
MUST NOT by themselves establish credential-authority trust or change
an approved Identity Binding or Client Association. Creating and changing bindings
and associations, including imports from platform registries, is an
administrative act outside this profile ({{operational-guidance}}).

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

## Canonical Identity and Tenant Boundaries {#canonical-identity}

The Governed Agent identifier MUST be unique and non-reassignable
within the IdP issuer's namespace. It need not equal an external
subject, OAuth client identifier, SPIFFE ID, display name, or instance
identifier. Restarting an execution, replacing a replica, or rotating
a key does not by itself create a new authorization principal.

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

The IdP MUST resolve the exact SPIFFE ID in the validated `sub` through
an Identity Binding, even when client authentication permits a prefix
match. It MUST separately authorize use of that binding under
{{identity-binding}}. The same credential serves client authentication
and agent resolution without making the client and agent the same
principal.

This input retains JWT-SVID's existing format and bearer semantics; it
requires no new `typ` value or issuer-bound key. DPoP binds the issued
grant to the grant proof key, not the JWT-SVID to its presenter. A
policy requiring issuer-bound presenter proof MUST reject this bearer
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
| Client Attestation, agent has its own client | Trusted attester and validated Client Attestation `sub` under {{agent-evidence}} | The validated `sub` identifies the OAuth client; client-to-agent mapping is explicit |
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
the selected actor credential class ({{flow-configuration}}). A Client
Association for a different Identity Binding of the same Governed Agent
MUST NOT satisfy this check, and the IdP MUST NOT substitute the
client's identity for the resolved actor.

## Subject Resolution and Linking {#subject-resolution}

For ID-JAG, subject resolution identifies the user and linking
associates that identity with a local account; WAG subject resolution
follows {{wag-flow}}. Subject identifiers, tenant relationships, and
`aud_sub`, `aud_tenant`, and `sub_id` follow {{ID-JAG, Sections 3.1, 5,
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
identifier: WAG (`iss`, `sub`) or ID-JAG (`act.iss`, `act.sub`).
The RAS MUST:

* Resolve that qualified identity independently of the user's identity;
  a bare subject, display name, or OAuth client identifier MUST NOT
  replace it.
* Deny authorization that depends on a missing provisioned agent record.

User-account and agent-record links are distinct. A changed Identity
Binding or local agent link MUST NOT transfer an existing delegation
to a different agent.

Where the RAS requires a local agent principal, the IdP or its
authorized directory connector SHOULD provision and synchronize that
principal keyed by the same pair and SHOULD propagate activation and
deactivation. Once deactivation is applied, the RAS MUST reject new
issuance and refresh for that agent; outstanding tokens follow
{{status-changes}}. No provisioning protocol is required
({{operational-guidance}}).

Existing service principals and directory connectors can satisfy these
requirements; no particular principal class or provisioning protocol
is required.

# Authorization Relationship {#authorization}

Validated identity does not grant authority. After resolution under
{{inputs}} and {{identity}}, the IdP MUST authorize issuance under
current assignments and policy for the resolved agent, authenticated
client, acting relationship, Governance and Target Tenants, RAS, resource, and
requested authority:

* Self-acting authority MUST NOT exceed the agent's authority.
* Delegated authority MUST NOT exceed the user's authority and the
  agent's authorized delegation ({{delegation-authorization}}).
  The actor gate is defined in {{actor-authorization}}.

The IdP authorizes cross-domain delegation within its configured
authority; the RAS and API apply resource-specific policy to the actual
operation. The IdP need not interpret every tool argument or business
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

When IdP approval imposes a deadline on continued access, the IdP MUST
issue only when trusted configuration ensures that the RAS obtains an
authoritative deadline for that delegation. Otherwise it MUST deny
issuance with `actor_unauthorized`. The RAS MUST bound access-token
expiration and refresh authorization by that deadline. This profile
defines no deadline claim; the ID-JAG's `exp` communicates the
redemption limit, not a continued-access deadline.
Absent such a deadline, the RAS determines authorization duration under
its local policy; revocation follows {{status-changes}}.

For example, both servers can share a policy record authorizing Alice
and `agent-42`, through the configured clients, for `files.read` in
`acme-data` until 18:00 UTC on an agreed date. Each server resolves that
record from its validated request context; the RAS caps access-token
and refresh authorization at 18:00, independently of the ID-JAG's `exp`.
Distinct deadlines for otherwise identical delegations need an
authoritative correlation or lookup mechanism. This profile defines no
such mechanism; without one, the IdP cannot issue those delegations.

## Delegated Actor Authorization {#actor-authorization}

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
| Request narrowing | Actor evidence, explicit resource, non-empty scope, and DPoP required; no incoming actor chain | {{root-request}}, {{actor-inputs}} |
| Identity and client binding | Resolve users and agents separately; derive downstream `client_id` from an authoritative client-registration association | {{subject-resolution}}, {{agent-correlation}}, {{flow-configuration}} |
| Grant narrowing | Require `cnf.jkt`, resource and scope constraints, and expiration bounded by evidence and policy | {{grant-issuance}} |
| Resource processing | Preserve actor and tenant context; enforce the user authority and actor gate with the selected token protection | {{access-token-response}}, {{api-processing}} |
| Refresh narrowing | Explicit policy, client and DPoP binding, and a finite absolute authorization expiration | {{ras-refresh}} |
| Error processing | Actor-credential failures use `invalid_grant` rather than RFC 8693's default `invalid_request`; actor authorization denial uses `actor_unauthorized` | {{errors}} |
| Profile discovery | Add this profile's URI to existing ID-JAG metadata | {{metadata}} |

Deployment policy selects trusted credential authorities, bindings,
delegation rules, local principal links, and resource protection. The
profile constrains their results without defining an administration
protocol ({{model}}).

## Prerequisites and Common Capabilities {#flow-configuration}

Before issuance, the IdP MUST have trusted configuration for:

* The Client Association: authenticated client, selected Identity
  Binding, flow, and actor credential class.
* That client's registration and the user's subject namespace at the
  target RAS ({{subject-resolution}}).
* The Governance Tenant, Target Tenant, RAS issuer, and permitted resource.

The IdP MUST derive the ID-JAG `client_id` from an authoritative
association between the authenticated IdP client and that client's
registration at the target RAS. A client-supplied downstream client
identifier MUST NOT select or override that association. This
association is distinct from the Client Association that permits use
of an Identity Binding.

The IdP and RAS MUST apply this profile whenever it is configured for
the client and trust relationship, even if `actor_token`, `act`, or
`cnf` is omitted from a request or grant.

Each authorization server establishes authoritative client metadata
through registration or, when supported, {{CIMD}}. Clients selecting
JWT-SVID use native authentication under {{jwt-svid-input}}. The client
and RAS MUST support `private_key_jwt` under {{RFC7523, Section 2.2}},
with the RAS token endpoint URL as the
assertion audience. Other configured methods MAY be used, and client
identifiers and keys MAY differ between servers.

One platform client, including an existing SSO client authorized for
Token Exchange, MAY serve many agents; each actor credential still
selects exactly one Identity Binding, and no per-agent
client or per-replica registration is required. With CIMD and SPIFFE
authentication, client association follows {{SPIFFE-OAUTH, Section
5.1}}, including its `spiffe_id` matching rules. A client-metadata prefix
match does not replace exact Identity Binding resolution.

The client, IdP, RAS, and API MUST support `RS256` for the grants,
access tokens, and client assertions they sign or validate, and `ES256`
for DPoP where applicable. The IdP MUST support both `RS256` and `ES256`
for JWT-SVID validation. Other algorithms permitted by the selected
credential specification MAY be selected through trusted configuration
and metadata; this profile does not change native credential formats.

The ID-JAG is bound to the DPoP key proven at issuance and MUST be
redeemed with that key, so the component that obtains the grant
controls the key that redeems it. This revision defines no key
transition; a distributed platform MUST route issuance and redemption
through the same key holder. This excludes a broker that obtains grants
for a pool of workers unless the broker also redeems them.

Before deployment, implementers confirm the following configuration
(a non-normative onboarding checklist):

* **Platform and IdP:** available workload evidence, supported user
  credential, credential trust, Identity Binding, and Client Association.
* **Client and both servers:** registrations, authentication methods,
  downstream client mapping, and the component retaining the DPoP key.
* **IdP and RAS:** user and agent links, Target Tenant, delegation
  policy, and any continued-access deadline ({{authorization-lifetime}}).
* **RAS and API:** tenant representation, actor gate, token protection,
  and disablement freshness.
* **Client and servers:** renewal strategy for unattended work and
  recovery when fresh user authorization is required.

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
| `subject_token` | User ID Token, SAML 2.0 assertion, or refresh token when supported, issued for the authenticated client |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:id_token`, `urn:ietf:params:oauth:token-type:saml2`, or `urn:ietf:params:oauth:token-type:refresh_token` |
| `actor_token` | Direct credential selected under {{actor-inputs}} |
| `actor_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `audience` | One target RAS issuer identifier |
| `resource` | One or more resource URIs under {{RFC8707}}, all served by the RAS named in `audience` |
| `scope` | Non-empty scope string for the requested resources |

This profile narrows ID-JAG by requiring actor evidence, an explicit
resource, a non-empty scope, and DPoP; `authorization_details` MAY
accompany `scope` and is processed under ID-JAG. Requiring scope gives
this revision a common authorization mechanism through grant issuance,
redemption, refresh, and API enforcement. Resource-specific
authorization details can supplement it; RAR-only authorization is
outside this revision ({{rar-gap}}).

The IdP MUST validate the DPoP proof under {{RFC9449}} and
{{ID-JAG, Section 9.8.1.1}}.

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

| Input | Support | Presentation and validation |
|---|---|---|
| JWT-SVID | REQUIRED at the IdP; selectable by the client | Identical compact JWT in `actor_token` and `client_assertion`; native JWT-SVID authentication under {{jwt-svid-input}} |
| Existing platform JWT | OPTIONAL | Existing platform JWT in `actor_token`; validate under {{imported-jwt-input}} and authenticate separately |
| Client Attestation | OPTIONAL | Identical compact JWT in `actor_token` and `OAuth-Client-Attestation`; own-client processing under {{agent-evidence}} |

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

For Client Attestation with `attest_jwt_client_auth`, the grant proof
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
| `cnf.jkt` | Thumbprint of the grant proof key |
| `resource` | The authorized resource URI or URIs, as a string or array |
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
* **Refresh token:** its expiry, if the IdP records one.

The IdP MUST also bound grant expiration by any deadline on continued
access under {{authorization-lifetime}}.

### Successful Response {#exchange-response}

The response follows {{ID-JAG, Section 4.3.4}}, with `issued_token_type`
of `urn:ietf:params:oauth:token-type:id-jag` and `token_type` of `N_A`.
The client MUST retain the DPoP key for redemption and MAY inspect the
grant, for example to confirm `cnf.jkt`.

## ID-JAG Redemption {#redemption}

### Request {#redemption-request}

The client sends an authenticated HTTPS POST to the RAS token endpoint
using `application/x-www-form-urlencoded`, with a fresh DPoP proof from
the grant proof key. These parameters are REQUIRED unless marked OPTIONAL:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:jwt-bearer` |
| `assertion` | The ID-JAG |
| `resource` | One resource authorized by the grant |
| `scope` | OPTIONAL subset of the grant's scope; if omitted, the grant's scope is the upper bound |

The confirmation checks of {{ID-JAG, Section 9.8.1.2}} apply to this
grant type ({{bound-grant-coordination}}).

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
  `act` unchanged. The authenticated client MUST NOT replace the actor.
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
* **Expiration:** No later than a continued-access deadline under
  {{authorization-lifetime}}, if one applies.

The response follows {{ID-JAG, Section 4.4.2}}; the client MUST reject
an output that does not satisfy its configured protection requirement.
Refresh-token issuance follows {{ras-refresh}}. An unexpired ID-JAG
remains reusable under ID-JAG, each redemption requiring fresh proof
validation and current RAS policy.

### Access-Token Protection {#access-token-protection}

The RAS MUST issue a sender-constrained access token unless the resource
is explicitly configured to permit bearer tokens. The permitted
protection is selected through trusted client and resource
configuration before issuance, not by a request flag, and a validation
failure MUST NOT trigger a weaker mode.

| Selected protection | Access token | Token response and API use |
|---|---|---|
| DPoP | `cnf.jkt` equals the redeemed grant's key thumbprint | `token_type=DPoP`; RFC 9449 proof and resource processing |
| Mutual TLS | `cnf.x5t#S256` identifies the client certificate validated at redemption | `token_type=Bearer`; certificate binding and presentation under RFC 8705 |
| Bearer | No `cnf` | `token_type=Bearer`; RFC 6750 presentation, explicitly permitted by policy |

For mutual TLS, the client MUST also prove possession of the grant's
DPoP key in the same redemption request; certificate possession alone
does not redeem the grant. In this mode the grant proof key protects
grant redemption and any DPoP-bound refresh token; the mutual-TLS key
protects subsequent access-token use. A native mutual-TLS-bound grant
is future work ({{mtls-grant-gap}}).

Bearer issuance accommodates resources without sender-constraint
support; grant proof validation remains
mandatory. The RAS MUST NOT copy the grant's `cnf` into an access token
whose binding will not be enforced, and clients and APIs MUST NOT treat
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
policy. The RAS MUST enforce:

* **Binding:** Bind the refresh token to the authenticated client and
  the redeemed grant's DPoP key, and validate both on every refresh.
* **Context:** Preserve the user, qualified actor, Target Tenant,
  resource, and delegation ceiling, including any effective
  `authorization_details`. Apply current local user and actor policy
  and {{RFC9396, Section 6}} when narrowing authorization details.
* **Lifetime:** Set a finite absolute expiration for the refresh
  authorization and an inactivity limit under {{RFC9700}}. The absolute
  expiration MUST NOT exceed a continued-access deadline under
  {{authorization-lifetime}}. Rotation, refresh, or repeated redemption
  of the same ID-JAG MUST NOT reset that absolute expiration. Extending
  it requires a new ID-JAG and current authorization.
* **Output:** Refresh responses MUST satisfy {{access-token-response}}
  and {{access-token-protection}}. Access-token expiration MUST NOT
  exceed the refresh authorization's absolute expiration.

Refresh is not evidence of a fresh IdP decision. IdP-side revocation
reaches the RAS only through a signal or online check ({{status-changes}}).

## Token Endpoint Error Responses {#errors}

Token endpoint errors follow {{RFC6749, Section 5.2}}, {{RFC8693,
Section 2.2.2}}, and the selected authentication and proof methods.
Servers MUST validate client authentication, credentials, and proofs
before authorization. This profile specifies the following outcomes:

| Failure | Error |
|---|---|
| Missing `actor_token` when this profile is configured, unsupported input combination, or ambiguous credential classification | `invalid_request` |
| Invalid subject or actor credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Valid identity evidence but absent, disabled, or ambiguous Identity Binding; no Client Association for the authenticated client; or unauthorized delegation | `actor_unauthorized`, as defined by Actor Profile, with HTTP 400 |
| Missing redemption proof, mismatch with grant `cnf.jkt`, or authenticated client differing from the grant's `client_id` | `invalid_grant` under ID-JAG confirmation processing |

Actor-credential failures use `invalid_grant` instead of the default
`invalid_request` described by RFC 8693; this narrowing is intentional.
DPoP proof and nonce errors follow {{RFC9449}} at both endpoints.

Client authentication failures use the authentication method's error,
including when the same JWT supplies actor evidence. Error descriptions
SHOULD NOT reveal user or agent
existence or binding and policy details. Distinguishing `invalid_grant`
from `actor_unauthorized` exposes a limited validity/authorization
signal, including to a holder of stolen bearer evidence who satisfies
the request's other authentication requirements.

## Continuing Access {#continuing-access}

Deployments select a renewal model before scheduling unattended work:

| Mechanism | Conditions |
|---|---|
| Redeem an existing ID-JAG | Grant remains valid; fresh proof and current RAS policy apply ({{redemption}}) |
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
and proof-binding context. It MUST reuse a token or grant only when
that context authorizes the operation. A shared client identifier or
matching scope alone MUST NOT permit reuse across agents, users, or tenants.

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
context and rejects ambiguous tokens. No new discriminator is defined.

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

## Walkthrough: Shared Platform Client {#walkthrough}

This non-normative walkthrough completes {{identity-example}} with
DPoP-protected access to the API. Key coordinates, thumbprints, token
hashes, and compact JWTs are labeled placeholders, not cryptographic
test vectors.

### SPIFFE Workload Evidence

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

### Exchange Request and Response

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

### Redemption Request and Response

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

### Protected Resource Request

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
DPoP at grant issuance and redemption remains required.

### Renewal and Rejection Examples

The response contains no refresh token. After access-token expiration,
the client obtains a new ID-JAG using valid subject and actor inputs.
If policy instead permits RAS refresh, the RAS sets an absolute refresh
authorization expiration at initial issuance. For example, a four-hour
authorization with a thirty-minute inactivity limit permits renewal
only while both limits hold. Rotation does not restart the four-hour
period, each access token expires no later than its end, and extension
requires a new ID-JAG. Any earlier continued-access deadline also applies.

Each rejection below changes one condition in the walkthrough; all
other credentials, proofs, and policy checks succeed. Token endpoint
errors follow {{errors}}; API errors follow {{resource-errors}}.

| Changed condition | Rejecting party | Result |
|---|---|---|
| JWT-SVID and Identity Binding remain valid, but the Client Association for `platform-sso` is disabled | IdP | HTTP 400, `actor_unauthorized`; no ID-JAG |
| Redemption carries a valid DPoP proof signed with another key, while the ID-JAG contains `cnf.jkt=JKT_K` | RAS | HTTP 400, `invalid_grant`; no access token |
| The client presents the access token for an operation in another tenant, with a fresh valid proof for that request URI | API | HTTP 401, `invalid_token`; no operation performed |

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

### Example: AWS STS and Amazon Bedrock AgentCore {#aws-example}

This non-normative example uses the AWS STS `GetWebIdentityToken`
credential documented in {{AWS-TOKEN-CLAIMS}}. It fits the existing
platform-JWT input without a new credential format:

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
DPoP proof under {{root-request}}. The resulting actor is
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
redemption, and the required DPoP processing; managed OBO support alone
does not establish these capabilities ({{access-token-subject-gap}}).

AgentCore's opaque workload access token is for first-party AgentCore
services {{AWS-WORKLOAD-TOKEN}}. It is not the STS JWT in this example
and is not external actor evidence under this profile.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL direct actor input for an agent with
its own client. The client MUST present the identical compact JWT in
`actor_token` and the `OAuth-Client-Attestation` header and
authenticate with the configured ATTEST method; the IdP MUST validate
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
  * Include `spiffe_jwt` in `token_endpoint_auth_methods_supported`
    under {{SPIFFE-OAUTH, Section 4}}. The generic JWT actor token type
    alone does not advertise JWT-SVID client authentication.
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

## Discovery and Profile Selection {#discovery}

RAS support is advertised in metadata. IdP issuance requires bilateral
configuration of trust, Identity Bindings, and Client Associations.
Conformance follows {{scope}}; deployment choices are summarized below.

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
compatible access-token protection. If the `actor_profile_token_exchange`
parameter of {{ACTOR-PROFILE, Section 16.2}} is published, it MUST
describe only the paths actually supported and agree with the ID-JAG
advertisement.

# Agent Federation Requirements for WAG {#wag-flow}

WAG carries the Governed Agent as subject for self-acting access. This
section states the Agent Federation requirements that apply to WAG
issuance and consumption. It is not a WAG wire profile: an interoperable
IdP-issued, sender-constrained WAG remains pending {{wag-gaps}}, and
this revision claims no WAG conformance.

The IdP and RAS MUST apply {{identity}}, in particular
{{agent-correlation}}, at these stages:

| Stage | Required identity relationship |
|---|---|
| Workload evidence to IdP | Validated external identity resolves through an approved Identity Binding to one active Governed Agent |
| IdP-issued WAG | Issuer-qualified `sub` identifies that Governed Agent; no `act` is needed solely to identify its executing instance |
| WAG to local authorization | The RAS resolves the Governed Agent identity to one local agent principal in the authorized Target Tenant |
| Access token to API | The token identifies the same agent in the RAS's subject namespace; authorization uses that agent's authority |

The RAS MUST resolve the same Governed Agent to the same local principal
whether it appears as a WAG subject or an ID-JAG actor; the acting
relationship still determines authorization, and a shared agent link
does not make those authorities interchangeable.

# Security Considerations {#security}

The security requirements of the selected credential and grant
specifications, {{RFC9700}}, and {{RFC8725}} apply.

## Cost of the Baseline {#baseline-costs}

The profile's security controls carry these deployment costs:

| Requirement | Benefit | Cost |
|---|---|---|
| Native JWT-SVID as the common input | Reuses SPIFFE issuance, client authentication, and trust-domain validation | JWT-SVID is bearer evidence; deployments requiring issuer-bound presenter proof must select another supported input |
| DPoP at both token endpoints; grant bound to the grant proof key | A stolen ID-JAG cannot be redeemed without the key | Every client holds and proves a key. Grant binding does not make bearer evidence proof of an issuer-authorized presenter ({{credential-requirements}}) |
| Same key for issuance and redemption | No key-transition protocol to secure | A broker that obtains grants must also redeem them ({{flow-configuration}}) |
| Access-token context as JWT claims or introspection | The API reads `act`, `scope`, and `cnf` from the token or from an authenticated introspection response ({{introspection}}) | Opaque-token deployments add an introspection round trip and a freshness policy |
| Actor-aware API processing | The actor gate is enforced where access happens | APIs parse `act` and consult the gate on delegated paths |
| Sender-constrained access tokens by default | Token theft is contained | Resources without DPoP or mutual TLS must be explicitly configured for bearer |

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

## ID-JAG Grant Profile URI

This document requests registration in the "OAuth URI" registry
established by {{RFC6755}}:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`
* Common Name: ID-JAG Agent Federation grant profile
* Change Controller: IETF
* Specification Document: {{metadata}} of this document.

The URI is used with ID-JAG's existing authorization server and client
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
* Preserving the authorization ceiling and continued-access deadline;
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
{{access-token-protection}} requires DPoP for grant redemption even when
the access token is certificate-bound.

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

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
