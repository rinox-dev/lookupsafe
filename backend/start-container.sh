#!/bin/sh
set -eu
npm run db:local
exec npm run dev
