# UK Medical Device Standards Assessment for WebTics

**Assessment Date:** February 16, 2026
**WebTics Version:** Development (pre-1.0)
**Use Case:** ADHD Assessment Telemetry & Therapeutic Game Analytics
**Target Classification:** UK MHRA Class I Medical Device (Software)

---

## Executive Summary

This document assesses WebTics telemetry system against UK medical device regulatory requirements for use in ADHD assessment and therapeutic gaming. WebTics is currently **NOT compliant** with UK medical device standards and would require significant process improvements and documentation to achieve Class I certification.

**Key Findings:**
- ✅ **Technical Security**: Strong encryption, NZ data sovereignty suitable for UK GDPR
- ❌ **Software Development Lifecycle**: No formal IEC 62304 compliance
- ❌ **Risk Management**: No ISO 14971 risk management process documented
- ❌ **Quality Management**: No ISO 13485 QMS in place
- ❌ **Clinical Risk Management**: No DCB0129/DCB0160 clinical safety documentation

**Estimated Effort to Compliance:** 6-12 months with dedicated quality and regulatory resources

**Recommendation:** For research use under NHS HRA approval, WebTics can be deployed with enhanced documentation. For commercial deployment as a Class I medical device, full regulatory compliance pathway required.

---

## UK Regulatory Framework Overview

### 1. MHRA Class I Medical Device Requirements

**What is Class I?**
- Lowest risk classification for medical devices
- Self-assessment by manufacturer (no notified body required)
- Requires CE UKCA marking from April 2026
- Annual registration fee: £300 per GMDN category

**WebTics Classification Analysis:**

| Criteria | WebTics Status | Class I Applicability |
|----------|----------------|----------------------|
| **Intended Purpose** | "Data collection for ADHD assessment and therapeutic game analysis" | ✅ Diagnostic support = Medical purpose |
| **Risk Level** | Low (non-invasive data collection only) | ✅ Appropriate for Class I |
| **Therapeutic Claims** | NO claims of diagnosis or treatment (data collection only) | ✅ Reduces risk classification |
| **Patient Contact** | None (software only, no hardware) | ✅ Class I suitable |
| **AI/Algorithm** | Basic statistical aggregation (no ML diagnosis) | ✅ Non-active algorithm |

**Conclusion:** WebTics **qualifies for Class I** classification if used for ADHD assessment data collection, provided it makes no diagnostic or therapeutic claims.

**MHRA Registration Requirements:**
1. Register manufacturer with MHRA (£300/year)
2. Appoint UK Responsible Person (UKRP) if manufacturer outside UK
3. Compile Technical Documentation (see below)
4. Self-declare conformity (Declaration of Conformity)
5. Apply CE UKCA marking
6. Implement post-market surveillance

**Current WebTics Status:** ❌ None of these steps completed

---

### 2. IEC 62304: Medical Device Software Lifecycle

**Standard Overview:**
- International standard for medical device software development
- Defines software lifecycle processes from planning to retirement
- Three safety classes: A (no injury), B (non-serious injury), C (death/serious injury)

**WebTics Safety Classification:**

WebTics would be **Class B** under IEC 62304:
- **Not Class A**: Software contributes to medical assessment (not purely informational)
- **Not Class C**: Cannot directly cause death or serious injury (data collection only)
- **Class B**: Software malfunction could lead to non-serious injury (e.g., incorrect ADHD assessment data leading to delayed diagnosis)

**IEC 62304 Process Requirements for Class B:**

| Process Area | IEC 62304 Requirement | WebTics Current Status | Gap Analysis |
|--------------|----------------------|------------------------|--------------|
| **Software Development Planning** | Documented development plan, standards, methods | ❌ No formal plan | Need: Software Development Plan (SDP) |
| **Requirements Analysis** | Functional, performance, safety requirements documented | ⚠️ Partial (GitHub issues, docs) | Need: Formal Requirements Specification |
| **Architectural Design** | Software architecture documented | ⚠️ Partial (README, implementation plan) | Need: Software Architecture Document (SAD) |
| **Detailed Design** | Module-level design specification | ❌ No formal documentation | Need: Detailed Design Specification |
| **Unit Testing** | Unit tests with documented results | ⚠️ Partial (tests exist, not documented for medical use) | Need: Unit Test Protocol & Report |
| **Integration Testing** | Integration tests documented | ⚠️ Partial | Need: Integration Test Protocol & Report |
| **System Testing** | System-level testing against requirements | ❌ No formal testing | Need: System Test Protocol & Report |
| **Risk Management** | Software risks identified and controlled | ❌ No risk analysis | Need: Software Risk Management File (per ISO 14971) |
| **Configuration Management** | Version control, change control | ✅ Git versioning in place | **COMPLIANT** |
| **Problem Resolution** | Bug tracking and resolution process | ⚠️ GitHub issues (informal) | Need: Formal problem resolution process |
| **Traceability** | Requirements → Design → Code → Tests | ❌ No traceability matrix | Need: Traceability Matrix |
| **Software Release** | Release checklist and approval | ❌ No release process | Need: Software Release Procedure |

