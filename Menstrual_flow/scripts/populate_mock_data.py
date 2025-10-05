import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.storage.model import FlowReading


def populate_mock_data(user_email: str):
    """Populate mock flow readings for testing."""
    session = SessionLocal()
    try:
        start_date = datetime(2025, 7, 30)

        for i in range(28):
            reading_date = start_date + timedelta(days=i)
            flow_ml = (i * 3 + 10) % 80
            reading = FlowReading(
                user_email=user_email,
                timestamp=reading_date,
                flow_ml=flow_ml,
                hb=12.5 + (i % 3) * 0.2,
                ph=7.0 + (i % 2) * 0.1,
                crp=5.0 + (i % 4) * 0.5,
                hba1c_ratio=5.5,
                clots_score=(i % 3),
                fsh_level=6.2,
                lh_level=8.1,
                amh_level=1.5,
                tsh_level=2.3,
                prolactin_level=12.8,
            )

            session.add(reading)

        session.commit()
        print(f"Mock data populated successfully for {user_email}")

    finally:
        session.close()


if __name__ == "__main__":
    populate_mock_data("testuser@example.com")
