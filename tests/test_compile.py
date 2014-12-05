import os.path
from build_pack_utils import BuildPack
from common.integration import OptionsHelper
from common.integration import DirectoryHelper
from common.integration import FileAssertHelper
from common.integration import ErrorHelper
from common.components import BuildPackAssertHelper
from common.components import HttpdAssertHelper
from common.components import NginxAssertHelper
from common.components import PhpAssertHelper


class TestCompileApp1(object):
    def __init__(self):
        self.app_name = 'app-1'

    def setUp(self):
        self.dh = DirectoryHelper()
        (self.build_dir,
         self.cache_dir,
         self.temp_dir) = self.dh.create_bp_env(self.app_name)
        self.bp = BuildPack({
            'BUILD_DIR': self.build_dir,
            'CACHE_DIR': self.cache_dir,
            'TMPDIR': self.temp_dir
        }, '.')
        self.dh.copy_build_pack_to(self.bp.bp_dir)
        self.dh.register_to_delete(self.bp.bp_dir)
        self.opts = OptionsHelper(os.path.join(self.bp.bp_dir,
                                               'defaults',
                                               'options.json'))
        self.opts.set_download_url(
            'http://localhost:5000/binaries/{STACK}')

    def tearDown(self):
        self.dh.cleanup()

    def test_with_httpd(self):
        # helpers to confirm the environment
        bp = BuildPackAssertHelper()
        httpd = HttpdAssertHelper()
        php = PhpAssertHelper()
        # set web server to httpd, since that's what we're expecting here
        self.opts.set_web_server('httpd')
        # run the compile step of the build pack
        output = ErrorHelper().compile(self.bp)
        # confirm downloads
        httpd.assert_downloads_from_output(output)
        # confirm start script
        bp.assert_start_script_is_correct(self.build_dir)
        httpd.assert_start_script_is_correct(self.build_dir)
        php.assert_start_script_is_correct(self.build_dir)
        # confirm bp utils installed
        bp.assert_scripts_are_installed(self.build_dir)
        bp.assert_config_options(self.build_dir)
        # check env & proc files
        httpd.assert_contents_of_procs_file(self.build_dir)
        httpd.assert_contents_of_env_file(self.build_dir)
        php.assert_contents_of_procs_file(self.build_dir)
        php.assert_contents_of_env_file(self.build_dir)
        # webdir exists
        httpd.assert_web_dir_exists(self.build_dir, self.opts.get_webdir())
        # check php & httpd installed
        httpd.assert_files_installed(self.build_dir)
        php.assert_files_installed(self.build_dir)

    def test_with_nginx(self):
        # helpers to confirm the environment
        bp = BuildPackAssertHelper()
        nginx = NginxAssertHelper()
        php = PhpAssertHelper()
        # set web server to httpd, since that's what we're expecting here
        self.opts.set_web_server('nginx')
        # run the compile step of the build pack
        output = ErrorHelper().compile(self.bp)
        # confirm downloads
        nginx.assert_downloads_from_output(output)
        # confirm start script
        bp.assert_start_script_is_correct(self.build_dir)
        nginx.assert_start_script_is_correct(self.build_dir)
        php.assert_start_script_is_correct(self.build_dir)
        # confirm bp utils installed
        bp.assert_scripts_are_installed(self.build_dir)
        bp.assert_config_options(self.build_dir)
        # check env & proc files
        nginx.assert_contents_of_procs_file(self.build_dir)
        php.assert_contents_of_procs_file(self.build_dir)
        php.assert_contents_of_env_file(self.build_dir)
        # webdir exists
        nginx.assert_web_dir_exists(self.build_dir, self.opts.get_webdir())
        # check php & nginx installed
        nginx.assert_files_installed(self.build_dir)
        php.assert_files_installed(self.build_dir)


class TestCompileApp6(TestCompileApp1):
    def __init__(self):
        self.app_name = 'app-6'

    def setUp(self):
        TestCompileApp1.setUp(self)
        self.opts.set_webdir('public')

    def tearDown(self):
        self.dh.cleanup()

    def assert_app6_specifics(self):
        fah = FileAssertHelper()
        (fah.expect()
            .root(self.build_dir)
                .path('public')  # noqa
                .path('public', 'index.php')
                .path('public', 'info.php')
                .path('vendor')
                .path('vendor', 'lib.php')
                .path('.bp-config', 'options.json')
            .exists())

    def test_with_httpd(self):
        TestCompileApp1.test_with_httpd(self)
        # some app specific tests
        self.assert_app6_specifics()

    def test_with_nginx(self):
        TestCompileApp1.test_with_nginx(self)
        # some app specific tests
        self.assert_app6_specifics()
