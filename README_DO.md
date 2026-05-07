# DigitalOcean App Platform deployment

## Local test (optional)

```bash
docker build -t personality-app .
docker run --rm -p 8080:8080 personality-app
```

Test:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"Time_spent_Alone":4.0,"Stage_fear":"No","Social_event_attendance":4.0,"Going_outside":6.0,"Drained_after_socializing":"No","Friends_circle_size":13.0,"Post_frequency":5.0}' \
  http://localhost:8080/predict
```

## DigitalOcean App Platform

1. Push this repo to GitHub.
2. DigitalOcean -> App Platform -> Create App -> GitHub.
3. Select this repo and branch.
4. App type: Dockerfile detected. Keep defaults.
5. Set HTTP port to 8080.
6. Deploy.

Your public endpoint will be:
```
https://<app-name>.ondigitalocean.app/predict
```
