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
  IDENTITY-CHAINING: I-D.ietf-oauth-identity-chaining
  OIDC:
    title: "OpenID Connect Core 1.0 incorporating errata set 2"
    target: https://openid.net/specs/openid-connect-core-1_0.html
    date: 2023-12
    author:
      - ins: N. Sakimura
      - ins: J. Bradley
      - ins: M. Jones
      - ins: B. de Medeiros
      - ins: C. Mortimore
  RFC6749:
  RFC7515:
  RFC7518:
  RFC7519:
  RFC7523:
  RFC7638:
  RFC7800:
  RFC8414:
  RFC8693:
  RFC8707:
  RFC8725:
  RFC9068:
  RFC9449:
  RFC9700:
informative:
  WAG: I-D.carleton-workload-authz-grant
  RFC6755:
  RFC6838:
  ENTITY-PROFILES: I-D.mora-oauth-entity-profiles
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  RFC7662:
  RFC9396:
  EMA:
    title: "MCP Enterprise-Managed Authorization"
    target: https://github.com/modelcontextprotocol/ext-auth/blob/main/specification/stable/enterprise-managed-authorization.mdx
    author:
      - org: Model Context Protocol
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
--- abstract

This specification profiles OAuth 2.0 Token Exchange to bind
platform-authenticated agents to registered principals at an identity
provider. It supports platform-issued JWTs, Attestation-Based Client
Authentication, and SPIFFE client authentication. An agent acting for
itself receives a Agent Federation Grant; an agent acting for a
user receives an Identity Assertion JWT Authorization Grant with an
explicit actor. Both grants are key-bound and redeemed at a resource
authorization server for sender-constrained access tokens.

--- middle

# Introduction

This document defines how an identity provider (IdP) resolves an
agent's platform identity to a governed principal and issues an
authorization grant for access to another service. It distinguishes:

* **Agent principal:** the non-human identity governed by the IdP,
  including its status, owner, and assignments.
* **Acting relationship:** whether the agent acts for itself or for
  a user.
* **Instance:** the installation or execution presenting the request.

An OAuth client identifier can identify the agent's client without
identifying the agent principal. Likewise, an instance identifier
provides execution context without establishing authority.

The IdP issues one of two grants:

* **Self-acting access:** a Agent Federation Grant (AFG)
  defined here, with the Registered Agent (the principal governed by
  the IdP) as subject.
* **User-delegated access:** an Identity Assertion JWT Authorization
  Grant (ID-JAG) {{ID-JAG}}, with the user as subject and the
  Registered Agent as actor under {{ACTOR-PROFILE}}.

Both grants bind to a key proved by the agent. The agent redeems the
grant at a Resource Authorization Server (RAS) for a sender-constrained
access token. The RAS trusts the IdP's grant; it need not validate the
platform's original evidence.

## Protocol Overview

~~~
 Platform       Agent             IdP             RAS        API
    |-- evidence ->|               |               |          |
    |              |-- evidence -->|               |          |
    |              |<-- grant -----|               |          |
    |              |-------- grant + proof ------->|          |
    |              |<------- access token ---------|          |
    |              |------------- token + proof ------------>|
~~~

The IdP resolves platform-issued JWTs, Client Attestations {{ATTEST}},
and SPIFFE SVIDs {{SPIFFE-OAUTH}} through trusted Federation Bindings.
{{paths}} selects direct exchange or intermediate-token acquisition.
Delegated requests also carry a user credential and require approval
for the Registered Agent to act for that user.

## Relationship to Other Specifications

This profile defines agent evidence, identity resolution, IdP access
token acquisition, grant issuance, and shared redemption requirements.
ID-JAG's format and downstream processing follow {{ID-JAG}} and
{{ACTOR-PROFILE}}. This document defines AFG in {{afg-profile}},
including its identifiers, sender constraint, and redemption rules.
AFG is distinct from the platform-issued Workload Authorization Grant
{{WAG}}; implementing either grant does not imply support for the other.

RFC Editor: Before publication as an RFC, remove repository links and
the Supporting Material appendix, or replace them with stable informative
references. All conformance requirements are contained in this document
and its normative references.

Actor Profile applies to user delegation. The Registered Agent is the
actor. Actor representation and chain processing belong to Actor
Profile and its consuming authorization profiles; this version does
not support delegation chains. Self-acting access does not require
Actor Profile.

Instance identification is separate from authorization identity
({{instance-identification}}). Provisioning and lifecycle mechanisms
supply governance inputs; this profile defines their use in federation,
not their transport. Enrollment, clone detection, and verified key
replacement depend on platform evidence mechanisms. Model and runtime
assurance semantics are outside this profile.

