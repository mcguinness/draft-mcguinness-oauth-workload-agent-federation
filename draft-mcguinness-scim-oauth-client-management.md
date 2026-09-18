---
title: "SCIM Profile for OAuth 2.0 Client Management"
abbrev: "SCIM OAuth Client Management"
category: std
docname: draft-mcguinness-scim-oauth-client-management-latest
submissiontype: IETF
stand_alone: yes
ipr: trust200902
area: "Security"
workgroup: "Web Authorization Protocol"
keyword:
 - OAuth
 - SCIM
 - client registration
venue:
  group: "Web Authorization Protocol"
  type: "Working Group"
  mail: "oauth@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/oauth/"
  github: "mcguinness/draft-mcguinness-oauth-workload-agent-federation"
  latest: "https://mcguinness.github.io/draft-mcguinness-oauth-workload-agent-federation/draft-mcguinness-scim-oauth-client-management.html"
author:
 - fullname: Karl McGuinness
   organization: Independent
   email: public@karlmcguinness.com
normative:
  CIMD: I-D.ietf-oauth-client-id-metadata-document
  RFC6749:
  RFC7591:
  RFC7592:
  RFC7643:
  RFC7644:
  RFC8414:
  RFC9700:
  RFC6585:
informative:
  HUNT:
    title: "OAuth 2.0 SCIM Client Registration Profile"
    author:
      - name: Phil Hunt
      - name: Morteza Ansari
      - name: Anthony Nadalin
    date: 2013-07-05
    seriesinfo:
      Internet-Draft: draft-hunt-oauth-scim-client-reg-00
    target: https://datatracker.ietf.org/doc/html/draft-hunt-oauth-scim-client-reg-00
  AGENT-MANAGEMENT:
    title: "SCIM Profile for Agent Federation Management"
    author:
      - name: Karl McGuinness
    date: 2026-09-18
    seriesinfo:
      Internet-Draft: draft-mcguinness-scim-agent-federation
  RFC9967:
--- abstract

This document defines a SCIM 2.0 resource for provisioning and managing
OAuth client registrations. It develops the approach proposed by Hunt,
Ansari, and Nadalin in the original OAuth 2.0 SCIM Client Registration
Profile, using the final SCIM and OAuth registration specifications.

The resource maps OAuth registration metadata to SCIM attributes and
uses SCIM operations, discovery, authorization, and conditional updates.
It can share a registration with OAuth dynamic registration interfaces.
It also manages local admission of clients using Client ID Metadata
Documents, preserving their URL identifiers and document-owned metadata.
The profile does not define a new client-authentication method or infer
an authorization principal from a client registration.

--- middle

# Introduction

An enterprise provisioning service needs to create, find, update, and
decommission OAuth client registrations. OAuth Dynamic Client Registration
{{RFC7591}} and Client Registration Management {{RFC7592}} define the
registration model and their own HTTP interfaces. SCIM {{RFC7643}}
{{RFC7644}} supplies a management interface with resource discovery,
collection queries, attribute-level updates, and concurrency controls.

{{HUNT}} first proposed representing OAuth registrations as SCIM resources.
This document is a modernized successor proposal, retaining that resource
model and management approach. It uses current OAuth metadata and SCIM 2.0
semantics instead of the earlier draft formats. {{changes}} describes
its relationship to that work; this proposal does not imply participation
or endorsement by the original authors.

The managed object is one client registration at one authorization server:

~~~
 SCIM provisioning client          Authorization server
          |                       +---------------------+
          +---- /OAuthClients --->| Client registration |
                                  +----------+----------+
                                             |
                                  OAuth protocol use
~~~

SCIM `id` identifies the management resource. OAuth `client_id` identifies
the client at its authorization server. Neither automatically identifies
a workload, runtime instance, or Agent Principal.

For Client ID Metadata Document (CIMD) clients {{CIMD}}, the resource
manages local admission at the authorization server. It retains the
Client Identifier URL; it does not allocate a replacement OAuth identity.
The document supplies client metadata, while SCIM supplies administrative
state and a stable reference for local relationships.
This management option does not make SCIM provisioning a prerequisite
for CIMD use outside this profile.

