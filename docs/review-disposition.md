# Review disposition and ownership correction

The current revision distinguishes requirements that Federation can define using existing extension points from changes to another specification's semantics. ATTEST is consumed as written, including its profiling support; its Last Call is not a prerequisite change request. Detailed upstream proposals remain for WAG and actor/grant composition.

| Earlier issue or local choice | Current disposition |
|---|---|
| AFG replacement for WAG | Removed. WAG is the intended self-acting grant; Federation neither forks its format nor assigns its identifiers. |
| WAG issuance described as platform-only | Corrected: WAG §5 already anticipates IdP issuance through exchange. The request is to complete that composition, not to introduce the idea of an IdP issuer. |
| Local WAG typing, sender constraint, authority, and replay rules | Replaced with concrete proposals to WAG and its collaborating specifications. No unresolved proposal is presented as existing WAG interoperability. |
| Locally relaxed WAG refresh rule | Removed. Current WAG behavior remains unchanged; any refresh change belongs upstream. |
| Mandatory IdP adapter access token | Removed, including acquisition, audience, eligibility, and reuse machinery. Direct mapped-actor construction is an Actor Profile/ID-JAG proposal; connection evidence is a separate SPIFFE OAuth composition gap. |
| Shared-agent evidence | Defined here as an ATTEST profile with the narrowly named `attested_agent_id` claim, required attester `iss`, exact namespace binding, and a self-contained claim registration request. Base ATTEST is unchanged. |
| First-use credential digest/key association | Remains removed. Federation now defines bearer-assurance, reuse, and key-role requirements directly; any additional proof mechanism uses the base specification's extension facilities. |
| Profile selection, trust, and discovery | Trusted configuration selects the Federation mode and accepted existing methods. Client restrictions intersect IdP trust. New generic discovery is separate optional work, not an ATTEST modification prerequisite. |
| SPIFFE JWT-SVID support | Retained for native authentication and Federation resolution, including issuer-less JWT-SVIDs. Missing grant composition is identified separately. |
| Additional required ATTEST timestamps and SPIFFE client-ID equality rules | Removed. Credential processing follows the owning specifications; exact Federation mapping remains required. |
| Local exchange/response errors and scope/resource/refresh narrowings | Removed. Federation applies policy; consuming profiles own the wire contract. |
| Identity mapping and authorization | Retained as normative Federation requirements, including exact trust, active bindings, delegation approval, authority limits, and principal-qualified correlation. |
| Instance identification | Remains outside current wire scope. Continuity and propagation requirements are detailed upstream without restoring an unpublished dependency. |
| Provisioning and disablement | Local authorization honors applied changes and freshness limits. Cross-system guarantees require the proposed lifecycle contract. |
| Supporting examples and test inventory | Rewritten to distinguish current identity/authentication behavior from acceptance criteria for unresolved upstream work. No placeholder full-protocol examples remain. |
| IANA Considerations | Federation requests registration of its own `attested_agent_id` claim. It leaves grant and base authentication identifiers with their owners. |

Federation-owned requirements are normative in this draft and have their own conformance cases. Upstream proposals remain open until the owning specification defines the necessary behavior and independent implementations pass the closure cases. The draft does not claim upstream acceptance.

Earlier review improvements remain applicable: configurable clock skew, issuer-scoped key trust, distinct client/agent/instance roles, normal handling of unknown parameters and claims, explicit transitive dependencies, concise normative text, and generated-document checks.

## Validation

HTML and text build successfully with kramdown-rfc and xml2rfc. All 84 XML cross-references resolve, every reference is used, and the generated HTML has 565 unique anchors with no broken internal links. All 20 documentation links to draft sections and four JSON blocks validate; the example P-256 public key is on the curve. `git diff --check` passes.

Submission-named text still receives five idnits `POSSIBLE_DOWNREF` flags for normative Internet-Drafts (SPIFFE OAuth, WIMSE credentials, ATTEST, Actor Profile, and ID-JAG), plus two indentation warnings on generated table-of-contents appendix entries. No new idnits findings were introduced by the profile.
