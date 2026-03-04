#!/usr/bin/env python3
import os
import sys
import runpy
from datetime import datetime

log_path = os.path.join(os.getcwd(), 'tmp')
os.makedirs(log_path, exist_ok=True)
log_file = os.path.join(log_path, f'register_send_{int(datetime.utcnow().timestamp())}.log')

# Run the existing test script but capture stdout/stderr to the log file
with open(log_file, 'w') as f:
    # Redirect stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = f
    sys.stderr = f
    try:
        runpy.run_path('scripts/run_register_test.py', run_name='__main__')
    except SystemExit as e:
        print('Script exited with', e)
    except Exception as e:
        import traceback
        print('Exception during run:', e)
        traceback.print_exc()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

print('Wrote log to', log_file)
