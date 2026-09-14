---
title: "OAuth 2.0 Profile for Agent Federation"
abbrev: "Agent Federation"
category: std
docname: draft-mcguinness-oauth-workload-agent-federation-latest
submissiontype: IETF
stand_alone: yes
date: 2026-09-11
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
  INSTANCE:
    title: "Client Instance Identification for Attestation-Based Client Authentication"
    target: https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-assertion/draft-mcguinness-oauth-client-instance-identification.html
    author:
      - fullname: Karl McGuinness
    date: 2026-09-11
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-client-instance-identification-latest
  SPIFFE-OAUTH: I-D.ietf-oauth-spiffe-client-auth
  WIT: I-D.ietf-wimse-workload-creds
  ATTEST: I-D.ietf-oauth-attestation-based-client-auth
  ACTOR-PROFILE: I-D.mcguinness-oauth-actor-profile
  ENTITY-PROFILES: I-D.mora-oauth-entity-profiles
  ID-JAG: I-D.ietf-oauth-identity-assertion-authz-grant
  IDENTITY-CHAINING: I-D.ietf-oauth-identity-chaining
  WAG: I-D.carleton-workload-authz-grant
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
  RFC6838:
  RFC7515:
  RFC7518:
  RFC7519:
  RFC7523:
  RFC7638:
  RFC7800:
  RFC8414:
  RFC8417:
  RFC8693:
  RFC8707:
  RFC8725:
  RFC9068:
  RFC9449:
  RFC9700:
informative:
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  JWT-DPOP: I-D.parecki-oauth-jwt-dpop-grant
  RFC2046:
  RFC7662:
  RFC8252:
  RFC9396:
  SPIFFE-CONCEPTS:
    title: "SPIFFE Concepts"
    target: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
    author:
      - org: SPIFFE
    date: 2026
  EMA:
    title: "MCP Enterprise-Managed Authorization"
    target: https://github.com/modelcontextprotocol/ext-auth/blob/main/specification/stable/enterprise-managed-authorization.mdx
    author:
      - org: Model Context Protocol
    date: 2026
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
--- abstract

This specification profiles OAuth 2.0 Token Exchange to bind
platform-authenticated agents to registered principals at an identity
provider. It supports platform-issued JWTs, Attestation-Based Client
Authentication, and SPIFFE client authentication. An agent acting for
itself receives a Workload Authorization Grant; an agent acting for a
user receives an Identity Assertion JWT Authorization Grant with an
explicit actor. Both grants are key-bound and redeemed at a resource
authorization server for sender-constrained access tokens. Instance
identification is optional.

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

* **Self-acting access:** a Workload Authorization Grant (WAG)
  {{WAG}}, with the Registered Agent as subject.
* **User-delegated access:** an Identity Assertion JWT Authorization
  Grant (ID-JAG) {{ID-JAG}}, with the user as subject and the
  Registered Agent as actor under {{ACTOR-PROFILE}}.

Both grants bind to a key proved by the agent. The agent redeems the
grant at a Resource Authorization Server (RAS) for a sender-constrained
access token. The RAS trusts the IdP's grant; it need not validate the
platform's original evidence.

## Evidence and Token Paths

The IdP accepts platform-issued JWTs, Client Attestations {{ATTEST}},
or SPIFFE SVIDs {{SPIFFE-OAUTH}}. Trusted configuration maps each
external identity to one Registered Agent:

* Platform JWTs supply workload evidence as a token-exchange
  `subject_token`. Separate client authentication depends on the
  requested path.
* ATTEST and SPIFFE also authenticate an OAuth client. A shared
  ATTEST client uses `agent_id` to distinguish its agents.
* {{INSTANCE}} optionally adds stable instance context to ATTEST.

For self-acting access, a platform JWT, Client Attestation, or
WIT-SVID is exchanged directly for WAG. X.509-SVID instead uses an
intermediate IdP access token because its TLS proof supplies no JWT
subject token.

For delegated access, all inputs use an IdP access token as the
`actor_token`, alongside the user's credential. That token carries
the canonical agent identity required by Actor Profile. Platform JWT
acquisition uses token exchange with separate client authentication;
ATTEST and SPIFFE acquisition use the client credentials grant. An
eligible IdP access token can also be reused for WAG.

{{paths}} summarizes the paths; {{bootstrap}} defines acquisition.

## Relationship to Other Specifications

This profile defines agent evidence, identity resolution, IdP access
token acquisition, grant issuance, and shared redemption requirements.
ID-JAG's format and downstream processing follow {{ID-JAG}} and
{{ACTOR-PROFILE}}. WAG's IdP issuance profile is defined in
{{wag-profile}}; open coordination items are recorded in
{{coordination}}.

Actor Profile applies to user delegation. The Registered Agent is the
actor, and instance identification adds context without adding an
actor hop. Self-acting access does not require Actor Profile.

Existing client-based delegation, including MCP Enterprise-Managed
Authorization, can be used when a separately governed agent principal
is unnecessary. {{models}} covers model selection, {{deployment}}
covers compatibility, and {{flows}} provides end-to-end examples.

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

* **Acting relationship:** each federation model can produce WAG with
  the agent as `sub`, or ID-JAG with the user as `sub` and agent as
  `act`. An agent can be both an OAuth client and a delegated actor.
* **Instance context:** one agent can run in several installations or
  executions. Optional `client_instance_id` distinguishes the configured
  unit for audit and risk. It does not select the principal or acting
  relationship, and key possession is required without it.

# Conventions and Scope

{::boilerplate bcp14-tagged}

OAuth terms follow {{RFC6749}} and {{RFC8693}}. Client Attestation,
Client Attester, and Client Instance follow {{ATTEST}}. Instance
Identifier and Instance Context follow {{INSTANCE}}. The IdP acts as
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

* WAG with a JWT input requires direct exchange under {{direct-wag}}.
* X.509-SVID and delegated ID-JAG require IdP access-token acquisition
  under {{bootstrap}}. Acquisition is optional for direct-WAG-only
  implementations.
* When acquisition is supported, the corresponding IdP access-token
  input is supported for each implemented output.
* Delegated ID-JAG requires {{ACTOR-PROFILE}}.

A RAS claiming this profile MUST implement {{consumption}} and the
validation rules for each output it accepts. The parties MUST
establish common inputs and outputs through trusted configuration
and the metadata in {{metadata}}.

The requirements of the referenced protocols apply unless this
profile explicitly narrows an option. WAG issuance details in
{{wag-profile}} are specific to this document pending coordination
with {{WAG}}. Task authority, delegation chains, and unlisted inputs
are outside this profile.

# Profile Selection and Identity Binding {#identity}

The IdP MUST configure:

* The input, identity model, Source Tenant, and permitted outputs.
* Credential verification authorities, keys, and validation policy.
* Approved RAS issuers, resources, Target Tenants, and subject and
  client mappings.

Unsigned request hints and discovered client metadata MUST NOT
establish this authority or change the configured binding. Bindings
can be imported from a platform registry. The IdP MUST authenticate
and audit binding changes, including imports, and record the platform
issuer and exact identity claims being bound.

| Input and identity model | Federation Binding lookup |
|---|---|
| Platform-issued JWT, imported workload | Approved issuer and configured exact identity claims under {{platform-jwt-input}}; OAuth client identity is separate |
| ATTEST, agent is the client | Exact attestation `(iss, sub)`; no `agent_id` |
| ATTEST, shared client | Exact attestation `(iss, sub, agent_id)` |
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
A new installation, execution, or key does not create a new principal.

The IdP MUST verify all configured evidence and an unambiguous Source
Tenant; grant issuance also requires an unambiguous Target Tenant. Evidence has distinct roles:

* Client authentication establishes the OAuth client.
* The Federation Binding establishes the Registered Agent.
* The DPoP proof establishes possession of the binding key.
* Validated instance evidence supplies optional execution context.

The IdP MUST NOT substitute one role for another or bypass a required
binding when evidence is omitted. Other client flows retain their own
requirements.

## Evidence and Client Authentication {#inputs}

Every acquisition and exchange request MUST include a fresh DPoP
proof under {{RFC9449}}. Implementations MUST support `ES256` for
DPoP. The IdP MUST bind the resolved agent, source tenant, and proven
key, plus the authenticated logical client when required, to the same
request. Platform JWTs supply subject evidence; the other inputs also
authenticate the client. Subsequent use of an IdP access token follows
{{idp-processing}}.

* When issuing an intermediate access token, the IdP MUST record
  its input method and external binding and check their current
  validity when that token is exchanged under {{idp-processing}}.
* The request MUST NOT supply a separate `agent_id` parameter; its
  presence MUST cause `invalid_request`. Within credentials, `agent_id`
  is permitted only for shared-client ATTEST or as an explicitly
  configured platform JWT identity claim. Other
  uses MUST be rejected with `invalid_client_attestation` for ATTEST
  and `invalid_grant` for other subject evidence.
* No input alone establishes stable instance context. The IdP MUST
  NOT infer `client_instance` from a workload identifier, key, or
  certificate, or copy unvalidated claims. Validated claims under
  {{instance-identification}} are the only source of that context.
