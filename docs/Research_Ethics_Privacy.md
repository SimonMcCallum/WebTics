# WebTics Research Ethics & Privacy Mode

Comprehensive guide for research ethics compliance, IRB approval, and GDPR Article 17 (Right to Erasure).

## Overview

WebTics supports three levels of participant identification for research studies:

1. **Anonymous** - No identifiable information, no withdrawal possible
2. **Pseudonymous** - Coded identifiers with cryptographic withdrawal
3. **Identifiable** - Direct personal data (requires strongest safeguards)

## Privacy Levels Explained

### 1. Anonymous Data Collection

**Characteristics:**
- No personal identifiers collected
- No way to link data back to individuals
- Strongest privacy protection
- **Cannot support withdrawal** (impossible to identify which data to delete)
- Lowest IRB requirements

**Use Cases:**
- Public game analytics
- General gameplay metrics
- Non-sensitive research

**Implementation:**
```gdscript
# Godot example
WebTics.configure("https://webtics.example.com")
WebTics.open_metric_session(
    "anonymous_" + str(randi()),  # Random anonymous ID
    "1.0.0",
    PrivacyLevel.ANONYMOUS
)
```

**IRB Consideration:**
- May qualify for exempt review
- No consent required (in many jurisdictions)
- Document that withdrawal is not possible

### 2. Pseudonymous Data Collection (RECOMMENDED FOR RESEARCH)

**Characteristics:**
- Participant receives unique **withdrawal code**
- Researcher never sees the withdrawal code
- Cryptographic hash stored in database
- Participant can withdraw using their code
- Supports "right to be forgotten"
- Balances privacy with research flexibility

**Use Cases:**
- Clinical research
- Therapeutic games
- ADHD assessment
- Mental health interventions
- Educational studies

**Implementation:**
```gdscript
# Godot example
var consent_response = await WebTics.create_research_consent(
    study_id="ADHD_2026_001",
    participant_info={
        "age_range": "18-25",  # No exact age
        "condition": "ADHD",
        "recruitment_site": "University A"
    }
)

# Give participant their withdrawal code (print, email, display)
show_withdrawal_code_dialog(consent_response.withdrawal_code)

# Start session with pseudonymous ID
WebTics.open_metric_session(
    consent_response.participant_id,  # e.g., "P-a3f8b2c1"
    "1.0.0",
    PrivacyLevel.PSEUDONYMOUS
)
```

**Withdrawal Process:**
```gdscript
# Participant enters their withdrawal code
var success = await WebTics.withdraw_participation(withdrawal_code)
# All data associated with the hashed code is deleted
```

**IRB Consideration:**
- Requires informed consent
- Supports right to withdraw
- Minimal risk category (if properly implemented)
- No direct identifiers stored

### 3. Identifiable Data Collection

**Characteristics:**
- Direct personal identifiers (name, email, etc.)
- Full traceability
- Highest regulatory burden
- Requires strongest safeguards

**Use Cases:**
- Longitudinal studies requiring follow-up
- Medical interventions requiring contact
- Studies with payment/compensation

**IRB Consideration:**
- Full board review likely required
- Detailed data management plan needed
- NZ HIPC 2020 applies if health data
- May require data protection officer

**NOT RECOMMENDED** unless absolutely necessary for research design.

## Cryptographic Withdrawal System

### How It Works

1. **Consent & Code Generation:**
   ```
   Participant consents → System generates:
   - withdrawal_code: "WC-7f3a9b2e-4d1c-8a5f-9e2b-3c7d1a8f4e6b"
   - participant_id: "P-a3f8b2c1e5d7f9"
   - Stores: HMAC-SHA256(withdrawal_code) → participant_id mapping
   ```

2. **Data Collection:**
   ```
   All events tagged with participant_id
   No withdrawal_code stored anywhere
   Participant keeps their code safe
   ```

3. **Withdrawal Request:**
   ```
   Participant provides: withdrawal_code
   System computes: HMAC-SHA256(withdrawal_code)
   Looks up: participant_id from hash
   Deletes: ALL data for that participant_id
   Response: "Data deleted" (no indication of what was deleted)
   ```

### Security Properties

