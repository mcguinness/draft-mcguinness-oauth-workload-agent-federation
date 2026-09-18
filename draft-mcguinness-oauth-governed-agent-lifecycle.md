---
title: "Governed Agent Lifecycle Profile for SCIM and OAuth"
abbrev: "Governed Agent Lifecycle"
category: std
docname: draft-mcguinness-oauth-governed-agent-lifecycle-latest
submissiontype: IETF
stand_alone: yes
ipr: trust200902
area: "Security"
workgroup: "Web Authorization Protocol"
keyword:
 - OAuth
 - agent provisioning
 - SCIM
 - lifecycle
 - shared signals
venue:
  group: "Web Authorization Protocol"
  type: "Working Group"
  mail: "oauth@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/oauth/"
  github: "mcguinness/draft-mcguinness-oauth-workload-agent-federation"
  latest: "https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-governed-agent-lifecycle.html"
author:
 - fullname: Karl McGuinness
   organization: Independent
   email: public@karlmcguinness.com
normative:
  AGENT-EVENTS:
    title: "Governed Agent Lifecycle Events Profile"
    author:
      - name: Karl McGuinness
    date: 2026-09-17
    seriesinfo:
      Internet-Draft: draft-mcguinness-ssf-governed-agent-events
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-ssf-governed-agent-events.html
  FEDERATION:
    title: "OAuth 2.0 Profile for Governed Agent Federation"
    author:
      - name: Karl McGuinness
    date: 2026-09-17
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-workload-agent-federation
  ID-JAG: I-D.ietf-oauth-identity-assertion-authz-grant
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  SSF:
    title: "OpenID Shared Signals Framework Specification 1.0"
    target: https://openid.net/specs/openid-sharedsignals-framework-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
  RFC6749:
  RFC6750:
  RFC7519:
  RFC7643:
  RFC7644:
  RFC7662:
  RFC8417:
  RFC8935:
  RFC8936:
  RFC9068:
informative:
  AGENT-MANAGEMENT:
    title: "SCIM Profile for Agent Federation Management"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-scim-agent-federation
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-scim-agent-federation.html
  RFC7009:
  RFC8792:
  SCIM-GOVERNANCE: I-D.kushwaha-scim-agent-governance
  WISE:
    title: "Workload Identity Security Events (WISE) Profile"
    target: https://github.com/identitymonk/openid-wise/blob/main/openid-wise-profile-1_0.md
    author:
      - org: WISE Contributors
  CAEP:
    title: "OpenID Continuous Access Evaluation Profile 1.0"
    target: https://openid.net/specs/openid-caep-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
  RISC:
    title: "OpenID RISC Profile Specification 1.0"
    target: https://openid.net/specs/openid-risc-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
  WAG: I-D.carleton-workload-authz-grant
--- abstract

This document profiles SCIM provisioning, Shared Signals, and OAuth for
the lifecycle of an issuer-qualified Agent Principal. It applies the state
and events defined by Governed Agent Lifecycle Events Profile to local
principal correlation, grant redemption, refresh, and API authorization.

An eligibility lease bounds reliance on active state. An authorization
cutoff prevents old authorization from reviving after reactivation. The
profile defines deployment requirements and denial bounds; it defines no
new event type, State Record format, SCIM schema, or delivery protocol.

--- middle

# Introduction

Governed Agent Federation {{FEDERATION}} separates agent identity,
client authority, user delegation, and resource authorization. It
identifies an agent by the pair (IdP issuer, Agent Principal identifier),
independently of the workload credentials used to establish it.

For delegated access, the governed identity is the actor in an Identity
Assertion JWT Authorization Grant (ID-JAG) {{ID-JAG}}. This companion
profiles Governed Agent Lifecycle Events Profile {{AGENT-EVENTS}},
carried in Security Event Tokens (SETs) {{RFC8417}} over the Shared
Signals Framework (SSF) {{SSF}}.

Federation establishes who the agent is. Lifecycle state establishes
whether that identity remains eligible. SCIM reconciles its local
representation; Shared Signals accelerates delivery of state changes.
OAuth enforcement limits how long stale authorization can remain usable.

The lifecycle registry and local resource representation are separate:

~~~
 Lifecycle Authority             Resource domain
 +-----------------+             +--------------------+
 | Lifecycle State | --SCIM/SET-> | Lifecycle Registry |
 +-----------------+             +----------+---------+
                                            |
                       +--------------------+-------------+
                       |                                  |
              +--------v--------+               +---------v---------+
              | SCIM Agent view |               | OAuth enforcement |
              | Local principal |               | RAS and API       |
              +-----------------+               +-------------------+
