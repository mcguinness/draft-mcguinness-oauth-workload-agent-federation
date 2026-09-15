<a id="flows"></a>

# Delegated agent-federation examples

The [main draft](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#delegated-flow) defines the protocol. [Signed example data](delegated-example.json) supplies complete compact JWTs, public keys, request forms, and response bodies for the required path. The examples use synthetic identities and a fixed evaluation time; they are not credentials for a live service.

## Configuration

| Relationship | Value |
|---|---|
| IdP issuer / token endpoint | `https://idp.example/tenant/acme` / `https://idp.example/tenant/acme/token` |
| RAS issuer / token endpoint | `https://as.app.example` / `https://as.app.example/token` |
| API resource | `https://api.app.example/tickets` |
| Client at IdP / RAS | `idp-agent-client` / `ras-agent-client` |
| External actor | (`https://platform.example`, `support-bot-7`) |
| Governed actor | (`https://idp.example/tenant/acme`, `agent-42`) |
| User at IdP / RAS | `user-17` / `app-user-17`, associated by a trusted mapping |

The IdP has approved the external-to-governed binding and the delegation to `agent-42`. The two client registrations use different authentication keys. One DPoP key binds the grant, access token, and API request. The API's trusted configuration requires this profile on the tickets path and permits this RAS to assert actors in the IdP namespace.

## Issuance

After the client obtains the user's ID Token through OpenID Connect, it sends the following form fields to the IdP. Token labels below identify exact compact JWTs in the signed example file. The form is URL-encoded in transmission.

```text
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
requested_token_type=urn:ietf:params:oauth:token-type:id-jag
subject_token_type=urn:ietf:params:oauth:token-type:id_token
subject_token=<user_id_token>
actor_token_type=urn:ietf:params:oauth:token-type:jwt
actor_token=<platform_actor>
audience=https://as.app.example
resource=https://api.app.example/tickets
scope=tickets.read tickets.write
client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
client_assertion=<idp_client_assertion>
```

The request's `DPoP` header carries `issuance_proof`. The IdP validates the user, actor, client assertion, and proof independently, resolves `support-bot-7` to `agent-42`, and authorizes only `tickets.read`. Here policy permits partial scope approval; policy requiring full approval would reject this request with `invalid_scope` instead.

The ID-JAG retains `sub=user-17`, has `client_id=ras-agent-client`, and carries this actor:

```json
{"iss":"https://idp.example/tenant/acme","sub":"agent-42","sub_profile":"ai_agent"}
```

The response uses `issued_token_type=urn:ietf:params:oauth:token-type:id-jag` and `token_type=N_A`. Its grant has `typ=oauth-id-jag+jwt`, the RAS issuer audience, the authorized resource and scope, and the issuance DPoP key's thumbprint in `cnf.jkt`.

## Redemption and API access

The client authenticates at the RAS using `ras_client_assertion`, supplies a fresh `redemption_proof` in `DPoP`, and sends:

```text
grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
assertion=<id_jag>
resource=https://api.app.example/tickets
client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
client_assertion=<ras_client_assertion>
```

The RAS checks the grant and its bound key, resolves the user and agent separately, and applies its own authorization policy. The response uses `token_type=DPoP`. The JWT access token has:

* RAS `iss`, resource `aud`, and local user `sub=app-user-17`.
* The unchanged IdP-qualified `act` object for `agent-42`.
* The same `cnf.jkt` and the narrowed `tickets.read` scope.

The client then sends `Authorization: DPoP <access_token>` and `DPoP: <api_proof>` to the API. The proof covers that resource request and the access-token hash. The API validates both user and actor authority. Missing or malformed `act` produces HTTP 401 `invalid_token`; a valid token whose required actor authorization fails produces HTTP 403 `actor_unauthorized`. The API does not switch to non-delegated processing when `act` is absent.

## Discovery

Example IdP extension metadata:

```json
{"agent_federation":{"issuance":true,"actor_inputs_supported":["platform_jwt","spiffe_jwt_svid","client_attestation","instance_attestation"]}}
```

Example RAS extension metadata:

```json
{"agent_federation":{"redemption":true}}
```

These are fragments. The full metadata also includes the issuer, endpoints, base grant capabilities, supported client authentication methods, and DPoP algorithms required by the draft. Advertising support does not authorize a trust relationship.

<a id="jwt-svid-flow"></a>

## Optional native JWT-SVID actor

The client presents the exact JWT-SVID as both `actor_token` and `client_assertion`, with the SPIFFE OAuth `jwt-spiffe` assertion-type URI. Its sole audience is `https://idp.example/tenant/acme`, the IdP issuer; the `private_key_jwt` assertion in the required path instead uses the token endpoint URL. The authentication-method metadata value is `spiffe_jwt` under SPIFFE OAuth.

The IdP validates native authentication and maps the exact SPIFFE ID to `agent-42`; the remaining issuance and redemption steps are unchanged. The user ID Token's audience identifies the authenticated client according to SPIFFE OAuth's client association. Optional JWT-SVID `iss` and `iat` remain optional.

<a id="device-flow"></a>
<a id="shared-client-flow"></a>

## Optional attested actor

For either attestation mode, the exact compact Client Attestation appears in `actor_token` and `OAuth-Client-Attestation`. The request uses the configured ATTEST proof mode, and the DPoP output key matches the attestation confirmation key.

Own-client mode resolves the attester identified by the trusted verification key and the client `sub`. The optional `instance_attestation` mode uses [Client Instance Identification](https://github.com/mcguinness/draft-mcguinness-oauth-client-instance-assertion/blob/main/draft-mcguinness-oauth-client-instance-id.md). It validates the signed `iss` and `client_instance_id`, the authenticated client association, and Identification's Receiver requirements before applying the Federation Binding.

For example, two attestations for the same shared client can contain these instance identities:

| Attester `iss` | `client_instance_id` | Approved governed agent |
|---|---|---|
| `https://attester.example/tenant/acme` | `i-7f3d9a2e6c8145b0a923d47e18f602cd` | `agent-42` |
| `https://attester.example/tenant/acme` | `i-b92c817fa6d043e59b7816c3a042de85` | `agent-42` |

Each request still needs proof under its attestation key and separate user-to-agent delegation approval. Both produce the governed actor `act={"iss":"https://idp.example/tenant/acme","sub":"agent-42"}`. Neither instance identifier is copied into `act`; downstream instance context is outside this revision.

A replacement instance receives an identifier under Identification's lifecycle rules and needs an approved new binding, which may resolve to `agent-42`. If a single instance instead maps ambiguously to two agents, this input is rejected with `actor_unauthorized`. An invalid instance claim or rejection by instance policy uses Identification's `invalid_client_attestation` error, with no own-client fallback.

## Other credentials and deferred self-acting access

X.509-SVID and WIT-SVID can authenticate the OAuth client when a supported actor JWT is also supplied. For example, a hosting platform's X.509-SVID identifies the OAuth client while `platform_actor` resolves to `agent-42`. The platform client needs permission to use that actor binding, but needs no Registered Agent record of its own.

Neither credential is claimed as a sole actor input in this revision. Direct WIT-SVID actor processing is a local scope deferral: its attestation proof already exists, but composing its output key must account for WIT's prohibition on using the key after credential expiry. Self-acting WAG access remains deferred; there is no WAG wire example or alternate grant here.

## Optional continuing access

The required example issues no RAS refresh token. If a deployment permits that exception with a one-hour continuation period, a grant with `iat=T` establishes a deadline of `T+3600`. Rotation or repeated redemption of that grant cannot advance the deadline, and access tokens issued under the exception cannot outlive it. Continued access beyond that deadline requires a new ID-JAG and the normal profile checks. Withdrawal of RAS authorization or an authenticated upstream disablement notification terminates further issuance earlier. Without a status signal, upstream changes can remain unknown during the configured period.

## Checking the example

Run `python3 scripts/check-delegated-example.py` from the repository. The check verifies nine JWT signatures, rejects tampering, checks the public keys, and follows user/actor namespaces, client bindings, resource and scope ceilings, and DPoP continuity through both token endpoints and the API.

This checks example consistency, not full conformance or interoperability between independent implementations. The [interoperability cases](interoperability.md) describe the implementation checks separately.
