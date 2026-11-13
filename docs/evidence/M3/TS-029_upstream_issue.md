## Summary

`gz sim -r -s --headless-rendering` intermittently hangs forever after SIGINT when the world has a `gpu_lidar`. I captured the hung process with gdb. The main thread is running gz-common's signal handler **inside an interrupted `gz::transport::NodeShared::Publish`**. That handler calls the Sensors system's `Stop()`, which joins the render thread. The render thread is destroying the `GpuLidarSensor` and is waiting for a gz-transport mutex, which the interrupted `Publish` most likely still holds (two gz-transport discovery threads are stuck on the same mutex). The process waits on itself and never exits.

This looks like the same class of problem as gazebosim/ros_gz#1011, where gz-common's handler stops the server from the signal context. That report and its fix (gazebosim/ros_gz#1012) are about the `GzServer` ROS node, though. I'm using the plain `gz sim` CLI, where the gz-common handler is still the one that runs, so #1012 wouldn't change anything here.

## Environment

- Ubuntu 24.04, x86_64, Intel integrated GPU, headless rendering (`--headless-rendering`, ogre2)
- Gazebo Harmonic from the ROS 2 Jazzy vendor packages:
  - gz-sim 8.15.0 (`ros-jazzy-gz-sim-vendor` 0.0.13)
  - gz-common 5.9.0, gz-transport 13.6.0, gz-sensors 8.2.2
- Started as `gz sim -r -s --headless-rendering <world>.sdf` (from `ros2 launch` via `ExecuteProcess`), stopped with SIGINT.

## What I see

- The server sometimes doesn't exit after SIGINT and has to be killed.
- My robot world has one `gpu_lidar` (360 samples, 10 Hz), an IMU, `gz_ros2_control` and a 1 ms physics step. On it:
  - a dedicated start / wait / SIGINT loop hung in **1 of 80** runs;
  - a batch of longer test runs hung in **3 of 17**.
- The hang also happens with my only custom system plugin removed, so the remaining systems are stock Gazebo plus `gz_ros2_control`.
- On a minimal world (below, with only stock systems and one static `gpu_lidar`), it did **not** reproduce: **0 hangs in 300** runs, all exiting with code 0. My guess is that the hang needs more gz-transport traffic, so the main thread spends more time inside `Publish` when the signal lands. My world adds an IMU and `gz_ros2_control` (joint states and odometry at 100 Hz), and in the longer test batch the robot was also moving. So I can't offer a stock-world reproduction yet; the stack trace is the main evidence.

## Stack trace of the hung process (gdb, `thread apply all bt`, 68 threads)

The two threads that matter:

**Thread 1 (main):** SIGINT arrived inside `Publish` (frames 11–19). The gz-common handler (frames 8–9) is stopping the server and joins the sensors render thread (frames 4–5).

<details><summary>Thread 1, full backtrace</summary>