~~~
{: #lifecycle-model title="Provisioning and lifecycle enforcement"}

The registry can retain state before a local Agent resource exists and
after it is deleted. Neither a descriptive SCIM edit nor event delivery
creates permission to act. Both bindings use the same lifecycle version
and cutoff, so delayed delivery cannot reverse a newer decision.

## Scope and Relationship to Other Specifications

This profile defines a complete IdP-to-resource-domain path:

* Provision or explicitly correlate an Agent Principal with a local record.
* Synchronize active, disabled, and retired state.
* Apply changes to grant redemption, access-token issuance, refresh, and
  API authorization.
* Recover from duplicate, delayed, or missed delivery.

It uses the Agent resource in {{SCIM-AGENT}} and the lifecycle extension
defined in {{AGENT-EVENTS}}. The event specification owns the state and
wire formats; this document defines their SCIM and OAuth application.

{{SCIM-GOVERNANCE}} describes broader administrative lifecycle states.
{{WISE}} describes changes to workloads, credentials, and trust material.
{{CAEP}} describes continuous-access events. Those mechanisms can supply
inputs to an authority's decision. The state applied here expresses the
result for an Agent Principal and the receiver obligations that follow.

Platform-to-IdP enrollment, Identity Binding administration, individual
delegation revocation, task cancellation, runtime instance lifecycle,
and risk scoring are outside this profile. Their boundaries are stated
in {{relationship-changes}}. {{AGENT-MANAGEMENT}} separately profiles
platform-to-IdP management of Agent Principals, Identity Bindings, and
Client Associations; it does not define runtime enrollment.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth terms follow {{RFC6749}}. Agent Principal, Identity Binding, Client
Association, Governance Tenant, Target Tenant, and resource
authorization server (RAS) follow {{FEDERATION}}. SCIM terms follow
{{RFC7643}} and {{RFC7644}}; Transmitter, Receiver, and stream follow
{{SSF}}.

Lifecycle Authority:
: The IdP responsible for the Agent Principal's enterprise lifecycle
  state. An authorized connector can deliver that state on its behalf.

Lifecycle Receiver:
: The resource-domain component accepting provisioning and lifecycle
  updates and making them effective at the RAS. It is a SCIM service
  provider and an SSF Receiver. It and the RAS form one administrative
  deployment responsible for atomic state application; they need not
  run in the same process.

Agent Principal Lifecycle State (State Record):
: The logical snapshot defined in {{AGENT-EVENTS}} and applied under
  {{state-schema}}, containing
  identity, lifecycle version, status, authorization cutoff, and lease.

Eligibility Lease:
: The time-limited permission to rely on active lifecycle state.
  `validUntil` gives its source expiration; receiver policy can shorten
  it. It grants no resource permissions and does not extend token validity.

Lifecycle Registry:
: The Receiver's durable state store, independent of its SCIM resources.
  It retains lifecycle decisions and retirement protection for each
  qualified agent within the authorized Target Tenant.

Authorization Cutoff:
: A time watermark invalidating authorization derived from grants
  issued at or before that time. It survives reactivation and missed
  intermediate state changes.

Local Suspension:
: A resource-domain restriction maintained independently of the
  Lifecycle Authority's state. Upstream activation cannot clear it.

# Conformance and Trust Configuration {#conformance}

This document separates two layers:

| Layer | Contract |
|---|---|
| Lifecycle state application | Apply the State Record from {{AGENT-EVENTS}} through SCIM and SSF to a local registry; reconcile and recover |
| OAuth enforcement | Issuance-time interpretation of the cutoff, retained authorization provenance, resource enforcement modes, and denial bounds |

{{AGENT-EVENTS}} defines independent event conformance. Conformance to
this consuming profile requires both layers below; accepting an event
alone does not establish an OAuth enforcement guarantee.

A deployment claiming this profile MUST implement:

| Component | Required behavior |
|---|---|
| Lifecycle Authority and its connector | Issue ordered state records; provision through SCIM; transmit lifecycle SETs; reconcile delivery |
| Lifecycle Receiver | Maintain the independent registry and correlation; apply both bindings through common state processing |
| IdP grant issuer | Enforce lifecycle eligibility and the issuance-time contract in {{cutoff}} |
| RAS | Enforce eligibility at redemption and refresh; retain grant provenance; implement the configured enforcement mode |
| API | Apply the configured mode in {{api-enforcement}} and the Federation authorization rules |

This profile adds lifecycle checks to the applicable Federation profile.
It does not replace its client authentication, grant validation, actor
gate, or access-token protection requirements. A deployment MUST
establish applicability through trusted configuration, not infer it from
a token missing lifecycle information.

Before provisioning, the parties MUST configure:

* The governing IdP issuer and the permitted agent namespace.
* The authenticated SCIM connector and SSF Transmitter authorized for
  that namespace, and the receiver audience and Target Tenant.
* The enforcement mode for each API population and its timing parameters
  ({{parameters}}, {{api-enforcement}}).
* The RAS and APIs covered by the lifecycle enforcement contract.

The Receiver MUST authorize SCIM and SSF writers for the same namespace.
An event's signing issuer need not equal the governing IdP issuer; that
authority relationship MUST be configured. A valid signature or a SCIM
write permission for another tenant does not establish it.

This profile has one logical Lifecycle Authority per governed identity.
Multiple connectors MAY represent it, but MUST share its version
sequence and issuance cutoff. Independent writers and authority failover
without preserved state are outside this profile.

The lifecycle guarantee assumes that the Authority applies its committed
decision to all grant-issuing nodes before publishing disablement, that
issuers report actual issuance times within the configured clock bounds,
and that renewals reflect a current lifecycle decision rather than a
connector's old cached state. These are source-side trust assumptions;
receivers cannot establish them by validating a State Record. A
deployment that does not satisfy them is non-conformant, not a degraded
mode of this profile.

## Timing Parameters {#parameters}

All intervals are seconds. Configured limits are finite; derived bounds
are calculated from them. No parameter is learned from an incoming token
or State Record.

| Symbol | Meaning | Configured by / use |
|---|---|---|
| S | Maximum absolute clock error from a common time source | All parties; state validation and denial bounds |
| D | Maximum whole seconds a grant issuer can be ahead of the Authority, covering at least ceiling(2S) and rounding | Authority and Receiver; cutoff generation and validation |
| L | Maximum eligibility-lease interval | Receiver, agreed with Authority; effective lease deadline |
| E | Claimed maximum delay to make accepted restrictions or lease expiry effective throughout the RAS deployment | Receiver and RAS; deployment denial bound |
| T | Timeout from starting introspection to a usable result or decision | API; both introspection modes |
| C | Maximum reuse interval after receipt of an active introspection response | API; bounded-cache mode |
| J | Maximum access-token lifetime, `exp - iat` | RAS and API; expiring-JWT mode |
| P | Maximum expiration leeway | API; expiring-JWT mode |
| A | J + 2S + P: elapsed JWT acceptance bound after issuance | Derived |
| B | L + 2S + E: RAS stopping bound after Authority disablement, including lost delivery | Derived |

The denial guarantee depends on the deployment meeting its clock and
application-delay bounds; these are operational commitments, not values
that a peer can verify from a SET.

# Identity, Correlation, and Administrative Authority {#identity}

The qualified identity is the exact pair (`issuer`, `subject`) in the
State Record. The subject MUST be unique and non-reassignable across all
Governance Tenants sharing that issuer. A Governance Tenant or Target
Tenant does not add a component to the qualified identity.

For delegated access, `issuer` and `subject` MUST equal the validated
ID-JAG's `act.iss` and `act.sub`, respectively. The RAS MUST look up
lifecycle state by that pair in the grant's authorized Target Tenant,
not by the user's `sub`, the OAuth client, or the access-token issuer.

The Receiver MUST:

* Match both components exactly, without case folding or URI rewriting.
* Correlate the pair with at most one local agent principal in each
  Target Tenant.
* Reject attempts to replace either component of an existing correlation.
* Require explicit local administrative authorization to attach the pair
  to a pre-existing principal; matching names or email addresses is not
  sufficient.

SCIM `id` identifies the Receiver's local resource. `externalId` is a
provisioning correlation value with the scope defined by {{RFC7643}}.
Neither replaces the qualified identity. `agentUserName` and display
attributes are not federation identifiers.

Existing service principals MAY represent agents locally. Their local
identifiers and implementation types do not change the governed
identity. The SCIM Agent resource MUST be a management representation of
that same local principal, not a second authorization principal. The
Receiver maintains the mapping from its SCIM `id` to the existing
principal and applies lifecycle changes to that principal's
authorization.

This is local state; no cross-resource linking attribute is defined.
Mapping it to a different principal requires explicit administrative
correlation, not an ordinary synchronization update. The same rules
apply when the agent is an ID-JAG actor or, in a future WAG composition,
a self-acting subject ({{self-acting}}).

## Ownership, Groups, and Entitlements

Agent ownership and group membership use {{SCIM-AGENT}} and {{RFC7643}}.
Receivers SHOULD support those attributes for administrative
accountability and local policy. They MUST authorize their modification
independently of permission to deliver lifecycle state.

An owner is an accountable party, not automatically a delegator. An
owner change MUST NOT itself create user delegation, Client Association,
or resource permissions. Group membership has only the authorization
meaning assigned by resource-domain policy; this document defines none.

The Lifecycle Authority controls enterprise eligibility. The resource
domain controls local permissions and suspension. Effective eligibility
requires both. An upstream update MUST NOT clear a Local Suspension or
restore previously revoked resource permissions.

Effective eligibility, Local Suspension, and local permissions are not
observable through this SCIM extension. A returned `active: true`
reports the source's administrative status only; it is not an access
decision.

# Lifecycle State Application {#state-schema}

The Authority and Receiver MUST use the State Record, version
comparison, and transition rules defined in {{AGENT-EVENTS}}. This
profile adds the clock bounds, local registry behavior, and OAuth
effects below; it does not redefine the state members or event
semantics.

This document uses SCIM attribute names for registry state. For event input,
the Receiver MUST apply the mapping in {{AGENT-EVENTS}}: identity comes
from `sub_id`, `event_timestamp` maps to `assertedAt`, `authorization_cutoff`
maps to `authorizationCutoff`, and `valid_until` maps to `validUntil`.
Time arithmetic compares instants after conversion. An event has no nested
`state` object.

The Receiver MUST reject a cutoff later than `assertedAt + D`, using the
configured issuer-ahead bound in {{parameters}}. Descriptive SCIM edits
leave lifecycle state and its version unchanged.

## Eligibility Lease {#lease}

For active state, `validUntil` is an eligibility lease, not an event
expiration or a resource authorization. The Authority renews it from a
current lifecycle decision to maintain continuous eligibility; the
source trust assumption is stated in {{conformance}}.

The Receiver MUST set its effective lease deadline to the earlier of
`validUntil` and `assertedAt + L`. It MUST clamp an excessive interval
without rejecting the record or rewriting the source fields, and MUST
stop relying on active eligibility at that deadline, accounting
conservatively for clock error.

For disabled or retired state, `validUntil` and L MUST NOT delay,
prevent, or expire the restriction. Syntax, authority, ordering, and
cutoff checks still apply. Arrival time, replay, stream heartbeats, and
reads of a local SCIM representation MUST NOT renew the lease.

Lease expiration is intentionally reversible: an unexpired lease from a
newer active State Record can restore eligibility. It does not reverse a
disablement or cutoff invalidation. Local permissions and authorization
remain separate decisions in either case.

## Activation and Cutoff Application {#transitions}

Initial provisioning SHOULD use disabled state. Initial activation
requires explicit enterprise and local acceptance; resource creation
alone MUST NOT supply either decision.

The Authority MUST generate cutoff advances required by {{AGENT-EVENTS}}
using {{cutoff}}. If clock precision prevents a strict advance within
the configured bound, it waits before asserting the transition;
disablement still closes its issuance gate immediately.

# Receiver Lifecycle Registry {#registry}

The Receiver MUST maintain a durable lifecycle registry independently of
SCIM resource existence. Each entry is addressed by the qualified agent
identity within its authorized Target Tenant and retains:

* The highest accepted lifecycle version and complete applied State Record.
* State accepted through SSF but pending application, until applied or
  superseded by newer complete state.
* Permanent retirement protection.
* The local-principal and SCIM-resource mapping, when provisioned.

A state entry need not have a SCIM resource. Receiving an active record
MUST NOT create a local principal, local permissions, or delegation.
Provisioning adds an authorized mapping to an existing entry when one is
already present; it MUST NOT reset that entry's version, cutoff, or
lease.

Registry retention across resource deletion follows {{scim}}. No
database layout or registry API is prescribed.

Pending state exists only on the asynchronous SSF path; SCIM application
is synchronous. Until pending state is applied, the RAS MUST enforce the
more restrictive of applied and pending state: deny if either is
disabled, retired, or beyond its effective lease deadline, and use the
greater cutoff. Without applied state, pending active state cannot
establish eligibility. A pending reactivation or lease renewal cannot
relax applied restrictions.

## State Acceptance and Ordering {#ordering}

Both transport bindings MUST apply the State Record validation and
ordering rules in {{AGENT-EVENTS}}, with these application requirements:

1. Authorize the sender for the governing issuer and Target Tenant before
   selecting the registry entry.
2. Reject `assertedAt` more than 2S in the future and a cutoff beyond
   `assertedAt + D`. Apply the lease clamp in {{lease}}.
3. Include pending accepted state in the version comparison. Map stale,
   conflicting, or invalid input to the SCIM or SSF response rules below.
4. Persist accepted state. SCIM application is synchronous; SSF may
   acknowledge durable pending state. Application atomically advances
   the applied record and its RAS enforcement state.

The event specification's equality rule excludes `validUntil` for
non-active state. A valid snapshot beyond its effective lease deadline
can advance registry state without establishing eligibility.

# SCIM Provisioning {#scim}

The Receiver MUST implement Agent resources at `/Agents` using
{{SCIM-AGENT}} and the extension in {{scim-schema}}. It MUST publish the
extension at `/Schemas` and advertise it in the Agent ResourceType's
`schemaExtensions`. The extension is REQUIRED for resources governed by
this profile; it need not be required for unrelated Agent resources.

This profile raises Federation's provisioning SHOULD to a MUST for the
local representation required by lifecycle enforcement.

The required operations are POST, resource GET, filtered collection GET,
PUT, and DELETE under {{RFC7644}}. Receivers MUST support equality
filtering on both extension identity attributes and their conjunction.
PATCH and Bulk are OPTIONAL; if supported, they MUST preserve the
atomicity and ordering rules below.

## Applying the SCIM Representation {#scim-schema}

The Receiver MUST use the `GovernedAgentLifecycle` extension defined by
{{AGENT-EVENTS}}, including its attribute types, case handling, conditional
`validUntil` requirement, and immutable identity fields. The extension
represents applied registry state, whether received through SCIM or SSF.

The Receiver MUST enforce uniqueness of the qualified agent identity
within each Target Tenant. Neither individual identity attribute is
independently unique.

## Creation and Existing Records

The connector MUST supply the Agent core's required attributes and the
complete extension. `active` MUST be `true` exactly when extension
`status` is `active`; inconsistent input is `400` with `invalidValue`.
The core attribute represents source administrative status, not the
result of lease enforcement or Local Suspension.

The Receiver MUST check its correlation and retirement records before
creation. A second Agent resource for the same qualified identity in the
Target Tenant is `409` with `uniqueness`. This requirement applies
independently of `agentUserName` uniqueness.

POST for an identity protected by a retirement tombstone receives `409`
with a `detail` string and no `scimType`, even if no resource remains.

A non-retired registry entry without an Agent resource is not a
duplicate resource. Authorized creation can establish the local
correlation using the same version and identical state retained from an
earlier event, without renewing its lease. A stale creation attempt
receives `409`; the connector obtains current state from its Authority
before retrying.

Malformed extension attributes use `400` with `invalidValue`; attempts
to change immutable identity attributes use `400` with `mutability`.
Other SCIM errors retain their meanings from {{RFC7644}}.

After an uncertain POST result, the connector MUST query by the
qualified identity before retrying creation. It MUST NOT create a second
principal under a different name to bypass a conflict.

Explicitly authorized correlation with an existing local principal MAY
occur before POST. The resulting Agent resource represents that
principal; the Receiver MUST NOT silently merge principals during
synchronization.

## Resource Updates and Lifecycle Versions {#scim-updates}

A SCIM write carrying the extension MUST submit its State Record to the
registry under {{ordering}}. A lower version or a conflicting equal
version receives `409` with a SCIM `detail` string and no `scimType`. An
invalid transition, decreasing cutoff, or cutoff beyond `assertedAt + D`
receives `400` with `invalidValue`. These errors reject the entire
write, including any accompanying descriptive edits.

An equal version with identical state is a lifecycle no-op, not a no-op
for the whole SCIM request. Authorized changes to `displayName` and
other non-lifecycle attributes MUST be applied when the write otherwise
succeeds, without changing the State Record, renewing its lease, or
emitting a lifecycle event. This also handles a SCIM representation
arriving after an event with the same state version. If that state is
pending from SSF, the Receiver MUST synchronously apply it and the
authorized SCIM changes before returning success.

A connector behind an SSF-delivered version reads and echoes the current
State Record for a descriptive PUT; it does not reuse its stale copy. If
another event wins the race, the connector reads again after the
conflict.

SCIM resource concurrency is independent of lifecycle ordering. Receivers
SHOULD support resource ETags and `meta.version` under {{RFC7644, Section
3.14}}; clients SHOULD use `If-Match` to avoid overwriting concurrent
metadata changes. Failed conditions return `412` under {{RFC7644, Section
3.12}}. Lifecycle `version` MUST NOT substitute for an HTTP entity tag.

PUT MUST contain the complete extension. A supported PATCH changing a
lifecycle attribute or core `active` MUST provide a complete resulting
State Record and consistent `active` value in one atomic request. A
PATCH changing only non-lifecycle attributes MAY omit the extension; it
MUST leave the registry unchanged. Removing the extension or a required
state attribute is `400` with `invalidValue`.

The Receiver MUST make accepted registry state and its RAS enforcement
state effective before reporting SCIM success. GET MUST project that
applied state into the extension and core `active` value, even if it
arrived by SSF. An unapplied event cannot appear as applied SCIM state.
Resource modification metadata, including an ETag when supported, MUST
reflect changes to the representation through either binding.

## Deletion and Retained State

Authorized DELETE follows {{RFC7644, Section 3.6}} regardless of
lifecycle status. Before success, the Receiver MUST remove the
representation and its local correlation and invalidate authorization
derived through that correlation. Existing API access ends within the
configured enforcement mode's residual bound. Deletion does not retire
the enterprise identity.

The Receiver MUST retain registry state, including the highest version,
cutoff, and any terminal retirement protection. Recreating a non-retired
representation requires explicit correlation and current eligible state
before access can resume; it cannot revive invalidated authorization.

# Lifecycle Signals {#signals}

## Target Tenant and Stream Binding {#stream-binding}

Each lifecycle stream MUST be bound by trusted administrative
configuration to exactly one governing issuer namespace and one Target
Tenant at the Receiver. The binding is associated with the SSF stream ID
and its stream configuration; this profile adds no SSF configuration
member.

The stream configuration and each SET `aud` MUST contain exactly one
audience value assigned exclusively to that issuer-namespace and Target
Tenant pair. Receivers MUST accept either a string or a one-element
string array.

For push delivery, the authenticated delivery context (endpoint and
credential association) MUST identify one configured stream before token
claims are used. A shared endpoint needs distinct credential
associations when necessary to distinguish streams. For polling, the
authenticated poll request identifies the stream. The Receiver MUST
then:

1. Validate the SET issuer, signature, and audience against that stream.
2. Require `sub_id.iss` to equal the stream's bound governing issuer.
3. Use the stream's bound Target Tenant for the registry lookup.

Ambiguous stream selection or a mismatch MUST be rejected. Neither the
agent identifier nor an unvalidated audience can select another tenant.

The SCIM connector's authorization and endpoint context MUST resolve the
same Target Tenant. Changing a stream's tenant or issuer-namespace
binding requires a new stream and audience value; replay on another
binding MUST be rejected. The Target Tenant scopes local correlation,
not the qualified identity or its source version sequence.

## Applying Lifecycle Events

The Transmitter and Receiver MUST implement the Agent State Changed
event defined in {{AGENT-EVENTS}}, including its payload, subject
matching, and validation rules. This profile adds the stream-to-tenant
binding above and the registry and enforcement requirements below. It
defines no event identifier or alternative event payload.

## Delivery and Acceptance

Both parties MUST support SSF push delivery using {{RFC8935}}. SSF poll
delivery {{RFC8936}} MAY additionally be supported. Mandatory push
support is this profile's requirement, not a requirement of base SSF.
Event discovery follows {{AGENT-EVENTS}} and SSF.

The Authority MUST arrange delivery of each new State Record through
SCIM or SSF, and MUST enqueue a lifecycle event on every status or
cutoff change for each configured target stream.

When a stream is paused or delivery fails, the Transmitter retains the
event for its configured retry period and the connector uses SCIM
reconciliation. Expiration of that period does not remove the obligation
to reconcile current state. SCIM and SSF can arrive in different orders;
both apply the common ordering rules in {{AGENT-EVENTS}}.

Receivers MUST durably deduplicate SETs by Transmitter issuer and `jti`
for the configured delivery retry period. Source-version processing
remains necessary after the deduplication record expires and across SCIM
delivery of the same state. Neither `jti` nor SET `iat` is a state
ordering mechanism.

Event acknowledgments and errors follow {{AGENT-EVENTS}}. This profile
additionally requires an administrative diagnostic for conflicting
equal-version records.

A delivery acknowledgment confirms durable acceptance for processing,
not completed RAS or API enforcement. Pending restrictions apply under
{{registry}}; E bounds the delay until restrictions are effective
throughout the Receiver and RAS deployment ({{parameters}}). API denial
then follows the configured mode's residual bound. SCIM success requires
completed RAS application under {{scim-updates}}, not expiration of every
API cache entry or offline token.

# Reconciliation and Recovery {#recovery}

The connector MUST maintain the mapping from each source identity to the
Receiver's SCIM resource ID and MUST periodically reconcile it.
Reconciliation uses ordinary SCIM GET and PUT; this document defines no
snapshot or cursor API.

For example, this is one decoded SCIM `filter` value. Unfold backslash
continuations under {{RFC8792}} before use; remaining line breaks stand
for whitespace. Percent-encode the complete value in the query
parameter:

~~~ text
=============== NOTE: '\' line wrapping per RFC 8792 ================

urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent:\
issuer eq "https://idp.example/" and
urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent:\
subject eq "agent-42"
~~~

The query runs under the connector's authorized Target Tenant. The
extension URI qualifies each attribute as specified by {{RFC7644}}.

For each identity assigned to a Target Tenant, the connector:

1. Queries its known resource ID, or filters by the qualified identity
   when the ID is unknown or the resource is missing.
2. Compares the returned State Record with the Authority's current record.
3. Creates a missing authorized resource or sends the current complete
   record when the Receiver is behind.
4. Investigates a Receiver version ahead of the source; it MUST NOT reset
   the sequence or overwrite state with a lower version.
5. Reconciles descriptive attributes separately under SCIM concurrency
   rules, even when lifecycle versions match. A descriptive difference
   does not require a new State Record.

An absent identity in a partial inventory MUST NOT be treated as
retired. The Authority MUST retain explicit retirement records and retry
them until affected receivers have applied them. Retirement tombstones
also protect against older backups and late provisioning requests.

Recovery uses the registry ordering in {{ordering}}; it MUST NOT depend
on observing every intermediate transition.

After loss of correlation or lifecycle state, the Receiver MUST deny
affected authorization until trusted reconciliation completes. Restoring
an old backup MUST NOT renew an eligibility lease or bypass retained
retirement protection. Restoring an Authority without its version and
issuance watermark requires administrative recovery, not a sequence
reset.

# OAuth Enforcement Layer {#enforcement}

This layer applies lifecycle state to ID-JAG and derived authorization
through issuance-time checks, retained provenance, and API denial
bounds.

## Authorization Cutoff and Issuance {#cutoff}

ID-JAG requires `iat` as a NumericDate {{ID-JAG, Section 3.1}}; RFC 7519
permits fractional values. Issuers SHOULD use whole seconds. For this
profile's cutoff processing, the issuance second is `floor(iat)`, the
greatest integer not exceeding the validated value. The RAS MUST compare
that value with the cutoff converted to NumericDate, without positive
clock-skew tolerance {{RFC7519}}.

When advancing the cutoff, the Authority MUST set it to its current
whole-second time plus D, strictly above the previous cutoff. This covers
all grants issued before the committed transition without tracking the
greatest `iat` across issuing nodes. The source-side assumptions in
{{conformance}} still require the issuance gate to close before publication.

After activation, the issuer MUST issue only grants whose issuance
second is strictly later than the cutoff. Until its actual clock clears
the cutoff, issuance waits or fails. A cutoff ahead of the Authority's
clock therefore creates a bounded activation delay; it does not justify
postdating grants.

This issuance-time contract adds to ID-JAG and depends on the trust
assumptions in {{conformance}}.

## Eligibility and Existing Authorization

The RAS MUST deny new grant redemption, access-token issuance, and
refresh unless all of the following hold:

* The qualified agent has an authorized local correlation.
* Its applied state is `active` and within its effective lease deadline,
  with no stricter pending restriction under {{registry}}.
* No applicable Local Suspension or terminal tombstone exists.
* The original IdP grant's issuance second clears the effective cutoff.
* The Federation profile's client, user, tenant, authority, and actor
  authorization requirements succeed.

On disablement or retirement, the RAS MUST invalidate existing derived
authorization. When the cutoff advances, it MUST invalidate
authorization whose original grant issuance second is at or before the
new cutoff. These invalidations are permanent: subsequent activation
cannot reverse them. At each RAS component applying the restriction,
they take effect with that application; pending-state enforcement and
the deployment-wide delay E follow {{registry}} and {{signals}}. Cached
decisions and offline access tokens cease API use within the applicable
mode's bound below.

A token request failing these lifecycle checks uses `invalid_grant` under
{{RFC6749}} and the applicable grant profile. Introspection returns
`active: false` under {{RFC7662}}. Error descriptions SHOULD avoid
disclosing lifecycle status or the existence of another tenant's agent.

## Grant Validation and Retained Provenance {#provenance}

The RAS MUST reject a grant that fails base `iat` validation, including
a missing or non-numeric value, or whose issuance second does not clear
the effective cutoff, using `invalid_grant`. A fractional `iat` is not
itself an error.

The RAS MUST retain the qualified identity, authorized Target Tenant,
and original grant issuance second with every authorization derived from
the grant, including access tokens and refresh authorization. Refresh,
rotation, and token issuance MUST NOT replace that provenance with a
newer local timestamp. This is an additional RAS requirement of this
companion, not an implied property of OAuth refresh or of an access
token's own `iat`. The RAS MUST be able to locate or collectively
invalidate derived authorization by qualified identity and Target
Tenant; no particular index is prescribed.

No new token claim or storage format is required. The RAS can retain the
context in its authorization record.

### Migration of Existing Authorization

Before applying this profile to an existing token population, the RAS
MUST either recover its original validated grant context or require a
new ID-JAG and new authorization. It MUST NOT infer missing provenance
from an access token's issue time, provisioning time, or current agent
state.

Legacy refresh authorization without recoverable provenance MUST NOT
mint tokens in the new population. Deployments MAY drain existing access
tokens under their previous policy before enabling the lifecycle
guarantee. The new guarantee begins only after those tokens and any
cached active results can no longer authorize requests. Migration does
not silently grandfather untracked tokens into a stronger bound.

## API Enforcement Modes {#api-enforcement}

The RAS and API MUST configure one of the following modes for each
governed token population. These are deployment modes, not new OAuth
profile URIs or assurance levels. A token or validation failure MUST NOT
select a weaker mode. All modes retain Federation's token protection and
actor gate.

| Mode | Resource behavior | Denial bound from Authority disablement |
|---|---|---|
| Online introspection | Introspect each request; no reuse | B + T |
| Bounded introspection cache | Reuse active responses for at most C, within token expiry | B + T + C |
| Expiring JWT | Offline validation; acceptance lifetime bounded by A | B + A |

B includes lost delivery; T, T + C, and A are the respective residual
bounds after RAS enforcement. Parameter definitions are in
{{parameters}}.

Both introspection modes use authenticated {{RFC7662}} processing.
Before returning `active: true`, the RAS MUST apply current eligibility
and retained-provenance checks in addition to normal token validation.
JWT or opaque access tokens can use these modes.

### Online Introspection

The API MUST introspect the access token on every request and MUST NOT
reuse an active response. A result or decision after timeout T MUST NOT
permit the request; the API denies or starts another check. An inactive
response or failed check cannot permit the request. This mode narrows
Federation's permitted introspection caching.

### Bounded Introspection Cache

The API MAY reuse an active response for at most C after its receipt,
provided that response arrived within T of starting introspection. It
MUST check both cache age and token expiry at each authorization
decision. The cache deadline MUST NOT extend beyond `exp`, and a
response without `exp` MUST NOT be reused, retaining Federation's
existing restriction.

Cache hits MUST NOT restart the interval. After expiry of the cached
result, failed revalidation or timeout cannot authorize use of stale
state. A newly obtained inactive response MUST invalidate the cached
active result. This mode makes Federation's configurable cache reuse
limit explicit.

### Expiring JWT

JWT validation follows {{RFC9068}} and Federation's JWT processing. The
RAS MUST limit each token's `exp - iat` to a configured maximum J. The
API MUST reject a token exceeding J with `invalid_token`, verify
expiration at each decision, and apply at most its configured expiration
leeway P. Refresh and repeated grant redemption remain subject to
current lifecycle state at the RAS.

In this mode the API performs no lifecycle lookup; it relies on the
RAS's issuance checks and bounded token lifetime. A previously issued
token can remain usable until expiry after RAS revocation. A includes
clock error and leeway ({{parameters}}); future dating cannot extend J.
Direct lifecycle event processing at APIs is outside this profile.

### Common Resource Requirements

The API MUST continue enforcing token authority, user authorization, and
the actor gate from {{FEDERATION}}. An active response or valid signature
does not itself authorize an operation. Invalid-token responses follow
{{RFC6750}} and the applicable access-token protection specification.

The bounds concern new authorization decisions, not rollback of
completed operations or cancellation of work already admitted.
Long-running sessions need separate revalidation or cancellation rules.
Where APIs use different modes, the deployment-wide bound is the longest
applicable bound.

## Denial Bounds and Loss of Delivery {#freshness}

An expired eligibility lease blocks new RAS issuance, refresh, and
active introspection. Cached results and offline tokens follow their
configured mode's residual acceptance bound. When a newer active lease
restores eligibility, still-valid authorization MAY be used only if its
original grant clears the cutoff and has not otherwise been revoked.

Under the source-side assumptions in {{conformance}}, B bounds RAS
stopping after disablement even if notification is lost. Notification
can shorten that interval. The mode table in {{api-enforcement}} adds
the residual API acceptance bound, including clock uncertainty for JWTs.

Deployments MUST document their mode, limits, timeouts, and outage
behavior. They MUST NOT claim a shorter bound based solely on grant
lifetime or successful event delivery.

# Relationship-Specific Changes {#relationship-changes}

Agent-wide lifecycle state is deliberately distinct from changes to an
individual relationship:

| Change | Required boundary |
|---|---|
| Disable one Identity Binding | Stop new grants through that binding; other approved bindings remain independent |
| Withdraw a Client Association | Stop the affected client use; do not infer that the agent has been disabled |
| Revoke one user's delegation | Affect that delegation; do not disable unrelated users or self-acting authority |
| Revoke a workload credential | Apply credential validation and IdP policy; do not automatically retire the governed principal |
| Change ownership or groups | Apply the authorized administrative or local policy change; do not infer new delegation |

The IdP applies the first three boundaries under {{FEDERATION}}. This
companion does not define portable events identifying those
relationships. Selective revocation of their existing downstream tokens
needs issuance provenance and an agreed relationship identifier; the
agent's `act` identity alone is insufficient.

OAuth token revocation {{RFC7009}} remains available to revoke a known
token at its issuing server. It neither identifies every authorization
derived from an Agent Principal nor distributes principal lifecycle state
across domains. It complements this profile; it does not replace its
cutoff, ordering, or propagation contract.

A WISE or other upstream signal MAY inform the Authority's decision. The
Authority MUST evaluate its source, affected credential or workload, and
Identity Bindings before producing agent-wide lifecycle state. Receivers
MUST NOT reinterpret such upstream subjects as governed identifiers
without the federation mapping.

## Self-Acting Access {#self-acting}

The lifecycle identity is independent of the authorization flow. The
intended {{WAG}} composition correlates the same Agent Principal with the
same local agent principal used for delegated access.

Delegated access preserves the IdP-qualified actor in `act`; self-acting
access represents the correlated local principal as the resource-domain
subject. These representations do not make their authority
interchangeable.

This profile claims no WAG wire conformance. A future composition needs
an authenticated governed subject and issuance time to apply the same
cutoff and provenance checks. It does not need a separate agent
lifecycle.

# Security Considerations

## Lifecycle Writers and Token Confusion

A lifecycle writer can disable agents or renew eligibility. Writer
authority comes from {{conformance}} and {{stream-binding}}, never an
unverified payload, supplied URL, or display name.

SETs are not OAuth grants or access tokens. Receivers MUST keep
lifecycle event validation separate from those token classes. The
`secevent+jwt` type and absence of `exp` support this separation; they
do not replace signature, issuer, audience, and writer authorization
checks.

## Rollback, Reactivation, and Compromised Authorities

Rollback and reactivation protection depend on retained versions and
cutoffs. Accepting a higher version cannot excuse a decreasing cutoff.

An authorized source that lies about status, issuance times, or lease
decisions can defeat the enterprise lifecycle guarantee. Local
restrictions remain independent and SHOULD be available for incident
containment. This profile does not protect against compromise of the
governing IdP itself.

## Availability and Administrative Evidence

Short eligibility leases and online introspection limit stale access but
increase load and sensitivity to outages. Cached introspection and
expiring JWTs trade longer residual access for fewer online checks.
Operators SHOULD choose the mode, lease interval L, and delivery
capacity together, and monitor renewal lag, conflicts, and enforcement
delays.

Deployments accepting hours of residual eligibility can choose L from
several hours to a day; shorter denial objectives require shorter
leases. This is operational guidance, not a default or a token-lifetime
requirement.

Maintaining N active agents with lease interval L requires more than N/L
renewed state assertions per second when allowing delivery margin. For
100,000 agents and five minutes, the nominal minimum is about 333 per
second per target domain, before retries. SSF delivery uses signed SETs;
SCIM renewals can use existing Bulk support when available. Neither
delivery choice removes the need for a current source eligibility
decision. Staggering renewals avoids synchronized bursts. Longer
intervals reduce traffic but increase the stated disablement bound; a
transmitter heartbeat alone cannot renew every agent's eligibility.

Audit records SHOULD distinguish source decision, receipt, application,
and API denial times. A transport acknowledgment is not evidence that
every API has stopped accepting affected authorization.

# Privacy Considerations

Stable governed identifiers enable correlation across users, resources,
and time. Lifecycle streams SHOULD be limited to resource domains that
have provisioned or otherwise authorized correlation for the agent.
Writers MUST be authorized for the Target Tenant before disclosure.

This profile does not require transmitting external workload
identifiers, credential identifiers, user delegations, owner email
addresses, or incident details in events. Implementations SHOULD
minimize such additional data. Retirement tombstones retain only the
identity and synchronization data needed to prevent reuse; other
attributes can follow local retention policy.

# IANA Considerations

This document requests no IANA registrations. {{AGENT-EVENTS}} defines the
event URI and requests registration of the SCIM schema.

--- back

# Shared Delegated Federation Walkthrough {#example}

This non-normative walkthrough composes the dedicated-client exchange
in {{FEDERATION}} with the events in {{AGENT-EVENTS}} and this lifecycle
profile. It is a protocol review scenario, not an executed implementation
or a set of cryptographic test vectors. The checklist in
{{acceptance-checklist}} identifies observable acceptance results.

## Shared Configuration

All times below are UTC on September 17, 2026. The parties configure
bound governed agent access, DPoP-protected API tokens, and online
introspection on every API request, including when the token is a JWT.
Local actor policy permits the example operation before disablement.

| Coordinate | Value |
|---|---|
| Governing IdP issuer | `https://idp.example/` |
| Agent Principal subject | `agent-42` |
| RAS issuer | `https://ras.example/` |
| IdP / RAS OAuth clients | `analysis-client` / `analysis-api` |
| User at IdP for RAS / at API | `alice-ras` / `user-108` |
| Target Tenant | `acme-data` |
| Resource | `https://api.example/tenants/acme-data/` |
| Scope | `files.read` |
| Grant and access-token proof key | K, with thumbprint `JKT_K` |
| RAS-local agent representation | SCIM resource `local-108` |

The configured Identity Binding maps the authenticated dedicated client
to `agent-42`; Client Association and delegation for Alice are separately
approved. Alice's ID Token has audience `analysis-client` and remains
valid through the issued grant's expiration. Credential and signature
values in the examples are placeholders.

For this example, S = 1 second, D = 2 seconds, L = 300 seconds,
E = 2 seconds, and T = 2 seconds. The short lease illustrates lost-event
handling; it is not a recommended deployment interval. The lifecycle
identity equals the ID-JAG actor exactly. SCIM `local-108` is neither
Alice's `user-108` nor the federated agent subject.

## Provision the Agent

The connector sends a disabled resource. A prior local administrative
decision permits creating the corresponding principal.

~~~ http-message
POST /scim/v2/Agents HTTP/1.1
Host: ras.example
Authorization: Bearer SCIM_CONNECTOR_TOKEN
Content-Type: application/scim+json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:Agent",
    "urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent"
  ],
  "agentUserName": "analysis-agent-42",
  "displayName": "Data Analysis Agent",
  "active": false,
  "urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent":
  {
    "issuer": "https://idp.example/",
    "subject": "agent-42",
    "version": "40",
    "status": "disabled",
    "authorizationCutoff": "2026-09-17T12:00:02Z",
    "assertedAt": "2026-09-17T12:00:00Z"
  }
}
~~~

