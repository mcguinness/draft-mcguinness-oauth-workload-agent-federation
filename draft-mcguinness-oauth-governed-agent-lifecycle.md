---
title: "A SCIM and Shared Signals Profile for Governed Agent Lifecycle"
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
  RFC9493:
informative:
  RFC6755:
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

This document defines provisioning and lifecycle management for the
stable, issuer-qualified principals established by Governed Agent
Federation. It profiles SCIM Agent resources for correlation with
resource-local principals and defines a Shared Signals event carrying
the same authoritative lifecycle state.

The profile specifies disablement, reactivation, retirement, update
ordering, recovery, and enforcement against new and existing OAuth
authorization. Lifecycle changes do not establish client authority,
user delegation, or resource permissions. No new workload credential
or event-delivery protocol is defined.

--- middle

# Introduction

Governed Agent Federation {{FEDERATION}} separates agent identity,
client authority, user delegation, and resource authorization. It
identifies an agent by the pair (IdP issuer, Governed Agent identifier),
independently of the workload credentials used to establish it.

For delegated access, the governed identity is the actor in an Identity
Assertion JWT Authorization Grant (ID-JAG) {{ID-JAG}}. This companion uses
Security Event Tokens (SETs) {{RFC8417}} and the Shared Signals Framework
(SSF) {{SSF}} to convey lifecycle changes to the resource domain.

Resource domains also need to provision that principal and respond to
changes in its eligibility. Creating a directory record does not grant
access. Disabling a record does not, by itself, invalidate issued tokens.
Delivering a security event does not demonstrate that an API enforced it.

This profile connects those operations:

~~~
 Enterprise IdP                         Resource domain
 +----------------------+               +--------------------+
 | Governed Agent       | -- SCIM ----> | Correlated local   |
 | Lifecycle Authority  | -- SET/SSF -> | agent + lifecycle  |
 +----------------------+               +---------+----------+
                                                  |
                                          +-------v-------+
                                          | RAS issuance, |
                                          | refresh, and  |
                                          | introspection |
                                          +-------+-------+
                                                  |
                                          +-------v-------+
                                          | API request   |
                                          | authorization |
                                          +---------------+