**Estimated Documentation Effort:**
- Software Development Plan: 2-3 weeks
- Requirements Specification: 3-4 weeks
- Architecture & Design Documents: 4-6 weeks
- Test Protocols & Reports: 6-8 weeks
- Traceability Matrix: 2-3 weeks
- **Total: 4-6 months** with dedicated technical writer + QA engineer

---

### 3. ISO 14971: Risk Management for Medical Devices

**Standard Overview:**
- Risk management throughout device lifecycle
- Hazard identification, risk estimation, risk control, residual risk evaluation
- Post-market surveillance and risk monitoring

**Required Risk Management Activities:**

#### 3.1 Risk Analysis

**Hazards to Identify for WebTics:**

| Hazard Category | Example Hazards | Current Mitigation | Gap |
|-----------------|-----------------|-------------------|-----|
| **Data Loss** | Database failure loses ADHD assessment data | ⚠️ PostgreSQL, daily backups recommended | Need: Formal backup validation testing |
| **Data Corruption** | Software bug corrupts event timestamps | ❌ No validation checks | Need: Data integrity checks, checksums |
| **Incorrect Data** | Event logging error records wrong response time | ❌ No data validation | Need: Input validation, range checks |
| **Unauthorized Access** | Breach exposes participant health data | ✅ TLS, encryption, access control | **ACCEPTABLE** (document in risk file) |
| **Data Sovereignty Breach** | Data accidentally sent offshore | ⚠️ NZ hosting documented | Need: Technical controls (geo-blocking) |
| **Unavailability** | Server downtime prevents data collection | ⚠️ Offline queue in SDK | **ACCEPTABLE** (document) |
| **Software Crash** | Backend crash loses in-flight events | ⚠️ Offline queue | **ACCEPTABLE** (document) |
| **Misinterpretation** | Researcher misinterprets data due to poor dashboard | ❌ No user training materials | Need: User manual, training materials |

#### 3.2 Risk Estimation

**Risk Matrix (Severity × Probability):**

| Risk | Severity | Probability | Risk Level | Action Required |
|------|----------|-------------|------------|-----------------|
| Data loss (unrecoverable) | Serious (delayed diagnosis) | Low (with backups) | **Medium** | Additional controls needed |
| Data corruption (undetected) | Serious | Low | **Medium** | Data validation needed |
| Unauthorized access breach | Serious | Very Low (strong encryption) | **Low** | Acceptable with monitoring |
| Server unavailability | Minor (offline queue handles) | Medium | **Low** | Acceptable as-is |
| Incorrect event timestamp | Moderate (affects assessment accuracy) | Low | **Low** | Acceptable with validation |

#### 3.3 Risk Control Measures Needed

**High Priority:**
1. **Automated Data Integrity Checks**
   - Hash validation for event data
   - Timestamp ordering validation
   - Range checks for numeric values (e.g., reaction time > 0ms, < 10,000ms)

2. **Database Backup Validation**
   - Automated backup testing (weekly restore tests)
   - Backup integrity verification
   - Off-site backup storage (separate NZ data center)

3. **User Training Materials**
   - Researcher manual for data interpretation
   - Warning labels on dashboard for experimental use
   - Limitations of use statement

**Medium Priority:**
4. **Geographic Controls**
   - Firewall rules blocking non-NZ IPs (optional, may block VPN users)
   - DNS verification (ensure hosting in NZ)

5. **Monitoring and Alerting**
   - Database health monitoring
   - Failed event ingestion alerts
   - Anomaly detection for unusual data patterns

**Risk Management File Required:**
- Risk Analysis Report (20-30 pages)
- Risk Control Verification Tests
- Residual Risk Evaluation
- Risk Management Review (annual)

**Estimated Effort:** 4-6 weeks with risk management specialist

