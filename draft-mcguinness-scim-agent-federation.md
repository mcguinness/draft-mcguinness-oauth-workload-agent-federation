---
title: "SCIM Profile for Agent Federation Management"
abbrev: "SCIM Agent Federation"
category: std
docname: draft-mcguinness-scim-agent-federation-latest
submissiontype: IETF
stand_alone: yes
ipr: trust200902
area: "Security"
workgroup: "System for Cross-domain Identity Management"
keyword:
 - SCIM
 - agent provisioning
 - workload federation
venue:
  group: "System for Cross-domain Identity Management"
  type: "Working Group"
  mail: "scim@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/scim/"
  github: "mcguinness/draft-mcguinness-oauth-workload-agent-federation"
  latest: "https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-scim-agent-federation.html"
author:
 - fullname: Karl McGuinness
   organization: Independent
   email: public@karlmcguinness.com
normative:
  OAUTH-CLIENT:
    title: "SCIM Profile for OAuth 2.0 Client Management"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-scim-oauth-client-management
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-scim-oauth-client-management.html
  FEDERATION:
    title: "OAuth 2.0 Profile for Governed Agent Federation"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-workload-agent-federation
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
  RFC6901:
  RFC6585:
informative:
  LIFECYCLE:
    title: "Governed Agent Lifecycle Profile for SCIM and OAuth"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-governed-agent-lifecycle
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-governed-agent-lifecycle.html
--- abstract

This document profiles the System for Cross-domain Identity Management
(SCIM) for platform-to-identity-provider management of Agent Principals,
Identity Bindings, and Client Associations. It extends the SCIM Agent
resource with the principal's issuer-qualified identity and defines
resources for the two independently authorized relationships. Client
Associations and dedicated-client bindings reference OAuthClient resources
from the generic SCIM client-management profile. Shared clients use
independent workload bindings to distinguish the agents they exercise.

The profile reuses SCIM operations, discovery, and conditional updates.
It defines how approved management changes affect new grant issuance;
it does not establish credential-authority trust, grant user delegation,
or revoke previously issued downstream authorization.

--- middle

# Introduction

Governed Agent Federation {{FEDERATION}} separates the identity of an
Agent Principal from its resolution inputs, permitted OAuth clients,
user delegations, and resource permissions. Its token protocol assumes
that the corresponding administrative relationships already exist.
This document manages Agent Principals, Identity Bindings, and Client
Associations at the IdP. OAuth client identity and configuration are
managed separately through {{OAUTH-CLIENT}}.

~~~
 Dedicated client                     Shared client

 OAuthClient                          External workload identity
      |                                         |
 Identity Binding                     Identity Binding
      |                                         |
      v                                         v
    Agent                                     Agent

 Both paths require:
 OAuthClient -- Client Association --> Identity Binding
~~~

A platform can administer only the identities and permissions delegated
to its connector. The IdP remains the authority for the Agent Principal
and the decision to accept each relationship. Approval can be established
by administrative policy before provisioning; this profile defines no
interactive approval workflow.

The management resources correspond to existing federation concepts:

| Resource | Question it answers |
|---|---|
| OAuthClient ({{OAUTH-CLIENT}}) | Which OAuth client is admitted at this IdP? |
| Agent | Which stable principal does the enterprise govern? |
| AgentIdentityBinding | Which validated client or workload identity resolves to that principal? |
| AgentClientAssociation | May this OAuth client use this binding in this flow? |

Successful provisioning does not authorize user delegation or resource
access. Token processing continues to apply every applicable check in
{{FEDERATION}}. The IdP-to-resource-domain provisioning and lifecycle
composition in {{LIFECYCLE}} is separate from this platform-to-IdP interface.

OAuthClient can represent a locally registered client or local admission
of a CIMD client. This profile references that resource; it does not copy
registration metadata, keys, or CIMD documents into Agent resources.
An OAuthClient can participate in multiple Client Associations. An Agent
can have multiple Identity Bindings. Neither relationship makes the
OAuth client and Agent Principal the same identity.

## Scope

This profile defines explicit bindings and associations for delegated
ID-JAG issuance. It supports the federation draft's dedicated-client,
SPIFFE, Client Attestation, and existing platform JWT resolution inputs.
Implementations need only support the credential classes they accept
under {{FEDERATION}}.

The following remain outside this profile:

* Establishing trust in a new credential authority. Trust remains a
  prerequisite, not an effect of a binding write. OAuth client registration
  is defined separately by {{OAUTH-CLIENT}}.
* User delegation, resource permissions, and cross-domain user linking.
* Runtime enrollment, credential issuance, key custody, and instance
  continuity.
* Relationship-change events and revocation of outstanding authorization.
* A portable policy language, automatic principal merging, and a WAG
  wire composition.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

SCIM attributes, resource types, and operations follow {{RFC7643}} and
{{RFC7644}}. Agent Principal, Identity Binding, Client Association,
credential class, and Governance Tenant follow {{FEDERATION}}.

Provisioning Client:
: The platform's authenticated SCIM connector. It is not necessarily
  an OAuth client permitted to exercise an Agent Principal.

Service Provider:
: The IdP's SCIM service, including the administration of configuration
  used by its grant issuer.

