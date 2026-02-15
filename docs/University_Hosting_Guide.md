# University Hosting Guide for WebTics

Quick guide for university researchers requesting hosting for WebTics.

## What Service Do I Need?

**WebTics requires: RESEARCH DATA HOSTING / DIGITAL SOLUTIONS**

**NOT: HPC (High Performance Computing)**

## The Difference

### Research Data Hosting / Digital Solutions ✅

**What it is:**
- Web server and database hosting
- VM/container hosting for applications
- Research file storage
- SSL certificates and network access
- Usually called: "Research IT", "Digital Solutions", "Research Data Hosting"

**What WebTics needs:**
- PostgreSQL database (50-500GB)
- Ubuntu VM for Docker (2-4 CPU, 4-8GB RAM)
- Public HTTPS access (port 443)
- SSL certificate
- Daily backups

**Cost:** FREE for university researchers

**Who provides it:** University IT Services - Research Support

### HPC (High Performance Computing) ❌

**What it is:**
- Supercomputer clusters for heavy computation
- For ML training, simulations, large-scale data analysis
- Hundreds to thousands of CPU cores
- Requires computational justification
- Usually called: "HPC cluster", "NeSI", "RAAPOI", "Research Computing"

**What it's used for:**
- Analyzing telemetry data AFTER collection (separate from WebTics)
- Machine learning model training
- Statistical analysis at scale
- Genomic analysis, climate modeling, etc.

**NOT needed for:** Hosting WebTics

## University-Specific Requests

### University of Auckland