---

### 4. ISO 13485: Quality Management System

**Standard Overview:**
- Quality management system for medical device manufacturers
- Covers design, development, production, installation, servicing
- More prescriptive than ISO 9001

**ISO 13485 Requirements for WebTics:**

| Clause | Requirement | WebTics Status | Gap |
|--------|-------------|----------------|-----|
| **4. Quality Management System** | QMS documentation, quality manual | ❌ None | Need: Quality Manual (50-100 pages) |
| **5. Management Responsibility** | Quality policy, objectives, management review | ❌ None | Need: Quality Policy, annual management review |
| **6. Resource Management** | Training records, competence | ❌ Informal | Need: Training matrix, competence records |
| **7.1 Planning** | Product realization planning | ⚠️ Implementation plan exists | Need: Formal Development Plan |
| **7.2 Customer Requirements** | Requirements determination | ⚠️ Partial (researcher needs) | Need: User Requirements Specification |
| **7.3 Design and Development** | Design inputs, outputs, review, verification, validation | ❌ No formal process | **MAJOR GAP** (see below) |
| **7.4 Purchasing** | Supplier evaluation (e.g., cloud hosting) | ❌ None | Need: Supplier approval process |
| **7.5 Production** | Software build process control | ⚠️ Docker containers | Need: Build validation documentation |
| **8.2 Monitoring & Measurement** | Customer feedback, internal audits | ❌ None | Need: Complaint handling, audit schedule |
| **8.3 Nonconforming Product** | Bug handling process | ⚠️ GitHub issues | Need: Nonconformance procedure |

**Design Control (7.3) - Most Critical Gap:**

ISO 13485 Clause 7.3 requires:
1. **Design Inputs**: User needs, regulatory requirements, risk management inputs
   - **WebTics Gap**: No formal User Requirements Specification (URS)
   - **Action**: Create URS document (3-4 weeks)

2. **Design Outputs**: Specifications, drawings, software code
   - **WebTics Gap**: Code exists but no formal design specifications
   - **Action**: Create Software Design Specification (4-6 weeks)

3. **Design Review**: Formal review at each stage
   - **WebTics Gap**: No design review records
   - **Action**: Establish Design Review Board, document reviews (ongoing)

4. **Design Verification**: Does design meet inputs?
   - **WebTics Gap**: No formal verification protocol
   - **Action**: Create Design Verification Protocol & Report (4-6 weeks)

5. **Design Validation**: Does product meet user needs?
   - **WebTics Gap**: No clinical validation
   - **Action**: Conduct usability testing with researchers, document results (8-12 weeks)

6. **Design Transfer**: Handoff to production
   - **WebTics Gap**: No transfer documentation
   - **Action**: Create Design Transfer Report (2 weeks)

7. **Design Changes**: Change control process
   - **WebTics Gap**: Git commits but no formal change control
   - **Action**: Implement Change Control Board (CCB), change request forms (2-4 weeks)

**ISO 13485 Certification:**
- Requires external audit by notified body (e.g., BSI, TÜV SÜD)
- Annual surveillance audits
- Cost: £5,000-£15,000 initial + £2,000-£5,000/year

**Estimated Effort for ISO 13485 Compliance:**
- QMS Documentation: 3-4 months (Quality Manual, SOPs, work instructions)
- Design Control Backfill: 4-6 months (documenting existing design)
- Internal Audits & Training: 2-3 months
- External Certification Audit Preparation: 2-3 months
- **Total: 12-18 months** with dedicated quality manager + technical writer

**Pragmatic Assessment:** ISO 13485 is **NOT required** for Class I devices in UK (only notified body involvement for Class IIa and above). However, having QMS demonstrates due diligence and is recommended for commercial products.

---

### 5. NHS Digital Clinical Safety Standards (DCB0129 / DCB0160)

**Standard Overview:**
- DCB0129: Clinical risk management for **manufacturers** of health IT systems
- DCB0160: Clinical risk management for **deploying organizations** (NHS trusts, universities)

**Applicability to WebTics:**

#### 5.1 DCB0129 (Manufacturer Responsibilities)

**Required Roles:**
1. **Clinical Safety Officer (CSO)**: Clinically qualified person overseeing safety
   - **WebTics Gap**: No CSO appointed (requires MD, RN, or equivalent)
   - **Action**: Appoint CSO (consultant, part-time role)

