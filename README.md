# DigitalTwin-Dashboard (ROS2 ➜ Web)

A minimal **digital twin** stack:
- **ROS2 subscriber backend** (FastAPI) aggregates robot state (pose, velocity, sensors).
- **WebSocket** stream `/ws` + REST `/state`.
- **Three.js** front-end renders a simple factory floor + robot avatar in 3D.
- Works alongside your ROS2 sims (Nav2/SLAM).

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend (subscribes to /odom and /cmd_vel)
uvicorn backend.server:app --host 0.0.0.0 --port 8001

# Open the web client
# (serves static files from ./web)
python -m http.server --directory web 8080
# then browse http://localhost:8080
```

**ROS 2 topics read by default:** `/odom` (`nav_msgs/Odometry`), `/cmd_vel` (`geometry_msgs/Twist`).

Set env to change topics:
```bash
export ODOM_TOPIC=/odom
export CMD_TOPIC=/cmd_vel
export WS_PORT=8001
```

---

## Docker
```bash
cd docker
docker build -f Dockerfile.backend -t digital-twin-backend ..
docker run --rm --net=host -e ODOM_TOPIC=/odom -e CMD_TOPIC=/cmd_vel digital-twin-backend
```
