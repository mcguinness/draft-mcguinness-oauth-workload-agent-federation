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
  OPENID:
    title: "OpenID Connect Core 1.0 incorporating errata set 2"
    target: https://openid.net/specs/openid-connect-core-1_0.html
    author:
      - org: OpenID Foundation
    date: 2023-12-15
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
  AGENT-LIFECYCLE:
    title: "Governed Agent Lifecycle Profile for SCIM and OAuth"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-governed-agent-lifecycle.html
    author:
      - name: Karl McGuinness
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-governed-agent-lifecycle
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
  AWS-AGENTCORE-OBO:
    title: "On-behalf-of token exchange with AgentCore Identity"
    target: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/on-behalf-of-token-exchange.html
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

This document defines how an identity provider resolves a dedicated
OAuth client identity or an independently validated workload identity
to a stable Agent Principal. Client authority and user
delegation are authorized separately. Resource systems consume the
issuer-qualified agent identity without interpreting the original
credential. No new credential format is defined.

The federation model covers self-acting access, with the Agent Principal
as subject, and delegated access, with the user as subject and the
agent as actor. This revision defines a complete delegated profile of
the Identity Assertion JWT Authorization Grant (ID-JAG), using existing
client assertions and workload credentials. It describes the self-acting
composition with the Workload Authorization Grant (WAG); its wire
requirements remain pending upstream coordination, and no WAG wire
conformance is claimed.

--- middle

# Introduction

Agent platforms establish workload identities. Enterprises govern
stable authorization principals. Resource systems need to recognize
those principals without understanding every platform's credentials.
This document defines how an identity provider (IdP) resolves client or
workload identity to an Agent Principal, separately authorizes OAuth
client use and user delegation, and carries the governed identity into
the resource domain.

Execution identity can be too coarse when one runtime serves several
actors that need independent governance. It can also be too unstable
when one actor moves across runtime identities while its authorization
identity needs to remain stable.

A dedicated OAuth client resolves through an explicit client-to-agent
binding. A shared client uses independently validated workload identity
to distinguish the agents it serves. Both deployments retain separate
identity, client-authority, delegation, and resource-policy decisions.

Four independent relationships establish that contract:

| Question | Relationship |
|---|---|
| What enterprise agent does this client or workload identity represent? | Identity Binding |
| May this OAuth client exercise that agent through this binding? | Client Association |
| May this agent act for this user toward the requested target and authority? | Delegation Authorization |
| What resource-local principal represents the IdP-qualified agent? | Agent Principal Correlation |

Client and workload credentials are resolution inputs; downstream
authorization identifies the IdP-governed principal. For delegated access,
the resource authorization server (RAS):

* Translates the user identity into its local namespace.
* Preserves the issuer-qualified agent identity.
* Correlates that identity with local authorization state without
  replacing it with the local principal's identifier.

External credentials, execution environments, and OAuth clients can
change without changing the governed identity.

Existing specifications leave that mapping open. {{RFC8693}} defines
`act`, while {{ID-JAG, Section 9.7}} leaves actor-token validation,
authorization, and representation to extensions. {{ATTEST}} and
{{SPIFFE-OAUTH}} authenticate OAuth clients, not the agents a shared
client serves.

The federation model ({{model}}) defines identity resolution, client
authorization, delegation authorization, and resource correlation.
Grant-specific realizations specify how those relationships are carried
and enforced:

* **Delegated ID-JAG:** {{delegated-flow}} defines the normative wire
  profile and is the basis for conformance in this revision.
* **Self-acting WAG:** {{wag-flow}} describes an informative composition;
  {{wag-gaps}} identifies its unresolved wire requirements.

Other grant realizations require their own composition rules; the
federation model alone does not define their wire behavior.

RFC 7523 client assertions, SPIFFE JWT-SVIDs, and the other supported
credentials supply inputs to the same identity model ({{evidence}},
{{optional-inputs}}).

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
  selected grant flow. One client registration can serve several agents.
  Client authentication identifies the client; agent resolution requires
  an explicit Identity Binding.

Identity Provider (IdP):
: The OAuth authorization server that resolves validated inputs to an
  Agent Principal, checks the permitted client and acting relationship,
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

Agent Principal:
: A stable, non-human authorization principal in the IdP's namespace
  representing an independently governed workload or agent. Its identity
  defines the boundary for independently managed authorization, delegation,
  attribution, correlation, and disablement. It is independent of the
  external credentials, execution environments, and OAuth clients used
  to obtain authorization for it; it does not necessarily identify an
  execution, process, replica, installation, or OAuth client.

Workload:
: An external computational principal identified by accepted workload
  evidence. It can span multiple running instances; its identity does
  not necessarily distinguish executions. An Identity Binding resolves
  that external identity to an Agent Principal.

Dedicated client:
: An OAuth client whose authenticated identity maps explicitly to one
  Agent Principal in the IdP's client-registration context. Dedicated
  refers to identity resolution, not to one process, replica, or
  installation.

Shared client:
: An OAuth client serving multiple Agent Principals. Its authenticated
  client identity alone cannot distinguish those agents; resolution
  requires independently validated workload identity.

Identity Binding:
: An approved association from an exact client or workload identity,
  qualified by its registration context or credential authority, to one
  Agent Principal. It is administered in a Governance Tenant and
  establishes identity resolution, not permission to exercise the agent.

Client Association:
: An approved permission for an authenticated OAuth client to use an
  Agent Principal through the selected Identity Binding, flow, and
  credential class. The permission can cover one binding or an explicitly
  authorized set of bindings under {{identity-binding}}. It is an
  authorization-policy relationship, independent of identity resolution.

Credential class:
: A configured category of agent-resolution input with mutually exclusive
  validation rules, such as an RFC 7523 client assertion, JWT-SVID,
  Client Attestation, or a platform issuer's workload JWT profile.
  JWT encoding alone does not identify the class.

Delegation Authorization:
: The IdP's decision that an Agent Principal may act for a user within
  an approved client, tenant, target, and authority context.

Agent Principal Correlation:
: The RAS's authoritative association of an IdP-qualified Agent Principal
  with a local principal. Correlation does not grant authority.

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
: The IdP tenant within whose governance domain the Agent Principal
  exists and is administered. The Agent Principal identifier remains
  qualified by the IdP issuer ({{canonical-identity}}), not by the
  tenant.

Target Tenant:
: The tenant at the RAS in which the agent or user is authorized.

Where the meaning is clear, this document uses agent as shorthand for
Agent Principal.

# Federation Model {#model}

The IdP controls Identity Bindings, Client Associations, and delegation
authorization. The RAS controls local principal correlation and
authorization, using trusted provisioning from the IdP or an authorized
directory connector where applicable.

Establishing one relationship MUST NOT be treated as establishing
another. A local principal link identifies the agent; resource policy
still determines whether to accept its delegated access.

~~~
 Resolution source        IdP namespace       Resource namespace

 dedicated client --\
                     >--> agent-42 ----------> local agent principal
 workload identity -/
            Identity Binding         Agent Correlation

 OAuth client -- Client Association --> permission to use binding
 agent-42 -- Delegation Authorization --> authority to act for user
~~~

External workload identity, Agent Principal identity, and OAuth client
identity are distinct. Identity Binding resolves the agent identity;
Client Association authorizes client use through the binding, flow,
and credential class. Its coverage is explicit under {{identity-binding}}.

The IdP is the authority for the Agent Principal: the ID-JAG's `act.iss`
equals its `iss`, and `act.sub` comes from the IdP's mapping rather than
forwarding the external subject.

The RAS needs no platform-specific credential validation or workload
resolution. An existing service
principal can represent the agent locally without replacing its
IdP-qualified identity ({{agent-correlation}}).

This revision assumes that the grant issuer governs the agent namespace.
Forwarding an actor
from another IdP namespace through a broker is outside its scope.

Token reuse preserves the authorized identity and authority context
under {{client-token-reuse}}.

## Core Invariants {#invariants}

Identity resolution establishes which governed principal participates
in a transaction. It does not establish client authority, user delegation,
resource authority, or permission to perform an operation. The identity
and actor attribution also do not establish a task's purpose, approval,
or lifecycle.

This non-normative index summarizes the requirements that connect
identity resolution to resource enforcement. The referenced sections
define their processing rules.

| Invariant | Required result | Defined in |
|---|---|---|
| Governance boundary | Actors needing independent governance have distinct identities; execution topology does not determine identity or authority | {{governance-boundary}} |
| Identity | Authenticated dedicated-client identity or independently validated workload identity resolves through an enabled exact Identity Binding to one active Agent Principal | {{identity-binding}} |
| Client authority | The authenticated client is permitted to use that binding, credential class, and flow | {{identity-binding}} |
| Delegation | The agent may act for the resolved user in the authorized client, tenant, target, and authority context | {{delegation-authorization}} |
| Federation | ID-JAG identifies the user in the target subject namespace and the agent as `act.iss` = governing IdP, `act.sub` = Agent Principal | {{subject-resolution}}, {{actor-construction}} |
| Resource enforcement | Local user authority, the actor gate, tenant, token authority, and applicable proof requirements all permit the operation | {{agent-correlation}}, {{api-processing}} |

The last three rows describe delegated access. The self-acting WAG
composition uses the same governed identity and client authorization,
with the agent as subject exercising its own authority ({{wag-flow}}).

## Authentication, Resolution, and Proof {#inputs}

The IdP MUST validate a credential according to its configured type
before using it for identity resolution; a generic JWT token-type URI,
an unverified header, or a caller-supplied claim MUST NOT select a
weaker validation path or establish an Identity Binding. Unrecognized
request parameters and JWT claims follow {{RFC6749, Section 3.2}} and
{{RFC7519, Section 4}}.

The IdP MUST distinguish three functions and MUST NOT substitute one
for another:

* **Client authentication:** evidence authenticating the OAuth client.
* **Agent resolution:** resolution of the authenticated dedicated-client
  identity or independently validated workload identity through an
  Identity Binding to exactly one Agent Principal.
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

The Agent Principal identifier MUST be unique and non-reassignable
within the IdP issuer's namespace, across all Governance Tenants sharing
that issuer identifier. Governance Tenant is not an additional component
of the downstream agent identity. Tenant-local identifiers MUST be
qualified to meet this issuer-wide uniqueness requirement before use
as an Agent Principal identifier.

It need not equal an external subject, OAuth client identifier,
SPIFFE ID, display name, or instance identifier. Identity continuity is
an explicit decision by the governing authority to preserve the same
principal; it does not imply that the principal's permissions remain
unchanged. Agent Principal continuity concerns the authorization
principal, not continuity of a particular execution or runtime instance.

An Agent Principal identity does not itself prove which runtime or
execution currently represents the agent; any such assurance comes from
the validated evidence and proofs required by the resolution-input
profile ({{evidence}}).

A transfer to a different Governance Tenant under a different
administrative authority MUST create a new Agent Principal identifier
and MUST NOT automatically carry forward delegations or RAS principal
links. This revision defines no cross-tenant identity migration protocol.

For example:

* Moving an agent to another customer's governance domain creates a
  new identity.
* Renaming a tenant or changing its owner or administrator within the
  same governance domain does not by itself change the principal.

Multiple Identity Bindings MAY resolve distinct client or workload
identities to the same Agent Principal when the IdP approves them as
representing the same governed principal. They share the governed
authorization identity downstream.

The IdP MUST establish an unambiguous Governance Tenant and, before
issuance, the Target Tenant for the requested RAS and resource. The RAS
MUST interpret an agent identifier in its asserted issuer context and
MUST NOT key agent authorization on a bare `sub`. Failure to resolve
the Governance Tenant uses `invalid_grant`; failure to resolve the
Target Tenant for the requested resource uses `invalid_target`.

## Governance Boundary and Execution Independence {#governance-boundary}

