# Decisions and risks

## Confirmed
End users upload documents after the product is available and ask questions through chat. Sample documents can be used for development.

## Proposed decisions
Use text-based PDF input, English first, session-scoped storage, Chroma for initial indexing, and no model training. Proposed limits: 10 files, 10 MB per file, 200 pages per session. Obtain reviewer agreement before representing these as contractual requirements.

## Risks and actions
| Risk | Priority | Proposed owner | Next action |
|---|---|---|---|
| Unsupported answers | High | Developer | Ground answers and run absent-answer tests |
| Cross-session leakage | High | Developer | Separate indexes and verify isolation |
| Scanned or complex PDFs | Medium | Developer | Reject unsupported extraction and explain OCR scope |
| API cost exceeds budget | Medium | Project owner | Agree spending cap and log usage |
| Prompt injection in uploaded text | High | Developer | Treat retrieved content as data and test malicious fixtures |
| Retention expectations unclear | High | Project owner | Confirm deletion policy before real-user deployment |

## Reviewer questions
Confirm language support, proposed size limits, external API processing consent, retention duration, hosting access and API budget. No interview responses or approval signatures have been invented.

## Approval record
Reviewer name: not recorded. Decision: not recorded. Date: not recorded. Comments: not recorded.
