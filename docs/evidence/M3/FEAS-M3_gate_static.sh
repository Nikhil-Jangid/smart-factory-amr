#!/usr/bin/env bash
# FEAS-M3 static gate (throwaway): G5 (default-off byte-identity) and G6 (sensors-on SDF checks).
# Usage: bash gate_static.sh <gate_dir> <repo>
# xacro is run from inside each workspace with the relative path, as in TEST-M1-02/TEST-M2-02,
# because xacro writes the source path into the header comment of its output.
G=$1; R=$2
source /opt/ros/jazzy/setup.bash
P=$G/ws/src/amr_description/urdf; RP=$R/amr_ws/src/amr_description/urdf
CF=$R/amr_ws/src/amr_bringup/config/controllers.yaml
echo "# FEAS-M3 static gate, $(date '+%Y-%m-%d %H:%M:%S %Z'), xacro from /opt/ros/jazzy, $(gz sim --version | head -1)"
echo "## G5: sensor option disabled (default) vs M1 evidence"
cd $G/ws && xacro src/amr_description/urdf/amr.urdf.xacro > $G/off.urdf; echo "xacro prototype default exit=$?"
sha256sum $G/off.urdf $R/docs/evidence/M1/TEST-M1-02_amr.urdf | sed "s#$G/##; s#$R/##"
cmp $G/off.urdf $R/docs/evidence/M1/TEST-M1-02_amr.urdf && echo "PASS  G5a default expansion byte-identical to M1 evidence TEST-M1-02_amr.urdf" || echo "FAIL  G5a"
cd $G/ws && xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:=$CF > $G/m2_proto.urdf
cd $R/amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:=$CF > $G/m2_repo.urdf
cmp $G/m2_proto.urdf $G/m2_repo.urdf && echo "PASS  G5b M2 expansion (use_ros2_control:=true), sensors off, byte-identical to the repo expansion" || echo "FAIL  G5b"
echo "## G6: sensors on, generated SDF"
xacro $P/amr.urdf.xacro use_ros2_control:=true controllers_file:=$CF use_sensors:=true > $G/on.urdf; echo "xacro sensors-on exit=$?"
check_urdf $G/on.urdf | sed -n '1,4p'
gz sdf -p $G/on.urdf > $G/on.sdf 2> $G/on_sdf.err; echo "gz sdf -p exit=$?"
echo "gz sdf stderr (colour codes stripped):"; sed 's/\x1b\[[0-9;]*m//g' $G/on_sdf.err
cp $G/m2_repo.urdf $G/off_m2_in.urdf; gz sdf -p $G/off_m2_in.urdf > $G/off_m2.sdf 2>/dev/null
python3 $G/sdf_check.py $G/on.sdf; echo "sdf_check exit=$?"
python3 - $G/on.sdf $G/off_m2.sdf <<'PY'
import sys, xml.etree.ElementTree as ET
get = lambda f: {l.get("name"): ET.tostring(l.find("inertial")) for l in ET.parse(f).getroot().find("model").findall("link")}
a, b = get(sys.argv[1]), get(sys.argv[2])
print(("PASS" if a == b else "FAIL") + "  G6 inertial blocks identical with sensors on vs off (links: %s)" % sorted(a))
PY
