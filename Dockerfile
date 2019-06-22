FROM continuumio/anaconda3

# Now install R and littler, and create a link for littler in /usr/local/bin
# Also set a default CRAN repo, and make sure littler knows about it too
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		littler \
        r-cran-littler \
		r-base \
		r-base-dev \
		r-recommended \
		libxml2-dev \
        && echo 'options(repos = c(CRAN = "https://cloud.r-project.org/"), download.file.method = "libcurl")' >> /etc/R/Rprofile.site \
        && echo 'source("/etc/R/Rprofile.site")' >> /etc/littler.r \
	&& ln -s /usr/share/doc/littler/examples/install.r /usr/local/bin/install.r \
	&& ln -s /usr/share/doc/littler/examples/install2.r /usr/local/bin/install2.r \
	&& ln -s /usr/share/doc/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
	&& ln -s /usr/share/doc/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
	&& install.r docopt \
	&& rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
	&& rm -rf /var/lib/apt/lists/*

RUN install2.r bupaR readR dplyr tidyr tidyverse stringr xesreadR DiagrammeRsvg

###################
# MONO
###################

RUN apt-get update \
	&& apt-get install -y --no-install-recommends apt-transport-https dirmngr gnupg ca-certificates \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
    && echo "deb https://download.mono-project.com/repo/debian stable-stretch main" | tee /etc/apt/sources.list.d/mono-official-stable.list \
    && apt-get update

RUN  apt-get install -y --no-install-recommends mono-complete ca-certificates-mono

###################
# Python
###################

WORKDIR /opt/

COPY environment.yml /opt/
RUN conda env create -f /opt/environment.yml

ENV PATH /opt/conda/envs/env/bin:$PATH
RUN echo "source activate env" > ~/.bashrc

###################
# Deployment
###################

# Fix xesreadR TODO move up
RUN  apt-get install -y --no-install-recommends \
	libcurl3 \
	libssl-dev \
	libcurl4-gnutls-dev \
	libxml2-dev \
	libicu-dev \
	r-cran-xml2

RUN install2.r xesreadR

COPY . /opt/

EXPOSE 8000

RUN ["python", "manage.py", "makemigrations"]
RUN ["python", "manage.py", "migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]