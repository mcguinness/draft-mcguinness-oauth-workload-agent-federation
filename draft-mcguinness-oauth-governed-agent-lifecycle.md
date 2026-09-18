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
  FEDERATION:
    title: "OAuth 2.0 Profile for Governed Agent Federation"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-oauth-workload-agent-federation
  AGENT-EVENTS:
    title: "Shared Signals Profile for Agent Provisioning and Session Revocation"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-ssf-governed-agent-events
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-ssf-governed-agent-events.html
  SCIM-AGENT: I-D.wzdk-scim-agent-resource
  RFC7643:
  RFC7644:
  RFC7662:
informative:
  AGENT-MANAGEMENT:
    title: "SCIM Profile for Agent Federation Management"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-scim-agent-federation
    target: https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-scim-agent-federation.html
  ID-JAG: I-D.ietf-oauth-identity-assertion-authz-grant
  RFC7009:
  RFC9967:
  WISE:
    title: "Workload Identity Security Events (WISE) Profile"
    target: https://github.com/identitymonk/openid-wise/blob/main/openid-wise-profile-1_0.md
    author:
      - org: WISE Contributors
  WAG: I-D.carleton-workload-authz-grant
--- abstract

This document profiles SCIM for provisioning issuer-qualified Agent
Principals into a resource domain and applying administrative disablement
to OAuth authorization. Existing SCIM Events can accelerate reconciliation;
existing session-revocation events can invalidate identified authorization
sessions independently of principal state.

The profile defines identity correlation, receiver actions, and the limits
of propagation and resource enforcement. It defines no new SCIM schema,
event type, eligibility lease, or authorization timestamp. Current
administrative state does not establish a history of revocation.

--- middle

# Introduction

Governed Agent Federation {{FEDERATION}} separates agent identity,
client authority, user delegation, and resource authorization. It
identifies an Agent Principal by the pair (IdP issuer, agent identifier),
independently of the client or workload credential used to resolve it.

For delegated access, the Identity Assertion JWT Authorization Grant
(ID-JAG) {{ID-JAG}} carries that principal as the actor. The resource
domain correlates the actor with its local agent record.

This companion defines how a resource domain provisions that principal
and applies changes to its administrative status. The responsibilities are:

| Mechanism | Responsibility |
|---|---|
| SCIM Agent {{SCIM-AGENT}} | Provision and update the local representation, including `active` |
| SCIM Events {{RFC9967}} | Notify the receiver that authoritative provisioning state changed |
| Session revocation | Invalidate identified authorization sessions without changing the principal's administrative status |
| OAuth enforcement | Apply local eligibility and revocation at issuance, refresh, introspection, and API access |

~~~
 Enterprise IdP / connector                  Resource domain
 +------------------------+                 +----------------------+
 | Agent Principal        | ---- SCIM ---->  | Local agent principal|
 | Administrative state   |                  | Correlation + active |
 +------------------------+                 +-----------+----------+
       |                                                |
       +---- change notice --> reconciliation           v
                                             RAS issuance / refresh
       +---- session revocation ------------> session invalidation
                                                        |
                                                        v
                                            API token enforcement