2. **Hazard Log**: Living document of clinical hazards
   - **WebTics Gap**: No hazard log
   - **Action**: Create and maintain Clinical Hazard Log (similar to ISO 14971 risk file)

**Clinical Safety Case Report Required:**
- Intended use and scope
- Clinical risk management approach
- Hazard analysis specific to clinical use
- Safety requirements derived from hazards
- Verification and validation evidence
- Residual risks and risk/benefit analysis

**WebTics-Specific Clinical Hazards:**

| Hazard | Clinical Impact | Severity | Mitigation |
|--------|----------------|----------|------------|
| **Data loss during ADHD assessment** | Delayed or missed diagnosis | Moderate | Offline queue, backup testing |
| **Incorrect reaction time logging** | Inaccurate ADHD assessment | Moderate | Data validation, range checks |
| **Researcher misinterprets dashboard** | Incorrect clinical decision | Moderate | User training, warning labels |
| **Participant withdrawal fails** | Privacy breach, distrust | Low (non-clinical) | Withdrawal audit trail, testing |
| **System unavailable during assessment** | Assessment interruption | Low | Offline queue handles gracefully |

**Estimated Effort:**
- Appoint CSO: 1-2 weeks (recruitment/contract)
- Clinical Safety Case Report: 6-8 weeks (with CSO input)
- Hazard Log maintenance: 2-4 hours/month (ongoing)

#### 5.2 DCB0160 (Deployment Organization Responsibilities)

**NOT WebTics' responsibility** (burden on NHS trust or university deploying the system)

However, WebTics should **support** deployers by providing:
1. Manufacturer's Clinical Safety Case Report (from DCB0129)
2. Deployment guidance document
3. Training materials for local clinical safety team
4. Incident reporting mechanism

---

## Gap Summary: What WebTics Needs for UK Medical Device Compliance

### Critical Gaps (Must-Have for Class I Certification)

| Gap | Standard | Estimated Effort | Priority |
|-----|----------|------------------|----------|
| **Software Development Plan** | IEC 62304 | 2-3 weeks | **HIGH** |
| **Requirements Specification** | IEC 62304, ISO 13485 | 3-4 weeks | **HIGH** |
| **Risk Management File** | ISO 14971, IEC 62304 | 4-6 weeks | **HIGH** |
| **Design Verification Protocol** | ISO 13485 | 4-6 weeks | **HIGH** |
| **Clinical Safety Case Report** | DCB0129 | 6-8 weeks | **HIGH** |
| **Traceability Matrix** | IEC 62304 | 2-3 weeks | **MEDIUM** |
| **User Manual (Researcher)** | General requirement | 3-4 weeks | **MEDIUM** |
| **Post-Market Surveillance Plan** | MHRA | 1-2 weeks | **MEDIUM** |
| **Technical Documentation File** | MHRA Class I | 4-6 weeks (compile existing) | **MEDIUM** |

**Total Critical Path: 6-9 months** (assuming parallel work where possible)

### High-Value Process Improvements (Beyond Compliance)

1. **Automated Data Validation**
   - Input validation (e.g., reaction time ranges)
   - Timestamp ordering checks
   - JSON schema validation for event data
   - **Effort:** 2-3 weeks development + 2 weeks testing

2. **Backup Validation Testing**
   - Weekly automated backup restore tests
   - Integrity verification scripts
   - Monitoring and alerting
   - **Effort:** 1-2 weeks development

3. **Enhanced Audit Logging**
   - Log all data access for GDPR/HIPC compliance
   - Immutable audit trail (append-only)
   - Audit log review process
   - **Effort:** 2-3 weeks development + integration

4. **Clinical User Training Materials**
   - Video tutorials for researchers
   - Dashboard interpretation guide
   - Limitations of use warnings
   - **Effort:** 3-4 weeks (with clinical input)

5. **Usability Testing**
   - Test with 5-10 researchers
   - Usability issues documented and resolved
   - Validation report for ISO 13485
   - **Effort:** 6-8 weeks (recruit participants, test, analyze, fix, re-test)

---

## Compliance Roadmap

### Option 1: Full Medical Device Certification (12-18 months)

**For:** Commercial deployment, selling to NHS trusts, regulatory compliance

**Phase 1: Foundation (Months 1-3)**
- Appoint Clinical Safety Officer
- Create Software Development Plan
- Write Requirements Specification
- Begin Risk Management File

**Phase 2: Design Documentation (Months 4-6)**
- Software Architecture Document
- Detailed Design Specification
- Traceability Matrix
- Test Protocols (unit, integration, system)