Provisioning Domain:
: The scope of one Provisioning Client's management authority within
  one Governance Tenant. The Service Provider establishes this scope
  from authenticated administrative context. Credential rotation need
  not change the Provisioning Domain.

The federation identity is the pair (IdP issuer, Agent Principal
subject). SCIM resource identifiers and connector correlation identifiers
serve management purposes and do not replace that pair.

# Conformance and Administrative Trust {#trust}

A conforming Service Provider supports the resources in {{resources}},
the operations in {{operations}}, and their effects in {{issuance}}.
A conforming Provisioning Client uses those representations and
operations within its administrative authorization.

Before provisioning, administrators establish:

* The authenticated connector, Governance Tenant, and Provisioning Domain.
* The credential authorities, validation profiles, and source-identity
  ranges the connector may use in Identity Bindings.
* The IdP OAuthClient resources the connector may reference in bindings
  and associations, and any separate client-management permissions under
  {{OAUTH-CLIENT}}. Referencing an existing client does not require permission
  to create it or change its metadata. Client-management permission does
  not imply binding or association permission.

Authentication and authorization of SCIM requests follow
{{Section 2 of RFC7644}}. This profile defines no new management-token
format or OAuth scope vocabulary.

The Service Provider MUST authorize each operation and security-relevant
attribute against this administrative context. In particular:

* Authority to create or describe an Agent MUST NOT imply authority to
  establish its bindings or client permissions.
* Binding administration MUST be restricted to approved credential
  classes, authorities, source identities, and destination agents.
* Association administration MUST be restricted to approved OAuth
  clients, bindings, and flows.
* Permission to disable a resource MUST NOT imply permission to enable
  it. An enabled resource is an approved relationship, not a pending request.
* Resource references MUST resolve within the authorized Governance
  Tenant. A request attribute, URI, or discovered key MUST NOT expand
  the caller's administrative scope.

These permissions can be delegated together, but each decision remains
independent. Policy may authorize an operation automatically; no
per-resource human approval is required by this profile. Rejection uses
SCIM errors rather than a new approval state.

# Resources and Schemas {#resources}

The SCIM service exposes the following resource types. This document
defines only the Agent extension and the two relationship schemas;
OAuthClient and the core Agent schema come from their respective profiles.

| Resource type | Endpoint |
|---|---|
| OAuthClient (defined in {{OAUTH-CLIENT}}) | `/OAuthClients` |
| Agent | `/Agents` |
| AgentIdentityBinding | `/AgentIdentityBindings` |
| AgentClientAssociation | `/AgentClientAssociations` |

The Service Provider MUST expose referenced OAuth clients under
{{OAUTH-CLIENT}} in the same authorized SCIM service. Existing registrations
can be represented without changing their OAuth client identifiers or keys.
Connectors can discover an authorized resource by its issuer and `client_id`
and then reference its SCIM `id`. They need not create a client for each
Agent. Client creation and CIMD admission remain separately authorized.

These are management representations, not requirements on an IdP's
internal database. An existing principal MAY be exposed as the Agent
resource without creating a second authorization principal. Establishing
that representation for an existing principal requires explicit local
administrative authorization; the API provides no automatic attachment
based on names or credentials.

## Common Attributes and References {#common}

Agent, AgentIdentityBinding, and AgentClientAssociation use SCIM `schemas`,
`id`, `externalId`, and `meta`. The rules below apply to those three types;
OAuthClient attribute and operation rules remain those of {{OAUTH-CLIENT}}.

* **Connector correlation:** POST requests MUST contain a non-empty
  `externalId`. Its value is chosen by the Provisioning Client and
  identifies its source record, not a workload credential subject.
  The Service Provider MUST enforce uniqueness of that value within
  the Provisioning Domain and resource type, including concurrent POSTs.
* **Stable management identity:** Once assigned, `externalId` MUST NOT
  change through this interface. This narrows SCIM's common attribute
  mutability. `id` and the federation identity remain server-assigned.
* **Versions:** Full resource responses MUST carry `meta.version`; individual
  resource responses MUST also carry the corresponding HTTP ETag.
  Version changes cover all modifications visible through this interface.
* **References:** A relationship reference is a single-valued complex
  attribute. Its REQUIRED string `value` is the target resource's SCIM
  `id`; its OPTIONAL read-only `$ref` is a reference to that resource,
  with `referenceTypes` set to the named target type. The Service
  Provider resolves `value` locally and MUST NOT fetch a caller-supplied
  `$ref` to establish the relationship.

The new schema tables below are normative. Unless specified otherwise,
attributes are required, immutable, single-valued, returned by default,
and have uniqueness `none`. String values are case-exact. Exceptions
appear with each table; no attribute has additional canonical values
unless listed.
The common attributes retain SCIM's characteristics except for the
explicit `externalId` narrowing above. Attribute-name processing remains
that of SCIM, independently of case-exact identity values.

Reference sub-attributes have `value` mutability `immutable` and `$ref`
mutability `readOnly`; both use uniqueness `none` and returned `default`.
A reference's requiredness is given in its resource table. Identity
values MUST NOT be normalized, case-folded, or matched by prefix.

