import sys
sys.path.append(".")

import ai
import unittest

import main
import urllib2

from ai.killncapture import KillNCapture

class TestAILoader(unittest.TestCase):
  def setUp(self):
    self.setupModule = main.setupModule
    self.urlopen = urllib2.urlopen
    pass

  def test_load_file_ai(self):
    from ai.killncapture import KillNCapture
    mod = main.loadFileAIData("ai/killncapture.py")
    self.assertEqual(mod.AIClass, KillNCapture.__name__)

  def test_load_github_ai(self):
    # [okay] unfortunately, need to know the internals of github loading
    # function to stub out the url loader, unless i want to abstract the url
    # loader out

    def mockLoadURL(url):
      return open("ai/killncapture.py")

    urllib2.urlopen = mockLoadURL
    mod = main.loadGithubAIData("okayzed:basic/killncapture.py")
    self.assertEqual(mod.AIClass, KillNCapture.__name__)

  # Test that github dependencies are properly loaded
  def test_load_github_dep(self):
    # [okay] unfortunately, need to know the internals of github loading
    # function to stub out the url loader, unless i want to abstract the url
    # loader out
    main.generate_github_url = lambda u,f: f
    mock_loaded_modules = []
    def mockLoadURL(filename):
      mock_loaded_modules.append(filename)
      print "Loading %s" % (filename)
      return open(filename)

    urllib2.urlopen = mockLoadURL
    mod = main.loadGithubAIData("okayzed:okay/remote_dep.py")

    self.assertIn("okay/remote_dep.py", mock_loaded_modules)
    self.assertIn("okay/okay.py", mock_loaded_modules)

  # Test that file dependencies are properly loaded
  def test_load_file_dep(self):
    loaded_modules = []
    def accountForSetupModule(*args, **kwargs):
      mod = self.setupModule(*args, **kwargs)
      loaded_modules.append(mod)
      return mod

    main.setupModule = accountForSetupModule
    main.loadFileAIData("dmanai/okay/remote_dep.py")
    ai_files = map(lambda m: m.__file__, loaded_modules)

    # These are hardcoded and probably wrong. It should do a check on the FS
    # to make sure that the two files are the same
    self.assertIn("dmanai/okay/remote_dep.py", ai_files)
    self.assertIn("dmanai/okay/../okay/okay.py", ai_files)

  # Test that an AI file can only be loaded once
  def test_load_file_once(self):
    bp =  "ai/basepatroller.py"
    knc = "ai/killncapture.py"
    options, ais = main.parseOptions([bp, knc, knc, bp])
    self.assertEquals(len(ais), 2)
    self.assertIn(bp, ais)
    self.assertIn(knc, ais)

  def test_load_highlighted_ai(self):
    bp =  "ai/basepatroller.py"
    knc = "ai/killncapture.py"
    options, ais = main.parseOptions(["--hl", bp, knc,])
    self.assertIn(bp, options.highlight)
    self.assertIn(knc, ais)

  def test_load_no_ai(self):
    options, ais = main.parseOptions([])
    self.assertEqual(ais, [])


if __name__ == "__main__":
  unittest.main()

