<!-- regenerate: off (set to off if you edit this file) -->

# OAuth 2.0 Profile for Agent Federation

This is the working area for the individual Internet-Draft, "OAuth 2.0 Profile for Agent Federation".

The main draft defines delegated ID-JAG issuance from direct workload evidence,
governed-actor mapping, redemption, and DPoP-bound API access. Self-acting WAG
access remains deferred.

The companion [OAuth 2.0 Attested Agent Identity](draft-mcguinness-oauth-attested-agent-identity.md)
is a separate Standards Track draft for the `attested_agent_id` claim and
ATTEST profile. Its [editor's copy](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-attested-agent-identity.html) builds from this repository; it
has not yet been submitted to the Datatracker. The main draft's required
platform-JWT path does not depend on it.

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

Formatted text and HTML versions of both drafts can be built using `make`.

```sh
$ make
```

Command line usage requires that you have the necessary software installed.  See
[the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).

## Supporting material

* [Deployment scenarios](docs/deployment-examples.md)
* [Federation checks and upstream closure cases](docs/interoperability.md)
* [Coordination and design decisions](docs/coordination.md)
* [Review disposition](docs/review-disposition.md)

The [signed delegated example](docs/delegated-example.json) includes public
keys, token requests, responses, and an API request. Check its signatures
and cross-hop consistency with Python 3 and OpenSSL:

```sh
python3 scripts/check-delegated-example.py
```

This verifies example fixtures; it is not an interoperability test between
independent server implementations.
