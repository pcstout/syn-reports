import sys
import datetime
import functools
import os
import urllib
import synapseclient as syn
from synapsis import Synapsis


class Utils:
    @staticmethod
    def eprint(*args, **kwargs):
        """Print to stderr"""
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def expand_path(local_path):
        var_path = os.path.expandvars(local_path)
        expanded_path = os.path.expanduser(var_path)
        return os.path.abspath(expanded_path)

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

    @classmethod
    def get_entity(cls, id_or_name, show_error_func=None, only_header=False):
        entity = None
        error = None
        try:
            if Synapsis.is_synapse_id(id_or_name):
                syn_id_to_load = id_or_name
            else:
                syn_id_to_load = Synapsis.findEntityId(id_or_name)

            if syn_id_to_load:
                if only_header:
                    entity = Synapsis.restGET('/entity/{0}/type'.format(syn_id_to_load))
                else:
                    entity = Synapsis.get(syn_id_to_load, downloadFile=False)
        except syn.core.exceptions.SynapseHTTPError as ex:
            if ex.response.status_code == 404:  # a 404 error is raised if the entity does not exist
                return None
            error = ex
        except Exception as ex:
            error = ex

        if error is not None:
            if show_error_func:
                show_error_func('Error loading entity header: {0}, Error: {1}'.format(id_or_name, ex))
            else:
                raise
        return entity

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

            response = Synapsis.Synapse.restGET(uri)
            for child in response['results']:
                yield child
            request['nextPageToken'] = response.get('nextPageToken', None)

    @classmethod
    def users_teams(cls, user_id):
        """Gets all the teams a user is part of.

        Args:
            user_id:

        Returns:

        """
        for item in Synapsis._GET_paginated('/user/{0}/team/'.format(user_id)):
            yield item

    class WithCache:
        LRU_MAXSIZE = (os.cpu_count() or 1) * 16

        @classmethod
        @functools.lru_cache(maxsize=LRU_MAXSIZE, typed=True)
        def get_user(cls, username_or_id):
            try:
                return Synapsis.getUserProfile(username_or_id, refresh=True)
            except (ValueError, syn.core.exceptions.SynapseHTTPError):
                return None

        @classmethod
        @functools.lru_cache(maxsize=LRU_MAXSIZE, typed=True)
        def get_team(cls, team_id_or_name):
            try:
                return Synapsis.getTeam(team_id_or_name)
            except (ValueError, syn.core.exceptions.SynapseHTTPError):
                return None

        @classmethod
        @functools.lru_cache(maxsize=LRU_MAXSIZE, typed=True)
        def get_user_or_team(cls, user_id_or_team_id):
            # NOTE: User and Team IDs do NOT overlap in Synapse.
            return cls.get_user(user_id_or_team_id) or cls.get_team(user_id_or_team_id)

        @classmethod
        @functools.lru_cache(maxsize=LRU_MAXSIZE, typed=True)
        def get_team_members(cls, team_id):
            try:
                return list(Synapsis.getTeamMembers(team_id))
            except (ValueError, syn.core.exceptions.SynapseHTTPError):
                return []

        @classmethod
        @functools.lru_cache(maxsize=LRU_MAXSIZE, typed=True)
        def get_team_open_invitations(cls, team_id):
            try:
                return list(Synapsis.get_team_open_invitations(team_id))
            except (ValueError, syn.core.exceptions.SynapseHTTPError):
                return []
