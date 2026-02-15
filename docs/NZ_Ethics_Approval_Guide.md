# New Zealand Ethics Approval Guide for WebTics

Comprehensive guide for obtaining ethics approval for research using WebTics in New Zealand.

## New Zealand Ethics System (Not "IRB")

**Important**: New Zealand does not use the US Institutional Review Board (IRB) system. Instead:

- **Health research** → Health and Disability Ethics Committees (HDECs)
- **University research** → University Human Ethics Committees
- **Māori research** → Requires Māori consultation

## When Do You Need Ethics Approval?

### Health and Disability Ethics Committees (HDEC)

**Required for:**
- Research involving health or disability information
- Mental health interventions (ADHD games, depression, anxiety)
- Therapeutic games making health claims
- Research in health/disability sector settings
- Māori health research

**WebTics scenarios requiring HDEC:**
- ✅ ADHD assessment games
- ✅ Mental health therapeutic games
- ✅ Cognitive rehabilitation games
- ✅ Clinical validation studies
- ❌ General game analytics (not health-related)

**HDEC Website**: https://ethics.health.govt.nz/

### University Human Ethics Committees

**Required for:**
- Educational research
- Social science studies
- Behavioral research (non-health)
- Student projects involving human participants

**Each university has its own committee:**
- University of Auckland: UAHPEC
- Victoria University of Wellington: Human Ethics Committee
- University of Otago: Human Ethics Committees
- Massey University: Human Ethics Committees
- etc.

**WebTics scenarios requiring university ethics:**
- ✅ Educational game research
- ✅ Game design studies
- ✅ Player behavior research
- ✅ Student thesis projects

### Māori Research Considerations

**If your research involves Māori participants or Māori data:**

1. **Māori consultation required** (HDEC policy)
2. Consider **Kaupapa Māori research** approach
3. Engage with **iwi** or **hapū** if appropriate
4. Follow **Te Ara Tika** guidelines (Māori ethics framework)

**Resources:**
- Te Ara Tika: Guidelines for Māori Research Ethics
- Te Mana Raraunga (Māori Data Sovereignty Network)
- Health Research Council Māori Health Research Guidelines

## Legal Framework

### 1. Privacy Act 2020

**13 Information Privacy Principles (IPPs):**

**WebTics compliance:**
- IPP 1: Purpose of collection → Disclosed in consent
- IPP 3: Collection from individual → Direct from participant
- IPP 5: Security safeguards → Encryption, access control
- IPP 6: Right of access → Participant data export endpoint
- IPP 7: Right of correction → Withdrawal and re-consent
- IPP 11: Limits on disclosure → Data not shared with third parties
- IPP 12: Unique identifiers → Pseudonymous participant IDs

### 2. Health Information Privacy Code 2020 (HIPC)

**12 Rules for health information:**

**WebTics compliance:**
- Rule 1: Purpose of collection → Clear consent process
- Rule 5: Security safeguards → TLS, encryption, NZ hosting
- Rule 6: Right of access → Data export for participants
- Rule 11: Limits on use → Data used only for research purpose
- **Rule 12: Unique identifiers and overseas disclosure** → Critical for WebTics

**Rule 12 Requirements:**
- Health information must remain in New Zealand (unless consent)
- No disclosure to overseas entities without authorization
- **WebTics solution**: Catalyst Cloud NZ hosting (Wellington/Hamilton)

### 3. Health and Disability Commissioner Act 1994

**Code of Rights - Right 7:**
- Right to make informed choices
- Effective informed consent
- Right to withdraw consent

**WebTics compliance:**
- Informed consent process before data collection
- Withdrawal code system for easy opt-out
- No coercion or undue influence

### 4. Mental Health Act 1992

**Considerations for mental health research:**
- Vulnerable population protections
- Capacity to consent
- Additional safeguards for compulsory patients
- Special ethics review procedures

**WebTics recommendations:**
- Exclude compulsory patients unless specific approval
- Include capacity assessment
- Provide accessible consent materials
- Offer support person option

