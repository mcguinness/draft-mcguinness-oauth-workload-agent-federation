---
title: "Shared Signals Profile for Agent Provisioning and Session Revocation"
abbrev: "Agent Provisioning Signals"
category: std
docname: draft-mcguinness-ssf-governed-agent-events-latest
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
  latest: "https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-ssf-governed-agent-events.html"
author:
 - fullname: Karl McGuinness
   organization: Independent
   email: public@karlmcguinness.com
normative:
  CAEP:
    title: "OpenID Continuous Access Evaluation Profile 1.0"
    target: https://openid.net/specs/openid-caep-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
  SSF:
    title: "OpenID Shared Signals Framework Specification 1.0"
    target: https://openid.net/specs/openid-sharedsignals-framework-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
  RFC7644:
  RFC8417:
  RFC9493:
  RFC9967:
informative:
  FEDERATION:
    title: "OAuth 2.0 Profile for Governed Agent Federation"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-workload-agent-federation
  LIFECYCLE:
    title: "Governed Agent Lifecycle Profile for SCIM and OAuth"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-governed-agent-lifecycle
  WISE:
    title: "Workload Identity Security Events (WISE) Profile"
    target: https://github.com/identitymonk/openid-wise/blob/main/openid-wise-profile-1_0.md
    author:
      - org: WISE Contributors
--- abstract

This document profiles existing SCIM Events and OpenID Continuous Access
Evaluation Profile session-revocation events over the Shared Signals
Framework for agent federation deployments. SCIM notices trigger retrieval
of authoritative provisioning state. Session revocation invalidates
identified authorization sessions independently of principal eligibility.

The profile defines trust, subject correlation, and receiver processing.
It introduces no event type, claim, SCIM schema, or lifecycle version.
Event delivery does not establish a complete revocation history or a
resource-enforcement deadline.

--- middle

# Introduction

An Agent Principal in {{FEDERATION}} has a stable issuer-qualified identity
and a separately correlated principal in each resource domain. Existing
protocols can report changes to its provisioned representation and to its
authorization sessions without introducing another lifecycle-state format.

This document uses two existing mechanisms:

| Mechanism | Subject | Receiver action |
|---|---|---|
| SCIM provisioning notice {{RFC9967}} | Resource at the configured source SCIM service | Retrieve current state and reconcile the authorized local representation |
| CAEP session revocation {{CAEP}} | Identified authorization session | Invalidate that session and its associated authorization |

Both use Security Event Tokens (SETs) {{RFC8417}} and Shared Signals
{{SSF}}. A provisioning change and a session revocation are not
interchangeable. A session can be revoked while the principal stays
active; an active principal can have previously revoked sessions.

{{LIFECYCLE}} defines SCIM provisioning and OAuth application of principal
state. This document supplies an optional event-driven reconciliation path
and a separate session-revocation capability. It does not require a new
registry, signed eligibility lease, or comparison of event time with grant
issuance time.

## Conventions and Conformance

{::boilerplate bcp14-tagged-bcp14}

Transmitter, Receiver, stream, and subject follow {{SSF}}. Source SCIM
service means the trusted service exposing authoritative provisioning
state, not the Receiver's local replica.

A conforming implementation MUST support the SCIM notice capability in
{{scim-events}}. CAEP session revocation in {{session-revocation}} is
OPTIONAL and requires established session correlation. Implementations
advertise the existing event types they support through SSF metadata and
stream configuration; this document defines no new discovery parameter.

# Trust and Delivery {#trust}

Before accepting events, the parties MUST configure:

* The trusted Transmitter and its signing and delivery configuration.
* The receiving audience and Target Tenant associated with each stream.
* The source SCIM base URI, retrieval credentials, and authority to
  publish changes for that service's resources.
* The correlation between source resources and governed identities.
* For CAEP, the session-identifier namespace and sessions the Transmitter
  is authorized to revoke.

The authenticated delivery context MUST identify the stream. SET issuer
and audience validation then uses that stream's configuration; an audience
array follows SSF audience-validation rules. A valid SET signature does
not authorize a Transmitter for another source namespace or Target Tenant.

The SET `iss` identifies the Transmitter. It need not be the governing
IdP issuer or source SCIM base URI. Those relationships MUST come from
trusted configuration, not equality assumptions or caller-selected URLs.

SET validation, deduplication, and delivery errors follow {{SSF}} and
{{RFC8417}}. The protected type is `secevent+jwt`; SSF SETs do not carry
`exp`. Push or poll delivery is selected using SSF; neither is uniquely
required by this profile. Acknowledgment indicates transport acceptance,
not successful reconciliation or completed API enforcement.

# SCIM Provisioning Notices {#scim-events}

## Event Types