## Scope

This profile supports authenticated administrative provisioning. A client
may manage its own registration when explicitly authorized, or a connector
may manage a bounded collection of registrations.

The representation covers locally managed registration metadata and
public-key configuration by `jwks_uri`, or a reference to CIMD metadata
under {{cimd}}. It does not define:

* Anonymous registration or a new registration access-token format.
* Generation, export, or rotation of shared secrets or private keys.
* Embedded `jwks`, localized metadata names, or software-statement
  submission through SCIM. These require explicit SCIM mappings beyond
  this revision. Their use within a CIMD document or through RFC 7591
  is unaffected.
* Agent identity, workload trust, consent, user delegation, or a policy
  language. {{AGENT-MANAGEMENT}} separately consumes client references.

An authorization server can continue to expose RFC 7591 and RFC 7592
interfaces for those deployments and features. SCIM support does not
require exposing either interface.

# Conventions and Administrative Authority {#trust}

{::boilerplate bcp14-tagged-bcp14}

OAuth terms follow {{RFC6749}}. Registration metadata follows {{RFC7591}};
SCIM terms follow {{RFC7643}} and {{RFC7644}}.

The SCIM Service Provider manages registrations for a configured
authorization server. Its authenticated administrative context MUST
identify the permitted authorization server, tenant, and management scope.
Request attributes MUST NOT expand that scope.

The Service Provider MUST authorize creation, metadata changes, key-source
changes, activation, and deletion against that context. Permission to read
or describe a client does not imply permission to change its keys, redirect
URIs, grants, or eligibility. A client-authentication credential MUST NOT
by itself establish permission to manage the registration.

SCIM request authorization uses {{Section 2 of RFC7644}}. This profile
defines no management scope names and issues no registration access token.
An RFC 7592 registration access token is not automatically accepted by the
SCIM interface; such use requires separately configured authorization.

# OAuthClient Resource {#schema}

The resource type is `OAuthClient`, exposed at `/OAuthClients`, with schema:

`urn:ietf:params:scim:schemas:core:2.0:OAuthClient`

The Service Provider MUST advertise the resource and attribute definitions
through `/ResourceTypes` and `/Schemas`, and supported operations through
`/ServiceProviderConfig`. This document proposes the schema registration;
it does not claim an existing IANA assignment.

## Identity and Administrative Attributes {#identity}

Common attributes `id`, `externalId`, and `meta` follow {{RFC7643}}.
The additional attributes are:

| Attribute | Type | Mutability | Required | Meaning |
|---|---|---|---|---|
| `authorizationServer` | string | readOnly | true | Authorization-server issuer identifier under {{RFC8414}} |
| `client_id` | string | readOnly | true | OAuth client identifier: server-assigned or the CIMD Client Identifier URL |
| `clientIdMetadataDocument` | string | immutable | false | Client Identifier URL selecting CIMD metadata, as defined in {{cimd}} |
| `active` | boolean | readWrite | true | Whether this registration is enabled for OAuth use |

All are single-valued, returned by default, and have uniqueness `none`.
String comparisons are case-exact. The server populates both read-only
values on creation; request values are processed under SCIM's read-only
rules and MUST NOT select an existing registration.

The pair (`authorizationServer`, `client_id`) MUST identify exactly one
registration and MUST remain unchanged for the resource's lifetime.
The issuer comes from configured server context, not from a URL supplied
by the provisioning client. `client_id` need not equal SCIM `id`.

The Service Provider MUST NOT reassign a deleted resource's `id` or
assign its issuer-qualified `client_id` to a different client. Explicit
readmission of the same CIMD client uses a new SCIM `id`; old references
MUST NOT become effective again. This prevents stale administrative
references from authorizing a replacement resource.

