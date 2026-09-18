---
title: "Governed Agent Lifecycle Events Profile"
abbrev: "Governed Agent Events"
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
  RFC3339:
  RFC7519:
  RFC7643:
  RFC8259:
  RFC8417:
  RFC9493:
informative:
  RFC9967:
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  FEDERATION:
    title: "OAuth 2.0 Profile for Governed Agent Federation"
    author:
      - name: Karl McGuinness
    date: 2026-09-17
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-workload-agent-federation
  LIFECYCLE:
    title: "Governed Agent Lifecycle Profile for SCIM and OAuth"
    author:
      - name: Karl McGuinness
    date: 2026-09-17
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-governed-agent-lifecycle
  WISE:
    title: "Workload Identity Security Events (WISE) Profile"
    target: https://github.com/identitymonk/openid-wise/blob/main/openid-wise-profile-1_0.md
    author:
      - org: WISE Contributors
  RISC:
    title: "OpenID RISC Profile Specification 1.0"
    target: https://openid.net/specs/openid-risc-1_0-final.html
    author:
      - org: OpenID Foundation
    date: 2025-08-29
--- abstract

This document defines an event profile of the Shared Signals Framework
for Agent Principal lifecycle changes. Transmitters report an agent's
current eligibility, lifecycle version, authorization cutoff, and, when
active, eligibility-lease expiration. Receivers use these assertions under
their own authorization policy or a consuming profile.

The profile reuses SSF subject identification and CAEP common event claims.
An optional SCIM representation maps the event's lifecycle state to an
Agent resource. Delivery and OAuth enforcement are defined separately.

--- middle

# Introduction

Agent Principal lifecycle events allow cooperating Transmitters and Receivers
to communicate changes in enterprise eligibility. The subject is the stable
issuer-qualified agent described by Governed Agent Federation {{FEDERATION}},
independent of its workload credentials and local resource representations.

This document profiles Security Event Tokens (SETs) {{RFC8417}} and the
Shared Signals Framework (SSF) {{SSF}}. It follows the event-definition
structure used by {{CAEP}} and {{WISE}}: common claims, event-specific
claims, subject identification, and examples.

An event reports state; it does not grant permission. {{LIFECYCLE}} defines
a consuming profile for SCIM reconciliation and OAuth enforcement, including
operational denial bounds. Those deployment requirements are not implied
by support for this event profile.

## Notational Conventions

{::boilerplate bcp14-tagged-bcp14}

Transmitter, Receiver, stream, and subject follow {{SSF}}. A Lifecycle
Authority governs the agent's eligibility. It may authorize a separate
Transmitter to send its decisions.

An implementation produces or consumes the event in {{event}} under SSF.
This document does not select a delivery method; consuming profiles can do
so through existing SSF mechanisms. The SCIM representation in {{scim-binding}}
is optional and does not require an event implementation to operate a SCIM
service.

# Subject Identification {#subjects}

The event subject is identified by top-level `sub_id`, following the SSF
rules for new event types. Its format MUST be `iss_sub` {{RFC9493}}:

* `iss` identifies the authority's Agent Principal namespace.
* `sub` identifies the Agent Principal within that namespace.

Receivers MUST correlate the exact pair without case folding or URI
rewriting and authorize the Transmitter to assert state for that namespace.
The SET's top-level `iss` identifies the Transmitter and need not equal
`sub_id.iss`. It cannot substitute for the governing issuer.

The event payload does not repeat the primary subject or define an
event-local `subject`. Local SCIM identifiers, OAuth client identifiers,
and external workload identifiers do not replace the qualified agent.

# Common Event Claims {#common-claims}

Events in this profile MAY include the common claims defined in
Section 2 of {{CAEP}}. Their types and meanings are inherited:

| Claim | Meaning |
|---|---|
| `event_timestamp` | Time of the event, as a JSON number of seconds since the Unix epoch |
| `initiating_entity` | `admin`, `user`, `policy`, or `system` |
| `reason_admin` | Localizable administrative explanation |
| `reason_user` | Localizable end-user explanation |

The reason claims use CAEP's language-tagged JSON objects, not plain strings.
These claims are optional unless an event definition requires them. The
Agent State Changed event requires `event_timestamp` and specifies its
relationship to lifecycle state below. The SET's `iat` remains the time
of token issuance; it is not a replacement for `event_timestamp`.

