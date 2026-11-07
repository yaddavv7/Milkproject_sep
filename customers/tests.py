from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from customers.models import Customer


class CustomerModelTest(TestCase):
    """Test suite for Task 3: Customer Model."""

    def setUp(self):
        self.customer = Customer.objects.create(
            name="Ramesh Kumar",
            address="12, Gandhi Road, Chennai",
            litres_per_day="3 Litres",
            phone="9876543210"
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, "Ramesh Kumar")
        self.assertEqual(self.customer.address, "12, Gandhi Road, Chennai")
        self.assertEqual(self.customer.litres_per_day, "3 Litres")
        self.assertEqual(self.customer.phone, "9876543210")

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "Ramesh Kumar")


class HomePageTest(TestCase):
    """Test suite for Task 2: Home Page."""

    def test_home_page_status_and_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/home.html')
        self.assertTemplateUsed(response, 'customers/base.html')
        self.assertContains(response, "Milk Distribution Customer Record System")
        self.assertContains(response, "manage customer details and daily milk requirements")
        self.assertContains(response, "Add Customer")
        self.assertContains(response, "View Customers")
        self.assertContains(response, "© 2026 Milk Distribution Customer Record System. All Rights Reserved.")


class AuthenticationAndProtectionTest(TestCase):
    """Test suite for Task 8 and Task 9: Authentication, Logout & Page Protection."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123"
        )

    def test_signup_view_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/signup.html')

    def test_signup_view_post_success(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'NewStrongPassword123!',
            'password2': 'NewStrongPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertContains(response, "Account created successfully! Please log in.")

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/login.html')

    def test_login_view_post_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, testuser")

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_logout_view(self):
        self.client.login(username='testuser', password='TestPassword123')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have been logged out successfully.")

    def test_page_protection_unauthenticated(self):
        # Unauthenticated users must be redirected to login
        urls_to_test = [
            reverse('customer_list'),
            reverse('add_customer'),
            reverse('edit_customer', kwargs={'id': 1}),
            reverse('delete_customer', kwargs={'id': 1}),
        ]
        for url in urls_to_test:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)


class CustomerCRUDTest(TestCase):
    """Test suite for Tasks 4, 5, 6, 7: Customer CRUD operations."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="demo_user",
            password="SecurePassword123"
        )
        self.client.login(username="demo_user", password="SecurePassword123")

    def test_customer_list_empty(self):
        response = self.client.get(reverse('customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, demo_user")
        self.assertContains(response, "No customer records available.")

    def test_customer_list_with_records(self):
        Customer.objects.create(
            name="Suresh Raina",
            address="45, Lake View, Coimbatore",
            litres_per_day="2 Litres",
            phone="9845123456"
        )
        response = self.client.get(reverse('customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, demo_user")
        self.assertContains(response, "Suresh Raina")
        self.assertContains(response, "45, Lake View, Coimbatore")
        self.assertContains(response, "2 Litres")
        self.assertContains(response, "9845123456")
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")

    def test_add_customer_post_valid(self):
        data = {
            'name': 'Anand Sharma',
            'address': '78, Anna Nagar, Madurai',
            'litres_per_day': '1.5 Litres',
            'phone': '9123456789'
        }
        response = self.client.post(reverse('add_customer'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Customer.objects.filter(name='Anand Sharma').exists())
        self.assertContains(response, "Customer added successfully!")

    def test_add_customer_post_empty_rejected(self):
        initial_count = Customer.objects.count()
        data = {
            'name': '',
            'address': 'Some Address',
            'litres_per_day': '',
            'phone': ''
        }
        response = self.client.post(reverse('add_customer'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.count(), initial_count)
        self.assertContains(response, "All fields are required.")

    def test_edit_customer_get_and_post(self):
        cust = Customer.objects.create(
            name="Kavitha M",
            address="15, Temple Street, Salem",
            litres_per_day="2 Litres",
            phone="9443212345"
        )
        # GET edit page pre-fills values
        response = self.client.get(reverse('edit_customer', kwargs={'id': cust.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kavitha M")
        self.assertContains(response, "15, Temple Street, Salem")

        # POST updated values
        update_data = {
            'name': 'Kavitha Murugan',
            'address': '15, South Car Street, Salem',
            'litres_per_day': '3.5 Litres',
            'phone': '9443219999'
        }
        response = self.client.post(reverse('edit_customer', kwargs={'id': cust.id}), update_data, follow=True)
        self.assertEqual(response.status_code, 200)

        cust.refresh_from_db()
        self.assertEqual(cust.name, 'Kavitha Murugan')
        self.assertEqual(cust.litres_per_day, '3.5 Litres')
        self.assertContains(response, "Customer details updated successfully!")

    def test_delete_customer_post(self):
        cust = Customer.objects.create(
            name="Murugan P",
            address="99, Bypass Road, Trichy",
            litres_per_day="1 Litre",
            phone="9789012345"
        )
        response = self.client.post(reverse('delete_customer', kwargs={'id': cust.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Customer.objects.filter(id=cust.id).exists())
        self.assertContains(response, "Customer deleted successfully!")

    def test_edit_or_delete_nonexistent_customer_returns_404(self):
        response_edit = self.client.get(reverse('edit_customer', kwargs={'id': 9999}))
        self.assertEqual(response_edit.status_code, 404)

        response_delete = self.client.post(reverse('delete_customer', kwargs={'id': 9999}))
        self.assertEqual(response_delete.status_code, 404)