* A JWT input credential MAY be the `subject_token` for direct WAG
  exchange under {{direct-wag}}. Input credentials MUST NOT be used
  as `actor_token`; delegated exchange uses an IdP-issued access token.
* Renewal or reissuance of an input credential does not rebind an
  existing access token to a different DPoP key. A changed key
  requires new issuance.

### Platform-Issued JWT {#platform-jwt-input}

The client MUST present a JWT issued by an approved platform as
`subject_token`, with
`subject_token_type=urn:ietf:params:oauth:token-type:jwt`, in a token
exchange request. This input is workload evidence, not client
authentication under {{RFC7523}}. It MUST NOT be presented as
`client_assertion`. The requested output is WAG under {{direct-wag}}
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
* Maximum credential age and lifetime. Maximum age MUST NOT exceed
  300 seconds; clock skew follows {{time-validation}}.
* A credential class, identified by either a dedicated issuer or an
  explicit protected-header `typ` used only for that class. Generic
  `typ=JWT` is insufficient.

The IdP MUST validate the JWT under {{RFC7519}} and {{RFC8725}},
including its signature, issuer, audience, and credential class, and
reject it if any of the following applies:

* `iss` or `sub` is missing or is not a nonempty string.
* `iat` or `exp` is missing or is not a NumericDate, `iat` does not
  precede `exp`, or a time check in {{time-validation}} fails.
* Its age or lifetime exceeds the configured limit.
* It is intended as a user ID Token or API access token.
* It contains `act` or fails a configured identity selector.

#### DPoP Binding and Credential Reuse

A platform-issued JWT is a bearer credential with no key of its
own. A separate DPoP proof establishes the token-binding key, which
the platform need not know. Both MUST be validated in the same request.

For this input the IdP MUST require a server-provided DPoP nonce under
{{RFC9449, Section 8}} on every acquisition and exchange request.
A missing or invalid nonce MUST produce `use_dpop_nonce` with a fresh
nonce; the client retries with a new proof. This prevents proof
pre-generation but does not prevent theft of the bearer JWT before
its first use.

The same platform JWT MAY be reused with fresh DPoP proofs. For each
successful use, the IdP MUST enforce the following association:

1. Compute the SHA-256 digest of the JWS Signing Input {{RFC7515}}.
2. On first use, atomically associate that digest with the Federation
   Binding and proven DPoP key.
3. Retain the association until `exp` plus allowable clock skew, even
   if the configured maximum age makes the JWT unusable sooner.
4. Reject reuse with another binding or key. Reuse with the same
   binding and key remains subject to current validation and status
   checks, but MUST NOT be rejected solely because the JWT or its
   `jti` was previously seen.

Excluding the signature from the digest prevents another valid
signature over the same signing input from bypassing this check.
Validation failures use `invalid_grant`; separate client
authentication errors retain their base processing.

Clients using cached JWTs MUST retain the associated DPoP key. A key
change requires a newly issued JWT with a different signing input,
such as a new `iat` or `jti`, or another independently authenticated,
approved binding. The IdP MUST NOT reset the association merely
because the caller supplies a new key.

Platforms unable to issue a fresh credential or target the IdP
audience can provide a token-exchange service or act as an ATTEST
attester instead.

### Client Authentication for Platform Evidence {#platform-client}

For direct platform-JWT-to-WAG exchange, the IdP MAY permit requests
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

Requests using a platform-origin IdP access token MUST include the
server-provided DPoP nonce required by {{platform-jwt-input}}.

A JWT used for client authentication MUST satisfy that method's client
identity and key requirements independently of the platform JWT. For
RFC 7523 client authentication, `sub` MUST be the OAuth `client_id`.
For ATTEST used solely in this role, its client authentication rules
apply; it does not independently select the Registered Agent or supply
instance context for the platform evidence path. No new client
authentication method or assertion type is defined here.

### Client Attestation {#agent-evidence}

The client MUST use `attest_jwt_client_auth_dpop` under {{ATTEST}}.
The Client Attestation MUST satisfy ATTEST and these additional rules:

* `iss` and `sub` are nonempty strings; `sub` equals `client_id`.
* `iat` and `exp` are NumericDates, with `iat` preceding `exp`.
* The signature uses an approved asymmetric algorithm and a `kid`
  resolved through trusted attester configuration. Implementations
  MUST support `ES256`.
* When the agent is the client, `agent_id` is absent. For a shared
  client, `agent_id` is a nonempty StringOrURI {{RFC7519}} naming
  the agent in the attester's namespace.

The attester MUST verify authorized execution of the named agent and
possession of the key in `cnf.jwk`.

The IdP MUST validate the attestation and combined-mode proof under
ATTEST, including the match between the DPoP key and `cnf.jwk`, and
apply a configured maximum age and lifetime for each attester:

* Missing or incorrectly typed required claims, invalid time ordering,
  or an `agent_id` inconsistent with the configured model produce
  `invalid_client_attestation`.
* An attestation outside configured age or lifetime limits produces
  `use_fresh_attestation` under ATTEST.

Request freshness comes from the proof and current status checks;
this profile does not impose a fixed attestation lifetime.

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

WIT-SVID uses the separate binding in {{wit-input}}. A JWT-SVID lacks
the `iss` claim {{RFC7523}} requires and remains outside this profile.

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
* A direct WAG request proves the new key under {{direct-wag}}.

{{WIT}} recommends a fresh key for each WIT, so reuse across renewal
is expected only where the deployment retains the key. The lifetime
limit in {{idp-access-token}} applies to the access token, not the WIT.

## Optional Instance Identification {#instance-identification}

An ATTEST deployment MAY configure {{INSTANCE}} for installation or
execution correlation. When configured, the IdP MUST:

* Validate the instance evidence, lifecycle granularity, and applicable
  instance status under that specification.
* Match current instance evidence to any context carried in an IdP
  access token presented for exchange.
* Reject missing required or conflicting context.

Without this extension, no stable instance identifier is required.
Unvalidated instance claims MUST NOT be copied into issued tokens.

## IdP Access Token {#idp-access-token}

This short-lived, DPoP-bound token carries the IdP's canonical
Registered Agent identity. It is an exchange adapter or actor
credential, not the access token used at a downstream API. Acquisition
is specified in {{bootstrap}}.

An unexpired access token that this IdP issued under {{bootstrap}} to
the same client, Registered Agent, input method, and DPoP key MAY be
reused for exchange. No other access token is eligible; a matching
audience or a caller-supplied claim does not make one eligible. The
IdP MUST NOT require reacquisition of a token that remains
eligible.

The issued access token MUST conform to {{RFC9068}}, including its
JWT typing and required claims, with these profile-specific values:

| Claim | Required value |
|---|---|
| `iss` | IdP issuer identifier |
| `sub` | Resolved Registered Agent identifier |
| `client_id` | Authenticated logical client identifier |
| `aud` | IdP issuer identifier, identifying the exchange service |
| `sub_profile` | `ai_agent` under {{ENTITY-PROFILES}} |
| `cnf.jkt` | SHA-256 JWK thumbprint of the proven DPoP key under {{RFC7638}} |
| `iat`, `exp` | Issuance and expiration times; `0 < exp - iat <= 300` seconds |
| `jti` | Token identifier under {{RFC9068}} |

The IdP's token endpoint is the resource for this token. `resource` in
the request and `aud` in the token both name the IdP issuer identifier
under {{RFC8707}} and {{RFC9068}}, and the token is accepted only as
`subject_token` or `actor_token` at that endpoint.

The token MUST NOT contain `act`; it supplies the agent subject from
which exchange constructs an actor when needed. The IdP MUST associate
the token with its Federation Binding, input method, Source Tenant,
and exchange authorization through trusted issuance policy or token
state. Validated `client_instance` MAY be included under
{{instance-identification}}.

The input credential is valid at issuance; its remaining validity
does not bound the access token. Binding revocation takes effect at
the next acquisition or exchange once applied at the IdP.

# Requesting an Authorization Grant {#exchange}

The client MUST use {{RFC8693}} at the IdP token endpoint with its
evidence and client authentication under {{inputs}}. When an IdP access token
is presented, the logical client MUST match the one that obtained it.

The DPoP proof establishes the issued grant's binding key:

* Direct JWT input uses the credential and proof checks in {{inputs}}
  and {{direct-wag}}.
* For an IdP access token presented as `subject_token` or `actor_token`,
  the proof key MUST match its `cnf.jkt`.

These token-endpoint exchanges do not require `ath`; input-key checks
are defined here in addition to {{RFC9449}}.

The IdP SHOULD issue server-provided nonces under
{{RFC9449, Section 8}} for acquisition and exchange requests so that
proofs cannot be generated in advance; this is REQUIRED for the
platform JWT input under {{platform-jwt-input}}.

