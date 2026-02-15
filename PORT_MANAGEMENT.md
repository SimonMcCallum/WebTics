# Port Management for WebTics Development

**IMPORTANT: For Claude and Future Developers**

To avoid port conflicts on this development machine, all services must use designated ports from the available pool below.

## Current Port Assignments

### WebTics Services
- **Backend API**: `8013` (FastAPI)
- **PostgreSQL**: `5432` (internal Docker only, not exposed)
- **Dashboard**: Served via file:// or nginx (no dedicated port)
- **Nginx (optional)**: `80`, `443` (if used for local proxy)

## Reserved Ports on This Machine

Based on common services running on Simon's machine, the following ports are **RESERVED** and should NOT be used:

### System Services
- `80` - HTTP (nginx, IIS)
- `443` - HTTPS (nginx, IIS)
- `3306` - MySQL
- `5432` - PostgreSQL
- `6379` - Redis
- `27017` - MongoDB

### Development Services (Likely in Use)
- `3000` - React development server
- `4200` - Angular development server
- `5000` - Flask default
- `5173` - Vite development server
- `8000` - Common FastAPI/Django default
- `8080` - Alternative HTTP, often used by Java/Spring
- `8888` - Jupyter Notebook
- `9000` - Various development tools

### Docker/Container Services
- `2375`, `2376` - Docker daemon
- `8006` - Portainer (if installed)

## Available Port Ranges for New Projects

When creating a new test service or Claude instance needs a port, choose from these ranges:

### Recommended Testing Ports (8001-8999)
- `8013` - **WebTics (CURRENT)**
- `8100-8199` - Available for Claude projects
- `8200-8299` - Available for Claude projects
- `8300-8399` - Available for Claude projects
- `8400-8499` - Available for Claude projects
- `8500-8599` - Available for Claude projects

### Alternative Ranges
- `9001-9099` - Available
- `9100-9199` - Available
- `10000-10099` - Available

## Port Selection Protocol for Claude

**When Claude needs to select a port for a new service:**

1. **Check Currently Used Ports First**:
   ```bash
   # On Windows
   netstat -ano | findstr LISTENING

   # On Linux/Mac
   lsof -i -P -n | grep LISTEN
   ```

2. **Choose from Available Ranges**:
   - Start with `8100` and increment upward
   - Skip any ports shown as "in use" from step 1
   - Document the choice in project documentation

3. **Update This Document**:
   - Add the new port assignment to "Current Port Assignments"
   - Commit the change so future instances see it

4. **Use Consistent Ports in Project**:
   - `docker-compose.yml`
   - `README.md`
   - Configuration files
   - SDK examples

## Checking for Port Conflicts

### Before Starting a Service

```bash
# Windows PowerShell
Test-NetConnection -ComputerName localhost -Port 8013

# Windows CMD
netstat -ano | findstr :8013

# Linux/Mac
lsof -i:8013

# Or use nc (netcat)
nc -zv localhost 8013
```

### Docker Compose Port Mapping

In `docker-compose.yml`, use:

```yaml
services:
  backend:
    ports:
      - "8013:8000"  # host:container
```

This maps:
- **Host port** `8013` (external access) ← **UNIQUE, avoid conflicts**
- **Container port** `8000` (internal) ← Can be standard across projects

## Port Change Checklist

If you need to change WebTics port from `8013` to another port:

- [ ] Update `docker-compose.yml` ports section
- [ ] Update `backend/app/main.py` (if it references the port)
- [ ] Update `README.md` examples
- [ ] Update `TESTING.md` curl examples
- [ ] Update `dashboard/index.html` default backend URL
- [ ] Update `sdk/godot/addons/webtics/WebTics.gd` default URL
- [ ] Update `sdk/unreal/WebTics/Source/WebTics/Private/WebTicsSubsystem.cpp` default URL
- [ ] Update all documentation in `docs/`
- [ ] Update `nginx/webtics.conf` upstream configuration
- [ ] Commit all changes with clear message: "Change port from X to Y"

## Examples of Good Port Selection

### Scenario 1: New FastAPI Service
```
✅ Good: Use 8100 (from available range)
❌ Bad: Use 8000 (likely taken by another FastAPI)
```

### Scenario 2: Multiple Test Environments
```
✅ Good:
  - Dev: 8013
  - Staging: 8014
  - QA: 8015

❌ Bad:
  - All use 8013 (port conflict when running parallel)
```

### Scenario 3: Microservices Architecture
```
✅ Good:
  - API Gateway: 8100
  - Auth Service: 8101
  - Data Service: 8102
  - Metrics Service: 8103

❌ Bad:
  - All use 8000 (can't run together)
```

## Common Port Conflict Errors

### Error: "Address already in use"

```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution:**
1. Find what's using the port: `netstat -ano | findstr :8000`
2. Choose a different port from available ranges
3. Update all configurations

### Error: "Port is not available"

```
docker: Error response from daemon: Ports are not available: exposing port
TCP 0.0.0.0:8000 -> 0.0.0.0:0: listen tcp 0.0.0.0:8000: bind: An attempt was
made to access a socket in a way forbidden by its access permissions.
```

**Solution:**
- Windows reserves certain ports dynamically
- Check reserved ranges: `netsh interface ipv4 show excludedportrange protocol=tcp`
- Choose port outside reserved ranges (usually 8100+ is safe)

## Port Assignment Log

Track port assignments here for future reference:

| Port | Service | Project | Date Assigned | Notes |
|------|---------|---------|---------------|-------|
| 8013 | WebTics Backend | WebTics | 2026-02-15 | Main telemetry API |
| 8014 | (Available) | - | - | - |
| 8015 | (Available) | - | - | - |
| 8100 | (Available) | - | - | - |

## For CI/CD and Production

**Production ports (80, 443) should ONLY be used via nginx reverse proxy.**

Never expose service ports directly in production:

```yaml
# ❌ BAD (exposes 8013 publicly)
services:
  backend:
    ports:
      - "8013:8000"

# ✅ GOOD (internal only, nginx proxy)
services:
  backend:
    expose:
      - "8000"
  nginx:
    ports:
      - "80:80"
      - "443:443"
```

## Resources

- [IANA Service Name and Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)
- [Well-known ports (0-1023)](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Well-known_ports)
- [Registered ports (1024-49151)](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Registered_ports)
- [Dynamic ports (49152-65535)](https://en.wikipedia.org/wiki/Ephemeral_port)

---

**Last Updated**: 2026-02-15
**WebTics Port**: 8013
**Machine**: Simon's Development Machine
