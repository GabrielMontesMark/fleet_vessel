# Odoo Fleet with Vessels - Docker Environment

This directory contains a complete Docker environment to run Odoo with the Fleet and Fleet Vessels modules.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)
- At least 2GB of free RAM
- Ports 8069 available on your machine

## Quick Start

### 1. Start the Environment

```bash
docker-compose up -d
```

This will:
- Pull the official Odoo 19 image
- Start a PostgreSQL 15 database
- Create and initialize the Odoo database
- Install the `fleet` and `fleet_vessels` modules automatically

### 2. Wait for Initialization

The first startup takes a few minutes. Monitor the logs:

```bash
docker-compose logs -f odoo
```

Wait until you see:
```
odoo_app | INFO odoo odoo: Odoo version 19.0
odoo_app | INFO odoo odoo: database: odoo@db:5432
```

### 3. Access Odoo

Open your browser and go to:
```
http://localhost:8069
```

**Default credentials:**
- Email: `admin`
- Password: `admin`

### 4. Verify Modules

1. Go to **Apps** menu
2. Remove the "Apps" filter
3. Search for "Fleet Vessels"
4. You should see both modules installed:
   - ✅ Fleet
   - ✅ Fleet Vessels

### 5. Test Vessel Functionality

1. Go to **Fleet** → **Configuration** → **Models**
2. Click **Create**
3. In the **Vehicle Type** field, select **Vessel**
4. You should see the **Vessel Information** tab appear
5. Fill in vessel details and save

## Docker Commands

### Start the environment
```bash
docker-compose up -d
```

### Stop the environment
```bash
docker-compose down
```

### Stop and remove all data (fresh start)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Only Odoo
docker-compose logs -f odoo

# Only PostgreSQL
docker-compose logs -f db
```

### Restart Odoo (after code changes)
```bash
docker-compose restart odoo
```

### Access Odoo shell
```bash
docker-compose exec odoo odoo shell -d odoo
```

### Access PostgreSQL
```bash
docker-compose exec db psql -U odoo -d odoo
```

## Updating Modules

If you make changes to the module code:

### Update without losing data
```bash
docker-compose exec odoo odoo -d odoo -u fleet_vessels --stop-after-init
docker-compose restart odoo
```

### Reinstall modules (will lose module data)
```bash
docker-compose down
docker-compose up -d
```

## Directory Structure

```
odoo_fleet/
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Custom Odoo image
├── config/
│   └── odoo.conf              # Odoo configuration file
├── fleet/                     # Original Fleet module
│   └── ...
└── fleet_vessels/             # Fleet Vessels extension
    └── ...
```

## Volumes

The setup creates two Docker volumes:

- `odoo-db-data`: PostgreSQL database data (persistent)
- `odoo-web-data`: Odoo filestore and sessions (persistent)

To remove all data and start fresh:
```bash
docker-compose down -v
```

## Ports

- **8069**: Odoo web interface (HTTP)

## Environment Variables

You can customize the environment by editing `docker-compose.yml`:

- `POSTGRES_USER`: Database username (default: odoo)
- `POSTGRES_PASSWORD`: Database password (default: odoo)
- `POSTGRES_DB`: Database name (default: postgres)

## Troubleshooting

### Port 8069 already in use
```bash
# Find what's using the port
sudo lsof -i :8069

# Change the port in docker-compose.yml
ports:
  - "8070:8069"  # Use port 8070 instead
```

### Database connection errors
```bash
# Check if database is healthy
docker-compose ps

# Restart database
docker-compose restart db
```

### Module not appearing
```bash
# Update module list
docker-compose exec odoo odoo -d odoo --update=all --stop-after-init
docker-compose restart odoo
```

### Permission errors
```bash
# Fix permissions
sudo chown -R $USER:$USER fleet fleet_vessels config
```

## Demo Data

The `fleet_vessels` module includes demo data with:
- 3 vessel brands (Azimut Yachts, Maersk, Sunseeker)
- 3 vessel models
- 3 vessel instances with complete information

To load demo data, the module is installed with demo data enabled by default.

## Production Considerations

This setup is for **development and testing only**. For production:

1. Change default passwords
2. Use proper SSL/TLS certificates
3. Configure proper backup strategy
4. Use environment variables for secrets
5. Set up proper logging and monitoring
6. Use a production-grade database setup

## Stopping the Environment

### Keep data
```bash
docker-compose down
```

### Remove all data
```bash
docker-compose down -v
```

## Support

For issues with:
- **Odoo**: Check [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- **Docker**: Check [Docker Documentation](https://docs.docker.com/)
- **Fleet Vessels Module**: See `fleet_vessels/README.md`

## License

- Odoo: LGPL-3
- Fleet module: LGPL-3
- Fleet Vessels module: LGPL-3
