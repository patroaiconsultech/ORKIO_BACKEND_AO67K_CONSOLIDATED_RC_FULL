# ORKIO Knowledge Fabric — Google Drive Connector v1

## Status

`proposal_only / inventory_only`

This connector is intentionally limited to metadata inventory and initial classification.

It does **not**:
- download document contents;
- index files into runtime;
- expose personal documents to Orkio;
- create RAG context;
- publish Knowledge Canon entries automatically.

## Required environment

```bash
ORKIO_KF_DRIVE_FOLDER_ID=<folder_id>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Recommended dependency group:

```bash
google-api-python-client
google-auth
```

## Access model

Use a Google Cloud service account with Drive metadata read-only scope.
Share the target Drive folder with the service account email.

Never commit the service-account JSON into GitHub.

## Command

```bash
python scripts/kf_drive_inventory.py   --folder-id "$ORKIO_KF_DRIVE_FOLDER_ID"   --output knowledge_fabric_out/drive_inventory.json
```

## Output

The output contains:
- file id;
- filename;
- MIME type;
- created/modified timestamps;
- web view link;
- checksum when available;
- metadata-only classification;
- sensitivity estimate;
- review status.

## Governance

Every item starts with:

```yaml
runtime_use_allowed: false
requires_human_approval: true
```

The next release may add:
- owner review;
- canonical summary;
- explicit approval workflow;
- Knowledge Canon publication.
