#!/usr/bin/env python

import lib_pipeline_ms
import sys

lib_pipeline_ms.merge_parmdb(sys.argv[1],sys.argv[2], sys.argv[3], clobber=True)