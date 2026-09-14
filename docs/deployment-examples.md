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

The IdP has approved the external-to-governed binding and the delegation to `agent-42`. The two client registrations use different authentication keys. One DPoP key binds the grant, access token, and API request.

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

The request's `DPoP` header carries `issuance_proof`. The IdP validates the user, actor, client assertion, and proof independently, resolves `support-bot-7` to `agent-42`, and authorizes only `tickets.read`.

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

The client then sends `Authorization: DPoP <access_token>` and `DPoP: <api_proof>` to the API. The proof covers that resource request and the access-token hash. The API validates both user and actor authority.

## Discovery

Example IdP extension metadata:

```json
{"agent_federation":{"issuance":true,"actor_inputs_supported":["platform_jwt","spiffe_jwt_svid","client_attestation","shared_client_attestation"]}}
```

Example RAS extension metadata:

```json
{"agent_federation":{"redemption":true}}
```

These are fragments. The full metadata also includes the issuer, endpoints, base grant capabilities, supported client authentication methods, and DPoP algorithms required by the draft. Advertising support does not authorize a trust relationship.

<a id="jwt-svid-flow"></a>

## Optional native JWT-SVID actor

The client presents the exact JWT-SVID as both `actor_token` and `client_assertion`, with the SPIFFE OAuth `jwt-spiffe` assertion-type URI. The IdP validates native authentication and maps the exact SPIFFE ID to `agent-42`; the remaining issuance and redemption steps are unchanged. The user ID Token's audience identifies the authenticated client according to SPIFFE OAuth's client association. Optional JWT-SVID `iss` and `iat` remain optional.

<a id="device-flow"></a>
<a id="shared-client-flow"></a>

## Optional attested actor

For either attestation mode, the exact compact Client Attestation appears in `actor_token` and `OAuth-Client-Attestation`. The request uses the configured ATTEST proof mode, and the DPoP output key matches the attestation confirmation key.

Own-client mode resolves the attester identified by the trusted verification key and the client `sub`. Shared-client mode uses the [companion profile](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-attested-agent-identity.html#shared-agent), which requires the signed `iss` and `attested_agent_id`. Both resolve the governed agent before actor construction; neither copies a shared OAuth client identifier into `act.sub`.

## Other credentials and deferred self-acting access

X.509-SVID and WIT-SVID can authenticate the OAuth client when a supported actor JWT is also supplied. Neither is claimed as a sole actor input in this revision. Self-acting WAG access remains deferred; there is no WAG wire example or alternate grant here.

## Checking the example

Run `python3 scripts/check-delegated-example.py` from the repository. The check verifies nine JWT signatures, rejects tampering, checks the public keys, and follows user/actor namespaces, client bindings, resource and scope ceilings, and DPoP continuity through both token endpoints and the API.

This checks example consistency, not full conformance or interoperability between independent implementations. The [interoperability cases](interoperability.md) describe the implementation checks separately.