**Phase 3: Verification & Validation (Months 7-9)**
- Execute test protocols
- Usability testing with researchers
- Data validation implementation
- Design Verification Report

**Phase 4: Regulatory Documentation (Months 10-12)**
- Clinical Safety Case Report (DCB0129)
- Technical Documentation File (MHRA)
- Declaration of Conformity
- User Manual and training materials

**Phase 5: Certification & Launch (Months 13-18)**
- MHRA manufacturer registration
- CE UKCA marking application
- Post-market surveillance setup
- Commercial launch

**Resources Required:**
- Clinical Safety Officer (part-time, 20%)
- Quality/Regulatory Specialist (full-time)
- Technical Writer (full-time, 6 months)
- QA Engineer (full-time)
- Software Developers (2-3, part-time for improvements)

**Budget Estimate:** £150,000 - £250,000

---

### Option 2: Research Use Under Ethics Approval (3-6 months)

**For:** Academic research, NHS HRA approval, pilot studies

**Advantages:**
- Research use exemption from full medical device regulations
- NHS HRA (Health Research Authority) pathway simpler than MHRA
- Can use WebTics under ethics committee oversight

**Phase 1: Enhanced Documentation (Months 1-2)**
- Requirements Specification (lightweight)
- Risk Analysis specific to research use
- Data Management Plan (already exists)
- Privacy Impact Assessment (already exists)

**Phase 2: Clinical Safety (Months 2-4)**
- Appoint Clinical Safety Officer (CSO)
- Clinical Hazard Log for research use
- Researcher User Manual
- Incident reporting procedure

**Phase 3: Validation (Months 4-6)**
- Usability testing with researchers
- Data validation checks implementation
- Backup testing automation
- Pilot study with 1-2 research groups

**Ethics Committee Submission Package:**
- Research protocol
- Consent forms (already created)
- WebTics technical documentation
- Clinical Safety Case (lightweight)
- Risk mitigation plan
- Data security documentation (already exists)

**Resources Required:**
- Clinical Safety Officer (consultant, 10-20%)
- Technical Writer (part-time, 3 months)
- QA Engineer (part-time, 3 months)

**Budget Estimate:** £30,000 - £60,000

**Regulatory Pathway:**
- NHS HRA approval (if NHS participants)
- University Ethics Committee approval
- **NOT** MHRA medical device registration (research exemption)

---

### Option 3: Minimal Compliance for Pilot (1-2 months)

**For:** Immediate pilot testing, proof-of-concept, non-clinical research

**Quick Wins:**
1. **Risk Assessment** (1 week)
   - Identify top 10 risks
   - Document mitigations (use existing: encryption, offline queue, etc.)
   - Create simple risk matrix

2. **User Manual** (2 weeks)
   - Researcher guide to WebTics dashboard
   - Limitations of use statement
   - Troubleshooting guide

3. **Data Validation** (2-3 weeks development)
   - Basic input validation (reaction time ranges, etc.)
   - Timestamp ordering checks
   - Error logging

4. **Backup Testing** (1 week)
   - Document backup procedure
   - Test restore process
   - Schedule regular backup validation

5. **Incident Reporting** (1 week)
   - Create incident report form
   - Define escalation process
   - Document GitHub issue process

**Deliverables:**
- Simple Risk Assessment (5-10 pages)
- User Manual (15-20 pages)
- Data validation code (integrated into backend)
- Backup validation checklist
- Incident reporting procedure

**Resources Required:**
- Technical Writer (part-time, 1 month)
- QA Engineer (part-time, 1 month)

**Budget Estimate:** £8,000 - £15,000

**Use Case:** Research-only deployment with explicit "Not for clinical use" disclaimer

---

## Recommendations

### For Academic Research (Recommended Starting Point)

**Pursue Option 2: Research Use Under Ethics Approval**

**Rationale:**
1. ✅ WebTics already has strong NZ Privacy Act / HIPC compliance (suitable for UK GDPR)
2. ✅ Research exemption avoids full MHRA medical device pathway
3. ✅ 3-6 month timeline feasible for academic projects
4. ✅ Can publish research using WebTics under ethics approval
5. ✅ Budget (£30K-£60K) achievable via research grants

**Action Plan:**
1. **Appoint Clinical Safety Officer** (consultant, part-time)
   - Seek recently retired clinician or NHS consultant with health IT experience
   - 1-2 days/month commitment

