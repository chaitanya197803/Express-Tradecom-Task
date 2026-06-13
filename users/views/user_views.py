import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

from users.services.user_service import UserService, UserValidationError, UserNotFoundError
from users.serializers.user_serializer import UserSerializer

logger = logging.getLogger('app')

# Inline serializers for Swagger documentation
class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()

class UserSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = UserSerializer()

class UserCreateSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="User created successfully")
    data = UserSerializer()

class UserListSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    data = UserSerializer(many=True)

class UserPaginatedSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    page = serializers.IntegerField()
    limit = serializers.IntegerField()
    total_records = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    data = UserSerializer(many=True)


class UserListCreateView(APIView):
    @extend_schema(
        summary="Get all users or search/paginate users",
        description="Retrieve a list of all users. Supports optional filtering by search query (name/email) and custom pagination (page/limit).",
        parameters=[
            OpenApiParameter(name='search', description='Search term (searches name and email)', required=False, type=str),
            OpenApiParameter(name='page', description='Page number for pagination', required=False, type=int),
            OpenApiParameter(name='limit', description='Number of records per page', required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(
                description="List of users returned successfully (paginated or full list)",
                response=serializers.Serializer # Will distinguish dynamically
            )
        }
    )
    def get(self, request):
        search_query = request.query_params.get('search')
        page = request.query_params.get('page')
        limit = request.query_params.get('limit')

        logger.info(f"API Request - GET /users: search={search_query}, page={page}, limit={limit}")

        try:
            queryset = UserService.search_users(search_query)

            # Check if pagination parameters are provided
            if page is not None or limit is not None:
                pagination_result = UserService.paginate_users(queryset, page, limit)
                serializer = UserSerializer(pagination_result['data'], many=True)
                response_data = {
                    "success": True,
                    "page": pagination_result['page'],
                    "limit": pagination_result['limit'],
                    "total_records": pagination_result['total_records'],
                    "total_pages": pagination_result['total_pages'],
                    "data": serializer.data
                }
            else:
                serializer = UserSerializer(queryset, many=True)
                response_data = {
                    "success": True,
                    "count": len(serializer.data),
                    "data": serializer.data
                }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"API Error - GET /users: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Create a new user",
        description="Creates a new user with the provided name, email, and role.",
        request=UserSerializer,
        responses={
            201: OpenApiResponse(response=UserCreateSuccessSerializer, description="User created successfully"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid input or email format"),
            409: OpenApiResponse(response=ErrorResponseSerializer, description="Email already exists")
        }
    )
    def post(self, request):
        logger.info(f"API Request - POST /users: body={request.data}")

        try:
            user = UserService.create_user(request.data)
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "message": "User created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except UserValidationError as e:
            logger.warning(f"Validation Error - POST /users: {e.message}")
            return Response(
                {"success": False, "error": e.message},
                status=e.status_code
            )
        except Exception as e:
            logger.error(f"API Error - POST /users: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailView(APIView):
    @extend_schema(
        summary="Get a user by ID",
        description="Retrieve a single user's details by their database ID.",
        responses={
            200: OpenApiResponse(response=UserSuccessSerializer, description="User retrieved successfully"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="User not found")
        }
    )
    def get(self, request, id):
        logger.info(f"API Request - GET /users/{id}")

        try:
            user = UserService.get_user_by_id(id)
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except UserNotFoundError as e:
            logger.warning(f"Validation Error - GET /users/{id}: {e.message}")
            return Response(
                {"success": False, "error": e.message},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"API Error - GET /users/{id}: {str(e)}", exc_info=True)
            return Response(
                {"success": False, "error": "An internal server error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
