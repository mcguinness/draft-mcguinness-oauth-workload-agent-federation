<a id="flows"></a>

# End-to-End Deployment Examples

These examples are informative. A harness is the software executing
the agent and making OAuth requests. These examples separate its
hosting environment, authentication evidence, and acting relationship:

| Use case | Deployment | Evidence accepted by IdP | Identity model | Grant |
|---|---|---|---|---|
| Agent acting for itself | SPIFFE workload | JWT-SVID, X.509-SVID, or WIT-SVID with DPoP and the input-specific proofs | Agent is the client | AFG |
| Agent acting for itself | Imported cloud or agent-platform agent | Platform-issued JWT and DPoP | Imported workload principal; no OAuth client required | AFG |
| Agent acting for itself | Managed platform | Platform Client Attestation and DPoP | Agents share a client | AFG |
| Agent acting for a user | Managed device | Enterprise Client Attestation and DPoP | Agent is the client | ID-JAG |
| Agent acting for a user | Managed platform | Platform Client Attestation and DPoP | Agents share a client | ID-JAG |
| Agent acting for a user | Imported cloud or agent-platform agent | Platform JWT, separate client credential, user credential, and DPoP | Imported agent with an authorized OAuth client | ID-JAG |

In each example, the IdP maintains the agent's status, owner, groups,
and application assignments. Before issuance, it establishes the
external identity binding and trusts the relevant credential issuer.
The RAS trusts the IdP at `https://idp.example/tenant/acme` as grant
issuer. Administrative configuration, JIT, or SCIM can establish
the downstream agent record, correlated by IdP issuer and agent
identifier. Receiving a grant does not by itself provision a record
or authorize every scope.

