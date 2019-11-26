import mock
from django.http.request import QueryDict

from ncdr.templatetags.utils import pagination


def get_context():
    qd = QueryDict()
    request = mock.MagicMock()
    request.GET = qd
    page_obj = mock.MagicMock()
    page_obj.number = 3
    paginator = mock.MagicMock()
    paginator.num_pages = 3
    return {"request": request, "page_obj": page_obj, "paginator": paginator}


def test_pagination_with_page():
    qd = QueryDict("page=2&letter=A")
    ctx = get_context()
    ctx["request"].GET = qd
    result = pagination(ctx)
    assert result["paginator_query_string"] == "&letter=A"


def test_pagination_without_page():
    qd = QueryDict("letter=A")
    ctx = get_context()
    ctx["request"].GET = qd
    result = pagination(ctx)
    assert result["paginator_query_string"] == "&letter=A"


def test_pagination_with_no_args():
    ctx = get_context()
    result = pagination(ctx)
    assert result["paginator_query_string"] == ""


def test_show_elipsis():
    """
    Elipsis should be True if there are more than 5 more pages
    """
    ctx = get_context()
    ctx["paginator"].num_pages = 7
    ctx["page_obj"].number = 1
    result = pagination(ctx)
    assert result["show_elipsis"]


def test_now_show_elipsis():
    """
    Elipsis should be False if there are fewer than 5 more pages
    """
    ctx = get_context()
    ctx["paginator"].num_pages = 6
    ctx["page_obj"].number = 1
    result = pagination(ctx)
    assert not result["show_elipsis"]


def test_show_additional_pages():
    """
    Additional pages should be True if there are more than or equal to 5 additional pages
    """
    ctx = get_context()
    ctx["paginator"].num_pages = 6
    ctx["page_obj"].number = 1
    result = pagination(ctx)
    assert result["additional_pages"]


def test_not_show_additional_pages():
    """
    Additional pages should be False if there are more than or equal to 5 additional pages
    """
    ctx = get_context()
    ctx["paginator"].num_pages = 5
    ctx["page_obj"].number = 1
    result = pagination(ctx)
    assert not result["additional_pages"]