## Agent Federation Extension {#agent-schema}

The Agent resource uses {{SCIM-AGENT}}, including its `agentUserName`,
`displayName`, and `active` attributes. It adds the required extension:

`urn:ietf:params:scim:schemas:extension:agent-federation:2.0:Agent`

The extension name is `AgentFederation`. Both attributes are required,
read-only strings.

| Attribute | Meaning |
|---|---|
| `issuer` | IdP issuer governing this Agent Principal |
| `subject` | Agent Principal identifier within that issuer's namespace |

The Service Provider assigns the pair when creating the Agent and
returns it in the extension object. Creation requests MAY omit this
read-only extension object and its schema URI; the server MUST populate
both in the created resource. Supplied read-only values are
handled under SCIM's read-only rules and MUST NOT select an existing
principal. The subject MUST be unique and non-reassignable across all
Governance Tenants sharing that issuer, as required by {{FEDERATION}}.
Changing the administrative authority represented by the principal is
not an update of these attributes.

For this profile, `active: false` prevents new grants involving the
principal. `active: true` permits evaluation of the other required
relationships; it does not bypass IdP policy, suspension, or delegation
checks. The Service Provider MUST authorize changes to `active`
separately from descriptive edits. Renaming the Agent, changing its
owners, or changing its `externalId` in an upstream platform does not
change the federation identity or grant permissions.

## Identity Binding {#binding-schema}

An `AgentIdentityBinding` links one resolution identity to one Agent.
For dedicated-client resolution it references an OAuthClient. For workload
resolution it names an external identity under an approved credential
authority. The credential class determines which representation applies.
Its schema URI is:

`urn:ietf:params:scim:schemas:core:2.0:AgentIdentityBinding`

| Attribute | Type | Meaning |
|---|---|---|
| `agent` | complex | Reference to the Agent whose principal is resolved |
| `credentialClass` | string | Input class from {{classes}} |
| `client` | complex | OAuthClient reference; required only for `dedicated-client` |
| `sourceAuthority` | string | Approved authority; required for all other classes |
| `sourceSubject` | string | Exact external identity; required for all other classes |
| `selectors` | complex | Additional platform-JWT claim constraints |
| `enabled` | boolean | Whether the binding may be used |

`selectors` is optional and multi-valued. `enabled` is optional and
readWrite, defaults to false on creation, and MUST be returned explicitly
unless excluded by SCIM attribute projection. An unassigned or removed
value is false; only boolean true enables the binding.
The reference target type of `agent` is Agent; that of `client` is
OAuthClient. `client`, `sourceAuthority`, and `sourceSubject` have schema
characteristic `required: false` with these conditional requirements:

* For `dedicated-client`, `client` MUST be present and `sourceAuthority`,
  `sourceSubject`, and `selectors` MUST be absent. The IdP resolves the
  authenticated client to the referenced OAuthClient using its configured
  authorization-server issuer and exact `client_id`.
* For all other classes, `sourceAuthority` and `sourceSubject` MUST be
  present and `client` MUST be absent. The external identity is validated
  and matched under {{classes}}; an OAuthClient reference cannot substitute
  for that evidence.

Every referenced OAuthClient's `authorizationServer` MUST equal the
Agent's federation `issuer`, and the reference must be authorized in the
same Governance Tenant. A CIMD URL is taken from the referenced client's
`client_id`; its document origin is not the IdP issuer. Client metadata
and key changes follow {{OAUTH-CLIENT}} and do not change this binding.

The dedicated-client reference selects the identity used for resolution;
it does not authorize use. A Client Association remains required, even
when it references the same OAuthClient. Administrators can manage the
two relationships together while retaining separate enablement and
authorization decisions.

Each `selectors` element has REQUIRED single-valued string attributes
`path` and `value`, both immutable, case-exact, returned by default, and
with uniqueness `none`. `path` is a JSON Pointer string under
{{Section 5 of RFC6901}}. `value` is the expected claim value.
Duplicate paths MUST be rejected. Selector order has no significance;
all selectors must match. Their evaluation follows {{FEDERATION}}.
Selectors are permitted only for `platform-jwt`; they cannot replace
`sourceAuthority` or `sourceSubject`. Adding, removing, or changing
selectors after creation requires a new binding, including when the
original binding had no selectors. This narrows SCIM's permission to
initially populate an unassigned immutable attribute.

### Credential Classes {#classes}

These names identify management input classes, not OAuth token types or
new credential formats. Each class uses its validation and presentation
rules from {{FEDERATION}}. The following classes use external identity
fields:

| Credential class | Source authority | Source subject |
|---|---|---|
| `spiffe-jwt` | Approved SPIFFE trust domain name | Complete SPIFFE ID from the JWT-SVID `sub` |
| `spiffe-wit` | Approved SPIFFE trust domain name | Complete SPIFFE ID from the WIT-SVID `sub` |
| `spiffe-x509` | Approved SPIFFE trust domain name | Complete SPIFFE ID from the certificate URI Subject Alternative Name |
| `client-attestation` | Identifier of the trusted attester in IdP configuration | Validated Client Attestation `sub` identifying the OAuth client |
| `platform-jwt` | Exact approved JWT issuer | Exact JWT `sub` |

