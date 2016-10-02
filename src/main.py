# coding=utf-8

import builtins
import os
import sys

import certifi

from src.low import constants
from src.low.custom_logging import make_logger
from src.low.custom_path import Path


def main(*, init_only=False, test_run=False):
    # FIXME: check all NotImplementedError
    # noinspection PyBroadException
    try:

        if len(sys.argv) > 1:
            print('sys.argv: ', str(sys.argv))
            if 'test_and_exit' in sys.argv:
                constants.TESTING = True

        if test_run:
            constants.TESTING = True

        if constants.TESTING:
            # Bypass creation of main logger for tests
            import logging

            logger = logging.getLogger('__main__')
        else:
            logger = make_logger(log_file_path=constants.PATH_LOG_FILE)

        cacert = Path(certifi.where())
        logger.info('checking certificate')
        if not cacert.crc32() == '7E8D9995':
            # FIXME this will need some work
            raise ImportError('cacert.pem file is corrupted, please reinstall EASI ({})'.format(cacert.crc32()))
        logger.debug('setting up local cacert file to: {}'.format(str(cacert)))
        os.environ['REQUESTS_CA_BUNDLE'] = str(cacert)

        logger.info('sentry: initializing')
        from src.sentry import crash_reporter, sentry_register_context

        logger.debug('sentry online: {}'.format(crash_reporter.state.ONLINE))

        logger.info('builtins overloads: registering')

        if constants.FROZEN:
            def new_print(*args, **kwargs):
                """Replace print builtins to mute output on frozen version"""
                pass

            builtins.print = new_print

        logger.info('builtins overloads: registered')

        from src.cfg import config

        sentry_register_context('config', config)

        from src.keyring import keyring

        from PyQt5.QtGui import QFontDatabase
        from PyQt5.QtWidgets import QApplication
        from src.qt import qt_resources
        from src.ui.dialog_disclaimer import DisclaimerDialog
        from src.ui.main_ui.main_ui import MainUi

        logger.info('QApplication: starting')
        qt_app = QApplication([])
        logger.info('QApplication: started')
        logger.info('QFontDatabase: starting')
        font_db = QFontDatabase()
        logger.debug('QFontDatabase: adding font to database')
        font_db.addApplicationFont(qt_resources.app_font)
        logger.debug('QFontDatabase: registering app-wide font')
        qt_app.setFont(font_db.font('Anonymous Pro', 'normal', 9))
        logger.info('QFontDatabase: started')

        if constants.TESTING:
            logger.info('disclaimer: skipping (testing mode)')
        else:
            logger.info('disclaimer: showing')
            if not DisclaimerDialog.make():
                logger.warning('disclaimer: user declined')
                sys.exit(0)
            logger.info('disclaimer: done')

        # noinspection PyUnusedLocal
        main_gui = MainUi(qt_app)

        if init_only:
            return qt_app, main_gui

        from src.upd import check_for_update
        from src.dcs import init_dcs_installs
        from src.keyring import init_keyring
        from src.threadpool import ThreadPool
        from src.sig import sig_splash, sig_main_ui, sig_main_ui_states
        import src.upd

        logger.info('startup: init')
        pool = ThreadPool(_num_threads=1, _basename='startup', _daemon=False)
        pool.queue_task(sig_splash.show)
        pool.queue_task(check_for_update)
        pool.queue_task(init_dcs_installs)
        pool.queue_task(init_keyring)
        pool.queue_task(sig_splash.kill)
        pool.queue_task(sig_main_ui.show)
        pool.queue_task(sig_main_ui_states.set_current_state, ['running'])
        pool.queue_task(logger.info, ['startup: all done!'])

        logger.debug('startup queue populated')

        if 'test_and_exit' in sys.argv:
            pool.queue_task(sys.exit, [0])

        if constants.TESTING:
            pool.queue_task(sig_main_ui.exit)

        logger.info('transferring control to QtApp')
        sys.exit(qt_app.exec())

    except SystemExit:
        print('catched SystemExit')
        if constants.TESTING:
            return
        nice_exit(0, None)

    except KeyboardInterrupt:
        print('catched KeyboardInterrupt')
        if constants.TESTING:
            return
        nice_exit(0, None)


if __name__ == '__main__':

    def nice_exit(*_):
        import os
        # Shameful monkey-patching to bypass windows being a jerk
        # noinspection PyProtectedMember
        os._exit(0)


    import signal

    signal.signal(signal.SIGINT, nice_exit)

    main()