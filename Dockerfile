FROM ubuntu
COPY helm /usr/bin/
COPY kubectl /usr/bin/ 
COPY run-diagnosis run-diagnosis
ENV TZ=Asia/Calcutta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get install -y curl vim python3 python3-pip git libffi-dev libssl-dev supervisor openssh-server sshpass openjdk-11-jre-headless wget apt-transport-https software-properties-common
RUN wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN apt-get install -y powershell
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN yes | pip3 install --upgrade pip setuptools
RUN yes | pip3 install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
WORKDIR /app
COPY inventory.vmware.yml /app/inventory.vmware.yml
RUN pwsh -Command Install-Module VMware.PowerCLI -Scope AllUSers -Force