~~~
{: #lifecycle-model title="Administrative state and authorization revocation"}

SCIM is the provisioning baseline. Shared Signals is an optional addition,
profiled in {{AGENT-EVENTS}} using existing event types. A deployment can
use direct SCIM updates, event-driven reconciliation, or both, provided
that they apply the same authoritative administrative decisions.

Disabling a principal and revoking a session are separate actions. Once
applied, disablement prevents new authorization and invalidates existing
RAS authorization for that principal. Re-enablement permits new decisions;
it does not restore revoked sessions. Neither an event acknowledgment nor
a SCIM response proves that every API has stopped accepting issued tokens.

## Scope

This profile covers IdP-to-resource-domain provisioning for delegated
Federation. It does not define:

* Platform enrollment or administration of Identity Bindings and Client
  Associations; {{AGENT-MANAGEMENT}} defines that separate interface.
* A new lifecycle state machine, signed eligibility lease, authorization
  cutoff, or distributed ordering protocol.
* Selective revocation of a binding or user delegation, or a WAG wire
  profile.
* A guarantee that an unobserved disable-and-reenable cycle invalidates
  all previously issued grants or sessions.

{{recovery}} and {{enforcement}} state the recovery and enforcement
limits. Deployments requiring stronger revocation-history guarantees need
an additional composition; timestamps in ordinary resource metadata do
not provide those guarantees.

# Conventions and Terminology

{::boilerplate bcp14-tagged-bcp14}

Agent Principal, Governance Tenant, Target Tenant, and resource
authorization server (RAS) follow {{FEDERATION}}. SCIM terms follow
{{RFC7643}} and {{RFC7644}}.

Provisioning Authority:
: The IdP governing the Agent Principal. An authorized connector can
  provision its decisions into the resource domain.

Receiver:
: The resource-domain SCIM service provider and the components applying
  accepted changes at the RAS. They form one administrative deployment;
  they need not run in one process.

Provisioning Context:
: Trusted configuration identifying one governing IdP issuer and one
  receiving Target Tenant, together with the connectors authorized to
  manage their correlation and administrative state.

Authorization Session:
: RAS state retaining the identity and authority derived from a grant,
  including any associated refresh authorization and access tokens. This
  is a processing concept, not a new token or wire identifier.

Local Suspension:
: A resource-domain restriction independent of the Provisioning Authority's
  administrative state. Upstream activation cannot clear it.

# Conformance and Configuration {#conformance}

Conformance requires the SCIM provisioning and OAuth receiver behavior in
this document. Events are optional; a deployment using them MUST apply
{{AGENT-EVENTS}}. Support for events alone is not conformance to this
lifecycle profile.

Before provisioning, the parties MUST establish:

* The Provisioning Context and authenticated connectors authorized for it.
* The SCIM base URI and access controls that select that context.
* The RAS and API token populations to which lifecycle enforcement applies.
* Reconciliation responsibilities, stale-state policy, and resource
  enforcement settings under {{recovery}} and {{enforcement}}.

A connector authorized for one context MUST NOT modify another context's
principal or correlation. Multiple writers MAY represent the same
Authority, but MUST reconcile against its current decisions rather than
replay queued activation writes after newer disablement. SCIM conditional
updates protect receiver resource versions; they do not order independent
source decisions.

The IdP continues to enforce current eligibility when issuing grants under
{{FEDERATION}}. This profile adds resource-domain application of that
state; it does not make SCIM availability or event delivery part of client
authentication.

# Identity and Local Correlation {#identity}

The federation identity remains the exact pair (IdP issuer, Agent
Principal identifier). A Target Tenant scopes local policy and correlation;
it is not an additional component of that identity.

For this provisioning interface:

* The governing issuer MUST come from the authenticated Provisioning
  Context, not from a caller-selected attribute.
* The connector MUST set the Agent's `externalId` to the exact Agent
  Principal identifier in that issuer's namespace.
* The Receiver MUST enforce uniqueness of `externalId` within that
  context, including concurrent creates. This is an explicit narrowing
  of SCIM's client-scoped `externalId` behavior.
* Once established, the pair MUST NOT change through a resource update.
  Attempts to change `externalId` use SCIM's `mutability` error.

Thus, `externalId` alone is not a globally qualified identity. A deployment
with multiple IdPs MUST retain the context with each resource; it cannot
merge records on equal `externalId` values across issuers. This use of
`externalId` is specific to the IdP-to-resource interface. A platform's
`externalId` at the IdP remains its own provisioning correlation value.

For delegated access, the RAS MUST resolve the validated ID-JAG's
`act.iss` and `act.sub` to this pair within the authorized Target Tenant.
It MUST NOT use the user subject, OAuth client, display name, or token
issuer as a substitute. Comparisons are exact, without case folding or
URI rewriting.

The Receiver MUST correlate the pair with at most one local agent
principal in the Target Tenant. An existing service principal MAY supply
that local representation, but attaching it requires explicit local
authorization. The SCIM Agent is then a management view of that same
principal, not a second authorization identity.

This profile raises Federation's provisioning recommendation to a
requirement: the RAS MUST have the authorized local correlation before
accepting a grant involving the agent. A missing or ambiguous correlation
fails under Federation's identity-resolution error rules.

# SCIM Provisioning {#scim}

The interface uses `/Agents` and the attributes of {{SCIM-AGENT}},
including required `agentUserName`, plus the common attributes of
{{RFC7643}}. It defines no extension schema. Receivers MUST support
creation, retrieval, filtering by `externalId`, PATCH, and deletion using
{{RFC7644}}.

## Creation and Updates

Creation requests MUST contain `externalId` and an explicit boolean
`active`. Only `active: true` permits authorization evaluation. Missing
required values use `invalidValue`; conflicting correlation values use
`uniqueness`, following SCIM's error model.

Within the authenticated Provisioning Context, a connector can reconcile
using:

~~~ http
GET /scim/v2/Agents?filter=externalId%20eq%20%22agent-42%22
~~~

The Receiver MUST restrict the result to that context. Names, owners,
groups, and other descriptive attributes do not select the governed
identity or grant delegation.

Receivers MUST support ETags and return `meta.version` on complete
resource representations. Connectors MUST use `If-Match` for updates and
deletion of existing resources. A failed precondition uses HTTP 412 under
{{Section 3.12 of RFC7644}}; the connector retrieves current state and
reconciles its intended change before retrying.

`meta.version` is an opaque resource validator, not a monotonic lifecycle
counter. `meta.lastModified` is the time the service provider modified the
resource, not a source decision time or a grant-revocation boundary. A
descriptive edit can change both without affecting authorization.

## Applying Administrative State {#application}

The Receiver MUST authorize changes to `active` separately from permission
to edit descriptive attributes. It MUST preserve Local Suspension and
resource permissions independently of upstream administrative updates.

| Applied action | New RAS authorization | Existing RAS authorization |
|---|---|---|
| Create or set `active: true` | Evaluate correlation, local status, and all Federation checks | Does not restore previously revoked sessions |
| Set `active: false` | Deny grant redemption and refresh involving this principal | Revoke associated authorization sessions |
| Delete the local Agent | Deny because the authorized correlation is absent | Revoke associated authorization sessions |
| Change display name, owner, or other descriptive data | No implicit change to eligibility or delegation | No implicit revocation or grant of authority |

Before reporting successful application of disablement or deletion, the
Receiver MUST make the restriction effective for RAS decisions beginning
after the response. If session invalidation is asynchronous, a local
restriction MUST deny use of the affected sessions until invalidation
completes. In-flight decisions may already have completed; API observation
of revocation follows {{enforcement}}.

Reactivation MUST NOT cancel pending invalidation or restore revoked
sessions. Recreating a deleted representation likewise does not restore
revoked authorization. Receivers MUST retain revocation state for as long
as affected tokens or refresh authorizations could otherwise be accepted.
This does not require retaining the deleted SCIM resource.

Deleting a local representation does not prove that the IdP retired the
Agent Principal globally. Permanent retirement and non-reassignment remain
authority responsibilities under {{FEDERATION}}.

## Effective Eligibility

The SCIM `active` value reports administrative state received through this
interface. Effective eligibility also requires an authorized correlation,
no Local Suspension, and applicable resource policy. Local Suspension need
not be exposed through this SCIM interface.

Owners provide accountability; they are not automatically user delegators.
Group membership has only the meaning assigned by local policy. Neither
provisioning nor a successful administrative write opens the actor gate.

# Signals and Reconciliation {#recovery}

{{AGENT-EVENTS}} profiles SCIM change notices and CAEP session revocation
over Shared Signals. The two have different processing:

* A change notice triggers reconciliation with an authoritative source.
  It is not an instruction to apply an old resource snapshot.
* Session revocation invalidates identified RAS authorization. It does
  not set the Agent's `active` value.

For event-driven reconciliation, the parties MUST configure the source
SCIM service, retrieval authorization, and mapping from its resource
identifier to the qualified agent and Target Tenant. The source and
receiver SCIM `id` values need not match. A GET of the receiver's own
replica does not establish the Authority's current state.

Direct SCIM connectors and event-driven workers MUST coordinate local
writes through the same correlation and conditional-update rules. A
reconciliation worker reads the receiver's ETag before retrieving source
state, then uses that ETag for its conditional write. After a conflict,
it retrieves both again. This prevents an in-flight fetch from overwriting
a later local restriction; it does not create a cross-domain transaction
or establish that a remote source replica is current.

Deployments SHOULD periodically reconcile managed principals even when an
event stream appears operational. They MUST document how source outages
and incomplete reconciliation affect continued reliance on local state.
A deployment claiming a maximum stale-state interval needs an authoritative
revalidation mechanism and a policy that denies new authorization and
refresh when that interval expires. Receiving traffic or reading the
Receiver's replica alone does not satisfy such a revalidation policy.

Transport failure, access denial, and partial list results MUST NOT be
interpreted as authoritative deletion. They leave reconciliation
incomplete. An authoritative absence for a previously mapped resource
requires disablement or deletion of its local representation; the receiver
must distinguish that absence from a visibility or authorization failure.

A stream verification event proves neither an individual agent's status
nor completion of resource enforcement. A delivery acknowledgment confirms
acceptance under the transport, not API denial.

## Missed Transitions and Reactivation {#missed-transitions}

Current state does not establish transition history. If disablement and
reactivation both occur between successful observations, a later active
resource does not reveal the missed revocation. A different ETag can also
result from an ordinary descriptive edit; it does not identify that history.

Consequently, this profile does not guarantee rejection after reactivation
of an old unredeemed ID-JAG or an authorization session whose revocation
was never observed. Grant validation, replay prevention, and expiration
still apply. Sessions actually revoked by the RAS remain revoked.

Deployments requiring revocation to survive every missed transition need
retained revocation history, an authoritative authorization check, or a
separately specified authorization-generation mechanism. SCIM modification
times, SET issuance times, and event timestamps MUST NOT be treated as
interchangeable grant-issuance cutoffs under this profile.

# OAuth Enforcement {#enforcement}

## RAS Processing

The RAS MUST check current locally applied eligibility at grant redemption
and refresh, in addition to Federation's validation and actor gate. It MUST
retain enough association to invalidate authorization sessions by the
qualified agent and Target Tenant, including related refresh tokens.

Refresh MUST NOT bypass a principal restriction or restore revoked
sessions. No additional grant issuance-time claim, comparison with a
lifecycle timestamp, or original-grant timestamp retention is required by
this companion.

The RAS MUST report revoked or disabled authorization as inactive under
{{RFC7662}}. Once reactivated, the principal may establish new authorization
under ordinary Federation processing, subject to {{missed-transitions}}.
Existing tokens whose agent correlation cannot be established MUST NOT be
represented as covered by this profile; a deployment can obtain new grants
or establish that correlation from trustworthy retained issuance records.

## Resource Enforcement and Delay {#api-enforcement}

The API applies Federation's token validation, actor gate, tenant, and
sender-constraint rules. The following are deployment choices, not new
conformance levels:

| Resource processing | When an applied RAS revocation becomes visible |
|---|---|
| Introspection on each request | On the next successful authorization check; a failed or timed-out check cannot authorize the request |
| Cached introspection | After any permitted active-response cache entry expires or is invalidated |
| Offline JWT validation | At token expiration, unless an independent local restriction takes effect earlier |

Caching follows Federation and {{Section 4 of RFC7662}}. In particular,
cached active responses cannot outlive token expiration or the configured
freshness limit. Offline validation does not consult principal lifecycle
state by itself. The RAS and API MUST configure token lifetimes, expiry
leeway, and caching consistently with their accepted revocation delay.

Deployments SHOULD document their expected and maximum disablement delays,
including propagation, reconciliation, local application, token lifetime,
and caching. A SCIM acknowledgment is not the starting point of an
end-to-end guarantee from the Authority's original decision. Without a
bound on propagation and enforcement, this profile claims no finite
end-to-end denial bound. A local stale-state restriction can limit new
issuance; it does not by itself revoke already-issued tokens.

# Relationship Boundaries {#relationship-changes}

| Change | Boundary |
|---|---|
| Disable an Identity Binding | Stop new grants through that binding; other bindings remain independent |
| Withdraw a Client Association | Stop that client use; do not infer agent-wide disablement |
| Revoke a user's delegation | Affect that delegation, not unrelated users or self-acting authority |
| Revoke a workload credential | Apply credential validation and IdP policy; do not automatically retire the Agent Principal |
| Revoke a RAS session | Invalidate that session; do not change principal eligibility |

{{FEDERATION}} defines the first three authorization relationships.
Selective downstream revocation needs identification of the affected
sessions or relationships; the agent's identity alone cannot distinguish
them. OAuth token revocation {{RFC7009}} can revoke a known token at its
issuing server but is not a principal-provisioning or cross-domain
notification protocol.

{{WISE}} can inform the IdP about workloads and credentials. The IdP must
evaluate those changes against its Identity Bindings before deciding on
agent-wide action. Sharing a credential source does not merge principals;
losing one credential does not necessarily disable a principal with other
valid bindings.

## Self-Acting Access

The intended {{WAG}} composition correlates the same Agent Principal with
the same local principal. Delegated access preserves the qualified actor
in `act`; self-acting access represents the correlated agent as a local
subject. Their authority remains distinct. This document defines no WAG
wire composition or additional WAG claim.

# Security Considerations

Provisioning writers can enable principals and change eligibility. Their
authority must remain scoped to the configured issuer and Target Tenant.
An event signature, matching display name, or equal `externalId` outside
that context does not establish permission to correlate a principal.

Conditional writes prevent stale updates to a known receiver version;
they do not prove that a connector consulted current source state.
Compromised or stale connectors can re-enable principals if their write
permission remains valid. Administrative authorization, reconciliation,
and local suspension therefore remain separate controls.

Event loss and reordering can delay enforcement. Receivers should retry
reconciliation, monitor failures, and retain revoked-session state across
restarts. Recovery from lost revocation state must not silently restore
sessions represented as revoked. The explicit limit in
{{missed-transitions}} is particularly relevant to unattended refresh.

A disabled principal may still have tokens accepted by an offline API.
Token expiry and cached responses must be included in operational claims;
stopping issuance alone does not terminate ongoing work or retract
operations already performed.

# Privacy Considerations

The qualified identity permits correlation across users and resources.
Provisioning and event access SHOULD be limited to the receiving domains
that need it. Logs should retain administrative actions and affected
identities without copying reusable grants, access tokens, or credentials.

# IANA Considerations

This document requests no IANA actions.

--- back

# Shared Delegated Federation Walkthrough {#example}

This non-normative walkthrough uses the dedicated-client exchange in
{{FEDERATION}}. It is a specification walkthrough, not an executed
implementation test.

## Correlate and Provision

The authenticated provisioning context binds `https://idp.example/` to
Target Tenant `acme-data`. The RAS resource is
`https://api.example/tenants/acme-data/`. The connector creates this Agent:

~~~ json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Agent"],
  "externalId": "agent-42",
  "agentUserName": "analysis-agent",
  "displayName": "Data analysis agent",
  "active": false
}
~~~

