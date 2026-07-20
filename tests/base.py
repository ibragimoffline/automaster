from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):

    def auth(self, user):
        self.client.force_authenticate(user=user)
        return user

    def logout(self):
        self.client.force_authenticate(user=None)

    def assertKeys(self, data, keys):
        for key in keys:
            self.assertIn(key, data, f'"{key}" javobda yo\'q')
