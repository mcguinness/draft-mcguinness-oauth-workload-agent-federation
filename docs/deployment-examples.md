<a id="flows"></a>

# Federation deployment scenarios

These scenarios illustrate identity resolution and the intended authorization result. They are not complete wire examples for unresolved grant compositions. The draft's [upstream proposals](https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-oauth-workload-agent-federation.html#upstream-gaps) identify the missing contracts; no placeholder WAG identifiers or adapter-token requests are supplied here.

The IdP governs `agent-42` in `https://idp.example/tenant/acme`. The resource is `https://api.app.example`, whose authorization server is `https://as.app.example`. The same agent may have several approved external bindings. Those bindings are configuration, not proof that every input/output combination is implemented.

<a id="self-flow"></a>

## Intended authorization identities

| Situation | Desired result | What still needs definition |
|---|---|---|
| Agent acts for itself | WAG subject identifies `agent-42` in the IdP namespace | IdP issuance, bound WAG semantics, and discovery |
| Agent acts for `user-17` | ID-JAG subject is the user; actor identifies `agent-42` in the IdP namespace | Direct mapped-actor construction and consuming ID-JAG rules |
| Agent restarts | Same governed authorization principal | Any execution identifier and propagation belong to Identification and its consumer |

<a id="jwt-svid-flow"></a>

## SPIFFE JWT-SVID

The IdP trusts JWT-SVID signing keys for `workloads.example` and maps the exact SPIFFE ID `spiffe://workloads.example/agents/support` to `agent-42`. Trusting the domain does not map every workload in that domain to this agent.

A JWT-SVID could have this decoded payload; its protected header and signature follow the JWT-SVID specification:

```json
{
  "sub": "spiffe://workloads.example/agents/support",
  "aud": ["https://idp.example/tenant/acme"],
  "exp": 1789128300
}
```

The example omits optional `iss` and `iat`. Existing SPIFFE OAuth client authentication uses:

| Field | Value |
|---|---|
| `client_assertion_type` | `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` |
| `client_assertion` | The signed JWT-SVID |
| OAuth client association | The association validated under SPIFFE OAuth |
| Federation resolution | Approved trust domain and exact authenticated SPIFFE ID → `agent-42` |

This authenticates the client under [SPIFFE OAuth §3.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-spiffe-client-auth-02#section-3.1). It does not by itself define how the JWT-SVID becomes WAG subject evidence or an ID-JAG actor input. Those compositions require the WAG and Actor Profile proposals. A DPoP proof accompanying the bearer JWT-SVID does not demonstrate that the platform endorsed its key.

<a id="spiffe-flow"></a>

## SPIFFE X.509-SVID and WIT-SVID

The same exact SPIFFE ID can be resolved after native X.509-SVID or WIT-SVID authentication under the corresponding SPIFFE OAuth sections.

| Evidence | What the IdP validates | Remaining composition gap |
|---|---|---|
| X.509-SVID | Certificate, trust-domain anchors, TLS authentication, and client identity | How connection evidence identifies the subject or actor during grant issuance |
| WIT-SVID | Credential, trust-domain anchors, confirmation key, and required proof | Which proof mode and output-key relationship the consuming grant supports |

A separate IdP access token is not required by this document for either input. If an upstream profile selects an intermediate credential, that profile must define its purpose, presentation, validation, and lifecycle. Replacing a credential or key does not automatically establish new instance identity.

<a id="platform-jwt-flow"></a>

## Imported platform identity

A platform may issue this workload evidence:

```json
{
  "iss": "https://platform.example",
  "sub": "support-bot-7",
  "aud": "https://idp.example/tenant/acme",
  "tenant": "customer-a",
  "iat": 1789128000,
  "exp": 1789128300
}
```

The IdP's configuration requires that exact issuer, subject, and tenant, and maps them to `agent-42`. It validates the credential class, audience, time limits, and trusted signature before resolving the binding. The external subject remains evidence; it is not copied automatically into a downstream grant.

A consuming flow may require separate OAuth client authentication. Possession of this platform JWT or an unrelated DPoP key does not satisfy such a requirement. The platform-evidence field and direct issuance behavior must be supplied by the consuming WAG or actor profile, not by a local adapter convention.

<a id="device-flow"></a>

## Agent with its own attested client

An attester authenticates the agent's own OAuth client under ATTEST. The IdP maps the validated attester/client identity to `agent-42`. The client authentication and its proof follow ATTEST without new mandatory attestation claims.

For user-delegated access, valid user and client credentials are not sufficient: the IdP also needs approval for `agent-42` to act for `user-17` for the target resource and scopes. Constructing a governed actor from the external credential follows the proposed Actor Profile extension point; this scenario does not substitute a newly issued adapter token.

<a id="shared-client-flow"></a>

## Agents behind a shared client

A platform uses one OAuth client for `support-bot-7` and `billing-bot-2`. Base ATTEST proves that shared client and its key. An unsigned agent selector, or an unrecognized claim named `agent_id`, does not distinguish the two agents authoritatively.

The proposed ATTEST extension needs authenticated agent evidence, its namespace, the attester's authority, proof-key binding, and extension negotiation. Once standardized, Federation can map those distinct identities to separate governed agents. Until then, this document does not define an interoperable shared-agent authentication path.

<a id="app-consumption"></a>
<a id="ras-auth"></a>
<a id="provisioning-example"></a>

## Downstream policy and record correlation

The RAS trusts an approved issuer for a defined grant profile, validates that grant under its owning specification, and makes its own access-token decision. Supporting a JWT bearer grant does not imply support for an unresolved WAG extension or direct mapped-actor input.

For a completed composition, the intended correlation is:

| Grant identity | Governed record |
|---|---|
| Self-acting subject in the IdP namespace | `agent-42` |
| Delegated actor in the same IdP namespace | `agent-42` |
| Same bare identifier under another issuer | A different identity unless an explicit trusted mapping establishes equivalence |

Provisioned properties belong to the principal they describe. User groups do not become agent memberships. Disablement affects new issuance after the relevant system applies it; revoking outstanding tokens requires the lifecycle mechanisms under discussion upstream.
