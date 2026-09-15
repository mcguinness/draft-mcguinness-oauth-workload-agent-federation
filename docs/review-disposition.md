# Review disposition

This revision replaces the separate attested-agent claim with an optional composition of Client Instance Identification. The normative reference identifies the publicly available editor's copy at commit `26abba5fb612381331c670f4d6dfc54737f698af`; it is not presented as a Datatracker publication.

| Concern | Resolution |
|---|---|
| Additional attested-agent claim duplicates available evidence | Removed the standalone attested-agent draft and its claim registration. The optional `instance_attestation` input reuses Identification's signed `iss` and `client_instance_id`. |
| Instance identity is not agent authority | Identification validates the instance; Federation checks its approved agent binding, authenticated client association, and separate delegation authorization. Only the governed identity enters `act`. |
| Multiple instances of one agent | Several issuer-qualified instance identities may resolve through approved bindings to the same governed agent. |
| Several agents in one identified instance | An ambiguous mapping is rejected. This input defines no additional selector; another supported input must distinguish the selected agent. |
| Renewal, replacement and key changes | Identification retains ownership of lifecycle and continuity rules. A new identifier needs an approved new binding; continuity does not transfer existing grants to a replacement key. |
| Claim-triggered fallback | Trusted configuration selects own-client or instance-based processing; invalid instance evidence cannot fall back to the own-client path. |
| Error ownership | Identification claim/instance-policy rejection uses `invalid_client_attestation`; a valid instance with no usable agent binding or delegation uses `actor_unauthorized`. |
| Dependency and scope | The required platform-JWT and own-client attestation paths remain independent of Identification. Downstream instance-context propagation remains outside this revision. |

The prior review corrections remain in place: client-only credentials do not require agent records; API applicability and errors are explicit; native audience rules are preserved; scope reduction is defined; WIT deferral is a local scope choice; and continuing access has a finite deadline requiring renewed IdP authorization.

The deployment examples and conformance inventory now describe instance-to-agent resolution, including shared clients, many instances per agent, ambiguous mappings, receiver/client restrictions and replacement identities. The signed fixture continues to exercise the required platform-JWT path. Neither it nor the scenario inventory is an independent implementation interoperability test.

## Validation

The draft builds to HTML and text through the repository Makefile and renders as a paginated submission copy. All 140 XML cross-references resolve, all 25 bibliography entries are cited, and the HTML has 582 unique anchors with 564 valid fragment links. Documentation links and JSON examples validate. The required-path signed fixture passes all nine signature checks and its identity, audience, client, scope, API and DPoP consistency checks. `git diff --check` passes. Retired draft sources, generated local artifacts, identifiers and links have been removed.

Idnits reports six `POSSIBLE_DOWNREF` flags, two `UNDEFINED_STATE` warnings for Identification's unsubmitted editor's copy, and two generated appendix table-of-contents indentation warnings. The counts and categories match the preceding revision; Identification replaces the removed attested-agent dependency. The pinned Identification source was verified publicly accessible. The main draft is not described as idnits-clean.
