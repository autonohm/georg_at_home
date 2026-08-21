SHELL := /bin/bash
.ONESHELL:
.DEFAULT_GOAL := up

#skip_packages = drive examples
skip_packages = 


.PHONY: up
up: check_pkgs
	@ #don't echo command
	echo -e "\033[7;95;1m   bringup containers  \033[0m"
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    composefiles="$${composefiles} -f $${dir}docker-compose.yaml" # software/pkg_xxx/ -> software/pkg_xxx/docker-compose.yaml
	  fi
	done
	docker compose $${composefiles} up -d

.PHONY: up_wlog
up_wlog: check_pkgs
	@ #don't echo command
	echo -e "\033[7;95;1m   bringup containers (with log) \033[0m"
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    composefiles="$${composefiles} -f $${dir}docker-compose.yaml" # software/pkg_xxx/ -> software/pkg_xxx/docker-compose.yaml
	  fi
	done
	docker compose $${composefiles} up



.PHONY: down
down: check_pkgs
	@ #don't echo command
	echo -e "\033[7;95;1m   bringdown containers  \033[0m"
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    composefiles="$${composefiles} -f $${dir}docker-compose.yaml" # software/pkg_xxx/ -> software/pkg_xxx/docker-compose.yaml
	  fi
	done
	docker compose $${composefiles} down


.PHONY: stop
stop: check_pkgs
	@ #don't echo command
	echo -e "\033[7;95;1m   stop containers  \033[0m"
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    composefiles="$${composefiles} -f $${dir}docker-compose.yaml" # software/pkg_xxx/ -> software/pkg_xxx/docker-compose.yaml
	  fi
	done
	docker compose $${composefiles} stop


.PHONY: build
build: check_pkgs build_base_image
	@ #don't echo command
	echo -e "\033[7;95;1m   build containers  \033[0m"
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    composefiles="$${composefiles} -f $${dir}docker-compose.yaml" # software/pkg_xxx/ -> software/pkg_xxx/docker-compose.yaml
	  fi
	done
	docker compose $${composefiles} build

.PHONY: build_base_image
build_base_image:
	@ #don't echo command

	echo -e "\033[7;95;1m   build georg-ros image   \033[0m"
	docker build -t georg-ros:humble software/docker_base_image/


.PHONY: check_pkgs
check_pkgs:
	@ #don't echo command
	for dir in software/pkg_*; do
	  pkg=$${dir%*/} # Remove the trailing "/" -> 'software/pkg_xxx'
	  pkg=$${pkg##*/} # Print everything after the final "/" -> 'pkg_xxx'
	  found_pkgs="$${found_pkgs}$${pkg:4} " # cut off first 4 chars "pkg_" -> 'xxx'
	done
	echo -e "\033[7;92;1m   found pkgs: $${found_pkgs}  \033[0m"
	for skip in ${skip_packages}; do
	  if [[ " $${found_pkgs} " == *" $${skip} "* ]]; then
	    echo -e "\033[7;93;1m   skipping pkg: $${skip}  \033[0m"
	  else
	    echo -e "\033[7;91;1m   invalid skipee: $${skip}  \033[0m "
	    exit 22
	  fi
	done
	# warnings:
	for dir in software/pkg_*/; do
	  if [[ "${skip_packages}" != *"$${dir:13:-1}"* ]]; then # if array doesn't contain x ; cut off first 13 and last 1 chars "software/pkg_xxx/" -> 'xxx'
	    if [ ! -f "$$dir/docker-compose.yaml" ]; then
	      echo -e "\033[7;91;1m   package $${dir:13:-1} missing docker-compose.yaml  \033[0m "
	      exit 66
	    fi
	    if [ ! -f "$$dir/README.md" ]; then
	      echo -e "\033[7;93;1m   package $${dir:13:-1} missing README.md  \033[0m "
	    fi
	  fi
	done

	sleep 0.5 # delay for dev to read message
