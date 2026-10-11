# Architecture

## Release publication

Manuscript builds and publication are separate operations. The release maintainer builds and reviews a PDF from an exact commit on `main`, then attaches it and a manifest to a draft GitHub release. The manifest binds the release tag, source commit, manuscript digest and reviewed PDF digest. The release event publishes those bytes to Zenodo; it cannot substitute a fresh render. `.zenodo.json` in the tagged source owns deposit metadata.

The publication job has read-only GitHub access and exposes the Zenodo credential only to the upload step after local validation. Publications are serialized across all tags in this repository. The uploader refuses an existing unpublished draft, a conflicting published version or an upload checksum mismatch. A retry after successful publication checks the existing version and performs no mutation when its PDF and descriptive metadata match.

GitHub release maintainers remain trusted to review and attach the intended artifacts. Manifest checks establish artifact identity, not scientific validity. The Zenodo account must use a single publisher: its separate GitHub integration must be disabled, and a maintainer must not edit drafts concurrently with publication. The legacy Zenodo API cannot atomically reserve a new draft against a concurrent manual edit; failed or uncertain uploads require inspection before retrying.