`dedicated-client` instead uses the OAuthClient reference defined in
{{binding-schema}}. It retains the authentication requirements of
{{FEDERATION}}; creating a reference neither configures a new
authentication method nor supplies workload provenance.
In that profile's `private_key_jwt` path, the validated assertion issuer
and subject both identify the referenced OAuthClient's `client_id`.
The reference does not replace those authentication checks.

A trust domain name is the authority component of the SPIFFE ID; for
example, `platform.example` for `spiffe://platform.example/agents/a7`.
The Service Provider MUST require it to match the subject's trust
domain. For `client-attestation`, the attester identifier references
preconfigured trust; it need not be an `iss` claim in the credential.

The Service Provider MUST resolve these values and the Governance
Tenant to one approved validation configuration, including applicable
client-registration context. Unknown, unsupported, or ambiguous
configurations MUST be rejected. This interface does not create them.
A signing-key identifier, URL, or possession of a credential is not
administrative permission to establish a binding.

### Binding Uniqueness and Changes

The Service Provider MUST reject duplicate bindings in the same
Governance Tenant, regardless of enabled state. The uniqueness key is:

| Input | Uniqueness key |
|---|---|
| Dedicated client | `credentialClass` and `client.value` |
| External identity | `credentialClass`, `sourceAuthority`, `sourceSubject`, and selector set |

The selector set is compared by decoded JSON Pointer paths and exact expected values,
independent of array order. The Agent reference is not part of this
uniqueness key: duplicating an identity does not authorize a second
principal.

Different selector sets can overlap. The runtime requirement to resolve
exactly one enabled binding remains in force; an ambiguous match MUST
NOT issue a grant. Management acceptance does not waive that check.

Changing the client reference, source identity, or destination Agent
requires a new binding; it is not an in-place credential rotation.
Rotation of an authority's
signing keys follows its preconfigured trust mechanism and need not
change the binding. An authorized replacement binding receives a new
SCIM `id`, so existing associations do not silently authorize its use.

## Client Association {#association-schema}

An `AgentClientAssociation` permits one authenticated IdP OAuth client
to use one Identity Binding in one flow. Multiple resources can express
an explicitly enumerated binding set. This profile defines no predicates
that automatically cover future bindings. Its schema URI is:

`urn:ietf:params:scim:schemas:core:2.0:AgentClientAssociation`

| Attribute | Type | Meaning |
|---|---|---|
| `binding` | complex | Reference to the binding the client may use |
| `client` | complex | Reference to the OAuthClient registration at this IdP, not the RAS |
| `flow` | string | `id-jag` in this revision |
| `enabled` | boolean | Whether the permission may be used |

`enabled` has the same characteristics as in {{binding-schema}}. The
reference target type of `binding` is AgentIdentityBinding; that of `client`
is OAuthClient. Each uses the `value` and `$ref` characteristics in
{{common}}. The client reference carries a SCIM `id`, not `client_id`.

The binding determines the Agent and permitted credential class. An
association MUST NOT be interpreted as permission to use another
binding to the same Agent, even with the same credential class. For
dedicated-client resolution, the association's `client.value` MUST equal
the binding's `client.value`. For external-identity resolution, this
reference independently selects the client permitted to present that
identity; it need not identify the workload credential's subject.
The client's `authorizationServer` MUST equal the governing IdP issuer.
A matching `client_id` at another authorization server does not qualify.

For a CIMD client managed under {{OAUTH-CLIENT}}, `client.value` still
references its SCIM `id`; its OAuth `client_id` remains the Client
Identifier URL. Document discovery and local admission establish
neither an Identity Binding nor a Client Association. Document metadata
changes MUST NOT create or expand those relationships.

The Service Provider MUST validate the referenced binding and client
registration and authorize their use together. It MUST reject duplicate
associations for the same binding, client, and flow in the Governance
Tenant, regardless of enabled state. Other flow values are unsupported
in this revision; accepting `id-jag` does not imply WAG support.

The association is necessary permission for this binding and flow.
Target, scope, user delegation, and other policy constraints remain
independently configured and evaluated by the IdP. This resource does
not express or override them.

# SCIM Operations {#operations}

This section applies to Agent, AgentIdentityBinding, and
AgentClientAssociation. OAuthClient operations follow {{OAUTH-CLIENT}}.

The Service Provider MUST support SCIM POST creation, individual and
collection GET, PATCH, and DELETE for these resources. PUT support is
OPTIONAL; when supported, the same authorization, reference, and
concurrency rules apply. SCIM Bulk and cross-resource transactions are
not required. All requests and responses use existing SCIM message
formats and status codes except the standard HTTP precondition response
specified in {{concurrency}}.

## Creation and Retry Recovery {#creation}

An Agent creation allocates a new principal unless an administrator has
already established its representation outside this creation operation.
POST MUST NOT attach to an existing principal by matching `agentUserName`,
`displayName`, `externalId`, or source credentials. To manage an existing
Agent, the connector must be granted access to that existing resource.

