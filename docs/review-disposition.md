# Review disposition

This revision addresses the review of a74cb5a. It keeps the main document on Standards Track by defining a complete delegated flow and extracts the independent attested-agent feature into its own short Standards Track draft.

| Review issue | Disposition |
|---|---|
| No complete protocol path | Main draft now defines ID Token + direct platform JWT exchange, governed actor construction, DPoP-bound ID-JAG, authenticated redemption, JWT access token, and API processing |
| Split attested-agent identity | New `draft-mcguinness-oauth-attested-agent-identity.md` owns the claim, modes, trust, verification and IANA request; no dependency on the federation flow |
| ID-JAG extension deferred upstream | Processing is defined here under ID-JAG §9.7; no base ID-JAG change required |
| Actor Profile copying rule differs | Main draft explicitly imports actor-object/resource rules, defines its own mapped-input processing, and does not advertise generic Actor Profile algorithm conformance |
| Self-acting WAG overstated | Abstract and introduction explicitly defer it; remaining asks stay with WAG |
| Attester identification | Own-client mode identifies the authority through the trusted verification key and configuration; a present `iss` must agree; shared mode requires `iss` |
| Metadata-name inference unexplained | SPIFFE assertion type versus authentication-method metadata distinction is explained; input capabilities are defined in an `agent_federation` object |
| Phantom owners | Identification and lifecycle work are described as future specifications |
| Actor Profile normative without use | Normative use is now explicit for actor structure and API authorization |
| WIT baseline absent | WIT-02 is listed |
| Own-client output unclear | Direct attestation maps to a governed actor even when identifiers differ; no normalization token |
| Product-like use of “Federation” | Prose uses “this profile” or “this document”; the defined term Federation Binding remains |
| Project-management agenda in the body | Remaining gaps contain concise problems and asks; criteria live only in repository interoperability notes |
| Stale gap anchors | Companion uses `shared-agent` and `attester-trust`; main normative processing has role-specific anchors |
| Silent narrowing risk | Table lists additional required fields, actor mapping, proof/key rules, algorithms, lifetime bounds, chain scope, and error behavior |
| New companion dependency | Explicit editor's-copy reference, built alongside the main draft; optional shared-client path only. It is not claimed to be a Datatracker publication |

The signed delegated example includes synthetic public keys and complete tokens for both exchanges and the API. Its checker verifies signatures and cross-hop consistency, not independent implementation interoperability. No upstream acceptance or IANA allocation is claimed.

## Validation

Both drafts build to HTML and text through the repository Makefile with refreshed bibliography data. All references are cited. All 120 main-draft and 14 companion cross-references resolve; the generated HTML has 532 and 174 unique anchors respectively. The ten documentation links to generated drafts and all three JSON blocks validate. The signed example checker passes all nine JWT signatures, tamper rejection, public-key consistency, and cross-hop identity, scope, client and DPoP checks. `git diff --check` passes.

The companion's submission-named text passes idnits with no findings. The main draft reports six `POSSIBLE_DOWNREF` flags for normative drafts, two `UNDEFINED_STATE` warnings for the new companion (not yet submitted), and two generated table-of-contents appendix indentation warnings. Its baseline remains implementable without the optional companion dependency; the main draft is not described as idnits-clean.