```
Thread 1 (Thread 0x7de59304bc40 (LWP 26826) "ruby"):
#0  0x00007de592898e51 in __futex_abstimed_wait_common64 (private=128, cancel=true, abstime=0x0, op=265, expected=26928, futex_word=0x7de56a7ff990) at ./nptl/futex-internal.c:57
#1  __futex_abstimed_wait_common (cancel=true, private=128, abstime=0x0, clockid=0, expected=26928, futex_word=0x7de56a7ff990) at ./nptl/futex-internal.c:87
#2  __GI___futex_abstimed_wait_cancelable64 (futex_word=futex_word@entry=0x7de56a7ff990, expected=26928, clockid=clockid@entry=0, abstime=abstime@entry=0x0, private=private@entry=128) at ./nptl/futex-internal.c:139
#3  0x00007de59289e883 in __pthread_clockjoin_ex (threadid=138424287753920, thread_return=0x0, clockid=0, abstime=0x0, block=<optimized out>) at ./nptl/pthread_join_common.c:102
#4  0x00007de58d8ece33 in std::thread::join() () from /lib/x86_64-linux-gnu/libstdc++.so.6
#5  0x00007de57003028c in gz::sim::v8::systems::SensorsPrivate::Stop() () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins/libgz-sim-sensors-system.so
#6  0x00007de58c96aa99 in ?? () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#7  0x00007de58c959aec in ?? () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#8  0x00007de58cfc9b74 in gz::common::SignalHandlerPrivate::OnSignal(int) () from /opt/ros/jazzy/opt/gz_common_vendor/lib/libgz-common5.so.5
#9  0x00007de58cfc8ca0 in onSignal(int) () from /opt/ros/jazzy/opt/gz_common_vendor/lib/libgz-common5.so.5
#10 <signal handler called>
#11 0x00007de59291b79d in __GI___poll (fds=0x7fff66bfaaf0, nfds=1, timeout=0) at ../sysdeps/unix/sysv/linux/poll.c:29
#12 0x00007de58c6d4f53 in ?? () from /lib/x86_64-linux-gnu/libzmq.so.5
#13 0x00007de58c6f7ec7 in ?? () from /lib/x86_64-linux-gnu/libzmq.so.5
#14 0x00007de58c6f8004 in ?? () from /lib/x86_64-linux-gnu/libzmq.so.5
#15 0x00007de58c70be6f in zmq_msg_send () from /lib/x86_64-linux-gnu/libzmq.so.5
#16 0x00007de58cf89eea in ?? () from /opt/ros/jazzy/opt/gz_transport_vendor/lib/libgz-transport13.so.13
#17 0x00007de58cf61569 in gz::transport::v13::NodeShared::Publish(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&, char*, unsigned long, void (*)(void*, void*), std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) () from /opt/ros/jazzy/opt/gz_transport_vendor/lib/libgz-transport13.so.13
#18 0x00007de58cf51ad4 in gz::transport::v13::Node::Publisher::Publish(google::protobuf::Message const&) () from /opt/ros/jazzy/opt/gz_transport_vendor/lib/libgz-transport13.so.13
#19 0x00007de58c962554 in gz::sim::v8::SimulationRunner::PublishStats() () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#20 0x00007de58c966d4c in gz::sim::v8::SimulationRunner::Step(gz::sim::v8::UpdateInfo const&) () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#21 0x00007de58c967c6f in gz::sim::v8::SimulationRunner::Run(unsigned long) () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#22 0x00007de58c959e5d in ?? () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8.so.8
#23 0x00007de58db425b0 in runServer () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/libgz-sim8-gz.so.8.15.0
#24 0x00007de59279ab16 in ?? () from /lib/x86_64-linux-gnu/libffi.so.8
#25 0x00007de5927973ef in ?? () from /lib/x86_64-linux-gnu/libffi.so.8
#26 0x00007de59279a0be in ffi_call () from /lib/x86_64-linux-gnu/libffi.so.8
#27 0x00007de58dcd743c in ?? () from /usr/lib/x86_64-linux-gnu/ruby/3.2.0/fiddle.so
#28 0x00007de592e1637c in rb_nogvl () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#29 0x00007de58dcd7b14 in ?? () from /usr/lib/x86_64-linux-gnu/ruby/3.2.0/fiddle.so
#30 0x00007de592e4d930 in ?? () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#31 0x00007de592e5013f in ?? () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#32 0x00007de592e5462c in ?? () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#33 0x00007de592e57b4a in rb_vm_exec () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#34 0x00007de592cb4e2c in ?? () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#35 0x00007de592cb9153 in ruby_run_node () from /lib/x86_64-linux-gnu/libruby-3.2.so.3.2
#36 0x00005e08fafe3187 in ?? ()
#37 0x00007de59282a1ca in __libc_start_call_main (main=main@entry=0x5e08fafe3120, argc=argc@entry=7, argv=argv@entry=0x7fff66bfc508) at ../sysdeps/nptl/libc_start_call_main.h:58
#38 0x00007de59282a28b in __libc_start_main_impl (main=0x5e08fafe3120, argc=7, argv=0x7fff66bfc508, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7fff66bfc4f8) at ../csu/libc-start.c:360
#39 0x00005e08fafe31d5 in _start ()
```
</details>

