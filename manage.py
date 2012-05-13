#!/usr/bin/env python
import os
import sys

if "USE_NEWRELIC" in os.environ and "celeryd" in sys.argv:
    import newrelic.agent

    newrelic.agent.initialize()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
