<!-- regenerate: off (set to off if you edit this file) -->

# OAuth 2.0 Profile for Governed Agent Federation

This is the working area for "OAuth 2.0 Profile for Governed Agent Federation"
and its lifecycle and Shared Signals companions.

The draft defines how an IdP resolves dedicated OAuth client identities or
independently validated workload identities to stable Governed Agents.
Identity Binding, Client Association, user delegation, and resource-local
authorization remain separate decisions.

The mandatory delegated path uses an ID Token issued for the dedicated
client, `private_key_jwt` client authentication, a governed ID-JAG, and RFC
7523 `jwt-bearer` redemption. Dedicated-client resolution uses the authenticated
client context without duplicating its assertion in `actor_token`.
SPIFFE JWT-SVID, existing platform JWT, and
Client Attestation inputs are optional. Shared platforms agree on a workload
input that distinguishes agents behind their SSO client. No new credential
format or per-replica registration is required.

Two governed profiles support incremental adoption. Bound governed agent
access requires DPoP at issuance and redemption; governed agent access permits
unbound grants only under explicit policy. Access-token protection is a
separate choice: DPoP, mutual TLS, or explicitly permitted bearer use. The
API enforces user authority and the actor gate in every governed mode.

The complete dedicated-client walkthrough includes a shared-client SPIFFE
variant. Continuing access uses eligible subject credentials for new ID-JAGs
or policy-permitted RAS refresh within retained authorization and lifetime
limits. Existing SSO refresh tokens do not automatically authorize downstream
resources.

WAG remains the intended self-acting composition with the same governed
identity and local principal correlation. Its wire requirements await
upstream coordination; this revision claims no WAG wire conformance.
Instance identification, attester endorsement, key transition, and Identity
Continuation Assertion compositions remain deferred.

* [Editor's Copy](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/#go.draft-mcguinness-oauth-workload-agent-federation.html)
* [Datatracker Page](https://datatracker.ietf.org/doc/draft-mcguinness-oauth-workload-agent-federation)
* [Individual Draft](https://datatracker.ietf.org/doc/html/draft-mcguinness-oauth-workload-agent-federation)
* [Compare Editor's Copy to Individual Draft](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/#go.draft-mcguinness-oauth-workload-agent-federation.diff)

## Provisioning and Lifecycle Companion

The lifecycle profile composes SCIM, Shared Signals, and OAuth for the same
IdP-qualified identity. It applies ordered state to local correlation,
disablement, reactivation, retirement, and authorization. It defines no new
event type or SCIM schema.

The separate event profile defines Agent State Changed with SSF subject
identification, CAEP common claims, and event-specific lifecycle claims.
Its SCIM mapping carries the same logical state using SCIM attribute names
and dateTime values.
It can be implemented independently of the OAuth enforcement profile.
The lifecycle profile supplies the configured enforcement modes and denial
bounds. WAG remains a future composition using the same principal lifecycle.

* [Lifecycle profile source](draft-mcguinness-oauth-governed-agent-lifecycle.md)
* [Lifecycle profile editor's copy](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-governed-agent-lifecycle.html)
* [Event specification source](draft-mcguinness-ssf-governed-agent-events.md)
* [Event specification editor's copy](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-ssf-governed-agent-events.html)

## Contributing

See the
[guidelines for contributions](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/CONTRIBUTING.md).

The contributing file also has tips on how to make contributions, if you
don't already know how to do that.

## Command Line Usage

Formatted text and HTML versions of all drafts can be built using `make`.

```sh
$ make
```

Command line usage requires that you have the necessary software installed.  See
[the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).