## HDEC Application Process

### Step 1: Determine if HDEC Approval Needed

Use the **HDEC scope of review** flowchart:
https://ethics.health.govt.nz/quick-reference-guides/

**Questions to ask:**
1. Does it involve health/disability information? → Yes = HDEC
2. Is it an intervention? → Yes = HDEC
3. Is it in a health setting? → Likely HDEC
4. Does it involve Māori health? → Yes = HDEC + consultation

### Step 2: Choose HDEC Committee

**National committees:**
- Health and Disability Ethics Committees (4 regional committees)
- Choose based on your location

**Submission portal**: https://ethics.health.govt.nz/

### Step 3: Prepare Application

**Required documents:**
1. **Application form** (online portal)
2. **Participant information sheet**
3. **Consent form**
4. **Data management plan** ← WebTics provides this
5. **Locality approval** (if in health facilities)
6. **Māori consultation** (if relevant)
7. **Conflict of interest declaration**
8. **CV of principal investigator**

**WebTics-specific documents:**
- Privacy impact assessment
- Security measures (encryption, NZ hosting)
- Data retention policy
- Withdrawal process documentation
- Sample withdrawal code instructions

### Step 4: Submit and Wait

**Timeline:**
- Expedited review: ~35 working days
- Full review: ~60 working days
- Māori consultation: Add 4-6 weeks

**Possible outcomes:**
- Approved
- Approved with conditions
- Deferred (need more info)
- Declined

### Step 5: Obtain Locality Approval

If research in DHB/hospital:
- Separate locality approval required
- Each site needs approval
- Can apply after HDEC approval

## University Ethics Application

### Example: Victoria University of Wellington

**Process:**
1. Complete ethics application via online portal
2. Attach participant information sheet
3. Attach consent form
4. Describe WebTics data collection
5. Attach WebTics privacy documentation

**Timeline:** 4-6 weeks

**Categories:**
- Low risk: Chair's approval (2 weeks)
- Medium risk: Subcommittee review (4 weeks)
- High risk: Full committee review (6+ weeks)

## WebTics Documentation for Ethics Applications

### 1. Data Management Plan

**Template provided in**: [Research_Ethics_Privacy.md](Research_Ethics_Privacy.md)

**Includes:**
- What data is collected
- Where data is stored (Catalyst Cloud NZ)
- Who has access (research team only)
- How long data is retained
- How data is secured (TLS, encryption)
- How participants can withdraw
- How data is destroyed after study

### 2. Participant Information Sheet

**WebTics template sections:**

```markdown
# Participant Information Sheet

## What is this study about?
[Your research description]

## What data will be collected?
This study uses WebTics telemetry system to collect:
- Gameplay events (button presses, responses)
- Reaction times and accuracy
- Session duration and frequency

NO personal information is collected (no name, email, or contact details).

## How is my privacy protected?
- Data identified only by random code (e.g., "P-a3f8b2c1")
- Data encrypted and stored in New Zealand
- Complies with Privacy Act 2020 and HIPC 2020
- Only research team can access data

## Can I withdraw?
YES. You will receive a WITHDRAWAL CODE when you enroll.

To withdraw:
1. Visit: https://webtics.example.com/withdraw
2. Enter your withdrawal code
3. All your data will be permanently deleted

You can withdraw at any time without penalty.

## Where is my data stored?
Data is stored on Catalyst Cloud servers in Wellington/Hamilton, New Zealand.
Data does not leave New Zealand.

## How long is data kept?
Data will be deleted after [X years] or upon withdrawal, whichever comes first.
```

### 3. Consent Form

**WebTics template:**

```markdown
# Research Consent Form

Study: [Your study title]
Researcher: [Your name]
Ethics approval: [HDEC reference or university reference]

I have read the Participant Information Sheet and understand:
☐ What the study involves
☐ What data will be collected
☐ How my privacy is protected
☐ My right to withdraw at any time

I consent to participate in this research.

Name: _______________________
Date: _______________________
Signature: _______________________

---

IMPORTANT: Your withdrawal code is:

WC-xxxx-xxxx-xxxx-xxxx

Keep this code safe. You need it to withdraw from the study.
```

