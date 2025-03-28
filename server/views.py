from django.db.models import Count
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from .models import Server
from .schema import server_list_docs
from .serializer import ServerSerializer


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """Returns a list of servers filtered by various parameters.

        This method retrieves a queryset of servers based on the query parameters
        provided in the `request` object. The following query parameters are supported:

        - `category`: Filters servers by category name.
        - `qty`: Limits the number of servers returned.
        - `by_user`: Filters servers by user ID, only returning servers that the user is a member of.
        - `by_serverid`: Filters servers by server ID.
        - `with_num_members`: Annotates each server with the number of members it has.

        Args:
        request: A Django Request object containing query parameters.

        Returns:
        A queryset of servers filtered by the specified parameters.

        Raises:
        AuthenticationFailed: If the query includes the 'by_user' or 'by_serverid'
            parameters and the user is not authenticated.
        ValidationError: If there is an error parsing or validating the query parameters.
            This can occur if the `by_serverid` parameter is not a valid integer, or if the
            server with the specified ID does not exist.

        Examples:
        To retrieve all servers in the 'gaming' category with at least 5 members, you can make
        the following request:

            GET /servers/?category=gaming&with_num_members=true&num_members__gte=5

        To retrieve the first 10 servers that the authenticated user is a member of, you can make
        the following request:

            GET /servers/?by_user=true&qty=10



        서버 목록을 다양한 매개변수로 필터링하여 반환합니다.

        이 메서드는 `request` 객체의 쿼리 매개변수를 기반으로 서버의 queryset을 검색합니다.
        지원되는 쿼리 매개변수는 다음과 같습니다:

        - `category`: 카테고리 이름으로 서버를 필터링합니다.
        - `qty`: 반환할 서버의 개수를 제한합니다.
        - `by_user`: 특정 사용자 ID를 기준으로 서버를 필터링하며, 해당 사용자가 멤버로 속한 서버만 반환합니다.
        - `by_serverid`: 특정 서버 ID를 기준으로 서버를 필터링합니다.
        - `with_num_members`: 각 서버에 속한 멤버 수를 함께 표시합니다.

        Args:
            request: 쿼리 매개변수를 포함하는 Django Request 객체.

        Returns:
            지정된 매개변수에 따라 필터링된 서버 queryset.

        Raises:
            AuthenticationFailed: `by_user` 또는 `by_serverid` 매개변수가 포함되었으나 사용자가 인증되지 않은 경우.
            ValidationError: 쿼리 매개변수의 파싱 또는 검증 오류 발생 시.
                예를 들어, `by_serverid` 값이 정수가 아니거나 해당 ID의 서버가 존재하지 않는 경우.

        Examples:
            `gaming` 카테고리에 속하며 최소 5명의 멤버가 있는 모든 서버 검색:
                GET /servers/?category=gaming&with_num_members=true&num_members__gte=5

            인증된 사용자가 속한 첫 10개의 서버 검색:
                GET /servers/?by_user=true&qty=10

        """
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        if category:
            self.queryset = self.queryset.filter(category__name=category)

        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        if by_serverid:
            if not request.user.is_authenticated:
                raise AuthenticationFailed()

            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(
                        detail=f"Server with id {by_serverid} not found"
                    )
            except ValueError:
                raise ValidationError(detail="Server value error")

        if qty:
            self.queryset = self.queryset[: int(qty)]

        serializer = ServerSerializer(
            self.queryset, many=True, context={"num_members": with_num_members}
        )
        return Response(serializer.data)