The RAS assigns SCIM `id` `local-108` and correlates the context's
`(https://idp.example/, agent-42)` with that local agent principal. Alice
is separately represented as `user-108`; the client is `analysis-api`.
Neither is the agent's correlation identifier.

## Activate and Exchange

The connector reads the resource and receives ETag `W/"a1"`. At 12:01 UTC
on September 17, 2026, it applies:

~~~ http
PATCH /scim/v2/Agents/local-108 HTTP/1.1
Host: ras.example
Authorization: Bearer CONNECTOR_ACCESS_TOKEN
Content-Type: application/scim+json
If-Match: W/"a1"

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{"op": "replace", "path": "active", "value": true}]
}
~~~

The placeholder connector token is not a test credential. The Receiver
returns a new ETag. At 12:01:03, the IdP issues the walkthrough's ID-JAG
for Alice with `act.iss` `https://idp.example/` and `act.sub` `agent-42`.
No lifecycle timestamp is added to the grant or compared with its `iat`.

At redemption, the RAS correlates that pair in `acme-data`, checks local
eligibility and Federation policy, and issues an access token. This
example uses introspection. A policy-permitted refresh retains the same
user, agent, client, tenant, resource, and authority constraints.

## Disable and Re-enable

At 12:02, an authorized connector sets `active: false` using the current
ETag. Before returning success, the Receiver blocks new RAS authorization
and makes existing sessions unusable at the RAS. Subsequent introspection
reports those tokens inactive. An API using a previously cached response
can continue to accept it only within its configured cache policy.

