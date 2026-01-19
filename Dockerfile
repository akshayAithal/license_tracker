# Docker file to orchestrate how the license_trracker is deployed.
# start from base

#Using multi stage builds
FROM node:14 as node-builder
# Copy application c
ADD . /opt/license_tracker
WORKDIR /opt/license_tracker/license_tracker/ui

# Enable proxy for inbound traffic 
ENV http_proxy http://proxy.sig.umbrella.com:80
ENV https_proxy http://proxy.sig.umbrella.com:443

ENV NODE_OPTIONS --max_old_space_size=2000

RUN npm config set registry https://registry.npmjs.org/ 
RUN npm config set strict-ssl false
RUN npm config set proxy http://proxy.sig.umbrella.com:80 
RUN npm config set https-proxy http://proxy.sig.umbrella.com:443 
#&& npm install node-sass \
# && nvm install-latest-npm \
#RUN npm install postcss-rtlcss@legacy 
RUN npm install 
#RUN npm install postcss@latest
RUN npm rebuild node-sass
RUN npm run build



FROM centos:7

# Update the repository URLs
# Here, as an example, we're replacing the base, updates, and extras repositories
# with a specific mirror. You should choose a mirror that's geographically close to you
# for better speeds. The following is just an example.

# Enable proxy for inbound traffic 
ENV http_proxy http://proxy.sig.umbrella.com:80
ENV https_proxy http://proxy.sig.umbrella.com:443

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Base.repo && \
    sed -i 's|#baseurl=http://mirror.centos.org/centos/$releasever|baseurl=http://mirror.centos.org/centos/7|g' /etc/yum.repos.d/CentOS-Base.repo


# Install basic tools and libraries
RUN yum -y update && yum install -y \
    gcc \
    gcc-c++ \
    make \
    git \
    curl \
    wget \
    vim \
    nano \
    python3 \
    openssl-devel \
    libffi-devel \
    postgresql-devel \
    unzip \
    zip \
    && yum clean all


# Python 3 and pip for Python 3
RUN yum -y install python3 && yum -y install python3-pip


RUN yum -y install redhat-lsb-core


#RUN pip install /apps.license_tracker

# Change this to start your application

COPY requirements.txt /opt/license_tracker/requirements.txt
WORKDIR /opt/license_tracker
RUN bash -c "python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip"
RUN bash -c "python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt"
RUN bash -c "python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir gunicorn"


ADD . /opt/license_tracker

COPY --from=node-builder /opt/license_tracker/license_tracker/ui /opt/license_tracker/license_tracker/ui

#Not the right thing but still
WORKDIR /opt/license_tracker/instance
WORKDIR /opt/license_tracker

COPY config/production.py  /opt/license_tracker/instance/config.py

RUN chmod +x utils/almutil
RUN chmod +x utils/lmutil
RUN chmod +x utils/rlmutil

# Copy application code

ENV http_proxy= 
ENV https_proxy=  

# Expose port
EXPOSE 2324

# start app

CMD [ "python3", "deploy_gunicorn.py" ]