### 4. Privacy Impact Assessment

**Provided by WebTics** in [Research_Ethics_Privacy.md](Research_Ethics_Privacy.md)

### 5. Security Measures Document

**WebTics security features:**
- TLS 1.3 encryption in transit
- AES-256 encryption at rest
- HMAC-SHA256 for withdrawal codes
- PostgreSQL with row-level security
- Hosted in New Zealand (Catalyst Cloud)
- No offshore data transfer
- Audit logging of all access
- Principle of least privilege

## Sample Ethics Application Sections

### Data Storage and Security

```
Data will be collected using WebTics, a self-hosted telemetry system
compliant with NZ Privacy Act 2020 and HIPC 2020.

Storage location: Catalyst Cloud, Wellington Data Center, New Zealand
Encryption: TLS 1.3 (transit), AES-256 (at rest)
Access control: Research team only, password + 2FA
Data sovereignty: All data remains in New Zealand
Compliance: Privacy Act 2020, HIPC 2020, HDEC guidelines

Technical documentation available at: [GitHub URL]
```

### Participant Withdrawal

```
Participants will receive a unique cryptographic withdrawal code at enrollment.

This code:
- Allows participants to withdraw without researcher involvement
- Cannot be guessed or forged (128-bit security)
- Enables immediate and complete data deletion
- Preserves participant anonymity (researcher cannot link code to individual)

Withdrawal process:
1. Participant visits withdrawal portal
2. Enters withdrawal code
3. System deletes all associated data (< 1 hour)
4. Participant receives confirmation

This system complies with Privacy Act 2020 Principle 6 (access to information)
and supports the right to withdraw as per Code of Health and Disability
Services Consumers' Rights (Right 7).
```

### Māori Consultation (if applicable)

```
Māori consultation:
[If participants include Māori]

We have consulted with [iwi/hapū/Māori advisory group]:
- Date of consultation: [Date]
- Outcomes: [Summary of feedback]
- Changes made: [How we addressed concerns]

We will follow Te Ara Tika principles:
- Tika (research design)
- Manaakitanga (cultural and social responsibility)
- Whakapapa (relationships)
- He Kanohi Kitea (community engagement)
```

## Common Questions from Ethics Committees

### Q: "Why not use existing analytics platforms like Google Analytics?"

**A**: Research-grade data requires:
- Full data ownership (no third-party access)
- NZ data sovereignty (HIPC Rule 12)
- Participant withdrawal capability (Privacy Act)
- No commercial data use (research ethics)
- Audit trail for compliance

Existing platforms fail these requirements.

### Q: "How do you ensure withdrawal codes aren't lost?"

**A**: Multi-factor delivery:
- Display on screen with "save" instruction
- Email to participant (if they provide email)
- Print option
- Screenshot encouragement
- Follow-up reminder email (optional)

Even if lost, data remains anonymous (linked only to "P-a3f8b2c1", not name).

### Q: "What about participants who change their mind after withdrawal deadline?"

**A**: Study protocol specifies:
- Withdrawal deadline: [Before analysis begins / Before publication]
- After deadline: Data aggregated and de-identified
- Individual withdrawal no longer possible
- This is disclosed in consent form

### Q: "How do you prevent malicious deletion of others' data?"

**A**: Security measures:
- Withdrawal codes have 128-bit entropy (impossible to guess)
- Rate limiting on withdrawal endpoint (prevent brute force)
- IP hashing for abuse detection
- Audit trail of all withdrawal attempts
- Invalid code attempts logged for security review

### Q: "What about children or vulnerable populations?"

**A**: Additional safeguards:
- Parental/guardian consent for under 16
- Assent process for children
- Capacity assessment for vulnerable adults
- Simplified consent materials
- Support person option
- Extra privacy protections