Clients, workloads, or other actors requiring independently managed
authorization, delegation, attribution, resource correlation, or
disablement as principals need separate Agent Principal identities.
Differences in process, replica, session, worker, or credential alone
do not require distinct
identities. Sharing those elements does not justify combining actors
that require independent governance.

Multiple executions MAY operate as the same Agent Principal, and an
agent MAY move between workloads or execution environments through
approved Identity Bindings. Conversely, one environment MAY host
multiple Agent Principals. The validated resolution input and its
Identity Binding MUST distinguish exactly one Agent Principal for each
authorization transaction; a shared workload identity alone cannot
select among agents.

Scaling, restarting, rescheduling, migration, credential rotation, or
creation of additional executions, replicas, credentials, Identity
Bindings, or Client Associations MUST NOT by itself create, merge,
transfer, or increase Agent Principal authority.
Each transaction remains subject to the applicable Client Association,
delegation authorization, target, and resource policy.
This profile defines no aggregate budget, quota, or concurrency semantics.

# Profiles and Conformance {#profile-overview}

## Grant Paths {#paths}

The federation model covers both acting relationships. The table
distinguishes their wire-profile status, not their architectural scope:

| Acting relationship | Grant | Profile status |
|---|---|---|
| Agent acts as itself | WAG composition; Agent Principal is the subject | Identity and authorization composition in {{wag-flow}} is informative; wire requirements pending {{wag-gaps}} |
| Agent acts for a user | ID-JAG; user is the subject and Agent Principal is the actor | Complete flow in {{delegated-flow}} |

An Agent Principal is not intrinsically self-acting or delegated. The
authorization transaction determines whether it is represented as the
subject or as the actor for another subject. Authorization for one
relationship does not imply authorization for the other.

The delegated realization transforms validated identities into bounded
authority at two authorization servers, followed by API enforcement:

~~~
 Resolution inputs         Enterprise IdP
 -----------------         --------------
 Dedicated client -------> Authenticate; resolve client binding
           OR
 Workload + client ------> Validate both; resolve workload binding
                                      |
                           Client Association
 User credential --------> Resolve user
                                      |
                           Delegation Authorization
                           (client, tenant, target, authority)
                                      |
                           ID-JAG: sub = user
                                   act = IdP-qualified agent
                                      |
                           Resource Domain
                           ---------------
                           RAS validates grant, client, and proof
                                      |
                           Resolve local user; correlate agent
                                      |
                           RAS authorization within grant ceiling
                                      |
                                 Access token
                                      |
                           API enforces user authority, actor gate,
                           tenant, token limits, and proof binding
~~~

The client presents a supported user credential and agent-resolution input,
and authenticates at each authorization server. The two token requests
are ID-JAG issuance at the IdP and redemption at the RAS. Proof processing
follows the applicable grant and access-token protection; each decision
is constrained by its own policy domain ({{actor-authorization}}).

## Scope and Conformance {#scope}

The adoption path preserves existing Enterprise-Managed Authorization
{{EMA}} deployments and adds agent governance before requiring grant
binding. The names identify deployment profiles, not assurance ratings.

This profile does not establish trust in previously unknown agent issuers
or automatically create Identity Bindings or Agent Principal Correlations
from presented credentials.

| Adoption profile | Required addition | Grant protection |
|---|---|---|
| Enterprise access | Existing EMA and base ID-JAG; no separate Agent Principal required | Existing deployment policy |
| Governed agent access | Agent resolution, Identity Binding, Client Association, governed actor, tenant enforcement, and downstream actor gate | Grants without sender constraint permitted only by explicit policy; any binding present is enforced |
| Bound governed agent access | All governed agent requirements plus DPoP at grant issuance and redemption | `cnf.jkt` and same-key continuity required |

"Bound" refers to sender constraint on the ID-JAG between issuance and
redemption. It does not imply sender constraint on the agent-resolution
credential or the resulting access token.

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
  * The client and IdP MUST implement ID Token subjects and dedicated-client
    resolution using RFC 7523 `private_key_jwt` authentication
    ({{client-assertion-input}}).
  * The client and RAS MUST implement `private_key_jwt` for redemption.
    DPoP support and use are REQUIRED for bound governed agent access;
    governed agent access follows {{grant-protection}}.
  * Access tokens are JWTs under {{RFC9068}} or opaque tokens whose
    introspection response carries the same context under
    {{introspection}}.
  * SPIFFE JWT-SVIDs, existing platform JWTs, Client Attestation, SAML
    subjects, and IdP refresh-token subjects are OPTIONAL capabilities. A
    deployment selects mutually supported inputs through trusted
    configuration; neither role needs SPIFFE for the client-assertion path.
    Shared-client interoperability is bilateral: the client and IdP must
    agree on an input that distinguishes the agents. Conformance alone
    does not guarantee a common shared-client input.
* **WAG:** {{wag-flow}} describes the self-acting identity and authorization
  composition informatively. This revision claims no WAG wire conformance
  while the requirements in {{wag-gaps}} remain unresolved.

The mandatory interoperability path uses an ID Token subject and
dedicated-client resolution at the IdP, followed by governed ID-JAG
redemption using `private_key_jwt` at the RAS and actor-aware processing
at the API. Grant protection follows the applicable governed profile.

ID-JAG requires support for Identity Assertions ({{ID-JAG, Section 4.3}}).
This profile specifically requires ID Token support to give independent
implementations a common subject-token format. This is an implementation
baseline, not a requirement to deploy one client per agent: deployments
MAY use mutually supported optional inputs. Support alone establishes
neither trust nor authorization configuration.

Under {{subject-token-validation}}, the ID Token's audience identifies
the dedicated client. A token issued only to a shared `platform-sso`
client cannot accompany
authentication as a separate `analysis-client`. Dedicated deployments
therefore need a user authorization flow for each agent's client
registration, though an existing IdP session may avoid another login
prompt. A platform retaining its shared SSO client instead uses an
agreed independent workload input ({{optional-inputs}} or {{jwt-svid-input}}).

Credential-class validation follows {{actor-inputs}}; profile
applicability and downgrade prevention follow {{discovery}}.

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

**At the IdP:**

* **Credential trust:** The IdP configures the issuer or trust domain,
  approved key source, algorithms, credential class, and time limits
  under the selected credential specification.
* **Identity Binding:** An IdP administrator or approved platform-registry
  import supplies the qualified client or workload identity, Agent
  Principal, and Governance Tenant.
* **Client Association:** The IdP administrator specifies the client,
  permitted binding or binding set, flow, and credential class.
* **Resolution mode and proof:** IdP policy and client configuration
  establish dedicated-client resolution or an actor-evidence input for
  the client, applicable profile, and target. Within an actor-evidence
  mode, they establish accepted credential classes and proof requirements.
  Request parameters do not select the resolution mode ({{actor-inputs}}).
* **Target:** The IdP administrator configures the RAS issuer, resources,
  Target Tenant, subject namespace, and authority to assert `aud_sub`.
* **Delegation:** IdP policy or consent authorizes the agent, user,
  client, tenant, RAS, resource, and authority relationship.

**Across the client and resource domain:**

* **Client registration:** The client establishes its registration and
  authentication keys at each authorization server, or through CIMD
  where supported. Each server consumes the corresponding metadata.
* **Local principals:** The RAS provisions or synchronizes local agent
  principals and user links for RAS and API processing.
* **Applicable profile:** Client, IdP, RAS, and resource policy establish
  the profile and minimum requirements per client, trust relationship,
  and resource; all roles enforce their applicable requirements.
* **Access-token protection:** The RAS and client configure protection
  per resource for client, RAS, and API use ({{access-token-protection}}).
  `token_type` distinguishes DPoP, but not mutual TLS from bearer.

Discovery exposes capabilities, not these authorization decisions:

* Credential metadata follows its credential specification; discovery
  MUST NOT establish trust.
* {{CIMD}} can supply client metadata where supported. RAS metadata
  under {{RFC8414}} confirms grant and profile support.
* Bindings, associations, delegation, and local links have no discovery
  mechanism here. Profile metadata does not establish acceptance policy
  ({{discovery}}).

Existing workload-federation configuration can supply credential trust
and exact identity selectors. The Agent Principal mapping and separate
Client Association are still required, but no new configuration object
types are prescribed. {{identity-example}} illustrates the shared-client
case; {{aws-example}} applies the model to an AWS STS workload credential.

Request hints, discovered client metadata, and unverified JWT claims
MUST NOT by themselves establish credential-authority trust or change
an approved Identity Binding or Client Association. Creating and changing bindings
and associations, including imports from platform registries, is an
administrative act outside this profile ({{operational-guidance}}).

## Identity Mapping Example {#identity-example}

Alice asks a data-analysis agent to read a file. The platform uses one
shared OAuth client for many agents, so its client identifier alone
cannot identify which agent is acting. This non-normative example uses
the optional SPIFFE input to make that distinction.

The request passes four separate decisions:

1. **Resolve the agent.** The IdP validates the
   workload's JWT-SVID. An Identity Binding maps its exact SPIFFE ID,
   `spiffe://platform.example/accounts/acme/agents/workload-7`, to
   `agent-42` in the namespace of `https://idp.example/`. The agent
   belongs to Governance Tenant `acme`.
2. **Authorize the client.** The IdP's configured SPIFFE
   association authenticates the caller as `platform-sso`. A separate
   Client Association permits that client to use this Identity Binding
   for delegated ID-JAG issuance. Authenticating the client does not
   grant that permission.
3. **Authorize delegation.** Alice's ID Token identifies her as
   `alice-app` and was issued for `platform-sso`. The IdP authorizes
   `agent-42` to act for her with `files.read` at the requested resource
   in Target Tenant `acme-data`, and issues an ID-JAG for the RAS.
4. **Apply resource policy.** The RAS resolves
   Alice to its local user `user-108` and correlates the IdP-qualified
   agent with local principal `service-principal-42`. Alice has the
   file permission, and resource policy permits this agent to act for
   her. In this example, the agent needs no separate file ACL.

The resulting tokens show which identities change across the boundary:

| Claim | ID-JAG issued by IdP | Access token issued by RAS |
|---|---|---|
| `sub` (Alice) | `alice-ras` | `user-108` |
| `act.iss` (agent namespace) | `https://idp.example/` | `https://idp.example/` |
| `act.sub` (Agent Principal) | `agent-42` | `agent-42` |
| `client_id` (client at RAS) | `platform-api` | `platform-api` |
| `scope` | `files.read` | `files.read` |

`alice-ras` is Alice's identifier in the target SSO namespace;
`platform-api` is the registration corresponding to `platform-sso` at
the RAS. The RAS translates the user and preserves the agent. Its local
agent record supports authorization; `service-principal-42` does not
replace `act.sub`.

If the agent later runs under another approved workload identity, a
second Identity Binding can resolve it to the same `agent-42`. Client
Association must permit that binding too. The downstream agent identity
then stays unchanged, and either binding can be disabled independently.

{{shared-client-example}} supplies the credential and request details
for this scenario, using the complete message sequence in {{walkthrough}}.

## Requirements by Implementer {#profile-requirements}

This non-normative index locates requirements by role. The differences
from the underlying protocols are summarized in {{profile-additions}}.

| Implementer | Requirement | Defined in |
|---|---|---|
| Client or platform | Supply credentials accepted by the configured agent-resolution input | {{evidence}} |
| Client | Select supported inputs, authenticate, satisfy the selected grant protection, and retain token context | {{scope}}, {{grant-protection}}, {{exchange-request}}, {{redemption}}, {{client-token-reuse}} |
| IdP | Validate evidence, resolve the agent, enforce the Client Association, and authorize delegation | {{inputs}}, {{identity}}, {{authorization}} |
| IdP | Construct the governed actor and issue the governed ID-JAG | {{actor-construction}}, {{grant-issuance}} |
| IdP and RAS | Resolve and link the user in the target namespace | {{subject-resolution}} |
| RAS | Validate and redeem the grant; apply local authorization and token-protection policy | {{redemption}} |
| API | Enforce profile applicability, actor authorization, tenant, and token protection | {{api-processing}} |
| Client, IdP, and RAS | Configure capabilities, advertise support, and process failures | {{metadata}}, {{errors}} |