**Render thread:** `SensorsPrivate::RenderThread` → `Manager::Remove` → `~GpuLidarSensor`, blocked on a mutex inside libgz-transport.

<details><summary>Render thread, full backtrace</summary>

```
Thread 62 (Thread 0x7de56a7ff6c0 (LWP 26928) "ruby"):
#0  futex_wait (private=0, expected=2, futex_word=0x5e090185eb30) at ../sysdeps/nptl/futex-internal.h:146
#1  __GI___lll_lock_wait (futex=futex@entry=0x5e090185eb30, private=0) at ./nptl/lowlevellock.c:49
#2  0x00007de5928a0237 in lll_mutex_lock_optimized (mutex=0x5e090185eb30) at ./nptl/pthread_mutex_lock.c:48
#3  ___pthread_mutex_lock (mutex=0x5e090185eb30) at ./nptl/pthread_mutex_lock.c:128
#4  0x00007de58cf4e6f2 in ?? () from /opt/ros/jazzy/opt/gz_transport_vendor/lib/libgz-transport13.so.13
#5  0x00007de58cf4a72a in ?? () from /opt/ros/jazzy/opt/gz_transport_vendor/lib/libgz-transport13.so.13
#6  0x00007de56bf0e8d6 in gz::sensors::v8::GpuLidarSensor::~GpuLidarSensor() () from /opt/ros/jazzy/opt/gz_sensors_vendor/lib/libgz-sensors8-gpu_lidar.so.8
#7  0x00007de56bf0ed75 in gz::sensors::v8::GpuLidarSensor::~GpuLidarSensor() () from /opt/ros/jazzy/opt/gz_sensors_vendor/lib/libgz-sensors8-gpu_lidar.so.8
#8  0x00007de56bbf7d33 in ?? () from /opt/ros/jazzy/opt/gz_sensors_vendor/lib/libgz-sensors8.so.8
#9  0x00007de56bbeb96e in gz::sensors::v8::Manager::Remove(unsigned long) () from /opt/ros/jazzy/opt/gz_sensors_vendor/lib/libgz-sensors8.so.8
#10 0x00007de57002f92c in gz::sim::v8::systems::SensorsPrivate::RenderThread() () from /opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins/libgz-sim-sensors-system.so
#11 0x00007de58d8ecdb4 in ?? () from /lib/x86_64-linux-gnu/libstdc++.so.6
#12 0x00007de59289cb84 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:447
#13 0x00007de592929ecc in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:78
```
</details>

Two more threads are blocked on **the same mutex** (`0x5e090185eb30`) as the render thread: the gz-transport discovery threads in `NodeShared::OnNewDisconnection` and `NodeShared::OnNewSrvDisconnection`. No thread that is still running holds it, which fits the interrupted `Publish` on the main thread holding it. The only other mutex waiter is the `gz_ros2_control` rclcpp `MultiThreadedExecutor` on its own lock. The remaining threads are in normal idle waits (condition variables, recv, epoll). I can post the full 68-thread output if useful.

## My analysis

1. The main thread is in `SimulationRunner::Step` → `PublishStats` → `NodeShared::Publish`, which I assume holds a gz-transport mutex.
2. SIGINT is delivered to that thread. gz-common's `onSignal` → `SignalHandlerPrivate::OnSignal` runs the server's stop callback right there, in signal context.
3. The stop path reaches `SensorsPrivate::Stop()`, which calls `std::thread::join()` on the render thread.
4. The render thread is removing the sensors. `~GpuLidarSensor` needs a gz-transport lock (presumably to tear down its publisher) and blocks.
5. The lock can't be released until the interrupted `Publish` resumes, and that can't happen until the handler returns. Deadlock.

That explains why it's intermittent: the signal has to land while the main thread is inside `Publish`, and the sensor teardown has to need the same lock.

## Suggested direction

