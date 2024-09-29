from worker_python3.static_scanner_qa_utils.results import JobQueue
from worker_python3.static_scanner_qa_utils.utils import (
    absolute_windows_path,
    IntervalCallable,
    find_file,
    find_java,
    s3_bucket,
    logger,
    show_cmdline,
    fetch_env_var,
)

import logging
import os
import pprint
from datetime import datetime
import time


long_ago = datetime(2000, 1, 1, 0, 0, 0, 0)   # don't allow start_time = None

HOME_LINUX = '/home/ec2-user' if os.path.exists('/home/ec2-user') else '/work'


class Preprocessor(object):
    def __init__(self, branch, revision, store_dir, store_name, extra_preprocessor_args):
        self._branch = branch
        self._revision = revision
        self._store_dir = os.path.abspath(store_dir)
        self._store_name = store_name
        self._app_path = None
        self._job_status = 'Ready'
        if extra_preprocessor_args:
            if extra_preprocessor_args[0] == extra_preprocessor_args[-1] == '"':
                extra_preprocessor_args = extra_preprocessor_args[1:-1]
            extra_preprocessor_args = extra_preprocessor_args.replace('\\"', '"')
        self._extra_preprocessor_args = extra_preprocessor_args.strip().split() if extra_preprocessor_args else []

    @property
    def extra_preprocessor_args(self):
        """:returns: any optional command line args for the preprocessor executable"""
        return self._extra_preprocessor_args

    @property
    def store_dir(self):
        return self._store_dir

    @property
    def store_name(self):
        return self._store_name

    def fetch_and_extract_build(self, branch, revision, outname, outdir,
                                is_scs=False):
        logger.info('saving preprocessor build {0} from S3 bucket to {1}'.format(revision, outname))
        assert not is_scs, 'SCS not yet implemented here'     # TODO

        prefix = "preprocessor/preprocessor"
        assert os.path.isdir(outdir)
        outname = os.path.realpath(os.path.join(os.getcwd(), outname))
        found = s3_bucket(prefix, branch, revision, download=outname)
        if found.endswith(".tar.gz") and not outname.endswith(".tar.gz"):
            assert not outname.endswith(".zip"), (found, outname)
            outname += ".tar.gz"
        if found.endswith(".zip") and not outname.endswith(".zip"):
            assert not outname.endswith(".tar.gz"), (found, outname)
            outname += ".zip"
        assert os.path.isfile(outname), outname
        self._store_name = outname
        logger.info('extracting %s to %s', outname, outdir)
        if outname.endswith("zip"):
            os.system('(cd {0}; unzip {1} >/dev/null)'.format(outdir, outname))
        elif outname.endswith("tar.gz"):
            os.system('(cd {0}; tar xfz {1})'.format(outdir, outname))
        else:
            logging.warning("Cannot figure how to extract {0}".format(outname))
        # what's the correct name for the log4j.xml file? nobody knows
        cmd = ("cp /work/preflight_log4j.xml " + outdir +
               "/preprocessor/preflight_log4j.xml")
        r = os.system(cmd)
        logger.debug("Exit status of {0} is {1}".format(cmd, r))
        cmd = ("cp /work/preflight_log4j.xml " + outdir +
               "/preprocessor/preflight_log4j2.xml")
        r = os.system(cmd)
        logger.debug("Exit status of {0} is {1}".format(cmd, r))

    def fetch_and_extract_preprocessor(self):
        # pylint: disable=no-member
        assert isinstance(self, Preprocessor)
        self.fetch_and_extract_build(self._branch, self._revision, self._store_name, self._store_dir)
        assert os.path.isfile(self._store_name), self._store_name
        assert os.path.isdir(self._store_dir), self._store_dir
        files = os.listdir(self._store_dir)
        assert len(files) > 0

    def __hash__(self):
        return hash((self.branch, self.revision))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    @property
    def job_status(self):
        return self._job_status

    @property
    def branch(self):
        return self._branch

    @property
    def branch_basename(self):
        return os.path.basename(self.branch)

    @property
    def revision(self):
        return self._revision

    def deploy_preprocessor(self):
        """
        :return:
        """
        self.fetch_and_extract_preprocessor()

    def get_preproc_path(self, is_scs=False):
        """ Return path to 'Preprocessor' folder """
        # pylint: disable=maybe-no-member
        p = "/lib/preprocessor.jar"
        preproc_jar = find_file(p, self._store_dir)
        r = preproc_jar.replace(p, "")
        assert os.path.isdir(r), r
        return r
        # pylint: enable=maybe-no-member

    def get_preflight_paths(self, request_info, preproc_path):
        """
        Getpaths for preprocessor to run
        @arg: request_info: PreprocessorRequest object
        return tuple (binary_eh_path, compile_xml_path, java_folder_path)
        """
        assert isinstance(preproc_path, str), repr(preproc_path)
        assert os.path.isdir(preproc_path), preproc_path
        binary_eh_path = request_info['app_ver_binary_root']
        compile_xml_path = os.path.join(binary_eh_path, 'compile.xml')
        if not os.path.exists(binary_eh_path):
            raise Exception("Binary path does not exist: '%s'!" % binary_eh_path)

        php_folder_path = os.path.join(preproc_path, 'php')
        if os.path.exists(php_folder_path):
            os.system("chmod -R 755 %s" % php_folder_path)

        java_bin_path = find_java(self.store_dir)
        assert os.path.exists(java_bin_path), "Java bin path '%s' does not exist!" % java_bin_path

        return (binary_eh_path, compile_xml_path, java_bin_path)

    def submit_preflight(self, request_info):
        """ Run preprocessor directly, without enginehost (STATICQA-6179) """
        assert request_info['app_ver_binary_root'] is not None
        assert os.path.isdir(request_info['app_ver_binary_root']), request_info['app_ver_binary_root']
        assert isinstance(request_info['app_ver_main_binary_files'], list), request_info['app_ver_main_binary_files']
        assert request_info['env_dir'], request_info['env_dir']
        # get and update paths
        logger.info("app_ver_binary_root = {0}".format(request_info['app_ver_binary_root']))
        logger.info("app_ver_main_binary_files = {0}".format(request_info['app_ver_main_binary_files']))
        assert isinstance(request_info['app_ver_main_binary_files'], list)
        is_scs = ('scs_test_worker' in self.store_dir.lower() or
                  'scs_test_worker' in request_info['app_ver_binary_root'].lower())
        PREPROC_PATH = self.get_preproc_path(is_scs)
        init_dir = os.getcwd()
        os.chdir(PREPROC_PATH)
        os.system('chmod 755 PreflightPreprocessor.sh')
        binary_eh_path, compile_xml_path, java_bin_path = self.get_preflight_paths(request_info, PREPROC_PATH)

        # copy preflight_log4j.xml to where preprocessor expects it to be
        os.system('mkdir -p dist/conf')  # Preprocessor expects ...log4j.xml to be here
        os.system('cp preflight_log4j.xml dist/conf/')

        # set up preproc command
        assert request_info['env_dir'] is not None, request_info
        preproc_cmd = (
            './PreflightPreprocessor.sh ' +
            ' --app_binary_root ' + binary_eh_path +
            ' --output_file_path ' + compile_xml_path +
            ' --environments_path ' + request_info['env_dir']
            + " " + (" ".join(self.extra_preprocessor_args) if isinstance(self.extra_preprocessor_args, (list, tuple))
   else self.extra_preprocessor_args)
        )
        if not logger.isEnabledFor(logging.DEBUG):
            preproc_cmd += " > /dev/null 2>&1"
        # check to see if /tmp is mounted with "noexec"
        cmd = 'mount | grep " /tmp" | grep noexec'
        r = os.system(cmd)
        if r == 0:
            logger.error("/tmp directory was mounted with 'noexec' option, REMOUNT IT")
            # zero exit status means it is mounted with noexec and that's a problem
            os.system("sudo mount /tmp -o remount,exec")

        # Update preproc to use correct JDK, e.g. .../preprocessor/Preprocessor/Java/bin/java
        # Add the java_bin_path First so the correct java is found there
        initial_env_path = os.environ['PATH']
        os.environ['PATH'] = java_bin_path + os.pathsep + initial_env_path
        try:
            # run preflight preprocessor to generate veracodegen.war files
            R = None
            if os.path.isfile(self._app_path):
                inf = open(self._app_path, "rb")
                R = inf.read()
                inf.close()

            show_cmdline(preproc_cmd, src=self, app_path=self._app_path)
            retcode = os.system(preproc_cmd)
            if retcode != 0:
                logger.error('\n\n\n * * * PREPROCESSOR FAILED * * *\n\n\n')
                self._job_status = 'Failed'
                return
            if R and not os.path.isfile(self._app_path):
                open(self._app_path, "wb").write(R)
            pp_out_files = fetch_env_var('PP_OUTPUT_TARBALL')
            if pp_out_files:
                cmd = "(cd {0}; find . -type f -name {1}".format(self._app_path, pp_out_files)
                logger.debug(cmd)
                files = [f.strip() for f in os.popen(cmd)]
                logger.debug(files)
                if files:
                    tarballname = '/tmp/pp_output_files_{0}.tar.gz'.format(time.time())
                    cmd = '(cd {0}; tar cfz {1} {2})'.format(
                        self._app_path, tarballname, " ".join(files)
                    )
                    logger.info(cmd)
                    os.system(cmd)
            self._job_status = 'Finished'
        finally:
            os.environ['PATH'] = initial_env_path
        os.chdir(init_dir)


class PreprocessorQueue(JobQueue):
    pass