# Agent Resolution Inputs {#evidence}

The inputs below resolve either an authenticated dedicated-client
identity or an independently validated workload identity. Each defines
credential validation, the identity used for binding, and any proof
requirements. The separation of authentication, resolution, and
permission in {{inputs}} applies to every input.

Input support follows {{scope}}; alternatives are in {{optional-inputs}}.
Support does not establish trust in a credential authority or permission
to use a binding.

Clients and platforms use existing credential mechanisms. For workload
evidence, those mechanisms MUST authorize issuance for the asserted
workload identity; a caller-supplied subject or agent identifier alone
MUST NOT establish that identity. For dedicated clients, the IdP relies
on the configured client-authentication method and approved binding.
Credential acquisition is outside this profile.

Audience validation follows the input's credential specification and
this profile's requirements; there is no universal IdP audience:

| Input | Audience rule | Source |
|---|---|---|
| Dedicated client using `private_key_jwt` | IdP token endpoint URL by default; an explicitly configured identifier for that AS is permitted | {{RFC7523, Section 3}} permits AS audience identifiers; {{client-assertion-input}} requires endpoint-URL support and defines configuration |
| SPIFFE JWT-SVID | IdP issuer identifier as the sole audience | {{SPIFFE-OAUTH, Section 3.1}} |
| Existing platform JWT | Configured audience authorizing presentation to the IdP as workload evidence | Credential issuer's profile and {{imported-jwt-input}}; may be the token endpoint URL |
| Client Attestation | Attestation and accompanying proof follow their distinct audience rules; no generic JWT audience is added to the attestation | {{ATTEST}} and {{agent-evidence}} |

## Dedicated Client Identity {#client-assertion-input}

This mode resolves an authenticated OAuth client identity to its
explicitly bound Agent Principal. Client authentication uses an
asymmetrically signed assertion under {{RFC7523}}; no separate
platform-issued credential is required. The common method is
`private_key_jwt`; other configured asymmetric RFC 7523 methods MAY
be supported.

### Presentation and Resolution

The assertion authenticates the client; it is not independent workload
evidence. In this explicitly configured mode, the IdP uses the validated
client-authentication context as the resolution source. The Identity
Binding determines the Agent Principal; client authentication alone does
not authorize its use.

The client MUST present its assertion in `client_assertion`, with
`client_assertion_type` set to
`urn:ietf:params:oauth:client-assertion-type:jwt-bearer`, and MUST omit
`actor_token` and `actor_token_type`. The IdP MUST reject either actor
parameter in this mode with `invalid_request`.

This profile defines the authenticated-client resolution composition;
it is not Actor Profile's dual-presentation input. Its relationship to
Token Exchange and Actor Profile is stated in
{{dedicated-client-coordination}}. Mode selection and missing-evidence
handling follow {{actor-inputs}}.

The IdP MUST:

* **Authentication:** Authenticate the client under {{RFC7523, Sections 3
  and 3.2}} and
  its configured authentication method, including issuer trust,
  signature, audience, expiration, and replay checks. The assertion's
  `sub` MUST equal the authenticated IdP `client_id`.
* **Key trust:** Use verification keys authorized for that client and
  assertion issuer.
  Assertion-supplied keys or issuer claims MUST NOT establish trust.
* **Resolution:** Resolve the exact validated (`iss`, `sub`) in the IdP's
  client-registration
  context through an enabled Identity Binding to one Agent Principal.
  Then enforce Client Association and delegation authorization separately.

For `private_key_jwt`, apply Section 9 of {{OPENID}}: the assertion issuer
and subject are the client's registered identifier.

### Assertion Audience

RFC 7523 client authentication uses these audience rules at both the
IdP and RAS:

* Clients and servers MUST support the token endpoint URL. The client
  MUST use that URL unless trusted configuration explicitly establishes
  another identifier for the same AS, such as its issuer identifier.
* The assertion's `aud` MUST contain the configured identifier, which
  the AS MUST compare using exact string matching under
  {{RFC7523, Section 3}}. The assertion MUST NOT establish the accepted
  audience configuration.
* A client MAY retry with another audience already authorized by trusted
  configuration for the same AS. An error response MUST NOT establish
  that authorization or broaden the configured audience set. Retries
  remain subject to {{client-assertion-input}}'s replay requirements.

This defines a common default while permitting existing AS audience
conventions; it does not change other credential classes' audience rules.

### Replay and Retries

For dedicated-client resolution, this profile prohibits negotiated
assertion reuse. These replay requirements narrow the base specifications:

* The assertion MUST contain a `jti`.
* The IdP MUST reject reuse in another request while the assertion
  remains acceptable.
* Replay identifiers MUST be qualified by the validated issuer and client.

For a retry of a dedicated-client exchange:

* The client MUST generate a new `client_assertion` with a fresh `jti`.
  This also applies after a `use_dpop_nonce` challenge under
  {{RFC9449, Section 8}}.
* For a nonce retry, the client MUST also generate a fresh DPoP proof
  containing the supplied nonce while retaining the grant proof key.

The IdP may already have consumed the previous assertion during
authentication. Changing only the DPoP proof does not satisfy the
assertion replay rule.

### Identity and Proof Boundaries

The client and agent remain distinct principals. This mode does not
distinguish agents behind one shared client identity; such a client
MUST present separate supported workload evidence in `actor_token`. An
additional agent claim in a self-signed client assertion MUST NOT select
another Agent Principal under this input.

Assertion signing authenticates the client; it does not bind the ID-JAG
to that signing key or establish an attested runtime identity. Grant
proof processing follows {{grant-protection}} independently, and the
DPoP key MAY differ from the client-authentication key. An assertion
carrying `cnf` MUST NOT be accepted unless its configured authentication
method defines and validates the corresponding proof.

{{client-assertion-example}} illustrates this input without SPIFFE.

## SPIFFE JWT-SVID {#jwt-svid-input}

This OPTIONAL input supports workload identity independently of the
OAuth client identifier, including multiple agents behind a shared client.

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

# Agent Principal Resolution {#identity}

Resolution turns validated inputs into principals: the Identity
Binding resolves a qualified client or workload identity to one Agent Principal,
subject resolution identifies the user for delegated access, and the
RAS correlates both to its local principals.

## Identity Binding {#identity-binding}

| Input | Identity used for resolution | Qualification |
|---|---|---|
| Dedicated client identity | Trusted assertion issuer and exact client `sub`, qualified by the IdP client-registration context | Common mode under {{client-assertion-input}}; explicit client-to-agent binding |
| SPIFFE JWT-SVID | Approved trust domain and exact SPIFFE ID in `sub` | Optional input under {{jwt-svid-input}}; native client authentication |
| Existing platform JWT | Approved issuer and exact subject, with configured additional selectors | Optional input under {{imported-jwt-input}} |
| Client Attestation whose attested client maps explicitly to one Agent Principal | Trusted attester and validated Client Attestation `sub` under {{agent-evidence}} | The validated `sub` identifies the OAuth client; client-to-agent mapping is explicit |

After validating the configured resolution input, the IdP MUST:

* Resolve the exact qualified client or workload identity to one active
  Agent Principal through an enabled Identity Binding; reject missing,
  ambiguous, or disabled mappings.
* Apply exact resolution even when client authentication permits a
  prefix match. A client identifier, including a {{CIMD}} URL,
  identifies the client, not the agent.

Similar names, unqualified identifiers, or a shared signing key MUST
NOT establish identity equivalence. The table above defines the
qualified identity for each input.

Deployments SHOULD permit an Identity Binding to be disabled independently
of the Agent Principal and its other bindings.
A disabled binding MUST NOT authorize new grant issuance. Disabling
a binding does not itself revoke outstanding tokens; their treatment
follows {{status-changes}}.

The IdP MUST verify a Client Association that permits the authenticated
client to use the selected Identity Binding in the selected flow with
the selected credential class ({{flow-configuration}}). The IdP
MUST NOT substitute the client's identity for the resolved actor.

A Client Association MAY authorize one or more Identity Bindings. The
IdP MUST determine explicitly whether the selected binding is within
that authorization. Authorization of one binding, a credential
authority, a credential class, or the Agent Principal itself MUST NOT
imply authorization of another binding unless the association's policy
explicitly includes it. No association overrides a disabled binding.
Policy representation and evaluation mechanisms are outside this profile.

For a dedicated client, Identity Binding determines which Agent Principal
the client represents. Client Association independently determines
whether that client may exercise the binding in the requested flow.
Deployments MAY administer both in one registration or policy object;
their identity and authorization semantics remain distinct.

A binding can remain valid while permission to use it is withdrawn,
preserving identity continuity across policy changes. Credential class
constrains the authorized resolution path even when several classes
can resolve to the same Agent Principal.

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

User-account links have these constraints:

* **Authority:** A link between an external user and a local account
  MUST rest on an authoritative association, not on email, username,
  or display-name equality alone.
* **Uniqueness:** Each qualified external identity MUST resolve to at
  most one local account per Target Tenant.
* **Continuity:** A link change MUST NOT transfer an outstanding grant
  or delegation to another user.
* **Failure:** The IdP and RAS MUST reject issuance for a disabled user
  or missing, ambiguous, or conflicting resolution ({{errors}}).

Linking mechanisms are deployment choices ({{operational-guidance}}).

## Agent Principal Correlation {#agent-correlation}

The Agent Principal identity is the pair of IdP issuer and agent
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
remove, or rewrite actor members.

Preservation applies to JSON members and values, not to serialization,
whitespace, or member order.

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

Issuance and denial follow these rules:

* The IdP MAY narrow scope, reflecting the result in the grant and
  response under {{RFC8693}}. It MUST return `invalid_scope` if no scope
  can be granted.
* It MUST NOT issue by dropping a required actor or binding,
  substituting an external identifier for the Agent Principal, or
  weakening proof requirements.
* Denied delegation MUST NOT fall back to self-acting access.

## Delegation Authorization {#delegation-authorization}

Before constructing `act`, the IdP MUST authorize the resolved Agent
Principal to act for the user in the requested client, tenant, RAS,
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

The actor gate is an authorization condition, not a protocol object.
It MAY be implemented through an agent registration, tenant assignment,
consent policy, or another explicit rule. Requiring the agent to also
hold independent permissions on each object is local
policy, not a baseline requirement.

Every operation the API permits
MUST be covered by an applicable actor-gate authorization. The API MAY
evaluate the gate directly or rely on a validated RAS authorization
whose scope and freshness satisfy resource policy; a fresh policy-service
evaluation is not required for every request.

Issuing an ID-JAG under this profile asserts that the IdP authorized
the specified delegation within the grant's constraints. The RAS MUST
independently decide whether to accept that delegation under its local
user, actor, client, tenant, and resource policy. The grant does not
assert that the RAS's policy has been satisfied or convey the IdP's
underlying approval records.

Audit records SHOULD identify both the user and the issuer-qualified
actor; the client identifier MUST NOT stand in for the actor in
authorization or attribution.

# Delegated ID-JAG Realization {#delegated-flow}

This section realizes the federation model as a normative profile of
ID-JAG issuance and redemption, using the actor extension point in
{{ID-JAG, Section 9.7}}. It specifies the wire requirements for carrying
and enforcing the relationships defined in {{model}}, {{identity}},
and {{authorization}}. Where it is silent, ID-JAG applies unchanged;
the text states only additions and narrowings.

## Relationship to Base Specifications {#profile-additions}

Token Exchange request and response syntax, the ID-JAG format,
`jwt-bearer` redemption, and DPoP proof processing are inherited from
{{RFC8693}}, {{ID-JAG}}, and {{RFC9449}}. This non-normative table
identifies this profile's additions and deliberate narrowings; the
referenced sections define the requirements.

