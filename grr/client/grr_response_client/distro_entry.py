#!/usr/bin/env python
"""This file defines the entry points for the client."""
from __future__ import unicode_literals

# pylint: disable=g-import-not-at-top
# Argparse runs on import, and maintains static state.

from grr_response_core.lib import config_lib
from grr_response_core.lib import flags


def SetConfigOptions():
  """Sets the default value for the config flag."""
  flags.PARSER.set_defaults(config=config_lib.Resource().Filter(
      "install_data/etc/grr-server.yaml@grr-response-core"))


def ClientBuild():
  from grr_response_client import client_build
  SetConfigOptions()
  flags.StartMain(client_build.main)


def Client():
  from grr_response_client import client
  SetConfigOptions()
  flags.StartMain(client.main)


def FleetspeakClient():
  from grr_response_client import grr_fs_client
  SetConfigOptions()
  flags.StartMain(grr_fs_client.main)


def PoolClient():
  from grr_response_client import poolclient
  SetConfigOptions()
  flags.StartMain(poolclient.main)
