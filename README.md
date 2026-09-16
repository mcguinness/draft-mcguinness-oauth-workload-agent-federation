<!-- regenerate: off (set to off if you edit this file) -->

# OAuth 2.0 Profile for Governed Agent Federation

This is the working area for the individual Internet-Draft, "OAuth 2.0 Profile for Governed Agent Federation".

The goal is a prescriptive integration contract for agent-platform vendors
and IdPs: supply workload evidence, bind it to a governed agent and permitted
OAuth client, and obtain downstream authorization. The draft identifies what
the platform, client, IdP, RAS, and API each implement. Its common delegated
path uses an existing SPIFFE JWT-SVID, a user ID Token, native SPIFFE
client authentication at the IdP, `private_key_jwt` at the RAS, and DPoP
at both token endpoints. The client and IdP implement JWT-SVID as the
common input; deployments can select another supported credential profile.

The draft retains both self-acting WAG and user-delegated ID-JAG, including
subject resolution and linking for each path. ID-JAG uses direct workload
evidence, governed-actor mapping, and RFC 7523 `jwt-bearer` redemption with
mandatory grant confirmation checks. WAG keeps its name and federation
requirements; its complete wire contract remains pending upstream coordination.

DPoP remains required at the IdP and RAS token endpoints. Access-token sender
constraint is the default: resource policy can select DPoP, mutual TLS,
or explicitly permitted bearer access. The actor authorization gate is
required; independent agent permissions on every data object are local policy.

The common-path example uses a shared registered platform SSO client and its
corresponding RAS registration, with complete parameter-level HTTP examples.
The identical JWT-SVID is presented as `client_assertion` and `actor_token`.
The IdP validates its audience and trust-domain signature, then resolves its
exact SPIFFE ID to the governed agent. Client Association separately permits
the authenticated client to use that binding. CIMD remains available where
supported, subject to SPIFFE OAuth's client matching rules.

The draft defines no new workload credential format or media type. Existing
platform JWTs and Client Attestation are optional actor inputs. X.509-SVID and
WIT-SVID can authenticate clients; their direct actor-evidence compositions
remain deferred. JWT-SVID retains its bearer semantics: DPoP protects the
issued grant, but does not bind the input credential to its presenter.
Deployments requiring issuer-bound presenter proof must select a supported
input that provides it. No per-replica IdP registration is required.

RAS refresh tokens retain ID-JAG's default recommendation against issuance,
with a constrained exception for authorized long-running work. Refresh tokens
are client- and DPoP-key-bound and retain the original authorization ceiling.
Cross-resource continuing access remains separate composition work with
[Identity Continuation Assertion](https://datatracker.ietf.org/doc/html/draft-mcguinness-oauth-id-continuation-assertion).

[Client Instance Identification](https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-id/draft-mcguinness-oauth-client-instance-id.html)
and
[Client Attester Endorsement](https://mcguinness.github.io/draft-mcguinness-oauth-client-attesters/draft-mcguinness-oauth-client-attesters.html)
are informative extension dependencies, outside core conformance. Their
canonical editor's-copy URLs replace the old repository's redirect stubs.
Configured ATTEST trust and the own-client attestation input remain available.

* [Editor's Copy](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/#go.draft-mcguinness-oauth-workload-agent-federation.html)
* [Datatracker Page](https://datatracker.ietf.org/doc/draft-mcguinness-oauth-workload-agent-federation)
* [Individual Draft](https://datatracker.ietf.org/doc/html/draft-mcguinness-oauth-workload-agent-federation)
* [Compare Editor's Copy to Individual Draft](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/#go.draft-mcguinness-oauth-workload-agent-federation.diff)


## Contributing

See the
[guidelines for contributions](https://github.com/mcguinness/draft-mcguinness-oauth-workload-agent-federation/blob/main/CONTRIBUTING.md).

The contributing file also has tips on how to make contributions, if you
don't already know how to do that.

## Command Line Usage

Formatted text and HTML versions of the draft can be built using `make`.

```sh
$ make
```

Command line usage requires that you have the necessary software installed.  See
[the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).