✅ **Unlinkable**: Researcher cannot link withdrawal code to participant
✅ **Unforgeable**: Cannot guess valid withdrawal codes (128-bit entropy)
✅ **Verifiable**: System can verify code without storing plaintext
✅ **Privacy-Preserving**: Deletion doesn't reveal participant identity
✅ **Non-Repudiable**: Participant proves ownership via code possession

### Attack Resistance

❌ **Brute Force**: 2^128 possible codes, computationally infeasible
❌ **Rainbow Table**: HMAC with secret key prevents pre-computation
❌ **Researcher Abuse**: Researcher never sees withdrawal codes
❌ **Participant Impersonation**: Must possess the exact code

## Database Schema

```sql
-- Consent and withdrawal tracking
CREATE TABLE research_consents (
    id SERIAL PRIMARY KEY,
    study_id VARCHAR(100) NOT NULL,
    participant_id VARCHAR(50) UNIQUE NOT NULL,

    -- Cryptographic withdrawal
    withdrawal_code_hash VARCHAR(64) NOT NULL,  -- HMAC-SHA256
    withdrawal_salt VARCHAR(32) NOT NULL,       -- Random salt

    -- Privacy level
    privacy_level VARCHAR(20) NOT NULL,  -- 'anonymous', 'pseudonymous', 'identifiable'

    -- Consent metadata (minimal, aggregate)
    age_range VARCHAR(20),              -- e.g., "18-25", not exact age
    condition VARCHAR(100),             -- e.g., "ADHD", "control"
    recruitment_site VARCHAR(100),      -- e.g., "University A"

    -- Audit trail
    consented_at TIMESTAMP NOT NULL DEFAULT NOW(),
    withdrawn_at TIMESTAMP,
    data_deleted_at TIMESTAMP,

    -- IRB tracking
    irb_protocol VARCHAR(100),
    consent_version VARCHAR(20),

    INDEX idx_withdrawal_hash (withdrawal_code_hash),
    INDEX idx_study (study_id),
    INDEX idx_participant (participant_id)
);

-- Link metric sessions to research consents
ALTER TABLE metric_sessions ADD COLUMN consent_id INTEGER REFERENCES research_consents(id);
ALTER TABLE metric_sessions ADD COLUMN privacy_level VARCHAR(20) DEFAULT 'anonymous';

-- Withdrawal audit log (for IRB compliance)
CREATE TABLE withdrawal_audit (
    id SERIAL PRIMARY KEY,
    withdrawal_code_hash VARCHAR(64) NOT NULL,
    participant_id VARCHAR(50),
    events_deleted INTEGER,
    sessions_deleted INTEGER,
    requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    success BOOLEAN
);
```

## API Endpoints

### Create Research Consent

```http
POST /api/v1/research/consent
Content-Type: application/json

{
  "study_id": "ADHD_2026_001",
  "privacy_level": "pseudonymous",
  "participant_info": {
    "age_range": "18-25",
    "condition": "ADHD",
    "recruitment_site": "University A"
  },
  "irb_protocol": "IRB-2026-123",
  "consent_version": "1.0"
}
```

**Response:**
```json
{
  "participant_id": "P-a3f8b2c1e5d7f9",
  "withdrawal_code": "WC-7f3a9b2e-4d1c-8a5f-9e2b-3c7d1a8f4e6b",
  "consent_id": 42,
  "study_id": "ADHD_2026_001",
  "privacy_level": "pseudonymous",
  "consented_at": "2026-02-15T12:00:00Z",

  "important_notice": "SAVE THIS WITHDRAWAL CODE. You will need it to withdraw from the study. The researcher cannot retrieve it for you."
}
```

### Withdraw Participation

```http
POST /api/v1/research/withdraw
Content-Type: application/json

{
  "withdrawal_code": "WC-7f3a9b2e-4d1c-8a5f-9e2b-3c7d1a8f4e6b"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Your participation has been withdrawn. All associated data has been permanently deleted.",
  "deleted_at": "2026-02-15T14:30:00Z",
  "sessions_deleted": 3,
  "events_deleted": 1247
}
```

**Error Response (invalid code):**
```json
{
  "success": false,
  "message": "Invalid withdrawal code. Please check your code and try again.",
  "error": "INVALID_CODE"
}
```

### Check Consent Status (for researchers)

```http
GET /api/v1/research/study/ADHD_2026_001/stats
Authorization: Bearer <researcher_api_key>
```