The request is authorized for Target Tenant `acme-data`. The Receiver
returns `201 Created`, a `Location` identifying
`https://ras.example/scim/v2/Agents/local-108`, and the created resource
including `id: "local-108"`. The connector retains that location. The
agent remains ineligible until both enterprise and local activation
conditions hold.

## Activate and Exchange

At 12:01:00 UTC the Authority issues version 41 with `status: "active"`,
cutoff 12:01:02, and `validUntil` 12:06:00. The connector PUTs the
complete resource with `active: true`. The Receiver applies it and
returns `200 OK`.

At 12:01:03, the client sends Federation's exchange request with Alice's
ID Token, a fresh `private_key_jwt` assertion, and a DPoP proof using K.
It sends no actor-token parameters. The IdP validates the credentials,
resolves the Agent Principal, and checks Client Association, delegation,
target authority, and current lifecycle eligibility.

The resulting `grant-1` has `iat=1789646463` (12:01:03),
`exp=1789646763` (12:06:03), and the Federation example's user, actor,
resource, client, scope, and `cnf.jkt` values. Its issuance second clears
the cutoff. An `iat` at 12:01:03.5 also clears it; one at 12:01:02.9
does not, because its issuance second equals the cutoff.

## Redeem and Call the API

At 12:01:04, `analysis-api` authenticates to the RAS and redeems
`grant-1` with a fresh proof using K. The RAS applies both profiles:

* Federation validates the grant and proof, translates Alice to
  `user-108`, correlates `agent-42` with `local-108`, and applies the
  actor gate and resource policy.
* Lifecycle verifies active state, its lease, local eligibility, and
  `floor(grant.iat) > authorizationCutoff`.

The RAS issues Federation's `access-1`, expiring at 12:11:04, preserving
the IdP-qualified `act` and binding the token to K. It retains original
grant issuance second `1789646463` with that authorization; the access
token's `iat=1789646464` does not replace it.

At 12:01:08, the client requests `report-7` with that token and a fresh
DPoP proof. The API introspects, validates the token/proof context, and
checks user authority, the actor gate, and Target Tenant. A valid JWT
signature does not skip introspection in this configured mode.

Neither grant nor access-token expiration is an eligibility lease.
The later token expiration does not permit the RAS to return an active
introspection result after lifecycle eligibility is lost.

## Optional RAS Refresh Branch

The base walkthrough issues no refresh token. In a separate run with
explicit RAS refresh policy, the RAS binds refresh authorization to K
and retains the same user, actor, client, tenant, resource, authority,
profile, and original grant issuance second. It sets Federation's
finite absolute authorization expiration and inactivity limit.

A permitted refresh at 12:01:30 can issue a new access token, but its
new issue time cannot replace `1789646463` in lifecycle provenance.
Disablement below invalidates both authorizations. Refresh cannot
renew a lease or establish a new IdP authorization decision.