This capability uses these existing event types from {{RFC9967}}:

| Event type | Meaning in this profile |
|---|---|
| `urn:ietf:params:scim:event:prov:create:notice` | Reconcile a newly created source resource, subject to provisioning authorization |
| `urn:ietf:params:scim:event:prov:patch:notice` | Reconcile the source resource after a PATCH |
| `urn:ietf:params:scim:event:prov:put:notice` | Reconcile the source resource after a PUT |
| `urn:ietf:params:scim:event:prov:delete` | Reconcile removal of the identified source representation |

A Transmitter MUST report changes to managed principal administrative
state through the appropriate event when this capability is configured.
Event payloads retain their RFC 9967 definitions. The deletion event has
no event-specific attributes.

The `version` attribute identifies the source resource's ETag. It is not
an ordered counter, an authorization generation, or the Receiver's ETag.
The SET's `iat` likewise does not order changes to the resource.

Full-resource replication and the existing activate/deactivate events
can be used by other agreed compositions. They are not required here.
This profile uses notices and authoritative retrieval to avoid defining
another snapshot-ordering protocol.

## Subject and Principal Correlation {#subjects}

SCIM events use top-level `sub_id` with the `scim` format and resource
`uri`, as defined in {{Section 2.1 of RFC9967}}. The URI identifies a
resource relative to the configured source SCIM base URI. It is not the
Receiver's SCIM identifier or the federated Agent Principal identifier.

Receivers MUST maintain an authorized mapping from the source service
and resource URI to the governed identity and receiving tenant before
applying changes to an existing local principal. A source `externalId`
can assist correlation within its configured namespace; it MUST NOT
establish a cross-issuer or cross-tenant mapping by itself.

For a new source resource, the notice can initiate an authorized
provisioning workflow. It MUST NOT create trust, select an existing local
principal by display name, or grant permissions merely because a signed
event names the resource.

## Receiver Processing {#processing}

After event validation and source authorization, the Receiver MUST:

1. Resolve the subject within the configured source service and tenant.
2. Mark the resource for reconciliation and retrieve its current
   representation using authenticated SCIM {{RFC7644}}. Requests MUST
   remain within the configured source service; the subject cannot
   redirect credentials to another host or arbitrary path.
3. Apply only authorized changes to the correlated local representation.
   Reconciliation MUST prevent an older in-flight result from overwriting
   a newer applied result or restriction.
4. Retry incomplete reconciliation and retain its pending status until
   successful or resolved administratively. Acknowledging the SET MUST
   NOT cause a failed reconciliation to be forgotten.

Implementations MAY coalesce notices for the same resource. A conditional
GET can confirm that the source representation has not changed. A stale
notice therefore need not reverse newer state, and repeated notices do
not require repeated state changes.

A deletion notice identifies a source resource, not permanent retirement
of its federated identity. The Receiver MUST reconcile the mapped source
representation before removing or disabling its local representation.
An authoritative absence can establish removal; an inaccessible endpoint,
a failed authorization, or an incomplete search cannot. Local protective
suspension MAY apply while that distinction is unresolved.

Receivers SHOULD reconcile periodically in addition to processing events.
A new active representation cannot reveal every earlier transition. This
profile supplies neither a complete event history nor a missed-revocation
guarantee; {{limits}} states the resulting boundary.

# CAEP Session Revocation {#session-revocation}

The optional revocation capability uses the existing event type:

`https://schemas.openid.net/secevent/caep/event-type/session-revoked`

For this capability, the subject MUST use the `opaque` format in
{{RFC9493}} to identify an established authorization session in the
configured namespace. This narrows CAEP's broader subject options to avoid
ambiguity between a delegated user, an acting agent, and a session.
The session identifier MUST have a pre-established correlation at the
Receiver; display names, OAuth client identifiers, and principal
identifiers MUST NOT be interpreted as session identifiers.

This profile defines no session-registration protocol. A deployment needs
an existing integration that makes the session identifier available to the
Transmitter and Receiver. An ID-JAG `jti` is not automatically a RAS session
identifier. Deployments without this correlation use SCIM lifecycle
application and do not claim this optional capability.

The Receiver MUST verify that the Transmitter can revoke the identified
session in the receiving tenant, then invalidate its associated local
authorization. It MUST retain that revocation while affected tokens or
refresh authorizations could still be accepted. An unknown session MUST
NOT cause creation of a session or a broader principal-level action;
processing it is an idempotent no-op and MAY produce a diagnostic.

The event does not change the Agent's `active` attribute. Later activation
or provisioning MUST NOT restore the revoked session. A consuming profile
defines how revocation reaches token validation and APIs.