For relationships, the referenced resource MUST exist in the authorized
Governance Tenant. It need not yet be enabled: the connector can stage
an inactive Agent, its bindings, and its associations before enabling
issuance. Each write is independently authorized; creation with
`enabled: true` additionally requires enabling permission.

If a response is lost, the connector queries the same resource type
by exact `externalId` before retrying. A duplicate POST uses `409` with
`scimType` `uniqueness`; it is not an upsert. The Service Provider MUST
serialize the uniqueness check with creation. The client MUST retrieve
and compare the existing resource before treating a conflict as success.
It MUST NOT silently overwrite a different existing relationship.

This profile's externalId uniqueness narrows generic SCIM behavior.
It applies to live resources. Deletion and stale-writer handling follow
{{deletion}}; no exactly-once delivery guarantee is implied.

## Updates and Concurrency {#concurrency}

Service Providers MUST support SCIM ETags and conditional updates under
{{Section 3.14 of RFC7644}}. Provisioning Clients MUST send the current
resource version in `If-Match` for PATCH, PUT, and DELETE. A missing
precondition receives HTTP `428` under {{RFC6585}}; a failed precondition
receives HTTP `412` under {{Section 3.12 of RFC7644}}. No new `scimType`
is defined for either response.

SCIM PATCH is atomic for one resource. An authorization or validation
failure MUST leave that resource unchanged. Clients MUST NOT retry a
stale update by fetching the new ETag and blindly overwriting the
resource; they first reconcile the current state with the intended
change. This prevents an old enablement from undoing a newer disablement.

Immutable values can be supplied unchanged on PUT but cannot be
reassigned. Removing an optional value does not make an existing
immutable identity replaceable. Changing a relationship's identity
requires a new resource. Ordinary descriptive Agent edits do not change
bindings, associations, or delegation.

## Deletion {#deletion}

DELETE of an agent-management resource prevents its use for new
grant issuance under {{issuance}}. It does not revoke already-issued
tokens. The Service Provider MUST NOT reuse a deleted SCIM `id` or an
Agent Principal's qualified identity.

Deletion has the following dependency effects:

| Deleted resource | Effect on dependent relationships |
|---|---|
| Agent | Its bindings and their associations are unusable |
| OAuthClient | Dedicated-client bindings and associations referencing it are unusable; external-identity bindings remain independent |
| AgentIdentityBinding | Its associations are unusable |
| AgentClientAssociation | Its permission is removed; client, binding, and Agent remain |

OAuthClient deletion follows {{OAUTH-CLIENT}}, including CIMD readmission
controls and the treatment of outstanding authorization. The rules here
do not weaken that behavior. The Service Provider MUST retain dependent
resources as non-effective references until explicitly deleted. A new
OAuthClient with the same OAuth identifier has a new SCIM `id` and MUST
NOT inherit the deleted resource's bindings or associations.

Direct and filtered reads allow authorized connectors to find and remove
these references. A missing target MUST NOT prevent an authorized
disablement or deletion of a dependent resource. Creation or enablement
with a missing target MUST be rejected.

A later POST with a previously used `externalId` is a new creation,
requiring current authorization and receiving a new `id`. Clients that
need reversible disablement use `active: false` or `enabled: false`,
not DELETE. To prevent an old connector from recreating deleted records,
administrators withdraw that connector's create authority; DELETE alone
does not revoke its management credentials.

## Query and Reconciliation {#query}

The Service Provider MUST support paginated collection reads and the
following `eq` filters, together with `and` combinations:

| Resource | Required filter attributes |
|---|---|
| The three agent-management types | `id`, `externalId` |
| Agent | `active`, extension `issuer` and `subject` |
| AgentIdentityBinding | `agent.value`, `client.value`, `credentialClass`, `enabled` |
| AgentClientAssociation | `binding.value`, `client.value`, `flow`, `enabled` |

OAuthClient queries follow {{OAUTH-CLIENT}}. Collection reads MUST return
only resources within the caller's read permission. For a platform
connector, an `externalId` lookup is scoped
to its Provisioning Domain and resource type; another connector's
correlation value cannot select its resource. An administrative reader
spanning several domains cannot assume that externalId alone is unique.

A binding lookup can use `agent.value eq "a17" and enabled eq true`.
To find dependencies of OAuthClient `oc7`, query both relationship
collections with `client.value eq "oc7"`. This finds dedicated-client
bindings and all associations naming that client. External-identity
bindings have no `client` attribute; their client permissions are found
through associations.
For an Agent subject lookup, the attribute name is the extension schema
URI followed by `:subject`, with the expression `eq "agent-42"`.
The connector URI-encodes the complete filter under SCIM's query rules.

Enumeration is not a transactional snapshot. Reconciliation reads
current resource versions and uses conditional changes; it MUST NOT
delete records solely because they were absent from an incomplete or
failed enumeration. This profile defines no change feed or event type.

## Discovery {#discovery}

The Service Provider MUST expose `/ServiceProviderConfig`, `/ResourceTypes`,
and `/Schemas` under {{Section 4 of RFC7644}}. It advertises PATCH,
filtering, and ETag support as enabled. Each ResourceType gives the
endpoint in {{resources}} and the schema defined for that resource;
Agent includes the federation
extension in `schemaExtensions` with `required: true`.

