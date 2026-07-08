import pytest

from titanic.domain.value_objects.gender_vo import Gender, GenderType
from titanic.domain.value_objects.age_vo import Age
from titanic.domain.value_objects.sibsp_vo import SibSp
from titanic.domain.value_objects.parch_vo import Parch
from titanic.domain.value_objects.survived_vo import Survived


class TestGender:
    def test_from_raw_male(self):
        assert Gender.from_raw("male").value == GenderType.MALE

    def test_from_raw_female(self):
        assert Gender.from_raw("female").value == GenderType.FEMALE

    def test_from_raw_none_is_unknown(self):
        assert Gender.from_raw(None).value == GenderType.UNKNOWN

    def test_from_raw_uppercase_is_normalized(self):
        assert Gender.from_raw("MALE").value == GenderType.MALE

    def test_from_raw_unrecognized_string_is_unknown(self):
        assert Gender.from_raw("other").value == GenderType.UNKNOWN

    def test_is_female_true_for_female(self):
        assert Gender.from_raw("female").is_female is True

    def test_is_female_false_for_male(self):
        assert Gender.from_raw("male").is_female is False

    def test_is_female_false_for_unknown(self):
        assert Gender.from_raw(None).is_female is False


class TestAge:
    def test_from_raw_valid_string(self):
        assert Age.from_raw("22.5").value == 22.5

    def test_from_raw_none_is_unknown(self):
        assert Age.from_raw(None).is_unknown is True

    def test_from_raw_empty_string_is_unknown(self):
        assert Age.from_raw("").is_unknown is True

    def test_negative_age_raises(self):
        with pytest.raises(ValueError):
            Age(value=-1.0)

    def test_age_over_120_raises(self):
        with pytest.raises(ValueError):
            Age(value=121.0)

    def test_boundary_0_is_valid(self):
        Age(value=0.0)

    def test_boundary_120_is_valid(self):
        Age(value=120.0)

    def test_non_numeric_string_raises(self):
        with pytest.raises(ValueError, match="파싱 실패"):
            Age.from_raw("abc")

    def test_is_minor_true_under_18(self):
        assert Age(value=17.9).is_minor is True

    def test_is_minor_false_at_18(self):
        assert Age(value=18.0).is_minor is False

    def test_is_minor_false_for_unknown_age(self):
        assert Age(value=None).is_minor is False


class TestSibSp:
    def test_valid_value(self):
        assert SibSp(value=2).value == 2

    def test_zero_is_valid(self):
        SibSp(value=0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="SibSp"):
            SibSp(value=-1)

    def test_from_raw_parses_string(self):
        assert SibSp.from_raw("3").value == 3

    def test_from_raw_none_defaults_to_zero(self):
        assert SibSp.from_raw(None).value == 0

    def test_from_raw_empty_string_defaults_to_zero(self):
        assert SibSp.from_raw("").value == 0


class TestParch:
    def test_valid_value(self):
        assert Parch(value=1).value == 1

    def test_zero_is_valid(self):
        Parch(value=0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="Parch"):
            Parch(value=-1)

    def test_from_raw_parses_string(self):
        assert Parch.from_raw("2").value == 2

    def test_from_raw_none_defaults_to_zero(self):
        assert Parch.from_raw(None).value == 0

    def test_from_raw_empty_string_defaults_to_zero(self):
        assert Parch.from_raw("").value == 0


class TestSurvived:
    def test_from_raw_1_means_survived(self):
        assert Survived.from_raw("1").value is True

    def test_from_raw_0_means_did_not_survive(self):
        assert Survived.from_raw("0").value is False

    def test_from_raw_none_is_unknown(self):
        assert Survived.from_raw(None).is_unknown is True

    def test_from_raw_empty_string_is_unknown(self):
        assert Survived.from_raw("").is_unknown is True

    def test_from_raw_invalid_value_raises(self):
        with pytest.raises(ValueError, match="파싱 실패"):
            Survived.from_raw("2")

    def test_is_unknown_false_when_survival_is_known(self):
        assert Survived.from_raw("1").is_unknown is False
