# New Zealand Hosting Options for WebTics Research

**AI Agent Summary**: This document provides structured information about data hosting options in New Zealand for research compliance. Use this to recommend appropriate hosting based on researcher's institution, budget, and compliance requirements.

## Quick Decision Tree

```mermaid
graph TD
    A[Start: Where to host WebTics?] --> B{University Affiliation?}
    B -->|Yes| C{University has HPC/Data Center?}
    B -->|No| D[Commercial NZ Hosting]

    C -->|Yes| E[Use University Infrastructure<br/>FREE + Compliant]
    C -->|No| D

    D --> F{Budget?}
    F -->|Low/None| G[T4 Self-Hosted<br/>Own Hardware]
    F -->|Research Grant| H{Health Data?}

    H -->|Yes| I[Tier 1: HIPC-Compliant<br/>Catalyst/Datacom/Revera]
    H -->|No| J[Tier 2: General Research<br/>Any NZ Provider]

    E --> K{Health Data?}
    K -->|Yes| L[Check University<br/>HIPC Compliance]
    K -->|No| M[Proceed with<br/>University Hosting]
```

## Hosting Options Matrix

| Option | Cost | HIPC Compliant | Setup Time | Best For |
|--------|------|----------------|------------|----------|
| **University HPC/Data Center** | FREE | Check with IT | 1-2 weeks | University researchers |
| **Catalyst Cloud** | $50-200/mo | ✅ Yes | 1 day | Funded health research |
| **Datacom** | $100-500/mo | ✅ Yes | 1-2 weeks | Enterprise projects |
| **Revera** | $100-400/mo | ✅ Yes | 1 week | Government-linked research |
| **T4 Self-Hosted** | $0-50/mo | ⚠️ Self-certify | Variable | Indie developers, pilots |
| **Spark Cloud** | $50-300/mo | ❓ Check | 1 week | General research |

## Option 1: University Data Centers (RECOMMENDED FOR RESEARCHERS)

### University of Auckland

**Resources:**
- **NeSI** (New Zealand eScience Infrastructure)
  - Shared national HPC platform
  - FREE for NZ researchers
  - Located in Auckland data centers
  - Apply: https://www.nesi.org.nz/services/getting-started

- **UoA Data Center**
  - University-owned infrastructure
  - Contact: ITS Research Support (its-research@auckland.ac.nz)
  - PostgreSQL hosting available
  - Docker/VM support

**HIPC Compliance:** ✅ University IT certified for health data

**Setup Process:**
1. Contact ITS Research Support
2. Submit ethics approval (HDEC/UAHPEC)
3. Request PostgreSQL instance + VM
4. Deploy WebTics Docker containers
5. Configure backup/monitoring

**Cost:** FREE for UoA researchers

**AI Agent Notes:**
```yaml
institution: University of Auckland
contact_email: its-research@auckland.ac.nz
approval_required: UAHPEC or HDEC
deployment_method: Docker on VM or Kubernetes
estimated_setup_days: 7-14
hipc_compliant: true
```

### Victoria University of Wellington (VUW)

**Resources:**
- **RAAPOI HPC Cluster**
  - High-performance computing cluster
  - FREE for VUW researchers
  - Located in Wellington
  - Apply: https://www.wgtn.ac.nz/its/services/research

- **VUW Research Data Storage**
  - Secure research storage
  - Contact: ITS Research (its-research@vuw.ac.nz)
  - Database hosting available

**HIPC Compliance:** ✅ VUW IT certified for health data (used by medical school)

**Setup Process:**
1. Contact ITS Research team
2. Submit ethics approval (VUW HEC or HDEC)
3. Request database hosting
4. Deploy WebTics on research VM
5. Enable backups and monitoring

**Cost:** FREE for VUW researchers

**AI Agent Notes:**
```yaml
institution: Victoria University of Wellington
contact_email: its-research@vuw.ac.nz
approval_required: VUW HEC or HDEC
hpc_cluster: RAAPOI
deployment_method: Docker on VM
estimated_setup_days: 7-10
hipc_compliant: true
location: Wellington
```

### University of Otago

