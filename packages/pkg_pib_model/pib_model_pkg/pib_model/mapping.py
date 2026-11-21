"""Motor angles of pib-backend <-> joint angles of the pib URDF (mapping.json of pib-3d).

pib-backend publishes /joint_states with motor names and positions in centidegrees. The URDF
needs its own joint names in radians. The formula is the one of Cerebra's robot view
(@pib/robot-view): urdf_deg = motor_deg * gearRatio * direction - zeroOffsetDeg, coupled
joints follow their driven joint times `factor`, passive joints stay at 0.
"""
import math


class MotorMapping:
    """Conversion based on mapping.json."""

    def __init__(self, mapping):
        """mapping: parsed mapping.json (dict with 'joints')."""
        self.joints = mapping['joints']
        self.driven = {j['motor']: j for j in self.joints
                       if j['class'] == 'driven' and j.get('motor')}
        self.by_joint = {j['urdfJoint']: j for j in self.joints}

    @property
    def motor_names(self):
        """Return the motor names that move a URDF joint."""
        return sorted(self.driven)

    def joint_names(self):
        """All URDF joints of the mapping (driven, coupled, passive)."""
        return [j['urdfJoint'] for j in self.joints]

    def motor_to_joint_rad(self, motor, centideg):
        """Joint angle in rad of the joint the motor drives."""
        j = self.driven[motor]
        deg = centideg / 100.0 * (j.get('gearRatio') or 1.0) * (j.get('direction') or 1) \
            - (j.get('zeroOffsetDeg') or 0.0)
        return math.radians(deg)

    def joint_rad_to_motor_centideg(self, motor, rad):
        """Inverse of motor_to_joint_rad."""
        j = self.driven[motor]
        deg = (math.degrees(rad) + (j.get('zeroOffsetDeg') or 0.0)) * (j.get('direction') or 1) \
            / (j.get('gearRatio') or 1.0)
        return deg * 100.0

    def joint_positions(self, motor_centideg):
        """URDF joint angles (rad) for all mapped joints from {motor: centidegrees}."""
        out = {j['urdfJoint']: 0.0 for j in self.joints}
        for motor, value in motor_centideg.items():
            if motor in self.driven:
                out[self.driven[motor]['urdfJoint']] = self.motor_to_joint_rad(motor, value)
        # coupled joints: follow the leading joint (chains are resolved step by step)
        for _ in range(len(self.joints)):
            changed = False
            for j in self.joints:
                coupling = j.get('coupling')
                if j['class'] == 'coupled' and coupling:
                    value = out.get(coupling['follows'], 0.0) * coupling.get('factor', 1.0)
                    if out[j['urdfJoint']] != value:
                        out[j['urdfJoint']] = value
                        changed = True
            if not changed:
                break
        return out