For connector reconciliation, this profile requires `externalId` on
creation and uniqueness within the authenticated provisioning domain and
resource type. It remains an administrative correlation value, not an
OAuth identifier. A duplicate creation uses `409` with `uniqueness`;
responses lost in transit can be recovered by an authorized exact lookup.

If omitted on creation, `active` defaults to false. Later removal is
invalid because it is required. `active: true` is necessary for use but
does not override local suspension, metadata validation, or OAuth policy.

## Registration Metadata {#metadata}

This section applies when `clientIdMetadataDocument` is absent. For CIMD
clients, {{cimd}} defines the metadata source instead.

The following attributes retain the metadata value syntax and meaning
specified in {{Section 2 of RFC7591}}. They are SCIM string attributes with
mutability `readWrite`, returned `default`, uniqueness `none`, and
`caseExact: true`. They have no SCIM canonical-value enumeration; accepted
OAuth values remain subject to the relevant specifications and server
policy.

| Attribute | Multi-valued | Required | Purpose |
|---|---|---|---|
| `token_endpoint_auth_method` | false | false | Registered client-authentication method; conditionally required below |
| `grant_types` | true | false | Permitted OAuth grant types; conditionally required below |
| `response_types` | true | false | Permitted authorization-endpoint response types |
| `redirect_uris` | true | false | Registered redirect URIs |
| `scope` | false | false | Space-separated registration scope configuration |
| `jwks_uri` | false | false | Public JWK Set location |
| `client_name` | false | false | Display name of the client |
| `client_uri` | false | false | Client information URL |
| `logo_uri` | false | false | Client logo URL |
| `tos_uri` | false | false | Terms-of-service URL |
| `policy_uri` | false | false | Privacy-policy URL |
| `contacts` | true | false | Client contacts |
| `software_id` | false | false | Software identifier |
| `software_version` | false | false | Software version |

Multi-valued attributes use arrays of strings, preserving the OAuth
metadata representation rather than adding SCIM complex-value wrappers.
SCIM attribute-name matching is case-insensitive; values use their OAuth
comparison rules. Responses SHOULD use the spelling in this table.

For locally managed metadata, creation MUST explicitly supply
`token_endpoint_auth_method` and a non-empty `grant_types`. This profile
therefore does not apply RFC 7591's
omission defaults for those attributes. For flows using the authorization
endpoint, the request MUST also supply the required `response_types` and
`redirect_uris`. For other flows, omission of `response_types` means no
authorization-endpoint response is enabled. These are explicit profile
narrowings, not changes to RFC 7591 endpoints.

The Service Provider MUST validate the effective registration against
{{RFC7591}}, applicable grant and authentication profiles, and OAuth
security requirements in {{RFC9700}}. Registration does not enable a grant
or response type prohibited by those requirements. An inactive resource
is not permission to store an invalid registration.

Accepted metadata is the authoritative configuration returned by the
server. A provisioning client MUST inspect that configuration before
relying on requested capabilities. Registration `scope` does not itself
supply user consent, delegation, or resource authorization.

## Client ID Metadata Documents {#cimd}

When the authorization server supports {{CIMD}}, the Service Provider MUST
support its management through the following representation:

* Creation supplies `clientIdMetadataDocument` with the Client Identifier
  URL. The returned `client_id` MUST equal that value exactly. The
  authorization-server issuer remains the server's configured issuer,
  not the document's origin.
* The URL and document are validated under {{CIMD}}, including the exact
  match of the document's `client_id`. Creation and activation require
  successfully validated metadata, which MAY come from a valid CIMD cache.
* Registration metadata attributes in {{metadata}} MUST be absent from
  this SCIM resource and its write requests. Supplying them receives
  `400` with `invalidValue`. Their required-value rules for locally
  managed registrations do not apply to the CIMD document.
* The metadata source is fixed at creation. Updates MUST NOT add, change,
  or remove `clientIdMetadataDocument`; such changes receive `400` with
  `mutability`. A URL-shaped `client_id` alone does not select CIMD.
  Omitting the immutable attribute from a PUT preserves its value.

This separates two authorities:

| Authority | Managed values |
|---|---|
| CIMD document publisher | OAuth metadata, including authentication method, keys, and redirect URIs |
| Authorization-server administrator through SCIM | Local admission, `active`, `externalId`, and authorized administrative extensions |

CIMD retrieval, validation, caching, and client authentication continue
to follow {{CIMD}} during OAuth use. SCIM neither freezes a metadata
snapshot nor supplies an alternative when document validation fails.
Public `jwks`, `jwks_uri`, and software statements in the document need
no SCIM mapping because they are not copied into this resource. CIMD's
prohibition on shared-secret authentication remains applicable.

Document metadata remains subject to authorization-server policy;
`active: true` does not approve every future metadata change or confer
agent, user, or resource authority. A document update cannot alter local
SCIM administrative state. The SCIM ETag versions that state, not the
remote document or its cache entry.

CIMD capability uses `client_id_metadata_document_supported` under
{{Section 6 of CIMD}}. This profile defines no additional OAuth discovery
parameter and does not require the SCIM service to host CIMD documents.

## Credentials and Extensions {#credentials}

`jwks_uri` configures public-key discovery under RFC 7591. Keys and their
use remain subject to the configured authentication profile. This SCIM
interface MUST NOT return or generate private keys, `client_secret`, or
`registration_access_token`, including in collection results, diagnostics,
and events. Reads MUST NOT rotate credentials.

For locally managed metadata, creation MUST fail if the requested
authentication method needs credential material that has neither been
configured through this interface nor
established through an independently authorized mechanism. For example,
`private_key_jwt` can use an approved `jwks_uri`; an existing secret-based
registration can have its public metadata managed without exposing its
secret. This document requires no new credential-issuance endpoint.

Further OAuth metadata requires a defined SCIM schema extension with
attribute types, mutability, and an explicit mapping to its OAuth meaning.
A name's presence in an OAuth registry does not alone define a SCIM schema.
Unrecognized attributes follow SCIM processing rules. Unsupported metadata
MUST NOT be silently reported as accepted configuration.

# SCIM Operations {#operations}

The Service Provider MUST support POST, individual and paginated collection
GET, PATCH, and DELETE under {{RFC7644}}. PUT is OPTIONAL. SCIM request and
response formats apply, including `application/scim+json`, ListResponse,
and Error. SCIM Bulk is not required.

## Creation and Existing Registrations

POST creates one registration and returns its SCIM representation,
Location, and ETag. Creation MUST be authorized for the effective metadata
and any requested activation. Supplied read-only identifiers cannot attach
the request to an existing registration.

For CIMD, POST instead establishes local management of the identified
client, including one previously discovered during OAuth use. It does
not change that client's identity. A second SCIM resource for the same
(`authorizationServer`, `client_id`) receives `409` with `uniqueness`.
If the identifier already belongs to a locally managed registration,
the server rejects the conflicting creation with `409` and `uniqueness`;
it MUST NOT convert that registration to CIMD.

Existing registrations, including registrations created through RFC 7591,
MAY be exposed as OAuthClient resources after administrative authorization.
They retain their OAuth `client_id` and credentials. Establishing this
management representation MUST NOT create a second OAuth registration or
merge clients based on names, redirect URIs, or keys. Attachment and read
permission are administrative decisions, not an unauthenticated discovery
mechanism.

An existing CIMD client's representation includes `clientIdMetadataDocument`.
When exposing an existing registration without a creation request,
`active` reflects its administrative enablement; exposure MUST NOT itself
enable or disable it. An explicit CIMD POST instead applies the requested
or default `active` state under the caller's administrative authority.

## Read, Query, and Update

The Service Provider MUST support `eq` filters on `id`, `externalId`,
`authorizationServer`, `client_id`, and `active`, including `and`
combinations. Results MUST remain within the caller's management scope.
An authorized reader spanning provisioning domains cannot assume
`externalId` alone is unique.