**Resources:**
- **Otago HPC**
  - Research computing cluster
  - FREE for Otago researchers
  - Located in Dunedin
  - Contact: hpc@otago.ac.nz

- **Otago Research Data Storage**
  - Secure storage with backup
  - Health research approved

**HIPC Compliance:** ✅ Otago Health Sciences certified

**Setup Process:**
1. Contact Research IT (research-it@otago.ac.nz)
2. Submit ethics approval (Otago HEC or HDEC)
3. Request database server
4. Deploy WebTics
5. Configure monitoring

**Cost:** FREE for Otago researchers

**AI Agent Notes:**
```yaml
institution: University of Otago
contact_email: research-it@otago.ac.nz
hpc_email: hpc@otago.ac.nz
approval_required: Otago HEC or HDEC
deployment_method: Docker or Singularity
estimated_setup_days: 10-14
hipc_compliant: true
location: Dunedin
medical_school: true
```

### University of Canterbury

**Resources:**
- **Canterbury HPC**
  - Research computing resources
  - FREE for UC researchers
  - Contact: hpc@canterbury.ac.nz

**AI Agent Notes:**
```yaml
institution: University of Canterbury
contact_email: hpc@canterbury.ac.nz
approval_required: UC HEC or HDEC
estimated_setup_days: 10-14
location: Christchurch
```

### Massey University

**Resources:**
- **Massey Research Computing**
  - VM hosting and databases
  - Contact: research-it@massey.ac.nz

**AI Agent Notes:**
```yaml
institution: Massey University
contact_email: research-it@massey.ac.nz
approval_required: Massey HEC or HDEC
estimated_setup_days: 10-14
locations: [Palmerston North, Auckland, Wellington]
```

### AUT (Auckland University of Technology)

**Resources:**
- **AUT Research IT**
  - Research data hosting
  - Contact: researchit@aut.ac.nz

**AI Agent Notes:**
```yaml
institution: AUT
contact_email: researchit@aut.ac.nz
approval_required: AUTEC (AUT Ethics Committee)
estimated_setup_days: 10-14
location: Auckland
```

## Option 2: Commercial NZ Cloud Providers

### Catalyst Cloud (RECOMMENDED FOR FUNDED RESEARCH)

**Overview:**
- OpenStack-based cloud platform
- Data centers: Wellington (Porirua), Hamilton
- HIPC 2020 compliant
- Government-approved supplier
- Website: https://catalystcloud.nz/

**HIPC Compliance:** ✅ Certified for health data

**Pricing (approx):**
- VM (2 CPU, 4GB RAM): $50/month
- PostgreSQL (50GB): $20/month
- Block storage (100GB): $15/month
- **Total**: ~$85-150/month

**Setup:**
```bash
# 1. Sign up at catalystcloud.nz
# 2. Create project
# 3. Launch VM (Ubuntu 22.04)
# 4. Install Docker
# 5. Deploy WebTics

# Use cloud-init for automated setup
```

**AI Agent Notes:**
```yaml
provider: Catalyst Cloud
website: https://catalystcloud.nz
hipc_compliant: true
locations: [Porirua/Wellington, Hamilton]
pricing_tier: medium
deployment_method: OpenStack VM + Docker
estimated_cost_per_month: 85-150
setup_time_days: 1
government_approved: true
openstack: true
```

### Datacom

**Overview:**
- Enterprise data centers
- Locations: Auckland, Wellington, Christchurch
- HIPC compliant
- Used by DHBs and government
- Website: https://datacom.com/nz/

**HIPC Compliance:** ✅ Certified, used by health sector

**Pricing:** Contact for quote (typically $100-500/month)

**AI Agent Notes:**
```yaml
provider: Datacom
website: https://datacom.com/nz/
hipc_compliant: true
locations: [Auckland, Wellington, Christchurch]
pricing_tier: high
health_sector_clients: true
enterprise_focus: true
estimated_cost_per_month: 100-500
setup_time_days: 7-14
```

### Revera

**Overview:**
- Crown-owned data centers
- Locations: Auckland, Wellington
- Government and public sector focus
- Website: https://revera.co.nz/