## Disable Through a Signal

At 12:02:00 the Authority commits disablement, closes issuance at every
IdP grant issuer, and publishes version 42 under {{conformance}}.
Its stream is administratively bound to issuer `https://idp.example/` and
Target Tenant `acme-data`, with the exclusive audience
`https://ras.example/lifecycle/acme-data/idp-example`. The Transmitter
sends the event defined in {{AGENT-EVENTS}} with disabled state version
42, `event_timestamp` corresponding to 12:02:00, and
`authorization_cutoff` corresponding to 12:02:02. Its examples show the
decoded SET. The stream audience identifies the receiving context; the
payload identifies the Agent Principal.

The Receiver durably accepts version 42 and acknowledges delivery.
Pending restrictions apply immediately where evaluated; enforcement
throughout the RAS completes within E. After application, redemption
and refresh fail with `invalid_grant`; introspection of either previously
issued token returns `{"active":false}`. The API denies requests using
that result. An introspection decision already in flight remains
subject to timeout T; the delivery acknowledgment alone is not proof
that every API has denied access.

## Reactivate or Recover a Lost Event

At 12:03:00, an independently authorized reactivation creates version 43,
cutoff 12:03:02, and a new lease ending at 12:08:00. Once it is applied,
a new grant issued at 12:03:03 can qualify. `grant-1` and its derived
refresh authorization cannot: their retained issuance second precedes
the new cutoff even though `grant-1` has not yet expired.