**Contact:** Use [AskAuckland](https://www.auckland.ac.nz/en/research/about-our-research/research-support-contacts.html) or contact form

**Alternative:** General IT support: university@auckland.ac.nz

**Subject:** Research Web Hosting Request

**Message:**
```
Dear Research Support,

I am requesting research web hosting for a telemetry database system (WebTics).

Project: [Your study name]
Ethics Approval: [HDEC or UAHPEC reference]
Principal Investigator: [Name]

Requirements:
- PostgreSQL database (100GB)
- Ubuntu VM for Docker containers (4 CPU, 8GB RAM)
- Public HTTPS access
- SSL certificate
- Daily backups

This is for hosting a research web application, not HPC computation.

Timeline: [Start date]

Documentation: https://github.com/SimonMcCallum/WebTics

Thank you,
[Your name]
```

### Victoria University of Wellington

**Contact:** [Digital Solutions Service Desk](https://www.wgtn.ac.nz/digital-solutions/contact-us) or phone 463 5050

**Website:** https://www.wgtn.ac.nz/its/staff-services/research-services

**Subject:** Research Data Hosting Request

**Message:**
```
Dear Digital Solutions / Research Services,

I need research data hosting (web server + database) for my study.

Project: [Your study name]
Ethics Approval: [VUW HEC or HDEC reference]
PI: [Name]

Requirements:
- PostgreSQL database (100GB)
- VM for Docker web application (4 CPU, 8GB RAM)
- HTTPS access with SSL
- Backup configuration

This is for web/database hosting, not the RAAPOI HPC cluster.

Documentation: https://github.com/SimonMcCallum/WebTics

Regards,
[Your name]
```

### University of Otago

**Email:** university@otago.ac.nz (General IT) or research@otago.ac.nz (Research Office)

**Phone:** 0800 80 80 98 or +64 3 479 7000

**Website:** https://www.otago.ac.nz/its/contacts

**Subject:** Health Research Data Hosting Request

**Message:**
```
Dear Research IT,

I require research data hosting for a health telemetry system.

Project: [Your study name]
Ethics: [Otago HEC or HDEC reference]
Data Type: Health research (HIPC 2020 applies)

Requirements:
- PostgreSQL database (health data)
- VM for Docker deployment
- HTTPS access
- SSL certificate
- Secure backup

This is database/web hosting, not HPC cluster access.

System: WebTics - https://github.com/SimonMcCallum/WebTics

Thank you,
[Your name]
```

### University of Canterbury

**Email:** eResearch@canterbury.ac.nz ✅ (Verified)

**Website:** https://www.canterbury.ac.nz/research/eresearch-at-canterbury

**Subject:** Research Web Hosting Request

**Message:**
```
Dear eResearch Team,

I need web hosting and database services for my research project.

Project: [Your study name]
Ethics: [UC HEC or HDEC]

Requirements:
- PostgreSQL database
- Ubuntu VM for Docker containers
- SSL and firewall configuration
- Backup system

This is for web application hosting, not HPC computation.

Thank you,
[Your name]
```

### Massey University

**Email:** contact@massey.ac.nz (General) or use [IT Services request form](https://www.massey.ac.nz/about/contact-us/it-services/)

**Phone:** 0800 MASSEY or +64 6 350 5701

**Website:** https://www.massey.ac.nz/research/masseys-research-community/researcher-support-and-development/

**Subject:** Research Data Hosting Request

**Message:**
```
Dear Research IT,

I am requesting digital solutions support for research data hosting.

Project: [Your study name]
Ethics: [Massey HEC or HDEC]

Requirements:
- PostgreSQL database hosting
- VM for web application (Docker)
- SSL certificate
- Network and backup configuration

This is for hosting a research database application.

Thanks,
[Your name]
```

### AUT

**Email:** research@aut.ac.nz (Research Office) or 0800 AUT ICT (0800 288 428)

**Website:** https://www.aut.ac.nz/research/aut-research-office or www.ithelp.aut.ac.nz

**Subject:** Research Web Hosting Request

**Message:**
```
Dear Research IT,

I require research web hosting for a database application.

Project: [Your study name]
Ethics: [AUTEC or HDEC]

Requirements:
- PostgreSQL database
- VM for Docker web app
- HTTPS access
- Backup configuration

This is for web/database hosting.

Regards,
[Your name]
```

## What Will Happen

1. **Initial Response** (1-3 days)
   - IT will acknowledge your request
   - May ask clarifying questions
   - Will verify ethics approval

2. **Setup** (1-2 weeks)
   - IT creates database and VM
   - Configures network access
   - Sets up backups
   - Provides credentials

3. **You Deploy** (1-2 days)
   - SSH to VM
   - Install Docker
   - Clone WebTics repo
   - Run `docker-compose up -d`
   - Configure SSL

4. **Go Live**
   - Test with your game
   - Verify data collection
   - Monitor logs

## Common Questions from IT

### Q: "What is WebTics?"
**A:** A self-hosted game telemetry system for research (NZ Privacy Act 2020 compliant). It's a lightweight web application with a PostgreSQL database. Documentation: https://github.com/SimonMcCallum/WebTics

### Q: "Why not use a commercial service?"
**A:** Research ethics requires full data ownership and NZ data sovereignty (especially for health data under HIPC 2020 Rule 12).

### Q: "How much compute do you need?"
**A:** Minimal - WebTics is lightweight:
- 2-4 CPU cores
- 4-8GB RAM
- 100-500GB storage
- Standard web server load

### Q: "How many users?"
**A:** Typically 10-100 research participants, not thousands. Low traffic.

### Q: "Do you need HPC?"
**A:** No, this is web hosting, not HPC. (If analyzing data later with ML, I might request HPC separately.)

### Q: "What about backups?"
**A:** Yes, daily PostgreSQL backups required. Retention: [duration of study + 5 years typically].

### Q: "Security requirements?"
**A:**
- HTTPS/SSL (TLS 1.3)
- Firewall (only port 443 inbound)
- Access control (SSH key only)
- Regular updates (Docker containers make this easy)

### Q: "HIPC compliance?" (if health data)
**A:** Yes, WebTics is designed for HIPC 2020 compliance:
- Data sovereignty (NZ hosting)
- Encryption at rest and in transit
- Access controls
- Audit logging
- Participant withdrawal system

## After Setup

### Access Your Server

```bash
# SSH to your VM (IT will provide details)
ssh your-username@webtics.university.ac.nz

# Check Docker is installed
docker --version
docker-compose --version

# Clone WebTics
git clone https://github.com/SimonMcCallum/WebTics.git
cd WebTics

# Configure (update port if needed)
nano docker-compose.yml

# Start WebTics
docker-compose up -d

# Check it's running
curl http://localhost:8013/

# View logs
docker-compose logs -f
```

### Configure SSL

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (IT may provide this)
sudo certbot --nginx -d webtics.university.ac.nz

# Or use university SSL certificate if provided
```

### Test Your Deployment

```bash
# Check API is accessible
curl https://webtics.university.ac.nz/

# Test database connection
docker-compose exec db psql -U webtics -d webtics

# Create test session
curl -X POST https://webtics.university.ac.nz/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "test_001", "build_number": "1.0"}'
```

## Troubleshooting

### "IT says I need HPC"
**Clarify:** "I need web hosting (database + web server), not HPC cluster. WebTics is a lightweight research application, not a computational workload."

### "IT says use commercial cloud"
**Explain:** "My ethics approval requires NZ data sovereignty and institutional hosting for health data (HIPC Rule 12). Commercial hosting adds cost and compliance complexity."

### "IT doesn't have database hosting"
**Ask:** "Can you provide a VM where I can run Docker containers with PostgreSQL? I can self-manage the database via Docker."

### "IT wants to know computational requirements"
**Clarify:** "This isn't HPC - it's a web application:
- 2-4 CPU cores (standard web server)
- 4-8GB RAM (database + API)
- No GPU needed
- No parallel computing
- Low traffic (10-100 users max)"

## When You WOULD Use HPC

**After collecting data with WebTics**, you might use HPC for:

1. **Machine Learning Analysis**
   - Train models on telemetry data
   - Requires GPU/many CPUs
   - Separate HPC request

2. **Statistical Analysis at Scale**
   - Large dataset analysis
   - Complex statistical models
   - Separate HPC request

**Workflow:**
1. WebTics collects data (on Research IT)
2. Export data from WebTics
3. Upload to HPC cluster
4. Run analysis on HPC
5. Download results

**Two separate systems, two separate requests.**

## Summary

✅ **DO:** Request "Research IT" or "Digital Solutions" for web hosting
✅ **DO:** Specify: PostgreSQL database + Docker VM
✅ **DO:** Mention: HIPC compliance if health data
✅ **DO:** Provide: Ethics approval reference

❌ **DON'T:** Request HPC cluster access
❌ **DON'T:** Say "high performance computing"
❌ **DON'T:** Apply for NeSI (that's for computation)
❌ **DON'T:** Overestimate compute needs (WebTics is lightweight)

---

**Questions?**
- WebTics: simon.mccallum@gmail.com
- Your University IT: See contact emails above

**Documentation:**
- This guide: docs/University_Hosting_Guide.md
- Full hosting options: docs/NZ_Hosting_Options.md
- Ethics guide: docs/NZ_Ethics_Approval_Guide.md