| Area | Profile requirement | Defined in |
|---|---|---|
| Actor extension | Resolve dedicated-client or workload identity through an Identity Binding; authorize client use through a separate Client Association | {{identity-binding}} |
| Dedicated-client input | Resolve from authenticated client context with no actor-token parameters; require token-endpoint audience support, explicit configuration for an alternative AS identifier, and single-use `jti` | {{client-assertion-input}} |
| Actor representation | One actor with the Agent Principal as `act.sub` and the IdP as `act.iss`; replaces Actor Profile's credential-to-actor copying | {{actor-construction}} |
| Request narrowing | Configured resolution mode, exactly one resource, and non-empty scope required; actor evidence required outside dedicated-client mode; no incoming actor chain | {{root-request}}, {{actor-inputs}} |
| Identity and client binding | Resolve users and agents separately; derive downstream `client_id` from an authoritative client-registration association | {{subject-resolution}}, {{agent-correlation}}, {{flow-configuration}} |
| Grant narrowing | One resource URI (issued as a string; singleton arrays also accepted), scope constraints, and input-specific expiration limits; bound profile requires DPoP and `cnf.jkt` | {{grant-issuance}}, {{redemption-validation}}, {{grant-protection}} |
| Resource processing | Preserve actor and tenant context; enforce the user authority and actor gate with the selected token protection | {{access-token-response}}, {{api-processing}} |
| Refresh narrowing | Explicit policy, client binding, preservation of proof binding and profile, and a finite absolute authorization expiration | {{ras-refresh}} |
| Error processing | Actor credential or resolution failures use `invalid_grant` rather than RFC 8693's default `invalid_request`; denial for a resolved actor uses `actor_unauthorized` | {{errors}} |
| Profile discovery | Identify supported governed profiles in existing ID-JAG metadata; trusted policy sets the minimum | {{metadata}} |

## Prerequisites and Common Capabilities {#flow-configuration}

Before issuance, the IdP MUST establish the applicable identity,
client, delegation, and target relationships in {{configuration}}.
Input and role capabilities are defined in {{scope}}; profile
applicability follows {{discovery}}.

The IdP MUST derive the ID-JAG `client_id` from an authoritative
association between the authenticated IdP client and that client's
registration at the target RAS. A client-supplied downstream client
identifier MUST NOT select or override that association. This
association is distinct from the Client Association that permits use
of an Identity Binding.

Each authorization server establishes authoritative client metadata
through registration or, when supported, {{CIMD}}. RFC 7523 client
authentication at either server follows {{client-assertion-input}};
JWT-SVID authentication follows {{jwt-svid-input}}. Other configured
methods MAY be used, and client identifiers and keys MAY differ
between servers.

`private_key_jwt` provides a common client-based input and redemption method
across independent implementations without provisioning a shared
client secret. It is mandatory to implement, not mandatory to use;
governed identity resolution does not depend on that method.

Neither the dedicated nor shared client model requires per-replica
registration. With CIMD and SPIFFE
authentication, client association follows {{SPIFFE-OAUTH, Section
5.1}}, including its `spiffe_id` matching rules. A client-metadata prefix
match does not replace exact Identity Binding resolution.

Each implementing role MUST support the capabilities below for the
artifacts it produces or validates:

| Artifact | Mandatory-to-implement (MTI) capability |
|---|---|
| ID-JAG | IdP signing and RAS validation: `RS256`, providing the MTI algorithm required by {{RFC7523, Section 5}} for the JWT bearer grant used at redemption |
| JWT access token | RAS signing and API validation: algorithms required by {{RFC9068, Section 2.1}}; not applicable to opaque-token consumers |
| `private_key_jwt` | Client signing and IdP/RAS validation: `RS256`, inherited from {{RFC7523, Section 5}} for JWT client authentication |
| JWT-SVID, where supported | IdP validation: `RS256` under {{RFC7523, Section 5}} as profiled by {{SPIFFE-OAUTH, Section 3.1}}; `ES256` support added by this profile |
| DPoP, where supported or required | Client proof generation and server validation: `ES256`, as this profile's MTI algorithm; {{RFC9449}} does not prescribe this minimum |

Other algorithms permitted by the selected specification MAY be used
through trusted configuration and metadata. Client authentication at
the IdP follows the selected method's algorithm requirements.

An ID-JAG containing `cnf.jkt` is bound to the DPoP key proven at issuance
and redeemed under {{grant-protection}}. The key-holder arrangements
through API use are described in {{distributed-key-use}}; independent
key transition is deferred under {{key-transition-gap}}.

Deployments choose a renewal strategy and recovery when fresh user
authorization is required under {{continuing-access}}.

## Grant Protection {#grant-protection}

The applicable profile determines whether an ID-JAG without sender
constraint is acceptable. Client authentication and all governance
requirements remain mandatory in either profile.

| Applicable profile | Grant-protection requirement |
|---|---|
| Bound governed agent access | The client MUST supply a DPoP proof at issuance; the IdP MUST reject its absence with `invalid_request`. The RAS MUST require `cnf.jkt` in the grant. |
| Governed agent access | DPoP support is OPTIONAL. The IdP and RAS MAY issue and accept grants without `cnf` only when trusted policy explicitly permits them for the client, trust relationship, and resource. |

The following rules apply to both profiles:

* **Supplied proof:** A supplied DPoP proof MUST be validated under
  {{RFC9449}}. An endpoint
  that does not support DPoP MUST reject a request containing such a
  proof with `invalid_request`; it MUST NOT silently ignore the proof.
  At issuance, a valid proof MUST result in `cnf.jkt` binding under
  {{ID-JAG, Section 9.8.1.1}}.
* **Bound grant:** A grant containing `cnf` MUST have a valid, supported
  `jkt` binding.
  The RAS MUST require a fresh DPoP proof whose public-key thumbprint
  matches exactly. Missing proof, missing required binding, unsupported
  confirmation, or key mismatch MUST fail with `invalid_grant`.
* **Unbound grant:** When policy permits a grant without `cnf`, the client
  MAY present a
  DPoP proof only at redemption to obtain a DPoP-bound access token.
  That proof protects the resulting token; it does not retroactively
  bind the grant. Access-token protection follows {{access-token-protection}}.
* **Credential proof:** Credential-specific proof requirements still apply.
  Selecting governed
  agent access MUST NOT disable proof required by the agent-resolution
  input or client authentication method.

## Token Exchange {#exchange-request}

### Request {#root-request}

The client sends an HTTPS POST to the IdP token endpoint, using
`application/x-www-form-urlencoded`, authenticates as the configured
client, and supplies any proof required by {{grant-protection}}.

The request also carries the
parameters or headers required by the configured client-authentication
method. For RFC 7523 and JWT-SVID authentication these include
`client_assertion_type` and `client_assertion`, and `client_id` where
required by the method or registration.

The following parameters are REQUIRED except where the resolution mode
specifies otherwise:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `requested_token_type` | `urn:ietf:params:oauth:token-type:id-jag` |
| `subject_token` | User ID Token, SAML 2.0 assertion, or refresh token when supported, issued for the authenticated client |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:id_token`, `urn:ietf:params:oauth:token-type:saml2`, or `urn:ietf:params:oauth:token-type:refresh_token` |
| `actor_token` | Omitted for dedicated-client resolution; REQUIRED for an actor-evidence input under {{actor-inputs}} |
| `actor_token_type` | Omitted with `actor_token`; otherwise REQUIRED with value `urn:ietf:params:oauth:token-type:jwt` |
| `audience` | One target RAS issuer identifier |
| `resource` | Exactly one resource URI under {{RFC8707}}, served by the RAS named in `audience` |
| `scope` | Non-empty scope string for the requested resource |

The two target parameters serve different purposes:

* `audience` selects the RAS that will redeem the grant.
* `resource` selects protected-resource authority at that RAS. Its URI
  conveys the Target Tenant through the configured resource-to-tenant
  association; it does not convey the IdP's Governance Tenant.

The request MUST contain exactly one `resource` parameter. A client
requiring access to multiple resources MUST obtain a separate ID-JAG
for each resource. The IdP MUST reject multiple `resource` parameters
with `invalid_target`.

This profile requires exactly one resource and a non-empty scope.
It requires `actor_token` for actor-evidence inputs and omits it for
configured dedicated-client resolution. `authorization_details` MAY
accompany `scope` and is processed under ID-JAG.

Requiring scope is a deliberate narrowing of ID-JAG for this realization,
not an identity-model invariant. It supplies a common authorization
mechanism through issuance, redemption, refresh, and API enforcement.
Structured authorization details can supplement it; RAR-only support
would require an agreed authorization-detail type and its processing
rules across those stages and remains deferred ({{excluded-compositions}}).

One resource per grant avoids carrying different scope ceilings for
different resources. The IdP MUST constrain all granted scope and
`authorization_details` to that resource.

If requested authorization details cannot be confined to it, the IdP
MUST reject the request with `invalid_authorization_details` under
{{RFC9396, Section 6}} rather than authorize additional resources.
Unsupported or invalid requested authorization details use the same
error; an unacceptable `resource` parameter uses `invalid_target`
({{errors}}).

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
  {{ID-JAG, Section 3.2}}; agent resolution and actor construction are
  unchanged.
* **Refresh token:** apply `refresh_token` grant validation, including
  client binding, validity, revocation, and proof requirements.
  * The requested scope and audience MUST remain within the token's
    retained authorization.
  * Any binding retained with that grant MUST be enforced rather than
    bypassed by selecting another agent-resolution input, with conflicts
    rejected as `invalid_grant`.

All subject inputs require a current validated agent-resolution input and delegation
authorization under {{delegation-authorization}}; the output remains an
ID-JAG. User access tokens are not subject inputs in this revision
({{access-token-subject-gap}}); JWT encoding alone does not make an
access token an ID Token.

Refresh-token eligibility includes cross-domain authorization, not
merely an SSO session:

* The IdP MUST establish that the token's retained authorization permits
  the requested target and authority under {{ID-JAG, Section 4.3.3}}.
  Possession of a refresh token or an `offline_access` grant alone
  MUST NOT establish that permission.
* The retained context may include an explicitly associated
  cross-domain delegation authorization. Its representation and
  provisioning are local to the IdP; OIDC scope names do not themselves
  map to resource-specific permissions.

For example, a token issued with `openid offline_access` is eligible
for `files.read` at `https://ras.example/` only if its authorization
context also permits that target and authority. Current agent and
delegation checks still apply. Without that authorization, the
deployment needs an authorization flow that establishes it before
unattended exchange can proceed.

### Agent Resolution Input Validation {#actor-inputs}

After client authentication, the IdP MUST determine the resolution mode
from trusted configuration for the authenticated client, applicable
profile, and target. If that configuration does not establish an
unambiguous mode, it MUST reject the request with `invalid_request`.
The presence or absence of actor-token parameters MUST NOT select or
change that mode.

* **Dedicated-client resolution:** Use the authenticated client context
  under {{client-assertion-input}}. The IdP MUST reject `actor_token` or
  `actor_token_type` with `invalid_request`.
* **Actor-evidence input:** The IdP MUST require both `actor_token` and
  `actor_token_type`. Missing either uses `invalid_request`. The type
  MUST be `urn:ietf:params:oauth:token-type:jwt`; any other type uses
  `invalid_request`. Missing or rejected evidence MUST NOT trigger
  dedicated-client resolution.

Both modes proceed through {{actor-construction}}. A governed request
MUST result in the required governed `act` or fail; omitting actor-token
parameters in dedicated-client mode does not request ordinary EMA or
subject-only impersonation.

