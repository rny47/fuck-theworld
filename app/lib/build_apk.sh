#!/usr/bin/env bash

java -jar AndResGuard-cli-1.2.15.jar /Users/spark/Projects/Company/YulongApkClean/ApkCleaner/work_dir/recompile.apk \
  -config config.xml \
  -out outapk \
  -signatureType v2 \
  -signature release.keystore testres testres testres
