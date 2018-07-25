# -*- coding: utf-8 -*-
"""
Tests for the Enterprise API permissions.
"""

from __future__ import absolute_import, unicode_literals

from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from enterprise.api.v1.permissions import HasEnterpriseDataAPIAccess, HasEnterpriseEnrollmentAPIAccess
from test_utils.factories import GroupFactory, UserFactory


class PermissionsTestMixin(object):
    """
    Permission Test Mixin.
    """
    def get_request(self, user=None, data=None):
        """
        :return Request object
        """
        request = APIRequestFactory().post('/', data)

        if user:
            force_authenticate(request, user=user)

        return Request(request, parsers=(JSONParser(),))


class TestEnterpriseAPIPermissions(PermissionsTestMixin, APITestCase):
    """
    Tests for Enterprise API permissions.
    """

    permissions_class_map = {
        'enterprise_enrollment_api_access': HasEnterpriseEnrollmentAPIAccess(),
        'enterprise_data_api_access': HasEnterpriseDataAPIAccess(),
    }

    def setUp(self):
        """
        Setup the test cases.
        """
        super(TestEnterpriseAPIPermissions, self).setUp()
        self.user = UserFactory(email='test@example.com', password='test', is_staff=True)

    def test_is_staff_or_user_in_group_permissions(self):
        for group_name in self.permissions_class_map:
            group = GroupFactory(name=group_name)
            group.user_set.add(self.user)
            request = self.get_request(user=self.user)
            self.assertTrue(self.permissions_class_map[group_name].has_permission(request, None))

    def test_not_staff_and_not_in_group_permissions(self):
        user = UserFactory(email='test@example.com', password='test', is_staff=False)
        for group_name in self.permissions_class_map:
            request = self.get_request(user=user)
            self.assertFalse(self.permissions_class_map[group_name].has_permission(request, None))

    def test_staff_but_not_in_group_permissions(self):
        user = UserFactory(email='test@example.com', password='test', is_staff=True)
        for group_name in self.permissions_class_map:
            request = self.get_request(user=user)
            self.assertTrue(self.permissions_class_map[group_name].has_permission(request, None))

    def test_not_staff_but_in_group_permissions(self):
        user = UserFactory(email='test@example.com', password='test', is_staff=False)
        for group_name in self.permissions_class_map:
            group = GroupFactory(name=group_name)
            group.user_set.add(user)
            request = self.get_request(user=user)
            self.assertTrue(self.permissions_class_map[group_name].has_permission(request, None))
