from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import Donation


def expire_stale_donations(db: Session) -> int:
	"""Mark donations as expired if past expires_at and not picked up.

	Returns number of donations updated.
	"""
	now = datetime.utcnow()

	q = db.query(Donation).filter(
		Donation.expires_at < now, Donation.status.in_(["posted", "matched"])
	)
	count = 0
	for d in q.all():
		d.status = "expired"
		count += 1
	return count


