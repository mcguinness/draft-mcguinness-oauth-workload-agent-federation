<!-- regenerate: off (set to off if you edit this file) -->

# OAuth 2.0 Profile for Agent Federation

This is the working area for the individual Internet-Draft, "OAuth 2.0 Profile for Agent Federation".

The draft retains both self-acting WAG and user-delegated ID-JAG, including
subject resolution and linking for each path. The ID-JAG flow defines issuance
from direct workload evidence, governed-actor mapping, `jwt-dpop` redemption,
and DPoP-bound API access. WAG keeps its name and federation requirements in the
main profile; its complete wire contract remains pending upstream coordination.

The core covers external evidence, governed-agent resolution, the permitted
OAuth client and flow, and preservation of the agent in the grant and access
token. Provisioning and account administration are informative deployment
guidance rather than conformance requirements.

Continuing access uses
[Identity Continuation Assertion](https://datatracker.ietf.org/doc/html/draft-mcguinness-oauth-id-continuation-assertion)
through a separate federation composition. The draft records that extension's
identity, binding, and eligibility questions; it does not define ICA exchange
or lifecycle requirements. ICA is an informative dependency. RAS refresh
tokens are not issued; an IdP refresh token can still serve as a new exchange's
subject input.

The optional `instance_attestation` input reuses
[Client Instance Identification for Attestation-Based Client Authentication](https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-assertion/draft-mcguinness-oauth-client-instance-id.html).
Federation maps a validated instance identity to a governed agent and
separately authorizes delegation. The required platform-JWT path and
own-client attestation input do not depend on Identification. No separate
attested-agent claim or draft is defined here.

Attester trust can use configured associations or
[Client Attester Endorsement](https://mcguinness.github.io/draft-mcguinness-oauth-client-instance-assertion/draft-mcguinness-oauth-client-attesters.html).
When selected, endorsement requires both current client metadata and IdP
policy approval. It does not establish a Federation Binding or select instance
identification. Both references track the editor's copies dated 15 September
2026; downstream instance-context propagation remains outside this revision.

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