2. **Create Enhanced Documentation**
   - Leverage existing WebTics documentation (privacy, consent, NZ compliance)
   - Adapt for UK context (GDPR, NHS HRA)
   - Add: Requirements Spec, Risk Analysis, User Manual

3. **Implement Data Validation Improvements**
   - 2-3 weeks development effort
   - High value for research data quality

4. **Pilot with 1-2 Research Groups**
   - Partner with university or NHS trust
   - Usability testing + validation
   - Refine based on feedback

5. **Submit for NHS HRA Approval**
   - Use enhanced documentation in ethics application
   - Demonstrate clinical safety considerations
   - Position as research telemetry tool, not diagnostic device

**Timeline to First Research Use:** 3-6 months

---

### For Commercial Medical Device (Long-Term Goal)

**Pursue Option 1: Full Medical Device Certification** (after research validation)

**Rationale:**
1. Only pursue if research pilots demonstrate clinical value
2. 12-18 month timeline requires commercial funding
3. ISO 13485 QMS provides competitive advantage
4. Opens door to NHS procurement

**Staged Approach:**
1. **Year 1: Research Use** (Option 2) - Validate WebTics with academic partners
2. **Year 2-3: Medical Device Certification** (Option 1) - If research shows clinical utility
3. **Year 3+: Commercial Launch** - NHS trusts, private healthcare, international

**Funding Strategy:**
- Year 1: Research grants (NIHR, MRC, Wellcome Trust)
- Year 2-3: Innovate UK, SBRI Healthcare, venture capital

---

## Technical Improvements for Compliance

### High-Priority Code Changes

#### 1. Data Validation Middleware (IEC 62304, ISO 14971)

**File:** `backend/app/middleware/data_validation.py`

```python
"""
Data validation middleware for medical device compliance.
Implements input validation, range checks, and error logging per ISO 14971 risk controls.
"""

from fastapi import Request, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger("webtics.validation")

# Validation rules based on risk analysis
VALIDATION_RULES = {
    "reaction_time_ms": (0, 10000),  # 0-10 seconds reasonable for human response
    "accuracy_percent": (0, 100),
    "session_duration_sec": (0, 86400),  # Max 24 hours
}

async def validate_event_data(request: Request, call_next):
    """Validate event data against defined ranges (ISO 14971 risk control)."""
    if request.url.path.startswith("/api/v1/events"):
        body = await request.json()

        # Validate magnitude field (used for reaction times, etc.)
        if "magnitude" in body:
            event_type = body.get("event_type")
            magnitude = body["magnitude"]

            # Example: reaction time validation
            if event_type in [102, 103]:  # CORRECT_RESPONSE, INCORRECT_RESPONSE
                min_val, max_val = VALIDATION_RULES["reaction_time_ms"]
                if not (min_val <= magnitude <= max_val):
                    logger.error(f"Data validation failed: magnitude {magnitude} outside range {min_val}-{max_val}")
                    raise HTTPException(status_code=400, detail=f"Invalid magnitude: must be between {min_val} and {max_val}")

        # Validate timestamp ordering (events must be chronological)
        timestamp = body.get("timestamp", datetime.utcnow().isoformat())
        # TODO: Check timestamp is not in future, not before session start

    response = await call_next(request)
    return response
```

**Integration:** Add to `backend/app/main.py`:
```python
from .middleware.data_validation import validate_event_data
app.middleware("http")(validate_event_data)
```

**Testing Required:** Unit tests for each validation rule, integration tests for rejection handling

---

#### 2. Database Backup Validation Script (ISO 14971)

**File:** `backend/scripts/validate_backup.py`