~~~
{: #lifecycle-model title="Provisioning and lifecycle enforcement"}

SCIM supplies the durable resource interface. Shared Signals supplies
timely notification. Both carry one versioned state, so delayed delivery
cannot reverse a newer change. A finite validity interval bounds reliance
on active state when neither channel delivers an update.

## Scope and Relationship to Other Specifications

This revision defines a complete IdP-to-resource-domain path:

* Provision or explicitly correlate a Governed Agent with a local record.
* Synchronize active, disabled, and retired state.
* Apply changes to grant redemption, access-token issuance, refresh, and
  API authorization.
* Recover from duplicate, delayed, or missed delivery.

It reuses the Agent resource in {{SCIM-AGENT}}. The extension defined here
adds federation identity and synchronization semantics. It does not
replace the Agent resource or define a general agent inventory.

{{SCIM-GOVERNANCE}} describes broader administrative lifecycle states.
{{WISE}} describes changes to workloads, credentials, and trust material.
{{CAEP}} describes continuous-access events. Those mechanisms can supply
inputs to an authority's decision. The state defined here expresses the
result for a Governed Agent and the receiver obligations that follow.

Platform-to-IdP enrollment, Identity Binding administration, individual
delegation revocation, task cancellation, runtime instance lifecycle,
and risk scoring are outside this revision. Their boundaries are stated
in {{relationship-changes}}.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

OAuth terms follow {{RFC6749}}. Governed Agent, Identity Binding, Client
Association, Governance Tenant, and resource authorization server (RAS)
follow {{FEDERATION}}. SCIM terms follow {{RFC7643}} and {{RFC7644}};
Transmitter, Receiver, and stream follow {{SSF}}.

Lifecycle Authority:
: The IdP responsible for the Governed Agent's enterprise lifecycle
  state. An authorized connector can deliver that state on its behalf.

Lifecycle Receiver:
: The resource-domain component accepting provisioning and lifecycle
  updates and making them effective at the RAS. It is a SCIM service
  provider and an SSF Receiver. It and the RAS form one administrative
  deployment responsible for atomic state application; they need not
  run in the same process.

State Record:
: The complete extension object defined in {{state-schema}}, including
  its identity, version, status, authorization cutoff, and validity.

Authorization Cutoff:
: A time watermark invalidating authorization derived from grants
  issued at or before that time. It survives reactivation and missed
  intermediate state changes.

Local Suspension:
: A resource-domain restriction maintained independently of the
  Lifecycle Authority's state. Upstream activation cannot clear it.

# Conformance and Trust Configuration {#conformance}

A deployment claiming this profile MUST implement:

| Component | Required behavior |
|---|---|
| Lifecycle Authority and its connector | Issue ordered state records; provision through SCIM; transmit lifecycle SETs; reconcile delivery |
| Lifecycle Receiver | Implement the SCIM extension, SSF push delivery, common ordering rules, and durable correlation |
| IdP grant issuer | Enforce lifecycle eligibility and the issuance-time contract in {{cutoff}} |
| RAS | Enforce eligibility at redemption and refresh; retain grant provenance; implement the configured enforcement mode |
| API | Apply the configured mode in {{api-enforcement}} and the Federation authorization rules |

This profile adds lifecycle checks to the applicable Federation profile.
It does not replace its client authentication, grant validation, actor
gate, or access-token protection requirements. A deployment MUST establish
applicability through trusted configuration, not infer it from a token
missing lifecycle information.

Before provisioning, the parties MUST configure:

* The governing IdP issuer and the permitted agent namespace.
* The authenticated SCIM connector and SSF Transmitter authorized for
  that namespace, and the receiver audience and target tenant.
* A maximum active-state validity interval, clock-error bounds, and
  maximum receiver enforcement delay ({{freshness}}).
* The enforcement mode and its introspection, caching, or token-lifetime
  limits for each API population ({{api-enforcement}}).
* The RAS and APIs covered by the lifecycle enforcement contract.

The Receiver MUST authorize SCIM and SSF writers for the same namespace.
An event's signing issuer need not equal the governing IdP issuer; that
authority relationship MUST be configured. A valid signature or a SCIM
write permission for another tenant does not establish it.

This revision has one logical Lifecycle Authority per governed identity.
Multiple connectors MAY represent it, but MUST share its version sequence
and issuance cutoff. Independent writers and authority failover without
preserved state are outside this profile.

The lifecycle guarantee assumes that the Authority applies its committed
decision to all grant-issuing nodes before publishing disablement, that
issuers report actual issuance times within the configured clock bounds,
and that renewals reflect a current lifecycle decision rather than a
connector's old cached state. These are source-side trust assumptions;
receivers cannot establish them by validating a State Record. A deployment
that does not satisfy them is non-conformant, not a degraded mode of
this profile.

# Identity, Correlation, and Administrative Authority {#identity}

The canonical identity is the exact pair (`issuer`, `subject`) in the
State Record. The subject MUST be unique and non-reassignable across all
Governance Tenants sharing that issuer. A Governance Tenant or target
tenant does not add a component to the canonical identity.

For delegated access, `issuer` and `subject` MUST equal the validated
ID-JAG's `act.iss` and `act.sub`, respectively. The RAS MUST look up
lifecycle state by that pair in the grant's authorized Target Tenant,
not by the user's `sub`, the OAuth client, or the access-token issuer.

The Receiver MUST:

* Match both components exactly, without case folding or URI rewriting.
* Correlate the pair with at most one local agent principal in each
  target tenant.
* Reject attempts to replace either component of an existing correlation.
* Require explicit local administrative authorization to attach the pair
  to a pre-existing principal; matching names or email addresses is not
  sufficient.

SCIM `id` identifies the Receiver's local resource. `externalId` is a
provisioning correlation value with the scope defined by {{RFC7643}}.
Neither replaces the canonical identity. `agentUserName` and display
attributes are not federation identifiers.

Existing service principals MAY represent agents locally. Their local
identifiers and implementation types do not change the governed identity.
The SCIM Agent resource MUST be a management representation of that same
local principal, not a second authorization principal. The Receiver
maintains the mapping from its SCIM `id` to the existing principal and
applies lifecycle changes to that principal's authorization.

This is local state; no cross-resource linking attribute is defined. Mapping it
to a different principal requires explicit administrative correlation,
not an ordinary synchronization update.
The same rules apply when the agent is an ID-JAG actor or, in a future WAG
composition, a self-acting subject ({{self-acting}}).

## Ownership, Groups, and Entitlements

Agent ownership and group membership use {{SCIM-AGENT}} and {{RFC7643}}.
Receivers SHOULD support those attributes for administrative accountability
and local policy. They MUST authorize their modification independently
of permission to deliver lifecycle state.

An owner is an accountable party, not automatically a delegator. An owner
change MUST NOT itself create user delegation, Client Association, or
resource permissions. Group membership has only the authorization meaning
assigned by resource-domain policy; this document defines none.

The Lifecycle Authority controls enterprise eligibility. The resource
domain controls local permissions and suspension. Effective eligibility
requires both. An upstream update MUST NOT clear a Local Suspension or
restore previously revoked resource permissions.

Effective eligibility, Local Suspension, and local permissions are not
observable through this SCIM extension. A returned `active: true` reports
the source's administrative status only; it is not an access decision.

# Lifecycle State {#state-schema}

## SCIM Extension Attributes

The extension schema URI is:

`urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent`

Its name is `GovernedAgentLifecycle`. The attributes below are all
single-valued, REQUIRED, returned by default, and have uniqueness `none`.
String attributes have `caseExact: true`. Mutability is `readWrite` except
for `issuer` and `subject`, which are `immutable`. Uniqueness of the
identity pair is enforced under {{identity}}.

| Attribute | SCIM type | Meaning |
|---|---|---|
| `issuer` | string | Governing IdP issuer identifier |
| `subject` | string | Governed Agent identifier in that issuer's namespace |
| `version` | string | Strictly increasing source version, defined below |
| `status` | string | One of `active`, `disabled`, or `retired` |
| `authorizationNotBefore` | dateTime | Authorization Cutoff; grants with `iat` at or before it are ineligible |
| `assertedAt` | dateTime | Time the Authority produced this State Record |
| `validUntil` | dateTime | Exclusive end of permission to rely on this record as active |

Dates MUST use UTC with the `Z` offset and whole-second precision.
`authorizationNotBefore` MAY be later than `assertedAt` by the configured
issuer-ahead clock bound in {{cutoff}}. For active state, `validUntil`
MUST be later than `assertedAt`. For disabled or retired state it remains
REQUIRED for a uniform record shape but is ignored for validity and
enforcement. These requirements narrow
the SCIM dateTime representation to allow unambiguous comparison with
JWT NumericDate values {{RFC7519}}.

The Receiver MUST reject a cutoff later than `assertedAt + D`. D is
agreed with the Authority for this issuer namespace, not learned from
an incoming record.

`version` MUST be a decimal string representing an integer from 1 through
9223372036854775807, using only ASCII digits and no leading zero.
Comparison is numerical, not lexical. Implementations MUST preserve it
without floating-point rounding; a signed 64-bit integer is sufficient.
The Authority MUST increase it for every new State Record,
including renewal of `validUntil`; it MUST NOT reuse or reset a version
for that identity.

The record is a complete snapshot, not a delta. The Authority MUST retain
the current version and cutoff across restarts, backup recovery, and
connector changes. SCIM `meta.version` remains the Receiver's HTTP entity
tag; it is not this source sequence.

The schema description above defines the `/Schemas` representation:
`status` has the three canonical values listed in {{transitions}};
the other attributes have no canonical value enumeration. Providers
MUST advertise the specified types, mutability, requiredness, return
behavior, and case sensitivity.

## States and Transitions {#transitions}

| State | Meaning | Permitted next states |
|---|---|---|
| `active` | Enterprise eligibility, subject to freshness and local authorization | `active`, `disabled`, `retired` |
| `disabled` | Reversible withdrawal of enterprise eligibility | `disabled`, `active`, `retired` |
| `retired` | Permanent withdrawal for this governed identity | `retired` |

Initial provisioning SHOULD use `disabled`. Initial `active` state
requires explicit enterprise activation and local acceptance; record
creation alone MUST NOT supply either decision.

On disablement or retirement, the Authority MUST advance the
Authorization Cutoff under {{cutoff}}. Repeated disabled or retired
snapshots retain that cutoff unless a later cutoff is needed.

On reactivation, the Authority MUST advance the cutoff again. Earlier
authorization remains invalid. Descriptive changes such as `displayName`
updates require a new source version, even when the lifecycle attributes
would otherwise be unchanged. Descriptive changes and active validity
renewals MUST NOT advance the cutoff unless the
Authority also intends to invalidate existing authorization.

If whole-second precision prevents a strictly increased cutoff within
the configured clock bound, the Authority waits before asserting the
new transition. Disablement still closes the issuance gate immediately.

Retirement is terminal. A new principal needs a new governed identifier.
Deletion of a local SCIM representation MUST NOT permit reuse of the
retired identity or erase its retirement protection.

## Authorization Cutoff and Issuance {#cutoff}

An Authorization Cutoff invalidates grants and retained authorization
issued at or before it, even if a Receiver missed the disabled state.
It MUST never decrease.

Every ID-JAG issued under this companion MUST contain `iat`, as already
required by {{ID-JAG, Section 3.1}}. This profile additionally requires a
whole-second NumericDate representing its issuance time.

Let D be the configured maximum number of whole seconds by which any
grant issuer can be ahead of the Authority, including clock error and
rounding. If each clock is within S seconds of a common time source,
D must cover at least 2S, rounded up. This is a difference between clocks,
not just one clock's error.

When advancing the cutoff, the Authority MUST set it to its current
whole-second time plus D, strictly above the previous cutoff. This covers
all grants issued before the committed transition without tracking the
greatest `iat` across issuing nodes. The source-side assumptions in
{{conformance}} still require the issuance gate to close before publication.

After activation, the issuer MUST issue only grants with `iat` strictly
later than the cutoff. Until its actual clock clears the cutoff, issuance
waits or fails. A cutoff ahead of the Authority's clock therefore creates
a bounded activation delay; it does not justify postdating grants.
Receivers MUST NOT apply positive clock-skew tolerance when comparing
the validated grant `iat` with the cutoff.

The issuance-time contract is an additional requirement of this companion;
the presence of `iat` is inherited from ID-JAG. No new grant or access-token
claim is defined. Shared lifecycle decisions and bounded clocks remain
necessary; a connector unable to obtain them is non-conformant.

# SCIM Provisioning {#scim}

The Receiver MUST implement Agent resources at `/Agents` using
{{SCIM-AGENT}} and the extension in {{state-schema}}. It MUST publish the
extension at `/Schemas` and advertise it in the Agent ResourceType's
`schemaExtensions`. The extension is REQUIRED for resources governed by
this profile; it need not be required for unrelated Agent resources.

The required operations are POST, resource GET, filtered collection GET,
and PUT under {{RFC7644}}. Receivers MUST support equality filtering on
both extension identity attributes and their conjunction. PATCH and Bulk
are OPTIONAL; if supported, they MUST preserve the atomicity and ordering
rules below.

## Creation and Existing Records

The connector MUST supply the Agent core's required attributes and the
complete extension. `active` MUST be `true` exactly when extension
`status` is `active`; inconsistent input is `400` with `invalidValue`.
The core attribute represents source administrative status, not the
result of freshness checks or Local Suspension.

The Receiver MUST check its correlation and retirement records before
creation. A duplicate canonical identity in the target tenant is `409`
with `uniqueness`. This requirement applies independently of
`agentUserName` uniqueness.

Malformed extension attributes use `400` with `invalidValue`; attempts
to change immutable identity attributes use `400` with `mutability`.
Other SCIM errors retain their meanings from {{RFC7644}}.

After an uncertain POST result, the connector MUST query by the qualified
identity before retrying creation. It MUST NOT create a second principal
under a different name to bypass a conflict.

Explicitly authorized correlation with an existing local principal MAY
occur before POST. The resulting Agent resource represents that principal;
the Receiver MUST NOT silently merge principals during synchronization.

## Updates and Common Processing {#ordering}

SCIM writes and lifecycle events MUST use the same processing rules:

1. Authenticate the sender and authorize its namespace and target tenant.
2. Validate the complete record, identity, and times. Reject an `assertedAt`
   in the future by more than the permitted clock error; delayed records
   are not rejected for their age alone. Apply the active-reliance clamp
   in {{freshness}}, rather than rejecting an excessive validity interval.
3. Compare the source version with the highest retained version.
   * A lower version cannot modify state.
   * An equal version with identical defined attribute values is a
     duplicate; it cannot extend freshness.
   * An equal version with different defined values is a conflict.
4. For a higher version, reject a decreasing cutoff or `assertedAt`, or
   any transition out of retained retirement. An expired snapshot may
   advance retained state, but cannot establish active eligibility.
   A change from active to inactive, or from disabled to active, MUST
   have a strictly increased cutoff.
5. Atomically persist the accepted state and make its issuance and
   introspection restrictions effective before reporting SCIM success.

Equality ignores JSON member order. Receivers MUST compare SCIM attribute
names according to SCIM rules and values according to {{state-schema}}.
Unknown extension attributes do not establish new permissions.

A lower-version SCIM write or a conflicting equal-version write receives
`409` with a SCIM `detail` string describing the conflict and no `scimType`.
There is no applicable registered `scimType` for a source-version conflict.

A duplicate write returns the current resource without reapplying
its lifecycle changes. If the same version arrived first through an
event, the first authorized SCIM representation at that version MAY
populate its descriptive attributes. The Receiver MUST remember that
application; changing those attributes again requires a newer version.

An invalid transition or decreasing cutoff receives `400`
with `invalidValue`. Failed HTTP conditional requests use the HTTP and
SCIM precondition rules, independently of source versions.

PUT MUST contain the complete extension. A supported PATCH changing any
lifecycle attribute MUST provide a complete resulting State Record and
consistent core `active` value in one atomic request. Omitting the
extension or deleting a required attribute is `400` with `invalidValue`.

Metadata changes MUST NOT bypass lifecycle version checks. If an older
PUT includes a stale status and new display name, the entire write is
rejected; it is not partially applied.

An accepted event MUST update the extension and core `active` value
visible through SCIM, including the resource's modification metadata.
GET therefore reports applied state, not merely the most recent SCIM
write. Pending events are not represented as successfully applied state.

## Retirement and Deletion

The connector MUST deliver retired state before deleting the local
representation. The Receiver MUST reject DELETE of a non-retired
profile resource with `403`. This is this profile's operation restriction,
not a DELETE rule of RFC 7644; it prevents deletion from bypassing ordered
lifecycle processing.

After deletion, the Receiver MUST retain a tombstone containing the
qualified identity, terminal status, highest version, and cutoff.
That identity MUST NOT be recreated as an active principal. A local
administrator can remove access without retiring the enterprise identity
by applying a Local Suspension instead.

# Lifecycle Signals {#signals}

## Target Tenant and Stream Binding {#stream-binding}

Each lifecycle stream MUST be bound by trusted administrative configuration
to exactly one governing issuer namespace and one Target Tenant at the
Receiver. The binding is associated with the SSF stream ID and its stream
configuration; this profile adds no SSF configuration member.

The configured `aud` MUST contain exactly one audience value assigned to
that issuer-namespace and Target-Tenant pair. That value MUST NOT be reused
for a different pair. Each SET MUST carry that audience as its sole
audience, and the Receiver MUST check it against the bound stream before
selecting the tenant or looking up the agent. A shared push endpoint can
use the authenticated stream and audience mapping; the agent identifier
alone cannot select a Target Tenant.

The SCIM connector's authorization and endpoint context MUST resolve the
same Target Tenant. Changing a stream's tenant or issuer-namespace binding
requires a new stream and audience value; replay on another binding MUST
be rejected. The target tenant scopes local correlation, not the canonical
agent identity or its source version sequence.

## Event Definition

This document defines the SET event type:

`urn:ietf:params:oauth:event-type:governed-agent-lifecycle`

It carries the Authority's current State Record, including validity
renewals. It is an assertion of enterprise lifecycle state, not a command
to grant local access.

The Transmitter and Receiver MUST follow {{RFC8417}} and {{SSF}}, including
signature validation, stream issuer, audience, and delivery authorization.
The event MUST:

* Use JWT type `secevent+jwt` and contain no `exp` claim, as required by
  SSF. The State Record's `validUntil` limits active-state reliance; it
  is not SET expiration.
* Identify the agent using the top-level `sub_id` with the `iss_sub`
  format from {{RFC9493}}.
* Contain a `state` member whose value is a JSON object with the seven
  attributes defined in {{state-schema}} directly as members. It MUST NOT
  wrap them in a SCIM schema-URN member or include a `schemas` member.
  Required member names use the spelling in that section. Receivers MUST
  ignore other unknown members; they confer no lifecycle semantics.
* Have matching `sub_id.iss` / `state.issuer` and `sub_id.sub` /
  `state.subject` values.

The event object has no other REQUIRED members. The subject MUST NOT be
placed in an event-local `subject` member. A Receiver MUST NOT infer the
agent's governing issuer from the SET's top-level `iss`.

## Delivery and Acceptance

Both parties MUST support SSF push delivery using {{RFC8935}}. SSF poll
delivery {{RFC8936}} MAY additionally be supported. Mandatory push support
is this profile's requirement, not a requirement of base SSF. The event type is
advertised through existing SSF event capability and stream configuration
fields; no separate discovery protocol is defined.

The Authority MUST arrange delivery of each new State Record through
SCIM or SSF, and MUST enqueue a lifecycle event on every status or cutoff
change for each configured target stream.

When a stream is paused or
delivery fails, the Transmitter retains the event for its configured
retry period and the connector uses SCIM reconciliation. Expiration of
that period does not remove the obligation to reconcile current state.
SCIM and SSF do not need to arrive in the same order. Retransmitting a
record MUST NOT change its version or validity; a fresh validity assertion
requires a new version.

Receivers MUST durably deduplicate SETs by Transmitter issuer and `jti`
for the configured delivery retry period. Source-version processing
remains necessary after the deduplication record expires and across
SCIM delivery of the same state. Neither `jti` nor SET `iat` is a state
ordering mechanism.

Accepted lower-version events and exact duplicates are acknowledged
without changing state. Invalid or conflicting events use the delivery
protocol's existing error reporting; this document defines no new
delivery error code. Conflicting equal-version records MUST also raise
an administrative diagnostic.

A delivery acknowledgment confirms durable acceptance for processing,
not completed API enforcement. The Receiver MUST make accepted restrictions
effective within its configured enforcement delay. It MUST NOT report
successful SCIM application of the same version while those restrictions
remain pending.

An event for an unprovisioned identity MUST NOT create an enabled local
principal. A Receiver MUST retain authorized disabled or retired state
for that identity, so a later stale provisioning request cannot bypass
it. For active state, it retains the version and cutoff but waits for
authorized SCIM provisioning before permitting access.

An authorized SCIM creation can establish the local correlation using
the same version and identical state retained from an earlier event.
This creates the resource without changing or refreshing the State Record.
A stale creation attempt is rejected with `409`; the connector obtains
the current record from its Authority before retrying.

# Enforcement and Freshness {#enforcement}

## Eligibility and Existing Authorization

The RAS MUST deny new grant redemption, access-token issuance, and refresh
unless all of the following hold:

* The qualified agent has an authorized local correlation.
* Its latest accepted status is `active` and its state is fresh.
* No applicable Local Suspension or terminal tombstone exists.
* The original IdP grant has a validated `iat` strictly after the current
  Authorization Cutoff.
* The Federation profile's client, user, tenant, authority, and actor
  authorization requirements succeed.

On disablement or retirement, the RAS MUST invalidate existing derived
authorization. When the cutoff advances, it MUST invalidate authorization
whose original grant `iat` is at or before the new cutoff. These
invalidations are permanent: subsequent activation cannot reverse them.
They take effect immediately at the RAS; cached decisions and offline
access tokens cease API use within the applicable mode's bound below.

A token request failing these lifecycle checks uses `invalid_grant` under
{{RFC6749}} and the applicable grant profile. Introspection returns
`active: false` under {{RFC7662}}. Error descriptions SHOULD avoid
disclosing lifecycle status or the existence of another tenant's agent.

## Grant Validation and Retained Provenance {#provenance}

The RAS MUST reject a grant with missing `iat`, a non-numeric or fractional
`iat`, or an issuance time inconsistent with its configured clock and
grant-validation rules, using `invalid_grant`. The grant MUST also clear
the current cutoff. Presence of `iat` follows ID-JAG; whole-second
precision and the cutoff check are additional companion requirements.

The RAS MUST retain the canonical agent identity, authorized Target Tenant,
and original grant `iat` with every authorization derived from the grant,
including access tokens and refresh authorization. Refresh, rotation, and
token issuance MUST NOT replace that provenance with a newer local timestamp.
This is an additional RAS requirement of this companion, not an implied
property of OAuth refresh or of an access token's own `iat`.

No new token claim or storage format is required. The RAS can retain the
context in its authorization record; APIs in the offline mode do not need
to recover the original grant time from the access token.

### Migration of Existing Authorization

Before applying this profile to an existing token population, the RAS MUST
either recover its original validated grant context or require a new
ID-JAG and new authorization. It MUST NOT infer missing provenance from an
access token's issue time, provisioning time, or current agent state.

Legacy refresh authorization without recoverable provenance MUST NOT mint
tokens in the new population. Deployments MAY drain existing access tokens
under their previous policy before enabling the lifecycle guarantee. The
new guarantee begins only after those tokens and any cached active results
can no longer authorize requests. Migration does not silently grandfather
untracked tokens into a stronger bound.

## API Enforcement Modes {#api-enforcement}

The RAS and API MUST configure one of the following modes for each governed
token population. These are deployment modes, not new OAuth profile URIs
or assurance levels. A token or validation failure MUST NOT select a weaker
mode. All modes retain Federation's token protection and actor gate.

| Mode | Resource behavior | Additional bound after RAS enforcement |
|---|---|---|
| Online introspection | Introspect each request; no reuse of active responses | T |
| Bounded introspection cache | Reuse an active response for at most C, within token expiry | T + C |
| Expiring JWT | Validate JWTs offline; bound their effective acceptance lifetime by A | A |

Both introspection modes MUST use authenticated {{RFC7662}} processing.
Before returning `active: true`, the RAS MUST apply current eligibility and
retained-provenance checks in addition to normal token validation. JWT or
opaque access tokens can use these modes.

### Online Introspection

The API MUST introspect the access token on every request and MUST NOT
reuse an active response. It MUST complete the authorization decision
within T of starting introspection; a late result requires another check
or denial. An inactive response, failed check, or timeout cannot permit
the request. This mode narrows Federation's permitted introspection caching.

### Bounded Introspection Cache

The API MAY reuse an active response for at most C after its receipt,
provided that response arrived within T of starting introspection.
It MUST check both cache age and token expiry at each authorization decision.
The cache deadline MUST NOT extend beyond `exp`, and a response without
`exp` MUST NOT be reused, retaining Federation's existing restriction.

Cache hits MUST NOT restart the interval. After expiry of the cached result,
failed revalidation or timeout cannot authorize use of stale state. A newly
obtained inactive response MUST invalidate the cached active result.
This mode makes Federation's configurable cache-freshness limit explicit.

### Expiring JWT

The RAS and API MUST apply {{RFC9068}} and Federation's JWT processing.
The RAS MUST limit each token's `exp - iat` to a configured maximum J.
The API MUST reject a token exceeding J, verify expiration at each decision,
and apply at most its configured expiration leeway P. Refresh and repeated
grant redemption remain subject to current lifecycle state at the RAS.

Let A = J + 2S + P, where S bounds each party's clock error. Issuers use
their actual issuance clock under {{conformance}}; future dating cannot
extend the configured lifetime. Thus A bounds elapsed acceptance after
issuance, including clock uncertainty and leeway.

This mode retains Federation's offline-validation option and adds a token
lifetime ceiling. An API may continue accepting a previously issued token
until its bounded expiry even after RAS revocation. Neither reactivation
nor a later cache policy change can extend that token's expiry. Direct
event processing at APIs can shorten this interval, but its consistency
protocol is outside this revision.

### Common Resource Requirements

The API MUST continue enforcing token authority, user authorization, and
the actor gate from {{FEDERATION}}. An active response or valid signature
does not itself authorize an operation. Invalid-token responses follow
{{RFC6750}} and the applicable access-token protection specification.

The bounds concern new authorization decisions, not rollback of completed
operations or cancellation of work already admitted. Long-running sessions
need separate revalidation or cancellation rules. Where APIs use different
modes, the deployment-wide bound is the longest applicable bound.

## State Freshness and Loss of Delivery {#freshness}

An active State Record is a time-limited assertion. The Authority MUST
renew it within the Receiver's accepted interval to maintain continuous
eligibility. The trust assumption for a current source decision on renewal
is stated in {{conformance}}.

For active state, the Receiver MUST set its effective reliance deadline to
the earlier of `validUntil` and `assertedAt + L`, where L is its configured
maximum interval. It MUST clamp an excessive interval, not reject the
State Record or rewrite the source's stored fields. It MUST stop relying
on active state at that deadline, accounting conservatively for clock error.

For disabled or retired state, `validUntil` and L MUST NOT delay, prevent,
or expire its restrictive effect. Syntax, source authorization, ordering,
and cutoff checks still apply. Arrival time, replay, stream heartbeats,
and reads of the Receiver's own SCIM resource cannot refresh source state.

Expiration blocks new RAS issuance, refresh, and active introspection until
a newer active record has an effective deadline in the future. Cached
results and offline tokens follow their mode's residual acceptance bound.
The distinction is intentional: freshness loss is reversible, while
administrative revocation is permanent. Still-valid authorization MAY
become usable after freshness is restored if its grant clears the cutoff;
disablement and cutoff invalidation cannot be reversed by renewal.

Let S bound clock error at each party and E bound enforcement delay after
acceptance. Under the source-side assumptions in {{conformance}}, the
conservative RAS stopping bound after disablement is B = L + 2S + E, even
if the notification is lost. Applied notification can shorten this window.

| Enforcement mode | Conservative denial bound from the Authority's disablement |
|---|---|
| Online introspection | B + T = L + 2S + E + T |
| Bounded introspection cache | B + T + C |
| Expiring JWT | B + A, with A = J + 2S + P |

The JWT term includes additional clock uncertainty at token issuance and
expiry validation; it is not merely the nominal token lifetime. All
parameters are finite deployment limits. Deployments MUST document their
mode, limits, timeouts, and outage behavior. They MUST NOT claim a shorter
bound based solely on grant lifetime or successful event delivery.

# Reconciliation and Recovery {#recovery}

The connector MUST maintain the mapping from each source identity to
the Receiver's SCIM resource ID and MUST periodically reconcile it.
Reconciliation uses ordinary SCIM GET and PUT; this document defines
no snapshot or cursor API.

For example, this is one decoded SCIM `filter` value. Unfold backslash
continuations under {{RFC8792}} before use; remaining line breaks stand
for whitespace. Percent-encode the complete value in the query parameter:

~~~ text
=============== NOTE: '\' line wrapping per RFC 8792 ================

urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent:\
issuer eq "https://idp.example" and
urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent:\
subject eq "agent-42"
~~~

The query runs under the connector's authorized Target Tenant. The
extension URI qualifies each attribute as specified by {{RFC7644}}.

For each identity assigned to a target tenant, the connector:

1. Queries its known resource ID, or filters by the qualified identity
   when the ID is unknown or the resource is missing.
2. Compares the returned State Record with the Authority's current record.
3. Creates a missing authorized resource or sends the current complete
   record when the Receiver is behind.
4. Investigates a Receiver version ahead of the source; it MUST NOT reset
   the sequence or overwrite state with a lower version.

An absent identity in a partial inventory MUST NOT be treated as retired.
The Authority MUST retain explicit retirement records and retry them
until affected receivers have applied them. Retirement tombstones also
protect against older backups and late provisioning requests.

SCIM records, pending event state, and tombstones participate in the same
version comparison. Applying version 43 does not require delivery of
version 42 because snapshots include the nondecreasing cutoff. A Receiver
MUST NOT depend on observing every intermediate transition.

After loss of correlation or lifecycle state, the Receiver MUST deny
affected authorization until trusted reconciliation completes. Restoring
an old backup MUST NOT make its active records fresh or bypass retained
retirement protections. Restoring an Authority without its version and
issuance watermark requires administrative recovery, not a sequence reset.

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

The IdP applies the first three boundaries under {{FEDERATION}}.
This companion does not define portable events identifying those
relationships. Selective revocation of their existing downstream tokens
needs issuance provenance and an agreed relationship identifier;
the agent's `act` identity alone is insufficient.

OAuth token revocation {{RFC7009}} remains available to revoke a known
token at its issuing server. It neither identifies every authorization
derived from a Governed Agent nor distributes principal lifecycle state
across domains. It complements this profile; it does not replace its
cutoff, ordering, or propagation contract.

A WISE or other upstream signal MAY inform the Authority's decision.
The Authority MUST evaluate its source, affected credential or workload,
and Identity Bindings before producing agent-wide lifecycle state.
Receivers MUST NOT reinterpret such upstream subjects as governed
identifiers without the federation mapping.

## Self-Acting Access {#self-acting}

The lifecycle identity is independent of the authorization flow. The
intended {{WAG}} composition correlates the same Governed Agent with the
same local agent principal used for delegated access.

Delegated access preserves the IdP-qualified actor in `act`; self-acting
access represents the correlated local principal as the resource-domain
subject. These representations do not make their authority interchangeable.

This revision claims no WAG wire conformance. A future composition needs
an authenticated governed subject and issuance time to apply the same
cutoff and provenance checks. It does not need a separate agent lifecycle.

# Security Considerations

## Lifecycle Writers and Token Confusion

A lifecycle writer can disable agents or assert renewed eligibility.
Receivers MUST restrict writers to explicitly authorized issuer and target
tenant relationships. They MUST NOT derive that permission from an
unverified payload, a supplied URL, or a display name. Channel credentials
and SET keys follow their underlying protocols' validation requirements.

SETs are not OAuth grants or access tokens. Receivers MUST keep lifecycle
event validation separate from those token classes. The `secevent+jwt`
type and absence of `exp` support this separation; they do not replace
signature, issuer, audience, and writer authorization checks.

## Rollback, Reactivation, and Compromised Authorities

Durable source versions prevent delivery rollback. The cutoff prevents
reactivation from reviving old authorization, including when a Receiver
missed disablement. Both properties depend on retained state. A higher
version does not make a decreasing cutoff acceptable.

An authorized source that lies about status, issuance times, or freshness
can defeat the enterprise lifecycle guarantee. Local restrictions remain
independent and SHOULD be available for incident containment. This profile
does not protect against compromise of the governing IdP itself.

## Availability and Administrative Evidence

Short validity intervals and online introspection limit stale access
but increase load and sensitivity to outages. Cached introspection and
expiring JWTs trade longer residual access for fewer online checks.
Operators SHOULD choose the mode, state interval, and delivery capacity
together, and monitor renewal lag, conflicts, and enforcement delays.

Maintaining N active agents with validity interval L requires more than
N/L fresh state assertions per second when allowing delivery margin.
For 100,000 agents and five minutes, the nominal minimum is about 333
per second per target domain, before retries. SSF delivery uses signed
SETs; SCIM renewals can use existing Bulk support when available. Neither
delivery choice removes the need for a current source eligibility decision.
Staggering renewals avoids synchronized bursts. Longer intervals reduce
traffic but increase the stated disablement bound; a transmitter heartbeat
alone cannot renew every agent's eligibility.

Audit records SHOULD distinguish source decision, receipt, application,
and API denial times. A transport acknowledgment is not evidence that
every API has stopped accepting affected authorization.

# Privacy Considerations

Stable governed identifiers enable correlation across users, resources,
and time. Lifecycle streams SHOULD be limited to resource domains that
have provisioned or otherwise authorized correlation for the agent.
Writers MUST be authorized for the target tenant before disclosure.

This profile does not require transmitting external workload identifiers,
credential identifiers, user delegations, owner email addresses, or incident
details in events. Implementations SHOULD minimize such additional data.
Retirement tombstones retain only the identity and synchronization data
needed to prevent reuse; other attributes can follow local retention policy.

# IANA Considerations

## SCIM Schema Registration

This document requests registration in the SCIM Schema URIs registry
under the procedure in {{RFC7643, Section 10.3}}. The registration template
is in {{schema-registration}}.

## OAuth URI Registration

This document requests registration in the OAuth URI registry under
{{RFC6755}}:

* URN: `urn:ietf:params:oauth:event-type:governed-agent-lifecycle`
* Common Name: Governed Agent Lifecycle Security Event
* Change Controller: IETF
* Specification Document: {{signals}} of this document.

The URI identifies a SET event, not a grant type or access-token type.
This registration deliberately introduces the `event-type` class under
the OAuth URN namespace; it is a proposed use of the registration procedure
in RFC 6755, not an existing event-type subregistry or a new registry.
Both identifiers are proposed registrations, not completed assignments.

# SCIM Schema Registration Template {#schema-registration}

The registration template required by {{RFC7643, Section 10.3.2}} is:

* Schema URI:
  `urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent`
* Schema Name: Governed Agent Lifecycle Extension
* Intended or Associated Resource Type: Agent
* Purpose: Carry the canonical governed identity and authoritative
  lifecycle state used for provisioning and OAuth enforcement.
* Single-value Attributes: `issuer`, `subject`, `version`, `status`,
  `authorizationNotBefore`, `assertedAt`, `validUntil`, as defined in
  {{state-schema}}.
* Multi-valued Attributes: None.

--- back

# Provisioning and Disablement Example {#example}

This non-normative example uses an IdP at `https://idp.example`, a RAS
at `https://ras.example`, and governed subject `agent-42`. It uses online
introspection, S = 1 second, and issuer-ahead bound D = 2 seconds.
Bearer values
and the SET signature are placeholders. SCIM locations identify the
Receiver's records, not the enterprise identity.

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
    "issuer": "https://idp.example",
    "subject": "agent-42",
    "version": "40",
    "status": "disabled",
    "authorizationNotBefore": "2026-09-17T12:00:02Z",
    "assertedAt": "2026-09-17T12:00:00Z",
    "validUntil": "2026-09-17T12:05:00Z"
  }
}
~~~