| Input | Support | Presentation and validation |
|---|---|---|
| Dedicated client identity | REQUIRED at the client and IdP for `private_key_jwt`; use is configurable | Authenticated client context; no actor-token parameters; explicit binding under {{client-assertion-input}} |
| JWT-SVID | OPTIONAL | Identical compact JWT in `actor_token` and `client_assertion`; native JWT-SVID authentication under {{jwt-svid-input}} |
| Existing platform JWT | OPTIONAL | Existing platform JWT in `actor_token`; validate under {{imported-jwt-input}} and authenticate separately |
| Client Attestation | OPTIONAL | Identical compact JWT in `actor_token` and `OAuth-Client-Attestation`; attested client maps explicitly to one Agent Principal under {{agent-evidence}} |

The following classification rules apply only to actor-evidence inputs.
The generic JWT token type retains existing credential formats without
defining new OAuth token types. Credential semantics come from
authenticated request context and trusted configuration, not the generic
token type ({{RFC8693, Section 3}}). These paths MUST have mutually
exclusive validation rules under {{RFC8725, Section 3.12}}.

The IdP MUST classify the `actor_token` using these steps:

1. Select a native credential class when the JWT is
   byte-identical to evidence used by the configured authentication
   method:
   * `client_assertion` with assertion type
     `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe`, used for
     JWT-SVID authentication, selects JWT-SVID.
   * `OAuth-Client-Attestation` used for Client Attestation
     authentication selects Client Attestation.
2. Otherwise, an issuer and credential class configured for the
   authenticated client's existing platform JWT input select that
   input. Apply its configured classification rules under
   {{imported-jwt-input}}; a generic `typ=JWT` alone is insufficient.

The IdP MUST reject a credential matching no configured class or more
than one class with `invalid_request`. Classification selects validation
rules; unverified claims do not establish trust.

Within one token
request, once a credential class is selected, the IdP MUST NOT validate
the credential under another class after rejection by the selected
class's validation or authorization rules.

For Client Attestation, the authentication method determines proof use:

* With `attest_jwt_client_auth`, any grant proof key MUST match the
  attestation's confirmation key, narrowing ATTEST's allowance for a
  separate DPoP key.
* With `attest_jwt_client_auth_dpop`, the keys are already one and its
  DPoP proof serves both roles.

ATTEST's errors apply.

To preserve the single user-to-agent relationship, the IdP MUST reject
an `actor_token` or ID Token containing `act`, and a refresh-token
subject whose retained authorization contains an actor chain.

### Actor Resolution and Construction {#actor-construction}

After credential validation, the IdP MUST resolve the agent under
{{identity}} and authorize issuance under {{authorization}}. The
ID-JAG MUST contain one `act` object with:

* `sub`: the Agent Principal identifier from the Identity Binding.
* `iss`: this IdP's issuer identifier.

These values MUST come from the approved mapping, even when source
and governed identifiers coincide. For actor-evidence inputs this
replaces credential-to-actor copying in {{ACTOR-PROFILE, Section 6.3}};
for dedicated-client resolution it uses the authenticated client context
under {{client-assertion-input}}.

The object MUST follow {{ACTOR-PROFILE, Section 3.4}}, including its
`sub_profile` recommendation and unclassified-actor rules. Any
`sub_profile` MUST reflect the IdP's authoritative classification.
{{ENTITY-PROFILES}} defines `service` and `ai_agent`; being an Agent
Principal does not itself establish the `ai_agent` classification.

### Grant Issuance {#grant-issuance}

The ID-JAG MUST use the format and claims of {{ID-JAG, Section 3.1}}
and additionally satisfy:

| Claim | Required result |
|---|---|
| `sub` | Same user as the validated subject credential, expressed in the IdP's subject namespace for the RAS |
| `act` | Agent Principal actor constructed under {{actor-construction}} |
| `cnf.jkt` | Thumbprint of the grant proof key when DPoP is used at issuance; REQUIRED for bound governed agent access ({{grant-protection}}) |
| `resource` | The authorized resource URI, issued as a JSON string; receivers also accept a single-element array under {{redemption-validation}} |
| `scope` | Non-empty authorized scope string, no broader than the approved request |
| `client_id` | The client's registration identifier at the RAS, derived under {{flow-configuration}} |

The IdP MUST NOT issue a grant if it cannot determine an unambiguous
user, actor, downstream client, or tenant relationship.

Grant lifetime has three limits:

* **Configured limit:** The grant lifetime SHOULD be at most five
  minutes and MUST NOT exceed the configured lifetime limit.
* **Subject credential:** The grant's expiration MUST NOT exceed the subject
  credential's expiration, determined below.
* **Agent-resolution input:** For dedicated-client resolution under
  {{client-assertion-input}}, the client assertion MUST be valid when
  the request is authenticated, but its expiration does not limit the
  issued grant's lifetime. For every other agent-resolution input, the
  grant MUST NOT outlive the validated credential.

The dedicated-client assertion authenticates one transaction rather
than defining a continuing workload-evidence validity window.

Subject-credential expiration is determined as follows:

* **ID Token:** its `exp` claim.
* **SAML assertion:** the earliest applicable `NotOnOrAfter` in the
  assertion's `Conditions` and the `SubjectConfirmationData` used to
  validate the subject. If neither supplies an expiration bound, the
  IdP MUST reject the subject as `invalid_grant`.
* **Refresh token:** its expiry, if the IdP records one. If no expiry is
  recorded, the configured grant-lifetime limit and applicable
  agent-resolution input limit still apply. Current refresh-token
  validity and delegation authorization remain required; absence of
  a recorded expiry does not authorize an unlimited grant lifetime.

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
3. **Authority:** Validate the resource, scope, and authorization details:
   * **Resource claim:** Require `resource` to be a URI encoded as a
     JSON string or a JSON array containing exactly one URI string,
     consistent with {{ID-JAG, Section 3.1}}. Normalize either
     representation to that URI; reject missing or invalid values,
     empty arrays, and arrays with multiple elements with `invalid_grant`.
   * **Requested resource:** The requested resource MUST match the URI
     exactly or the RAS MUST return `invalid_target`.
   * **Scope:** Require the grant's `scope` claim to be a non-empty
     string. A supplied request `scope` MUST be a non-empty subset of
     that claim or the RAS MUST return `invalid_scope`; omission retains
     the claim as the ceiling.
   * **Authorization details:** Apply ID-JAG's processing for
     `authorization_details`; reject the grant with `invalid_grant`
     if its authority extends beyond that resource.
4. **Local authorization:** Resolve the user under
   {{subject-resolution}} and the Agent Principal actor under
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
* **Tenant:** By default, the resource URI is tenant-specific and the
  access-token audience identifies the authorized Target Tenant under
  {{RFC8707, Section 3}}. An existing tenant claim or authoritative token
  context MAY replace that representation only by explicit RAS/API
  configuration. In every mode the API MUST resolve the authorized
  tenant unambiguously; a request parameter alone cannot establish it.
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
possession alone does not redeem the grant. In this mode:

* The DPoP key protects grant redemption and any DPoP-bound refresh token.
* The mutual-TLS key protects subsequent access-token use.
* The access token carries only `cnf.x5t#S256`, not `cnf.jkt`, and the
  response uses `token_type=Bearer`.

This uses RFC 9449 Section 5's allowance for access tokens that are not
DPoP-bound; receipt of the grant proof does not override the configured
access-token protection. A native mutual-TLS-bound grant
is future work ({{excluded-compositions}}).

Bearer issuance accommodates resources without sender-constraint
support; the RAS MUST still enforce any grant binding. The RAS MUST NOT
copy the grant's `cnf` into an access token whose binding will not be
enforced, and clients and APIs MUST NOT treat
a constrained token as an unconstrained bearer token or bypass an
unrecognized confirmation method.

### Distributed Platforms and Key Use {#distributed-key-use}

Bound-grant issuance and redemption require the same key holder. For
a DPoP access token, API use also requires proofs from that key; handing
only the token to a worker with an independent key is insufficient.

| Arrangement | Requirement through API use |
|---|---|
| Broker obtains and uses the token | Broker holds the grant proof key and calls the API, including when proxying an authorized worker request |
| Worker uses a DPoP token | Worker holds the same key or obtains request-specific proofs from its authorized key holder; a remote signing interface and its authorization are outside this profile |
| Another access-token protection mode | Explicitly configured bearer use needs no API proof key; mutual TLS requires the certificate key to which the RAS bound the access token at redemption |

Remote signing or shared key custody does not establish an independent
worker binding and expands the trusted computing base. This revision
defines no handoff to a worker's independent DPoP key
({{key-transition-gap}}). Access-token and refresh-token bindings remain
subject to {{access-token-protection}} and {{ras-refresh}}.

### Opaque Access Tokens and Introspection {#introspection}

The RAS MAY issue an opaque access token instead of a JWT when the API
obtains equivalent context through token introspection {{RFC7662}}.
In that case:

* **Endpoint:** Endpoint authentication and token-state processing follow
  {{RFC7662, Sections 2 and 4}}.
* **Identity and authority:** The response MUST carry `sub`, `aud`, `scope`,
  `client_id`, and the
  validated `act` object unchanged, using the `act` introspection
  member registered by {{RFC8693, Section 7.5}}.
* **Context:** The response MUST preserve the Target Tenant representation and any
  effective `authorization_details` required by {{access-token-response}}.
* **Protection:** For a bound token the response MUST carry `cnf` with `jkt` under
  {{RFC9449, Section 6.2}} or `x5t#S256` under
  {{RFC8705, Section 3.2}}, and the API MUST enforce it as it would
  the JWT claim.
* **Caching:** Caching follows {{RFC7662, Section 4}} and the resource's disablement
  freshness policy. A cached active response MUST NOT be used beyond
  `exp` or that policy's freshness limit. Without `exp`, the API MUST
  introspect again for subsequent requests rather than reuse an active
  response. This restriction narrows RFC 7662 so cached authorization
  cannot outlive an expiration unknown to the API.

The processing in {{api-processing}} applies to the introspected
context exactly as to JWT claims. Deployments also applying
{{AGENT-LIFECYCLE}} use that companion's configured enforcement mode:
online introspection forbids active-response reuse, while bounded
introspection caching imposes an explicit cache interval in addition
to the limits above.

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

* **Client and proof:** Authenticate the bound client and enforce any sender
  binding under
  RFC 9449 or RFC 8705. Dropping or replacing a sender binding requires
  a new grant in this revision.
* **Authorization context:** Preserve the user, qualified actor, Target
  Tenant, resource, and
  authorization ceiling, including `authorization_details`. Apply
  current local user and actor policy and {{RFC9396, Section 6}}.
* **Profile:** Enforce current minimum-profile policy against the profile under
  which the grant was accepted; reject with `invalid_grant` if it no
  longer qualifies. Adding a proof does not upgrade that authorization.
* **Lifetime:** Enforce a finite absolute authorization expiration set at issuance
  under local policy and an inactivity limit under {{RFC9700}}.
  Rotation, refresh, or repeated redemption of the same ID-JAG MUST NOT
  reset the absolute expiration.
* **Output:** Issue access tokens under {{access-token-response}} and
  {{access-token-protection}}, expiring no later than the absolute
  authorization expiration.

This is RAS-local authorization context; no refresh-token format or
storage representation is defined. Absolute expiration prevents
indefinite renewal from one ID-JAG without a fresh IdP decision.

Continued access beyond that expiration requires a new ID-JAG and new
IdP and RAS authorization decisions, establishing a new period rather
than extending the old one.
IdP refresh-token and delegation policy, together with any cumulative
RAS limits, bound overall unattended access. IdP revocation reaches
existing RAS authorization only through a signal or online check
({{status-changes}}).

## Token Endpoint Error Responses {#errors}

Token endpoint errors follow {{RFC6749, Section 5.2}}, {{RFC8693,
Section 2.2.2}} for Token Exchange, {{RFC8707, Section 2}} for resource
parameters, {{RFC9396, Section 6}} for requested authorization details,
and the applicable authentication and proof methods.
Servers MUST validate client authentication, credentials, and proofs
before authorization. This profile specifies the following outcomes:

**Request, client authentication, and proof**

| Failure | Error |
|---|---|
| Missing required request parameter, unsupported input combination, or ambiguous credential classification | `invalid_request` |
| No unambiguous configured resolution mode, actor-token parameters in dedicated-client mode, or missing actor-token parameters in actor-evidence mode | `invalid_request`; no mode fallback |
| Unsupported `actor_token_type` in actor-evidence mode | `invalid_request` |
| Missing required issuance DPoP proof, or DPoP supplied to an endpoint that does not support it | `invalid_request` |
| Failed RFC 7523 client authentication | `invalid_client`; other methods use their specified authentication errors |
| Invalid DPoP proof or required nonce challenge | `invalid_dpop_proof` or `use_dpop_nonce`, as specified by RFC 9449 |
| Missing required grant binding or redemption proof, unsupported confirmation, mismatch with grant `cnf.jkt`, or authenticated client differing from the grant's `client_id` | `invalid_grant` under {{grant-protection}} and ID-JAG client processing |

**Target and authority**

| Failure | Error |
|---|---|
| Unacceptable `resource` parameter at exchange, redemption, or refresh, including multiple values or a target outside the grant or retained authorization | `invalid_target` under RFC 8707 |
| Requested authorization details are unsupported, invalid, exceed permitted authorization, or cannot be confined to the single resource | `invalid_authorization_details` under RFC 9396 |
| Issued ID-JAG has invalid resource or authorization-detail claims, including authority beyond its single resource | `invalid_grant`; the assertion violates this profile |
| Target Tenant cannot be resolved for the requested resource | `invalid_target` |
| Unacceptable requested scope, invalid scope reduction, or no non-empty scope can be issued | `invalid_scope` |

**Identity resolution and delegation**

| Failure | Error |
|---|---|
| Invalid subject or agent-resolution credential, disallowed inbound actor chain, or invalid ID-JAG | `invalid_grant` |
| User cannot be resolved, user or required link is disabled, or subject identifiers conflict | `invalid_grant`; no token or automatic linking fallback |
| Absent, disabled, or ambiguous Identity Binding, or no active Agent Principal can be resolved | `invalid_grant` |
| Governance Tenant cannot be resolved unambiguously from trusted identity and configuration context | `invalid_grant` |
| Resolved Agent Principal, but no Client Association permits the selected binding and flow, or delegation is unauthorized | `actor_unauthorized`, as defined by Actor Profile, with HTTP 400 |

Agent-resolution credential failures use `invalid_grant` instead of
the default `invalid_request` described by RFC 8693; this narrowing is
intentional.
When DPoP is used, proof and nonce errors follow {{RFC9449}} at both
endpoints; unsupported DPoP and missing required issuance proof follow
{{grant-protection}}.

Client authentication failures use the authentication method's error,
including when JWT-SVID or Client Attestation also serves as actor
evidence. Error descriptions
SHOULD NOT reveal identity, binding, or policy details beyond those
disclosed by the error category. Distinguishing `invalid_grant`
from `actor_unauthorized` reveals that an actor was resolved but denied
authorization, including to a holder of stolen bearer evidence who
satisfies the request's other authentication requirements. It does not
distinguish the individual binding-resolution failures.

## Continuing Access {#continuing-access}

Deployments select a renewal model before scheduling unattended work:

| Mechanism | Conditions |
|---|---|
| Redeem an existing ID-JAG | Grant remains valid; any required proof and current RAS policy apply ({{redemption}}) |
| Obtain a new ID-JAG | Valid subject credential, current agent-resolution input, and a fresh IdP authorization decision ({{exchange-request}}) |
| RAS refresh | Preserves authorization at the same RAS within its lifetime and policy limits ({{ras-refresh}}) |

An IdP refresh token can supply the subject credential for a new
exchange only when eligible under {{subject-token-validation}};
otherwise renewal may require user interaction.
The five-minute ID-JAG recommendation bounds redemption, not task
duration. Cross-domain continuity using Identity Continuation Assertion
{{ICA}} is a separate, deferred composition ({{excluded-compositions}}).

## Client Token Reuse {#client-token-reuse}

The client MUST associate each cached grant, access token, and refresh
token with its authorized context:

* User and Agent Principal.
* Governance and Target Tenants.
* OAuth client registrations, target RAS, and resource.
* Authority, applicable profile, and proof binding.

It MUST reuse a token or grant only when that context authorizes the
operation. A shared client
identifier or matching scope alone MUST NOT permit reuse across agents,
users, or tenants.

The association can use trusted request and configuration context;
clients need not parse opaque tokens. If the client cannot establish
the required association, it MUST obtain a token or grant for the current
context. A credential change alone need not invalidate cached tokens
when the governed principal and authorization context remain the same.

## Resource Server Processing {#api-processing}

The RAS and API MUST establish profile applicability through trusted
issuer, client, and resource configuration or authoritative token-issuance
context. The RAS MUST NOT issue governed and ordinary tokens for the
same client and resource unless the API can distinguish them through
validated claims or authenticated introspection context. This profile
defines no discriminator for mixed populations.

The API MUST reject ambiguous applicability and reject missing or
malformed `act` for a configured governed population. An ordinary
`act` claim alone does not establish governed issuance. Both governed
profiles require the same API processing; their grant protection is
enforced by the RAS independently of access-token protection.

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

{{AGENT-LIFECYCLE}} adds lifecycle enforcement when that companion is
configured. Its expiring-JWT mode retains offline validation with an
explicit token-lifetime ceiling; its introspection modes bound the
time an active response can be relied upon. This document alone does
not impose those additional modes or their disablement guarantees.

If the API delegates authorization evaluation to a policy decision
service, it MUST preserve the distinction between the user, the
issuer-qualified Agent Principal, and the OAuth client, and supply the
tenant and token constraints needed to evaluate the requested operation.
{{AUTHZEN}} provides an optional evaluation interface; this profile
defines no AuthZEN message mapping and requires no particular policy
engine. A policy permit does not override the token's constraints.

For example, reserve `platform-api` for governed tokens and
`interactive-web` for ordinary user tokens under a trusted RAS issuer.
The API rejects a `platform-api` token without `act`.

### Error Responses {#resource-errors}

Challenges and scope errors use the selected protection mechanism:
`DPoP` under {{RFC9449, Section 7.1}}, or `Bearer` under {{RFC6750}} for
bearer and mutual-TLS tokens.

| Failure | Response |
|---|---|
| Missing or invalid required actor claims; unauthorized namespace assertion; missing, ambiguous, or conflicting token tenant context | HTTP 401, `invalid_token` |
| Denial for a valid actor identity | HTTP 403, `actor_unauthorized` under {{ACTOR-PROFILE, Section 8.2}} |

Actor denial MUST NOT use `insufficient_scope`. The API MUST NOT expose
actor-specific rejection details outside the trust domain.

# Optional Agent Resolution Inputs {#optional-inputs}

The inputs in this section are OPTIONAL. Existing platform JWTs and
Client Attestations support agent resolution; X.509-SVIDs and WIT-SVIDs
support client authentication only. Each composition requires trusted
configuration under {{flow-configuration}}.

## Existing Platform JWT {#imported-jwt-input}

This input accepts existing signed platform JWTs without requiring a
new media type or reissuance in a federation-specific format. The
client presents the JWT as `actor_token` and authenticates separately
with a configured method. The IdP MUST explicitly configure the
accepted issuer, credential class, and authenticated client. Credential
classification and rejection follow {{actor-inputs}}.

The Identity Binding MUST specify an exact issuer and `sub` and MAY
require additional string values from the JWT Claims Set, including
nested claims. Additional selectors MUST use the JSON Pointer string
representation in {{RFC6901, Section 5}}, evaluated from the Claims Set
root under {{RFC6901, Section 4}}:

* **Exact value:** Every selector MUST resolve unambiguously to a string equal to its
  configured value, without type conversion, case folding, or Unicode
  normalization. Missing paths, evaluation errors, non-string values,
  or unequal values MUST prevent that binding from matching.
* **No patterns:** Selectors MUST NOT use wildcard, prefix, or pattern matching, and
  MUST NOT replace the exact issuer and `sub` checks.
* **Claim authority:** A caller-controlled claim MUST NOT distinguish agents
  unless trusted
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

An AWS STS example appears in {{aws-example}}.

## Client Attestation {#agent-evidence}

Client Attestation is an OPTIONAL agent-resolution input where the
attested OAuth client identity maps explicitly to one Agent Principal.

* **Client presentation:** The client MUST present the identical compact
  JWT in `actor_token` and the `OAuth-Client-Attestation` header and
  authenticate with the configured ATTEST method.
* **Validation:** The IdP MUST validate the attestation and proof under
  {{ATTEST}} before resolving the agent ({{actor-inputs}}).
* **Resolution:** The IdP MUST identify the attester unambiguously from
  the trusted verification key and configured attester-to-client
  associations, and resolve the trusted attester and validated Client
  Attestation `sub` through an approved Identity Binding. An `iss`, when
  present, MUST match that authority; base ATTEST does not require it.

Unlike ordinary dedicated-client resolution from a registered client
key, this input relies on a trusted attester's endorsement of client
identity and its confirmation key. Runtime or workload provenance is
established only to the extent supported by verified attestation claims
and the attester's trusted issuance policy; Client Attestation alone
does not imply those properties.

This input does not distinguish agents behind a shared client; those
agents need distinct workload evidence, such as a JWT-SVID or an
accepted platform JWT. Instance-based resolution
and attester endorsement are deferred ({{excluded-compositions}}).

## SPIFFE X.509-SVID and WIT-SVID Client Authentication {#spiffe-input}

X.509-SVID MAY authenticate the client under {{SPIFFE-OAUTH, Section
3.2}}, and WIT-SVID under {{SPIFFE-OAUTH, Section 3.3}} and {{WIT}},
including their proof and key-use requirements:

| Authentication credential | Validated client identity |
|---|---|
| X.509-SVID | Approved trust domain and exact SPIFFE ID in the URI SAN |
| WIT-SVID | Approved trust domain and exact SPIFFE ID in `sub` |

Either request still requires a separate supported agent-resolution
input. These authentication identities alone do not produce an Identity
Binding in this revision ({{excluded-compositions}}).

## Bearer Evidence Limits {#credential-requirements}

Where issuer endorsement of the proof key is required, the deployment
MUST use a supported input that cryptographically binds the key, such
as Client Attestation under {{agent-evidence}}; DPoP co-presented with
bearer JWT-SVID or unbound platform JWT evidence establishes possession only.
DPoP MUST NOT substitute for a credential proof that the selected input
requires.

Bearer-evidence theft remains a threat even when the output is
sender-constrained ({{security}}). Shared workload identities also do
not distinguish replicas ({{excluded-compositions}}).

Bearer evidence establishes the credential authority's assertion of
the workload identity, not a cryptographic binding of the current
presenter to that workload. The attack proceeds as follows:

1. An attacker obtains acceptable bearer workload evidence.
2. The attacker satisfies the request's client authentication, Client
   Association, user-credential, and delegation checks.
3. The attacker obtains a grant while impersonating the workload and
   can choose its own grant proof key.

In the JWT-SVID path, the same bearer credential also satisfies client
authentication; that check is not an independent possession factor.

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
  * Include `private_key_jwt` in `token_endpoint_auth_methods_supported`.
  * When JWT-SVID is supported, include `spiffe_jwt` under
    {{SPIFFE-OAUTH, Section 4}}. The generic JWT actor token type alone
    does not advertise JWT-SVID client authentication.
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

1. **Establish policy:** Before exchange, trusted configuration MUST
   establish the applicable
   governed profile and minimum requirements for the client, issuer
   trust relationship, and target resource. The client, IdP, and RAS
   MUST use that configuration. Client identity, issuer context, and
   target resource identify the applicable policy; this document defines
   no transaction-level profile negotiation.