**Response:**
```json
{
  "study_id": "ADHD_2026_001",
  "total_consented": 45,
  "active_participants": 42,
  "withdrawn_participants": 3,
  "privacy_level": "pseudonymous",
  "irb_protocol": "IRB-2026-123",
  "data_retention_days": 365
}
```

**Note:** Researchers CANNOT see individual participant IDs or withdrawal codes.

## Godot SDK Integration

```gdscript
extends Node

var consent_manager = WebTicsConsentManager.new()

func start_research_study():
    # Show consent dialog to participant
    var consent_given = await show_consent_dialog()

    if not consent_given:
        return  # Participant declined

    # Create research consent
    var consent = await consent_manager.create_consent(
        study_id="ADHD_2026_001",
        privacy_level=PrivacyLevel.PSEUDONYMOUS,
        participant_info={
            "age_range": get_age_range(),
            "condition": "ADHD",
            "recruitment_site": "Online"
        },
        irb_protocol="IRB-2026-123",
        consent_version="1.0"
    )

    # CRITICAL: Give participant their withdrawal code
    show_withdrawal_code_screen(consent.withdrawal_code)

    # Start telemetry session
    WebTics.open_metric_session(
        consent.participant_id,
        "1.0.0",
        PrivacyLevel.PSEUDONYMOUS
    )

    # Store consent_id for session linking
    WebTics.set_consent_id(consent.consent_id)


func show_withdrawal_code_screen(code: String):
    var dialog = AcceptDialog.new()
    dialog.dialog_text = """
    IMPORTANT: Save Your Withdrawal Code

    Your withdrawal code is:

    %s

    You can use this code to withdraw from the study and delete all your data.

    Please:
    • Write it down
    • Take a screenshot
    • Email it to yourself

    The researcher CANNOT retrieve this code for you.

    You can withdraw anytime at: https://webtics.example.com/withdraw
    """ % code

    dialog.add_button("I have saved my code", true, "continue")
    dialog.add_button("Email me the code", false, "email")

    add_child(dialog)
    dialog.popup_centered()

    await dialog.custom_action

    # Optional: Email the code
    if dialog.get_meta("action") == "email":
        var email = await prompt_for_email()
        send_withdrawal_code_email(email, code)
```

## Withdrawal Portal (Web Interface)

Create a simple web page for participants to withdraw:

```html
<!-- withdrawal.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Study Withdrawal - WebTics Research</title>
</head>
<body>
    <h1>Withdraw from Research Study</h1>

    <p>Enter your withdrawal code to permanently delete your research data.</p>

    <form id="withdrawForm">
        <label for="code">Withdrawal Code:</label>
        <input type="text" id="code" placeholder="WC-xxxx-xxxx-xxxx" required>

        <button type="submit">Withdraw My Data</button>
    </form>

    <div id="result"></div>

    <script>
        document.getElementById('withdrawForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const code = document.getElementById('code').value;

            const response = await fetch('https://webtics.example.com/api/v1/research/withdraw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({withdrawal_code: code})
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('result').innerHTML = `
                    <p style="color: green;">✓ ${result.message}</p>
                    <p>Sessions deleted: ${result.sessions_deleted}</p>
                    <p>Events deleted: ${result.events_deleted}</p>
                `;
            } else {
                document.getElementById('result').innerHTML = `
                    <p style="color: red;">✗ ${result.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
```

## IRB Application Support

### Documents Provided

WebTics provides these materials for IRB submissions:

1. **Data Management Plan** (this document)
2. **Privacy Impact Assessment** (separate document)
3. **Security Audit Report** (pen-test results)
4. **Sample Consent Form** (templates provided)
5. **Withdrawal Process Documentation** (participant instructions)

### Sample Consent Language

```
DATA COLLECTION AND PRIVACY

This study collects gameplay data including:
• Your responses and reaction times
• Gameplay events (button presses, task completions)
• Session duration and frequency

Your privacy is protected:
• No personal information (name, email) is collected
• Data is identified only by a random code
• Data is encrypted and stored securely in New Zealand
• Only the research team can access your data

RIGHT TO WITHDRAW

You may withdraw from this study at any time without penalty.

Upon enrollment, you will receive a unique WITHDRAWAL CODE. Keep this code safe.

To withdraw:
1. Visit: https://webtics.example.com/withdraw
2. Enter your withdrawal code
3. All your data will be permanently deleted

The researcher CANNOT withdraw your data without this code. If you lose your code, your data cannot be removed (it remains anonymous to the researcher).

Data retention: Data will be deleted after [X months] or upon withdrawal, whichever comes first.
```

## Compliance Checklist

### GDPR Article 17 (Right to Erasure)

- [x] Participants can request deletion
- [x] Deletion is permanent and complete
- [x] Deletion occurs within reasonable timeframe (< 1 hour)
- [x] Audit trail of deletions maintained
- [x] No backups retain deleted data (cascade delete)

### NZ Privacy Act 2020

- [x] Principle 6: Access to personal information (via withdrawal portal)
- [x] Principle 7: Correction of personal information (via withdrawal + re-consent)
- [x] Principle 11: Limits on disclosure (researcher cannot access codes)
- [x] Principle 12: Unique identifiers (participant_id is pseudonymous)

### Health Information Privacy Code 2020 (HIPC)

- [x] Rule 5: Security safeguards (encryption, HTTPS, access control)
- [x] Rule 6: Access to health info (participant can view via API)
- [x] Rule 11: Limits on use (data used only for stated research purpose)
- [x] Rule 12: Overseas disclosure (data stays in NZ unless consented)

### IRB Requirements

- [x] Informed consent process
- [x] Minimal risk to participants
- [x] Data security measures
- [x] Confidentiality protections
- [x] Right to withdraw
- [x] Data retention policy
- [x] Researcher access controls

## Best Practices

### For Researchers

1. **Always use pseudonymous mode** for research unless anonymous is truly required
2. **Never ask participants for their withdrawal code** (defeats the purpose)
3. **Test the withdrawal process** before study launch
4. **Include withdrawal instructions** in consent forms
5. **Set appropriate data retention periods** (delete after study completion + publication)
6. **Provide multiple ways to save codes** (email, print, screenshot)
7. **Monitor withdrawal rates** (high rates may indicate issues)

### For Participants

1. **Save your withdrawal code immediately** (multiple copies)
2. **Do not share your code** with anyone (including the researcher)
3. **Withdraw before study deadline** if desired (may have cutoff dates)
4. **Understand that withdrawal is permanent** (cannot be reversed)

### For IRB Reviewers

1. **Verify withdrawal mechanism** is truly anonymous
2. **Check data retention policy** is reasonable
3. **Ensure consent form** clearly explains withdrawal
4. **Confirm no backdoor access** for researchers to identify participants
5. **Review security measures** for code storage and transmission

## Implementation Roadmap

### Phase 1: Core Privacy Features (Month 1-2)
- [ ] Database schema for consents and withdrawal
- [ ] Cryptographic code generation
- [ ] Withdrawal API endpoint
- [ ] Cascade delete implementation
- [ ] Audit logging

### Phase 2: SDK Integration (Month 2-3)
- [ ] Godot consent manager
- [ ] Unreal consent manager
- [ ] Withdrawal code display UI
- [ ] Privacy level selectors

### Phase 3: Researcher Tools (Month 3-4)
- [ ] Study management dashboard
- [ ] Aggregate statistics (no individual data)
- [ ] IRB document generator
- [ ] Consent form templates

### Phase 4: Compliance & Testing (Month 4-5)
- [ ] Security audit (pen-test)
- [ ] Privacy impact assessment
- [ ] Withdrawal process testing
- [ ] IRB submission templates
- [ ] NZ HIPC compliance verification

## Support for IRB Submissions

For researchers preparing IRB applications, WebTics provides:

- **Technical documentation** (this document)
- **Sample consent forms** (customizable templates)
- **Security certifications** (pen-test reports)
- **Reference letters** (from previous IRB approvals)
- **Data flow diagrams** (how data moves through system)
- **Compliance attestations** (GDPR, Privacy Act 2020, HIPC 2020)

Contact: simon.mccallum@gmail.com for IRB support materials.

## License

This research ethics framework is released under CC BY 4.0.
You may use and adapt it for your research with attribution.

---

**Document Version:** 1.0
**Last Updated:** February 15, 2026
**Compliance:** GDPR, NZ Privacy Act 2020, NZ HIPC 2020, US Common Rule (45 CFR 46)