# Event Types

The provisional base URI for this profile's event types is:

`https://mcguinness.github.io/secevent/agent/`

This author-controlled namespace identifies the events in this individual
proposal; it is not an assignment in an OpenID Foundation namespace.

## Agent State Changed {#event}

Event Type URI:

`https://mcguinness.github.io/secevent/agent/state-changed`

Agent State Changed signals that the Authority has established a new version
of an Agent Principal's eligibility state. This includes initial state,
disablement, reactivation, retirement, and renewal of an active eligibility
lease. Renewal changes the state version even when `status` is unchanged.

The event carries a complete snapshot so a Receiver can process it without
having received every earlier transition. Separate enabled, disabled, and
renewed event types are not needed to reconstruct current state.

### Event-Specific Claims {#event-claims}

These claims appear directly in the event object under its Event Type URI.
There is no nested `state` wrapper. Names are case-sensitive; Receivers
ignore unrecognized fields under SSF. Duplicate JSON member names MUST be
rejected {{RFC8259}}.

event_timestamp:
: REQUIRED, JSON number. Time the Authority established this state version,
  including a lease renewal. This event requires whole-second NumericDate
  values {{RFC7519}}. Reissuing the SET does not change this timestamp.

version:
: REQUIRED, JSON string. Strictly increasing lifecycle version, represented
  by ASCII decimal digits from 1 through 9223372036854775807, without a
  leading zero. Comparison is numerical, not lexical; implementations MUST
  preserve the value without floating-point rounding.

status:
: REQUIRED, JSON string. One of `active`, `disabled`, or `retired`, with the
  semantics in {{state-semantics}}.

authorization_cutoff:
: REQUIRED, JSON number. Whole-second NumericDate watermark invalidating
  authorization issued at or before that instant. It MUST NOT decrease
  between state versions. A consuming authorization profile specifies the
  issuance-time provenance and comparison needed to enforce it.

valid_until:
: REQUIRED when `status` is `active`, JSON number. Exclusive eligibility-lease
  expiration, as a whole-second NumericDate later than `event_timestamp`.
  For disabled or retired state, it SHOULD be omitted; its presence and
  value MUST be ignored during lifecycle validation and comparison.

The whole-second event times are an explicit requirement of this event type,
not a restriction on NumericDate generally. Their SCIM conversion is defined
in {{scim-schema}}.

### State Semantics {#state-semantics}

| Status | Meaning | Permitted next status |
|---|---|---|
| `active` | Eligible until the effective lease deadline, subject to independent authorization | `active`, `disabled`, `retired` |
| `disabled` | Reversible withdrawal of eligibility | `disabled`, `active`, `retired` |
| `retired` | Permanent withdrawal for this qualified identity | `retired` |

A consuming profile can shorten reliance on an active lease. Delivery,
replay, or stream heartbeats MUST NOT renew it. Disabled and retired state
do not expire, and retirement protection survives local resource deletion.
A retired qualified identity MUST NOT be reused for a new principal.

Transitions from `active` to `disabled` or `retired`, and from `disabled`
to `active`, MUST advance `authorization_cutoff`. A transition from
`disabled` to `retired` need not. A lease renewal alone does not advance it.
Reactivation cannot revive authorization invalidated by an earlier cutoff.

### Examples {#example}

These non-normative decoded SETs use a Transmitter separately authorized to
publish state for `https://idp.example`. Protected headers include
`typ: secevent+jwt`, a negotiated signing algorithm, and a key identifier.
Audience interpretation and enforcement follow the consuming profile.

The first event establishes active state at 12:01:00 UTC on September 17,
2026, with a cutoff at 12:01:02 and a lease ending at 12:06:00.

~~~ json
{
  "iss": "https://signals.idp.example",
  "aud": "https://ras.example/lifecycle/tenant-7/idp-example",
  "iat": 1789646460,
  "jti": "event-41",
  "sub_id": {
    "format": "iss_sub",
    "iss": "https://idp.example",
    "sub": "agent-42"
  },
  "events": {
    "https://mcguinness.github.io/secevent/agent/state-changed": {
      "event_timestamp": 1789646460,
      "version": "41",
      "status": "active",
      "authorization_cutoff": 1789646462,
      "valid_until": 1789646760,
      "initiating_entity": "system"
    }
  }
}
~~~