The same result holds if the Receiver never received disabled version
42. Version 43 is a complete snapshot carrying the advanced cutoff.
Any cached or offline acceptance remains subject to the applicable API
mode's residual bound; reactivation does not extend it.

In a separate lost-delivery run, neither version 42 nor a later version
arrives. The last active lease ends at 12:06:00. The Receiver stops
relying on it without needing a disablement event. A later lease renewal
can restore eligibility only under {{freshness}}; it cannot undo an
observed revocation or cutoff invalidation.

## Declared Denial Bounds

The configured values give B = L + 2S + E = 304 seconds. From Authority
disablement, the online-introspection bound is B + T = 306 seconds,
including loss of notification. Delivered notifications can shorten
that interval. This is a worst-case deployment bound, not a claim that
the particular lease above lasts 304 seconds after disablement.

Alternative runs retain the same identity and grant processing:

| API mode | Additional limits | Worst-case denial bound |
|---|---|---|
| Online introspection | T = 2 seconds | 306 seconds |
| Bounded cache | T = 2, C = 30 seconds | 336 seconds |
| Expiring JWT | J = 600, P = 1 second; A = 603 seconds | 907 seconds |

These bounds concern new API authorization decisions. They do not
cancel work already admitted. An implementation exercising one mode
has not demonstrated the behavior of another.