CAEP's common claims, including `event_timestamp` and localized reasons,
retain their existing meanings. They are not new lifecycle claims.
In particular, the event timestamp describes the revocation occurrence;
it MUST NOT be used here as an agent-wide cutoff against token `iat`.
The event has no new event-specific claims.

# Limits and Recovery {#limits}

Events can arrive after later changes. Current SCIM retrieval resolves
current administrative state, not the historical effect of every change.
If a disabled principal is re-enabled before either state is observed,
a subsequent active GET cannot prove that earlier sessions were revoked.
ETags distinguish representations but do not explain their differences.

Similarly, reliable receipt of one SET does not prove receipt of all
previous revocations. Stream verification is not confirmation of each
principal's eligibility. Recovery of missing revocation history needs an
additional mechanism, such as an authoritative session-status check or
retained revocation records available to the Receiver.

Reconciliation and retry reduce stale state, but this profile declares no
maximum propagation or denial time. Cached introspection and offline JWT
validation can continue accepting tokens after a RAS applies revocation.
Operational claims must account for those enforcement paths.

# Security Considerations

Event trust, provisioning permission, and resource authorization are
separate. A Transmitter authorized to report a workload credential change
is not necessarily authorized to disable its mapped Agent Principal.
A connector with descriptive-write permission is not necessarily authorized
to enable that principal.

Source retrieval creates an outbound request. Receivers must authorize
the configured source and constrain URI resolution, redirects, and
credential forwarding. A signed subject is not permission to fetch an
arbitrary URL.

Delayed and duplicate events must not undo local revocation. Session
identifiers MUST NOT be reassigned while an event for an earlier session
could still be accepted. Loss of retained revocation or pending
reconciliation state requires explicit recovery, not presumed activation.

SETs are notifications, not OAuth grants or access tokens. Their successful
validation does not bypass local policy or establish user delegation.

# Privacy Considerations

Events and retrieval access SHOULD be limited to the receiving domains
that need the information. A notice can avoid distributing a full Agent
record to every consumer. Opaque session identifiers reduce unnecessary
identity disclosure but still permit correlation within their namespace.
Reasons SHOULD omit sensitive task contents and reusable credentials.

# IANA Considerations

This document requests no IANA actions. All event types and subject formats
are defined by the referenced specifications.

--- back

# Examples {#example}

These decoded SETs are non-normative and omit signatures. Protected
headers use `typ: secevent+jwt` and an agreed signing algorithm and key.
The stream configuration binds the audience to Target Tenant `acme-data`.

## Provisioning Change Notice

The trusted source SCIM service has resource `/Agents/source-42`. Its
configured correlation is `(https://idp.example/, agent-42)`, represented
at the RAS by `/Agents/local-108`. At 12:02 UTC on September 17, 2026,
the source changes the principal's `active` value to false:

~~~ json
{
  "iss": "https://signals.idp.example",
  "aud": ["https://ras.example/signals/acme-data"],
  "iat": 1789646520,
  "jti": "change-42",
  "sub_id": {
    "format": "scim",
    "uri": "/Agents/source-42"
  },
  "events": {
    "urn:ietf:params:scim:event:prov:patch:notice": {
      "version": "W/\"source-b7\"",
      "attributes": ["active"]
    }
  }
}
~~~

The Receiver retrieves the source Agent, observes `active: false`, and
applies disablement under {{LIFECYCLE}}. The notice itself contains no
boolean state, authorization cutoff, or lease. If delivered after a later
change, retrieval obtains current state instead.

## Revoke an Identified Session

Separately, an authorized Transmitter can report revocation of the
pre-correlated session `session-7` while the principal remains active:

~~~ json
{
  "iss": "https://signals.idp.example",
  "aud": ["https://ras.example/signals/acme-data"],
  "iat": 1789646520,
  "jti": "revoke-session-7",
  "sub_id": {
    "format": "opaque",
    "id": "session-7"
  },
  "events": {
    "https://schemas.openid.net/secevent/caep/event-type/session-revoked": {
      "event_timestamp": 1789646520,
      "initiating_entity": "admin",
      "reason_admin": {"en": "Administrator revoked this session."}
    }
  }
}
~~~

No principal-state update is implied. Revoking this session does not revoke
another user's unrelated session or every session involving the same agent.

# Relationship to Other Event Profiles

{{WISE}} describes workload and credential changes. Those events can inform
an IdP's governance decisions, but a workload identity and an Agent Principal
are not interchangeable. Their federation mapping determines the affected
principal and whether other valid bindings remain.

This profile deliberately reuses SCIM notices for administrative changes
and CAEP for session revocation. It does not define an Agent State Changed
event, add fields to CAEP or WISE, or require new event registrations.
A future need for agent-wide revocation history should be specified as
an explicit additional contract rather than inferred from these events.

# Document History

Initial version.