At 12:02:00, the Authority disables the agent. The new snapshot advances
the cutoff to 12:02:02 and carries no eligibility-lease expiration.

~~~ json
{
  "iss": "https://signals.idp.example",
  "aud": "https://ras.example/lifecycle/tenant-7/idp-example",
  "iat": 1789646520,
  "jti": "event-42",
  "sub_id": {
    "format": "iss_sub",
    "iss": "https://idp.example",
    "sub": "agent-42"
  },
  "events": {
    "https://mcguinness.github.io/secevent/agent/state-changed": {
      "event_timestamp": 1789646520,
      "version": "42",
      "status": "disabled",
      "authorization_cutoff": 1789646522,
      "initiating_entity": "admin",
      "reason_admin": {
        "en": "Enterprise administrator disabled the agent."
      }
    }
  }
}
~~~

# Lifecycle State Processing {#ordering}

## State Record {#state-schema}

The State Record is the logical combination of the qualified subject and
`version`, `status`, `authorization_cutoff`, `event_timestamp`, and, when
active, `valid_until`. It is not a second JSON payload format. The event
and SCIM representations convey this same information through the mapping
in {{scim-schema}}.

The Authority MUST advance `version` whenever a lifecycle-relevant value
changes and retain the version and cutoff across restart or recovery.
Descriptive SCIM edits and changes to optional reason claims do not change
lifecycle state. Optional claims other than `event_timestamp` do not
participate in state equality.

## Receiver Processing

After SSF validation and source authorization, the Receiver MUST:

1. Select retained state by the qualified subject within its authorized
   receiving context.
2. Compare `version` with the highest accepted version, including pending
   state. Treat a lower version as stale.
3. Treat an equal version as a duplicate only if all lifecycle-relevant
   values match; otherwise reject it as a conflict. Ignore `valid_until`
   for non-active state and compare numeric times by value.
4. Reject a higher version with a decreasing cutoff, a transition out of
   retirement, or a missing cutoff advance required by {{state-semantics}}.
   `event_timestamp` does not order records; a decrease alone is not an error.
5. Retain accepted state durably. An older record MUST NOT overwrite newer
   accepted state. An expired active snapshot cannot establish eligibility.

SET deduplication and state ordering are separate. Neither `jti` nor SET
`iat` substitutes for `version`. Reissuing a SET MUST preserve its lifecycle
state, including `event_timestamp`.

Stale and duplicate events are acknowledged without changing state. Invalid
and conflicting events use the delivery protocol's existing error mechanism;
a conflict SHOULD produce an administrative diagnostic. An acknowledgment
is not evidence that resource enforcement has completed.

A consuming profile specifies clock tolerances, lease limits, application
timing, and recovery. These requirements cannot permit replay to renew a
lease or erase retirement protection. Event discovery and delivery follow
SSF, including existing `events_supported` and stream configuration fields.

# Security Considerations

Receivers apply {{SSF}} and {{RFC8417}}, including signature, issuer,
audience, and subject validation, `secevent+jwt` typing, and SSF's prohibition
on SET `exp`. The eligibility lease does not expire the SET itself.

A valid signature does not authorize the Transmitter for another governing
issuer or receiving tenant. Receivers MUST keep event validation separate
from OAuth grants and access tokens. Local resource permissions remain
independent of lifecycle eligibility.

Rollback protection depends on retained versions and cutoffs. Loss of
retained state requires trusted recovery before relying on active state.
The Authority's truthfulness and the consuming profile's source-coordination
and issuance-time rules determine cutoff effectiveness. Event delivery alone
does not guarantee immediate resource denial.

# Privacy Considerations

Stable subjects permit correlation. Transmitters SHOULD limit events to
authorized receiving domains and minimize identifying information in
`reason_admin` and `reason_user`. Reasons are explanatory text, not policy
inputs or an alternative subject identifier.

# IANA Considerations

The HTTPS event-type identifier uses an author-controlled namespace and
requires no IANA event registration.

## SCIM Schema Registration

This document requests registration of the extension URI in the SCIM
Schema URIs registry under {{RFC7643, Section 10.3}} using the template
below. The SCIM schema identifier remains a proposed registration.

## SCIM Schema Registration Template {#schema-registration}

The registration template required by {{RFC7643, Section 10.3.2}} is:

* Schema URI:
  `urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent`
