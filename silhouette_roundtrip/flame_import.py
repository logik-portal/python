"""
Send rendered Silhouette sequences to Flame through Logik Backdoor.

Run as a separate process by silhouette_setup.py's post_render hook, so the
import never depends on Silhouette's Python threads getting time to run:

    python3 flame_import.py --reel Elements --result /tmp/x.json PATTERN [PATTERN ...]

Writes progress to /tmp/silhouette_roundtrip.log and a JSON summary to --result.
Exit code 0 when every sequence imported, 1 otherwise.

Flame also imports every .py file in its python folders, so this file does
nothing unless run as a script.
"""

import argparse
import json
import os
import socket
import sys
import time

LOGIK_BACKDOOR_PATH = '/opt/Autodesk/shared/python/logik_backdoor'
SETUP_LOG = '/tmp/silhouette_roundtrip.log'
BACKDOOR_TIMEOUT = 600


def _log(msg):
    line = '==silhouette_roundtrip[flame_import]: %s' % msg
    print(line)
    try:
        with open(SETUP_LOG, 'a') as fh:
            fh.write(line + '\n')
    except Exception:
        pass


def _write_result(path, ok, failures):
    if not path:
        return
    try:
        with open(path, 'w') as fh:
            json.dump({'ok': ok, 'failures': failures}, fh)
    except Exception as exc:
        _log('Could not write result file %s: %s' % (path, exc))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--reel', default='Elements')
    parser.add_argument('--result', default='')
    parser.add_argument('patterns', nargs='+')
    args = parser.parse_args(argv)

    _log('Started (pid %s, Python %s)' % (os.getpid(), sys.version.split()[0]))

    if LOGIK_BACKDOOR_PATH not in sys.path:
        sys.path.insert(0, LOGIK_BACKDOOR_PATH)
    try:
        import logik_backdoor_client as backdoor
    except Exception as exc:
        message = 'Logik Backdoor client not found at %s (%s)' % (LOGIK_BACKDOOR_PATH, exc)
        _log(message)
        _write_result(args.result, False, [message])
        return 1

    if not backdoor.available():
        try:
            home = backdoor._home()
            listing = sorted(os.listdir(os.path.join(str(home), 'sessions')))
        except Exception as exc:
            home, listing = '?', 'unreadable (%s)' % exc
        _log('Logik Backdoor: no live Flame session. host=%s config=%s sessions=%s' % (
            socket.gethostname(), home, listing))
        message = 'Flame is not running (or Logik Backdoor is not loaded).'
        _write_result(args.result, False, [message])
        return 1

    failures = []
    for pattern in args.patterns:
        _log('Sending to Flame: %s -> reel %r' % (pattern, args.reel))
        start = time.time()
        result = backdoor.call(
            'import_image_to_batch',
            timeout=BACKDOOR_TIMEOUT,
            path=pattern,
            reel_name=args.reel,
        )
        if result.get('ok'):
            _log('import_image_to_batch ok in %.1fs: %s' % (time.time() - start, result.get('clips')))
        else:
            _log('import_image_to_batch failed: %s' % result.get('error'))
            failures.append('%s: %s' % (os.path.basename(pattern), result.get('error')))

    _write_result(args.result, not failures, failures)
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
