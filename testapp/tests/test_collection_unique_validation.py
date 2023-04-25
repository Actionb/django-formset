from django.test import TestCase

from testapp.forms.company import CompanyCollection
from testapp.models import Company, Team, Member


class TestUniqueValidation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Foo Corp")
        cls.team = Team.objects.create(name="Alice Validation Team", company=cls.company)
        cls.alice = Member.objects.create(name="Alice", team=cls.team)

    def test_control(self):
        data = {
            "company": {"name": self.company.name, "id": self.company.pk},
            "teams": [
                {
                    "team": {"name": self.team.name, "company": self.company, "id": self.team.pk},
                    "members": [
                        {"member": {"name": self.alice.name, "team": self.team.pk, "id": self.alice.pk}}
                    ]
                },
            ]
        }
        coll = CompanyCollection(data=data, instance=self.company)
        self.assertFalse(coll.errors)

    def test_add_duplicate_team(self):
        data = {
            "company": {"name": self.company.name, "id": self.company.pk},
            "teams": [
                {
                    "team": {"name": self.team.name, "company": self.company, "id": self.team.pk},
                    "members": [
                        {"member": {"name": self.alice.name, "team": self.team.pk, "id": self.alice.pk}}
                    ]
                },
                {
                    "team": {"name": self.team.name, "company": self.company, "id": None},
                    "members": []
                },
            ]
        }
        coll = CompanyCollection(data=data, instance=self.company)
        self.assertFalse(coll.is_valid())
        self.assertIn("Team with this Team Name and Company already exists", str(coll.errors))

    def test_add_duplicate_member(self):
        data = {
            "company": {"name": self.company.name, "id": self.company.pk},
            "teams": [
                {
                    "team": {"name": self.team.name, "company": self.company, "id": self.team.pk},
                    "members": [
                        {"member": {"name": self.alice.name, "team": self.team.pk, "id": self.alice.pk}},
                        {"member": {"name": self.alice.name, "team": self.team.pk, "id": None}},
                    ]
                },
            ]
        }
        coll = CompanyCollection(data=data, instance=self.company)
        self.assertFalse(coll.is_valid())
        self.assertIn("Member with this Member Name and Team already exists", str(coll.errors))

    def test_add_new_team_with_duplicate_members(self):
        data = {
            "company": {"name": self.company.name, "id": self.company.pk},
            "teams": [
                {
                    "team": {"name": "Bob's Test Team", "company": self.company, "id": None},
                    "members": [
                        {"member": {"name": "Bob", "team": None, "id": None}},
                        {"member": {"name": "Bob", "team": None, "id": None}},
                    ]
                },
            ]
        }
        coll = CompanyCollection(data=data, instance=self.company)
        self.assertFalse(coll.is_valid())

    def test_add_new_company_with_duplicate_teams(self):
        data = {
            "company": {"name": "Bob Corp", "id": None},
            "teams": [
                {
                    "team": {"name": "Bob's Test Team", "company": None, "id": None},
                    "members": []
                },
                {
                    "team": {"name": "Bob's Test Team", "company": None, "id": None},
                    "members": []
                },
            ]
        }
        coll = CompanyCollection(data=data, instance=self.company)
        self.assertFalse(coll.is_valid())