The `/Schemas` representations MUST describe the characteristics in
{{common}}, {{agent-schema}}, {{binding-schema}}, and
{{association-schema}}. Discovery advertises syntax and capabilities;
it does not approve a connector, credential authority, or relationship.
Unsupported credential classes remain subject to {{classes}}. The
connector and IdP agree on usable input classes during trust setup.

## Errors

Errors follow {{Section 3.12 of RFC7644}} except the HTTP `428` response
in {{concurrency}}. The following mappings make the profile's failures
predictable:

| Failure | Response |
|---|---|
| Unauthorized operation, tenant, or protected attribute | `403`; no new `scimType` |
| Duplicate externalId in its scope, binding key, or association key | `409`, `uniqueness` |
| Unsupported class or flow, invalid combination of binding fields, ambiguous authority configuration, malformed selector, or missing/invalid reference | `400`, `invalidValue` |
| Attempt to change an immutable value, including externalId | `400`, `mutability` |
| Missing conditional-write precondition | `428`; no new `scimType` |
| Failed conditional-write precondition | `412`; no new `scimType` |

Standard SCIM request syntax, filter, authentication, and not-found
errors retain their meanings. Responses MUST NOT reveal cross-tenant
resource existence. Authorized administrators need sufficient diagnostics
to distinguish configuration and permission failures without exposing
credentials or key material.

# Effect on Grant Issuance {#issuance}

For new issuance, the IdP evaluates the conjunction of:

* An active OAuthClient whose issuer-qualified `client_id` matches the
  authenticated client.
* An eligible Agent Principal represented by an active Agent.
* Exactly one matching, enabled Identity Binding whose Agent exists.
  Dedicated-client matching uses the authenticated OAuthClient reference;
  other classes use the independently validated external identity.
* An enabled Client Association referencing that binding and the
  authenticated OAuthClient for the requested flow.
* All remaining credential, delegation, target, and policy checks in
  {{FEDERATION}}.

Missing configuration is not implicit permission. Disabling an Agent
blocks every path to that principal. Disabling one binding or association
blocks only its use; independent approved relationships remain available.
Disabling an OAuthClient blocks dedicated-client resolution through it
and its use of every association, without disabling the associated Agent
Principals or independent workload bindings. Client registration alone
establishes neither an Identity Binding nor a Client Association.
Re-enabling a parent does not change a child's explicit disabled state.

Before returning success for a restrictive change, the Service Provider
MUST make that restriction effective for grant-authorization decisions
that begin after the response. A provider with asynchronous internal
replication must enforce the restriction at issuance or delay success;
a successful SCIM response MUST NOT mean only that an update was queued.
An in-flight decision made before the restriction can still complete.
If this guarantee cannot be met, the write MUST fail without reporting
successful application; the connector reconciles current state before
retrying.

This is a new-issuance guarantee, not a downstream revocation bound.
The IdP's refresh-token subject processing still makes a new issuance
decision and therefore applies these restrictions. Previously issued
ID-JAGs, resource access tokens, and RAS refresh authorizations require
their own validation and revocation processing. {{LIFECYCLE}} addresses
agent-wide propagation; this document defines no selective relationship
revocation event or automatic cancellation of existing work.

# Security Considerations

## Administrative Privilege and Confused Deputies

Binding and association writes can enable impersonation of an Agent
Principal. The Service Provider MUST check the connector's authority over
both ends of each relationship, including on creation with disabled state
and on later enablement. Permission to manage a platform catalog is not
permission to bind its records to arbitrary enterprise principals.

Credential-authority trust remains preconfigured. `sourceAuthority` is
an identifier to match, not a URL to fetch or an instruction to trust a
new issuer. A valid workload credential or control of an OAuth client
key cannot authorize an administrative write by itself. References do
not permit cross-tenant attachment or SSRF.

## Independent Controls and Stale State

OAuthClient, Agent, binding, and association enablement have distinct
effects. An owner, group, or display-name update MUST NOT implicitly enable any of
them. All writers to the underlying relationships, including local
administrative interfaces, need to preserve the same semantics and
invalidate the SCIM resource version when visible state changes.

A client key rotation or CIMD metadata update does not create a new Agent
Principal or expand its bindings and associations. A shared client's
authentication credential cannot select among agents without the
resolution input required by {{FEDERATION}}. Dedicated-client resolution
proves the authenticated client identity, not an independent runtime.

ETags prevent stale conditional writes; they are not lifecycle versions
and do not revoke previously issued tokens. A connector that retains
create or enable permission can request new access after earlier
disablement, subject to current policy. Administrators must withdraw
that authority when the connector itself is compromised.

Management changes SHOULD be audited with the administrative actor,
Provisioning Domain, affected resource, and changed relationships.
Audit records should identify principals and configuration changes
without retaining reusable workload credentials.

# Privacy Considerations

The profile correlates platform records, workload identities, enterprise
principals, and OAuth clients. SCIM readers SHOULD receive only the
attributes and resources needed for their management role. Stable
correlation identifiers and selectors SHOULD avoid personal data when
opaque platform identifiers suffice. Read authorization is independent
of permission to exercise the agent at a token endpoint.

