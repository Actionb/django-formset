import pytest

from testapp.forms.company import CompanyCollection
from testapp.models import Company, Team, Member


@pytest.fixture
def team(company):
    return Team.objects.create(name="Alice Validation Team", company=company)


@pytest.fixture
def company():
    return Company.objects.create(name="Foo Corp")


@pytest.fixture
def member(team):
    return Member.objects.create(name="Alice", team=team)


@pytest.mark.django_db
def test_control(company, team, member):
    # protect against the possibility that the other tests pass because the
    # collection is always invalid
    data = {
        "company": {"name": company.name, "id": company.pk},
        "teams": [
            {
                "team": {"name": team.name, "id": team.pk},
                "members": [
                    {"member": {"name": member.name, "id": member.pk}}
                ]
            },
        ]
    }
    coll = CompanyCollection(data=data, instance=company)
    assert coll.is_valid()


@pytest.mark.django_db
def test_add_duplicate_team(company, team, member):
    data = {
        "company": {"name": company.name, "id": company.pk},
        "teams": [
            {
                "team": {"name": team.name, "id": team.pk},
                "members": [
                    {"member": {"name": member.name, "id": member.pk}}
                ]
            },
            {
                "team": {"name": team.name, "id": None},
                "members": []
            },
        ]
    }
    coll = CompanyCollection(data=data, instance=company)
    assert not coll.is_valid()
    assert "Please correct the duplicate data for name and company, which must be unique." in str(coll.errors)


@pytest.mark.django_db
def test_add_duplicate_member(company, team, member):
    data = {
        "company": {"name": company.name, "id": company.pk},
        "teams": [
            {
                "team": {"name": team.name, "id": team.pk},
                "members": [
                    {"member": {"name": member.name, "id": member.pk}},
                    {"member": {"name": member.name, "id": None}},
                ]
            },
        ]
    }
    coll = CompanyCollection(data=data, instance=company)
    assert not coll.is_valid()
    assert "Please correct the duplicate data for name and team, which must be unique." in str(coll.errors)


@pytest.mark.django_db
def test_add_new_team_with_duplicate_members(company, team, member):
    data = {
        "company": {"name": company.name, "id": company.pk},
        "teams": [
            {
                "team": {"name": "Bob's Test Team", "id": None},
                "members": [
                    {"member": {"name": "Bob", "id": None}},
                    {"member": {"name": "Bob", "id": None}},
                ]
            },
        ]
    }
    coll = CompanyCollection(data=data, instance=company)
    assert not coll.is_valid()
    assert "Please correct the duplicate data for name and team, which must be unique." in str(coll.errors)


@pytest.mark.django_db
def test_add_new_company_with_duplicate_teams(company, team, member):
    data = {
        "company": {"name": "Bob Corp", "id": None},
        "teams": [
            {
                "team": {"name": "Bob's Test Team", "id": None},
                "members": []
            },
            {
                "team": {"name": "Bob's Test Team", "id": None},
                "members": []
            },
        ]
    }
    coll = CompanyCollection(data=data, instance=company)
    assert not coll.is_valid()
    assert "Please correct the duplicate data for name and company, which must be unique." in str(coll.errors)
