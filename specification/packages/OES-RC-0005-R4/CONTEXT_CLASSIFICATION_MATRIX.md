# Context Classification Matrix

Release Candidate: OES-RC-0005-R4

| Class | Raw content allowed | Founder approval required | Public repository allowed |
|---|---|---|---|
| PUBLIC | false | true | true only after approval |
| INTERNAL | false | true | false |
| FOUNDER_PRIVATE | false | true | false |
| SENSITIVE | false | true | false |
| STRATEGIC_CONFIDENTIAL | false | true | false |
| DO_NOT_USE | false | true | false |

## Source Candidates

`PRIVATE_SOURCE_CANDIDATE` is not a final classification. It is a pre-use holding state.

While a record is a source candidate:

* publication is false;
* content access is false;
* founder approval before use is true;
* allowed current use is limited to `none` or `metadata_only_without_content_access`.