The client MUST include each of the following parameters exactly once:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` |
| `requested_token_type` | WAG under {{self-exchange}} or ID-JAG under {{delegated-exchange}} |
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
| WAG; platform JWT, ATTEST, or WIT-SVID | The JWT credential as `subject_token`, type `jwt` | Not required; preferred path |
| WAG; X.509-SVID | IdP access token as `subject_token`, type `access_token` | Required unless an eligible token is held |
| WAG; another supported input with an eligible IdP access token | IdP access token as `subject_token`, type `access_token` | Reuse the existing token |
| ID-JAG; any supported input | User credential as `subject_token`; IdP access token as `actor_token` | Required unless an eligible actor token is held; platform evidence requires separate client authentication |

The abbreviated token types in this table use the
`urn:ietf:params:oauth:token-type:` prefix.

## Self-Acting Agent {#self-exchange}

`requested_token_type` MUST be `urn:ietf:params:oauth:token-type:wag`.
The client MUST omit `actor_token` and `actor_token_type` and use one of the
subject inputs below. The issued WAG is specified in {{wag-profile}}
and its identifiers are registered in {{iana}}.

### Direct JWT Credential {#direct-wag}

`subject_token_type` MUST be `urn:ietf:params:oauth:token-type:jwt`.
The IdP MUST validate the `subject_token` under its configured input:

| Input | Presentation | Identity resolved by the IdP |
|---|---|---|
| Platform JWT | `subject_token` only; separate client authentication when required | Approved issuer and exact configured identity claims |
| Client Attestation | Same JWT in `subject_token` and `OAuth-Client-Attestation` | Approved `(iss, sub)` or shared-client `(iss, sub, agent_id)` binding |
| WIT-SVID | Same JWT in `subject_token` and `OAuth-Client-Attestation` | Approved trust domain and exact SPIFFE ID in `sub` |

For ATTEST and WIT-SVID, the IdP MUST reject a different JWT in
`subject_token` with `invalid_grant`, even if both JWTs identify the
same agent. The generic JWT token type MUST NOT select an input or
relax its validation requirements. Trusted configuration determines
credential type, issuer or trust-domain validation, identity mapping,
and required proofs under {{inputs}}. A direct input carrying `act`
MUST be rejected with `invalid_grant`; this path represents a
self-acting agent.

These checks establish subject evidence, not permission to obtain
WAG. The IdP MUST resolve the Registered Agent under {{identity}} and
apply {{idp-processing}} before issuance. The resulting WAG `sub` is
that Registered Agent's identifier. It MUST NOT be copied from an
external `sub`, `client_id`, or instance identifier merely because
that value was authenticated.

For a shared client, `agent_id` selects an approved binding without
granting authority. Optional instance context follows
{{instance-identification}}.

For ATTEST and WIT-SVID, the DPoP key MUST match the credential's
`cnf.jwk` under the selected input. Platform JWTs retain the bearer
credential and DPoP association rules in {{platform-jwt-input}}.
For ATTEST and WIT-SVID the same JWT also authenticates the client.
No additional credential issuance is required for any direct JWT input.

Example direct exchange using Client Attestation:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...attestation...
DPoP: eyJ...instance-proof...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=
  https%3A%2F%2Fplatform.example%2Fagents%2Fsupport-agent-7
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Awag
&subject_token=eyJ...attestation...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

### IdP Access Token {#wag-access-token}

Where supported under {{bootstrap}}, `subject_token` MAY instead be
an eligible IdP-issued access token, with
`subject_token_type=urn:ietf:params:oauth:token-type:access_token`.
The IdP MUST apply the token and current-authentication checks in
{{idp-processing}}. X.509-SVID uses this path because its TLS proof
supplies no JWT subject token. {{spiffe-flow}} shows the complete flow.

## Agent Acting for a User {#delegated-exchange}

`requested_token_type` MUST be
`urn:ietf:params:oauth:token-type:id-jag`. `actor_token` MUST be
the IdP-issued access token, with
`actor_token_type=urn:ietf:params:oauth:token-type:access_token`.
The IdP MUST apply Actor Profile's JWT access-token actor-input
processing. The token's `sub` identifies the Registered Agent;
its instance context does not supply `act.sub`. Acquisition under
{{bootstrap}} is required when no eligible actor token is available.
The direct JWT input in {{direct-wag}} applies only to self-acting
WAG; it does not change Actor Profile's actor-input rules.

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
DPoP: eyJ...instance-proof...

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
   client authentication under {{inputs}}. For direct WAG, validate
   the subject credential and resolve its binding under {{direct-wag}}.
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

3. **Validate instance context.** Apply {{instance-identification}}
   and reject inconsistent evidence.
4. **Authorize the target.** Check current agent status, authority
   trust, binding, assignment, and permitted output. Validate the
   RAS/resource association and determine a nonempty authorized subset
   of the requested scopes.
5. **Authorize delegation, for ID-JAG.** Validate the user credential
   under {{ID-JAG}}, including audience/client checks and scope
   ceilings. Resolve the user and downstream client, and verify the
   approval described below.
6. **Construct the grant.** Apply {{grant}} using the resolved
   principal and proven key, without expanding the authority above.

### Delegation Approval {#delegation-approval}

The IdP MUST validate an authenticated approval record or policy
decision binding all of the following:

* The issuer-qualified Registered Agent and user.
* The logical client, Source Tenant, and Target Tenant.
* The target RAS, resource, and permitted scopes.

On every issuance, the IdP MUST verify the approving user's or
administrator's authority and the approval's current validity and
revocation status. Missing or insufficient approval prevents issuance
under {{exchange-errors}}.

Approval MUST NOT be inferred from user sign-in or possession of both
credentials. A shared client MUST NOT reuse one agent's approval for
another. The approval interface and storage mechanism are outside
this profile.

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

### Workload Authorization Grant Issued by an IdP {#wag-profile}

{{WAG}} defines the grant concept, per-tenancy issuer model, Agent
Identifier, Agent Properties, and RFC 7523 redemption. This section
profiles issuance by an enterprise IdP through token exchange.

In addition to the common claims above, the WAG MUST have:

| Header or claim | Value |
|---|---|
| Protected-header `typ` | `oauth-wag+jwt` |
| `iss` | IdP issuer identifier for the Source Tenant |
| `sub` | Registered Agent identifier resolved under {{idp-processing}} |
| `sub_profile` | `ai_agent` under {{ENTITY-PROFILES}} |

The WAG MUST NOT contain `act`. Its token type is
`urn:ietf:params:oauth:token-type:wag` ({{iana}}). The `scope` and
`resource` claims use the definitions in {{ID-JAG}}. The single RAS
issuer audience selects one of WAG's accepted audience forms.

#### Tenant Issuers and Agent Identifiers

The IdP MUST use a distinct issuer identifier and distinct signing
keys per Source Tenant, and publish each issuer's keys through that
issuer's metadata. Tenant issuers MUST NOT share signing keys.

The RAS MUST:

* Select an allowlisted exact `iss` and validate only with keys
  authorized for that issuer.
* Retain the issuer association in key caches. Neither `kid` alone
  nor a union of tenant key sets can select a verification key.
* Interpret `sub` and `jti` within that issuer's namespace.
* Treat `sub` as an exact-match opaque string, including when the IdP
  uses WAG's recommended URI form under the tenant issuer.

The Agent Identifier is immutable and never reassigned. It is the
same Registered Agent identifier for direct JWT and IdP access-token
inputs.

#### Agent Properties and Provisioning

A WAG MAY carry Agent Properties from the Registered Agent record and
its memberships:

* `groups` and `roles` use {{RFC9068}} definitions and describe the
  agent's memberships.
* `name` uses the OpenID Connect definition {{OIDC}}. It MUST NOT
  serve as an authorization or attribution key.
* `namespace` and `ctx` are WAG placeholders pending registration.

The RAS MUST NOT require prior provisioning merely to accept a WAG
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
| `act.sub_profile` | `ai_agent` |
| `client_id` | Downstream client identifier |

Exactly one actor is introduced. Other required ID-JAG claims,
including applicable tenant context, follow ID-JAG. Translating the
client identifier MUST NOT rewrite the actor's namespace or substitute
a recipient-specific agent identifier. ID-JAG's issuer-identifier
audience rule applies instead of Actor Profile's generic
token-endpoint audience guidance.

### Instance Context in Grants {#grant-instance}

The IdP MAY include `client_instance` for downstream audit or risk
only after validating current evidence under {{instance-identification}}.
The object describes the subject's instance in WAG and the actor's
instance in ID-JAG.

The mapped form in {{INSTANCE}} is RECOMMENDED: `iss` identifies the
IdP, and `id` is an unambiguous IdP-assigned reference, preferably
scoped to the recipient. Pass-through context requires the recipient
trust configuration and validation defined by INSTANCE.

When issuing an access token, the RAS MUST preserve the context's
association with the subject or actor and validate or remap it under
INSTANCE. It MUST NOT copy an IdP-mapped context under a new token
issuer without an approved pass-through relationship or its own
unambiguous mapping. Recipients whose processing depends on lifecycle
granularity MUST establish it under INSTANCE.

### Example Grant Payloads

Example WAG payload:

~~~ json
{
  "iss": "https://idp.example/tenant/acme",
  "sub": "agent-42",
  "sub_profile": "ai_agent",
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

Example ID-JAG payload for the managed-device flow in {{device-flow}}:

~~~ json
{
  "iss": "https://idp.example/tenant/acme",
  "sub": "user-17",
  "act": {
    "iss": "https://idp.example/tenant/acme",
    "sub": "agent-17",
    "sub_profile": "ai_agent"
  },
  "client_id": "dev-agent-at-app",
  "aud": "https://as.app.example",
  "resource": "https://api.app.example",
  "scope": "tickets.read",
  "cnf": {
    "jkt": "Ak20Cf62SpTybasujYXbaI-Ms655MyvOZCtnnf8y1QU"
  },
  "client_instance": {
    "iss": "https://idp.example/tenant/acme",
    "id": "m-9584b70e0ac64fd8a903de0b586ec3a1"
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
| `issued_token_type` | Requested WAG or ID-JAG token type |
| `token_type` | `N_A`; the returned grant is not an API access token |
| `expires_in` | Remaining grant lifetime in seconds |
| `scope` | Approved scopes, matching the grant's `scope` |

The IdP MUST NOT issue a refresh token in this response.

The client MUST verify the returned token types and the grant's
protected-header `typ`, audience, resource, scope subset, and
`cnf.jkt` against its request and proven key. Missing or inconsistent
values cause failure. These checks do not replace cryptographic
validation at the RAS.

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

* X.509-SVID uses it as the WAG exchange subject.
* All delegated inputs use it as the ID-JAG actor credential.
* Other WAG inputs can use it when the deployment supports that path.

The IdP MUST NOT require acquisition before direct JWT-to-WAG exchange.
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
`resource` equal to the IdP issuer identifier and authentication under
{{inputs}}. Platform JWT input instead uses {{platform-acquisition}}.
The client credentials grant retains its confidential-client
requirement under {{RFC6749, Section 4.4}}. The example uses ATTEST
without optional instance identification.

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...attestation...
DPoP: eyJ...instance-proof...

grant_type=client_credentials
&client_id=
  https%3A%2F%2Fplatform.example%2Fagents%2Fsupport-agent-7
&resource=https%3A%2F%2Fidp.example%2Ftenant%2Facme
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
| `resource` | IdP issuer identifier |

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
follow {{ID-JAG}} for delegated access and {{wag-profile}} for
self-acting access. Delegated processing also follows Actor Profile,
including preservation of `act`.

## Redemption Request {#redemption-request}

The client MUST present a fresh DPoP proof and include each required
parameter exactly once:

| Parameter | Value |
|---|---|
| `grant_type` | `urn:ietf:params:oauth:grant-type:jwt-bearer` |
| `assertion` | WAG or ID-JAG |
| `resource` | Exact value of the grant's `resource` claim |
| `scope` | Optional subset of the grant's scopes; omission requests the grant's scopes |

Client authentication depends on the grant:

* **ID-JAG:** the client MUST authenticate using a credential registered
  or otherwise trusted for the grant's downstream `client_id`. The
  RAS MUST match that identifier to the authenticated client. An IdP
  client-ID mapping does not provision the downstream credential.
* **WAG:** the RAS MAY require client authentication by configuration,
  in addition to the DPoP proof.

DPoP possession alone MUST NOT satisfy a client authentication
requirement. {{ras-auth}} describes separate downstream credentials.

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

For WAG, the RAS MUST make any Agent Properties available to the
resource server's authorization decision and MUST NOT issue a refresh
token. ID-JAG refresh behavior follows {{delegated-lifecycle}}.
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

The same bound-grant error distinctions apply to WAG and ID-JAG.
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

Under {{ID-JAG}}, the RAS SHOULD NOT issue a refresh token by default.
A deployment enabling them applies the client and sender bindings,
refresh-token protection in {{RFC9700, Section 4.14}}, and current
RAS authorization policy. This is a separately configured lifecycle.
An ID-JAG itself remains single use under {{redemption-validation}}.

## Agent Record Correlation {#agent-correlation}

The canonical Registered Agent identity is the exact pair of IdP
issuer and agent identifier. For a WAG issued here, the pair is
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
or user membership to the agent. {{provisioning-example}} illustrates
this contract without defining new SCIM attributes.

# Metadata and Configuration {#metadata}

The IdP MUST advertise its implemented capabilities through existing
metadata under {{RFC8414}} and the referenced specifications:

| Capability | Metadata |
|---|---|
| Token exchange | `grant_types_supported` includes `urn:ietf:params:oauth:grant-type:token-exchange` |
| Client credentials acquisition, when supported | `grant_types_supported` includes `client_credentials` |
| Client authentication | `token_endpoint_auth_methods_supported` includes implemented methods, such as `attest_jwt_client_auth_dpop`, `spiffe_x509`, or `spiffe_wit` |
| DPoP | `dpop_signing_alg_values_supported` includes `ES256` under {{RFC9449}} |
| Grant outputs | `identity_chaining_requested_token_types_supported` lists supported WAG and/or ID-JAG token types under {{IDENTITY-CHAINING}} |
| Delegation, when supported | Actor Profile metadata for ID Token subject input, JWT access-token actor input, and `ai_agent` entity profile |

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

# Security and Privacy Considerations {#security}

The security requirements of {{RFC9700}}, {{RFC8693}}, {{RFC8725}},
and the selected input and output specifications apply to their
respective protocol roles. {{INSTANCE}} also applies when configured.

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
In particular, an IdP access token, WAG, ID-JAG, client assertion, or
platform JWT does not become another credential class merely because
it has a trusted signature. The intentional dual use of a Client
Attestation or WIT-SVID in {{direct-wag}} requires both sets of checks.

For JWTs accepted under this profile, validators MUST:

* Enforce signature algorithms and key sources authorized for the
  credential class and issuer or trust domain.
* Enforce `exp` and, when present, `nbf` under {{RFC7519}}.
* Reject `iat` later than the current time plus configured clock skew.
* Use at most 30 seconds of clock skew, without increasing a
  permitted `exp - iat` lifetime or a configured maximum age.

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
subjects under {{wag-profile}}.

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
client, tenant, key, and validated instance context to one request.
Independently valid evidence for different agents or identified
instances MUST NOT be combined.

Configured requirements for agent identity, key binding, or explicit
actors MUST NOT be bypassed by selecting an existing client-based
flow. A shared client alone does not authenticate the agent behind it.
Instance context does not authorize key rebinding or delegation.

## Platform Credential Theft

A platform JWT is a bearer credential. Theft before first use can let
an attacker establish the initial DPoP key association. Subsequent
key matching cannot prevent that race; audience restriction, bounded
age, and transport protection limit exposure.

The reuse association in {{platform-jwt-input}} prevents an already
used JWT from enrolling another key. Platforms MUST NOT share one
cached JWT among clients using independent DPoP keys. Platforms unable
to meet those prerequisites need another approved evidence path.

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

## Privacy and Correlation

Stable agent and instance identifiers permit correlation. The IdP
SHOULD release only necessary context and retain internal mappings
for recipient-scoped instance references. Raw attestation material
and private keys MUST NOT appear in grants or audit logs.

A canonical agent identifier is stable across RASes. For a per-user
agent, WAG `sub` or ID-JAG `act.sub` can therefore correlate the user
across services even when ID-JAG uses a pairwise user subject. The
IdP SHOULD NOT expose such a cross-context user pseudonym without a
correlation requirement at the receiving RASes.

This profile preserves the canonical agent identifier under
{{grant}}. Pairwise agent identifiers require an additional profile
coordinated with Actor Profile. Recipient-scoped instance context
is available under {{grant-instance}}.

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

## Media Type Registration

This section registers the `application/oauth-wag+jwt` media type
{{RFC2046}} in the "Media Types" registry in the manner described in
{{RFC6838}}, using the `+jwt` structured syntax suffix {{RFC8417}}.
It is used as the JOSE `typ` value `oauth-wag+jwt` under {{RFC8725}}
to indicate that the content is a Workload Authorization Grant
issued under {{wag-profile}}.

* Type name: application
* Subtype name: oauth-wag+jwt
* Required parameters: n/a
* Optional parameters: n/a
* Encoding considerations: binary; a JWT is a sequence of
  base64url-encoded values separated by period characters
* Security considerations: see {{security}} and {{RFC8725}}
* Interoperability considerations: n/a
* Published specification: this document
* Applications that use this media type: identity providers,
  resource authorization servers, and agent clients implementing
  this document
* Fragment identifier considerations: n/a
* Additional information:
  * Magic number(s): n/a
  * File extension(s): n/a
  * Macintosh file type code(s): n/a
* Person and email address to contact for further information:
  Karl McGuinness, public@karlmcguinness.com
* Intended usage: COMMON
* Restrictions on usage: none
* Author: Karl McGuinness
* Change controller: IETF
* Provisional registration? No

## OAuth URI Registration

This section registers `urn:ietf:params:oauth:token-type:wag` in the
"OAuth URI" subregistry of the "OAuth Parameters" registry.

* URN: urn:ietf:params:oauth:token-type:wag
* Common Name: Token type URI for a Workload Authorization Grant
* Change Controller: IETF
* Specification Document: This document

## Other Identifiers

`client_instance` is defined by {{INSTANCE}}; `act` follows
{{ACTOR-PROFILE}}; `ai_agent` is defined by {{ENTITY-PROFILES}}.
No new actor format, access-token type, or grant-profile URI is
registered.

--- back

# Deployment and Compatibility {#deployment}
{:numbered="false"}

This appendix is informative.

A deployment can adopt user-delegated ID-JAG first, adding Actor
Profile and this document's sender-binding and replay requirements
to its existing user federation. Self-acting WAG is a separate
capability: it requires issuer-based workload trust, new-subject
handling, bound grants, and the WAG definitions coordinated in
{{coordination}}. Supporting ID-JAG does not imply WAG support, and a
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
X.509-SVID and WIT-SVID authentication follow {{spiffe-input}} and
{{wit-input}}. Other credential types need explicit binding and proof
rules; support for one platform's tokens does not imply that every
token format is accepted. Direct WIT actor evidence under Actor
Profile is a different input path. It would need explicit
external-subject mapping and proof rules; it does not implicitly
substitute for the IdP access token here.

# End-to-End Deployment Examples {#flows}
{:numbered="false"}

This appendix is informative. A harness is the software executing
the agent and making OAuth requests. These examples separate its
hosting environment, authentication evidence, and acting relationship:

| Use case | Deployment | Evidence accepted by IdP | Identity model | Grant |
|---|---|---|---|---|
| Agent acting for itself | SPIFFE workload | X.509-SVID or WIT-SVID with their required proofs | Agent is the client | WAG |
| Agent acting for itself | Imported cloud or agent-platform agent | Platform-issued JWT and DPoP | Imported workload principal; no OAuth client required | WAG |
| Agent acting for itself | Managed platform | Platform Client Attestation and DPoP | Agents share a client | WAG |
| Agent acting for a user | Managed device | Enterprise Client Attestation and DPoP | Agent is the client | ID-JAG |
| Agent acting for a user | Managed platform | Platform Client Attestation and DPoP | Agents share a client | ID-JAG |
| Agent acting for a user | Imported cloud or agent-platform agent | Platform JWT, separate client credential, user credential, and DPoP | Imported agent with an authorized OAuth client | ID-JAG |

In each example, the IdP maintains the agent's status, owner, groups,
and application assignments. Before issuance, it establishes the
external identity binding and trusts the relevant credential issuer.
The RAS trusts the IdP at `https://idp.example/tenant/acme` as grant
issuer. Administrative configuration, JIT, or SCIM can establish
the downstream agent record, correlated by IdP issuer and agent
identifier. Receiving a grant does not by itself provision a record
or authorize every scope.

