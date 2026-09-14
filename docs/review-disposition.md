# Review disposition

This note records the current disposition of both reviews. The second review
used commit `2a18cae`; these changes also preserve the JWT-SVID support added
in `e3305eb`. The self-acting output is now Agent Federation Grant (AFG).
The delegated -00 flow retains the IdP access-token adapter.

| Finding | Disposition |
|---|---|
| Dead INSTANCE dependency | Removed the reference and all instance-context conformance requirements and example claims. Stable instance identity is out of scope. |
| Dependency stack | Removed INSTANCE and made WAG informative. Six Internet-Drafts are directly normative: five WG and Actor Profile. Entity Profiles remains transitively normative through Actor Profile; its annotation is recommended, not mandatory. |
| Self-acting grant and identifier ownership | Replaced the proposed WAG extension with AFG, defined unconditionally for this profile. The draft owns its token-type and media-type registration requests; IANA Considerations are self-contained. |
| Direct actor input | Retained the adapter in -00. The mapped-actor proposal is a concrete -01 coordination item: direct Actor Profile processing uses credential `sub`, so governed-agent mapping, especially for a shared client, needs an explicit companion rule. |
| Adapter token confusion | Kept exchange-only acceptance, RFC 9068 typing, and issuance eligibility. Audience now defaults to the trusted IdP token endpoint URL, with an explicit configured override when needed; it remains distinct from issuer/API audiences. |
| Platform JWT compatibility | Made age policy configurable, with a 300-second recommendation when issuance permits it. Allowed distinguishing issuer/audience/identity policies without dedicated `typ`; removed blanket rejection of ID-token-shaped workload credentials. Cached JWT/key-association constraints still apply. |
| Per-tenant signing keys | Retained exact issuer-scoped verification. Recommended separate keys for independent signing authorities; permitted explicitly authorized shared keys. |
| Clock skew | Replaced the 30-second cap with a configured, small allowance consistent with RFC 7519. Replay retention includes the largest allowance. |
| Delegated lifecycle cost | Documented two or three endpoint calls and user-credential renewal. Made adapter lifetime configurable, keeping current-policy checks and a short-lifetime recommendation. |
| Refresh asymmetry | Aligned AFG and ID-JAG on SHOULD NOT issue refresh tokens by default. Enabling refresh requires an authorized client, sender binding, protected refresh tokens, and continuing authorization/status checks. |
| Input-specific nonce rule | Removed the platform-only mandate; the common nonce recommendation applies to every input. |
| Unknown request parameters and claims | Removed blanket `agent_id` rejection; retain normal ignore behavior. Extra data cannot select an identity model. |
| `agent_id` extension | Explicitly identified the shared-agent binding as an ATTEST extension implemented by this profile. Base ATTEST validation alone does not authorize agent resolution. Extracting a separate extension document remains optional organization work. |
| Internal-state mandates | Kept observable authorization and current-binding outcomes mandatory. Removed a prescribed approval-record schema and unconditional token-reuse promise; auditing is guidance and attester issuance assurance is a trust assumption. |
| Silent narrowings | The table now includes invalid_grant for credential/binding failures and rejection of authorization_details, alongside ATTEST/SPIFFE and request/response narrowings. |
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

## Second review details

| Finding | Disposition |
|---|---|
| WAG conformance hedge | Removed. AFG issuance and redemption rules apply to every implementation claiming that output. WAG support is a separate capability. |
| IANA text points to repository | Complete OAuth URI and media-type templates now reside in the draft. Added an RFC Editor note to remove or replace repository links before RFC publication. |
| Adapter audience discovery | Default is the RFC 8414 token_endpoint URL; overrides are explicit and must be distinct from issuer/API audiences. Updated acquisition examples. |
| Delegation metadata | Named actor_profile_token_exchange and its three nested arrays. Both output advertisements must agree about this profile's ID-JAG support; unrelated outputs and self-acting AFG need not appear in both. |
| Actor Profile audience | Reworded as the token-endpoint audience shown in Actor Profile's examples, not a rule defined by Actor Profile. |
| act.sub_profile | Explicitly retained Actor Profile's SHOULD, explained unclassified-actor processing, and acknowledged the transitive Entity Profiles dependency. |
| Undefined endorsement | Removed from the normative body. Kept the potential trust-configuration concept in informative coordination notes. |
| Instance section | Reduced to one paragraph. Design boundaries remain in coordination notes; removed the optional-instance wording from acquisition. |
| Lowercase should | Changed the attester-approval recommendation to SHOULD. |
| BCP 14 and list formatting | Added the combined BCP 14 reference through kramdown's boilerplate support; removed the split list and extra blank line. |
| Appendix indentation | Confirmed all three warnings point to xml2rfc-generated appendix entries in the table of contents, not malformed section headings. Left the generated TOC formatting unchanged. |

The adapter and shared-agent ATTEST extension are the remaining coordination
items described in [coordination notes](coordination.md). They do not make
current conformance conditional on a future decision.

## Validation of the revised draft

* kramdown-rfc and xml2rfc generate HTML and text without warnings.
* All 229 XML cross-references resolve and all 35 bibliography entries are
  cited, including the BCP 14 reference group and its component RFCs.
* All 885 HTML fragment links resolve; supporting-document links are valid.
* Eleven JSON blocks and fifteen HTTP examples parse. The AFG identifiers,
  default adapter audiences, and role-specific metadata are consistent.
* idnits on a generated -00 submission-format text copy reports five
  possible-downref flags for existing normative Internet-Drafts and three
  appendix-TOC indentation warnings. It reports no BCP 14, filename, or
  boilerplate errors. These remaining flags are not described as a clean
  idnits pass.
