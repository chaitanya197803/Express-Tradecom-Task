import math
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from users.models.user_model import User

class UserValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class UserNotFoundError(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        self.status_code = 404
        super().__init__(message)

class UserService:
    @staticmethod
    def validate_user_data(data, check_email_exists=True, user_id=None):
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')

        # Check required fields
        if name is None or email is None or role is None:
            raise UserValidationError("name, email, and role are required", 400)

        # Strip fields
        name = str(name).strip()
        email = str(email).strip()
        role = str(role).strip()

        if not name or not email or not role:
            raise UserValidationError("name, email, and role cannot be empty", 400)

        # Validate email format using Django's validate_email
        try:
            validate_email(email)
        except ValidationError:
            raise UserValidationError("Invalid email format", 400)

        # Check duplicate email
        if check_email_exists:
            query = User.objects.filter(email=email)
            if user_id:
                query = query.exclude(id=user_id)
            if query.exists():
                raise UserValidationError("Email already exists", 409)

    @staticmethod
    def create_user(data):
        UserService.validate_user_data(data, check_email_exists=True)
        user = User.objects.create(
            name=str(data['name']).strip(),
            email=str(data['email']).strip(),
            role=str(data['role']).strip()
        )
        return user

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            raise UserNotFoundError("User not found")

    @staticmethod
    def search_users(search_query):
        if not search_query:
            return User.objects.all()
        # Case-insensitive search on name or email
        return User.objects.filter(
            Q(name__icontains=search_query) | Q(email__icontains=search_query)
        )

    @staticmethod
    def paginate_users(queryset, page_str, limit_str):
        # Default/fallback page and limit
        try:
            page = int(page_str) if page_str is not None else 1
            if page <= 0:
                page = 1
        except (ValueError, TypeError):
            page = 1

        try:
            limit = int(limit_str) if limit_str is not None else 10
            if limit <= 0:
                limit = 10
        except (ValueError, TypeError):
            limit = 10

        total_records = queryset.count()
        total_pages = math.ceil(total_records / limit) if total_records > 0 else 1

        # Adjust page if it exceeds total pages
        if page > total_pages and total_pages > 0:
            page = total_pages

        start = (page - 1) * limit
        end = start + limit
        paginated_data = queryset[start:end]

        return {
            "page": page,
            "limit": limit,
            "total_records": total_records,
            "total_pages": total_pages,
            "data": paginated_data
        }