## Acceptance Checklist {#acceptance-checklist}

The following is a manual review and deployment-validation checklist,
not a claim that tests have been executed. All unrelated credentials
and policy checks succeed in each negative case.

| Check | Expected observation |
|---|---|
| Identity join | ID-JAG `act`, event `sub_id`, and SCIM extension identify exactly (`https://idp.example/`, `agent-42`) |
| Tenant isolation | Wrong stream audience, governing issuer, or Target Tenant is rejected before changing the registry |
| Provisioning boundary | A valid active event without an authorized local correlation does not enable redemption |
| Grant binding | Redemption with a key other than K fails even while the agent is active |
| Actor preservation | The RAS translates Alice's subject but preserves the qualified actor; `local-108` never replaces `act.sub` |
| Refresh provenance | A refreshed token retains the original grant issuance second and becomes inactive after the same cutoff advance |
| Source coordination | No new IdP authorization succeeds after committed disablement; no renewal is produced from stale pre-disablement state |
| Publication order | The disabled snapshot is published only after the IdP issuance gate closes; reactivation does not postdate grants to clear its cutoff |
| Enforcement milestones | Record acceptance, completed RAS application, and API denial separately; an acknowledgment alone does not satisfy the denial bound |
| Migration | Existing authorization without recoverable grant provenance cannot enter the lifecycle-governed population |