```python
"""
Automated backup validation script.
Verifies PostgreSQL backups can be restored and data integrity is maintained.
Per ISO 14971 risk control for data loss hazard.
"""

import subprocess
import psycopg2
from datetime import datetime
import hashlib

def validate_latest_backup(backup_dir="/backups", test_db="webtics_backup_test"):
    """
    Restore latest backup to test database and verify integrity.
    Should be run weekly via cron.
    """
    # Find latest backup file
    latest_backup = subprocess.run(
        ["ls", "-t", backup_dir, "|", "head", "-1"],
        capture_output=True, text=True
    ).stdout.strip()

    # Restore to test database
    restore_cmd = f"pg_restore -d {test_db} {backup_dir}/{latest_backup}"
    result = subprocess.run(restore_cmd, shell=True, capture_output=True)

    if result.returncode != 0:
        log_failure(f"Backup restore failed: {result.stderr}")
        return False

    # Verify data integrity (check row counts, sample data)
    conn = psycopg2.connect(database=test_db)
    cur = conn.cursor()

    # Check critical tables exist and have data
    critical_tables = ["metric_sessions", "play_sessions", "events", "research_consents"]
    for table in critical_tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        if count == 0 and table != "research_consents":  # research_consents may be empty
            log_failure(f"Table {table} has 0 rows after restore")
            return False

    log_success(f"Backup validation passed: {latest_backup}")
    return True

def log_success(message):
    with open("/var/log/webtics/backup_validation.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} SUCCESS: {message}\n")

def log_failure(message):
    with open("/var/log/webtics/backup_validation.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} FAILURE: {message}\n")
    # TODO: Send alert to admin email

if __name__ == "__main__":
    validate_latest_backup()
```

**Cron Job:** `0 2 * * 0 /usr/bin/python3 /app/scripts/validate_backup.py` (every Sunday 2am)

---

#### 3. Audit Logging Enhancement (GDPR, DCB0129)

**File:** `backend/app/models_audit.py`

```python
"""
Enhanced audit logging for compliance.
Logs all data access, modification, deletion per GDPR Article 30 (records of processing).
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base

class AuditLog(Base):
    """Immutable audit trail of all data operations."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    actor = Column(String(100))  # User ID, API key, or "SYSTEM"
    action = Column(String(50), nullable=False)  # "CREATE", "READ", "UPDATE", "DELETE"
    resource_type = Column(String(50), nullable=False)  # "event", "session", "consent"
    resource_id = Column(String(100))  # ID of affected resource
    details = Column(Text)  # JSON details of operation
    ip_address_hash = Column(String(64))  # Hashed IP for abuse detection

    def __repr__(self):
        return f"<AuditLog {self.timestamp} {self.actor} {self.action} {self.resource_type}/{self.resource_id}>"
```

**Middleware:** Auto-log all API calls in `backend/app/middleware/audit.py`

---

### Medium-Priority Documentation

#### 1. Software Requirements Specification (IEC 62304)

**File:** `docs/compliance/Software_Requirements_Specification.md`

**Template:**
```markdown
# Software Requirements Specification (SRS)
# WebTics Telemetry System

**Version:** 1.0
**Date:** [Date]
**Author:** [Name]
**Approval:** [CSO Name], Clinical Safety Officer

## 1. Introduction
### 1.1 Purpose
This document specifies functional and non-functional requirements for WebTics medical device software.

### 1.2 Scope
WebTics is a Class I medical device software for collecting telemetry data from ADHD assessment and therapeutic games.

### 1.3 Intended Use
Data collection for research and clinical assessment of ADHD, cognitive function, and therapeutic game effectiveness.

### 1.4 Intended Users
- Clinical researchers
- Healthcare professionals (psychiatrists, psychologists)
- Game developers (under clinical supervision)

## 2. Functional Requirements

### FR-001: Session Management
**Description:** System shall create unique metric sessions for each participant.
**Rationale:** Required to link events to participants while maintaining pseudonymity.
**Acceptance Criteria:**
- Metric session created with unique ID
- Build number recorded
- Timestamp recorded
**Traceability:** Implements user need UN-001, mitigates risk R-005 (data loss)

[Continue for all 50-100 functional requirements...]

## 3. Non-Functional Requirements

### NFR-001: Data Security
**Description:** All data shall be encrypted in transit (TLS 1.3) and at rest (AES-256).
**Rationale:** GDPR Article 32, HIPC 2020 Rule 5 compliance.
**Verification:** Penetration testing, TLS configuration scan

[Continue for all non-functional requirements: performance, reliability, usability, compliance...]

## 4. Safety Requirements (IEC 62304 Class B)

### SR-001: Data Integrity
**Description:** System shall validate all numeric event data is within acceptable ranges.
**Rationale:** Prevents incorrect data from corrupting assessment (ISO 14971 hazard H-003).
**Verification:** Unit tests for validation logic

[Continue...]
```

**Estimated Effort:** 3-4 weeks with clinical input

---

#### 2. Clinical Safety Case Report (DCB0129)

**File:** `docs/compliance/Clinical_Safety_Case_Report.md`

