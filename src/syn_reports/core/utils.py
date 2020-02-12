import os
import re
import datetime


class Utils:

    @staticmethod
    def expand_path(local_path):
        var_path = os.path.expandvars(local_path)
        expanded_path = os.path.expanduser(var_path)
        return os.path.abspath(expanded_path)

    @staticmethod
    def is_synapse_id(value):
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

    @staticmethod
    def entity_type_display_name(concrete_type):
        return {
            'org.sagebionetworks.repo.model.FileEntity': 'File',
            'org.sagebionetworks.repo.model.Folder': 'Folder',
            'org.sagebionetworks.repo.model.Link': 'Link',
            'org.sagebionetworks.repo.model.Project': 'Project',
            'org.sagebionetworks.repo.model.table.TableEntity': 'Table'
        }.get(concrete_type, 'Unknown Type: {0}'.format(concrete_type))

    @staticmethod
    def ensure_dirs(local_path):
        """Ensures the directories in local_path exist.

        Args:
            local_path: The local path to ensure.

        Returns:
            None
        """
        if not os.path.isdir(local_path):
            os.makedirs(local_path)

    @staticmethod
    def timestamp_str():
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
