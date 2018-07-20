from decimal import Decimal

from mixt.contrib.css.units import (
    Unit,
    decimalize,
    is_addition_part,
    is_number,
    is_quantified_unit,
)


def test_is_number():
    assert is_number(1) is True
    assert is_number(1.1) is True

    assert is_number(Decimal(1.1)) is True
    assert is_number(Decimal("1.1")) is True

    assert is_number("1.1") is False

    px, em = Unit.many("px em")
    assert is_number(px(3)) is False
    assert is_number(px(3) * 3) is False

    assert is_number(px(3) * 3 + px(2)) is False
    assert is_number(px(3) * 3 + em(2)) is False


def test_is_addition_part():
    assert is_addition_part(1) is False
    assert is_addition_part(1.1) is False

    assert is_addition_part(Decimal(1.1)) is False
    assert is_addition_part(Decimal("1.1")) is False

    assert is_addition_part("1.1") is False

    px, em = Unit.many("px em")
    assert is_addition_part(px(3)) is True
    assert is_addition_part(px(3) * 3) is True

    assert is_addition_part(px(3) * 3 + px(2)) is True
    assert is_addition_part(px(3) * 3 + em(2)) is True


def test_is_quantified_unit():
    assert is_quantified_unit(1) is False
    assert is_quantified_unit(1.1) is False

    assert is_quantified_unit(Decimal(1.1)) is False
    assert is_quantified_unit(Decimal("1.1")) is False

    assert is_quantified_unit("1.1") is False

    px, em = Unit.many("px em")
    assert is_quantified_unit(px(3)) is True
    assert is_quantified_unit(px(3) * 3) is True

    assert is_quantified_unit(px(3) * 3 + px(2)) is True
    assert is_quantified_unit(px(3) * 3 + em(2)) is False


def test_decimalize():
    assert repr(decimalize(1)) == "Decimal('1')"
    assert repr(decimalize(1.1)) == "Decimal('1.1')"
    assert repr(decimalize(Decimal("1.1"))) == "Decimal('1.1')"
    assert repr(decimalize("1.1")) == "Decimal('1.1')"


def test_unit_initialization():
    xx = Unit("xx")

    assert str(xx(3)) == "3xx"
    assert str(3 * xx) == "3xx"
    assert str(xx * 3) == "3xx"

    assert str(xx(-3.1)) == "-3.1xx"
    assert str(-3.1 * xx) == "-3.1xx"
    assert str(xx * -3.1) == "-3.1xx"

    assert str(-xx(3.1)) == "-3.1xx"
    assert str(-(3.1 * xx)) == "-3.1xx"
    assert str(-(xx * 3.1)) == "-3.1xx"


def test_unit_operations():
    xx = Unit("xx")

    assert str(xx(3) + 2 * xx) == "5xx"
    assert str(xx(3) + 2) == "3xx+2"
    assert str(2 + xx(3)) == "2+3xx"

    assert str(xx(3) - 2 * xx) == "1xx"
    assert str(xx(3) - 3 * xx) == "0xx"
    assert str(xx(3) - 4 * xx) == "-1xx"
    assert str(xx(3) - 2) == "3xx-2"
    assert str(2 - xx(3)) == "2-3xx"

    assert str(xx(3) * 2 * xx) == "6xx*xx"
    assert str(xx(3) * xx(2)) == "3xx*2xx"
    assert str(xx(3) * 2) == "6xx"
    assert str(2 * xx(3)) == "6xx"

    assert str(xx(3) / 2 * xx) == "1.5xx*xx"
    assert str(xx(3) / xx(2)) == "3xx/2xx"
    assert str(xx(3) / 2) == "1.5xx"
    assert str(2 / xx(3)) == "2/3xx"


def test_multi_unit_operations():
    xx = Unit("xx")
    yy = Unit("yy")

    assert str(xx(2) + yy(3)) == "calc(2xx + 3yy)"
    assert str(xx(2) + yy(3) - xx(2)) == "3yy"
    assert str((xx(2) + yy(3)) * 2 - yy(2)) == "calc(4xx + 4yy)"
    assert str((xx(100) - yy(30)) / 3) == "calc(100xx / 3 - 10yy)"
    assert str(xx(100) - yy(30) / 3) == "calc(100xx - 10yy)"
    assert str(xx(100) / 3 + yy(30) - xx(120) / 4 - yy(30)) == "calc(10xx / 3)"
    assert str(xx(2) + yy(3) - xx(2) - yy(9) / 3) == "0"