* Schema Name: Governed Agent Lifecycle Extension
* Intended or Associated Resource Type: Agent
* Purpose: Carry the qualified agent identity and authoritative
  lifecycle state used for provisioning and OAuth enforcement.
* Single-value Attributes: `issuer`, `subject`, `version`, `status`,
  `authorizationCutoff`, `assertedAt`, `validUntil`, as defined in
  {{state-schema}} and mapped to SCIM types in {{scim-schema}}.
* Multi-valued Attributes: None.

--- back

# SCIM State Representation {#scim-binding}

This optional representation exposes the State Record as an extension of
an Agent resource {{SCIM-AGENT}} using {{RFC7643}}. It lets SCIM and
event consumers exchange identical lifecycle values without treating
SCIM ETags as lifecycle versions. It does not require the Transmitter to
operate a SCIM service or the Receiver to create a local resource from
an event.

## SCIM Representation {#scim-schema}

The extension schema URI is:

`urn:ietf:params:scim:schemas:extension:governed-agent:2.0:Agent`

Its name is `GovernedAgentLifecycle`. The State Record has the following
SCIM representation; event field names are not SCIM attribute names.

| SCIM attribute | Event source | SCIM type |
|---|---|---|
| `issuer` | `sub_id.iss` | `string` |
| `subject` | `sub_id.sub` | `string` |
| `version` | `version` | `string` |
| `status` | `status` | `string` |
| `authorizationCutoff` | `authorization_cutoff` | `dateTime` |
| `assertedAt` | `event_timestamp` | `dateTime` |
| `validUntil` | `valid_until`, when active | `dateTime` |

The three time attributes MUST represent the same instants as their
NumericDate event values, using RFC 3339 {{RFC3339}} UTC with uppercase
`T` and `Z`, whole-second precision, and seconds from 00 through 59.
Conversion counts seconds since 1970-01-01T00:00:00Z, ignoring leap seconds.
Receivers MUST compare instants after conversion, not date strings to JSON
numbers. Neither conversion nor a SCIM read can renew an eligibility lease.

All attributes are single-valued, returned by default, and have
uniqueness `none`. All except `validUntil` have `required: true`;
`validUntil` has `required: false` in the schema and is required by this
profile only for active state. SCIM responses omit it for disabled or
retired state. String attributes have `caseExact: true`. Mutability is
`readWrite` except for immutable `issuer` and `subject`. The consumer
enforces uniqueness of the qualified identity within its correlation
scope; the individual attributes are not independently unique.

Providers exposing this representation MUST advertise these
characteristics in `/Schemas`. `status` has the three canonical values
in {{state-semantics}}; the other attributes have no enumeration. SCIM
attribute-name matching follows {{RFC7643}}; the binding decodes those
names to the event claim names through the table above before state comparison.
Ambiguous duplicate attributes MUST be rejected.

The extension represents the same state as an event payload. A SCIM edit
outside the extension does not advance the lifecycle version. SCIM
operations and their effect on a local principal are defined by a
consuming profile, such as {{LIFECYCLE}}.


# Relationship to Existing Events {#existing-events}

The new event reports a complete eligibility snapshot independent of
resource creation, credential issuance, or session revocation. It also
represents lease renewal without a status transition.

| Existing profile | Reuse and boundary |
|---|---|
| SCIM Events {{RFC9967}} | Full create and PUT events can carry the lifecycle extension in a resource. Their subject identifies the publisher's SCIM resource and their version is an ETag; neither replaces the qualified agent or lifecycle version. |
| {{CAEP}} | Session revocation, token-claim changes, and credential changes retain those meanings. They do not by themselves assert agent-wide eligibility or renew a lease. |
| {{WISE}} | Workload disabled, enabled, and purged events overlap the lifecycle transitions. They include workload and credential semantics that need explicit mapping to an Agent Principal. |
| {{RISC}} | Account transitions can inform lifecycle decisions but do not carry this snapshot's version, cutoff, and lease contract. |

A SCIM-based deployment can profile existing full-resource events to
transport this state; a notice requires authoritative retrieval. The
event in this document serves consumers that need a qualified agent
snapshot without a source SCIM-resource identity or resource-change
operation. It does not supersede those events or treat them as
interchangeable.

The event is proposed for coordination with the relevant event-profile
communities. This document does not assign URIs in the CAEP or WISE
namespaces or change their event definitions.

# Document History

Initial version.
