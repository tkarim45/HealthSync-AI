# HealthSync-AI

{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZDMwNzRjMy0xMmU1LTQ1MTctYjY2MS0wOGM3ZTM5MDI5NmUiLCJyb2xlIjoidXNlciIsImV4cCI6MTc0NjI2NjAwMn0.DEEkHNpMpXsRW2yi_w4qlWYi3AyEnk604Iea8g1hyzU","user":{"id":"0d3074c3-12e5-4517-b661-08c7e390296e","username":"Taimour","email":"taimourabdulkarim20@gmail.com","role":"user"}}

curl -X POST "http://localhost:8000/api/medical-history" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZDMwNzRjMy0xMmU1LTQ1MTctYjY2MS0wOGM3ZTM5MDI5NmUiLCJyb2xlIjoidXNlciIsImV4cCI6MTc0NjI2NjAwMn0.DEEkHNpMpXsRW2yi_w4qlWYi3AyEnk604Iea8g1hyzU" \
-d '{
"conditions": "Hypertension, Type 2 Diabetes",
"allergies": "Penicillin, Peanuts",
"notes": "Patient diagnosed with hypertension in 2020. Type 2 Diabetes managed with metformin."
}'

curl -X POST "http://localhost:8000/api/medical-history" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZDMwNzRjMy0xMmU1LTQ1MTctYjY2MS0wOGM3ZTM5MDI5NmUiLCJyb2xlIjoidXNlciIsImV4cCI6MTc0NjI2NjAwMn0.DEEkHNpMpXsRW2yi_w4qlWYi3AyEnk604Iea8g1hyzU" \
-d '{
"conditions": "Asthma",
"allergies": "Dust mites",
"notes": "Asthma diagnosed in 2018. Uses albuterol inhaler as needed."
}'
