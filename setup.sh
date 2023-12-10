#!/bin/bash
docker image build ./jobdash -t jobdash:latest
docker image build ./pe_etl_ml -t pe_etl_ml:latest