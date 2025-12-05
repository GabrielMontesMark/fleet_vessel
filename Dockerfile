FROM odoo:19.0

# Switch to root to install dependencies
USER root

# Install additional Python packages if needed
# RUN pip3 install --no-cache-dir <package-name>

# Create directory for custom addons
RUN mkdir -p /mnt/extra-addons

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# The addons will be mounted as volumes from docker-compose
