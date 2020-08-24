import pytest
from app.clients.sms.aws_sns import AwsSnsClient


@pytest.fixture(scope='function')
def aws_sns_client(notify_api, mocker):
    with notify_api.app_context():
        aws_sns_client = AwsSnsClient()
        statsd_client = mocker.Mock()
        aws_sns_client.init_app(notify_api, statsd_client)
        return aws_sns_client


@pytest.fixture(scope='function')
def boto_mock(aws_sns_client, mocker):
    boto_mock = mocker.patch.object(aws_sns_client, '_client', create=True)
    return boto_mock


def test_send_sms_successful_returns_aws_sns_response(aws_sns_client, boto_mock):
    to = "6135555555"
    content = reference = 'foo'
    aws_sns_client.send_sms(to, content, reference)
    boto_mock.publish.assert_called_once_with(
        PhoneNumber="+16135555555",
        Message=content,
        MessageAttributes={'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}}
    )


def test_send_sms_returns_raises_error_if_there_is_no_valid_number_is_found(aws_sns_client, boto_mock):
    to = ""
    content = reference = 'foo'

    with pytest.raises(ValueError) as excinfo:
        aws_sns_client.send_sms(to, content, reference)

    assert 'No valid numbers found for SMS delivery' in str(excinfo.value)
