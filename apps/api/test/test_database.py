from app.models.law_office import LawOffice
from app.models.user import User


def test_law_office_user_relationship(db):
    office = LawOffice(name="Test Law Office")
    user = User(
        email="test@example.com",
        full_name="Test User",
        role="STAFF",
    )

    office.users.append(user)

    db.add(office)
    db.flush()

    assert len(office.users) == 1
    assert office.users[0].email == "test@example.com"
    assert office.users[0].law_office_id == office.id