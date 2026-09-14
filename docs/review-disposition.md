# Review disposition

This revision addresses the supplied critique while preserving both acting
relationships. It does not claim to settle WAG's upstream ownership or adopt
a direct mapped-actor protocol without an explicit design decision.

| Finding | Disposition |
|---|---|
| Dead INSTANCE dependency | Removed the reference and all instance-context conformance requirements and example claims. Stable instance identity is out of scope. |
| Dependency stack | Removed INSTANCE; made Entity Profiles an independently optional annotation. Actor Profile and WAG remain normative where their behavior is selected. Dependencies now number seven Internet-Drafts, five WG and two individual. A WG-only core remains a scope option. |
| WAG extension and identifier ownership | Marked IdP-issued WAG as an explicit proposed extension, rather than base WAG behavior. Removed WAG registration requests from IANA Considerations; moved proposal templates to coordination notes. Upstream agreement or a distinct name remains unresolved. |
| Direct actor input | Recorded a concrete request and validation proposal in coordination notes. The current adapter remains an explicit design choice; the draft no longer claims Actor Profile universally requires it. |
| Adapter token confusion | Required a dedicated exchange audience, separate from the issuer and API audiences. Restricted token acceptance to federation subject/actor input; updated acquisition examples. |
| Platform JWT compatibility | Made age policy configurable, with a 300-second recommendation when issuance permits it. Allowed distinguishing issuer/audience/identity policies without dedicated `typ`; removed blanket rejection of ID-token-shaped workload credentials. Cached JWT/key-association constraints still apply. |
| Per-tenant signing keys | Retained exact issuer-scoped verification. Recommended separate keys for independent signing authorities; permitted explicitly authorized shared keys. |
| Clock skew | Replaced the 30-second cap with a configured, small allowance consistent with RFC 7519. Replay retention includes the largest allowance. |
| Delegated lifecycle cost | Documented two or three endpoint calls and user-credential renewal. Made adapter lifetime configurable, keeping current-policy checks and a short-lifetime recommendation. |
| Refresh asymmetry | Explained that WAG's prohibition is inherited from WAG-00, while ID-JAG permits a separate refresh lifecycle. Changing WAG refresh is an upstream or distinct-grant decision. |
| Input-specific nonce rule | Removed the platform-only mandate; the common nonce recommendation applies to every input. |
| Unknown request parameters and claims | Removed blanket `agent_id` rejection; retain normal ignore behavior. Extra data cannot select an identity model. |
| `agent_id` extension | Explicitly identified the shared-agent binding as an ATTEST extension implemented by this profile. Base ATTEST validation alone does not authorize agent resolution. Extracting a separate extension document remains optional organization work. |
| Internal-state mandates | Kept observable authorization and current-binding outcomes mandatory. Removed a prescribed approval-record schema and unconditional token-reuse promise; auditing is guidance and attester issuance assurance is a trust assumption. |
| Silent narrowings | Added a table identifying extra ATTEST, SPIFFE, exchange, grant, response, and redemption requirements. Retained these deliberately rather than presenting them as base-protocol requirements. |
| Terminology | Defined Registered Agent at first use, moved harness definition into terminology, and replaced undefined logical client with OAuth client. |
| Client grant parsing | Kept response-type checking mandatory; grant inspection is recommended in line with ID-JAG. RAS validation remains mandatory. |
| Missing conformance keyword | Added explicit MUST for the supported adapter-token input. |
| Length | Moved deployment examples, test inventory, and coordination material into ordinary Markdown repository documents; condensed introduction to one overview diagram and the existing path table. |
| Editorial issues | Removed fixed document date and unsupported dates for living web resources; reduced history to initial version; replaced instance-proof placeholders; numbered retained appendices; separated Security Considerations and Privacy Considerations. |

Some statements in the critique need qualification:

* Internet-Draft dependencies are a maturity and publication-coordination issue,
  not a blanket prohibition on submitting an initial Internet-Draft. A normative
  Informational downreference needs the applicable IETF downreference process;
  it is not inherently impossible. See
  [RFC 3967](https://www.rfc-editor.org/rfc/rfc3967.html).
* JWT profiles may specify claim requirements; RFC 7519's ignore rule applies
  in the absence of such requirements. The previous claim prohibition was
  unnecessary, but not universally forbidden for an explicitly defined profile.
  See [RFC 7519, Section 4](https://www.rfc-editor.org/rfc/rfc7519.html#section-4).
* Required authorization behavior remains testable even when internal records
  are not exposed. A revoked binding or missing delegation must cause rejection.
  Weakening these outcomes to SHOULD would weaken the trust model.

Remaining decisions are documented in [coordination notes](coordination.md):
retain WAG pending upstream agreement, define a distinct self-acting grant, or
reduce the initial core; and adopt or defer the direct mapped-actor input.
