import os
import logging
import getpass
import synapseclient as syn
import synapseclient.utils as syn_utils


class SynapseProxy:
    _synapse_client = None
    _synapse_username = None
    _synapse_password = None

    @classmethod
    def configure(cls, **kwargs):
        if kwargs.get('username', None):
            cls._synapse_username = kwargs.get('username')
        if kwargs.get('password', None):
            cls._synapse_password = kwargs.get('password')

    @classmethod
    def login(cls, username=None, password=None):
        username = cls._synapse_username if username is None else username
        password = cls._synapse_password if password is None else password

        username = username or os.getenv('SYNAPSE_USERNAME')
        password = password or os.getenv('SYNAPSE_PASSWORD')

        if not username:
            username = input('Synapse username: ')

        if not password:
            password = getpass.getpass(prompt='Synapse password: ')

        print('Logging into Synapse as: {0}'.format(username))
        try:
            # Disable the synapseclient progress output.
            syn.utils.printTransferProgress = lambda *a, **k: None

            cls._synapse_client = syn.Synapse(skip_checks=True)
            cls._synapse_client.login(username, password, silent=True, rememberMe=False)
        except Exception as ex:
            cls._synapse_client = None
            print('Synapse login failed: {0}'.format(str(ex)))

        return cls._synapse_client is not None

    @classmethod
    def logged_in(cls):
        return cls._synapse_client is not None

    @classmethod
    def client(cls):
        if not cls._synapse_client:
            cls.login()
        return cls._synapse_client

    class Permissions:
        ADMIN = [
            'UPDATE',
            'DELETE',
            'CHANGE_PERMISSIONS',
            'CHANGE_SETTINGS',
            'CREATE',
            'DOWNLOAD',
            'READ',
            'MODERATE'
        ]

        CAN_EDIT_AND_DELETE = [
            'DOWNLOAD',
            'UPDATE',
            'CREATE',
            'DELETE',
            'READ'
        ]

        CAN_EDIT = [
            'DOWNLOAD',
            'UPDATE',
            'CREATE',
            'READ'
        ]

        CAN_DOWNLOAD = [
            'DOWNLOAD',
            'READ'
        ]

        CAN_VIEW = [
            'READ'
        ]

        TEAM_MANAGER = [
            'SEND_MESSAGE',
            'READ',
            'UPDATE',
            'TEAM_MEMBERSHIP_UPDATE',
            'DELETE'
        ]

        @classmethod
        def name(cls, codes):
            codes = set(codes)
            if set(cls.ADMIN) == codes:
                return 'Administrator'
            elif set(cls.CAN_DOWNLOAD) == codes:
                return 'Can download'
            elif set(cls.CAN_VIEW) == codes:
                return 'Can view'
            elif set(cls.CAN_EDIT) == codes:
                return 'Can edit'
            elif set(cls.CAN_EDIT_AND_DELETE) == codes:
                return 'Can edit & delete'