2. **Enforce the minimum:** Each server MUST enforce its configured minimum
   regardless of absent
   `actor_token`, `act`, DPoP, or `cnf`. Their presence or absence MUST
   NOT select a different profile. Metadata advertises capabilities;
   it MUST NOT authorize a lower profile or override resource policy.
3. **Prevent fallback:** Implementations MUST NOT retry a failed governed
   request as ordinary
   EMA or drop proof to retry as governed agent access. A lower profile
   requires a separately authorized configuration, not an error-driven
   fallback.
4. **Enforce resource policy:** The RAS and API MUST agree on the minimum
   profile for their resource.
   The API relies on the RAS to enforce grant protection; an access
   token's `cnf` describes its own protection and does not establish
   which grant profile was used. Where multiple paths share a resource,
   applicability follows {{api-processing}}.

An implementation MAY serve existing EMA and either governed profile
concurrently under these rules. Supporting the bound profile does not
require accepting grants without sender constraint or advertising the
intermediate profile.

Migration changes the configured profile after
the participating roles implement its requirements; it does not relabel
previously issued grants or refresh tokens.

Before using the delegated path:

* **Issuance support:** The client and IdP MUST agree through trusted
  configuration on issuance support and any options; generic JWT or
  authentication-method support is insufficient.
* **RAS capabilities:** The client MUST verify the RAS's profile
  advertisement, JWT bearer grant support, and compatible access-token
  protection. If no supported profile satisfies the configured minimum,
  the client MUST NOT initiate that path.
* **Metadata consistency:** If the `actor_profile_token_exchange`
  parameter of {{ACTOR-PROFILE, Section 16.2}} is published, it MUST
  describe only the paths actually supported and agree with the
  ID-JAG advertisement.

# Self-Acting WAG Composition {#wag-flow}

Self-acting access uses the same Agent Principal model as delegated
access, with the agent as subject. This informative section describes
the identity and authorization composition. IdP issuance and other WAG
wire requirements remain pending {{wag-gaps}}; this revision defines no
WAG wire profile or implementation conformance target.

A WAG composition will need to preserve the identity invariants in
{{identity}}, particularly {{agent-correlation}}, at these stages:

| Stage | Intended identity relationship |
|---|---|
| Agent resolution at IdP | Validated dedicated-client or workload identity resolves through an approved Identity Binding to one active Agent Principal |
| Client authorization | A separate Client Association permits the authenticated client to use that binding for self-acting access |
| IdP-issued WAG | Issuer-qualified `sub` identifies that Agent Principal; no `act` is needed solely to identify its executing instance |
| WAG to local authorization | The RAS resolves the Agent Principal identity to one local agent principal in the authorized Target Tenant |
| Access token to API | The token identifies the same agent in the RAS's subject namespace; authorization uses that agent's authority |

The intended composition correlates the same Agent Principal to the same
local agent principal in both paths:

* In delegated access, the access token preserves the IdP-qualified
  agent as `act`.
* In self-acting access, the RAS represents the correlated agent as
  its local subject.

These representations do not make delegated and self-acting authority
interchangeable.

# Security Considerations {#security}

The security requirements of the selected credential and grant
specifications, {{RFC9700}}, and {{RFC8725}} apply.

## Adoption Tradeoffs {#baseline-costs}

The profile's security controls carry these deployment costs:

| Requirement | Benefit | Cost |
|---|---|---|
| Dedicated-client resolution as the common mode | Reuses deployed client authentication and registered keys | Each client identity resolves to one Agent Principal; proves registered-client identity, not independent runtime or workload provenance |
| Optional native JWT-SVID input | Reuses SPIFFE issuance, client authentication, and trust-domain validation | JWT-SVID is bearer evidence; deployments requiring issuer-bound presenter proof must select another supported input |
| Bound profile: DPoP at both token endpoints; grant bound to the grant proof key | A stolen ID-JAG cannot be redeemed without the key | Every client holds and proves a key. Grant binding does not make bearer evidence proof of an issuer-authorized presenter ({{credential-requirements}}) |
| Bound grants: same key for issuance and redemption | No key-transition protocol to secure | A broker that obtains bound grants must also redeem them ({{flow-configuration}}) |
| Access-token context as JWT claims or introspection | The API reads `act`, `scope`, and `cnf` from the token or from an authenticated introspection response ({{introspection}}) | Opaque-token deployments add an introspection round trip and a freshness policy |
| Actor-aware API processing | The actor gate is enforced where access happens | APIs parse `act` and consult the gate on delegated paths |
| Sender-constrained access tokens by default | Token theft is contained | Resources without DPoP or mutual TLS must be explicitly configured for bearer |

Governed agent access without grant binding adds agent authorization
to existing enterprise access but leaves stolen grants redeemable by
an attacker able to authenticate as their designated client. This is
particularly relevant to shared clients. Binding only the resulting
access token does not prevent that redemption.

Explicit acceptance
policy, short grant lifetimes, credential confidentiality, and the
no-fallback rules in {{discovery}} limit this exposure; they do not
provide proof of possession of an issuer-authorized grant key.

## Credential and Token Confusion

Credential classification and mutually exclusive validation follow
{{actor-inputs}} and {{RFC8725, Section 3.12}}. Signature validity alone
establishes neither a credential's intended use nor permission to
resolve or exercise an agent.

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

## Dedicated-Client Key Compromise

In dedicated-client resolution, compromise of the client's authentication
key permits an attacker to authenticate as the resolution source for its
bound Agent Principal. No independent workload credential is required.
A normalized Agent Principal identity does not imply uniform runtime
assurance; assurance depends on the resolution input, verified claims,
and the credential authority's issuance policy.

The attacker still needs an acceptable user subject credential and must
satisfy Client Association and delegation authorization, but existing
permissions may already authorize the compromised client.

Grant binding does not prevent this impersonation at issuance. Unless
policy independently constrains the grant proof key, the attacker can
obtain an ID-JAG bound to an attacker-controlled DPoP key. The proof
protects that grant against theft; it does not establish legitimate
runtime provenance.

Deployments requiring runtime or workload provenance MUST use an
agent-resolution input whose verified claims and trusted issuance policy
establish the required properties, rather than dedicated-client
resolution alone. Authentication-key revocation and binding disablement
affect subsequent issuance under {{status-changes}}.

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
limits.

Cross-system disablement and revocation need the mechanisms in
{{lifecycle-gap}}; without a signal or online check, issued tokens
remain usable until expiration.

For deployments applying {{AGENT-LIFECYCLE}}, that companion defines
ordered state propagation, reactivation cutoffs, and mode-specific
denial bounds. Its RAS enforcement stops issuance and refresh; cached
introspection results or offline JWTs may remain usable within the
configured mode's explicit bound.

Execution termination, Identity Binding disablement, Client Association
removal, delegation revocation, and Agent Principal disablement have
different effects. Deployments MUST NOT treat one as evidence that the
others have occurred. In particular, stopping an execution does not
revoke credentials or authority held elsewhere.

The following table summarizes the effect after a change is applied at
the enforcing server; it defines no new propagation mechanism:

| Administrative action | Effect on new authorization | Previously issued authority |
|---|---|---|
| Terminate an execution | Stops that execution; does not disable the agent or its approved relationships | Credentials and tokens remain subject to their validation and revocation rules |
| Disable one Identity Binding at the IdP | No new ID-JAG through that binding; other enabled bindings remain usable with their own Client Associations | Existing grants and RAS tokens need separate revocation or expiry |
| Remove a Client Association at the IdP | No new ID-JAG through that permission; the Identity Binding can remain valid | Existing grants and RAS tokens need separate revocation or expiry |
| Disable the Agent Principal at the IdP | No new ID-JAG for that agent, regardless of binding or client | RAS issuance and refresh stop when the change reaches and is applied by the RAS |
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
{{excluded-compositions}}.

# Privacy Considerations {#privacy}

A stable agent identifier can correlate activity across resources,
users, and instances. Preserving the same issuer-qualified actor across
delegated users enables a resource domain to correlate activity performed
by the same Agent Principal for different users, supporting audit while
linking those activities.

Issuers SHOULD disclose only the agent attributes needed for the
authorized purpose. User and agent context remain separate when the
agent acts for a user. The mapping in {{actor-construction}} keeps
external workload identifiers out of the ID-JAG; this profile does not
define pairwise actor translation.

Any future instance context needs purpose limits, retention guidance,
and clear rules about whose activity it describes.

# IANA Considerations {#iana}

## ID-JAG Grant Profile URIs

This document requests registration in the "OAuth URI" registry
established by {{RFC6755}}:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-agent-federation`
* Common Name: ID-JAG Bound Governed Agent Access grant profile
* Change Controller: IETF
* Specification Document: {{metadata}} of this document.

This document also requests:

* URN: `urn:ietf:params:oauth:grant-profile:id-jag-governed-agent`
* Common Name: ID-JAG Governed Agent Access grant profile
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

### WAG {#wag-gaps}

{{WAG, Section 5}} anticipates IdP issuance through Token Exchange
without specifying it. Coordination is needed on:

* **Issuance:** Dedicated-client or workload-identity resolution at
  the IdP; the Agent Principal in its namespace as the issued WAG's subject.
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

### Dedicated-Client Identity Mapping {#dedicated-client-coordination}

This document explicitly defines delegated issuance from authenticated
client context and an approved Identity Binding, without `actor_token`.
ID-JAG makes that parameter optional and leaves actor processing to
extensions ({{ID-JAG, Section 9.7}}); its omission alone does not establish
this composition.

{{RFC8693, Appendix A.1}} describes a subject-only request as
impersonation. Actor Profile Section 6.3.1 permits authentication-context
reuse only when the same client assertion is also present as
`actor_token`, and requires the client subject as `act.sub`.
Neither defines the dedicated-client mapping specified here.

Coordination with Actor Profile and ID-JAG is needed on this explicit
extension: trusted configuration selects authenticated-client resolution,
separate mapping and authorization checks establish the governed actor,
and the issued ID-JAG contains `act`. Generic Token Exchange or Actor
Profile support does not advertise support for this composition.

## Deferred Compositions

### Grant Key Transition {#key-transition-gap}

A control plane obtaining a bound grant for redemption by a different
worker needs an authorized proof-key transition. This revision defines
no such transition: the holder of the issuance key also redeems the
grant ({{flow-configuration}}). A future composition would need to bind
the new key without weakening the applicable grant protection.

### Portable Authorization Deadlines {#deadline-gap}

A portable IdP-imposed deadline on downstream access needs an
authenticated claim or reference, its association with the delegation,
and enforcement rules for access tokens and refresh authorization.
That composition is outside this revision. ID-JAG `exp` remains the
redemption limit; it cannot communicate when subsequent access must end
({{authorization-lifetime}}).

### User Access Tokens as Subjects {#access-token-subject-gap}

Deployed OBO flows, including {{AWS-AGENTCORE-OBO}}, use a user access
token as input. This revision accepts ID-JAG's ID Token, SAML, and
refresh-token subjects; it defines no access-token subject composition.
Such a composition needs rules for token eligibility and audience,
user/client/actor resolution, sender constraints, and the authority to
request downstream access. Coordinate those rules with ID-JAG;
changing only `subject_token_type` does not establish them.

### Excluded Compositions {#excluded-compositions}

The following compositions are not defined in this revision. Their
exclusion does not prevent the independently supported uses listed here.

| Composition | Boundary in this revision |
|---|---|
| Asynchronous approval with {{AROP}} | No approval transport or completion flow; external approval remains subject to {{external-approval}} and the lifetime limits in {{authorization-lifetime}} |
| Continuation with {{ICA}} | No ICA issuance or continuation chain; supported renewal follows {{continuing-access}} |
| X.509-SVID or WIT-SVID actor evidence | Client authentication is supported under {{spiffe-input}}, with a separate supported JWT as actor evidence |
| Instance-based resolution or propagated instance context under {{INSTANCE}} | Workload evidence resolves the agent; no per-instance enrollment or continuity protocol is required. Shared workload identity does not distinguish replicas {{SPIFFE-CONCEPTS}} |
| Client attester endorsement under {{ATTESTER-ENDORSEMENT}} | Attester trust is configured under {{agent-evidence}} |
| Mutual-TLS-bound ID-JAG | Bound grants use DPoP. Mutual TLS remains available for access-token protection under {{access-token-protection}} |
| RAR-only authority | This profile requires meaningful scope alongside any authorization details; it does not define the scope-free mode permitted by {{RFC9396}} |

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
missed-event recovery, and the effect on outstanding tokens. The companion
{{AGENT-LIFECYCLE}} defines a proposed SCIM and Shared Signals composition
for those requirements. It is not required for conformance to this
federation profile; {{agent-correlation}} and {{status-changes}} state
the guarantees of this document alone.

# Walkthrough: Dedicated Client {#walkthrough}

This non-normative walkthrough exercises the common dedicated-client
input, bound governed agent access, and DPoP-protected API access.
Key coordinates, thumbprints, token hashes, and compact JWTs are labeled
placeholders, not cryptographic test vectors. The optional shared-client
SPIFFE variant follows in {{shared-client-example}}.

The dedicated client is `analysis-client` at the IdP and `analysis-api`
at the RAS. In the IdP's client-registration context, an Identity
Binding maps (`analysis-client`, `analysis-client`) to `agent-42`.
A separate Client Association permits use of that binding, and
delegation authorization permits the agent to act for Alice.
Alice's ID Token has audience `analysis-client`; subject resolution
produces `alice-ras` for the RAS and `user-108` at the resource.

## Dedicated Client Authentication {#client-assertion-example}

The client signs this illustrative assertion payload with its
registered private key, using an `RS256` header and the registered
key identifier:

~~~ json
{
  "iss": "analysis-client",
  "sub": "analysis-client",
  "aud": "https://idp.example/token",
  "iat": 1789488000,
  "exp": 1789488060,
  "jti": "analysis-auth-1"
}
~~~

`CLIENT_ASSERTION` denotes the signed compact JWT presented only in
`client_assertion` under {{client-assertion-input}}. The configured
Identity Binding resolves the authenticated client to `agent-42`;
no actor-token parameters are sent. The assertion supplies no independent
workload identity. The client assertion expires after 60 seconds;
the resulting grant can remain valid for 300 seconds.

## Exchange Request and Response

The HTTP examples show application parameters and relevant headers;
framing headers are omitted. Bodies are line-wrapped for display;
concatenate their lines before sending.

`IDP_DPOP_PROOF` proves a separate grant key K, with `htm=POST`,
`htu=https://idp.example/token`, a current `iat`, and a unique `jti`.
A server nonce is included if challenged. The same key is proven at
redemption; `JKT_K` denotes its public key thumbprint.

