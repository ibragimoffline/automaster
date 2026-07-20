import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from tests.base import BaseAPITestCase
from tests.factories import DEFAULT_PASSWORD, CustomerFactory, UserFactory

User = get_user_model()


class RegisterAPITestCase(BaseAPITestCase):
    url = reverse('register')

    def payload(self, **overrides):
        data = {
            'username': 'yangi_user',
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'email': 'ali@example.com',
            'phone': '+998901112233',
            'password': 'StrongPass123',
        }
        data.update(overrides)
        return data

    def test_register_creates_user_and_returns_tokens(self):
        resp = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertKeys(resp.data, ['id', 'username', 'phone', 'role', 'tokens'])
        self.assertKeys(resp.data['tokens'], ['access', 'refresh'])

        user = User.objects.get(username='yangi_user')
        self.assertTrue(user.check_password('StrongPass123'))
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.phone_verified)

    def test_password_is_hashed_and_not_returned(self):
        resp = self.client.post(self.url, self.payload(), format='json')

        self.assertNotIn('password', resp.data)
        user = User.objects.get(username='yangi_user')
        self.assertNotEqual(user.password, 'StrongPass123')

    def test_register_as_master_role(self):
        resp = self.client.post(
            self.url, self.payload(role=User.Role.MASTER), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['role'], User.Role.MASTER)

    def test_phone_verified_is_read_only_on_register(self):
        resp = self.client.post(
            self.url, self.payload(phone_verified=True), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertFalse(resp.data['phone_verified'])
        self.assertFalse(User.objects.get(username='yangi_user').phone_verified)

    def test_short_password_rejected(self):
        resp = self.client.post(self.url, self.payload(password='qisqa'), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data)

    def test_duplicate_username_rejected(self):
        UserFactory(username='band_user')

        resp = self.client.post(self.url, self.payload(username='band_user'), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', resp.data)

    def test_duplicate_phone_rejected(self):
        UserFactory(phone='+998901112233')

        resp = self.client.post(self.url, self.payload(phone='+998901112233'), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', resp.data)

    def test_missing_required_fields_rejected(self):
        resp = self.client.post(self.url, {'username': 'faqat_username'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', resp.data)
        self.assertIn('password', resp.data)


class TokenAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.user = CustomerFactory(username='tokenchi', phone='+998907778899')
        self.url = reverse('token_obtain_pair')

    def test_obtain_token_with_valid_credentials(self):
        resp = self.client.post(
            self.url,
            {'username': 'tokenchi', 'password': DEFAULT_PASSWORD},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertKeys(resp.data, ['access', 'refresh', 'user'])
        self.assertEqual(resp.data['user']['username'], 'tokenchi')
        self.assertEqual(resp.data['user']['role'], User.Role.CUSTOMER)

    def test_token_payload_contains_custom_claims(self):
        from rest_framework_simplejwt.tokens import AccessToken

        resp = self.client.post(
            self.url,
            {'username': 'tokenchi', 'password': DEFAULT_PASSWORD},
            format='json',
        )
        token = AccessToken(resp.data['access'])

        self.assertEqual(token['username'], 'tokenchi')
        self.assertEqual(token['role'], User.Role.CUSTOMER)
        self.assertEqual(token['phone'], '+998907778899')
        self.assertTrue(token['phone_verified'])

    def test_wrong_password_rejected(self):
        resp = self.client.post(
            self.url, {'username': 'tokenchi', 'password': 'notmypassword'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_new_access(self):
        obtain = self.client.post(
            self.url,
            {'username': 'tokenchi', 'password': DEFAULT_PASSWORD},
            format='json',
        )

        resp = self.client.post(
            reverse('token_refresh'),
            {'refresh': obtain.data['refresh']},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    def test_invalid_refresh_token_rejected(self):
        resp = self.client.post(
            reverse('token_refresh'), {'refresh': 'yaroqsiz.token.qiymat'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_header_authenticates_request(self):
        obtain = self.client.post(
            self.url,
            {'username': 'tokenchi', 'password': DEFAULT_PASSWORD},
            format='json',
        )

        resp = self.client.get(
            reverse('me'), HTTP_AUTHORIZATION=f'Bearer {obtain.data["access"]}')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'tokenchi')


class MeAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.user = CustomerFactory()
        self.url = reverse('me')

    def test_anonymous_cannot_access(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_own_profile(self):
        self.auth(self.user)

        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.user.id)
        self.assertEqual(resp.data['phone'], self.user.phone)

    def test_can_update_own_profile(self):
        self.auth(self.user)

        resp = self.client.patch(
            self.url, {'first_name': 'Bekzod', 'email': 'bekzod@example.com'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Bekzod')
        self.assertEqual(self.user.email, 'bekzod@example.com')

    def test_phone_verified_cannot_be_set_via_patch(self):
        user = CustomerFactory(phone_verified=False)
        self.auth(user)

        resp = self.client.patch(self.url, {'phone_verified': True}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.phone_verified)

    def test_cannot_take_someone_elses_phone(self):
        CustomerFactory(phone='+998900000001')
        self.auth(self.user)

        resp = self.client.patch(self.url, {'phone': '+998900000001'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', resp.data)


class VerifyPhoneAPITestCase(BaseAPITestCase):
    url = reverse('verify-phone')

    def test_anonymous_cannot_verify(self):
        resp = self.client.post(self.url)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verifies_own_phone(self):
        user = CustomerFactory(phone_verified=False)
        self.auth(user)

        resp = self.client.post(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['phone_verified'])
        user.refresh_from_db()
        self.assertTrue(user.phone_verified)

    def test_verifying_twice_is_idempotent(self):
        user = CustomerFactory(phone_verified=True)
        self.auth(user)

        resp = self.client.post(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.phone_verified)



@pytest.mark.django_db
def test_user_str_contains_username_and_role():
    user = UserFactory(username='ali', role=User.Role.MASTER)

    assert str(user) == 'ali - MASTER'


@pytest.mark.django_db
def test_default_role_is_customer():
    user = User.objects.create_user(
        username='oddiy', password=DEFAULT_PASSWORD, phone='+998905554433')

    assert user.role == User.Role.CUSTOMER
    assert user.phone_verified is False


@pytest.mark.django_db
@pytest.mark.parametrize('role', [User.Role.CUSTOMER, User.Role.MASTER, User.Role.ADMIN])
def test_register_accepts_every_role(api_client, role):
    resp = api_client.post(
        reverse('register'),
        {
            'username': f'user_{role.lower()}',
            'phone': f'+99890{abs(hash(role)) % 10000000:07d}',
            'password': 'StrongPass123',
            'role': role,
        },
        format='json',
    )

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data['role'] == role