Complete representations MUST carry `meta.version`; individual responses
MUST carry the corresponding ETag. Clients MUST use `If-Match` on PATCH,
PUT, and DELETE. A missing precondition receives HTTP 428 {{RFC6585}};
a failed precondition receives HTTP 412 under {{Section 3.12 of RFC7644}}.
After a conflict, the client retrieves and reconciles before retrying.

PATCH and PUT retain their SCIM semantics. The Service Provider MUST
validate and authorize the resulting registration before committing the
atomic resource change. Removal of a required attribute, including one
conditionally required under {{metadata}}, is invalid;
read-only attributes follow SCIM's read-only processing. A mutation MUST
NOT change unrelated agent bindings, consent, or resource permissions.

## Disablement and Deletion {#disablement}

Setting `active: false` disables the registration. Before returning success,
the server MUST prevent new OAuth authorization and token issuance for
that client, including refresh decisions beginning after the response.
Reactivation requires separate administrative authorization.

DELETE de-registers the underlying client; it is not merely removal of
its SCIM representation. The server MUST invalidate any RFC 7592
registration access token for that registration. The recommendation to
invalidate outstanding grants and tokens in {{Section 2.3 of RFC7592}}
also applies; HTTP processing and error responses remain SCIM's.
The server MUST document the treatment of outstanding authorization on
reversible disablement as well.

For a CIMD client, disablement and deletion apply to its local admission,
not the publisher's document. Neither operation requires successful
document retrieval. The authorization server MUST retain an administrative
denial for the issuer-qualified client identifier after deletion so that
CIMD rediscovery cannot bypass the decision. Restoring admission requires
explicit administrative authorization; fetching valid metadata is not
such authorization. Deletion does not disable the client at other servers.

Neither response implies immediate rejection by offline resource servers.
Reactivation MUST NOT restore authorization already revoked. Client
eligibility is separate from any Agent Principal's eligibility: disabling
a shared client does not declare its associated agents disabled.

## Errors

| Failure | Response |
|---|---|
| Malformed SCIM message | `400`, `invalidSyntax` |
| Invalid metadata, missing required value, or inconsistent configuration | `400`, `invalidValue` |
| Duplicate connector correlation value or managed OAuth client | `409`, `uniqueness` |
| Attempt to change the metadata source | `400`, `mutability` |
| CIMD requested at a server without CIMD support | `400`, `invalidValue` |
| CIMD metadata temporarily unavailable when creation or activation requires retrieval | `503` |
| Unauthorized administrative change | `403` |
| Missing / failed conditional-write precondition | `428` / `412` |

Other errors retain SCIM meanings. OAuth DCR errors such as
`invalid_client_metadata` are not substituted for SCIM error responses.
Error details MUST NOT expose secrets or resources outside the caller's
administrative scope.

# Coexistence with Dynamic Registration {#coexistence}

For locally managed metadata, the following coexistence rules apply.
CIMD metadata remains document-owned under {{cimd}}; an RFC 7592 endpoint
MUST NOT replace it with an independent, locally editable copy.

When SCIM and RFC 7591/7592 manage the same registration, they MUST share
one authoritative configuration. A change through any administrative
interface that alters the SCIM representation MUST change its ETag.
An update cannot leave different effective keys, redirect URIs, or grants
behind the two representations.

Each interface retains its own protocol:

| Interface | Representation and management authority |
|---|---|
| SCIM | OAuthClient resource, SCIM authorization, queries, PATCH, and ETags |
| RFC 7591 | OAuth client-registration request and response |
| RFC 7592 | Client configuration endpoint and registration access token |

SCIM `meta.location` is not RFC 7592's `registration_client_uri`. A
registration access token and a SCIM management token are not implicitly
interchangeable. Supporting one interface does not advertise support for
the other, and this profile defines no additional RFC 8414 metadata.

Update omission rules apply to the attributes managed by that interface.
An RFC 7592 update MUST NOT clear SCIM-only `active`, `externalId`, or
administrative extension values merely because they have no RFC 7592
representation. Conversely, a SCIM update MUST preserve credentials and
unmapped metadata that its schema does not manage. Changes to supported
metadata still require validation against the complete registration,
including RFC 7591's exclusivity of `jwks` and `jwks_uri`.