After `use_dpop_nonce`, retry with a new `client_assertion` and a fresh
DPoP proof containing the nonce, still signed by K
({{client-assertion-input}}). For example, replace
assertion `jti=analysis-auth-1` with `analysis-auth-2`; resending
`analysis-auth-1` with only a new proof is a replay.

~~~ http-message
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: IDP_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&requested_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid-jag
&client_id=analysis-client
&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth
%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=CLIENT_ASSERTION
&subject_token=ALICE_ID_TOKEN_FOR_ANALYSIS_CLIENT
&subject_token_type=urn%3Aietf%3Aparams%3Aoauth
%3Atoken-type%3Aid_token
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
  "client_id": "analysis-api",
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

The 60-second client assertion authenticates issuance and does not cap
this grant's 300-second lifetime. Alice's ID Token remains valid for
at least that period. Adding another agent's identifier to the client
assertion cannot select that agent.

## Redemption Request and Response

`RAS_CLIENT_ASSERTION` authenticates the corresponding RAS client with
`iss=sub=analysis-api`, `aud=https://ras.example/token`, a short
expiration, and its own `jti`. It uses that registration's signing key.
`RAS_DPOP_PROOF` is a fresh proof using K, `htm=POST`, and
`htu=https://ras.example/token`.
The RAS validates the grant binding regardless of the API's token mode.
It also accepts `resource` encoded as the single-element array
`["https://api.example/tenants/acme-data/"]`, with the same authorization
result as the string shown above.

~~~ http-message
POST /token HTTP/1.1
Host: ras.example
Content-Type: application/x-www-form-urlencoded
DPoP: RAS_DPOP_PROOF

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&client_id=analysis-api
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
  "client_id": "analysis-api",
  "scope": "files.read",
  "act": {"iss":"https://idp.example/", "sub":"agent-42"},
  "cnf": {"jkt":"JKT_K"}
}
~~~

The RAS translates Alice's subject while preserving the Agent Principal
actor. The dedicated OAuth client identifier does not replace that
actor, and the access token is bound to the same key K used at both
token endpoints.

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
permissions there. The client caches this token for Alice and
`agent-42` in `acme-data`; matching client identity or scope alone does
not permit other uses.

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

The client assertion, Identity Binding, Client Association, user and actor
identities, scope, tenant checks, and actor gate are unchanged. An
unbound grant may instead obtain a DPoP-bound access token by presenting
a valid proof at redemption; this does not establish bound governed
agent access.
Refresh, if enabled, follows the applicable binding rules in {{ras-refresh}}.

## Renewal and Rejection Examples

The response contains no refresh token. After access-token expiration,
the client obtains a new ID-JAG using valid subject and agent-resolution
inputs.

If policy instead permits RAS refresh, the RAS sets an absolute refresh
authorization expiration at initial issuance. For example, with a
four-hour authorization and a thirty-minute inactivity limit:

* Renewal is permitted only while both limits hold.
* Rotation and refresh do not restart the four-hour period.
* Each access token expires no later than that period's end.
* Access beyond the period requires a new ID-JAG and new IdP and RAS
  authorization decisions. These establish a new period under
  {{ras-refresh}}; the previous expiration remains unchanged.

Each rejection below changes one condition in the walkthrough; all
other credentials, proofs, and policy checks succeed. Token endpoint
errors follow {{errors}}; API errors follow {{resource-errors}}.

| Changed condition | Rejecting party | Result |
|---|---|---|
| Dedicated-client exchange includes `actor_token` or `actor_token_type`, even a duplicate client assertion | IdP | HTTP 400, `invalid_request`; no switch to actor-evidence mode |
| Configured actor-evidence exchange omits `actor_token` or its type | IdP | HTTP 400, `invalid_request`; no fallback to dedicated-client resolution |
| Configured actor-evidence exchange uses an unsupported `actor_token_type` | IdP | HTTP 400, `invalid_request` |
| Bound-profile exchange omits its DPoP proof | IdP | HTTP 400, `invalid_request` |
| Exchange repeats `analysis-auth-1` | IdP | HTTP 400, `invalid_client`; the authentication assertion was already consumed |
| After a nonce challenge, retry uses a fresh proof but reuses the consumed `analysis-auth-1` assertion | IdP | HTTP 400, `invalid_client`; regenerate `client_assertion` |
| Exchange contains a second `resource` parameter | IdP | HTTP 400, `invalid_target`; obtain separate grants for the resources |
| Exchange requests authorization details that cannot be confined to its resource | IdP | HTTP 400, `invalid_authorization_details`; no ID-JAG |
| Redemption requests a resource different from the grant's resource | RAS | HTTP 400, `invalid_target`; no access token |
| ID-JAG `resource` is an empty or multi-element array | RAS | HTTP 400, `invalid_grant`; the grant must identify exactly one resource |
| Client assertion remains valid, but its Identity Binding is disabled | IdP | HTTP 400, `invalid_grant`; no actor can be resolved through this binding |
| Client assertion and Identity Binding remain valid, but the Client Association for `analysis-client` is disabled | IdP | HTTP 400, `actor_unauthorized`; no ID-JAG |
| Redemption carries a valid DPoP proof signed with another key, while the ID-JAG contains `cnf.jkt=JKT_K` | RAS | HTTP 400, `invalid_grant`; no access token |
| Bound governed agent access is required, but the grant has no `cnf` | RAS | HTTP 400, `invalid_grant`; no fallback to governed agent access |
| Governed agent access permits unbound grants, but this grant has `cnf.jkt` and redemption omits the proof | RAS | HTTP 400, `invalid_grant`; the existing binding is enforced |
| The client presents the access token for an operation in another tenant, with a fresh valid proof for that request URI | API | HTTP 401, `invalid_token`; no operation performed |

# Variant: Shared Platform Client with SPIFFE {#shared-client-example}

This non-normative variant completes {{identity-example}} with the
OPTIONAL JWT-SVID input. It substitutes a shared `platform-sso` client
at the IdP and `platform-api` at the RAS for the dedicated registrations
in {{walkthrough}}. The independent workload identity selects `agent-42`;
client authentication alone cannot distinguish agents behind this client.

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

Relative to the dedicated-client exchange, change only these inputs:

| Item | Shared-client value |
|---|---|
| IdP `client_id` | `platform-sso` |
| `client_assertion_type` | `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` |
| Resolution mode | Trusted configuration selects the JWT-SVID actor-evidence input |
| `client_assertion` and `actor_token` | The identical compact `JWT_SVID` |
| `actor_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `subject_token` | Alice's ID Token with audience `platform-sso` |
| Identity Binding | Approved trust domain and exact SPIFFE ID resolve to `agent-42` |
| Client Association | `platform-sso` may use that binding for delegated ID-JAG |

The JWT-SVID authenticates the client through the configured SPIFFE
association and resolves the agent separately. It is bearer evidence;
it does not attest that grant proof key K belongs to the workload.

The response, redemption, and API sequence are those in {{walkthrough}},
with `platform-api` replacing `analysis-api` in grants, access tokens,
and RAS client authentication. User and governed actor identities,
resource, scope, tenant, and proof key K are unchanged. The grant also
expires no later than the JWT-SVID. The same rejection cases apply to
this binding and Client Association; client-assertion-specific replay
and equality rules instead follow the JWT-SVID input specification.

# Example: AWS Workload Identity Binding {#aws-example}

This non-normative example uses the AWS STS `GetWebIdentityToken`
credential documented in {{AWS-TOKEN-CLAIMS}}. It fits the existing
platform-JWT input ({{imported-jwt-input}}) without a new credential format:

| Item | Example configuration |
|---|---|
| Credential authority | The AWS account's configured STS issuer and approved verification keys |
| Exact `sub` | `arn:aws:iam::123456789012:role/AgentRuntime` |
| Accepted audience | `https://idp.example/token` |
| Additional selector | `/https:~1~1sts.amazonaws.com~1/aws_account` equals `123456789012` |
| Identity Binding result | Agent Principal `agent-42` in Governance Tenant `acme` |
| Client Association | `platform-sso` may use this binding for delegated ID-JAG with the platform-JWT agent-resolution input |

The selector addresses the string `aws_account` within the
`https://sts.amazonaws.com/` object; `~1` escapes each slash in that
member name. The client presents the STS JWT as `actor_token`,
authenticates separately, and supplies a supported user credential and
any proof required by the applicable profile under {{root-request}}.
The resulting actor is
`{"iss":"https://idp.example/","sub":"agent-42"}`.

If several agents share this role, issuer and `sub` identify the
shared IAM principal, not an individual agent. Mapping those agents to
distinct Agent Principals requires distinct credential identities or
additional trusted selectors. A caller-supplied agent name does not
provide that distinction.

This example covers evidence resolution, not a product's end-to-end
conformance. An integration also needs the client, subject, grant, and
resource processing defined by this profile. User-access-token OBO
composition remains outside this revision ({{access-token-subject-gap}}).

# Document History

RFC Editor: Remove this section before publication.

* Initial version.