The examples request `tickets.read` at `https://api.app.example`
through the RAS `https://as.app.example`. Each harness controls its
own key, denoted `K`; `JKT(K)` denotes its thumbprint. JWKs sent to
attesters contain only public keys. IdP requests use the evidence and
any client authentication described in each example, with fresh proofs
for the respective endpoints. The illustrated RAS
issues DPoP access tokens bound to that key, satisfying the
sender-constraint requirement in {{consumption}}.

## Agent Acting for Itself {#self-flow}
{:numbered="false"}

The agent is the WAG subject; the flow ends with a
sender-constrained access token for the agent alone. JWT credentials
use direct exchange under {{direct-wag}}. The X.509-SVID example
first illustrates the adapter needed when no JWT credential is
available; the subsequent variants omit that acquisition step.

Direct JWT path:

~~~
 Platform          Harness             IdP          RAS         API
     |-- JWT -------->|                 |            |           |
     |                |-- JWT + proof ->|            |           |
     |                |<----- WAG ------|            |           |
     |                |-------- WAG + DPoP --------->|           |
     |                |<--------- app AT ------------|           |
     |                |-------------- app AT + DPoP ------------>|
~~~

### SPIFFE Workload with X.509-SVID {#spiffe-flow}
{:numbered="false"}

Use this model when the workload already has a SPIFFE identity
representing the agent. This example uses X.509-SVID client
authentication under {{spiffe-input}}, without a Client Attestation
or stable instance identifier. X.509-SVID uses {{bootstrap}} because
the TLS credential is not a JWT subject token. The WAG is specified
in {{wag-profile}}.

