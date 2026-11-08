# CHANGELOG — identity and repository personalization

Scope: update current student/submission metadata and student-controlled repository references only.
Numerical values, datasets, model/training parameters, cost inputs, thresholds, network configuration, timestamps, IDs, and experimental results were not modified.

## Modified files

### `AI_USE.md`
- Change: reviewer prompt changed from Vivek to Kshitij. The declared Claude attribution and description of AI assistance were preserved.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `README.md`
- Change: student details, profile link, repository URL and clone instructions updated. The unverified old Release link was replaced with a pending/not-available note; no Release URL was invented.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `STATUS.md`
- Change: current GitHub profile and repository fields updated. Historical initial commit hash, previous push-count statement, and dated verification notes were retained as historical records.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `reflection/reflection_draft.md`
- Change: student name, roll number, GitHub repository, and suggested handwritten-scan filename updated. The actual handwritten scan is not modified.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `report/report.md`
- Change: report author front matter updated from Vivek Sagarwal / roll 230101055 / old repository to Kshitij Singh / roll 230101049 / supplied repository.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `scripts/make_submission_zip.sh`
- Change: usage comment updated with the new roll-number PDF example; script logic unchanged.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

### `scripts/up.sh`
- Change: default `REPO_SLUG` changed to `KshitijSingh07/CS3081-Cloud-Computing-Mini-Project`; release tag and deploy logic unchanged.
- Previous/current metadata: old student profile/repository references replaced with Kshitij Singh (`230101049`) and the supplied GitHub profile/repository where those fields represented the current submitter.
- Numerical content: unchanged.

## Preserved attribution and historical references
- `230101055.pdf` is retained byte-for-byte. It is a supplied image-only handwritten document that identifies the previous student; changing the visible handwriting would misrepresent authorship.
- `report/report.pdf` is regenerated from `report/report.md` and its PDF Author metadata is updated; the technical narrative, numeric tables, and pending-result markers are unchanged.
- `STATUS.md` retains historical Git repository facts such as the initial commit hash and previously recorded pushed-file count; these are historical records, not current student metadata.
- AI tool attribution in `AI_USE.md` (Claude/Anthropic) and original technical/citation credits remain intact.
- Old identity references remain only in the preserved handwritten PDF (image content is not text-extractable) and in historical Git/initial-submission notes; inspect these before submission if assignment policy requires a clean replacement.

## Verification performed
- Recursive text/binary inventory and identity search performed on the extracted archive.
- PDF text and metadata inspected; original handwritten PDF preserved unchanged.
- Unit tests, network simulator, syntax/configuration checks, numeric-content comparison, and ZIP integrity verification recorded in the delivery summary.
- GitHub repository links were checked for consistency in editable project metadata; no push was performed.
- All original non-identity files remain byte-for-byte unchanged; designated edited text files were checked for unchanged non-identity numeric token streams. The original handwritten PDF remains byte-for-byte unchanged.