**Template Sections:**
1. Executive Summary
2. Clinical Context and Intended Use
3. Clinical Hazard Log (link to ISO 14971 risk file)
4. Safety Requirements Derived from Hazards
5. Verification and Validation Evidence
6. Residual Risks and Risk/Benefit Analysis
7. Post-Market Surveillance Plan
8. Clinical Safety Officer Declaration

**Estimated Effort:** 6-8 weeks with CSO

---

## Cost-Benefit Analysis

### Investment Required

| Compliance Level | Timeline | Budget | Resources |
|-----------------|----------|--------|-----------|
| **Minimal (Option 3)** | 1-2 months | £8K-£15K | Technical writer, QA (part-time) |
| **Research Use (Option 2)** | 3-6 months | £30K-£60K | CSO (consultant), writer, QA |
| **Full Medical Device (Option 1)** | 12-18 months | £150K-£250K | CSO, quality manager, writer, QA, developers |

### Return on Investment

**Research Use Path (Option 2):**
- **Market:** 50-100 UK research institutions using ADHD assessment games
- **Pricing:** £2,000-£5,000/year per research group (support + hosting)
- **Revenue Potential:** £100K-£500K/year
- **Payback Period:** 6-12 months
- **Strategic Value:** Establishes WebTics as research-grade platform

**Medical Device Path (Option 1):**
- **Market:** 100-200 NHS trusts + private clinics using therapeutic games
- **Pricing:** £10,000-£20,000/year per site (enterprise license + support)
- **Revenue Potential:** £1M-£4M/year
- **Payback Period:** 12-24 months
- **Strategic Value:** Opens procurement contracts, competitive moat via certification

---

## Conclusion

WebTics has **strong technical foundations** (encryption, data sovereignty, consent management) suitable for medical use, but **lacks formal regulatory compliance documentation** required for UK medical device certification.

**Key Findings:**
1. ✅ **Qualifies for Class I medical device** classification (low-risk data collection)
2. ❌ **Not currently compliant** with IEC 62304, ISO 14971, or DCB0129
3. ⚠️ **Significant documentation gap** (6-12 months to close)
4. ✅ **Research use exemption** provides faster path to deployment (3-6 months)

**Recommended Strategy:**
1. **Short-term (2026):** Pursue **Research Use Under Ethics Approval** (Option 2)
   - Appoint Clinical Safety Officer
   - Create essential documentation (requirements, risk analysis, user manual)
   - Pilot with 1-2 academic partners
   - Budget: £30K-£60K

2. **Medium-term (2027-2028):** Evaluate **Full Medical Device Certification** (Option 1)
   - Based on research pilot success
   - Pursue if clinical utility demonstrated
   - Budget: £150K-£250K

3. **Technical Improvements (Immediate):**
   - Implement data validation middleware (2-3 weeks)
   - Automate backup validation testing (1-2 weeks)
   - Enhance audit logging (2-3 weeks)

**Next Steps:**
1. Review this assessment with project stakeholders
2. Decide on compliance pathway (Option 1, 2, or 3)
3. If Option 2 selected: Begin CSO recruitment, requirements documentation
4. If Option 1 selected: Engage regulatory consultant, create project plan
5. Implement technical improvements regardless of pathway (improve data quality)

---

## References

### Regulatory Guidance
1. MHRA, "Guidance on Medical Devices: Software and AI as a Medical Device," January 2025
2. IEC 62304:2006+AMD1:2015, "Medical device software - Software life cycle processes"
3. ISO 14971:2019, "Medical devices - Application of risk management to medical devices"
4. ISO 13485:2016, "Medical devices - Quality management systems"
5. NHS Digital, "DCB0129: Clinical Risk Management - Manufacturer Requirements," v5.0
6. NHS Digital, "DCB0160: Clinical Risk Management - Deployer Requirements," v4.0

### UK Medical Device Registration
7. MHRA Registration Portal: https://devices.mhra.gov.uk/
8. MHRA Guidance: https://www.gov.uk/guidance/medical-devices-conformity-assessment-and-the-ukca-mark

### Additional Standards
9. GDPR (UK GDPR): Data protection requirements
10. ISO/IEC 27001:2022: Information security management
11. ISO/IEC 27018:2019: Cloud privacy
12. OWASP Top 10: Web application security

---

**Document Control:**
- **Version:** 1.0
- **Date:** February 16, 2026
- **Author:** WebTics Development Team
- **Status:** Draft for Review
- **Next Review:** March 2026 (if pursuing compliance pathway)