Existing client-based delegation, including MCP Enterprise-Managed
Authorization, can be used when a separately governed agent principal
is unnecessary. {{models}} covers model selection, {{deployment}}
covers compatibility, and [End-to-End Deployment Examples](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md#flows) provides end-to-end examples.

## Choosing an Identity Model {#models}

This section is informative. Choose the model according to the
principal the IdP governs and the identity the platform authenticates.

| Model | Use when | Binding |
|---|---|---|
| Existing client-based delegation | The OAuth client is sufficient for policy | Existing ID-JAG/EMA flow; Actor Profile can represent the client explicitly |
| Imported workload principal | The IdP governs a platform agent independently of an OAuth client | Platform JWT issuer and exact identity claims |
| Agent with its own client identity | ATTEST or SPIFFE authenticates each agent as its own client | Client identity maps to the Registered Agent |
| Agents behind a shared client | A platform hosts individually governed agents through one OAuth client | ATTEST `(iss, sub, agent_id)` maps to the Registered Agent |

Use a separate agent principal when client identity alone cannot
express the required policy. For a shared client, the attester is
trusted to distinguish agents and verify their authorized execution.
Its authority therefore spans the agents behind that client
({{security}}).

A client identifier metadata document {{CIMD}} can give each hosted
agent its own `client_id`. Control of a metadata URL does not establish
which agent is running; an approved platform authority still supplies
that binding. These choices also apply to MCP clients.

The other identity dimensions remain independent:

* **Acting relationship:** each federation model can produce AFG with
  the agent as `sub`, or ID-JAG with the user as `sub` and agent as
  `act`. An agent can be both an OAuth client and a delegated actor.
* **Instance:** one agent can run in several installations or
  executions. This profile does not define a stable instance identifier
  or transmit instance context. Key possession remains required.

# Conventions and Scope

{::boilerplate bcp14-tagged-bcp14}

OAuth terms follow {{RFC6749}} and {{RFC8693}}. Client Attestation,
Client Attester, and Client Instance follow {{ATTEST}}. A harness is
the software executing an agent and making OAuth requests. The IdP acts as
an OAuth authorization server; the RAS issues access tokens for the
target resource. Both roles can be implemented by the same service.

Token endpoint requests use HTTP POST and UTF-8
`application/x-www-form-urlencoded` bodies under {{RFC6749}}.
Response encoding, HTTP status codes, and cache controls follow
Sections 5.1 and 5.2 of that RFC and the applicable grant specification.
Examples abbreviate cryptographic values and omit HTTP framing
headers; line breaks in form bodies are for display only. Platform
JWT examples assume the client has obtained the required IdP nonce.

Registered Agent:
: A non-human principal represented at the IdP with a stable,
  non-reassignable identifier, status, and authorized platform bindings.

Federation Binding:
: An approved association between a credential authority, external
  identity, tenant, and Registered Agent, plus OAuth client context
  where required. A platform JWT binding records exact claim selectors
  and permitted clients when client authentication is used. An ATTEST
  binding includes the platform agent identifier for a shared client.

Source Tenant:
: The IdP tenant that governs the Registered Agent and issues the
  access token and grant.

Target Tenant:
: The tenant at the RAS in which the agent or user is authorized,
  identified by the IdP's configuration for the approved RAS and
  resource.

Agent Status:
: The IdP's current lifecycle state for a Registered Agent, at
  minimum active or disabled. Only an active agent is eligible for
  issuance.

## Conformance

A client or IdP claiming this profile MUST implement at least one
input in {{inputs}} and the exchange requirements for its supported
outputs. Each implementation MUST meet the applicable requirements below:

* AFG with a JWT input requires direct exchange under {{direct-afg}}.
* X.509-SVID and delegated ID-JAG require IdP access-token acquisition
  under {{bootstrap}}. Acquisition is optional for direct-AFG-only
  implementations.
* When acquisition is supported, the corresponding IdP access-token
  input MUST be supported for each implemented output.
* Delegated ID-JAG requires {{ACTOR-PROFILE}}.

A RAS claiming this profile MUST implement {{consumption}} and the
validation rules for each output it accepts. The parties MUST
establish common inputs and outputs through trusted configuration
and the metadata in {{metadata}}.

The requirements of the referenced protocols apply unless this
profile explicitly narrows an option. An implementation supporting
self-acting access MUST implement AFG issuance or redemption, as
applicable, under {{afg-profile}} and {{consumption}}. Task authority,
delegation chains, and unlisted inputs are outside this profile.

## Additional Requirements of This Profile {#profile-requirements}

Implementing ID-JAG, ATTEST, or SPIFFE OAuth alone does not imply
conformance here. This profile adds the following requirements:

| Area | Additional requirement | Defined in |
|---|---|---|
| ATTEST | `iat` required for configured age/lifetime checks; shared-agent binding | {{agent-evidence}} |
| JWT-SVID and WIT-SVID | `client_id` equals the authenticated SPIFFE ID; trust anchors come from the configured trust domain | {{jwt-svid-input}}, {{wit-input}} |
| Bearer JWT inputs | DPoP association enforced across acquisition and exchange, including credential reuse | {{bearer-reuse}} |
| Exchange request | Explicit nonempty `scope`, one `resource`, and one RAS `audience` | {{exchange}} |
| Grant | Required `scope`, `resource`, and `cnf.jkt`; bounded lifetime | {{grant}} |
| Exchange response | Required `expires_in` and response `scope` even when unchanged | {{exchange-response}} |
| Exchange errors | `invalid_grant` for credential and binding failures instead of RFC 8693's default `invalid_request` | {{exchange-errors}} |
| Authorization details | Reject `authorization_details` with `invalid_request` | {{exchange}} |
| Redemption | Explicit matching `resource`, DPoP binding, single use, and sender-constrained output | {{consumption}} |

AFG is defined in {{afg-profile}}, with registrations in {{iana}}.
The IdP and RAS agree support through trusted configuration;
base-protocol metadata alone does not signal acceptance of every
additional check.

# Profile Selection and Identity Binding {#identity}

The IdP MUST configure:

* The input, identity model, Source Tenant, and permitted outputs.
* Credential verification authorities, keys, and validation policy.
* Approved RAS issuers, resources, Target Tenants, and subject and
  client mappings.

Unsigned request hints and discovered client metadata MUST NOT
establish this authority or change the configured binding. Bindings
can be imported from a platform registry. The IdP MUST authorize
binding changes, including imports. Operators SHOULD authenticate and
audit the administrative source of each change. Binding configuration
identifies the credential authority and exact identity selectors.

| Input and identity model | Federation Binding lookup |
|---|---|
| Platform-issued JWT, imported workload | Approved issuer and configured exact identity claims under {{platform-jwt-input}}; OAuth client identity is separate |
| ATTEST, agent is the client | Exact attestation `(iss, sub)`; `agent_id` is not used |
| ATTEST, shared client | Exact attestation `(iss, sub, agent_id)` |
| SPIFFE JWT-SVID, agent is the client | Approved trust domain and exact JWT `sub`; `client_id` equals that SPIFFE ID |
| SPIFFE X.509-SVID, agent is the client | Approved trust domain and exact SPIFFE ID; `client_id` equals that ID |
| SPIFFE WIT-SVID, agent is the client | Approved trust domain and exact WIT `sub`; `client_id` equals that SPIFFE ID |

The IdP MUST resolve the lookup to exactly one active Registered Agent
through an enabled binding. Missing or ambiguous matches cause
rejection. ATTEST's `agent_id` rules follow {{agent-evidence}}; claim
presence MUST NOT select the identity model.

The Registered Agent identifier MUST be unique and non-reassignable
within the IdP issuer's namespace. It need not equal the external
identifier. Multiple approved bindings can identify the same agent;
display names or unqualified strings MUST NOT establish equivalence.
A new installation, execution, or key does not by itself create a new
authorization principal.

The IdP MUST verify all configured evidence and an unambiguous Source
Tenant; grant issuance also requires an unambiguous Target Tenant. Evidence has distinct roles:

* Client authentication establishes the OAuth client.
* The Federation Binding establishes the Registered Agent.
* The DPoP proof establishes possession of the binding key.

The IdP MUST NOT substitute one role for another or bypass a required
binding when evidence is omitted. Other client flows retain their own
requirements.

## Evidence and Client Authentication {#inputs}

Every acquisition and exchange request MUST include a fresh DPoP
proof under {{RFC9449}}. Implementations MUST support `ES256` for
DPoP. The IdP MUST bind the resolved agent, source tenant, and proven
key, plus the authenticated OAuth client when required, to the same
request. Platform JWTs supply subject evidence; the other inputs also
authenticate the client. Subsequent use of an IdP access token follows
{{idp-processing}}.

* When an intermediate access token is exchanged, the IdP MUST verify
  its eligibility and the current validity of its Federation Binding.
  Token claims or server-side state can establish that association.
* This profile defines no `agent_id` request parameter. Unrecognized
  request parameters are ignored under {{RFC6749, Section 3.2}};
  unrecognized JWT claims are ignored under {{RFC7519, Section 4}}.
  An extra claim does not select an identity model or establish a
  binding unless that model uses it.
* A JWT input credential MAY be the `subject_token` for direct AFG
  exchange under {{direct-afg}}. Input credentials MUST NOT be used
  as `actor_token`; delegated exchange uses an IdP-issued access token.
* Renewal or reissuance of an input credential does not rebind an
  existing access token to a different DPoP key. A changed key
  requires new issuance.

### Bearer JWT Credential Reuse {#bearer-reuse}

This section applies to platform JWT evidence and JWT-SVID client
authentication. The same credential MAY be reused with fresh DPoP
proofs. After validating the request and before issuance, the IdP
MUST atomically establish or enforce the following association:

1. Compute the SHA-256 digest of the JWS Signing Input {{RFC7515}}.
2. On first use, associate that digest with the Federation Binding
   and proven DPoP key.
3. Retain the association until `exp` plus allowable clock skew, even
   if a configured maximum age makes the JWT unusable sooner.
4. Reject reuse with another binding or key. Reuse with the same
   association remains subject to current validation and
   status checks, but MUST NOT be rejected solely because the JWT or
   its `jti` was previously seen.

The IdP MUST enforce one association across acquisition and exchange,
including direct AFG and delegated ID-JAG requests and all endpoint
replicas. Excluding the signature from the digest prevents another
valid signature over the same signing input from bypassing this check.
Failures use the error defined for the input in {{inputs}}.

Clients using cached JWTs MUST retain the associated DPoP key. A key
change requires a newly issued JWT with a different signing input,
such as a new `iat` or `jti`, or another independently authenticated,
approved binding. The IdP MUST NOT reset the association merely
because the caller supplies a new key. A renewed credential does not
change the key binding of an existing grant or access token.

### Platform-Issued JWT {#platform-jwt-input}

The client MUST present a JWT issued by an approved platform as
`subject_token`, with
`subject_token_type=urn:ietf:params:oauth:token-type:jwt`, in a token
exchange request. This input is workload evidence, not client
authentication under {{RFC7523}}. It MUST NOT be presented as
`client_assertion`. The requested output is AFG under {{direct-afg}}
or an IdP access token under {{platform-acquisition}}.

The Federation Binding MUST specify an exact `sub` value. It MAY also
specify top-level string claims identifying the agent or restricting
its identity context. The IdP MUST require every configured selector to:

* Be present as a nonempty string.
* Match the configured value exactly, without patterns or prefixes.
* Together with the issuer, resolve to one Registered Agent.

For example, an agent identifier and tenant claim can qualify a
shared platform `sub`. Selectors come from trusted configuration;
no external claim need equal an OAuth `client_id`.

Client authentication, when required, follows {{platform-client}}.
A Federation Binding MAY designate an IdP-assigned OAuth client or an
explicit set of permitted clients, independently of the platform's
identity namespace. That association authorizes use of the binding
by those clients; it MUST NOT substitute for client authentication.

#### Issuer Configuration and Validation

For each approved platform issuer, the IdP MUST configure:

* The exact issuer identifier and a trusted key source: issuer
  metadata under {{OIDC}} or {{RFC8414}}, or a configured key set.
  A URL or key supplied in the JWT MUST NOT establish that trust.
* Accepted audiences identifying the IdP and permitted asymmetric
  signature algorithms.
* Maximum credential age and lifetime, accounting for the platform's
  issuance and caching behavior. The maximum age SHOULD be no more
  than 300 seconds where the platform can refresh credentials that
  frequently; a longer age requires an explicit deployment policy.
* Validation rules distinguishing workload credentials from other
  tokens issued by the platform. These can use an explicit `typ`, a
  dedicated issuer or audience, or an audience combined with exact
  workload identity claims. Generic `typ=JWT` alone is insufficient.

The IdP MUST validate the JWT under {{RFC7519}} and {{RFC8725}},
including its signature, issuer, audience, and credential class, and
reject it if any of the following applies:

* `iss` or `sub` is missing or is not a nonempty string.
* `iat` or `exp` is missing or is not a NumericDate, `iat` does not
  precede `exp`, or a time check in {{time-validation}} fails.
* Its age or lifetime exceeds the configured limit.
* It identifies a user rather than an approved workload, or its
  audience and credential class do not authorize use as workload
  evidence at this IdP.
* It contains `act` or fails a configured identity selector.

#### DPoP Binding and Credential Reuse

A platform-issued JWT is a bearer credential with no key of its
own. A separate DPoP proof establishes the token-binding key, which
the platform need not know. Both MUST be validated in the same request.

Nonce policy follows the common rule in {{exchange}}. A nonce
prevents proof pre-generation; it does not prevent theft of the bearer
JWT before its first use or bind that JWT to a platform-proven key.

Platform JWTs MUST follow the association and key-change rules in
{{bearer-reuse}}. Validation failures use `invalid_grant`; separate
client authentication errors retain their base processing.

Platforms unable to issue a fresh credential or target the IdP
audience can provide a token-exchange service or act as an ATTEST
attester instead.

### Client Authentication for Platform Evidence {#platform-client}

For direct platform-JWT-to-AFG exchange, the IdP MAY permit requests
without OAuth client authentication or identification, as allowed by
{{RFC8693, Section 2.1}}. This does not waive validation of the platform
JWT, DPoP nonce and key association, or agent authorization. A binding
configured to require client authentication MUST NOT permit its omission.

Acquisition from platform evidence and subsequent use of the IdP
access token MUST authenticate the OAuth client independently:

* The client uses a separately configured OAuth authentication method,
  such as `private_key_jwt` under {{OIDC}} and {{RFC7523}}, or ATTEST.
* The request includes `client_id`, and the IdP verifies that it
  identifies the authenticated client permitted by the binding.
* Neither DPoP possession nor the mapped platform identity substitutes
  for client authentication.

Requests using a platform-origin IdP access token follow the same
nonce policy as other inputs under {{exchange}}.

A JWT used for client authentication MUST satisfy that method's client
identity and key requirements independently of the platform JWT. For
RFC 7523 client authentication, `sub` MUST be the OAuth `client_id`.
For ATTEST used solely in this role, its client authentication rules
apply; it does not independently select the Registered Agent for the
platform evidence path. No new client
authentication method or assertion type is defined here.

### Client Attestation and Shared-Agent Binding {#agent-evidence}

The client MUST use `attest_jwt_client_auth_dpop` under {{ATTEST}}.
This section defines an ATTEST extension for agent identity binding;
base ATTEST validation alone does not establish an agent identity.
An IdP enables the extension only for an approved Federation Binding.
The Client Attestation MUST satisfy ATTEST and these additional rules:

* `iss` and `sub` are nonempty strings; `sub` equals `client_id`.
* `iat` and `exp` are NumericDates, with `iat` preceding `exp`.
* The signature uses an approved asymmetric algorithm and a `kid`
  resolved through trusted attester configuration. Implementations
  MUST support `ES256`.
* For a shared client, `agent_id` is a nonempty StringOrURI
  {{RFC7519}} naming the agent in the attester's namespace. When the
  agent is the client, the binding uses `(iss, sub)`; an additional
  `agent_id` claim does not change that binding.

The shared-client binding assumes that the attester verifies the
named agent's authorized execution and possession of the `cnf.jwk`
key. The IdP SHOULD approve an attester for this binding only when
its issuance policy provides that assurance.

The IdP MUST validate the attestation and combined-mode proof under
ATTEST, including the match between the DPoP key and `cnf.jwk`, and
apply a configured maximum age and lifetime for each attester:

* Missing or incorrectly typed required claims, invalid time ordering,
  or an invalid shared-client `agent_id` produce
  `invalid_client_attestation`.
* An attestation outside configured age or lifetime limits produces
  `use_fresh_attestation` under ATTEST.

Request freshness comes from the proof and current status checks;
this profile does not impose a fixed attestation lifetime.

### SPIFFE JWT-SVID {#jwt-svid-input}

The client MUST authenticate under {{SPIFFE-OAUTH, Section 3.1}} with:

* `client_assertion_type` set to
  `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe`.
* `client_assertion` containing a single JWT-SVID.
* `client_id` equal to the exact SPIFFE ID in the JWT-SVID's `sub`.
  This is a narrowing of SPIFFE OAuth's client-identifier association
  options; this input represents the agent as its own client.

The IdP MUST validate the JWT-SVID under that specification, including
its required `sub`, `aud`, and `exp`, signature, and time checks under
{{time-validation}}. In particular:

* The sole audience MUST be the IdP issuer identifier, not the RAS
  issuer, token endpoint URL, or selected exchange audience of the
  IdP access token.
* Verification keys MUST come from the configured trust domain in
  the SPIFFE ID, using {{SPIFFE-OAUTH, Section 6}}. The IdP MUST resolve
  the exact Federation Binding under {{identity}}.
* An optional `iss` MUST NOT select trust anchors or replace that
  lookup. Absence of `iss` or `iat` alone MUST NOT cause rejection;
  SPIFFE OAuth defines this adaptation of {{RFC7523}}.

JWT-SVID authenticates the client as a bearer credential. The IdP MUST
also validate the separate DPoP proof under {{inputs}} and enforce
{{bearer-reuse}}. DPoP does not prove possession of a key certified by
that JWT-SVID. Nonce policy follows {{exchange}}.

For self-acting access, the client uses {{direct-afg}}. For acquisition,
it uses the client credentials grant under {{bootstrap}}. At exchange
of an IdP access token, a renewed JWT-SVID MAY authenticate the same
client and Federation Binding; DPoP MUST still prove the token's key.
Delegated exchange retains the IdP access token as `actor_token`.

JWT-SVID authentication and credential-reuse failures produce
`invalid_client` under {{RFC7523, Section 3.2}}. DPoP failures use the
errors in {{exchange-errors}}. A valid authentication assertion that
differs from the direct AFG `subject_token` produces `invalid_grant`.

### SPIFFE X.509-SVID {#spiffe-input}

The client MUST authenticate using `spiffe_x509` under
{{SPIFFE-OAUTH, Section 3.2}}, with `client_id` equal to the exact
SPIFFE ID in the certificate's URI SAN. The IdP MUST validate the
SVID and trust bundle under that specification and resolve the
approved trust-domain and identity binding in {{identity}}. This
input represents the agent as client.

A separate DPoP proof establishes the token-binding key. This key
MAY differ from the SVID's TLS key. Both proofs MUST be validated
in the same authenticated token request. At exchange, a renewed SVID
MAY authenticate the same SPIFFE ID under the same approved binding;
the DPoP key MUST still match the access token.

### SPIFFE WIT-SVID {#wit-input}

The client MUST authenticate using `spiffe_wit` under
{{SPIFFE-OAUTH, Section 3.3}}. It MUST send the WIT-SVID directly in
`OAuth-Client-Attestation` and a fresh Client Attestation PoP JWT in
`OAuth-Client-Attestation-PoP`, with `client_id` equal to the exact
SPIFFE ID in the WIT's `sub`. This input represents the agent as
client. The requirements specific to {{agent-evidence}} do not apply
to this input.

The IdP MUST validate the WIT under {{WIT}}, including `typ=wit+jwt`,
expiration, signature, and the public key and proof algorithm in
`cnf.jwk`. It MUST use trust anchors configured for the trust domain
in `sub` and resolve the exact binding in {{identity}}. The optional
`iss` claim MUST NOT select trust anchors or replace that lookup;
its absence alone MUST NOT cause rejection.

The IdP MUST validate the Client Attestation PoP JWT under {{ATTEST}},
including the IdP issuer audience, freshness, and required challenge.
The request also includes the DPoP proof required by {{inputs}}.
For those proofs:

* Both MUST use the WIT's `cnf.jwk` key and its `alg` value.
* The IdP MUST compare keys using {{RFC7638}} thumbprints and reject
  a mismatch.
* Implementations MUST support `ES256`.

The attestation proof authenticates the client; DPoP establishes the
token binding. DPoP alone MUST NOT replace the attestation proof.
Validation errors follow ATTEST or DPoP, as applicable.

A renewed WIT-SVID MAY authenticate an exchange using an existing
eligible IdP access token only if its identity binding and proof key
remain the same. If the WIT key changes:

* The IdP access-token path requires new acquisition.
* A direct AFG request proves the new key under {{direct-afg}}.

{{WIT}} recommends a fresh key for each WIT, so reuse across renewal
is expected only where the deployment retains the key. The lifetime
limit in {{idp-access-token}} applies to the access token, not the WIT.

## Instance Identification {#instance-identification}

Stable instance identifiers, instance claims, and their lifecycle
semantics are outside this profile. It does not interpret
`client_instance_id` or `client_instance`, define enrollment or
key replacement, or infer installation or execution continuity from
key possession. Unrecognized instance claims do not establish identity
or authorization. The repository coordination notes record design
boundaries for future consuming profiles.

## IdP Access Token {#idp-access-token}

This DPoP-bound token carries the IdP's canonical
Registered Agent identity. It is an exchange adapter or actor
credential, not the access token used at a downstream API. Acquisition
is specified in {{bootstrap}}.

This revision selects a canonical IdP-issued actor token for delegation.
Actor Profile also defines direct credential inputs; the adapter is
this profile's choice to normalize agent identity before actor
construction, not a universal Actor Profile requirement. Actor Profile's
direct credential processing uses the credential's `sub` as `act.sub`;
this profile instead exposes the governed Registered Agent identifier.
A direct mapped-actor input requires a companion rule for that mapping,
including shared-client attestations, before it can replace the adapter.

An unexpired access token that this IdP issued under {{bootstrap}} to
the same client, Registered Agent, input method, and DPoP key MAY be
reused for exchange. No other access token is eligible; a matching
audience or a caller-supplied claim does not make one eligible. The
IdP MAY require new acquisition when current policy requires fresh
authentication, even if the token has not expired.

The issued access token MUST conform to {{RFC9068}}, including its
JWT typing and required claims, with these profile-specific values:

| Claim | Required value |
|---|---|
| `iss` | IdP issuer identifier |
| `sub` | Resolved Registered Agent identifier |
| `client_id` | Authenticated OAuth client identifier |
| `aud` | Federation exchange audience; defaults to the IdP token endpoint URL |
| `cnf.jkt` | SHA-256 JWK thumbprint of the proven DPoP key under {{RFC7638}} |
| `iat`, `exp` | Issuance and expiration times within the configured token lifetime |
| `jti` | Token identifier under {{RFC9068}} |

The federation exchange audience MUST default to the IdP's
`token_endpoint` URL obtained from trusted {{RFC8414}} metadata.
A deployment MAY configure an alternative absolute URI, communicated
to the client through trusted configuration. In either case:

* The acquisition request's `resource` and the token's `aud` MUST
  equal the selected URI exactly.
* That URI MUST be distinct from the IdP issuer identifier and all
  API audiences. If the token endpoint URL cannot meet this condition,
  the deployment MUST configure an override.
* The IdP MUST accept this token only as `subject_token` or
  `actor_token` at its federation token endpoint. Other endpoints
  and resource servers MUST NOT accept it as API authorization.

The default needs no new metadata field. An override need not resolve
to an HTTP endpoint; for example,
`https://idp.example/tenant/acme/agent-federation`. The `at+jwt` type,
issuance eligibility, and input-specific validation prevent a matching
audience from making this token a client assertion or an API token.

The token MUST NOT contain `act`; it supplies the agent subject from
which exchange constructs an actor when needed. The IdP MUST associate
the token with its Federation Binding, input method, Source Tenant,
and exchange authorization through trusted issuance policy or token
state.

The IdP MUST configure a finite access-token lifetime. A lifetime of
at most 300 seconds is RECOMMENDED; deployments MAY use a longer
lifetime when current binding and authorization checks remain enforced
on every exchange. Revocation or a policy change can make an unexpired
token ineligible or require new acquisition.

The input credential is valid at issuance; its remaining validity
does not bound the access token. Binding revocation takes effect at
the next acquisition or exchange once applied at the IdP.

# Requesting an Authorization Grant {#exchange}

The client MUST use {{RFC8693}} at the IdP token endpoint with its
evidence and client authentication under {{inputs}}. When an IdP access token
is presented, the OAuth client MUST match the one that obtained it.

The DPoP proof establishes the issued grant's binding key:

* Direct JWT input uses the credential and proof checks in {{inputs}}
  and {{direct-afg}}.
* For an IdP access token presented as `subject_token` or `actor_token`,
  the proof key MUST match its `cnf.jkt`.

These token-endpoint exchanges do not require `ath`; input-key checks
are defined here in addition to {{RFC9449}}.

The IdP SHOULD issue server-provided nonces under
{{RFC9449, Section 8}} for acquisition and exchange requests so that
proofs cannot be generated in advance. This recommendation applies
to every input. When a nonce is required, a missing or invalid nonce
produces `use_dpop_nonce` with a fresh `DPoP-Nonce` value under RFC 9449.

The client MUST include each of the following parameters exactly once:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `requested_token_type` | AFG under {{self-exchange}} or ID-JAG under {{delegated-exchange}} |
| `subject_token` | Credential selected under {{paths}} |
| `subject_token_type` | Token type corresponding to that credential |
| `audience` | One target RAS issuer identifier |
| `resource` | One absolute resource URI without a fragment, under {{RFC8707}} |
| `scope` | Nonempty, space-delimited scope tokens under {{RFC6749, Section 3.3}} |

The IdP MUST reject `authorization_details` {{RFC9396}} with
`invalid_request`. This version carries authorization through
`scope`; richer authorization requires a separate profile.

## Selecting an Exchange Input {#paths}

| Output and evidence input | Exchange input | Acquisition |
|---|---|---|
| AFG; platform JWT, ATTEST, JWT-SVID, or WIT-SVID | The JWT credential as `subject_token`, type `jwt` | Not required; preferred path |
| AFG; X.509-SVID | IdP access token as `subject_token`, type `access_token` | Required unless an eligible token is held |
| AFG; another supported input with an eligible IdP access token | IdP access token as `subject_token`, type `access_token` | Reuse the existing token |
| ID-JAG; any supported input | User credential as `subject_token`; IdP access token as `actor_token` | Required unless an eligible actor token is held; platform evidence requires separate client authentication |

The abbreviated token types in this table use the
`urn:ietf:params:oauth:token-type:` prefix.

## Self-Acting Agent {#self-exchange}

`requested_token_type` MUST be `urn:ietf:params:oauth:token-type:afg`.
The client MUST omit `actor_token` and `actor_token_type` and use one of the
subject inputs below. The issued AFG is specified in {{afg-profile}}
and its identifier registrations are specified in {{iana}}.

### Direct JWT Credential {#direct-afg}

`subject_token_type` MUST be `urn:ietf:params:oauth:token-type:jwt`.
The IdP MUST validate the `subject_token` under its configured input:

| Input | Presentation | Identity resolved by the IdP |
|---|---|---|
| Platform JWT | `subject_token` only; separate client authentication when required | Approved issuer and exact configured identity claims |
| Client Attestation | Same JWT in `subject_token` and `OAuth-Client-Attestation` | Approved `(iss, sub)` or shared-client `(iss, sub, agent_id)` binding |
| JWT-SVID | Same JWT in `subject_token` and `client_assertion`, with the `jwt-spiffe` assertion type | Approved trust domain and exact SPIFFE ID in `sub` |
| WIT-SVID | Same JWT in `subject_token` and `OAuth-Client-Attestation` | Approved trust domain and exact SPIFFE ID in `sub` |

For ATTEST, JWT-SVID, and WIT-SVID, `subject_token` MUST contain the
identical JWT used for client authentication. The IdP MUST reject a
mismatch with `invalid_grant`, even if both JWTs identify the same
agent. The generic JWT token type MUST NOT select an input or relax
its validation requirements. Trusted configuration determines
credential type, issuer or trust-domain validation, identity mapping,
and required proofs under {{inputs}}. A direct input carrying `act`
MUST be rejected with `invalid_grant`; this path represents a
self-acting agent.

These checks establish subject evidence, not permission to obtain
AFG. The IdP MUST resolve the Registered Agent under {{identity}} and
apply {{idp-processing}} before issuance. The resulting AFG `sub` is
that Registered Agent's identifier. It MUST NOT be copied from an
external `sub`, `client_id`, or instance identifier merely because
that value was authenticated.

For a shared client, `agent_id` selects an approved binding without
granting authority.

For ATTEST and WIT-SVID, the DPoP key MUST match the credential's
`cnf.jwk` under the selected input. Platform JWTs and JWT-SVIDs retain
the bearer credential and DPoP association rules in {{bearer-reuse}}.
For ATTEST, JWT-SVID, and WIT-SVID the same JWT also authenticates the
client. No additional credential issuance is required for any direct
JWT input.

Example direct exchange using Client Attestation:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...attestation...
DPoP: eyJ...dpop-proof...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=
  https%3A%2F%2Fplatform.example%2Fagents%2Fsupport-agent-7
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aafg
&subject_token=eyJ...attestation...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

### IdP Access Token {#afg-access-token}

Where supported under {{bootstrap}}, `subject_token` MAY instead be
an eligible IdP-issued access token, with
`subject_token_type=urn:ietf:params:oauth:token-type:access_token`.
The IdP MUST apply the token and current-authentication checks in
{{idp-processing}}. X.509-SVID uses this path because its TLS proof
supplies no JWT subject token. [SPIFFE Workload with X.509-SVID](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md#spiffe-flow) shows the complete flow.

## Agent Acting for a User {#delegated-exchange}

`requested_token_type` MUST be
`urn:ietf:params:oauth:token-type:id-jag`. `actor_token` MUST be
the IdP-issued access token, with
`actor_token_type=urn:ietf:params:oauth:token-type:access_token`.
The IdP MUST apply Actor Profile's JWT access-token actor-input
processing. The token's `sub` identifies the Registered Agent;
the client identity does not supply `act.sub`. Acquisition under
{{bootstrap}} is required when no eligible actor token is available.
The direct JWT input in {{direct-afg}} applies only to self-acting
AFG; it does not change Actor Profile's actor-input rules.

`subject_token` MUST be a user credential accepted under {{ID-JAG}}.
Implementations MUST support an OpenID Connect ID Token with
`subject_token_type=urn:ietf:params:oauth:token-type:id_token`.
Other inputs permitted by ID-JAG MAY be supported with their
validation and authorization limits. Inputs carrying an existing
`act` chain MUST be rejected, not erased or extended.

For a shared client, the user credential was issued to the shared
client and cannot distinguish the agents behind it. The delegation
approval verified in {{idp-processing}} is the only element that names
the acting agent. The IdP MUST NOT issue an ID-JAG for a shared-client
agent without an approval that names that agent.

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...attestation...
DPoP: eyJ...dpop-proof...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=
  https%3A%2F%2Fplatform.example%2Fagents%2Fsupport-agent-7
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid-jag
&subject_token=eyJ...user-id-token...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid_token
&actor_token=eyJ...agent-access-token...
&actor_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

## IdP Processing {#idp-processing}

Before issuing a grant, the IdP MUST complete these checks:

1. **Validate request evidence.** Validate the DPoP proof and required
   client authentication under {{inputs}}. For direct AFG, validate
   the subject credential and resolve its binding under {{direct-afg}}.
2. **Validate any IdP access token.** Apply {{idp-access-token}},
   including signature, JWT type, issuer, audience, lifetime, and
   issuance eligibility. Then:

   * Match the token's client and DPoP key to the current request.
   * Verify that its recorded binding still identifies the same agent,
     Source Tenant, and input method.
   * For ATTEST and SPIFFE, match current authentication to that binding.
   * For platform origin, apply {{platform-client}} to the recorded
     binding. No new platform JWT is needed; the IdP access token
     does not authenticate the client.

3. **Authorize the target.** Check current agent status, authority
   trust, binding, assignment, and permitted output. Validate the
   RAS/resource association and determine a nonempty authorized subset
   of the requested scopes.
4. **Authorize delegation, for ID-JAG.** Validate the user credential
   under {{ID-JAG}}, including audience/client checks and scope
   ceilings. Resolve the user and downstream client, and verify the
   approval described below.
5. **Construct the grant.** Apply {{grant}} using the resolved
   principal and proven key, without expanding the authority above.

### Delegation Approval {#delegation-approval}

The IdP MUST authorize the Registered Agent to act for the user in the
requested client, tenant, RAS, resource, and scope context. It MUST
reject issuance when that delegation is absent, expired, revoked, or
insufficient, as specified in {{exchange-errors}}.

Approval MUST NOT be inferred from user sign-in or possession of both
credentials. A shared client MUST NOT reuse one agent's approval for
another. Approval records, policy engines, and storage schemas are
implementation choices. An approval mechanism needs to authenticate
the approving party, verify its authority, and support withdrawal;
these are trust assumptions for the authorization decision.

## Grant Construction {#grant}

The IdP MUST issue a signed JWT using an approved asymmetric algorithm
and a `kid` resolved through trusted issuer configuration. Grant
issuers and validators MUST support `ES256` {{RFC7518}} in addition
to algorithms required by the underlying specifications.

Both grants MUST contain the following claims:

| Claim | Value |
|---|---|
| `iss` | IdP issuer identifier |
| `aud` | Exact target RAS issuer identifier, as a string or a single-element array |
| `resource` | Approved resource URI |
| `scope` | Nonempty authorized subset of the requested scopes, using {{RFC6749}} scope syntax |
| `cnf.jkt` | Confirmation claim {{RFC7800}} with the SHA-256 JWK thumbprint under {{RFC9449, Section 6.1}} |
| `iat`, `exp` | Issuance and expiration NumericDates; `0 < exp - iat <= 300` seconds |
| `jti` | Unique grant identifier; the IdP MUST NOT reuse `(iss, jti)` |

For ID-JAG, `exp` MUST NOT exceed the expiration of the accepted user
credential or applicable delegation, where either has a fixed
expiration. The agent credential or IdP access token is valid at
exchange; its remaining validity does not bound the grant.

### Agent Federation Grant {#afg-profile}

An Agent Federation Grant (AFG) is an IdP-issued JWT authorizing a
Registered Agent to request self-acting access at one RAS. An AFG MUST
use JWS Compact Serialization {{RFC7515}}. This section
and {{consumption}} define its issuance and redemption requirements.
The registrations in {{iana}} belong to this specification.

In addition to the common claims above, the AFG MUST have:

| Header or claim | Value |
|---|---|
| Protected-header `typ` | `oauth-afg+jwt` |
| `iss` | IdP issuer identifier for the Source Tenant |
| `sub` | Registered Agent identifier resolved under {{idp-processing}} |

The AFG MUST NOT contain `act`. Its token type is
`urn:ietf:params:oauth:token-type:afg` ({{iana}}). The `scope` and
`resource` claims use the definitions in {{ID-JAG}}. Its sole audience
is the target RAS issuer identifier under {{grant}}.

#### Tenant Issuers and Agent Identifiers

The IdP MUST use a distinct issuer identifier per Source Tenant and
publish the authorized keys through that issuer's metadata. Distinct
signing keys per tenant are RECOMMENDED where the deployment provides
independent tenant signing authority. A shared signing service can
use shared keys if it enforces issuer-specific signing authorization.
The RAS's issuer-scoped validation requirements apply in either case.

The RAS MUST:

* Select an allowlisted exact `iss` and validate only with keys
  authorized for that issuer.
* Retain the issuer association in key caches. Neither `kid` alone
  nor a union of tenant key sets can select a verification key.
* Interpret `sub` and `jti` within that issuer's namespace.
* Treat `sub` as an exact-match opaque string, including when the IdP
  uses a URI under the tenant issuer.

The Registered Agent identifier is immutable and never reassigned. It is the
same Registered Agent identifier for direct JWT and IdP access-token
inputs.

#### Agent Properties and Provisioning

Agent Properties are optional attributes of the Registered Agent and
its memberships. An AFG MAY carry these claims:

* `groups` and `roles` use {{RFC9068}} definitions and describe the
  agent's memberships.
* `name` uses the OpenID Connect definition {{OIDC}}. It MUST NOT
  serve as an authorization or attribution key.

The RAS MUST NOT require prior provisioning merely to accept an AFG
subject under an allowlisted issuer. It MUST apply issuer-specific
policy before authorizing access. Authorization dependent on a
provisioned record can be withheld until correlation succeeds under
{{agent-correlation}}. Agent Properties are authoritative only to
the extent configured for that issuer.

### Identity Assertion JWT Authorization Grant {#id-jag-profile}

The IdP MUST construct the JWT under {{ID-JAG}} and {{ACTOR-PROFILE}},
with the following values:

| Header or claim | Value |
|---|---|
| Protected-header `typ` | `oauth-id-jag+jwt` |
| `sub` | User identifier resolved under ID-JAG subject-mapping rules |
| `act.iss` | IdP issuer identifier |
| `act.sub` | IdP-issued actor token's `sub` |
| `client_id` | Downstream client identifier |

Exactly one actor is introduced. {{ACTOR-PROFILE, Section 3.4}}
recommends `act.sub_profile`; this profile retains that recommendation
without making the claim mandatory. Deployments omitting the annotation
follow Actor Profile's unclassified-actor processing. Entity Profiles
{{ENTITY-PROFILES}} remains a transitive normative dependency through
Actor Profile despite its informative classification here.

Other required ID-JAG claims, including applicable tenant context,
follow ID-JAG. Translating the
client identifier MUST NOT rewrite the actor's namespace or substitute
a recipient-specific agent identifier. ID-JAG's issuer-identifier
audience rule applies instead of the token-endpoint audience shown
in Actor Profile's examples.

### Example Grant Payloads

Example AFG payload:

~~~ json
{
  "iss": "https://idp.example/tenant/acme",
  "sub": "agent-42",
  "aud": "https://as.app.example",
  "resource": "https://api.app.example",
  "scope": "tickets.read",
  "cnf": {
    "jkt": "Ak20Cf62SpTybasujYXbaI-Ms655MyvOZCtnnf8y1QU"
  },
  "iat": 1789128000,
  "exp": 1789128240,
  "jti": "grant-f194"
}
~~~

Example ID-JAG payload for the managed-device flow in [Harness on a Managed Device](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md#device-flow):

~~~ json
{
  "iss": "https://idp.example/tenant/acme",
  "sub": "user-17",
  "act": {
    "iss": "https://idp.example/tenant/acme",
    "sub": "agent-17"
  },
  "client_id": "dev-agent-at-app",
  "aud": "https://as.app.example",
  "resource": "https://api.app.example",
  "scope": "tickets.read",
  "cnf": {
    "jkt": "Ak20Cf62SpTybasujYXbaI-Ms655MyvOZCtnnf8y1QU"
  },
  "iat": 1789128000,
  "exp": 1789128240,
  "jti": "grant-f195"
}
~~~

## Successful Response {#exchange-response}

The response follows {{RFC8693, Section 2.2.1}}. The IdP MUST return:

| Parameter | Value |
|---|---|
| `access_token` | Issued grant |
| `issued_token_type` | Requested AFG or ID-JAG token type |
| `token_type` | `N_A`; the returned grant is not an API access token |
| `expires_in` | Remaining grant lifetime in seconds |
| `scope` | Approved scopes, matching the grant's `scope` |

The IdP MUST NOT issue a refresh token in this response.

The client MUST verify the returned `issued_token_type` and
`token_type`.
It SHOULD inspect the grant's `cnf.jkt` to detect a missing or incorrect
key binding, following ID-JAG's recommendation. A client that inspects the grant
SHOULD also check its type, audience, resource, and scope against the
request and reject inconsistencies. Cryptographic validation and
binding enforcement remain the RAS's responsibility.

## Error Response {#exchange-errors}

The IdP MUST return errors under {{RFC8693, Section 2.2.2}} and the
applicable authentication or proof specification. This profile uses
`invalid_grant` for credential and binding failures, consistent with
ID-JAG and Actor Profile, as a more specific error than RFC 8693's
default `invalid_request`.

| Condition | Error |
|---|---|
| Malformed request, duplicate parameter, prohibited parameter, or unsupported output/input combination | `invalid_request` |
| Unsupported `grant_type` | `unsupported_grant_type` |
| Client not permitted to use the requested grant type | `unauthorized_client` |
| Invalid subject or actor credential, disallowed actor chain, or inconsistent binding | `invalid_grant` |
| Missing, invalid, or unapproved target RAS/resource | `invalid_target` |
| Invalid scope or no authorized requested scope | `invalid_scope` |
| Missing or insufficient delegation approval after credential validation | `actor_unauthorized` under {{ACTOR-PROFILE}} |
| Failed client authentication | Error defined by the authentication method |
| Missing or invalid DPoP proof | `invalid_dpop_proof`, subject to the selected authentication method's proof errors |
| Missing or invalid required DPoP nonce | `use_dpop_nonce` with `DPoP-Nonce` under {{RFC9449, Section 8}} |

The IdP MUST validate client, subject, and actor credentials before
evaluating or disclosing delegation status. Absent, revoked, expired,
and insufficient approvals MUST produce the same `actor_unauthorized`
response without user, agent, assignment, or approval details. Error
descriptions and response timing SHOULD NOT distinguish those causes.
A failed delegated request MUST NOT fall back to a self-acting grant.

# Obtaining an IdP Access Token When Needed {#bootstrap}

This path obtains the canonical agent token defined in
{{idp-access-token}} when no eligible token is held:

* X.509-SVID uses it as the AFG exchange subject.
* All delegated inputs use it as the ID-JAG actor credential.
* Other AFG inputs can use it when the deployment supports that path.

The IdP MUST NOT require acquisition before direct JWT-to-AFG exchange.
Acquisition establishes an exchange credential; subsequent requests
still require authentication and current authorization checks.

Example decoded Client Attestation payload for an agent with its
own client identity. The IdP maps this client to `agent-42`; the
subsequent requests and grants use that binding.

~~~ json
{
  "iss": "https://attester.example/tenant/acme",
  "sub": "https://platform.example/agents/support-agent-7",
  "iat": 1789128000,
  "exp": 1789128300,
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "x": "VcKVNBZ4IaBAYW3jxM4w3TJFVA7myeUGQyGt-g_yvpQ",
      "y": "f-E-hYE3TAWKwhVv9pej9NABs9SX9XsNO80x57jFTyU"
    }
  }
}
~~~

For a shared client, the attestation instead uses that client's
identifier, such as `https://platform.example/oauth-client`, as
`sub` and includes `"agent_id": "support-agent-7"`. The request's
`client_id` matches that shared client identifier. The approved
binding can resolve to the same `agent-42` in either model.

## Request

ATTEST and SPIFFE clients MUST use the client credentials grant with
`resource` equal to the selected exchange audience in
{{idp-access-token}} and authentication under
{{inputs}}. Platform JWT input instead uses {{platform-acquisition}}.
The client credentials grant retains its confidential-client
requirement under {{RFC6749, Section 4.4}}. The example uses ATTEST.

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...attestation...
DPoP: eyJ...dpop-proof...

grant_type=client_credentials
&client_id=
  https%3A%2F%2Fplatform.example%2Fagents%2Fsupport-agent-7
&resource=
  https%3A%2F%2Fidp.example%2Ftoken
~~~

### Acquisition from Platform JWT Evidence {#platform-acquisition}

The client MUST use token exchange with separate client authentication
under {{platform-client}} and the following parameters:

| Parameter | Required value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `subject_token` | Platform JWT validated under {{platform-jwt-input}} |
| `subject_token_type` | `urn:ietf:params:oauth:token-type:jwt` |
| `requested_token_type` | `urn:ietf:params:oauth:token-type:access_token` |
| `resource` | Selected exchange audience under {{idp-access-token}} |

The client MUST omit `audience`, `scope`, `actor_token`, and
`actor_token_type`; their presence produces `invalid_request`. The
platform JWT MUST NOT be used with the client credentials grant.

## Processing and Response

The IdP MUST validate the configured input and DPoP proof, resolve
the Federation Binding, and verify that the Registered Agent is
active and permitted to use this client and exchange service.

The issued token MUST satisfy {{idp-access-token}}. Its issuance does
not authorize skipping authentication or current-policy checks at exchange.

The response follows {{RFC6749, Section 5.1}} for client credentials
and {{RFC8693, Section 2.2.1}} for platform JWT exchange. The IdP MUST:

* Return `access_token`, `token_type=DPoP`, and `expires_in`.
* For platform JWT exchange, also return
  `issued_token_type=urn:ietf:params:oauth:token-type:access_token`.
* Omit `refresh_token`.

Clients need not parse the access token. Reuse and key changes follow
{{idp-access-token}} and {{inputs}}. Errors follow the applicable
grant, authentication, and DPoP specifications, with credential and
binding failures reported as described in {{exchange-errors}}.

Example client credentials response:

~~~ json
{
  "access_token": "eyJ...agent-access-token...",
  "token_type": "DPoP",
  "expires_in": 300
}
~~~

# Grant Consumption {#consumption}

Redemption uses the RFC 7523 JWT bearer grant, with DPoP proof of
possession as required by this profile. The grant format and processing
follow {{ID-JAG}} for delegated access and {{afg-profile}} for
self-acting access. Delegated processing also follows Actor Profile,
including preservation of `act`.

## Redemption Request {#redemption-request}

The client MUST present a fresh DPoP proof and include each required
parameter exactly once:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:jwt-bearer` |
| `assertion` | AFG or ID-JAG |
| `resource` | Exact value of the grant's `resource` claim |
| `scope` | Optional subset of the grant's scopes; omission requests the grant's scopes |

Client authentication depends on the grant:

* **ID-JAG:** the client MUST authenticate using a credential registered
  or otherwise trusted for the grant's downstream `client_id`. The
  RAS MUST match that identifier to the authenticated client. An IdP
  client-ID mapping does not provision the downstream credential.
* **AFG:** the RAS MAY require client authentication by configuration,
  in addition to the DPoP proof.

DPoP possession alone MUST NOT satisfy a client authentication
requirement. [Client Authentication at the RAS](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md#ras-auth) describes separate downstream credentials.

## Validation and Replay Prevention {#redemption-validation}

Before issuing an access token, the RAS MUST:

1. Validate the grant under {{RFC7523}}, {{RFC8725}}, and the selected
   output profile, including signature, protected-header `typ`, trusted
   issuer, required claims, and time checks under {{time-validation}}.
2. Require `aud` to identify only this RAS issuer, as defined in
   {{grant}}. A token endpoint URL or additional audience is not accepted.
3. Match the requested resource to the grant and restrict scopes to
   the grant's scope ceiling and the RAS's authorization policy.
4. Validate the DPoP proof under {{RFC9449}} and match its SHA-256 JWK
   thumbprint to `cnf.jkt`. No `ath` is required for grant redemption.
5. Enforce single use of `(iss, jti)`:

   * Retain consumed identifiers through `exp` plus the maximum allowed
     clock skew across validators.
   * Make replay checking and consumption atomic across token-endpoint
     replicas, so concurrent redemptions cannot issue multiple tokens.
   * Reject a previously consumed grant, even with a fresh DPoP proof.

The RAS applies its own authorization policy before issuance. A valid
grant establishes an authorization ceiling, not an obligation to issue
an access token.

## Access Token Response {#redemption-response}

The RAS MUST issue a sender-constrained access token and MUST NOT
issue a bearer access token from a grant under this profile. A
DPoP-bound access token uses the proof key under {{RFC9449}}; another
sender-constraint mechanism requires its own binding and proof rules.
The client uses this access token at the resource server.

For AFG, the RAS MUST make any Agent Properties available to the
resource server's authorization decision. Refresh-token behavior for
both grants follows {{refresh-policy}}.
Access-token format, lifetime, and introspection follow the selected
grant and resource policy.

## Redemption Errors {#redemption-errors}

The RAS MUST return an OAuth token error response under
{{RFC6749, Section 5.2}} with the applicable error below:

| Condition | Error |
|---|---|
| Malformed request or duplicate parameter | `invalid_request` |
| Unsupported `grant_type` | `unsupported_grant_type` |
| Failed required client authentication | Error defined by the authentication method |
| Invalid grant, wrong audience, client mismatch, or replayed grant | `invalid_grant` |
| Missing DPoP proof or proof key does not match the grant | `invalid_grant` under ID-JAG's bound-grant rules |
| Presented DPoP proof fails RFC 9449 validation | `invalid_dpop_proof` |
| Missing or invalid required DPoP nonce | `use_dpop_nonce` with `DPoP-Nonce` under {{RFC9449, Section 8}} |
| Missing, invalid, or mismatched resource | `invalid_target` |
| Requested scope exceeds the grant or no requested scope is authorized | `invalid_scope` |

The same bound-grant error distinctions apply to AFG and ID-JAG.
A nonce challenge follows RFC 9449 and does not consume the grant.

## Continuing Delegated Access {#delegated-lifecycle}

A background agent needs continuing user authorization as well as its
own credential. Agent acquisition and grant exchange issue no refresh
token. OpenID Connect sign-in can separately issue a user-session
refresh token.

To obtain another ID-JAG, the client MUST present a currently valid
user credential and an eligible agent actor token. The IdP MAY accept
a user-session refresh token as `subject_token` under ID-JAG, or use
it in the normal OpenID Connect flow to issue a new ID Token.
When accepting a refresh token, the IdP MUST enforce:

* Its client binding, current validity, and revocation status.
* Its scope ceiling and the agent's current delegation approval.
* The grant lifetime limits in {{grant}}, including when the refresh
  token has no fixed expiration.

If no eligible user credential can be obtained, the agent MUST stop
delegated issuance and obtain renewed user authorization.

## Refresh Tokens at the RAS {#refresh-policy}

For both AFG and ID-JAG, the RAS SHOULD NOT issue a refresh token by
default. A deployment MAY enable refresh when continuing authorization
can be checked independently of a new IdP grant. The RAS MUST:

* Establish an authorized OAuth client at redemption before issuing
  a refresh token, including when AFG redemption would otherwise
  omit client authentication.
* Bind each refresh token to that client, agent, resource, scope
  ceiling, and sender key; for ID-JAG, also retain the user and
  delegation association.
* Apply refresh-token protection under {{RFC9700, Section 4.14}} and
  verify the client and sender bindings on refresh.
* Recheck current authorization under its configured freshness and
  revocation policy, including agent status and, for ID-JAG, continuing
  delegation. A RAS unable to perform those checks MUST NOT issue a
  refresh token.

Neither grant becomes reusable when refresh is enabled; both remain
single use under {{redemption-validation}}. Deployments that do not
establish continuing authorization obtain a new grant instead.

## Request Cost

Direct AFG requires an IdP exchange and RAS redemption. With no
eligible IdP token, the adapter path requires acquisition, exchange,
and redemption. User-credential renewal can add another request for
delegation. Reusing an eligible adapter token avoids acquisition;
its configurable lifetime does not remove current-policy checks.

The grant's short lifetime and single-use rule bound the redemption
window, not the downstream access-token lifetime. The same refresh
policy in {{refresh-policy}} applies to self-acting and delegated
access; no AFG behavior is inherited from WAG.

## Agent Record Correlation {#agent-correlation}

The canonical Registered Agent identity is the exact pair of IdP
issuer and agent identifier. For an AFG issued here, the pair is
`(iss, sub)`; for delegated ID-JAG it is `(act.iss, act.sub)`.

A RAS using provisioned agent records MUST resolve both forms through
the same issuer-qualified mapping. It MUST NOT key that lookup on
bare `sub`, the OAuth client, or instance context. Missing or ambiguous
mappings MUST prevent authorization that depends on that record.

Provisioning protocols and policy rules remain deployment choices.
If SCIM `externalId` is used, the provisioning relationship MUST
associate it with the IdP issuer so another issuer's equal string
cannot resolve to the same agent accidentally. Group membership
resolved for this agent MUST NOT be attributed to an ID-JAG user,
or user membership to the agent. [One Agent Record for Self-Acting and Delegated Access](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md#provisioning-example) illustrates
this contract without defining new SCIM attributes.

# Metadata and Configuration {#metadata}

The IdP MUST advertise its implemented capabilities through existing
metadata under {{RFC8414}} and the referenced specifications, except
for the JWT-SVID configuration described below:

| Capability | Metadata |
|---|---|
| Token exchange | `grant_types_supported` includes `urn:ietf:params:oauth:grant-type:token-exchange` |
| Client credentials acquisition, when supported | `grant_types_supported` includes `client_credentials` |
| Client authentication | `token_endpoint_auth_methods_supported` includes implemented methods, such as `attest_jwt_client_auth_dpop`, `spiffe_x509`, or `spiffe_wit` |
| DPoP | `dpop_signing_alg_values_supported` includes `ES256` under {{RFC9449}} |
| Grant outputs | `identity_chaining_requested_token_types_supported` lists supported AFG and/or ID-JAG token types under {{IDENTITY-CHAINING}} |
| Delegation, when supported | `actor_profile_token_exchange` with the role-specific arrays below |

An IdP supporting delegated ID-JAG MUST include the following in
`actor_profile_token_exchange` under {{ACTOR-PROFILE}}:

* `subject_token_types_supported` includes
  `urn:ietf:params:oauth:token-type:id_token`, and includes
  `urn:ietf:params:oauth:token-type:refresh_token` when that input is
  supported under {{delegated-lifecycle}}.
* `actor_token_types_supported` includes
  `urn:ietf:params:oauth:token-type:access_token`.
* `requested_token_types_supported` includes
  `urn:ietf:params:oauth:token-type:id-jag`.

An IdP claiming delegated ID-JAG support under this profile MUST
advertise ID-JAG in both
`actor_profile_token_exchange.requested_token_types_supported` and
`identity_chaining_requested_token_types_supported`. Clients MUST NOT
attempt this profile's delegated exchange if the two advertisements
disagree about ID-JAG support. A single advertisement can describe a
path outside this profile; it does not establish support for this one. The arrays need not otherwise be equal:
AFG is self-acting and is advertised only through identity chaining
for this profile; an AS can also support unrelated Actor Profile
outputs. These coarse signals do not replace the binding configuration.

JWT-SVID support MUST be agreed through trusted configuration using
the assertion type in {{jwt-svid-input}}. SPIFFE OAuth defines that
assertion type but no corresponding `token_endpoint_auth_methods_supported`
value. This profile does not invent one or treat `private_key_jwt`
as an advertisement of JWT-SVID support.

Platform JWT evidence defines no client authentication method. Its
issuer and claim mappings use trusted configuration. An IdP supporting
{{platform-acquisition}} also advertises the separate authentication
methods accepted on that path.

A RAS MUST advertise `urn:ietf:params:oauth:grant-type:jwt-bearer` in
`grant_types_supported`, DPoP support under {{RFC9449}}, and metadata
required by the selected grant and Actor Profile. Before issuance,
the IdP MUST verify that the configured RAS supports the required
grant, key binding, and actor processing.

Metadata discovery does not establish issuer trust or delegation
authority. {{identity}} defines trusted profile selection. No new
metadata parameter, bootstrap scope, or grant-profile URI is defined.

# Security Considerations {#security}

The security requirements of {{RFC9700}}, {{RFC8693}}, {{RFC8725}},
and the selected input and output specifications apply to their
respective protocol roles.

## Transport and Credential Handling

All acquisition, exchange, and redemption requests MUST use HTTPS
with server certificate validation. Credentials and proofs MUST NOT
appear in URLs. Token responses use the cache controls in
{{RFC6749, Section 5.1}}. DPoP does not replace transport protection.

Implementations SHOULD use asymmetric client authentication where
client authentication is required, as recommended by
{{RFC9700, Section 2.5}}. Acquisition using client credentials retains
that grant's confidential-client requirement; installing the same
secret in every distributed agent does not establish confidentiality.

## JWT Validation and Time Limits {#time-validation}

Validators MUST apply mutually exclusive validation rules to the
credential classes they accept, under {{RFC8725, Section 3.12}}.
In particular, an IdP access token, AFG, ID-JAG, client assertion, or
platform JWT does not become another credential class merely because
it has a trusted signature. The intentional dual use of a Client
Attestation, JWT-SVID, or WIT-SVID in {{direct-afg}} requires both sets
of checks.

For JWTs accepted under this profile, validators MUST:

* Enforce signature algorithms and key sources authorized for the
  credential class and issuer or trust domain.
* Enforce `exp` and, when present, `nbf` under {{RFC7519}}.
* When `iat` is present, reject a non-NumericDate value or a value
  later than the current time plus configured clock skew.
* Use a configured clock-skew allowance, without increasing a
  permitted `exp - iat` lifetime or a configured maximum age.

Deployments SHOULD keep that allowance small, normally no more than
a few minutes under {{RFC7519}}. Replay-state retention accounts for
the largest allowance used by any validator.

Required timestamps and credential-specific age and lifetime limits
are defined with each input or output. Proof freshness additionally
follows the applicable DPoP or attestation specification.

## Audience Restriction and Replay

The single-audience and resource checks in {{grant}} and
{{redemption-validation}} confine grants to one RAS and approved
resource. RFC 9700's access-token audience restriction and privilege
restriction guidance applies to downstream issuance.

Single-use processing prevents repeated issuance even by the
legitimate key holder. Short lifetimes and DPoP alone do not provide
that property. Sender constraint protects stolen grants and access
tokens while the corresponding private key remains uncompromised;
it does not establish assignments or delegation approval.

## Tenant and Authority Isolation

A compromised tenant issuer can forge subjects and properties within
its namespace, including previously unseen agents. The RAS MUST NOT
let an issuer assert another issuer's agents, memberships, or Target
Tenant. Its issuer-specific policy governs authorization for new
subjects under {{afg-profile}}.

Distinct tenant keys and issuer-bound validation limit cross-tenant
forgery, but do not protect against compromise of the IdP's shared
control plane. The IdP MUST isolate signing authority so control of
one tenant does not permit signing for another.

A shared-client attester can assert every approved `agent_id` behind
that client. A compromised platform issuer can similarly impersonate
any agent bound to it. Deployments therefore:

* SHOULD use a distinct `client_id` per tenant or governance boundary.
* SHOULD limit each authority's approved bindings to agents it governs.
* MUST enforce withdrawal of authority trust on subsequent
  authentication and grant issuance.
* SHOULD retain the credential authority and Federation Binding with
  each issuance for audit.

## Evidence Substitution and Downgrade

The evidence checks in {{identity}} and {{idp-processing}} bind agent,
client, tenant, and key to one request. Independently valid evidence
for different agents MUST NOT be combined.

Configured requirements for agent identity, key binding, or explicit
actors MUST NOT be bypassed by selecting an existing client-based
flow. A shared client alone does not authenticate the agent behind it.
Instance context does not authorize key rebinding or delegation.

## Bearer Workload Credential Theft

Platform JWTs and JWT-SVIDs are bearer credentials. Theft before first
use can let an attacker establish the initial DPoP key association.
Subsequent key matching cannot prevent that race; audience restriction,
short credential lifetimes, and transport protection limit exposure.
A DPoP nonce does not bind the bearer credential to its intended holder.

The reuse association in {{bearer-reuse}} prevents an already used JWT
from enrolling another key. Platforms MUST NOT share one cached JWT
among clients using independent DPoP keys. This also applies to SPIFFE
replicas that share a workload identity: independent keys require
credentials with distinct signing inputs. A request for another
JWT-SVID does not guarantee that its signing input differs.

Deployments unable to obtain distinct credentials need another approved
evidence path, such as X.509-SVID or WIT-SVID. None of these inputs
establishes distinct replica identity without additional evidence.

## Status Changes and Revocation {#status-changes}

The IdP MUST define freshness limits for cached authorization data and
reject data exceeding those limits. The current-status checks in
{{idp-processing}} apply on every grant issuance, including when an
IdP access token remains unexpired. Once applied at the IdP, a disabled
agent or revoked binding prevents new issuance.

Status propagation uses deployment-specific provisioning or security
event channels:

* The IdP SHOULD propagate disabled status and withdrawn assignments.
* After receiving and validating a change, the RAS MUST apply it to
  subsequent grant and refresh processing. It SHOULD revoke affected
  access and refresh tokens or report them inactive by introspection.
* A resource server enforcing that status SHOULD deny affected requests.

These rules do not guarantee delivery or immediate revocation of
issued tokens. Without a signal, a resource server can accept an
access token until expiration. Deployments allowing refresh tokens
also need a status check or revocation mechanism at renewal.

# Privacy Considerations {#privacy}

Stable agent identifiers permit correlation. The IdP SHOULD release
only necessary identity and authorization context. Raw attestation
material and private keys MUST NOT appear in grants or audit logs.

A canonical agent identifier is stable across RASes. For a per-user
agent, AFG `sub` or ID-JAG `act.sub` can therefore correlate the user
across services even when ID-JAG uses a pairwise user subject. The
IdP SHOULD NOT expose such a cross-context user pseudonym without a
correlation requirement at the receiving RASes.

This profile preserves the canonical agent identifier under
{{grant}}. Pairwise agent identifiers require an additional profile
coordinated with Actor Profile.

# IANA Considerations {#iana}

## JWT Claims Registration

This specification requests registration of the following claim in
the "JSON Web Token Claims" registry established by {{RFC7519}}:

* Claim Name: `agent_id`
* Claim Description: Attester-scoped agent principal identifier
* Change Controller: IETF
* Specification Document(s): {{agent-evidence}} of this document

The value is a nonempty StringOrURI distinguishing agents represented
by a shared ATTEST client. Platform JWT identity selectors are
configured separately under {{platform-jwt-input}}.

## OAuth URI Registration

This specification requests registration in the "OAuth URI" registry
established by {{RFC6755}}:

* URN: `urn:ietf:params:oauth:token-type:afg`
* Common Name: Token type URI for an Agent Federation Grant
* Change Controller: IETF
* Specification Document: {{afg-profile}} of this document

The URI identifies AFG in Token Exchange requests and responses. It
does not define a new `grant_type`; redemption uses the JWT bearer
grant under {{consumption}}.

## Media Type Registration

This specification requests registration of `application/oauth-afg+jwt`
in the "Media Types" registry under {{RFC6838}}:

* Type name: application
* Subtype name: oauth-afg+jwt
* Required parameters: none
* Optional parameters: none
* Encoding considerations: binary; AFG uses JWS Compact Serialization
* Security considerations: {{security}} and {{privacy}} of this document
* Interoperability considerations: implementations apply the JWT type,
  issuer, audience, authorization, proof, and replay checks in
  {{afg-profile}} and {{consumption}}
* Published specification: this document
* Applications that use this media type: OAuth clients and authorization
  servers exchanging and redeeming Agent Federation Grants
* Fragment identifier considerations: none
* Additional information:
  * Deprecated alias names for this type: none
  * Magic number(s): none
  * File extension(s): none
  * Macintosh file type code(s): none
* Person and email address to contact for further information:
  Karl McGuinness, public@karlmcguinness.com
* Intended usage: COMMON
* Restrictions on usage: none
* Author: Karl McGuinness
* Change controller: IETF
* Provisional registration: no

## Other Identifiers

`act` follows {{ACTOR-PROFILE}}, including its recommendation for
`act.sub_profile` as described in {{id-jag-profile}}. This document
registers no new actor format, API access-token type, or grant-profile
URI.

--- back

# Deployment and Compatibility {#deployment}

This appendix is informative.

A deployment can adopt user-delegated ID-JAG first, adding Actor
Profile and this document's sender-binding and replay requirements
to its existing user federation. Self-acting AFG is a separate
capability: it requires issuer-based workload trust, new-subject
handling, and the bound-grant rules in {{afg-profile}}. Supporting
ID-JAG does not imply AFG support, and a
RAS need not implement both outputs. Implementations should negotiate
only the capabilities actually deployed.

Existing ID-JAG flows, including MCP
Enterprise-Managed Authorization {{EMA}}, can authorize a client
for a user without a separately represented agent. The user is the
subject and the client is identified through normal OAuth context.
Absence of `act` does not imply absence of authorization, a human
presenter, or self-acting access. Those deployments retain their
existing authentication and sender-constraint choices and need no
bootstrap from this specification.

CIMD {{CIMD}} can supply client metadata and a common client identifier
across servers. When the client itself is the explicit actor, Actor
Profile already defines JWT client assertion input, including reuse
of one JWT as `client_assertion` and `actor_token`. That path does not
require an additional IdP-issued access token or ATTEST. A shared
client identity does not distinguish separately governed agents.
Instance identification can add audit context to client-based flows
without introducing an actor.

Agent admission and provisioning can use administrative configuration,
JIT, or SCIM Agent resources {{SCIM-AGENT}} with {{RFC7644}}. A SCIM
`externalId` {{RFC7643}} can correlate a record with the IdP agent
identifier when issuer and tenant are retained. Groups, ownership,
and assignments are policy inputs; group claims about an ID-JAG user
do not describe the agent actor's memberships. Provisioning transport,
synchronization, policy engines, access-token formats, and introspection
{{RFC7662}} are deployment choices outside this profile.

Platform-issued JWTs follow {{platform-jwt-input}}; native SPIFFE
JWT-SVID, X.509-SVID, and WIT-SVID authentication follow
{{jwt-svid-input}}, {{spiffe-input}}, and {{wit-input}}. Other credential
types need explicit binding and proof rules; support for one platform's tokens does not imply that every
token format is accepted. Direct WIT actor evidence under Actor
Profile is a different input path. It would need explicit
external-subject mapping and proof rules; it does not implicitly
substitute for the IdP access token here.

# Supporting Material

The source repository maintains non-normative
[deployment examples](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/deployment-examples.md), an
[interoperability inventory](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/interoperability.md), and
[coordination notes](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/docs/coordination.md). These documents do not
add conformance requirements.

# Document History

*RFC EDITOR: Remove this section before publication.*

* Initial version.
