<!-- regenerate: off (set to off if you edit this file) -->

# OAuth 2.0 Profile for Agent Federation

This is the working area for the individual Internet-Draft, "OAuth 2.0 Profile for Agent Federation".

The main draft defines delegated ID-JAG issuance from direct workload evidence,
governed-actor mapping, redemption, and DPoP-bound API access. Self-acting WAG
access remains deferred.

The optional `instance_attestation` input reuses
[Client Instance Identification for Attestation-Based Client Authentication](https://github.com/mcguinness/draft-mcguinness-oauth-client-instance-assertion/blob/main/draft-mcguinness-oauth-client-instance-id.md).
Federation maps a validated instance identity to a governed agent and
separately authorizes delegation. The required platform-JWT path and
own-client attestation input do not depend on Identification. No separate
attested-agent claim or draft is defined here.

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
