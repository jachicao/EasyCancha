#!/bin/sh
set -e

docker-compose exec django python ${@}

exit 0
