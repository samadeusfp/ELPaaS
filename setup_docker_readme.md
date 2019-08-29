# Installation Docker

## Required software

Install [Docker](https://docs.docker.com/install/) according to the operating system you are using..

## Preparation

What to do, before server can be run the first time:

* Adjust configuration parameters in `docker-compose.yml` to set-up the following: 
	* Configure the port on which ELPaaS is exposed. In the following configuration, the ELPaaS would be available at: (http://localhost:8282/):
	  ```
	    ports:
     	- "8282:8000"   
	  ```
	* Enable the Sending of e-Mails:
		In ElPaas/settings.py scroll down to the bottom and exchange the data in the
		following fields with the smtp settings of your desired mail hoster that
		should be used:
		* EMAIL_HOST
		* EMAIL_PORT
		* EMAIL_HOST_USER		
		* EMAIL_HOST_PASSWORD
		* EMAIL_SENDER
* Build the Docker image:
```
docker-compose build
```
Note that this requires an active internet connection and may take a long time to download the necessary dependencies.

## Start

How to run the server:

```
docker-compose up -d
```