import mock
from django.http.request import QueryDict

from ncdr.templatetags.utils import pagination


def test_pagination_with_page():
    qd = QueryDict("page=2&letter=A")
    request = mock.MagicMock()
    request.GET = qd
    ctx = {"request": request}
    result = pagination(ctx)
    assert result["paginator_query_string"] == "&letter=A"


def test_pagination_without_page():
    qd = QueryDict("letter=A")
    request = mock.MagicMock()
    request.GET = qd
    ctx = {"request": request}
    result = pagination(ctx)
    assert result["paginator_query_string"] == "&letter=A"


def test_pagination_with_no_args():
    qd = QueryDict()
    request = mock.MagicMock()
    request.GET = qd
    ctx = {"request": request}
    result = pagination(ctx)
    assert result["paginator_query_string"] == ""
