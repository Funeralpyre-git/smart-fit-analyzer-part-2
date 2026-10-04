import csv
from pathlib import Path
from exceptions import InvalidIdentifierError, InvalidRecordError
from validators import validate_participant_id, validate_session_id, validate_sensor_values
from models import Participant, Observation, Session

# stores metadata for a rejected CSV row
class RejectedRecord:
    def __init__(self, filename: str, row_number: int, field: str, reason: str, raw_line: str = ""):
        self.filename = filename
        self.row_number = row_number
        self.field = field
        self.reason = reason
        self.raw_line = raw_line

    def __str__(self):
        return f"[{self.filename}: Row {self.row_number}] Field {self.field} rejected: {self.reason}"

    def __repr__(self) -> str:
        return self.__str__()

##### loads participants.csv and returns a dictionary of Participant objects keyed by ID #####
def load_participants(file_path: Path, rejected_list: list) -> dict:
    participants = {}
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")

    with open(path, mode="r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row_idx, row in enumerate(reader, start=2):
            try:
                p_id = row.get("participant_id", "").strip()
                name = row.get("name", "").strip()
                b_hr = row.get("baseline_heart_rate", "").strip()

                validate_participant_id(p_id)
                resting_hr = float(b_hr)
                if resting_hr < 0:
                    raise InvalidRecordError(f"Resting heart rate must be a positive: {p_id}")

                participants[p_id] = Participant(p_id, name, resting_hr=resting_hr, max_hr=185.0)

            except (InvalidRecordError, InvalidRecordError, ValueError) as e:
                rejected_list.append(
                    RejectedRecord(path.name, row_idx, "participant_id/baseline", str(e), str(row))
                )
    return participants

##### loads session csv files and constructs Session objects with Observation streams #####
def load_sessions(file_paths: list, participants: dict, rejected_list: list) -> dict:
    sessions = {}

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        with open(path, mode="r", encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row_idx, row in enumerate(reader, start=2):
                sess_id = row.get("session_id", "").strip()
                part_id = row.get("participant_id", "").strip()

                # validate session ID format
                try: validate_session_id(sess_id)
                except InvalidIdentifierError as e:
                    rejected_list.append(
                        RejectedRecord(path.name, row_idx, "session_id", str(e), str(row))
                    )
                    continue

                # validate participant lookup
                if part_id not in participants:
                    try:
                        validate_participant_id(part_id)
                        reason = f"Unknown participant ID '{part_id}' not found in profiles."
                    except InvalidIdentifierError as e:
                        reason = str(e)
                    rejected_list.append(
                        RejectedRecord(path.name, row_idx, "participant_id", reason, str(row))
                    )
                    continue

                # ensure Session object exists
                if sess_id not in sessions:
                    sessions[sess_id] = Session(sess_id, participants[part_id])

                session = sessions[sess_id]

                try:
                    timestamp = int(row.get("timestamp", -1))
                    hr = float(row.get("heart_rate", -1))
                    skin = float(row.get("skin_response", -1))
                    temp = float(row.get("temperature", -1))
                    act = float(row.get("activity_level", -1))
                    sig = float(row.get("signal_quality", -1))

                    is_valid = validate_sensor_values(hr, act, temp, sig)
                    if not is_valid:
                        rejected_list.append(
                            RejectedRecord(path.name, row_idx, "biometrics", "Sensor reading failed range or quality rules.", str(row))
                        )

                    obs = Observation(timestamp, hr, skin, temp, act, sig, is_valid=is_valid)
                    session.add_observation(obs)

                except (ValueError, TypeError) as e:
                    rejected_list.append(
                        RejectedRecord(
                            path.name, row_idx, "biometrics", f"Type conversion failed: {(str(e))}", str(row))
                    )

                    # invalid observation placeholder
                    session.add_observation(Observation(0, 0, 0, 0, 0, 0, is_valid=False))
    return sessions