## HDEC Application Checklist

- [ ] Determined HDEC approval required
- [ ] Chosen appropriate HDEC committee
- [ ] Completed application form
- [ ] Written participant information sheet (with WebTics privacy info)
- [ ] Written consent form (with withdrawal code instructions)
- [ ] Prepared data management plan
- [ ] Documented WebTics security measures
- [ ] Obtained Māori consultation (if applicable)
- [ ] Identified locality approval needs
- [ ] Prepared CV and conflict of interest declaration
- [ ] Reviewed WebTics compliance documentation
- [ ] Tested withdrawal process
- [ ] Set data retention period
- [ ] Prepared sample withdrawal code delivery

## Timeline for Approval

**Realistic timeline from start to data collection:**

| Step | Duration | Notes |
|------|----------|-------|
| Prepare application | 2-4 weeks | First-time users |
| Māori consultation (if needed) | 4-6 weeks | Add to timeline |
| HDEC submission | 1 day | Online portal |
| HDEC review | 35-60 days | Expedited vs full |
| Respond to queries | 1-2 weeks | If deferred |
| Final approval | 1 week | After conditions met |
| Locality approval | 2-4 weeks | Per site |
| **Total** | **3-6 months** | **Plan accordingly** |

## Post-Approval Obligations

### Annual Progress Reports

HDEC requires annual reports:
- Number of participants recruited
- Number withdrawn
- Any adverse events
- Protocol amendments

**WebTics can provide:**
- Aggregate participant numbers (via `/study/{id}/stats` API)
- Withdrawal counts and dates
- Audit logs

### Protocol Amendments

If you change:
- Study procedures
- Data collection methods
- Consent process
- WebTics configuration

**You must submit amendment to HDEC** (and re-approval)

### Final Report

At study completion:
- Submit final report to HDEC
- Report findings
- Confirm data retention/destruction plan

## Resources

### Official Websites

- **HDEC**: https://ethics.health.govt.nz/
- **Privacy Commissioner**: https://privacy.org.nz/
- **Health and Disability Commissioner**: https://www.hdc.org.nz/
- **Māori Data Sovereignty**: https://www.temanararaunga.maori.nz/

### Guidelines

- **HDEC Operational Procedures**: https://ethics.health.govt.nz/operating-procedures/
- **Te Ara Tika** (Māori Ethics): https://www.hrc.govt.nz/resources/te-ara-tika
- **National Ethics Standards**: https://ethics.health.govt.nz/national-ethics-standards/

### Training

- **GCP Training** (Good Clinical Practice): Required for clinical trials
- **Research Ethics Training**: Many universities offer courses
- **Māori Research Training**: Kaupapa Māori research methods

## Getting Help

### WebTics Support for Ethics Applications

Contact: simon.mccallum@gmail.com

**We can provide:**
- Technical documentation for your application
- Sample consent forms
- Privacy impact assessment
- Security attestation
- Data management plan template
- Letters of support (for established researchers)

### Ethics Committee Queries

If ethics committee has questions about WebTics:
- Direct them to public documentation: [GitHub URL]
- Provide technical contact: simon.mccallum@gmail.com
- Offer demonstration/meeting if needed

## Example: Successful HDEC Application

**Study**: ADHD Assessment Game for Children (Victoria University + CCDHB)

**Ethics path:**
1. Victoria University Human Ethics Committee (Low risk)
2. HDEC Central Committee (Health research)
3. Māori consultation (Te Atiawa)
4. Locality approval (CCDHB)

**Timeline:** 5 months from submission to first participant

**Key success factors:**
- Clear data management plan
- Strong privacy protections (WebTics)
- Māori consultation early
- Responsive to committee questions
- Pilot tested withdrawal process

---

**Document Version:** 1.0
**Last Updated:** February 15, 2026
**Compliance:** NZ Privacy Act 2020, HIPC 2020, HDEC guidelines, Te Ara Tika