# Security Considerations

Key-source and redirect-URI changes can transfer control of a registration.
Servers must authorize them as security-sensitive changes, independently
of descriptive metadata edits. A software name, `software_id`, or client
identifier is not proof of software integrity or runtime provenance.
Public and confidential client classification follows {{Section 2.1 of
RFC6749}}; allocating an identifier does not change that classification.

Fetching CIMD documents, `jwks_uri`, and other URLs needs SSRF controls,
trusted transport, and restrictions on redirects and credential forwarding.
Descriptive URLs
are not credential-authority trust. Public-key replacement affects client
authentication but does not necessarily revoke previously issued tokens.

CIMD URL or domain ownership can change independently of SCIM state.
Administrators should reassess admission and associated permissions when
control changes. A valid document does not prove continuity of the party
previously admitted, and local management does not remove this CIMD risk.

Administrative access can be broader than runtime client authority.
Servers should audit the writer, affected registration, and security-relevant
changes without logging secrets. All writers must preserve disablement,
read-only identifiers, and concurrency behavior across administrative APIs.

SCIM change events under {{RFC9967}} MAY report resource changes. They
retain their existing meanings and MUST NOT contain secret material.
This document defines no client-specific event or delivery guarantee.

# Privacy Considerations

Client metadata can expose application deployments, contacts, redirect
locations, and tenant relationships. Query and event access SHOULD be
limited to authorized management scopes. Public-key discovery does not
justify exposing the complete registration to unauthenticated readers.

# IANA Considerations {#iana}

This document requests registration in the SCIM Schema URIs registry
using {{Section 10.3.2 of RFC7643}}:

* Schema URI: `urn:ietf:params:scim:schemas:core:2.0:OAuthClient`
* Schema Name: OAuth Client
* Intended or Associated Resource Type: OAuthClient
* Purpose: Provision and manage an OAuth client registration using SCIM.
* Single-value Attributes: `authorizationServer`, `client_id`,
  `clientIdMetadataDocument`, `active`,
  `token_endpoint_auth_method`, `scope`, `jwks_uri`, `client_name`,
  `client_uri`, `logo_uri`, `tos_uri`, `policy_uri`, `software_id`, and
  `software_version`, defined in {{identity}} and {{metadata}}.
* Multi-valued Attributes: `grant_types`, `response_types`, `redirect_uris`,
  and `contacts`, defined in {{metadata}}.

No OAuth client metadata, token-endpoint authentication method, or event
type is registered by this document.

--- back

# Example: Provision and Disable a Client

These non-normative examples assume a connector authorized to manage
registrations at `https://idp.example/`. Tokens and identifiers are
illustrative, not test credentials. The authorization server accepts
`private_key_jwt` using the configured public JWK Set.

## Register

~~~ http-message
POST /scim/acme/OAuthClients HTTP/1.1
Host: idp.example
Authorization: Bearer CONNECTOR_ACCESS_TOKEN
Content-Type: application/scim+json
Accept: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:OAuthClient"],
  "externalId": "platform-registration-7",
  "active": false,
  "client_name": "Analysis platform",
  "token_endpoint_auth_method": "private_key_jwt",
  "grant_types": ["client_credentials"],
  "jwks_uri": "https://platform.example/oauth/jwks.json"
}
~~~

~~~ http-message
HTTP/1.1 201 Created
Location: https://idp.example/scim/acme/OAuthClients/oc7
ETag: W/"c1"
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:OAuthClient"],
  "id": "oc7",
  "externalId": "platform-registration-7",
  "authorizationServer": "https://idp.example/",
  "client_id": "platform-client-7",
  "active": false,
  "client_name": "Analysis platform",
  "token_endpoint_auth_method": "private_key_jwt",
  "grant_types": ["client_credentials"],
  "jwks_uri": "https://platform.example/oauth/jwks.json",
  "meta": {
    "resourceType": "OAuthClient",
    "version": "W/\"c1\"",
    "location": "https://idp.example/scim/acme/OAuthClients/oc7"
  }
}
~~~

