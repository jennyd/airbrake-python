import airbrake
import mock
import unittest
from airbrake.notifier import Airbrake


class TestErrbit(unittest.TestCase):
    def test_one_of_project_id_and_api_url_required(self):
        with self.assertRaises(TypeError):
            Airbrake(api_key=2, environment='test')

    def test_api_key_required(self):
        with self.assertRaises(TypeError):
            Airbrake(project_id=1, environment='test')

    def test_airbrake_io_api_url(self):
        ab = Airbrake(project_id=1, api_key=2, environment='test')
        self.assertEqual(
            'https://airbrake.io/api/v3/projects/1/notices',
            ab.api_url
        )

    def test_custom_api_url(self):
        ab = Airbrake(api_url='https://example.com', api_key=2, environment='test')
        self.assertEqual('https://example.com', ab.api_url)


class TestAirbrakeNotifier(unittest.TestCase):

    def _create_notify(test, exception, session={}, environment={}):
        def notify(self, payload):
            test.assertEqual(session, payload['session'])
            test.assertEqual(environment, payload['environment'])
            test.assertEqual(str(exception), payload['errors'][0]['message'])
        return notify

    def setUp(self):
        super(TestAirbrakeNotifier, self).setUp()
        self.logger = airbrake.getLogger(
            'custom-loglevel',
            api_key='fakekey', project_id='fakeprojectid')
        self.session = {'user_id': 100}
        self.environment = {'PATH': '/usr/bin/'}

    def test_string(self):
        msg = "Zlonk!"
        notify = self._create_notify(msg)
        with mock.patch.object(Airbrake, 'notify', notify):
            self.logger.exception(msg)

    def test_exception(self):
        msg = "Pow!"
        notify = self._create_notify(Exception(msg))
        with mock.patch.object(Airbrake, 'notify', notify):
            self.logger.exception(Exception(msg))

    def test_exception_with_session(self):
        msg = "Boff!"
        notify = self._create_notify(msg, session=self.session)
        with mock.patch.object(Airbrake, 'notify', notify):
            extra = {'session': self.session}
            self.logger.exception(Exception(msg), extra=extra)

    def test_exception_with_environment(self):
        msg = "Whap!"
        notify = self._create_notify(msg, environment=self.environment)
        with mock.patch.object(Airbrake, 'notify', notify):
            extra = {'environment': self.environment}
            self.logger.exception(Exception(msg), extra=extra)

if __name__ == '__main__':
    unittest.main()
