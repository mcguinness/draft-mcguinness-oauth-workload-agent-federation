# Review disposition and ownership correction

The current revision follows the instruction to resolve gaps in their owning specifications. It supersedes the earlier attempt to close every integration issue locally. Detailed upstream proposals now appear in the draft itself, with owners, rationale, and closure criteria.

| Earlier issue or local choice | Current disposition |
|---|---|
| AFG replacement for WAG | Removed. WAG is the intended self-acting grant; Federation neither forks its format nor assigns its identifiers. |
| WAG issuance described as platform-only | Corrected: WAG §5 already anticipates IdP issuance through exchange. The request is to complete that composition, not to introduce the idea of an IdP issuer. |
| Local WAG typing, sender constraint, authority, and replay rules | Replaced with concrete proposals to WAG and its collaborating specifications. No unresolved proposal is presented as existing WAG interoperability. |
| Locally relaxed WAG refresh rule | Removed. Current WAG behavior remains unchanged; any refresh change belongs upstream. |
| Mandatory IdP adapter access token | Removed, including acquisition, audience, eligibility, and reuse machinery. Direct mapped-actor construction is an Actor Profile/ID-JAG proposal; connection evidence is a separate SPIFFE OAuth composition gap. |
| Shared-agent `agent_id` registration | Removed. The draft specifies the evidence and trust requirements for an ATTEST extension to define upstream. |
| First-use credential digest/key association | Removed as a normative protocol. Its theft and replica limitations explain why upstream credential-binding semantics are needed. |
| Local authentication-method/discovery names | Removed. Existing SPIFFE/ATTEST capabilities remain available under their defining specifications; missing discovery is listed upstream. |
| SPIFFE JWT-SVID support | Retained for native authentication and Federation resolution, including issuer-less JWT-SVIDs. Missing grant composition is identified separately. |
| Additional required ATTEST timestamps and SPIFFE client-ID equality rules | Removed. Credential processing follows the owning specifications; exact Federation mapping remains required. |
| Local exchange/response errors and scope/resource/refresh narrowings | Removed. Federation applies policy; consuming profiles own the wire contract. |
| Identity mapping and authorization | Retained as normative Federation requirements, including exact trust, active bindings, delegation approval, authority limits, and principal-qualified correlation. |
| Instance identification | Remains outside current wire scope. Continuity and propagation requirements are detailed upstream without restoring an unpublished dependency. |
| Provisioning and disablement | Local authorization honors applied changes and freshness limits. Cross-system guarantees require the proposed lifecycle contract. |
| Supporting examples and test inventory | Rewritten to distinguish current identity/authentication behavior from acceptance criteria for unresolved upstream work. No placeholder full-protocol examples remain. |
| IANA Considerations | No IANA actions requested by Federation. The owning specifications are responsible for their identifiers. |

A gap is closed when the relevant specification defines the behavior and independent implementations can pass the listed closure cases. A private convention, a new local token, or merely documenting a proposal does not close it. This repository records proposals; it does not claim that upstream maintainers have accepted them.

Earlier review improvements remain applicable: configurable clock skew, issuer-scoped key trust, distinct client/agent/instance roles, normal handling of unknown parameters and claims, explicit transitive dependencies, concise normative text, and generated-document checks.

## Validation

HTML and text build successfully with kramdown-rfc and xml2rfc. All 67 XML cross-references resolve, every reference is used, and the generated HTML has 494 unique anchors with no broken internal links. The 17 documentation links to draft sections and both JSON examples also validate. `git diff --check` passes.

The submission-named text still receives five idnits `POSSIBLE_DOWNREF` flags for normative Internet-Drafts (SPIFFE OAuth, WIMSE credentials, ATTEST, Actor Profile, and ID-JAG), plus two indentation warnings on the generated table-of-contents appendix entries. These remain reported dependencies and formatting diagnostics; the build is not described as a clean idnits pass.