The Receiver returns `201 Created`, a `Location` identifying
`https://ras.example/scim/v2/Agents/local-108`, and the created resource
including `id: "local-108"`. The connector retains that location. The
agent remains ineligible until both enterprise and local activation
conditions hold.

## Activate and Issue Authorization

At 12:01:00 UTC the Authority issues version 41 with `status: "active"`,
cutoff 12:01:02, and validity until 12:06:00. The connector PUTs the
complete resource with `active: true`. The Receiver applies it and
returns `200 OK`.

An ID-JAG issued at 12:01:03 clears the cutoff. The RAS retains its
original `iat` with the derived access token and refresh authorization.
The API introspects the access token on each request.

## Disable Through a Signal

At 12:02:00 the Authority disables the agent and publishes version 42.
Its stream is administratively bound to issuer `https://idp.example`
and Target Tenant `tenant-7`, with the exclusive audience
`https://ras.example/lifecycle/tenant-7/idp-example`.
The decoded SET has protected header `{"typ":"secevent+jwt"}` together
with the negotiated signing algorithm and key identifier, and this payload:

~~~ json
{
  "iss": "https://signals.idp.example",
  "aud": "https://ras.example/lifecycle/tenant-7/idp-example",
  "jti": "event-42",
  "iat": 1789646520,
  "sub_id": {
    "format": "iss_sub",
    "iss": "https://idp.example",
    "sub": "agent-42"
  },
  "events": {
    "urn:ietf:params:oauth:event-type:governed-agent-lifecycle": {
      "state": {
        "issuer": "https://idp.example",
        "subject": "agent-42",
        "version": "42",
        "status": "disabled",
        "authorizationNotBefore": "2026-09-17T12:02:02Z",
        "assertedAt": "2026-09-17T12:02:00Z",
        "validUntil": "2026-09-17T12:07:00Z"
      }
    }
  }
}
~~~