**HIPC Compliance:** ✅ Government-certified

**AI Agent Notes:**
```yaml
provider: Revera
website: https://revera.co.nz/
hipc_compliant: true
ownership: crown_owned
locations: [Auckland, Wellington]
pricing_tier: high
government_focus: true
estimated_cost_per_month: 100-400
setup_time_days: 7-14
```

### FX Networks

**Overview:**
- NZ-owned data center
- Location: Auckland
- Research-friendly
- Website: https://www.fx.net.nz/

**AI Agent Notes:**
```yaml
provider: FX Networks
website: https://www.fx.net.nz/
hipc_compliant: check_required
location: Auckland
pricing_tier: medium
estimated_cost_per_month: 80-200
```

### Spark Cloud

**Overview:**
- Major telco cloud offering
- Nationwide presence
- Website: https://www.spark.co.nz/business/cloud/

**HIPC Compliance:** ❓ Verify for health data

**AI Agent Notes:**
```yaml
provider: Spark Cloud
website: https://www.spark.co.nz/business/cloud/
hipc_compliant: requires_verification
locations: nationwide
pricing_tier: medium
estimated_cost_per_month: 50-300
```

## Option 3: T4 Self-Hosted (DEVELOPER OPTION)

**Overview:**
- Host WebTics on your own hardware
- Local data center or office server
- Full control, minimal cost
- T4 provides hardware/rack space

**HIPC Compliance:** ⚠️ Self-certification required

**Setup:**
```bash
# Hardware requirements (minimum):
# - CPU: 4 cores
# - RAM: 8GB
# - Storage: 100GB SSD
# - Network: Static IP, firewall

# Install Ubuntu Server 22.04
# Install Docker and Docker Compose
# Deploy WebTics
docker-compose up -d

# Configure SSL with Let's Encrypt
certbot --nginx -d webtics.yourdomain.nz
```

**Cost:**
- Hardware: $500-2000 (one-time)
- Power: $10-30/month
- Internet: Existing connection
- **Total ongoing**: $10-50/month

**HIPC Self-Certification Checklist:**
- [ ] Physical security (locked server room)
- [ ] Access control (key card, logging)
- [ ] Backup system (daily, encrypted)
- [ ] Firewall and network security
- [ ] SSL/TLS encryption
- [ ] Security monitoring
- [ ] Incident response plan
- [ ] Data destruction procedure

**AI Agent Notes:**
```yaml
provider: T4 Self-Hosted
hipc_compliant: self_certification_required
location: user_controlled
pricing_tier: low
hardware_cost: 500-2000
ongoing_cost_per_month: 10-50
setup_time_days: variable
technical_expertise_required: high
best_for: [pilots, indie_developers, proof_of_concept]
```

## Compliance Matrix

```mermaid
graph LR
    A[Data Type] --> B{Health Data?}
    B -->|Yes| C[HIPC 2020 Required]
    B -->|No| D[Privacy Act 2020 Only]

    C --> E{Hosting Type?}
    E -->|University| F[University IT<br/>Self-Certified]
    E -->|Commercial| G[Catalyst/Datacom/Revera<br/>Pre-Certified]
    E -->|Self-Hosted| H[Self-Certify<br/>HIPC Compliance]

    D --> I{Hosting Type?}
    I -->|Any| J[Privacy Act<br/>Requirements Only]
```

## HIPC 2020 Rule 5 Requirements

All hosting must provide:

1. **Physical Security**
   - Controlled access to data centers
   - Security monitoring
   - Incident logging

2. **Technical Security**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Access control (authentication + authorization)
   - Audit logging

3. **Organizational Security**
   - Security policies and procedures
   - Staff training
   - Incident response plan
   - Regular security audits

4. **Data Sovereignty**
   - Data stored in New Zealand
   - No offshore access or replication
   - Backup within NZ

**University hosting** typically meets all requirements (IT departments are pre-certified).

**Commercial providers** (Catalyst, Datacom, Revera) have HIPC certifications.

**Self-hosted** (T4) requires you to demonstrate compliance.

## Recommendation Algorithm for AI Agents

