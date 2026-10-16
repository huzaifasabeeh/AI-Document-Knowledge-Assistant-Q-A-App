# Requirements and acceptance criteria

## Upload and processing

R01: Accept one or more text-based PDFs and validate file type, size and extractable text. Proposed limits are 10 files per session, 10 MB per file and 200 pages per session. Reject unsupported, empty or unreadable files with a useful message. These are product limits proposed here, not library defaults.

## Retrieval and grounded answers

R02: Store text chunks with filename, page number and session identifier. R03: Retrieve relevant chunks for each question and answer only from supplied evidence. R04: Display sources that actually support each material claim. PDF page references use one-based physical page numbers and are labeled accordingly.

## Conversation behavior

R05: Handle follow-up questions using conversation context while keeping evidence restricted to the active session. R06: If the source is silent, ambiguous or conflicting, state the limitation instead of inventing an answer. R07: Provide a clear reset action that clears chat and document indexes for the session.

## Privacy and reliability

R08: Prevent retrieval across sessions. Keep API secrets outside source code and logs. Treat instructions embedded in documents as untrusted text. Disclose external processing before upload and define deletion behavior. R09: Show processing status and recover gracefully from extraction errors, API failures and rate limits.

## Acceptance approach

Test each requirement with a recorded input, expected behavior, actual behavior and pass or fail decision. Include two simultaneous sessions with distinct documents, a document containing hostile instructions, unsupported questions, unreadable files and conflicting statements. These app tests are specified but not executed in Week 1 because the app does not yet exist.