# IANA Considerations {#iana}

This document requests the following entries in the SCIM Schema URIs
registry using {{Section 10.3.2 of RFC7643}}. These URIs are proposed
registrations; no assignment is implied by this editor's copy.

## Agent Federation Extension

* Schema URI:
  `urn:ietf:params:scim:schemas:extension:agent-federation:2.0:Agent`
* Schema Name: Agent Federation
* Intended or Associated Resource Type: Agent
* Purpose: Expose the IdP-qualified Agent Principal represented by a
  SCIM Agent resource.
* Single-value Attributes: `issuer`, `subject`, defined in {{agent-schema}}.
* Multi-valued Attributes: None.

## Agent Identity Binding

* Schema URI:
  `urn:ietf:params:scim:schemas:core:2.0:AgentIdentityBinding`
* Schema Name: Agent Identity Binding
* Intended or Associated Resource Type: AgentIdentityBinding
* Purpose: Manage an approved resolution identity's binding to an Agent
  Principal.
* Single-value Attributes: `agent`, `credentialClass`, `client`, `sourceAuthority`,
  `sourceSubject`, `enabled`, defined in {{binding-schema}}.
* Multi-valued Attributes: `selectors`, defined in {{binding-schema}}.

## Agent Client Association

* Schema URI:
  `urn:ietf:params:scim:schemas:core:2.0:AgentClientAssociation`
* Schema Name: Agent Client Association
* Intended or Associated Resource Type: AgentClientAssociation
* Purpose: Manage an OAuth client's permission to use an Identity
  Binding in a flow.
* Single-value Attributes: `binding`, `client`, `flow`, `enabled`,
  defined in {{association-schema}}.
* Multi-valued Attributes: None.

No new OAuth token type, event type, HTTP method, or SCIM error type is
registered. Credential-class names are local to this profile's schema.

--- back

# Example: Platform Onboarding {#example}

These non-normative examples show a shared platform client. Administrative
policy has already authorized the connector for Governance Tenant
`acme`, the platform JWT issuer `https://platform.example/`, its permitted
workload subjects, and permission to reference and associate the platform's
existing IdP OAuthClient. The token value is a placeholder. Content-Length
and repeated authorization headers are omitted for readability.

The IdP preconfigures the platform credential's validation rules,
including the audience and key source. None are established by these
SCIM requests.

## Obtain the OAuthClient Reference

The connector first obtains an authorized OAuthClient under
{{OAUTH-CLIENT}}. It can reference an existing registration, create one
with separate permission, or admit a CIMD client. Client authentication
and token-exchange metadata are established by that profile, not by the
agent-management requests below.

For this example, the client is already active and has:

| Attribute | Value used here |
|---|---|
| SCIM `id` | `oc7` |
| `authorizationServer` | `https://idp.example/` |
| OAuth `client_id` | `platform-sso` |

The connector can find an existing resource with the filter
`authorizationServer eq "https://idp.example/" and client_id eq "platform-sso"`,
URI-encoded in a collection request. It uses `oc7` in relationships and
`platform-sso` at the token endpoint. For a CIMD client, the filter and
OAuth requests use the Client Identifier URL instead; relationship
requests still use the returned SCIM `id`.

## Create an Inactive Agent

~~~ http-message
POST /scim/acme/Agents HTTP/1.1
Host: idp.example
Authorization: Bearer CONNECTOR_ACCESS_TOKEN
Content-Type: application/scim+json
Accept: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Agent"],
  "externalId": "agent-7",
  "agentUserName": "analysis-agent-7",
  "displayName": "Analysis agent",
  "active": false
}
~~~

The required extension is populated by the server:

~~~ http-message
HTTP/1.1 201 Created
Location: https://idp.example/scim/acme/Agents/a17
ETag: W/"a1"
Content-Type: application/scim+json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:Agent",
    "urn:ietf:params:scim:schemas:extension:agent-federation:2.0:Agent"
  ],
  "id": "a17",
  "externalId": "agent-7",
  "agentUserName": "analysis-agent-7",
  "displayName": "Analysis agent",
  "active": false,
  "urn:ietf:params:scim:schemas:extension:agent-federation:2.0:Agent": {
    "issuer": "https://idp.example/",
    "subject": "agent-42"
  },
  "meta": {
    "resourceType": "Agent",
    "version": "W/\"a1\"",
    "location": "https://idp.example/scim/acme/Agents/a17"
  }
}
~~~

The platform's `agent-7`, SCIM's `a17`, and the IdP's
`agent-42` have separate roles. Only (`https://idp.example/`, `agent-42`)
is the federated Agent Principal identity.

## Bind the Workload Identity

~~~ http-message
POST /scim/acme/AgentIdentityBindings HTTP/1.1
Host: idp.example
Content-Type: application/scim+json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:AgentIdentityBinding"
  ],
  "externalId": "platform-binding-7",
  "agent": {"value": "a17"},
  "credentialClass": "platform-jwt",
  "sourceAuthority": "https://platform.example/",
  "sourceSubject": "workload-7",
  "enabled": true
}
~~~