~~~
 Workload           Harness            IdP          RAS         API
    API
     |                 |                |            |           |
     |<-- get SVID ----|                |            |           |
     |-- X.509-SVID -->|                |            |           |
     |                 |- credentials ->|            |           |
     |                 |<--- IdP AT ----|            |           |
     |                 |--- exchange -->|            |           |
     |                 |<---- WAG ------|            |           |
     |                 |-------- WAG + DPoP -------->|           |
     |                 |<--------- app AT -----------|           |
     |                 |------------- app AT + DPoP ------------>|
     |                 |<--------------- tickets ----------------|
~~~

1. The harness obtains an X.509-SVID for
   `spiffe://workloads.example/agents/support` from its Workload API.
   The IdP has approved that exact identity and trust domain for
   Registered Agent `agent-42`; trusting the domain alone does not
   admit every workload as that agent.
2. The harness sends a client credentials request to the IdP over
   mutually authenticated TLS, with that SPIFFE ID as `client_id`
   and the IdP issuer as `resource`. A DPoP proof establishes a
   separate application key `K`. The IdP validates the SVID using
   the configured SPIFFE trust bundle and resolves the agent binding.
3. Under {{idp-access-token}}, the IdP issues an access token with `sub=agent-42`, the SPIFFE ID as `client_id`, its own
   issuer as `aud`, and `cnf.jkt=JKT(K)`. The TLS credential
   authenticates the workload; `K` binds the issued token.
4. The harness requests WAG using that access token as
   `subject_token`, the target RAS as `audience`, and the API and
   scope above. It again authenticates with its SVID and proves
   possession of `K`. The IdP checks the current binding and policy
   before issuing WAG with `sub=agent-42` and no `act`.
5. The harness redeems WAG at the RAS with a fresh proof from `K`,
   receives the application access token, and calls the API. The
   downstream processing is described in {{app-consumption}}.

The illustrative bootstrap request is sent over the mutually
authenticated TLS connection established with the X.509-SVID:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...workload-key-proof...

grant_type=client_credentials
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&resource=https%3A%2F%2Fidp.example%2Ftenant%2Facme
~~~

The harness then sends this exchange over mutually authenticated TLS,
using the same SPIFFE identity and DPoP key:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...workload-key-proof...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Awag
&subject_token=eyJ...agent-access-token...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The resulting WAG payload appears in {{grant}}. The harness redeems
it at the RAS:

~~~ http
POST /token HTTP/1.1
Host: as.app.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...grant-key-proof...

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&assertion=eyJ...idp-wag...
&resource=https%3A%2F%2Fapi.app.example
~~~

~~~ json
{
  "access_token": "eyJ...app-access-token...",
  "token_type": "DPoP",
  "expires_in": 600,
  "scope": "tickets.read"
}
~~~

The RAS validates `typ`, resolves the IdP's key by `iss` through its
allowlist, checks `aud`, lifetime, and `jti`, matches `resource` to
the grant, and compares the DPoP proof key to `cnf.jkt` under
{{consumption}}.

It accepts `agent-42` even if it has not seen that
subject before, applies any Agent Properties and its provisioned
record under {{agent-correlation}}, and issues a DPoP-bound access
token with no refresh token. No client authentication is required
for this redemption.

A SPIFFE workload can have several instances {{SPIFFE-CONCEPTS}}.
This flow correlates key possession through `cnf.jkt`; it does not
claim a stable runtime identity. A renewed SVID can be used with an
existing eligible token when the approved SPIFFE binding and DPoP
key remain the same. An unrelated identity or replacement DPoP key
cannot use that token.

### WIT-SVID Variant
{:numbered="false"}

With {{wit-input}} configured, the harness instead obtains a WIT-SVID
for the same SPIFFE ID, binding key `K`. The following decoded payload
omits the optional `iss`; the IdP uses the configured trust anchors
for `workloads.example`. Its protected header uses `typ=wit+jwt`,
`alg=ES256`, and a `kid` selecting a key in that trusted bundle.

~~~ json
{
  "sub": "spiffe://workloads.example/agents/support",
  "iat": 1789128000,
  "exp": 1789131600,
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "alg": "ES256",
      "x": "VcKVNBZ4IaBAYW3jxM4w3TJFVA7myeUGQyGt-g_yvpQ",
      "y": "f-E-hYE3TAWKwhVv9pej9NABs9SX9XsNO80x57jFTyU"
    }
  }
}
~~~

The harness sends this request over server-authenticated TLS. The
Client Attestation PoP JWT has `aud=https://idp.example/tenant/acme`,
a fresh `iat` and unique `jti`, and the IdP's challenge if supplied.
It uses `typ=oauth-client-attestation-pop+jwt`. Both that proof and
the DPoP proof are signed with `K` using `ES256`.

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...wit-svid...
OAuth-Client-Attestation-PoP: eyJ...attestation-pop...
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Awag
&subject_token=eyJ...wit-svid...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The same WIT-SVID appears in the header and `subject_token`. The IdP
validates it and both proofs, resolves `agent-42`, checks assignments,
and returns WAG with `sub=agent-42` and `cnf.jkt=JKT(K)`. No IdP access
token is acquired. The extra JWK `alg` member does not change the
RFC 7638 thumbprint. The harness redeems WAG and calls the API as
shown above. For user-delegated access, it instead obtains or reuses
an IdP actor token under {{bootstrap}} and {{delegated-exchange}}.

### Platform-Issued JWT Variant {#platform-jwt-flow}
{:numbered="false"}

