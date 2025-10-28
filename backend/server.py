from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import asyncio, os, threading, time, math

STATE = {'pose': {'x':0.0,'y':0.0,'theta':0.0}, 'twist': {'lx':0.0,'az':0.0}, 'stamp': 0.0}
ODOM_TOPIC = os.environ.get('ODOM_TOPIC','/odom')
CMD_TOPIC = os.environ.get('CMD_TOPIC','/cmd_vel')

def ros2_thread():
    try:
        import rclpy
        from rclpy.node import Node
        from nav_msgs.msg import Odometry
        from geometry_msgs.msg import Twist
    except Exception as e:
        print("ROS2 not available in this environment:", e)
        return

    class TwinNode(Node):
        def __init__(self):
            super().__init__('digital_twin_backend')
            self.sub_odom = self.create_subscription(Odometry, ODOM_TOPIC, self.on_odom, 10)
            self.sub_cmd = self.create_subscription(Twist, CMD_TOPIC, self.on_cmd, 10)
        def on_odom(self, msg: Odometry):
            q = msg.pose.pose.orientation
            # yaw from quaternion
            siny_cosp = 2 * (q.w * q.z + q.x * q.y)
            cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
            yaw = math.atan2(siny_cosp, cosy_cosp)
            STATE['pose'] = {'x': msg.pose.pose.position.x, 'y': msg.pose.pose.position.y, 'theta': yaw}
            STATE['stamp'] = time.time()
        def on_cmd(self, msg: Twist):
            STATE['twist'] = {'lx': msg.linear.x, 'az': msg.angular.z}
            STATE['stamp'] = time.time()

    rclpy.init()
    node = TwinNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

# spawn ROS2 subscriber thread
t = threading.Thread(target=ros2_thread, daemon=True)
t.start()

app = FastAPI(title="Digital Twin Backend", version="0.1.0")


@app.get('/health')
def health():
    return {'status': 'ok', 'odom_topic': ODOM_TOPIC, 'cmd_topic': CMD_TOPIC}

@app.get('/state')
def state():
    return JSONResponse(STATE)

@app.websocket('/ws')
async def ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_json(STATE)
            await asyncio.sleep(0.2)
    except Exception:
        pass
