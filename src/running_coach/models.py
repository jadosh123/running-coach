from pydantic import BaseModel


class Activity(BaseModel):
    activity_id: int
    activity_name: str | None
    activity_type: str
    start_time_local: str
    start_time_gmt: str
    distance_meters: float | None
    duration_seconds: float | None
    moving_duration_seconds: float | None
    elevation_gain_meters: float | None
    elevation_loss_meters: float | None
    average_speed_mps: float | None
    max_speed_mps: float | None
    calories: float | None
    average_hr: float | None
    max_hr: float | None
    average_cadence: float | None
    max_cadence: float | None
    steps: int | None


class ActivitySplit(BaseModel):
    id: int
    activity_id: int
    lap_index: int
    start_time_gmt: str
    distance_meters: float | None
    duration_seconds: float | None
    moving_duration_seconds: float | None
    elevation_gain_meters: float | None
    elevation_loss_meters: float | None
    average_speed_mps: float | None
    max_speed_mps: float | None
    calories: float | None
    average_hr: float | None
    max_hr: float | None
    average_cadence: float | None
    max_cadence: float | None
    stride_length_cm: float | None
    start_latitude: float | None
    start_longitude: float | None
    end_latitude: float | None
    end_longitude: float | None