The examples request `tickets.read` at `https://api.app.example`
through the RAS `https://as.app.example`. IdP metadata advertises
`token_endpoint=https://idp.example/token`; the examples use that URL
as the default adapter-token audience and acquisition `resource`.
The IdP issuer remains `https://idp.example/tenant/acme`. Each harness controls its
own key, denoted `K`; `JKT(K)` denotes its thumbprint. JWKs sent to
attesters contain only public keys. IdP requests use the evidence and
any client authentication described in each example, with fresh proofs
for the respective endpoints. The illustrated RAS
issues DPoP access tokens bound to that key, satisfying the
sender-constraint requirement in [Grant Consumption](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#consumption).

The following metadata excerpt advertises both grant outputs and the
adapter-based delegated path. Unrelated metadata members are omitted:

~~~ json
{
  "issuer": "https://idp.example/tenant/acme",
  "token_endpoint": "https://idp.example/token",
  "identity_chaining_requested_token_types_supported": [
    "urn:ietf:params:oauth:token-type:afg",
    "urn:ietf:params:oauth:token-type:id-jag"
  ],
  "actor_profile_token_exchange": {
    "subject_token_types_supported": [
      "urn:ietf:params:oauth:token-type:id_token"
    ],
    "actor_token_types_supported": [
      "urn:ietf:params:oauth:token-type:access_token"
    ],
    "requested_token_types_supported": [
      "urn:ietf:params:oauth:token-type:id-jag"
    ]
  }
}
~~~

<a id="self-flow"></a>

## Agent Acting for Itself

The agent is the AFG subject; the flow ends with a
sender-constrained access token for the agent alone. JWT credentials
use direct exchange under [Direct JWT Credential](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#direct-afg). The X.509-SVID example
first illustrates the adapter needed when no JWT credential is
available; the subsequent variants omit that acquisition step.

Direct JWT path:

~~~
 Platform          Harness             IdP          RAS         API
     |-- JWT -------->|                 |            |           |
     |                |-- JWT + proof ->|            |           |
     |                |<----- AFG ------|            |           |
     |                |-------- AFG + DPoP --------->|           |
     |                |<--------- app AT ------------|           |
     |                |-------------- app AT + DPoP ------------>|
~~~

<a id="spiffe-flow"></a>

### SPIFFE Workload with X.509-SVID

Use this model when the workload already has a SPIFFE identity
representing the agent. This example uses X.509-SVID client
authentication under [SPIFFE X.509-SVID](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#spiffe-input), without a Client Attestation
or stable instance identifier. X.509-SVID uses [Obtaining an IdP Access Token When Needed](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#bootstrap) because
the TLS credential is not a JWT subject token. The AFG is specified
in [Agent Federation Grant](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#afg-profile).

~~~
 Workload           Harness            IdP          RAS         API
    API
     |                 |                |            |           |
     |<-- get SVID ----|                |            |           |
     |-- X.509-SVID -->|                |            |           |
     |                 |- credentials ->|            |           |
     |                 |<--- IdP AT ----|            |           |
     |                 |--- exchange -->|            |           |
     |                 |<---- AFG ------|            |           |
     |                 |-------- AFG + DPoP -------->|           |
     |                 |<--------- app AT -----------|           |
     |                 |------------- app AT + DPoP ------------>|
     |                 |<--------------- tickets ----------------|
~~~

1. The harness obtains an X.509-SVID for
   `spiffe://workloads.example/agents/support` from its Workload API.
   The IdP has approved that exact identity and trust domain for
   Registered Agent `agent-42`; trusting the domain alone does not
   admit every workload as that agent.
2. The harness sends a client credentials request to the IdP over
   mutually authenticated TLS, with that SPIFFE ID as `client_id`
   and the selected exchange audience as `resource`. A DPoP proof establishes a
   separate application key `K`. The IdP validates the SVID using
   the configured SPIFFE trust bundle and resolves the agent binding.
3. Under [IdP Access Token](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#idp-access-token), the IdP issues an access token with `sub=agent-42`, the SPIFFE ID as `client_id`, the selected
   exchange audience as `aud`, and `cnf.jkt=JKT(K)`. The TLS credential
   authenticates the workload; `K` binds the issued token.
4. The harness requests AFG using that access token as
   `subject_token`, the target RAS as `audience`, and the API and
   scope above. It again authenticates with its SVID and proves
   possession of `K`. The IdP checks the current binding and policy
   before issuing AFG with `sub=agent-42` and no `act`.
5. The harness redeems AFG at the RAS with a fresh proof from `K`,
   receives the application access token, and calls the API. The
   downstream processing is described in [Downstream Application Processing](deployment-examples.md#app-consumption).

The illustrative bootstrap request is sent over the mutually
authenticated TLS connection established with the X.509-SVID:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...workload-key-proof...

grant_type=client_credentials
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&resource=
  https%3A%2F%2Fidp.example%2Ftoken
~~~

The harness then sends this exchange over mutually authenticated TLS,
using the same SPIFFE identity and DPoP key:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...workload-key-proof...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aafg
&subject_token=eyJ...agent-access-token...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The resulting AFG payload appears in [Grant Construction](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#grant). The harness redeems
it at the RAS:

~~~ http
POST /token HTTP/1.1
Host: as.app.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...grant-key-proof...

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&assertion=eyJ...idp-afg...
&resource=https%3A%2F%2Fapi.app.example
~~~

~~~ json
{
  "access_token": "eyJ...app-access-token...",
  "token_type": "DPoP",
  "expires_in": 600,
  "scope": "tickets.read"
}
~~~

The RAS validates `typ`, resolves the IdP's key by `iss` through its
allowlist, checks `aud`, lifetime, and `jti`, matches `resource` to
the grant, and compares the DPoP proof key to `cnf.jkt` under
[Grant Consumption](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#consumption).

It accepts `agent-42` even if it has not seen that
subject before, applies any Agent Properties and its provisioned
record under [Agent Record Correlation](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#agent-correlation), and issues a DPoP-bound access
token with no refresh token. No client authentication is required
for this redemption.

A SPIFFE workload can have several instances [SPIFFE-CONCEPTS](https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/).
This flow correlates key possession through `cnf.jkt`; it does not
claim a stable runtime identity. A renewed SVID can be used with an
existing eligible token when the approved SPIFFE binding and DPoP
key remain the same. An unrelated identity or replacement DPoP key
cannot use that token.

<a id="jwt-svid-flow"></a>

### JWT-SVID Variant

With [SPIFFE JWT-SVID](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#jwt-svid-input)
configured, the harness obtains a JWT-SVID for the IdP issuer audience.
Its protected header uses `typ=JWT`, `alg=ES256`, and a `kid` selecting a
JWT-SVID signing key in the approved `workloads.example` trust bundle.
This decoded payload deliberately omits optional `iss` and `iat`:

~~~ json
{
  "sub": "spiffe://workloads.example/agents/support",
  "aud": ["https://idp.example/tenant/acme"],
  "exp": 1789128300
}
~~~

The harness authenticates the client with this JWT-SVID and sends the
identical JWT as subject evidence for direct AFG. The separate DPoP proof
is signed with `K` and targets `POST https://idp.example/token`:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-spiffe
&client_assertion=eyJ...jwt-svid...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aafg
&subject_token=eyJ...jwt-svid...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The IdP validates client authentication, identical subject evidence, and
DPoP, resolves `agent-42`, and checks its assignments. It enforces the
credential's association with that binding and `K` before issuing AFG
with `sub=agent-42` and `cnf.jkt=JKT(K)`. Redemption follows the X.509-SVID
example above. The JWT-SVID does not certify `K`; theft before first use
can allow an attacker to establish a different initial association.

For user-delegated access, the harness first acquires an IdP actor token:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...fresh-proof-K...

grant_type=client_credentials
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-spiffe
&client_assertion=eyJ...jwt-svid...
&resource=
  https%3A%2F%2Fidp.example%2Ftoken
~~~

The JWT-SVID's audience remains the IdP issuer. The returned token's
`aud` instead equals the selected exchange resource above; its
`client_id` is the SPIFFE ID, `sub` is `agent-42`, and `cnf.jkt` is
`JKT(K)`. The harness then sends this delegated exchange with an accepted
user credential issued to that client and approval for the requested
agent, user, client, tenant, resource, and scopes:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...next-proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-spiffe
&client_assertion=eyJ...jwt-svid...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid-jag
&subject_token=eyJ...user-id-token...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid_token
&actor_token=eyJ...agent-access-token...
&actor_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The JWT-SVID authenticates the client; the IdP access token supplies the
canonical actor identity. ID-JAG contains the user as `sub`, the IdP's
`agent-42` as `act.sub`, and `cnf.jkt=JKT(K)`. Reusing the JWT-SVID across
these requests requires fresh DPoP proofs from the same key. A renewed
JWT-SVID can authenticate an existing actor token only with the same
binding and key. None of these steps creates an instance identifier.

### WIT-SVID Variant

With [SPIFFE WIT-SVID](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#wit-input) configured, the harness instead obtains a WIT-SVID
for the same SPIFFE ID, binding key `K`. The following decoded payload
omits the optional `iss`; the IdP uses the configured trust anchors
for `workloads.example`. Its protected header uses `typ=wit+jwt`,
`alg=ES256`, and a `kid` selecting a key in that trusted bundle.

~~~ json
{
  "sub": "spiffe://workloads.example/agents/support",
  "iat": 1789128000,
  "exp": 1789131600,
  "cnf": {
    "jwk": {
      "kty": "EC",
      "crv": "P-256",
      "alg": "ES256",
      "x": "VcKVNBZ4IaBAYW3jxM4w3TJFVA7myeUGQyGt-g_yvpQ",
      "y": "f-E-hYE3TAWKwhVv9pej9NABs9SX9XsNO80x57jFTyU"
    }
  }
}
~~~

The harness sends this request over server-authenticated TLS. The
Client Attestation PoP JWT has `aud=https://idp.example/tenant/acme`,
a fresh `iat` and unique `jti`, and the IdP's challenge if supplied.
It uses `typ=oauth-client-attestation-pop+jwt`. Both that proof and
the DPoP proof are signed with `K` using `ES256`.

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
OAuth-Client-Attestation: eyJ...wit-svid...
OAuth-Client-Attestation-PoP: eyJ...attestation-pop...
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=spiffe%3A%2F%2Fworkloads.example%2Fagents%2Fsupport
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aafg
&subject_token=eyJ...wit-svid...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The same WIT-SVID appears in the header and `subject_token`. The IdP
validates it and both proofs, resolves `agent-42`, checks assignments,
and returns AFG with `sub=agent-42` and `cnf.jkt=JKT(K)`. No IdP access
token is acquired. The extra JWK `alg` member does not change the
RFC 7638 thumbprint. The harness redeems AFG and calls the API as
shown above. For user-delegated access, it instead obtains or reuses
an IdP actor token under [Obtaining an IdP Access Token When Needed](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#bootstrap) and [Agent Acting for a User](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-exchange).

<a id="platform-jwt-flow"></a>

### Platform-Issued JWT Variant

Use this model when the IdP imports an agent from a cloud or agent
platform. The following binding uses a shared platform subject plus
an agent identifier and tenant restriction.

Its exact selectors are
`iss=https://agents.cloud.example/tenant/acme`,
`sub=agent-service`, `platform_agent=support-agent-7`, and
`tenant=acme`. Together they identify Registered Agent `agent-42`;
no OAuth client is needed for this self-acting exchange. The issuer
is configured as a dedicated workload credential issuer. The
platform-specific claims are illustrative, not new claim registrations.
Decoded platform JWT:

~~~ json
{
  "iss": "https://agents.cloud.example/tenant/acme",
  "sub": "agent-service",
  "platform_agent": "support-agent-7",
  "tenant": "acme",
  "aud": "https://idp.example/tenant/acme",
  "iat": 1789128000,
  "exp": 1789128600,
  "jti": "plat-4d1e"
}
~~~

The harness generates `K` and presents the JWT only as subject
evidence, with a DPoP proof containing the IdP's nonce:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aafg
&subject_token=eyJ...platform-jwt...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The IdP validates the signature with the configured issuer's keys,
matches every selector, and checks `agent-42`'s assignments. It issues
AFG directly with `sub=agent-42` and `cnf.jkt=JKT(K)`. The harness
redeems AFG at the RAS and calls the API as above. Subsequent AFG
requests can reuse the platform JWT within its permitted age and
lifetime with fresh proofs from `K` under [Platform-Issued JWT](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#platform-jwt-input).
The platform never sees `K`; DPoP binds the grant but does not prove
an independently registered OAuth client identity.

For a platform that already names the individual agent in `sub`,
the binding can instead use only its issuer and that exact `sub`.
Multiple approved bindings can resolve to the same Registered Agent
without forcing platforms to share an OAuth client namespace.

<a id="platform-flow"></a>

### Shared Client in a Managed Platform

Use this model when a hosting platform runs separately governed
agents through one OAuth client. The IdP approves the platform
attester `https://attester.example/tenant/acme` for shared client
`https://platform.example/oauth-client`, mapping its
`agent_id=support-agent-7` to Registered Agent `agent-42`.

The platform attester supplies the Client Attestation. The harness
exchanges it directly for AFG, without an intermediate IdP access token.

1. The control plane launches `support-agent-7`. Its harness generates
   `K`. The attester verifies the launch assignment, runtime
   isolation, and key possession, then issues an attestation with
   `sub` equal to the shared client, `agent_id=support-agent-7`,
   and `cnf.jwk` containing the public key.
   The harness cannot select another agent merely by naming it.
2. The harness follows [Direct JWT Credential](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#direct-afg), sending the shared `client_id`
   and the same attestation in `OAuth-Client-Attestation` and
   `subject_token`, with a DPoP proof from `K`. The IdP resolves
   `(iss, sub, agent_id)` to `agent-42` and authorizes the requested access using the agent's assignments.
3. The IdP returns AFG with `sub=agent-42`, no `act`, and
   `cnf.jkt=JKT(K)`. The harness redeems it
   and calls the API as described in [Downstream Application Processing](deployment-examples.md#app-consumption).

A second runtime can use a different key but the same `agent-42`
principal. This profile assigns no stable runtime identifier. A different agent behind
the shared client has its own binding and permissions. The IdP
does not infer equivalent authority from the common client identity.

<a id="delegated-flow"></a>

## Agent Acting on Behalf of a User

The user is the ID-JAG subject and the Registered Agent its actor;
the flow ends with a sender-constrained access token that carries
both.

<a id="device-flow"></a>

### Harness on a Managed Device

Use this model when an enterprise governs a desktop agent as a
Registered Agent with its own client identity. The example binds
`client_id=https://desktop.example/agents/dev-17` to `agent-17`.
The IdP trusts `https://devices.example/attester` to attest this client.
The managed device, the agent, and the running harness are different
entities; device enrollment does not itself authorize user delegation.

~~~
Enterprise         Harness      User/browser     IdP      RAS     API
attester
    |                 |               |           |        |       |
    |                 |--- sign-in -->|           |        |       |
    |                 |               |- sign-in >|        |       |
    |                 |               |<- code ---|        |       |
    |                 |<--- code -----|           |        |       |
    |< evidence, JWK -|               |           |        |       |
    |-- attestation ->|               |           |        |       |
    |                 |------- code + PKCE ------>|        |       |
    |                 |<------- ID Token ---------|        |       |
    |                 |-- credentials + ATTEST -->|        |       |
    |                 |<-------- IdP AT ----------|        |       |
    |                 |-- user + actor exchange ->|        |       |
    |                 |<-------- ID-JAG ----------|        |       |
    |                 |---------- ID-JAG + DPoP ---------->|       |
    |                 |<------------- app AT --------------|       |
    |                 |-------------- app AT + DPoP -------------->|
    |                 |<---------------- tickets ------------------|
~~~

1. The harness generates `K` and starts sign-in in an external
   browser using an authorization code flow with PKCE under
   [RFC8252](https://www.rfc-editor.org/info/rfc8252). The enterprise records user or administrator approval
   for this agent to read tickets for that user. Sign-in alone is
   not delegation approval.
2. After the browser returns the code, the enterprise attester
   validates device evidence, harness and agent assignment, and key
   possession. The Client Attestation contains:

   * The agent's client identifier as `sub`, without `agent_id`.
   * `cnf.jwk` containing `K`'s public key.

   The harness redeems the code with PKCE and fresh ATTEST
   authentication to obtain its user ID Token. Device evidence and
   issuance APIs remain deployment-specific under [ATTEST](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-attestation-based-client-auth-11).
3. The harness then obtains its IdP access token under [Obtaining an IdP Access Token When Needed](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#bootstrap),
   identifying `agent-17`, the client, and `JKT(K)`, or reuses an eligible token. Acquisition follows the
   interactive wait so the short token lifetime is available for
   exchange. If credentials expire before exchange, the harness
   renews the required evidence and token; it does not bypass checks.
4. The harness follows [Agent Acting for a User](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-exchange), sending the user
   ID Token as `subject_token` and the IdP access token as
   `actor_token`, with fresh ATTEST authentication. The IdP validates
   both identities and the delegation, then issues ID-JAG with
   `sub=user-17`, `act={iss: IdP, sub: agent-17}`,
   and the downstream client identifier `dev-agent-at-app`.
5. The harness redeems ID-JAG and accesses the API as described in
   [Downstream Application Processing](deployment-examples.md#app-consumption), authenticating as `dev-agent-at-app` with
   the separate RAS credential described in [Client Authentication at the RAS](deployment-examples.md#ras-auth). The device
   attester and device record do not become actors.

The redemption request appears in [Client Authentication at the RAS](deployment-examples.md#ras-auth) and the response has
the shape shown above, with `sub=user-17` and `act.sub=agent-17` in
the resulting access token.

If the enterprise only needs existing client-based delegation, the
harness can use the ID-JAG/EMA path in [Deployment and Compatibility](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#deployment) without the
agent bootstrap and actor token. A desktop harness shared by several
separately governed agents instead uses the shared-client binding
illustrated in [Shared Client in a Managed Platform](deployment-examples.md#platform-flow). Device hosting does not select
the identity model automatically.

### Shared Client Variant

For user-delegated work in the shared-client platform deployment of
[Shared Client in a Managed Platform](deployment-examples.md#platform-flow), the harness obtains or reuses an IdP access token
under [Obtaining an IdP Access Token When Needed](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#bootstrap), then follows [Agent Acting for a User](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-exchange) with an
accepted user credential and that actor token. After checking
delegation approval, the IdP issues ID-JAG with the user as `sub` and
`agent-42` as `act`. Its downstream `client_id` is `platform-at-app`;
redemption uses the platform signing service in [Client Authentication at the RAS](deployment-examples.md#ras-auth). The
hosting platform is client context, not an additional actor.

<a id="platform-delegated-flow"></a>

### Imported Platform Agent Acting for a User

The binding in [Platform-Issued JWT Variant](deployment-examples.md#platform-jwt-flow) also permits the IdP-assigned OAuth client
`agent-harness-23` to act as `agent-42`. The harness separately
provisions a client credential, here `private_key_jwt` using key `C`
registered with the IdP. The platform JWT does not authenticate that
client. A platform unable to supply a client credential can use the
self-acting path but cannot use this delegated path by itself.

1. The harness obtains the platform JWT above and generates or retains
   `K`. It authenticates `agent-harness-23` with a client assertion
   signed by `C` and exchanges the platform JWT for an IdP access
   token under [Acquisition from Platform JWT Evidence](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#platform-acquisition). The IdP verifies both the
   agent binding and that this client is permitted to use it.
2. The returned token has `sub=agent-42`, `client_id=agent-harness-23`,
   the selected exchange audience as `aud`, and `cnf.jkt=JKT(K)`.
   Its lifetime is 300 seconds in this example.
3. The harness obtains a user credential for `user-17`, issued to
   `agent-harness-23`, and an applicable user or administrator approval
   for this agent, client, resource, and scope. It requests ID-JAG
   with the user credential as subject and the IdP token as actor,
   authenticating the same client and proving `K` again. No platform
   JWT is included in this request.
4. The IdP checks the token, current platform binding, permitted client,
   user credential, and approval. It issues ID-JAG with `sub=user-17`,
   `act.sub=agent-42`, and the configured downstream
   `client_id=platform-at-app`. The harness redeems it using that
   client's separate downstream credential and proof from `K`, as
   described in [Client Authentication at the RAS](deployment-examples.md#ras-auth), then uses the application token at the API.

The acquisition request is:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=agent-harness-23
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...idp-client-assertion-C...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&subject_token=eyJ...platform-jwt...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt
&resource=
  https%3A%2F%2Fidp.example%2Ftoken
~~~

The client assertion has `iss` and `sub` equal to `agent-harness-23`,
an audience accepted by the IdP for client authentication, short
expiration, and a unique `jti`. It is signed by `C`, independently
of the platform JWT and the DPoP key `K`. The DPoP proof includes
an IdP nonce. The response is:

~~~ json
{
  "access_token": "eyJ...platform-agent-access-token...",
  "issued_token_type":
    "urn:ietf:params:oauth:token-type:access_token",
  "token_type": "DPoP",
  "expires_in": 300
}
~~~

Using that token, the delegated request is:

~~~ http
POST /token HTTP/1.1
Host: idp.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...fresh-proof-K...

grant_type=
  urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange
&client_id=agent-harness-23
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...fresh-idp-client-assertion-C...
&requested_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid-jag
&subject_token=eyJ...user-id-token-for-agent-harness-23...
&subject_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aid_token
&actor_token=eyJ...platform-agent-access-token...
&actor_token_type=
  urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Aaccess_token
&audience=https%3A%2F%2Fas.app.example
&resource=https%3A%2F%2Fapi.app.example
&scope=tickets.read
~~~

The IdP binds the user's credential to the authenticated client,
and the actor token to that same client and `K`. The platform JWT's
`sub` remains `agent-service`; the OAuth client is `agent-harness-23`;
the governed actor is `agent-42`. None of these identifiers substitutes
for the other two. Renewal follows [Continuing Delegated Access](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-lifecycle).

<a id="ras-auth"></a>

## Client Authentication at the RAS

These examples separate the DPoP key `K` from a registered client
signing key `C`. Before delegated access, the RAS has registered
`C`'s public key for the following client; the IdP knows the client-ID
mapping. This is client credential provisioning, independent of the
agent record and of trust in the IdP as grant issuer.

| Deployment | Downstream client | Custody of client signing key C |
|---|---|---|
| Managed device | `dev-agent-at-app` | Protected storage for this managed installation; its public key is enrolled at the RAS |
| Managed platform | `platform-at-app` | Platform signing service; an authorized harness obtains a short-lived assertion without receiving the private key |

At redemption, the harness supplies a fresh `private_key_jwt`
assertion signed with `C`. Its `iss` and `sub` equal the downstream
client identifier, its `aud` is the RAS issuer, and it has a short
expiration and unique `jti`, validated under [RFC7523](https://www.rfc-editor.org/info/rfc7523). A separate
DPoP proof from `K` proves possession of the grant's binding key.
Neither credential substitutes for the other.

The self-acting AFG
example redeems the bound grant with a DPoP proof and no client
authentication, as [Grant Consumption](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#consumption) permits for AFG.

Illustrative desktop redemption; the client assertion and ID-JAG
are different JWTs with different purposes and signing authorities:

~~~ http
POST /token HTTP/1.1
Host: as.app.example
Content-Type: application/x-www-form-urlencoded
DPoP: eyJ...grant-key-proof...

grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer
&assertion=eyJ...idp-id-jag...
&resource=https%3A%2F%2Fapi.app.example
&client_id=dev-agent-at-app
&client_assertion_type=
  urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer
&client_assertion=eyJ...client-key-assertion...
~~~

The RAS uses its client registration to validate the client assertion
and its IdP trust to validate ID-JAG. It does not need to accept the
enterprise or platform attester as an agent-identity authority.
If a deployment instead authenticates the client with ATTEST at the
RAS, it needs a separate, explicit RAS attester trust configuration;
trust in the IdP's grant does not create that relationship.

<a id="app-consumption"></a>

## Downstream Application Processing

Both use cases finish at the same application trust boundary:

1. The harness presents the IdP-issued grant to the RAS using the
   selected grant's redemption procedure and the client authentication
   in [Client Authentication at the RAS](deployment-examples.md#ras-auth), including ID-JAG's downstream client binding.
   Its DPoP proof uses the key named by the grant's `cnf.jkt`.
2. The RAS validates the trusted IdP signature, issuer, audience,
   lifetime, replay state, target resource, scopes, and key proof.
   It resolves the subject and any actor, applies local assignments,
   and issues an API access token. In these examples it retains
   the IdP's principal identifiers and uses a JWT access token.
3. The API receives only its access token and a fresh DPoP proof,
   including the access-token hash under [RFC9449](https://www.rfc-editor.org/info/rfc9449). It validates
   the token and proof, then evaluates resource policy for the agent
   or the user and agent actor. It does not consume the upstream
   SVID, device evidence, Client Attestation, AFG, or ID-JAG.

| Example | Application access-token identity | Key binding |
|---|---|---|
| SPIFFE workload, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Imported platform agent, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Imported platform agent, delegated | User `sub`, `act.sub=agent-42` | `cnf.jkt=JKT(K)` |
| Managed device, delegated | `sub=user-17`, `act.sub=agent-17` | `cnf.jkt=JKT(K)` |
| Managed platform, self-acting | `sub=agent-42`, no `act` | `cnf.jkt=JKT(K)` |
| Managed platform, delegated variant | User `sub`, `act.sub=agent-42` | `cnf.jkt=JKT(K)` |

For delegated tokens, the actor also retains its IdP `iss` under
Actor Profile. The RAS is the access-token
issuer and the API is its audience. Groups and owner relationships
can come from provisioned records or approved claims; user groups
do not supply an agent actor's memberships.

<a id="provisioning-example"></a>

## One Agent Record for Self-Acting and Delegated Access

The RAS has an authenticated SCIM provisioning relationship with
IdP issuer `https://idp.example/tenant/acme`. The IdP provisions the
following Agent resource using [SCIM-AGENT](https://datatracker.ietf.org/doc/html/draft-wzdk-scim-agent-resource-00). The RAS assigns `id`;
the IdP supplies `externalId`. The issuer association is kept with
the provisioning relationship, not encoded in a new SCIM attribute.

~~~ json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Agent"],
  "id": "ra-42",
  "externalId": "agent-42",
  "agentUserName": "support-agent",
  "displayName": "Support Agent",
  "active": true
}
~~~

The application's directory records `ra-42` as a member of group
`support-eng`; its local policy grants that group `tickets.read`.
This is a provisioned group relationship, not a claim inferred from
the agent name or a new group schema. Both grant paths resolve the
same record under [Agent Record Correlation](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#agent-correlation):

| Validated grant | Agent lookup | Record and policy input |
|---|---|---|
| AFG: `iss=https://idp.example/tenant/acme`, `sub=agent-42` | `(iss, sub)` | `ra-42`, member of `support-eng` |
| ID-JAG: `sub=user-17`, `act.iss=https://idp.example/tenant/acme`, `act.sub=agent-42` | `(act.iss, act.sub)` | The same `ra-42` and membership |

For delegated access, the application also evaluates `user-17`'s
permissions and the authorized delegation. The agent's group does
not add that user to the group. An equal `agent-42` from another
issuer does not match this record. Setting `active=false` blocks new
issuance once applied by the relevant server; already-issued tokens
follow the deployment's expiration and revocation behavior.
