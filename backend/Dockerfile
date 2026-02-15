# Backend Dockerfile - Flask API Service
FROM centos:7

# Enable proxy for inbound traffic (if needed)
ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}

# Update repository URLs for CentOS 7 (using vault since CentOS 7 is EOL)
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo

# Install basic tools and libraries
RUN yum -y update && yum install -y \
    gcc \
    gcc-c++ \
    make \
    git \
    curl \
    wget \
    python3 \
    openssl-devel \
    libffi-devel \
    postgresql-devel \
    unzip \
    zip \
    redhat-lsb-core \
    && yum clean all

# Install Python 3 and pip
RUN yum -y install python3-pip

# Create application directory
WORKDIR /opt/license_tracker

# Copy and install Python dependencies
COPY requirements.txt ./
RUN python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip && \
    python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt && \
    python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir gunicorn flask-cors

# Copy application code (excluding UI since frontend is separate)
COPY license_tracker/__init__.py ./license_tracker/
COPY license_tracker/app.py ./license_tracker/
COPY license_tracker/logger.py ./license_tracker/
COPY license_tracker/license_tracker.py ./license_tracker/
COPY license_tracker/api ./license_tracker/api/
COPY license_tracker/extensions ./license_tracker/extensions/
COPY license_tracker/models ./license_tracker/models/
COPY license_tracker/utils ./license_tracker/utils/
COPY config ./config/
COPY utils ./utils/
COPY deploy_gunicorn.py ./
COPY setup.py ./
COPY setup.cfg ./

# Create instance directory
RUN mkdir -p instance

# Copy production config
COPY config/production.py instance/config.py

# Set executable permissions for utility binaries
RUN chmod +x utils/almutil utils/lmutil utils/rlmutil

# Clear proxy after installation
ENV http_proxy=
ENV https_proxy=

# Expose API port
EXPOSE 2324

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:2324/api/health || exit 1

# Start the application
CMD ["python3", "deploy_gunicorn.py"]