Use this model when the IdP imports an agent from a cloud or agent
platform. The following binding uses a shared platform subject plus
an agent identifier and tenant restriction.

Its exact selectors are
`iss=https://agents.cloud.example/tenant/acme`,
`sub=agent-service`, `platform_agent=support-agent-7`, and
`tenant=acme`. Together they identify Registered Agent `agent-42`;
no OAuth client is needed for this self-acting exchange. The issuer
is configured as a dedicated workload credential issuer. The
platform-specific claims are illustrative, not new claim registrations.
Decoded platform JWT:

~~~ json
{
  "iss": "https://agents.cloud.example/tenant/acme",
  "sub": "agent-service",
  "platform_agent": "support-agent-7",
  "tenant": "acme",
  "aud": "https://idp.example/tenant/acme",
  "iat": 1789128000,
  "exp": 1789128600,
  "jti": "plat-4d1e"
}
~~~

The harness generates `K` and presents the JWT only as subject
evidence, with a DPoP proof containing the IdP's nonce:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Awag
&subject_token=eyJ...platform-jwt...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The IdP validates the signature with the configured issuer's keys,
matches every selector, and checks `agent-42`'s assignments. It issues
WAG directly with `sub=agent-42` and `cnf.jkt=JKT(K)`. The harness
redeems WAG at the RAS and calls the API as above. Subsequent WAG
requests can reuse the platform JWT within its permitted age and
lifetime with fresh proofs from `K` under {{platform-jwt-input}}.
The platform never sees `K`; DPoP binds the grant but does not prove
an independently registered OAuth client identity.

For a platform that already names the individual agent in `sub`,
the binding can instead use only its issuer and that exact `sub`.
Multiple approved bindings can resolve to the same Registered Agent
without forcing platforms to share an OAuth client namespace.

### Shared Client in a Managed Platform {#platform-flow}
{:numbered="false"}

Use this model when a hosting platform runs separately governed
agents through one OAuth client. The IdP approves the platform
attester `https://attester.example/tenant/acme` for shared client
`https://platform.example/oauth-client`, mapping its
`agent_id=support-agent-7` to Registered Agent `agent-42`.

The platform attester supplies the Client Attestation. The harness
exchanges it directly for WAG, without an intermediate IdP access token.

1. The control plane launches `support-agent-7`. Its harness generates
   `K`. The attester verifies the launch assignment, runtime
   isolation, and key possession, then issues an attestation with
   `sub` equal to the shared client, `agent_id=support-agent-7`,
   `client_instance_id=i-bc6701a8d32549ef80e143fd267b95ca`, and `cnf.jwk` containing the public
   key. This deployment opts into execution-level instance tracking.
   The harness cannot select another agent merely by naming it.
2. The harness follows {{direct-wag}}, sending the shared `client_id`
   and the same attestation in `OAuth-Client-Attestation` and
   `subject_token`, with a DPoP proof from `K`. The IdP resolves
   `(iss, sub, agent_id)` to `agent-42`, validates instance context,
   and authorizes the requested access using the agent's assignments.
3. The IdP returns WAG with `sub=agent-42`, no `act`, validated
   instance context, and `cnf.jkt=JKT(K)`. The harness redeems it
   and calls the API as described in {{app-consumption}}.

A second runtime for this agent gets a different instance identifier
and key, but the same `agent-42` principal. A different agent behind
the shared client has its own binding and permissions. The IdP
does not infer equivalent authority from the common client identity.

## Agent Acting on Behalf of a User {#delegated-flow}
{:numbered="false"}

The user is the ID-JAG subject and the Registered Agent its actor;
the flow ends with a sender-constrained access token that carries
both.

### Harness on a Managed Device {#device-flow}
{:numbered="false"}

Use this model when an enterprise governs a desktop agent as a
Registered Agent with its own client identity. The example binds
`client_id=https://desktop.example/agents/dev-17` to `agent-17`.
The IdP trusts `https://devices.example/attester` to attest this client.
The managed device, the agent, and the running harness are different
entities; device enrollment does not itself authorize user delegation.

~~~
Enterprise         Harness      User/browser     IdP      RAS     API
attester
    |                 |               |           |        |       |
    |                 |--- sign-in -->|           |        |       |
    |                 |               |- sign-in >|        |       |
    |                 |               |<- code ---|        |       |
    |                 |<--- code -----|           |        |       |
    |< evidence, JWK -|               |           |        |       |
    |-- attestation ->|               |           |        |       |
    |                 |------- code + PKCE ------>|        |       |
    |                 |<------- ID Token ---------|        |       |
    |                 |-- credentials + ATTEST -->|        |       |
    |                 |<-------- IdP AT ----------|        |       |
    |                 |-- user + actor exchange ->|        |       |
    |                 |<-------- ID-JAG ----------|        |       |
    |                 |---------- ID-JAG + DPoP ---------->|       |
    |                 |<------------- app AT --------------|       |
    |                 |-------------- app AT + DPoP -------------->|
    |                 |<---------------- tickets ------------------|
~~~

1. The harness generates `K` and starts sign-in in an external
   browser using an authorization code flow with PKCE under
   {{RFC8252}}. The enterprise records user or administrator approval
   for this agent to read tickets for that user. Sign-in alone is
   not delegation approval.
2. After the browser returns the code, the enterprise attester
   validates device evidence, harness and agent assignment, and key
   possession. This deployment opts into installation-level instance
   identification. The Client Attestation contains:

   * The agent's client identifier as `sub`, without `agent_id`.
   * `client_instance_id=i-64b89d23c05a4e1f9a76bd2381d0e547`.
   * `cnf.jwk` containing `K`'s public key.

   The harness redeems the code with PKCE and fresh ATTEST
   authentication to obtain its user ID Token. Device evidence and
   issuance APIs remain deployment-specific under {{ATTEST}}.
3. The harness then obtains its IdP access token under {{bootstrap}},
   identifying `agent-17`, the client, optional installation context,
   and `JKT(K)`, or reuses an eligible token. Acquisition follows the
   interactive wait so the short token lifetime is available for
   exchange. If credentials expire before exchange, the harness
   renews the required evidence and token; it does not bypass checks.
4. The harness follows {{delegated-exchange}}, sending the user
   ID Token as `subject_token` and the IdP access token as
   `actor_token`, with fresh ATTEST authentication. The IdP validates
   both identities and the delegation, then issues ID-JAG with
   `sub=user-17`, `act={iss: IdP, sub: agent-17, sub_profile: ai_agent}`,
   and the downstream client identifier `dev-agent-at-app`.
5. The harness redeems ID-JAG and accesses the API as described in
   {{app-consumption}}, authenticating as `dev-agent-at-app` with
   the separate RAS credential described in {{ras-auth}}. The device
   attester and device record do not become actors.

The redemption request appears in {{ras-auth}} and the response has
the shape shown above, with `sub=user-17` and `act.sub=agent-17` in
the resulting access token.

If the enterprise only needs existing client-based delegation, the
harness can use the ID-JAG/EMA path in {{deployment}} without the
agent bootstrap and actor token. A desktop harness shared by several
separately governed agents instead uses the shared-client binding
illustrated in {{platform-flow}}. Device hosting does not select
the identity model automatically.

### Shared Client Variant
{:numbered="false"}

For user-delegated work in the shared-client platform deployment of
{{platform-flow}}, the harness obtains or reuses an IdP access token
under {{bootstrap}}, then follows {{delegated-exchange}} with an
accepted user credential and that actor token. After checking
delegation approval, the IdP issues ID-JAG with the user as `sub` and
`agent-42` as `act`. Its downstream `client_id` is `platform-at-app`;
redemption uses the platform signing service in {{ras-auth}}. The
hosting platform is client context, not an additional actor.

### Imported Platform Agent Acting for a User {#platform-delegated-flow}
{:numbered="false"}

The binding in {{platform-jwt-flow}} also permits the IdP-assigned OAuth client
`agent-harness-23` to act as `agent-42`. The harness separately
provisions a client credential, here `private_key_jwt` using key `C`
registered with the IdP. The platform JWT does not authenticate that
client. A platform unable to supply a client credential can use the
self-acting path but cannot use this delegated path by itself.

1. The harness obtains the platform JWT above and generates or retains
   `K`. It authenticates `agent-harness-23` with a client assertion
   signed by `C` and exchanges the platform JWT for an IdP access
   token under {{platform-acquisition}}. The IdP verifies both the
   agent binding and that this client is permitted to use it.
2. The returned token has `sub=agent-42`, `client_id=agent-harness-23`,
   the IdP issuer as `aud`, and `cnf.jkt=JKT(K)`. It records the platform
   input and binding. Its lifetime is at most 300 seconds.
3. The harness obtains a user credential for `user-17`, issued to
   `agent-harness-23`, and an applicable user or administrator approval
   for this agent, client, resource, and scope. It requests ID-JAG
   with the user credential as subject and the IdP token as actor,
   authenticating the same client and proving `K` again. No platform
   JWT is included in this request.
4. The IdP checks the token, current platform binding, permitted client,
   user credential, and approval. It issues ID-JAG with `sub=user-17`,
   `act.sub=agent-42`, and the configured downstream
   `client_id=platform-at-app`. The harness redeems it using that
   client's separate downstream credential and proof from `K`, as
   described in {{ras-auth}}, then uses the application token at the API.