The IdP authorizes the relationship and returns `201 Created` with the
resource representation, `id: b9`, ETag `W/"b1"`, and its Location.
The binding is enabled, but the inactive Agent prevents issuance.

## Authorize Client Use

~~~ http-message
POST /scim/acme/AgentClientAssociations HTTP/1.1
Host: idp.example
Content-Type: application/scim+json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:AgentClientAssociation"
  ],
  "externalId": "platform-association-7",
  "binding": {"value": "b9"},
  "client": {"value": "oc7"},
  "flow": "id-jag",
  "enabled": true
}
~~~

The IdP returns `201 Created` with the resource representation,
`id: c3`, ETag `W/"c1"`, and its Location. The reference `oc7` resolves to
OAuth client `platform-sso`; it does not replace that client's identity
at the token endpoint. This permission does not
supply a user subject credential, consent, or target-resource authority.

## Enable the Agent

~~~ http-message
PATCH /scim/acme/Agents/a17 HTTP/1.1
Host: idp.example
Content-Type: application/scim+json
If-Match: W/"a1"

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    {"op": "replace", "path": "active", "value": true}
  ]
}
~~~

The IdP returns `204 No Content` with ETag `W/"a2"` after applying
the authorized change. Subsequent token exchanges can now resolve
`workload-7` through `b9` to `agent-42`, and verify client permission
through `c3`. The IdP still checks user delegation and target authority
before issuing an ID-JAG with `act.iss` equal to `https://idp.example/`
and `act.sub` equal to `agent-42`.

## Recover a Lost Creation Response

The connector can recover the Agent resource using its correlation value:

~~~ http-message
GET /scim/acme/Agents?filter=externalId%20eq%20%22agent-7%22 HTTP/1.1
Host: idp.example
Accept: application/scim+json
~~~

An authorized query returns a SCIM ListResponse containing `a17`. The
connector verifies the record before continuing. A racing duplicate
POST receives `409` with `scimType: uniqueness`, not another principal.

## Disable One Binding

~~~ http-message
PATCH /scim/acme/AgentIdentityBindings/b9 HTTP/1.1
Host: idp.example
Content-Type: application/scim+json
If-Match: W/"b1"

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    {"op": "replace", "path": "enabled", "value": false}
  ]
}
~~~

After a successful response, new grant-authorization decisions cannot
use `b9`. Association `c3` remains recorded but cannot override the
disabled binding. Another independently approved binding can still
resolve `agent-42`. Previously issued tokens are not revoked by this
SCIM operation.

## Rejection and Boundary Examples

| Operation | Result |
|---|---|
| Retry Agent POST with the same externalId in the same Provisioning Domain | `409`, `uniqueness`; query and compare |
| Add a binding to an unapproved issuer or another tenant's Agent | Rejected; no trust or cross-tenant attachment |
| Create another binding for the same source key and selector set | `409`, `uniqueness`, even if disabled |
| Supply both `client` and `sourceSubject` on a dedicated-client binding | `400`, `invalidValue`; the client reference supplies the resolution identity |
| Associate a dedicated-client binding with a different OAuthClient | `400`, `invalidValue`; the two references must match |
| Change a binding's Agent or source subject | `400`, `mutability`; create a separately authorized replacement |
| Enable an association while its binding is disabled | Permission can be recorded but cannot authorize issuance |
| Change displayName with a connector lacking enable permission | Descriptive change can succeed; eligibility is unchanged |
| PATCH without If-Match | `428`; retrieve current version |
| PATCH with a stale version | `412`; reconcile before retrying |
| Delete a binding and create another with the same externalId | New id; old association does not attach to the replacement |
| Delete a CIMD OAuthClient and readmit the same URL | New SCIM id; prior bindings and associations remain unusable |
| Disable the Agent | All new issuance paths for that principal are blocked |

# Example: Dedicated Client {#dedicated-example}

This variant uses the same Agent `a17` but a dedicated OAuthClient `oc9`.
Its `authorizationServer` is `https://idp.example/`, and its `client_id`
is `analysis-client`. The connector creates this binding instead of the
platform-JWT binding in {{example}}:

~~~ json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:AgentIdentityBinding"
  ],
  "externalId": "dedicated-binding-7",
  "agent": {"value": "a17"},
  "credentialClass": "dedicated-client",
  "client": {"value": "oc9"},
  "enabled": true
}
~~~

After receiving binding `b10`, it separately creates the permission:

~~~ json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:AgentClientAssociation"
  ],
  "externalId": "dedicated-association-7",
  "binding": {"value": "b10"},
  "client": {"value": "oc9"},
  "flow": "id-jag",
  "enabled": true
}
~~~

At issuance, the IdP authenticates `analysis-client`, matches OAuthClient
`oc9`, resolves binding `b10` to Agent `a17`, and checks the separate
association. The resulting actor is still (`https://idp.example/`,
`agent-42`). No client assertion, key, or copied client identifier is
stored in the binding.

If `oc9` instead represents a CIMD client, its URL is the runtime
`client_id`; both relationship bodies are unchanged. An authorized key
rotation also leaves them unchanged. Replacing `oc9` with another SCIM
resource requires a new binding and association.

# Document History

Initial version.