Alternatively, a SCIM change notice can trigger an authoritative GET and
the same local update. {{AGENT-EVENTS}} shows that notice and a separate
CAEP session-revocation example; session revocation need not disable the
principal.

At 12:03, reactivation permits new authorization decisions. It does not
restore the sessions revoked at 12:02. If the Receiver missed the entire
disable-and-reenable cycle, a later active GET alone cannot establish
that those sessions were revoked. An old unredeemed grant is likewise
subject to normal grant validation, not a new lifecycle cutoff.

## Acceptance Checklist {#acceptance-checklist}

| Case | Expected result |
|---|---|
| Equal `externalId` under a different IdP context | Distinct qualified identity; no automatic correlation |
| Stale `If-Match` | HTTP 412; retrieve and reconcile before retrying |
| Descriptive edit | Resource ETag may change; no implicit authorization change |
| Applied disablement | New redemption and refresh denied; existing RAS sessions revoked |
| Reactivation after applied disablement | New decisions allowed; revoked sessions stay revoked |
| Delayed activation notice | Retrieve current source state; do not apply the notice as an activation command |
| Entire disable-and-reenable cycle missed | Current active state cannot recover revocation history |
| Source unavailable | No activation inferred; local stale-state policy applies |
| SCIM success or SET acknowledgment | Does not establish immediate API denial |
| Offline JWT | May remain usable until expiration unless separately restricted |

# Document History

Initial version.