The acquisition request is:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=agent-harness-23
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...idp-client-assertion-C...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&subject_token=eyJ...platform-jwt...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&resource=https%3A%2F%2Fidp.example%2Ftenant%2Facme
~~~

The client assertion has `iss` and `sub` equal to `agent-harness-23`,
an audience accepted by the IdP for client authentication, short
expiration, and a unique `jti`. It is signed by `C`, independently
of the platform JWT and the DPoP key `K`. The DPoP proof includes
an IdP nonce. The response is:

~~~ json
{
  "access_token": "eyJ...platform-agent-access-token...",
  "issued_token_type":
    "urn:ietf:params:oauth:token-type:access_token",
  "token_type": "DPoP",
  "expires_in": 300
}
~~~

Using that token, the delegated request is:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...fresh-proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=agent-harness-23
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...fresh-idp-client-assertion-C...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid-jag
&subject_token=eyJ...user-id-token-for-agent-harness-23...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid_token
&actor_token=eyJ...platform-agent-access-token...
&actor_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The IdP binds the user's credential to the authenticated client,
and the actor token to that same client and `K`. The platform JWT's
`sub` remains `agent-service`; the OAuth client is `agent-harness-23`;
the governed actor is `agent-42`. None of these identifiers substitutes
for the other two. Renewal follows {{delegated-lifecycle}}.

## Client Authentication at the RAS {#ras-auth}
{:numbered="false"}

These examples separate the DPoP key `K` from a registered client
signing key `C`. Before delegated access, the RAS has registered
`C`'s public key for the following client; the IdP knows the client-ID
mapping. This is client credential provisioning, independent of the
agent record and of trust in the IdP as grant issuer.

| Deployment | Downstream client | Custody of client signing key C |
|---|---|---|
| Managed device | `dev-agent-at-app` | Protected storage for this managed installation; its public key is enrolled at the RAS |
| Managed platform | `platform-at-app` | Platform signing service; an authorized harness obtains a short-lived assertion without receiving the private key |

At redemption, the harness supplies a fresh `private_key_jwt`
assertion signed with `C`. Its `iss` and `sub` equal the downstream
client identifier, its `aud` is the RAS issuer, and it has a short
expiration and unique `jti`, validated under {{RFC7523}}. A separate
DPoP proof from `K` proves possession of the grant's binding key.
Neither credential substitutes for the other.

The self-acting WAG
example redeems the bound grant with a DPoP proof and no client
authentication, as {{consumption}} permits for WAG.

Illustrative desktop redemption; the client assertion and ID-JAG
are different JWTs with different purposes and signing authorities:

~~~ http
POST /token HTTP/1.1
Host: as.app.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...grant-key-proof...

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&assertion=eyJ...idp-id-jag...
&resource=https%3A%2F%2Fapi.app.example
&client_id=dev-agent-at-app
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...client-key-assertion...
~~~

The RAS uses its client registration to validate the client assertion
and its IdP trust to validate ID-JAG. It does not need to accept the
enterprise or platform attester as an agent-identity authority.
If a deployment instead authenticates the client with ATTEST at the
RAS, it needs a separate, explicit RAS attester trust configuration;
trust in the IdP's grant does not create that relationship.

## Downstream Application Processing {#app-consumption}
{:numbered="false"}

Both use cases finish at the same application trust boundary:

1. The harness presents the IdP-issued grant to the RAS using the
   selected grant's redemption procedure and the client authentication
   in {{ras-auth}}, including ID-JAG's downstream client binding.
   Its DPoP proof uses the key named by the grant's `cnf.jkt`.
2. The RAS validates the trusted IdP signature, issuer, audience,
   lifetime, replay state, target resource, scopes, and key proof.
   It resolves the subject and any actor, applies local assignments,
   and issues an API access token. In these examples it retains
   the IdP's principal identifiers and uses a JWT access token.
3. The API receives only its access token and a fresh DPoP proof,
   including the access-token hash under {{RFC9449}}. It validates
   the token and proof, then evaluates resource policy for the agent
   or the user and agent actor. It does not consume the upstream
   SVID, device evidence, Client Attestation, WAG, or ID-JAG.

| Example | Application access-token identity | Key binding |
|---|---|---|
| SPIFFE workload, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Imported platform agent, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Imported platform agent, delegated | User `sub`, `act.sub=agent-42` | `cnf.jkt=JKT(K)` |
| Managed device, delegated | `sub=user-17`, `act.sub=agent-17` | `cnf.jkt=JKT(K)` |
| Managed platform, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Managed platform, delegated variant | User `sub`, `act.sub=agent-42` | `cnf.jkt=JKT(K)` |

For delegated tokens, the actor also retains its IdP `iss` and
`sub_profile=ai_agent` under Actor Profile. The RAS is the access-token
issuer and the API is its audience. Groups and owner relationships
can come from provisioned records or approved claims; user groups
do not supply an agent actor's memberships. Optional instance context
supports audit and risk without changing those principal identities.

## One Agent Record for Self-Acting and Delegated Access {#provisioning-example}
{:numbered="false"}

The RAS has an authenticated SCIM provisioning relationship with
IdP issuer `https://idp.example/tenant/acme`. The IdP provisions the
following Agent resource using {{SCIM-AGENT}}. The RAS assigns `id`;
the IdP supplies `externalId`. The issuer association is kept with
the provisioning relationship, not encoded in a new SCIM attribute.

~~~ json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Agent"],
  "id": "ra-42",
  "externalId": "agent-42",
  "agentUserName": "support-agent",
  "displayName": "Support Agent",
  "active": true
}
~~~

The application's directory records `ra-42` as a member of group
`support-eng`; its local policy grants that group `tickets.read`.
This is a provisioned group relationship, not a claim inferred from
the agent name or a new group schema. Both grant paths resolve the
same record under {{agent-correlation}}:

| Validated grant | Agent lookup | Record and policy input |
|---|---|---|
| WAG: `iss=https://idp.example/tenant/acme`, `sub=agent-42` | `(iss, sub)` | `ra-42`, member of `support-eng` |
| ID-JAG: `sub=user-17`, `act.iss=https://idp.example/tenant/acme`, `act.sub=agent-42` | `(act.iss, act.sub)` | The same `ra-42` and membership |

For delegated access, the application also evaluates `user-17`'s
permissions and the authorized delegation. The agent's group does
not add that user to the group. An equal `agent-42` from another
issuer does not match this record. Setting `active=false` blocks new
issuance once applied by the relevant server; already-issued tokens
follow the deployment's expiration and revocation behavior.

# Interoperability Test Cases
{:numbered="false"}

This appendix is informative; the normative requirements are in the
body. Independent platform, client, IdP, and RAS implementations can
exercise:

## Identity and Input Selection
{:numbered="false"}

| Case | Expected result |
|---|---|
| Shared client omits `agent_id` | Reject; no fallback to client-only binding |
| Missing, ambiguous, or disabled binding | Reject issuance |
| Unexpired token from this document's acquisition; same client, agent, input method, and key | Reused without reacquisition |
| Direct JWT input contains `act` | `invalid_grant`; no conversion from delegation to self-acting access |
| Same registered agent through direct WAG and the access-token adapter | Same WAG `sub` and issuer namespace |
| Direct WAG with shared-client ATTEST; approved `(iss, sub, agent_id)` and key proof | WAG subject is the Registered Agent, not the shared client |
| Agent with its own client identity supplies `agent_id` | Reject; no switch to the shared-client model |
| Access token from any other issuance, even with a matching audience | Not eligible as an IdP access-token input; use direct WAG or acquire an eligible token |

## Platform JWT Evidence
{:numbered="false"}

| Case | Expected result |
|---|---|
| Platform JWT with no valid IdP-provided DPoP nonce | `use_dpop_nonce`; no grant issued |
| Platform JWT outside the configured credential class or older than the bounded age | Reject input |
| Direct WAG with platform JWT; approved issuer and exact selectors, nonce and DPoP proof; no client authentication required by the binding | WAG for the bound agent without acquisition or `client_id` |
| Platform-issued JWT with an unapproved issuer, wrong audience, or expired | Reject subject evidence with `invalid_grant` |
| Platform JWT with an unbound subject, missing additional selector, or wrong exact claim value | `invalid_grant`; no prefix, wildcard, or partial match |
| Shared platform subject plus exact agent and tenant claims matches one approved binding | Resolve that Registered Agent independently of OAuth `client_id` |
| Platform JWT presented as `client_assertion` without independent client authentication | Does not authenticate the OAuth client |
| Platform acquisition with a valid JWT but no separate client authentication, or an unauthorized client | Reject; workload evidence alone cannot obtain the actor credential |
| Platform acquisition requests an audience, scope, or actor | `invalid_request` |
| Platform-origin actor token used with another authenticated client or DPoP key | `invalid_grant` |
| Platform-origin actor token, same permitted client and key, current binding, valid user and approval; no platform JWT resent | Issue ID-JAG |
| Platform JWT with missing or mistyped `iat`, invalid time ordering, excessive age or lifetime, or future `iat` beyond clock skew | `invalid_grant` |
| Cached platform JWT reused with the same binding and key, all other checks valid | Accept with fresh DPoP proof |
| Previously used platform JWT presented with another key, including a different signature over the same signing input | `invalid_grant`; no new key association |

