# Review disposition

This revision resolves the fresh-eye review of `4deadff`. It retains the delegated ID-JAG architecture and the separate attested-agent draft.

| Review issue | Resolution |
|---|---|
| Client authentication forces agent resolution | Only selected actor evidence resolves to a Registered Agent. X.509-SVID and WIT-SVID used for client authentication identify the OAuth client; that client must be permitted to use the separate actor binding. |
| API applicability and rejection rules incomplete | Trusted resource configuration selects profile-required paths independently of token claims. Those paths require a valid single actor, approved actor namespace, scope and DPoP binding. Resource errors distinguish malformed tokens, denied actor authorization, insufficient scope and proof failures. |
| Client-assertion audience ambiguous | The token-endpoint audience requirement is explicitly limited to `private_key_jwt`. Native JWT-SVID retains the sole IdP-issuer audience; ATTEST retains its own proof audience. |
| Requested and granted authority conflated | Ceilings apply to issued authority. Policy may approve a non-empty subset; no authorized scope or unavailable mandatory full approval produces `invalid_scope`. Delegation approval applies to the authority actually issued. |
| WIT deferral presented as an upstream proof gap | Reframed as a local scope choice. SPIFFE OAuth already supplies the attestation proof. Direct actor composition still needs an explicit output-key choice: WIT-02 §9.4 prohibits key use after credential expiry, so sharing that key with downstream DPoP requires corresponding lifetime limits. No change to ATTEST is requested. |
| Refresh has no explicit continuation bound | The optional RAS refresh exception requires a finite deadline anchored to the authorizing ID-JAG's `iat`, termination events and status-freshness policy. Rotation and reuse cannot advance the deadline; extending it requires a new ID-JAG and full profile checks. Tokens issued under the exception cannot outlive the deadline. |

The examples and conformance inventory cover these outcomes, including a hosting client with no agent record, native audience selection, partial scope approval, missing API actor context and refresh deadline behavior. The signed fixture now includes explicit API path and actor-namespace trust configuration, checked against its tokens. These are example-integrity checks and conformance scenarios, not an implemented IdP/RAS pair or independent interoperability results.

## Validation

The main draft builds to HTML and text through the repository Makefile; the unchanged companion outputs remain current. Both also render as paginated submission copies. All 130 main-draft and 14 companion cross-references resolve, and all 25 main-draft and 6 companion bibliography entries are cited. Generated HTML fragment links, documentation links and JSON blocks validate. The signed example checker passes all nine JWT signatures, tamper rejection, identity/client/scope/DPoP checks and API configuration checks. `git diff --check` passes.

The companion passes idnits with no findings. The main draft retains the prior six `POSSIBLE_DOWNREF` flags, two `UNDEFINED_STATE` warnings for the unsubmitted companion, and two generated appendix table-of-contents indentation warnings. No new idnits findings were introduced; the main draft is not described as idnits-clean.
