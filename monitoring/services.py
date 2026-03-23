from monitoring.models import Alert, AlertSeverity, AlertType


def generate_alerts_for_observation(observation):
    alerts_to_create = []

    if observation.heart_rate is not None and observation.heart_rate > 130:
        alerts_to_create.append(
            {
                "type": AlertType.HIGH_HEART_RATE,
                "message": f"Heart rate is critically high: {observation.heart_rate} bpm.",
            }
        )

    if observation.temperature is not None and observation.temperature >= 39.0:
        alerts_to_create.append(
            {
                "type": AlertType.HIGH_TEMPERATURE,
                "message": f"Temperature is critically high: {observation.temperature} °C.",
            }
        )

    if observation.spo2 is not None and observation.spo2 < 90:
        alerts_to_create.append(
            {
                "type": AlertType.LOW_SPO2,
                "message": f"SpO2 is critically low: {observation.spo2}%.",
            }
        )

    for alert_data in alerts_to_create:
        Alert.objects.get_or_create(
            patient=observation.patient,
            type=alert_data["type"],
            is_active=True,
            defaults={
                "severity": AlertSeverity.SEVERE,
                "message": alert_data["message"],
            },
        )