The connector uses `oc7` for management and the assigned `platform-client-7`
for OAuth. Registration has created neither an Agent Principal nor user
delegation. An authorized PATCH can enable `active` before runtime use.

## Disable

After activation, the connector retrieves the current ETag, shown here
as `W/"c2"`, and applies:

~~~ http-message
PATCH /scim/acme/OAuthClients/oc7 HTTP/1.1
Host: idp.example
Authorization: Bearer CONNECTOR_ACCESS_TOKEN
Content-Type: application/scim+json
If-Match: W/"c2"

{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [{"op": "replace", "path": "active", "value": false}]
}
~~~

The server returns success after blocking new client use as specified in
{{disablement}}. Existing resource access follows the documented token
revocation policy; it is not inferred from the SCIM response.

# Example: Admit a CIMD Client

The same connector can admit a client whose metadata remains at its
Client Identifier URL. This non-normative example assumes the document
at `https://platform.example/oauth/client.json` validates under {{CIMD}}.

~~~ http-message
POST /scim/acme/OAuthClients HTTP/1.1
Host: idp.example
Authorization: Bearer CONNECTOR_ACCESS_TOKEN
Content-Type: application/scim+json
Accept: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:OAuthClient"],
  "externalId": "platform-cimd-7",
  "clientIdMetadataDocument": "https://platform.example/oauth/client.json",
  "active": false
}
~~~

~~~ http-message
HTTP/1.1 201 Created
Location: https://idp.example/scim/acme/OAuthClients/oc8
ETag: W/"c1"
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:OAuthClient"],
  "id": "oc8",
  "externalId": "platform-cimd-7",
  "authorizationServer": "https://idp.example/",
  "client_id": "https://platform.example/oauth/client.json",
  "clientIdMetadataDocument": "https://platform.example/oauth/client.json",
  "active": false,
  "meta": {
    "resourceType": "OAuthClient",
    "version": "W/\"c1\"",
    "location": "https://idp.example/scim/acme/OAuthClients/oc8"
  }
}
~~~

The connector uses `oc8` in SCIM references. OAuth requests use the URL
as `client_id`. Keys and redirect URIs come from the CIMD document;
activation, disablement, and agent associations remain local administrative
decisions. Another authorization server can admit the same URL under its
own independent policy and SCIM resource.

# Relationship to the Original Proposal {#changes}

This work builds on {{HUNT}} by Phil Hunt, Morteza Ansari, and Anthony
Nadalin. It retains SCIM registration resources, CRUD management, and
resource/schema discovery. It updates that approach as follows:

| Area | This proposal |
|---|---|
| SCIM model | Final SCIM 2.0 schemas and operations; `OAuthClient` at `/OAuthClients` |
| OAuth metadata | Final RFC 7591 definitions and existing registries |
| Management coexistence | Explicit relationship to the RFC 7592 interface |
| CIMD | Local admission of URL-identified clients without copying document metadata |
| Client identity | Registration identity, without requiring one identifier per execution |
| Administrative access | Authenticated, scoped provisioning; client authentication is separate |
| Credentials | Public metadata and `jwks_uri`; secret distribution and rotation are outside the interface |
| Software assertions | No replacement format; RFC 7591 software statements remain available through their defined interface |

The earlier schema and endpoint formats are not claimed to be wire
compatible with this proposal. Deployment migration needs explicit mapping
of existing registrations; it must not silently allocate new client IDs.
Coordination with the original authors and the OAuth and SCIM communities
is intended. This document does not claim to update an adopted standard
or to be an agreed continuation under the earlier draft name.

# Acknowledgments

The original SCIM client-registration design by Phil Hunt, Morteza Ansari,
and Anthony Nadalin provides the foundation for this proposal.

# Document History

Initial version.
