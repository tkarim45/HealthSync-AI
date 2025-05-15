SELECT
  d.id AS doctor_id,
  d.username AS doctor_username,
  COUNT(a.id) AS appointment_count
FROM users d
LEFT JOIN appointments a ON d.id = a.doctor_id
WHERE d.role = 'doctor'
GROUP BY d.id, d.username