## SPIFFE and Credential Renewal
{:numbered="false"}

| Case | Expected result |
|---|---|
| X.509-SVID client with approved exact ID and DPoP proof | IdP access token without stable instance context |
| Direct WAG with WIT-SVID; approved exact ID, attestation PoP, matching DPoP key; no `iss` | WAG for the configured agent without acquisition |
| WIT-SVID with missing attestation PoP, mismatched key or proof algorithm, or expired credential | Reject authentication or proof |
| WIT-SVID with unapproved trust domain or mismatched `client_id` | Reject; `iss` cannot select another trust anchor |
| Renewed X.509-SVID, same binding and DPoP key | Existing eligible token remains usable |
| Renewed WIT-SVID, same binding and unchanged `cnf.jwk` | Existing eligible token remains usable |
| Renewed WIT-SVID with a new `cnf.jwk` | Reject exchange with the old token; new IdP access token required |
| Direct WAG using a renewed WIT-SVID and proofs from its new key | WAG bound to the new key; no IdP access token required |
| Direct ATTEST or WIT-SVID subject differs from the authentication JWT, even for the same identity | `invalid_grant` |
| X.509-SVID request omits `subject_token` | `invalid_request`; use the access-token adapter |

## Delegation and Instance Context
{:numbered="false"}

| Case | Expected result |
|---|---|
| Direct WAG with ATTEST agent as client; approved binding and proof, instance extension disabled | WAG for the Registered Agent, without acquisition or stable instance context |
| Valid client and user credentials, with absent, revoked, or expired approval | Same non-enumerating `actor_unauthorized` response |
| Valid user and agent credentials without delegation | `actor_unauthorized` |
| Instance context names an unconfigured authority | Reject context; no required-context fallback |
| Direct external credential supplied as ID-JAG `actor_token` | Reject; this delegated path requires the IdP-issued actor token |
| Same agent in a second execution | Same agent subject; distinct context if execution tracking is configured |
| Unrelated client, agent, instance, or key at exchange | Reject inconsistent evidence |
| Agent acting for itself | WAG subject is the agent; no `act` |
| Agent acting for a user | User subject; Registered Agent `act` |
| Optional downstream instance context | Same principal and binding semantics |
| Configured instance extension, missing or mismatched evidence | Reject; no fallback to key-only processing |

## Grant Validation and Redemption
{:numbered="false"}

| Case | Expected result |
|---|---|
| Grant with tenant B `iss` signed by tenant A's key, including colliding `kid` | Reject; key lookup is scoped to exact issuer |
| Grant redemption with missing proof or mismatched key | `invalid_grant` |
| JWT with a future `nbf` outside allowed skew | Reject as not yet valid |
| Redemption without `resource`, or with `resource` not matching the grant | `invalid_target` |
| Replayed grant with a valid DPoP proof | `invalid_grant`; grants are single use |
| ID-JAG redemption with DPoP but no required client authentication | Reject; DPoP is not the registered client credential |
| Valid grant for one RAS also lists another audience | Reject; exactly one RAS issuer is allowed |
| Replayed grant during allowed expiration skew | Reject; consumed identifiers remain recorded through `exp` plus skew |
| Unsupported requested output | `invalid_request`; no fallback |
| Presented redemption proof has an invalid signature, wrong endpoint/method, or stale timestamp | `invalid_dpop_proof` |
| Redemption proof lacks a required RAS nonce | `use_dpop_nonce` with `DPoP-Nonce`; grant remains unconsumed |
| Concurrent redemption of one grant at two RAS replicas | At most one access token issued |
| Repeated `audience`, `resource`, or other request parameter | `invalid_request` |

## Status and Record Correlation
{:numbered="false"}

| Case | Expected result |
|---|---|
| WAG subject and ID-JAG actor name the same IdP agent | Resolve the same provisioned record |
| Platform-origin actor token used after its recorded binding is disabled | Reject even though the token is unexpired |
| WAG with a previously unseen `sub` under an allowlisted `iss` | Accept subject; issue only if RAS policy authorizes access; record-dependent authorization requires correlation |
| Authenticated disabled-agent status reaches the RAS | Block subsequent issuance and refresh; revoke or deactivate affected tokens as supported |
| Canonical agent identifier in the IdP access token | Same value in WAG `sub` and ID-JAG `act.sub`; no recipient-specific substitution |
| Same bare agent identifier from another issuer | No match to the original issuer's record |

Only cases for the implemented input and output are applicable.
Existing client-based deployments are compatibility context, not an additional
conformance path for this specification.

# Coordination with Related Work {#coordination}
{:numbered="false"}

*RFC EDITOR: Remove this section before publication.*

## WAG Gaps Filled by This Document {#wag-gaps}
{:numbered="false"}

This appendix is informative. WAG-00 leaves IdP issuance through
exchange open. The definitions below allow this profile to be
implemented while related drafts are coordinated. Once WAG adopts
an item, this document can reference that definition.

| Item | Definition in this profile | Coordination needed |
|---|---|---|
| Token type | `urn:ietf:params:oauth:token-type:wag` | Common identifier for RFC 8693 request and response; move registration to WAG |
| JWT type | `oauth-wag+jwt` | Explicit typing to distinguish WAG from other JWTs; move media type registration to WAG |
| Sender constraint | `cnf.jkt`, DPoP proof, and key match at redemption | Resolve WAG's open possession requirement using ID-JAG's bound-grant procedure |
| Authorization claims | Required `scope` and `resource`, using ID-JAG definitions | Add claims to WAG so the RAS can enforce the grant's authorization ceiling |
| Redemption errors | {{redemption-errors}} | Align grant, proof, nonce, resource, and scope failures across both outputs |
| Replay prevention | Atomic single use of `(iss, jti)` through expiration plus skew | Define consistent grant consumption regardless of issuer |
| Acting relationship | WAG excludes `act` | Reserve WAG for self-acting access |
| IdP issuance | Tenant-specific IdP issuer and canonical Registered Agent `sub` | Acknowledge IdP placement in WAG; retain identity-resolution mechanics here |

Further agreement is needed on:

* The single issuer-identifier audience, already accepted by WAG.
* Agent Properties registrations, including the RFC 9068 and OpenID
  Connect definitions for `groups`, `roles`, and `name`.
* WAG's Informational status as a normative dependency of this
  standards-track profile.
* Advertising WAG through
  `identity_chaining_requested_token_types_supported`.

## Other Coordination Items
{:numbered="false"}

The following items remain open:

* **Actor identifiers:** pairwise agent identifiers need an Actor
  Profile extension. This document preserves the actor token's `sub`.
* **Grant audience:** ID-JAG's RAS issuer audience takes precedence
  over Actor Profile's generic token-endpoint guidance; that precedence
  needs agreement in Actor Profile.
* **Redemption grant type:** ID-JAG and WAG's normative text uses
  `jwt-bearer`, while ID-JAG's bound-grant example and {{JWT-DPOP}}
  use `jwt-dpop`. This document follows the normative `jwt-bearer`
  text with DPoP and will follow ID-JAG if it adopts `jwt-dpop`.
* **SPIFFE and ATTEST:** `spiffe_wit` currently uses a separate Client
  Attestation PoP JWT plus DPoP with the same key. Its metadata needs
  alignment with ATTEST's evolving proof modes. General WIT actor
  inputs need separate mapping and trust-domain rules when `iss` is
  absent.
* **Document relationship:** this draft and
  draft-mcguinness-oauth-client-instance-identification are intended
  to replace draft-mcguinness-oauth-ai-agent-instance. The separate
  draft-mcguinness-oauth-client-instance-assertion proposal carries
  a standalone assertion alongside other authentication methods.

# Document History
{:numbered="false"}

*RFC EDITOR: Remove this section before publication.*

* Defined platform-to-IdP agent binding and both self-acting WAG and
  user-delegated ID-JAG issuance.
* Added ATTEST, SPIFFE X.509-SVID, WIT-SVID, and imported platform JWT
  inputs, with optional instance identification.
* Distinguished an agent's own OAuth client from a shared client;
  limited ATTEST `agent_id` to the shared-client model.
* Made direct JWT exchange the preferred WAG path. Retained IdP access
  tokens for X.509-SVID and canonical Actor Profile input for ID-JAG.
* Separated platform workload evidence from client authentication;
  defined exact identity selectors, registry import, bounded age, and
  cached-JWT reuse with the first proven DPoP key.
* Profiled WAG token type, JWT type, claims, tenant issuers, Agent
  Properties, redemption, and IANA registrations.
* Required key-bound grants, sender-constrained downstream tokens,
  atomic single-use redemption, and issuer-qualified record correlation.
* Defined per-issuance status and delegation checks, tenant key
  isolation, bounded clock skew, and delegated renewal behavior.
* Added end-to-end examples, interoperability cases, compatibility
  guidance, and related-draft coordination items.
* Consolidated normative rules into validation steps and claim tables;
  aligned security guidance with RFC 9700, clarified DPoP errors and
  time validation, and separated acceptance from RAS authorization.