Doing the stop work (joins, destructors, locks) inside the signal handler isn't async-signal-safe. A fix could have the handler only set an atomic flag (or write to a self-pipe) and let the run loop perform the stop on its next iteration. That might be done in `gz::common::SignalHandler` itself, or in how gz-sim registers its callback. ros_gz#1012 sidesteps the problem in the ROS node by keeping gz-common's handler from running at all, but the CLI path still runs it.

As a workaround on my side I'm treating a hang after a clean run as an invalid shutdown and repeating the run. I noticed `/server_control` with `stop: true` stops the server without a signal, but I haven't tested whether that avoids the deadlock.

## Reproduction attempt with a minimal world (0 hangs in 300 runs)

World (stock systems + Sensors/ogre2 + one static `gpu_lidar`):

<details><summary>gpu_lidar_sigint.sdf</summary>

```xml
<?xml version="1.0" ?>
<!-- Minimal world for a gz sim SIGINT shutdown hang: stock empty.sdf systems + Sensors (ogre2) + one static gpu_lidar. -->
<sdf version="1.6">
  <world name="gpu_lidar_sigint">
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="c"><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></collision>
        <visual name="v"><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></visual>
      </link>
    </model>
    <model name="box">
      <static>true</static>
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="c"><geometry><box><size>0.2 1 1</size></box></geometry></collision>
        <visual name="v"><geometry><box><size>0.2 1 1</size></box></geometry></visual>
      </link>
    </model>
    <model name="lidar">
      <static>true</static>
      <pose>0 0 0.23 0 0 0</pose>
      <link name="link">
        <sensor name="gpu_lidar" type="gpu_lidar">
          <topic>scan</topic>
          <update_rate>10</update_rate>
          <always_on>true</always_on>
          <lidar>
            <scan><horizontal><samples>360</samples><resolution>1</resolution>
              <min_angle>-3.14159</min_angle><max_angle>3.14159</max_angle></horizontal></scan>
            <range><min>0.12</min><max>12.0</max><resolution>0.01</resolution></range>
          </lidar>
        </sensor>
      </link>
    </model>
  </world>
</sdf>
```
</details>

Loop (start, wait for `/scan`, hold 3 s, SIGINT, wait 5 s, dump with gdb if still alive):

<details><summary>sigint_loop.sh</summary>

```bash
#!/usr/bin/env bash
# gz sim SIGINT shutdown-hang loop. Usage: sigint_loop.sh <runs> <hold seconds> <outdir>
# Starts `gz sim -r -s --headless-rendering gpu_lidar_sigint.sdf`, waits until /scan is published, holds,
# sends SIGINT to the gz process, and waits 5 s. A process still alive then counts as a hang: its threads
# are dumped with gdb (this shell is its parent, so ptrace_scope=1 allows it), then it is killed.
WORLD="$(cd "$(dirname "$0")" && pwd)/gpu_lidar_sigint.sdf"; RUNS=$1; HOLD=$2; OUT=$3; mkdir -p "$OUT"
hangs=0
for i in $(seq 1 "$RUNS"); do
  export GZ_PARTITION=sigint_$$_$i
  gz sim -r -s --headless-rendering "$WORLD" > "$OUT/run$i.log" 2>&1 &
  GZ=$!
  for _ in $(seq 1 100); do timeout 1 gz topic -e -n 1 -t /scan >/dev/null 2>&1 && break; done
  sleep "$HOLD"
  kill -INT "$GZ"
  for _ in $(seq 1 50); do kill -0 "$GZ" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$GZ" 2>/dev/null; then
    hangs=$((hangs + 1))
    gdb -q -batch -p "$GZ" -ex "set debuginfod enabled off" -ex "set pagination off" -ex "thread apply all bt" > "$OUT/run${i}_gdb.txt" 2>&1
    kill -KILL "$GZ"; wait "$GZ" 2>/dev/null
    echo "run $i: HANG (alive 5 s after SIGINT; gdb in run${i}_gdb.txt)"
  else
    wait "$GZ"; echo "run $i: exit $? "; rm -f "$OUT/run$i.log"
  fi
done
echo "summary: $hangs hang(s) in $RUNS runs, hold $HOLD s"
```
</details>

Happy to run more variants, a debug build, or a patch if that helps.
