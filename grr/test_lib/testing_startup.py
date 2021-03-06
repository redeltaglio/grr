#!/usr/bin/env python
"""Initialize for tests."""

import os

from grr_response_core import config
from grr_response_core.config import contexts
from grr_response_core.lib import config_lib
from grr_response_core.lib import flags
from grr_response_core.lib import registry
from grr_response_core.lib import stats
from grr_response_core.lib.util import compatibility
from grr_response_server import aff4
from grr_response_server import data_store
from grr_response_server import server_logging
from grr_response_server import threadpool
from grr_response_server.data_stores import fake_data_store
from grr.test_lib import blob_store_test_lib

# Make sure we do not reinitialize multiple times.
INIT_RAN = False

flags.DEFINE_string(
    "test_data_store", None, "The data store implementation to use for running "
    "the tests.")


def TestInit():
  """Only used in tests and will rerun all the hooks to create a clean state."""
  global INIT_RAN

  if stats.STATS is None:
    stats.STATS = stats.StatsCollector()
    threadpool.InitializeMetrics()

  # Tests use both the server template grr_server.yaml as a primary config file
  # (this file does not contain all required options, e.g. private keys), and
  # additional configuration in test_data/grr_test.yaml which contains typical
  # values for a complete installation.
  flags.FLAGS.config = config_lib.Resource().Filter(
      "install_data/etc/grr-server.yaml@grr-response-core")

  flags.FLAGS.secondary_configs.append(config_lib.Resource().Filter(
      "grr_response_test/test_data/grr_test.yaml@grr-response-test"))

  # This config contains non-public settings that should be applied during
  # tests.
  extra_test_config = config.CONFIG["Test.additional_test_config"]
  if os.path.exists(extra_test_config):
    flags.FLAGS.secondary_configs.append(extra_test_config)

  # Tests additionally add a test configuration file.
  config_lib.SetPlatformArchContext()
  config_lib.ParseConfigCommandLine()

  # We are running a test so let the config system know that.
  config.CONFIG.AddContext(contexts.TEST_CONTEXT,
                           "Context applied when we run tests.")

  test_ds = flags.FLAGS.test_data_store
  if test_ds is None:
    test_ds = compatibility.GetName(fake_data_store.FakeDataStore)

  config.CONFIG.Set("Datastore.implementation", test_ds)

  if not INIT_RAN:
    server_logging.ServerLoggingStartupInit()
    server_logging.SetTestVerbosity()

  blob_store_test_lib.UseTestBlobStore()
  registry.TestInit()

  db = data_store.DB.SetupTestDB()
  if db:
    data_store.DB = db
  data_store.DB.Initialize()
  aff4.AFF4InitHook().Run()

  INIT_RAN = True
