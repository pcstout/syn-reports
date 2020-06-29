import os
import urllib
import getpass
import re
import synapseclient as syn


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
            syn.core.utils.printTransferProgress = lambda *a, **k: None

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

    @classmethod
    def is_synapse_id(cls, value):
        """Gets if a string is a Synapse ID.

        Args:
            value: The string to check.

        Returns:
            True or False.
        """
        if isinstance(value, str):
            return re.match('^syn[0-9]+$', value.strip(), re.IGNORECASE) is not None
        else:
            return False

    PROJECT_TYPE_DISPLAY_NAME = 'Project'
    FOLDER_TYPE_DISPLAY_NAME = 'Folder'
    FILE_TYPE_DISPLAY_NAME = 'File'
    LINK_TYPE_DISPLAY_NAME = 'Line'
    TABLE_TYPE_DISPLAY_NAME = 'Table'

    CONCRETE_TYPE_MAPPING = {
        'org.sagebionetworks.repo.model.FileEntity': FILE_TYPE_DISPLAY_NAME,
        'org.sagebionetworks.repo.model.Folder': FOLDER_TYPE_DISPLAY_NAME,
        'org.sagebionetworks.repo.model.Link': LINK_TYPE_DISPLAY_NAME,
        'org.sagebionetworks.repo.model.Project': PROJECT_TYPE_DISPLAY_NAME,
        'org.sagebionetworks.repo.model.table.TableEntity': TABLE_TYPE_DISPLAY_NAME
    }

    @classmethod
    def _extract_concrete_type(cls, obj):
        result = obj
        if not isinstance(obj, str):
            for key in ['concreteType', 'type']:
                if key in obj:
                    result = obj[key]
                    break

        if str(result) not in cls.CONCRETE_TYPE_MAPPING.keys():
            raise ValueError('Cannot extract type from: {0}'.format(obj))

        return result

    @classmethod
    def entity_type_display_name(cls, concrete_type):
        concrete_type = cls._extract_concrete_type(concrete_type)
        return cls.CONCRETE_TYPE_MAPPING.get(concrete_type, 'Unknown Type: {0}'.format(concrete_type))

    @classmethod
    def is_project(cls, concrete_type):
        return cls.entity_type_display_name(concrete_type) == cls.PROJECT_TYPE_DISPLAY_NAME

    @classmethod
    def is_folder(cls, concrete_type):
        return cls.entity_type_display_name(concrete_type) == cls.FOLDER_TYPE_DISPLAY_NAME

    @classmethod
    def is_file(cls, concrete_type):
        return cls.entity_type_display_name(concrete_type) == cls.FILE_TYPE_DISPLAY_NAME

    @classmethod
    def users_teams(cls, user_id):
        """Gets all the teams a user is part of.

        Args:
            user_id:

        Returns:

        """
        for item in cls.client()._GET_paginated('/user/{0}/team/'.format(user_id)):
            yield item

    @classmethod
    def users_project_access(cls, user_id, **kwparams):
        """ Gets the Projects a user has access to.

        https://rest-docs.synapse.org/rest/GET/projects/user/principalId.html

        Args:
            user_id: The user ID to get activity for.
            **kwparams: Params for the GET request.

        Returns:
            Generator
        """
        request = (kwparams or {})

        response = {"nextPageToken": "first"}
        while response.get('nextPageToken') is not None:
            url_params = urllib.parse.urlencode(request)
            uri = '/projects/user/{0}?{1}'.format(user_id, url_params)

            response = cls.client().restGET(uri)
            for child in response['results']:
                yield child
            request['nextPageToken'] = response.get('nextPageToken', None)

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