Source coordination requires observation of the Authority and issuing
nodes; it cannot be established from SET contents. Clock accuracy,
application delay, and API timeout/cache behavior require operational
measurement before a deployment claims the calculated bounds.

### Ordering and Recovery Cases

| Subsequent input | Result |
|---|---|
| Delayed SCIM PUT carrying active version 41 | `409`; disabled version 42 remains in effect |
| Authorized SCIM PUT with identical state 42 and a new display name | Descriptive edit applies; lifecycle version, cutoff, and lease remain unchanged |
| Descriptive edit with a stale `If-Match`, when ETags are supported | `412`; no change |
| Retransmission of event 42 | Acknowledged without renewing the lease or changing state |
| Applied active 41 with pending disabled 42 | RAS denies new authorization; API residual bounds still apply |
| Applied disabled 42 with pending active 43 | RAS denies until reactivation is applied |
| Different cutoff or status using version 42 | Rejected and diagnosed as a conflict |
| Version 42 differing only in an inactive `validUntil` | Duplicate; ignored member does not change eligibility |
| SCIM PUT matching SSF-pending version 42 | State and authorized edits applied synchronously before success |
| POST against a retired identity's tombstone | `409`; no resource created |
| DELETE of the disabled representation | Correlation removed; registry state retained |
| Authorized active version 43 with cutoff 12:03:02 | Grants with issuance seconds after the cutoff can qualify; old tokens stay invalid |
| Version 43 delivered without version 42 | The newer cutoff still rejects the grant issued at 12:01:03 |
| No update or renewal after active version 41 | Authorization is denied when its eligibility lease ends |
| Retired version 44 followed by an active version 45 | Invalid transition; retirement remains terminal |

In bounded-cache mode an earlier active introspection result may still
be used within C; in expiring-JWT mode the API can accept the old token
until its bounded expiry. Neither mode allows RAS refresh after the
disablement is applied. Their longer bounds are explicit in
{{freshness}}.

# Relationship to Event Specifications

This profile consumes the lifecycle snapshot from {{AGENT-EVENTS}}.
That specification owns event definitions and their coordination with
{{CAEP}}, {{WISE}}, and {{RISC}}; this document does not extend their event
vocabularies. A future binding to existing SCIM Events would likewise be
specified separately before this profile could claim support for it.

The essential consumer requirements are authoritative agent correlation,
shared state ordering, eligibility-lease enforcement, and application of
the cutoff to retained authorization. A different event carrier cannot
silently weaken those requirements or substitute a resource ETag for the
lifecycle version.

# Document History

Initial version.