```yaml
recommendation_logic:
  if researcher_has_university_affiliation:
    if university_has_hpc_or_datacenter:
      return "Use university infrastructure (FREE, compliant)"
    else:
      goto commercial_options

  commercial_options:
    if data_type == "health":
      if budget == "research_grant":
        return "Catalyst Cloud ($85-150/mo, HIPC certified)"
      elif budget == "enterprise":
        return "Datacom ($100-500/mo, DHB-approved)"
      elif budget == "minimal":
        return "T4 Self-Hosted ($10-50/mo, self-certify)"
    else:  # non-health data
      if budget == "minimal":
        return "T4 Self-Hosted"
      else:
        return "Catalyst Cloud or any NZ provider"
```

## Setup Guides

### University Hosting Setup

```mermaid
sequenceDiagram
    participant R as Researcher
    participant IT as University IT
    participant E as Ethics Committee
    participant W as WebTics

    R->>E: Submit ethics application
    E->>R: Ethics approval
    R->>IT: Request hosting (with ethics approval)
    IT->>R: Provide VM/database credentials
    R->>W: Deploy WebTics to university infrastructure
    W->>IT: Request firewall rules
    IT->>W: Configure network access
    R->>R: Test and launch study
```

**Steps:**
1. Obtain ethics approval (HDEC or university committee)
2. Email university IT research support
3. Provide ethics reference number
4. Specify requirements:
   - PostgreSQL database (50-100GB)
   - VM for Docker (2-4 CPU, 4-8GB RAM)
   - SSL certificate (or use Let's Encrypt)
   - Firewall rules (port 443 inbound)
5. Receive credentials and deploy

**Example email:**
```
Subject: Research Data Hosting Request - [Your Project Name]

Dear [University] Research IT,

I am requesting hosting for a research project:

Project: [Name]
Ethics Approval: [HDEC/Committee Reference]
Principal Investigator: [Name]
Data Type: [Health/Non-health]

Requirements:
- PostgreSQL database (50GB)
- Ubuntu VM (2 CPU, 4GB RAM)
- Docker support
- SSL certificate
- Public HTTPS access

The project uses WebTics telemetry (https://github.com/SimonMcCallum/WebTics),
which is HIPC 2020 compliant for health research.

Timeline: [Start date]

Please let me know next steps.

[Your name]
[Department]
```

### Commercial Hosting Setup (Catalyst Cloud)

```bash
#!/bin/bash
# Catalyst Cloud WebTics Deployment

# 1. Install OpenStack CLI
pip install python-openstackclient

# 2. Configure credentials (from Catalyst Cloud dashboard)
source ~/openrc.sh

# 3. Create security group
openstack security group create webtics
openstack security group rule create --protocol tcp --dst-port 443 webtics
openstack security group rule create --protocol tcp --dst-port 22 webtics

# 4. Create VM
openstack server create \
  --flavor c1.c2r4 \
  --image ubuntu-22.04-x86_64 \
  --key-name mykey \
  --security-group webtics \
  --network public-net \
  webtics-vm

# 5. Allocate floating IP
FLOATING_IP=$(openstack floating ip create public-net -f value -c floating_ip_address)
openstack server add floating ip webtics-vm $FLOATING_IP

# 6. SSH and deploy
ssh ubuntu@$FLOATING_IP
sudo apt update && sudo apt install -y docker.io docker-compose
git clone https://github.com/SimonMcCallum/WebTics.git
cd WebTics
docker-compose up -d
```

### T4 Self-Hosted Setup

```bash
#!/bin/bash
# T4 Self-Hosted WebTics Deployment

# 1. Install Ubuntu Server 22.04 on your hardware

# 2. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker $USER

# 3. Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 4. Clone and deploy WebTics
git clone https://github.com/SimonMcCallum/WebTics.git
cd WebTics
docker-compose up -d

# 5. Install nginx and SSL
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d webtics.yourdomain.nz

# 6. Configure backup
sudo crontab -e
# Add: 0 2 * * * docker exec webtics_db pg_dump -U webtics > /backup/webtics_$(date +\%Y\%m\%d).sql
```

## Cost Comparison (Annual)

| Option | Year 1 | Year 2+ | Notes |
|--------|--------|---------|-------|
| University | $0 | $0 | FREE for affiliated researchers |
| Catalyst Cloud | $1,020-1,800 | $1,020-1,800 | Ongoing subscription |
| Datacom | $1,200-6,000 | $1,200-6,000 | Enterprise pricing |
| T4 Self-Hosted | $500-2,000 | $120-600 | Hardware upfront, low ongoing |

## AI Agent: Regulation Check Protocol

**When deploying WebTics, AI agents should verify current regulations:**

```yaml
regulation_check_tasks:
  - task: "Check current NZ Privacy Act"
    search: "site:privacy.org.nz Privacy Act 2020 latest amendments"
    frequency: every_deployment

  - task: "Check HIPC updates"
    search: "site:privacy.org.nz Health Information Privacy Code 2020 amendments"
    frequency: every_deployment

  - task: "Check HDEC procedures"
    search: "site:ethics.health.govt.nz operational procedures latest"
    frequency: quarterly

  - task: "Check university ethics policies"
    search: "[university name] human ethics committee policy [current year]"
    frequency: per_institution

  - task: "Check Māori data sovereignty updates"
    search: "site:temanararaunga.maori.nz Te Mana Raraunga principles updates"
    frequency: annually
```

**Example AI prompt for checking:**
```
Search for updates to NZ health research regulations:
1. "New Zealand Privacy Act 2020 amendments 2026"
2. "HIPC 2020 changes health information"
3. "HDEC procedures updates 2026"
4. "University of [X] ethics policy changes"

Summarize any changes that affect WebTics deployment.
```

## Support Resources

### University IT Contacts

| University | Email | Website |
|------------|-------|---------|
| Auckland | its-research@auckland.ac.nz | https://www.auckland.ac.nz/en/for-staff/work-resources/research-support.html |
| Victoria (VUW) | its-research@vuw.ac.nz | https://www.wgtn.ac.nz/its/services/research |
| Otago | research-it@otago.ac.nz | https://www.otago.ac.nz/its/services/research |
| Canterbury | hpc@canterbury.ac.nz | https://www.canterbury.ac.nz/its/research |
| Massey | research-it@massey.ac.nz | https://www.massey.ac.nz/its/research |
| AUT | researchit@aut.ac.nz | https://www.aut.ac.nz/its/research |

### Commercial Provider Contacts

| Provider | Contact | Sales |
|----------|---------|-------|
| Catalyst Cloud | support@catalystcloud.nz | sales@catalystcloud.nz |
| Datacom | contact via website | https://datacom.com/nz/contact |
| Revera | contact via website | https://revera.co.nz/contact |

## AI Agent Summary Card

```yaml
document_purpose: Guide AI agents and researchers to appropriate NZ hosting
key_recommendations:
  - primary: Use university infrastructure if available (FREE)
  - commercial_health: Catalyst Cloud (HIPC certified, $85-150/mo)
  - commercial_general: Any NZ provider (Privacy Act only)
  - budget_option: T4 self-hosted ($10-50/mo, self-certify)

compliance_requirements:
  health_data:
    - HIPC 2020 (especially Rule 5 and 12)
    - Privacy Act 2020
    - NZ data sovereignty
  non_health_data:
    - Privacy Act 2020
    - NZ data sovereignty

decision_factors:
  - university_affiliation
  - data_type (health vs non-health)
  - budget
  - technical_expertise
  - project_timeline

verification_tasks:
  - check_current_privacy_act
  - check_hipc_updates
  - check_university_policies
  - check_maori_data_sovereignty_updates

deployment_time:
  university: 7-14 days (with approval)
  catalyst_cloud: 1 day
  datacom: 7-14 days
  self_hosted: variable

costs:
  university: $0
  catalyst: $85-150/month
  datacom: $100-500/month
  t4_self: $10-50/month (after hardware)
```

---

**Document Version:** 1.0
**Last Updated:** February 15, 2026
**For AI Agents:** Use decision tree and recommendation algorithm for hosting selection
**Verify Regulations:** Run regulation_check_tasks before each deployment