The Receiver applies version 42. Redemption and refresh fail with
`invalid_grant`; introspection of the previously issued token returns
`{"active":false}`. The API denies its next use.

## Delayed Delivery and Reactivation

| Subsequent input | Result |
|---|---|
| Delayed SCIM PUT carrying active version 41 | `409`; disabled version 42 remains in effect |
| Retransmission of event 42 | Acknowledged without extending validity or changing state |
| Different state using version 42 | Rejected and diagnosed as a conflict |
| Authorized active version 43 with cutoff 12:03:02 | Fresh grants after the cutoff can qualify; old tokens stay invalid |
| Version 43 delivered without version 42 | The newer cutoff still rejects the grant issued at 12:01:03 |
| No update or renewal after active version 41 | Authorization is denied when its finite validity ends |
| Retired version 44 followed by an active version 45 | Invalid transition; retirement remains terminal |

In bounded-cache mode an earlier active introspection result may still
be used within C; in expiring-JWT mode the API can accept the old token
until its bounded expiry. Neither mode allows RAS refresh after the
disablement is applied. Their longer bounds are explicit in {{freshness}}.

# Relationship to Existing Work

The assessed inputs are SCIM Agent Resource -00, SCIM Agent Governance
-00, and the WISE editor's copy. Their evolution can change the most
appropriate schema and event bindings.

This profile deliberately reuses the Agent resource, SCIM operations,
SET subject identifiers, and SSF delivery. The new material is the
qualified identity extension, shared source ordering, finite state
validity, issuance cutoff, and enforcement contract.

The account-disabled, account-enabled, and account-purged events in
{{RISC}} report account transitions. They do not define this profile's
shared source version, issuance cutoff, or finite active-state validity.
Those fields must also survive missed transitions and SCIM reconciliation.
A dedicated event makes those receiver obligations explicit without
changing the meaning of existing account events. This is a distinction
in event semantics, not a claim that SSF subjects must be human users.

Detailed quarantine workflows, autonomy classifications, and credential
discovery are not required for that contract. A deployment using richer
governance states maps them into active, disabled, or retired eligibility
at the Lifecycle Authority, rather than asking each RAS to interpret them.

# Document History

Initial version.
